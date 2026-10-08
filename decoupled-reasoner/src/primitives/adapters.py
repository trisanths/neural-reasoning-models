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

    Most items in this suite carry their material inside the question and
    hand the same text over as chunks, so an adapter can use whichever
    channel its model was trained on. Rendering both would state the
    archive twice, which on the longest items pushes the prompt into the
    context limit and truncates the brief the question depends on. A chunk
    whose text is already in the question is therefore dropped.

    Chunks that do add something are packed until the budget runs out, and
    the question is always kept, so a long archive costs context rather
    than the ask.
    """
    sid = tokenizer.special_ids
    head = [sid["<|world|>"], *tokenizer.encode(
        render_world_preamble({"domain": "primitive_suite"}))]
    tail = [sid["<|q|>"], *tokenizer.encode(question), sid["<|a|>"]]
    budget = max_len - reserve - len(head) - len(tail)
    body: list[int] = []
    for chunk in chunks or []:
        text = chunk["text"] if isinstance(chunk, dict) else str(chunk)
        if text in question:
            continue
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
        self.choices = 0
        self.truncated = 0

    def meta(self) -> dict:
        return {"temperature": self.temperature, "top_k": self.top_k,
                "max_new_tokens": self.max_new_tokens,
                "max_seq_len": self.max_len, "seed": self.seed,
                "step": int(self.state.get("step", -1)),
                "calls": self.calls, "forced_choices": self.choices,
                "truncated_prompts": self.truncated,
                "greedy": self.temperature <= 0.0}

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
        # The key and value cache is allocated for max_len positions on
        # every layer, which at a 4096 window and a 24 layer model is
        # gigabytes the batch will never touch. Size it to what this batch
        # actually needs.
        need = max(len(p) for p in prompts) + self.max_new_tokens + 2
        policy = CachedPolicy(self.model, self.device,
                              max_len=min(self.max_len, need),
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

    def _option_nlls(self, ctx_ids, options) -> list[tuple]:
        """(summed negative log likelihood, token count) for each option.

        The sum is the quantity src/evals/mc.option_nll computes, batched
        across the options of one prompt. Padding goes on the right:
        attention is causal, so nothing after an option can influence it,
        and every sequence still starts at rotary position zero.

        The token count comes back because the sum is not comparable
        across options of different lengths. Where an item's correct
        option is systematically the longest, and several here are, a
        summed score picks the shortest option almost every time and the
        result reads as a faculty of zero when it is an artefact of
        length. The caller divides.
        """
        cap = self.max_len
        seqs, lens = [], []
        for opt in options:
            oid = (self.tokenizer.encode(opt)
                   or self.tokenizer.encode(" " + opt))
            seq = list(ctx_ids) + oid
            if len(seq) > cap:
                seq = seq[-cap:]
            seqs.append(seq)
            lens.append(min(len(oid), len(seq) - 1))
        width = max(len(s) for s in seqs)
        x = torch.full((len(seqs), width), 0, dtype=torch.long,
                       device=self.device)
        for i, s in enumerate(seqs):
            x[i, :len(s)] = torch.tensor(s, dtype=torch.long,
                                         device=self.device)
        with torch.no_grad():
            logits, _ = self.model(x)
            logprobs = torch.log_softmax(logits[:, :-1].float(), dim=-1)
        out = []
        for i, s in enumerate(seqs):
            n, end = lens[i], len(s)
            tgt = x[i, end - n:end]
            got = logprobs[i, end - n - 1:end - 1].gather(1, tgt.unsqueeze(1))
            out.append((float(-got.sum().item()), max(1, n)))
        return out

    def choose_both(self, question: str, chunks=None, options=()) -> tuple:
        """(length-normalised pick, summed pick) over the option texts.

        The prompt ends at the answer marker and each option is scored as
        the continuation, which is what the held-out suite already does
        for multiple choice. The normalised pick is the reported one and
        the summed pick is carried beside it, so a reader can see when the
        two disagree and how much of a score is option length. Ties break
        toward the earliest option, so both channels are deterministic
        whatever the decoding temperature is.
        """
        ids = build_prompt_ids(question, chunks, self.tokenizer,
                               self.max_len, 32)
        scored = self._option_nlls(ids, list(options))
        self.choices += 1
        norm = min(range(len(scored)),
                   key=lambda i: (scored[i][0] / scored[i][1], i))
        total = min(range(len(scored)), key=lambda i: (scored[i][0], i))
        return norm, total

    def choose_many(self, triples) -> list[int]:
        return [self.choose_both(q, c, o)[0] for q, c, o in triples]

    def choose(self, question: str, chunks=None, options=()) -> int:
        return self.choose_both(question, chunks, options)[0]


class BatchedPredictor:
    """Wraps a CheckpointPredictor so the single-item runner still batches.

    The runner calls predict once per item. This collects those calls by
    running the whole item list through predict_many first, then serving
    the answers back from a cache keyed by the prompt. Nothing about the
    runner changes; it simply finds every answer already computed.

    Batches are formed against a token budget rather than a fixed count,
    because a batch of long prompts costs far more cache than the same
    count of short ones, and this project's boxes share their GPUs.
    A batch that runs out of memory anyway is halved and retried down to
    one prompt, so a crowded card costs time and not a run.
    """

    def __init__(self, predictor: CheckpointPredictor, batch: int = 16,
                 char_budget: int | None = None):
        self.predictor = predictor
        self.batch = int(batch)
        self.char_budget = int(char_budget or self.batch * 1200)
        self.cache: dict[str, str] = {}
        self.retries = 0

    def _blocks(self, pairs):
        block: list = []
        widest = 0
        for pair in pairs:
            width = max(widest, len(pair[0]))
            if block and (len(block) + 1 > self.batch
                          or width * (len(block) + 1) > self.char_budget):
                yield block
                block, widest = [pair], len(pair[0])
                continue
            block.append(pair)
            widest = width
        if block:
            yield block

    def _decode(self, block) -> None:
        try:
            for (q, _), text in zip(block, self.predictor.predict_many(block)):
                self.cache[q] = text
            return
        except torch.OutOfMemoryError:
            if len(block) == 1:
                raise
            self.retries += 1
            torch.cuda.empty_cache()
        half = max(1, len(block) // 2)
        self._decode(block[:half])
        self._decode(block[half:])

    def warm(self, pairs, progress=None) -> None:
        """Decode everything the suite will ask for, shortest prompts first.

        Mixing lengths in one batch wastes the whole batch's cache on its
        longest member, so prompts are grouped by size. The cache is keyed
        by prompt, so the order they were decoded in is invisible to the
        runner.
        """
        pairs = sorted(pairs, key=lambda qc: len(qc[0]))
        done = 0
        for block in self._blocks(pairs):
            self._decode(block)
            done += len(block)
            if progress:
                progress(f"    decoded {done}/{len(pairs)}")

    def __call__(self, question: str, chunks=None) -> str:
        hit = self.cache.get(question)
        if hit is not None:
            return hit
        text = self.predictor(question, chunks)
        self.cache[question] = text
        return text

    def choose(self, question: str, chunks=None, options=()) -> int:
        return self.predictor.choose(question, chunks, options)

    def choose_both(self, question: str, chunks=None, options=()) -> tuple:
        return self.predictor.choose_both(question, chunks, options)
