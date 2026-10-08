"""A vLLM backend for bench.py's ModelFn: text in, text out, in batches.

Three ways of putting a prompt to a model, chosen by the model config:

  base       plain completion. The bench prompt already ends in "Answer:", so
             the continuation is the answer; the tokenizer's own special
             tokens are kept, which for LFM2.5 means the bos token (worth 7.5
             to 12.2 MMLU points on LFM2-350M, src/STATE.md claim T0). Greedy,
             a short budget, and the first non-empty line is the answer.
  instruct   the tokenizer's chat template, the prompt as one user turn with
             its trailing "Answer:" line dropped (the instruction above it
             already asks for the answer after the word Answer). Thinking off
             is Qwen3's enable_thinking=False, which pre-fills an empty think
             block. Greedy.
  thinking   enable_thinking=True, in two passes so the thinking budget is a
             hard cap: generate up to think_budget tokens stopping at
             </think>; then append </think> (closing a truncated block by
             force) and generate the answer. Sampled at Qwen's recommended
             thinking settings (T 0.6, top-p 0.95, top-k 20) with a per-prompt
             seed, because greedy decoding loops in thinking mode.

Every call returns the text with any think block removed, the full raw
output, and the token counts, so a record can be regraded without a rerun.

The pure helpers at the top (strip_thinking, chat_prompt_text, seed_for)
carry no vLLM import and are what the tests exercise.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field

# FlashInfer's top-k/top-p sampler is compiled on first use and needs nvcc,
# which the box does not have on its path; vLLM's own sampler needs nothing.
os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")

THINK_BUDGET = 4096
ANSWER_BUDGET_INSTRUCT = 512
ANSWER_BUDGET_BASE = 24
THINK_SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20}


@dataclass(frozen=True)
class ModelSpec:
    name: str
    hf_id: str
    kind: str                       # base or instruct
    thinking_modes: tuple = (False,)
    notes: str = ""


MODELS: dict[str, ModelSpec] = {s.name: s for s in (
    ModelSpec("lfm2.5-350m-base", "LiquidAI/LFM2.5-350M-Base", "base"),
    ModelSpec("lfm2.5-350m", "LiquidAI/LFM2.5-350M", "instruct", (False,),
              "chat template has no thinking switch; thinking off only"),
    ModelSpec("qwen3-0.6b-base", "Qwen/Qwen3-0.6B-Base", "base"),
    ModelSpec("qwen3-0.6b", "Qwen/Qwen3-0.6B", "instruct", (False, True)),
    ModelSpec("qwen3-1.7b-base", "Qwen/Qwen3-1.7B-Base", "base"),
    ModelSpec("qwen3-1.7b", "Qwen/Qwen3-1.7B", "instruct", (False, True)),
    ModelSpec("qwen3-4b", "Qwen/Qwen3-4B", "instruct", (False, True)),
    ModelSpec("qwen3-8b", "Qwen/Qwen3-8B", "instruct", (False, True)),
)}

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.S)


def strip_thinking(text: str) -> str:
    """Remove closed think blocks; an unclosed one runs to the end."""
    text = _THINK_BLOCK.sub("", text or "")
    if "<think>" in text:
        text = text.split("<think>")[0]
    if "</think>" in text:
        text = text.split("</think>")[-1]
    return text.strip()


def user_content(prompt: str) -> str:
    """The bench prompt as a chat turn: drop the trailing bare Answer: cue."""
    stripped = prompt.rstrip()
    if stripped.endswith("\nAnswer:"):
        stripped = stripped[: -len("\nAnswer:")]
    return stripped


def chat_prompt_text(tokenizer, prompt: str, thinking: bool | None) -> str:
    msgs = [{"role": "user", "content": user_content(prompt)}]
    kwargs = {"tokenize": False, "add_generation_prompt": True}
    if thinking is not None:
        kwargs["enable_thinking"] = thinking
    return tokenizer.apply_chat_template(msgs, **kwargs)


def seed_for(prompt: str) -> int:
    return int(hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8], 16)


@dataclass
class Generation:
    text: str
    raw: str
    n_prompt_tokens: int
    n_think_tokens: int = 0
    n_answer_tokens: int = 0
    think_truncated: bool = False
    finish_reason: str | None = None
    extra: dict = field(default_factory=dict)


class VLLMModel:
    """One loaded model. Call it as a ModelFn or hand it a batch."""

    def __init__(self, spec: ModelSpec, max_model_len: int = 24576,
                 gpu_memory_utilization: float = 0.88, seed: int = 0,
                 think_budget: int = THINK_BUDGET, enforce_eager: bool = False):
        from transformers import AutoTokenizer
        from vllm import LLM

        self.spec = spec
        self.think_budget = think_budget
        self.max_model_len = max_model_len
        self.tok = AutoTokenizer.from_pretrained(spec.hf_id)
        self.llm = LLM(model=spec.hf_id, dtype="bfloat16", seed=seed,
                       max_model_len=max_model_len,
                       gpu_memory_utilization=gpu_memory_utilization,
                       enable_prefix_caching=True, enforce_eager=enforce_eager)
        self.think_end = None
        if "</think>" in self.tok.get_vocab():
            self.think_end = self.tok.convert_tokens_to_ids("</think>")
        self.thinking = False

    def close(self) -> None:
        """Shut the engine process down so the GPU is free for the next model."""
        try:
            self.llm.llm_engine.engine_core.shutdown()
        except Exception as exc:                          # noqa: BLE001
            print(f"engine shutdown: {type(exc).__name__}: {exc}", flush=True)

    # -- the ModelFn face ---------------------------------------------------
    def __call__(self, prompt: str) -> str:
        return self.generate([prompt])[0].text

    def set_thinking(self, on: bool) -> None:
        if on and on not in self.spec.thinking_modes:
            raise ValueError(f"{self.spec.name} has no thinking mode")
        self.thinking = on

    # -- prompt encoding ----------------------------------------------------
    def encode(self, prompt: str) -> list[int]:
        if self.spec.kind == "base":
            # add_special_tokens keeps whatever the tokenizer prepends: the
            # bos token for LFM2.5, nothing for Qwen3.
            return self.tok(prompt).input_ids
        thinking = self.thinking if "enable_thinking" in (
            self.tok.chat_template or "") else None
        text = chat_prompt_text(self.tok, prompt, thinking)
        return self.tok(text, add_special_tokens=False).input_ids

    def decode_params(self) -> dict:
        if self.spec.kind == "base":
            return {"mode": "base", "temperature": 0.0,
                    "max_tokens": ANSWER_BUDGET_BASE}
        if not self.thinking:
            return {"mode": "instruct", "temperature": 0.0,
                    "max_tokens": ANSWER_BUDGET_INSTRUCT}
        return {"mode": "thinking", **THINK_SAMPLING,
                "think_budget": self.think_budget,
                "max_tokens": ANSWER_BUDGET_INSTRUCT, "seed": "sha256(prompt)"}

    # -- generation -----------------------------------------------------------
    def generate(self, prompts: list[str]) -> list[Generation]:
        from vllm import SamplingParams

        ids = [self.encode(p) for p in prompts]
        too_long = [len(x) + self.think_budget + ANSWER_BUDGET_INSTRUCT
                    > self.max_model_len for x in ids]
        out: list[Generation | None] = [None] * len(prompts)
        live = [i for i, bad in enumerate(too_long) if not bad]
        for i, bad in enumerate(too_long):
            if bad:
                out[i] = Generation("", "", len(ids[i]),
                                    finish_reason="prompt_too_long")
        if not live:
            return out

        if self.spec.kind == "base" or not self.thinking:
            budget = (ANSWER_BUDGET_BASE if self.spec.kind == "base"
                      else ANSWER_BUDGET_INSTRUCT)
            sp = SamplingParams(temperature=0.0, max_tokens=budget)
            res = self.llm.generate([{"prompt_token_ids": ids[i]} for i in live],
                                    sp, use_tqdm=False)
            for i, r in zip(live, res):
                o = r.outputs[0]
                out[i] = Generation(strip_thinking(o.text) if self.spec.kind != "base"
                                    else o.text, o.text, len(ids[i]),
                                    n_answer_tokens=len(o.token_ids),
                                    finish_reason=o.finish_reason)
            return out

        # Thinking: pass one, bounded thinking.
        p1 = [SamplingParams(max_tokens=self.think_budget,
                             stop_token_ids=[self.think_end] if self.think_end else None,
                             seed=seed_for(prompts[i]), **THINK_SAMPLING)
              for i in live]
        res1 = self.llm.generate([{"prompt_token_ids": ids[i]} for i in live],
                                 p1, use_tqdm=False)
        close = self.tok("\n</think>\n\n", add_special_tokens=False).input_ids
        second, meta = [], []
        for i, r in zip(live, res1):
            o = r.outputs[0]
            toks = list(o.token_ids)
            hit_end = (self.think_end is not None and
                       (o.stop_reason == self.think_end or
                        (toks and toks[-1] == self.think_end)))
            if toks and self.think_end is not None and toks[-1] == self.think_end:
                toks = toks[:-1]
            truncated = o.finish_reason == "length"
            if not hit_end and not truncated:
                # The model closed its turn without a think block to close.
                out[i] = Generation(strip_thinking(o.text), o.text, len(ids[i]),
                                    n_think_tokens=0,
                                    n_answer_tokens=len(o.token_ids),
                                    finish_reason=o.finish_reason)
                continue
            second.append({"prompt_token_ids": ids[i] + toks + close})
            meta.append((i, o.text, len(toks), truncated))
        if second:
            p2 = [SamplingParams(max_tokens=ANSWER_BUDGET_INSTRUCT,
                                 seed=seed_for(prompts[i]) + 1, **THINK_SAMPLING)
                  for i, *_ in meta]
            res2 = self.llm.generate(second, p2, use_tqdm=False)
            for (i, think_text, n_think, truncated), r in zip(meta, res2):
                o = r.outputs[0]
                raw = f"{think_text}\n</think>\n\n{o.text}"
                out[i] = Generation(strip_thinking(o.text), raw, len(ids[i]),
                                    n_think_tokens=n_think,
                                    n_answer_tokens=len(o.token_ids),
                                    think_truncated=truncated,
                                    finish_reason=o.finish_reason)
        return out

    # -- likelihood scoring ---------------------------------------------------
    def loglik(self, pairs: list[tuple[str, str]]) -> list[tuple[float, int]]:
        """(summed NLL, token count) of each continuation given its context.

        Context and continuation are tokenized apart and concatenated, the
        same split src/evals/mc.py uses, so an option's tokens do not depend
        on the context's last word. The context keeps the tokenizer's special
        tokens (the bos token for LFM2.5).
        """
        from vllm import SamplingParams

        reqs, spans = [], []
        for ctx, cont in pairs:
            c = self.tok(ctx).input_ids
            o = self.tok(cont, add_special_tokens=False).input_ids
            if not o:
                raise ValueError(f"continuation {cont!r} has no tokens")
            reqs.append({"prompt_token_ids": c + o})
            spans.append((len(c), len(o)))
        sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0.0)
        res = self.llm.generate(reqs, sp, use_tqdm=False)
        out = []
        for r, (n_ctx, n_opt), req in zip(res, spans, reqs):
            toks = req["prompt_token_ids"]
            plp = r.prompt_logprobs
            total = 0.0
            for pos in range(n_ctx, n_ctx + n_opt):
                total -= plp[pos][toks[pos]].logprob
            out.append((total, n_opt))
        return out
