"""Token shard io, episode rendering, and fixed length batch loading.

Shard format: each shard is a flat little endian uint16 file. An index.json in
the shard directory records the dtype, per shard token counts, and the total.

Procgen warm up convention: a procgen .bin file is a flat little endian uint16
stream of raw symbol ids in [0, PROCGEN_SYMBOLS), that is [0, 256). The
tokenizer reserves vocabulary ids [PROCGEN_OFFSET, PROCGEN_OFFSET +
PROCGEN_SYMBOLS), which is [7, 263), immediately after the seven named special
tokens. A raw symbol id s therefore maps to vocabulary id PROCGEN_OFFSET + s,
and load_procgen_bin applies that offset. The warm up stream never emits the
named special tokens or any learned BPE token.
"""

import json
from pathlib import Path

import numpy as np
import torch

from src.train.tokenizer import PROCGEN_OFFSET, PROCGEN_SYMBOLS, TrainTokenizer

INDEX_NAME = "index.json"
SHARD_DTYPE = np.uint16


class ShardWriter:
    """Buffers uint16 tokens and writes fixed size shard files plus an index."""

    def __init__(self, out_dir: str, prefix: str = "shard", shard_size: int = 1 << 24):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.shard_size = shard_size
        self.buffer: list[np.ndarray] = []
        self.buffered = 0
        self.shards: list[dict] = []
        self.closed = False

    def write(self, tokens) -> None:
        arr = np.asarray(tokens)
        if arr.size == 0:
            return
        if arr.min() < 0 or arr.max() >= 1 << 16:
            raise ValueError("token ids must fit in uint16")
        arr = arr.astype(SHARD_DTYPE)
        self.buffer.append(arr)
        self.buffered += arr.size
        while self.buffered >= self.shard_size:
            self._flush_shard(self.shard_size)

    def _flush_shard(self, count: int) -> None:
        flat = np.concatenate(self.buffer)
        chunk, rest = flat[:count], flat[count:]
        name = f"{self.prefix}-{len(self.shards):05d}.bin"
        chunk.tofile(self.out_dir / name)
        self.shards.append({"file": name, "num_tokens": int(chunk.size)})
        self.buffer = [rest] if rest.size else []
        self.buffered = int(rest.size)

    def close(self) -> None:
        if self.closed:
            return
        if self.buffered > 0:
            self._flush_shard(self.buffered)
        index = {
            "dtype": "uint16",
            "shards": self.shards,
            "total_tokens": int(sum(s["num_tokens"] for s in self.shards)),
        }
        with open(self.out_dir / INDEX_NAME, "w") as fh:
            json.dump(index, fh, indent=2)
        self.closed = True


class ShardReader:
    """Memory maps the shards named in index.json and serves flat slices."""

    def __init__(self, shard_dir: str):
        self.shard_dir = Path(shard_dir)
        with open(self.shard_dir / INDEX_NAME) as fh:
            self.index = json.load(fh)
        if self.index["dtype"] != "uint16":
            raise ValueError(f"unsupported shard dtype {self.index['dtype']}")
        self.maps = [
            np.memmap(self.shard_dir / s["file"], dtype=SHARD_DTYPE, mode="r")
            for s in self.index["shards"]
        ]
        sizes = [s["num_tokens"] for s in self.index["shards"]]
        for mm, size in zip(self.maps, sizes):
            if mm.size != size:
                raise ValueError("shard file size disagrees with index")
        self.offsets = np.concatenate([[0], np.cumsum(sizes)])
        self.total_tokens = int(self.offsets[-1])

    def get_slice(self, start: int, length: int) -> np.ndarray:
        if start < 0 or start + length > self.total_tokens:
            raise IndexError("slice out of range")
        out = np.empty(length, dtype=SHARD_DTYPE)
        filled = 0
        pos = start
        while filled < length:
            shard_idx = int(np.searchsorted(self.offsets, pos, side="right")) - 1
            local = pos - int(self.offsets[shard_idx])
            take = min(length - filled, self.maps[shard_idx].size - local)
            out[filled : filled + take] = self.maps[shard_idx][local : local + take]
            filled += take
            pos += take
        return out


