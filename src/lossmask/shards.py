"""Tagged shards: the existing uint16 token stream plus a uint8 tag stream.

Layout, next to a plain shard directory rather than instead of one:

    index.json           the same keys src/train/data.py writes, with a
                         tag_file added inside each shard entry and
                         tag_dtype and tag_names added at the top level
    shard-00000.bin      uint16 tokens, byte identical to a plain render
    shard-00000.tag.bin  uint8 tags, one per token

The compatibility contract runs both ways. src.train.data.ShardReader opens
a tagged directory unchanged, because everything it reads is still there and
it ignores the keys it does not know, so every existing tool trains and
evaluates on this data as if the tags were not written. And TaggedShardReader
opens a plain directory too, serving an all-plain tag stream, so a weighted
run can be pointed at untagged data and gets the control arm rather than an
error.

Shard files may be named with a relative path, so a directory of chunks
written by parallel workers becomes one readable stream by writing one
top level index over them with no merge pass.
"""

import json
from pathlib import Path

import numpy as np

from src.lossmask.tags import TAG_NAMES
from src.train.data import INDEX_NAME, SHARD_DTYPE, ShardReader
from src.train.data import BatchLoader

TAG_DTYPE = np.uint8
TAG_SUFFIX = ".tag.bin"


class TaggedShardWriter:
    """Buffers tokens and their tags and writes both streams in lockstep."""

    def __init__(self, out_dir: str, prefix: str = "shard",
                 shard_size: int = 1 << 24):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.shard_size = shard_size
        self.tokens: list[np.ndarray] = []
        self.tags: list[np.ndarray] = []
        self.buffered = 0
        self.shards: list[dict] = []
        self.histogram = np.zeros(len(TAG_NAMES) + 4, dtype=np.int64)
        self.closed = False

    def write(self, tokens, tags) -> None:
        tok = np.asarray(tokens)
        tag = np.asarray(tags)
        if tok.size != tag.size:
            raise ValueError(
                f"{tok.size} tokens against {tag.size} tags; the two streams "
                "must stay in lockstep")
        if tok.size == 0:
            return
        if tok.min() < 0 or tok.max() >= 1 << 16:
            raise ValueError("token ids must fit in uint16")
        if tag.min() < 0 or tag.max() >= 1 << 8:
            raise ValueError("tags must fit in uint8")
        self.histogram += np.bincount(
            tag.astype(np.int64), minlength=self.histogram.size)
        self.tokens.append(tok.astype(SHARD_DTYPE))
        self.tags.append(tag.astype(TAG_DTYPE))
        self.buffered += int(tok.size)
        while self.buffered >= self.shard_size:
            self._flush(self.shard_size)

    def _flush(self, count: int) -> None:
        tok = np.concatenate(self.tokens)
        tag = np.concatenate(self.tags)
        name = f"{self.prefix}-{len(self.shards):05d}.bin"
        tok[:count].tofile(self.out_dir / name)
        tag[:count].tofile(self.out_dir / (name + TAG_SUFFIX))
        self.shards.append({"file": name, "num_tokens": int(count),
                            "tag_file": name + TAG_SUFFIX})
        rest_tok, rest_tag = tok[count:], tag[count:]
        self.tokens = [rest_tok] if rest_tok.size else []
        self.tags = [rest_tag] if rest_tag.size else []
        self.buffered = int(rest_tok.size)

    def close(self) -> dict:
        if not self.closed:
            if self.buffered > 0:
                self._flush(self.buffered)
            with open(self.out_dir / INDEX_NAME, "w") as fh:
                json.dump(self.index(), fh, indent=2)
            self.closed = True
        return self.index()

    def index(self) -> dict:
        return {
            "dtype": "uint16",
            "tag_dtype": "uint8",
            "tag_names": {str(k): v for k, v in sorted(TAG_NAMES.items())},
            "shards": self.shards,
            "total_tokens": int(sum(s["num_tokens"] for s in self.shards)),
            "tag_histogram": {
                str(i): int(c) for i, c in enumerate(self.histogram) if c},
        }


