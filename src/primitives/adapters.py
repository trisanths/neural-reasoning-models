"""Turning a project checkpoint into the runner's predict callable.

The runner asks only for predict(question, chunks) -> str. This module
supplies that for a src/train TransformerLM checkpoint, rendering prompts
the way src/rl/env.build_prompt does so the model meets the layout it was
trained on: a world preamble, the chunks as <|doc|> spans, the question
after <|q|>, and generation beginning at <|a|>.

Decoding is sampled, not greedy. Greedy decoding on this project has
produced zeros that turned out to be an artefact of a single high-mass
token at the first position rather than a real inability, so the default
here is temperature 0.7 with top-k, and the temperature is recorded in the
report. Sampling runs through src.rl.sampler.CachedPolicy, the same key
and value cached decoder the rollout loop uses, batched across items so a
suite of a few thousand prompts is minutes rather than hours.

Long prompts are truncated from the left, keeping the tail, because the
question and the answer marker sit at the end of every item in this suite.
"""

from __future__ import annotations

import torch

from src.evals.mc import load_checkpoint_model
from src.rl.sampler import PAD_TOKEN, CachedPolicy
from src.train.data import render_world_preamble
from src.train.tokenizer import load_tokenizer

DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_K = 50
DEFAULT_MAX_NEW = 48


def build_prompt_ids(question: str, chunks, tokenizer, max_len: int,
                     reserve: int) -> list[int]:
    """World preamble, chunks as documents, question, answer marker.

    Chunks are packed until the budget runs out, and the question is
    always kept, so a long archive costs context rather than the ask.
    """
    sid = tokenizer.special_ids
    head = [sid["<|world|>"], *tokenizer.encode(
        render_world_preamble({"domain": "primitive_suite"}))]
    tail = [sid["<|q|>"], *tokenizer.encode(question), sid["<|a|>"]]
    budget = max_len - reserve - len(head) - len(tail)
    body: list[int] = []
    for chunk in chunks or []:
        text = chunk["text"] if isinstance(chunk, dict) else str(chunk)
        ids = [sid["<|doc|>"], *tokenizer.encode(text)]
        if len(ids) > budget:
            continue
        body.extend(ids)
        budget -= len(ids)
    ids = head + body + tail
    if len(ids) > max_len - reserve:
        # Keep the tail: the question and the answer marker live there.
        ids = ids[-(max_len - reserve):]
    return ids


def _decode_answer(tokenizer, generated: list[int]) -> str:
    sid = tokenizer.special_ids
    stop = set(sid.values())
    out: list[int] = []
    for t in generated:
        if t in stop:
            break
        out.append(t)
    return tokenizer.decode(out)


class CheckpointPredictor:
    """predict(question, chunks) -> str over a trainer checkpoint.

    Calls are buffered so decoding runs in batches. The runner drives one
    item at a time, so flushing happens per call by default; set batch to
    one to make that explicit or use predict_many for real batching.
    """

    def __init__(self, ckpt_path: str, tokenizer_path: str, device=None,
                 temperature: float = DEFAULT_TEMPERATURE,
                 top_k: int = DEFAULT_TOP_K,
                 max_new_tokens: int = DEFAULT_MAX_NEW,
                 seed: int = 1234, max_len: int | None = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, self.state = load_checkpoint_model(ckpt_path, self.device)
        self.model.eval()
        self.tokenizer = load_tokenizer(tokenizer_path)
        self.temperature = float(temperature)
        self.top_k = int(top_k)
        self.max_new_tokens = int(max_new_tokens)
        self.seed = int(seed)
        cap = self.model.cfg.max_seq_len
        self.max_len = min(int(max_len or cap), cap)
        self.calls = 0
        self.truncated = 0

    def meta(self) -> dict:
        return {"temperature": self.temperature, "top_k": self.top_k,
                "max_new_tokens": self.max_new_tokens,
                "max_seq_len": self.max_len, "seed": self.seed,
                "step": int(self.state.get("step", -1)),
                "calls": self.calls, "truncated_prompts": self.truncated}

    def predict_many(self, pairs) -> list[str]:
        """pairs is a sequence of (question, chunks). One batched decode."""
        prompts = []
        for question, chunks in pairs:
            ids = build_prompt_ids(question, chunks, self.tokenizer,
                                   self.max_len, self.max_new_tokens + 4)
            full = len(self.tokenizer.encode(question))
            if full + 8 > self.max_len - self.max_new_tokens:
                self.truncated += 1
            prompts.append(ids)
        self.calls += len(prompts)
        policy = CachedPolicy(self.model, self.device, max_len=self.max_len,
                              temperature=self.temperature, top_k=self.top_k,
                              seed=self.seed)
        eot = self.tokenizer.special_ids["<|eot|>"]
        outs: list[list[int]] = [[] for _ in prompts]
        done = [False] * len(prompts)
        toks = policy.begin(prompts)
        for _ in range(self.max_new_tokens):
            for i, t in enumerate(toks):
                if done[i]:
                    continue
                if t == eot:
                    done[i] = True
                    continue
                outs[i].append(int(t))
            if all(done):
                break
            feed = [PAD_TOKEN if done[i] else toks[i]
                    for i in range(len(toks))]
            try:
                toks = policy.advance(feed)
            except ValueError:
                break
        return [_decode_answer(self.tokenizer, o) for o in outs]

    def __call__(self, question: str, chunks=None) -> str:
        return self.predict_many([(question, chunks)])[0]


class BatchedPredictor:
    """Wraps a CheckpointPredictor so the single-item runner still batches.

    The runner calls predict once per item. This collects those calls by
    running the whole item list through predict_many first, then serving
    the answers back from a cache keyed by the prompt. Nothing about the
    runner changes; it simply finds every answer already computed.
    """

    def __init__(self, predictor: CheckpointPredictor, batch: int = 16):
        self.predictor = predictor
        self.batch = int(batch)
        self.cache: dict[str, str] = {}

    def warm(self, pairs, progress=None) -> None:
        pairs = list(pairs)
        for start in range(0, len(pairs), self.batch):
            block = pairs[start:start + self.batch]
            for (q, c), text in zip(block, self.predictor.predict_many(block)):
                self.cache[q] = text
            if progress:
                progress(f"    decoded {min(start + self.batch, len(pairs))}"
                         f"/{len(pairs)}")

    def __call__(self, question: str, chunks=None) -> str:
        hit = self.cache.get(question)
        if hit is not None:
            return hit
        text = self.predictor(question, chunks)
        self.cache[question] = text
        return text