class ArraySource:
    """Adapts an in memory token array to the reader interface."""

    def __init__(self, tokens: np.ndarray):
        self.tokens = np.asarray(tokens, dtype=SHARD_DTYPE)
        self.total_tokens = int(self.tokens.size)

    def get_slice(self, start: int, length: int) -> np.ndarray:
        if start < 0 or start + length > self.total_tokens:
            raise IndexError("slice out of range")
        return self.tokens[start : start + length]


def load_procgen_bin(path: str) -> np.ndarray:
    """Read a raw procgen stream and shift it into the reserved vocab range."""
    arr = np.fromfile(path, dtype=SHARD_DTYPE)
    if arr.size == 0:
        raise ValueError(f"empty procgen stream {path}")
    if int(arr.max()) >= PROCGEN_SYMBOLS:
        raise ValueError(
            f"procgen symbol id {int(arr.max())} outside [0, {PROCGEN_SYMBOLS})"
        )
    return arr + PROCGEN_OFFSET


def render_world_preamble(world: dict) -> str:
    """Serialize the world header as plain text. Facts stay out of the preamble
    because the documents carry them and the questions test recovering them."""
    lines = [f"domain: {world.get('domain', 'unknown')}"]
    for ent in world.get("entities", []):
        lines.append(f"entity {ent['id']} {ent.get('type', '')} {ent.get('name', '')}".rstrip())
    for rule in world.get("rules", []):
        lines.append(f"rule: {rule}")
    return "\n".join(lines)


def render_episode(
    episode: dict, tokenizer: TrainTokenizer, max_doc_tokens: int | None = None
) -> list[int]:
    """Convert one worldgen episode into a token stream.

    Layout: <|world|> preamble, then <|doc|> text per document, then
    <|q|> question <|a|> answer <|eot|> per question. When max_doc_tokens is
    set, documents are included in order until the budget is exhausted; the
    rest are reachable only through retrieval, per SPEC.md section 2.
    """
    sid = tokenizer.special_ids
    tokens: list[int] = [sid["<|world|>"]]
    tokens.extend(tokenizer.encode(render_world_preamble(episode.get("world", {}))))
    doc_budget = max_doc_tokens
    for doc in episode.get("documents", []):
        doc_tokens = tokenizer.encode(doc["text"])
        cost = len(doc_tokens) + 1
        if doc_budget is not None:
            if cost > doc_budget:
                break
            doc_budget -= cost
        tokens.append(sid["<|doc|>"])
        tokens.extend(doc_tokens)
    for question in episode.get("questions", []):
        tokens.append(sid["<|q|>"])
        tokens.extend(tokenizer.encode(question["text"]))
        tokens.append(sid["<|a|>"])
        tokens.extend(tokenizer.encode(question["answer"]))
        tokens.append(sid["<|eot|>"])
    return tokens


def render_jsonl_to_shards(
    jsonl_path: str,
    tokenizer: TrainTokenizer,
    out_dir: str,
    max_doc_tokens: int | None = None,
    shard_size: int = 1 << 24,
) -> int:
    """Render every episode in a worldgen JSONL file into uint16 shards.
    Returns the total token count."""
    writer = ShardWriter(out_dir, shard_size=shard_size)
    total = 0
    with open(jsonl_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            episode = json.loads(line)
            tokens = render_episode(episode, tokenizer, max_doc_tokens=max_doc_tokens)
            writer.write(tokens)
            total += len(tokens)
    writer.close()
    return total


class BatchLoader:
    """Yields fixed length next token prediction batches from a token source.

    The source is anything with total_tokens and get_slice, so shard
    directories and in memory procgen streams load the same way. Sampling is
    deterministic for a given seed.
    """

    def __init__(self, source, batch_size: int, seq_len: int, seed: int = 0):
        if source.total_tokens < seq_len + 2:
            raise ValueError("token source is shorter than one training sequence")
        self.source = source
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.rng = np.random.default_rng(seed)

    def next_batch(self) -> tuple[torch.Tensor, torch.Tensor]:
        high = self.source.total_tokens - self.seq_len - 1
        starts = self.rng.integers(0, high, size=self.batch_size, endpoint=True)
        rows = np.stack(
            [self.source.get_slice(int(s), self.seq_len + 1).astype(np.int64) for s in starts]
        )
        batch = torch.from_numpy(rows)
        return batch[:, :-1].contiguous(), batch[:, 1:].contiguous()

    def __iter__(self):
        while True:
            yield self.next_batch()