def write_index(out_dir, shards: list[dict], histogram=None) -> dict:
    """Write a top level index over shard entries that may name files in
    subdirectories, so parallel chunk writers need no merge pass."""
    index = {
        "dtype": "uint16",
        "tag_dtype": "uint8",
        "tag_names": {str(k): v for k, v in sorted(TAG_NAMES.items())},
        "shards": shards,
        "total_tokens": int(sum(s["num_tokens"] for s in shards)),
    }
    if histogram:
        index["tag_histogram"] = {str(k): int(v) for k, v in histogram.items()}
    with open(Path(out_dir) / INDEX_NAME, "w") as fh:
        json.dump(index, fh, indent=2)
    return index


class TaggedShardReader(ShardReader):
    """A ShardReader that also serves the tag stream.

    Opening a plain shard directory is legal and serves all-plain tags, so
    the weighted training path degrades to the control arm on untagged data
    instead of failing.
    """

    def __init__(self, shard_dir: str):
        super().__init__(shard_dir)
        self.tagged = all("tag_file" in s for s in self.index["shards"])
        self.tag_maps = []
        if self.tagged:
            for shard, tokens in zip(self.index["shards"], self.maps):
                path = self.shard_dir / shard["tag_file"]
                mm = np.memmap(path, dtype=TAG_DTYPE, mode="r")
                if mm.size != tokens.size:
                    raise ValueError(
                        f"{path} holds {mm.size} tags for {tokens.size} tokens")
                self.tag_maps.append(mm)

    def get_tag_slice(self, start: int, length: int) -> np.ndarray:
        if not self.tagged:
            return np.zeros(length, dtype=TAG_DTYPE)
        if start < 0 or start + length > self.total_tokens:
            raise IndexError("slice out of range")
        out = np.empty(length, dtype=TAG_DTYPE)
        filled = 0
        pos = start
        while filled < length:
            idx = int(np.searchsorted(self.offsets, pos, side="right")) - 1
            local = pos - int(self.offsets[idx])
            take = min(length - filled, self.tag_maps[idx].size - local)
            out[filled:filled + take] = self.tag_maps[idx][local:local + take]
            filled += take
            pos += take
        return out


class WeightedBatchLoader(BatchLoader):
    """BatchLoader that also yields the per token loss weight of the targets.

    The draw stream is the parent's, untouched: this subclass consumes the
    rng exactly as BatchLoader does, so a weighted run and a plain run at
    the same seed read the same offsets in the same order and the arms of a
    weighting experiment differ only in the third tensor.

    That tensor is aligned with targets, not with inputs. Position i of a
    batch predicts token i + 1, so the weight that matters is the tag of the
    token being predicted, and the loader indexes the tag stream from one.
    """

    def __init__(self, source, batch_size: int, seq_len: int, weight_table,
                 seed: int = 0, rank: int = 0, world_size: int = 1):
        super().__init__(source, batch_size, seq_len, seed=seed, rank=rank,
                         world_size=world_size)
        self.weight_table = np.asarray(weight_table, dtype=np.float32)

    def next_batch(self):
        import torch

        starts = self.region_start + self.rng.integers(
            0, self.high, size=self.batch_size, endpoint=True)
        self.batches_drawn += 1
        rows = np.stack([
            self.source.get_slice(int(s), self.seq_len + 1).astype(np.int64)
            for s in starts])
        tags = np.stack([
            self.source.get_tag_slice(int(s) + 1, self.seq_len)
            for s in starts])
        batch = torch.from_numpy(rows)
        weights = torch.from_numpy(self.weight_table[tags])
        return (batch[:, :-1].contiguous(), batch[:, 1:].contiguous(),
                weights.contiguous())
