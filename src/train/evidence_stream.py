"""The training stream for the evidence cross-attention lane.

src/train/data.py streams token windows, which is the wrong unit here: an
evidence example is a question, a bank of retrievable chunks, and an answer,
and the bank has to be rebuilt per example. This module produces those
examples from two sources and batches them through EvidenceCollator.

  worldgen   src.worldgen.engine episodes generated on the fly. Cheap, index
             addressable from a seed, and unbounded, so the lane never sees
             the same world twice and nothing can be memorized from a fixed
             file. Gold chunks are the windows of documents that support a
             fact in the question's derivation.
  web        scrubbed-web episodes read from the JSONL that
             scripts/render_evidence_web.py pre-renders. Rendering one costs
             a parquet read, a scrub pass, and a BM25 verification, which is
             far too much CPU to run beside a training step, so these are
             built once and read back.

INDEXING. Everything is a pure function of (seed, example index). Example
index i maps to episode index i // questions_per_episode and question slot
i % questions_per_episode, so the Q consecutive examples of one episode share
a single generation through a one-entry cache, and a run that resumes at
optimizer step N recreates exactly the examples it would have seen. There is
no shuffling buffer and no iterator state to checkpoint.

THE POOL. An episode owns twenty-odd documents, which is far short of a bank
of 256, so the rest is filled from a pool of chunks harvested once at stream
construction from its own set of pool episodes. The pool is fixed for the
run, which is what makes bank composition reproducible; it is drawn from a
different seed stream than the training episodes, so a pool chunk is never
the gold chunk of the example it pads.
"""

from __future__ import annotations

import json
import queue
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.train.evidence_data import (EvidenceCollator, EvidenceExample,
                                     chunk_document, episode_chunks,
                                     examples_from_episode,
                                     examples_from_web_episode, hash_str)
from src.worldgen.domains import DOMAIN_ORDER
from src.worldgen.engine import episode_seed, make_episode

# Independent seed offsets so the pool, the source coin, and the episodes
# never share a stream.
POOL_OFFSET = 90001
COIN_OFFSET = 90011
BANK_OFFSET = 90017

# Sentinel for the prefetch queue: the producer puts this when the source
# iterator ends or raises, so the consumer never blocks forever.
_END = object()


def _prefetched(source, depth: int):
    """Yield from `source` with up to `depth` items built ahead on a thread.

    The thread is a daemon and the queue is bounded, so a consumer that stops
    early leaves at most `depth` built batches behind and nothing to join. An
    exception in the producer is re-raised in the consumer at the point it
    would have been raised without prefetching.
    """
    q: queue.Queue = queue.Queue(maxsize=depth)

    def produce():
        try:
            for item in source:
                q.put(item)
        except BaseException as exc:  # re-raised on the consumer side
            q.put((_END, exc))
            return
        q.put((_END, None))

    thread = threading.Thread(target=produce, daemon=True)
    thread.start()
    while True:
        item = q.get()
        if isinstance(item, tuple) and len(item) == 2 and item[0] is _END:
            if item[1] is not None:
                raise item[1]
            return
        yield item


@dataclass
class StreamConfig:
    """Knobs for the example stream, read from the `data` config section."""

    bank_size: int = 256
    chunk_len: int = 128
    bank_mode: str = "oracle"
    pool_chunks: int = 4096
    pool_episodes: int = 64
    questions_per_episode: int = 4
    web_share: float = 0.0
    max_question_tokens: int = 256
    max_answer_tokens: int = 64
    contradiction_rate: float = 0.15
    filler_rate: float = 0.25
    prefetch: int = 4
    seed: int = 1234

    def __post_init__(self):
        if not 0.0 <= self.web_share <= 1.0:
            raise ValueError("web_share must be between 0 and 1")
        if self.questions_per_episode < 1:
            raise ValueError("questions_per_episode must be at least 1")
        if self.bank_size < 1:
            raise ValueError("bank_size must be at least 1")


