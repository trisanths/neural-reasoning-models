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

    Data parallel sharding. The stream is cut into world_size contiguous
    regions and a rank only ever samples inside its own region, so two ranks
    never read the same token and the regions together cover the whole stream
    apart from the last seq_len + 1 tokens of each region, which no legal
    start position can reach. Any leftover from an uneven division rides with
    the last rank. Rank zero of a world of one owns the whole stream and draws
    exactly the offsets the single GPU loader has always drawn, so nothing
    about single GPU training moves.

    Resuming. The draw stream is a plain counter based fast forward: the
    checkpoint records how many batches this loader has produced, and
    load_state_dict reseeds and replays that many draws, which puts every rank
    back on the offset it would have reached without the interruption.
    """

    # Spacing between per rank seeds. Prime, and far larger than any run
    # length, so no two ranks land on overlapping stretches of the stream.
    RANK_SEED_STRIDE = 1_000_003

    def __init__(
        self,
        source,
        batch_size: int,
        seq_len: int,
        seed: int = 0,
        rank: int = 0,
        world_size: int = 1,
    ):
        if world_size < 1:
            raise ValueError(f"world_size must be at least 1, got {world_size}")
        if not 0 <= rank < world_size:
            raise ValueError(f"rank {rank} outside a world of {world_size}")
        span = source.total_tokens // world_size
        self.region_start = rank * span
        self.region_end = source.total_tokens if rank == world_size - 1 else self.region_start + span
        region_tokens = self.region_end - self.region_start
        if region_tokens < seq_len + 2:
            if world_size == 1:
                raise ValueError("token source is shorter than one training sequence")
            raise ValueError(
                f"rank {rank} of {world_size} gets {region_tokens} tokens, which is "
                f"shorter than one training sequence of {seq_len + 1}; use fewer ranks "
                "or more data"
            )
        self.source = source
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.seed = seed
        self.rank = rank
        self.world_size = world_size
        self.rank_seed = seed + rank * self.RANK_SEED_STRIDE
        # Largest offset inside this region that still leaves a full sequence.
        self.high = region_tokens - seq_len - 1
        self.rng = np.random.default_rng(self.rank_seed)
        self.batches_drawn = 0

    def next_batch(self) -> tuple[torch.Tensor, torch.Tensor]:
        starts = self.region_start + self.rng.integers(
            0, self.high, size=self.batch_size, endpoint=True
        )
        self.batches_drawn += 1
        rows = np.stack(
            [self.source.get_slice(int(s), self.seq_len + 1).astype(np.int64) for s in starts]
        )
        batch = torch.from_numpy(rows)
        return batch[:, :-1].contiguous(), batch[:, 1:].contiguous()

    def skip(self, batches: int) -> None:
        """Advance the draw stream without touching the token source. Drawing
        n batches worth of offsets in one call leaves the generator in the same
        state as n separate calls."""
        if batches <= 0:
            return
        self.rng.integers(0, self.high, size=batches * self.batch_size, endpoint=True)
        self.batches_drawn += batches

    def state_dict(self) -> dict:
        return {
            "batches_drawn": int(self.batches_drawn),
            "batch_size": int(self.batch_size),
            "seq_len": int(self.seq_len),
            "seed": int(self.seed),
            "rank": int(self.rank),
            "world_size": int(self.world_size),
        }

    def load_state_dict(self, state: dict) -> None:
        """Put this loader back where the saved one was. The saved position is
        a batch count, which every rank shares, so one rank's record restores
        the whole world."""
        self.rng = np.random.default_rng(self.rank_seed)
        self.batches_drawn = 0
        self.skip(int(state["batches_drawn"]))

    def __iter__(self):
        while True:
            yield self.next_batch()