def config_from_yaml(cfg: dict) -> StreamConfig:
    """Build a StreamConfig from the `data` section of a yaml config."""
    fields = set(StreamConfig.__dataclass_fields__)
    unknown = set(cfg) - fields
    if unknown:
        raise ValueError(f"unknown data config keys: {sorted(unknown)}")
    return StreamConfig(**cfg)


def load_web_episodes(path: str | None) -> list:
    """Read the pre-rendered scrubbed-web episodes, or return an empty list."""
    if not path:
        return []
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"web episode file {p} does not exist")
    episodes = []
    with open(p) as fh:
        for line in fh:
            line = line.strip()
            if line:
                episodes.append(json.loads(line))
    if not episodes:
        raise ValueError(f"web episode file {p} is empty")
    return episodes


class EvidenceStream:
    """Index addressable (question, bank, answer) examples from two sources.

    The stream is infinite: episode indices keep counting up and worldgen
    generates a fresh world for each one. Web episodes are a finite file and
    are cycled, so a long run revisits them; their share is what bounds how
    often that happens.
    """

    def __init__(self, tokenizer, cfg: StreamConfig, web_episodes: list | None = None,
                 domains: list | None = None):
        self.tok = tokenizer
        self.cfg = cfg
        self.web = list(web_episodes or [])
        if cfg.web_share > 0 and not self.web:
            raise ValueError("web_share is positive but no web episodes were given")
        self.domains = list(domains or DOMAIN_ORDER)
        self.pool = self._build_pool()
        self._cache_key = None
        self._cache_examples: list = []
        self.counts = {"worldgen": 0, "web": 0}

    # ---- pool ----

    def _build_pool(self) -> list:
        """Harvest a fixed chunk pool from its own episodes.

        Worldgen pool episodes come first because they are free; if the run
        carries web episodes, a proportional slice of the pool is taken from
        them so the padding of a web example is not exclusively synthetic.
        """
        cfg = self.cfg
        chunks: list = []
        n_web_pool = int(round(cfg.pool_episodes * cfg.web_share)) if self.web else 0
        n_world_pool = max(1, cfg.pool_episodes - n_web_pool)
        for k in range(n_world_pool):
            ep = make_episode(
                episode_seed(cfg.seed + POOL_OFFSET, k),
                f"pool-{k:06d}", self.domains[k % len(self.domains)],
                contradiction_rate=cfg.contradiction_rate,
                filler_rate=cfg.filler_rate)
            chunks.extend(episode_chunks(ep, self.tok, cfg.chunk_len,
                                         source=f"pool-{k:06d}"))
            if len(chunks) >= cfg.pool_chunks:
                return chunks[:cfg.pool_chunks]
        for k in range(n_web_pool):
            ep = self.web[(k * 7919) % len(self.web)]
            for i, doc in enumerate(ep["documents"]):
                chunks.extend(chunk_document(
                    doc["text"], self.tok, cfg.chunk_len, reliability=1.0,
                    source=f"pool-web-{k:06d}", doc_index=i))
            if len(chunks) >= cfg.pool_chunks:
                break
        return chunks[:cfg.pool_chunks]

    # ---- example addressing ----

    def is_web(self, episode_index: int) -> bool:
        """Deterministic source coin for one episode index."""
        if not self.web or self.cfg.web_share <= 0:
            return False
        if self.cfg.web_share >= 1.0:
            return True
        draw = hash_str(f"src-{self.cfg.seed + COIN_OFFSET}-{episode_index}")
        return (draw % 1_000_000) < int(self.cfg.web_share * 1_000_000)

    def _episode_examples(self, episode_index: int) -> list:
        """Every example of one episode, cached for the Q consecutive uses."""
        if self._cache_key == episode_index:
            return self._cache_examples
        cfg = self.cfg
        seed = cfg.seed + BANK_OFFSET
        if self.is_web(episode_index):
            episode = self.web[episode_index % len(self.web)]
            examples = examples_from_web_episode(
                episode, self.tok, cfg.chunk_len, cfg.bank_size, cfg.bank_mode,
                seed + episode_index, pool_chunks=self.pool)
            self.counts["web"] += 1
        else:
            episode = make_episode(
                episode_seed(cfg.seed, episode_index),
                f"ep-{episode_index:08d}",
                self.domains[episode_index % len(self.domains)],
                contradiction_rate=cfg.contradiction_rate,
                filler_rate=cfg.filler_rate)
            examples = examples_from_episode(
                episode, self.tok, cfg.chunk_len, cfg.bank_size, cfg.bank_mode,
                seed + episode_index, pool_chunks=self.pool)
            self.counts["worldgen"] += 1
        examples = [self._clamp(ex) for ex in examples]
        self._cache_key = episode_index
        self._cache_examples = examples
        return examples

    def _clamp(self, ex: EvidenceExample) -> EvidenceExample:
        """Bound the working sequence so the collator can never overflow."""
        cfg = self.cfg
        q = list(ex.question_ids[:cfg.max_question_tokens])
        a = list(ex.answer_ids[:cfg.max_answer_tokens])
        if len(q) == len(ex.question_ids) and len(a) == len(ex.answer_ids):
            return ex
        return EvidenceExample(
            question_ids=q, answer_ids=a, chunks=ex.chunks,
            gold_positions=ex.gold_positions, mode=ex.mode,
            question_text=ex.question_text, answer_text=ex.answer_text,
        )

    def example(self, index: int) -> EvidenceExample:
        """The example at a global index, a pure function of (seed, index)."""
        q = self.cfg.questions_per_episode
        episode_index = index // q
        slot = index % q
        examples = self._episode_examples(episode_index)
        if not examples:
            # An episode that produced no question (a web bundle whose
            # candidates were all dropped) is skipped by advancing to the
            # next episode rather than by retrying this one, so the mapping
            # from index to example stays total and terminating.
            return self.example((episode_index + 1) * q + slot)
        return examples[slot % len(examples)]

    def examples(self, start: int = 0):
        """Infinite iterator of examples from a global start index."""
        i = start
        while True:
            yield self.example(i)
            i += 1

    def batches(self, batch_size: int, collator: EvidenceCollator, start: int = 0,
                prefetch: int | None = None):
        """Infinite iterator of EvidenceBatch, aligned to the global index.

        Building one micro batch of 8 measures 0.051 s, so an optimizer step
        of eight accumulation micro batches spends 0.41 s assembling banks.
        Against a step of roughly 2.3 s that is close to a fifth of the lane,
        paid while the GPU idles, so by default the assembly runs one step
        ahead on a background thread. The queue preserves order, so the
        examples a run sees are the same ones it would see with prefetch off;
        set data.prefetch to 0 to check that.
        """
        depth = self.cfg.prefetch if prefetch is None else prefetch
        if depth <= 0:
            return self._batches(batch_size, collator, start)
        return _prefetched(self._batches(batch_size, collator, start), depth)

    def _batches(self, batch_size: int, collator: EvidenceCollator, start: int = 0):
        it = self.examples(start)
        while True:
            yield collator([next(it) for _ in range(batch_size)])

    def bank_report(self, n: int = 64, start: int = 0) -> dict:
        """Gold hit rate and bank fill over the first n examples, for the dry run."""
        rows = [self.example(start + i) for i in range(n)]
        gold = sum(1 for e in rows if e.gold_present)
        sizes = [len(e.chunks) for e in rows]
        tokens = [sum(len(c.token_ids) for c in e.chunks) for e in rows]
        return {
            "examples": len(rows),
            "gold_present": gold,
            "gold_rate": round(gold / max(1, len(rows)), 4),
            "mean_bank_chunks": round(float(np.mean(sizes)), 2),
            "mean_bank_tokens": round(float(np.mean(tokens)), 1),
            "mean_question_tokens": round(
                float(np.mean([len(e.question_ids) for e in rows])), 2),
            "mean_answer_tokens": round(
                float(np.mean([len(e.answer_ids) for e in rows])), 2),
            "pool_chunks": len(self.pool),
            "episodes_worldgen": self.counts["worldgen"],
            "episodes_web": self.counts["web"],
        }
