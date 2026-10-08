"""Merge chunked regime C shards into one flat shard directory.

scripts/render_regime_c.py writes shards/chunk-XXXXX/ directories, each with
its own index.json and one small shard, plus a chunk-XXXXX.done marker next to
the directory. src.train.data.ShardReader wants a single directory whose
index.json lists every shard file, and memory-mapping 8741 tiny shards would
blow the default open-file limit anyway. This script concatenates the chunk
shards in chunk order into 256 MiB flat shards and writes a combined
index.json, then re-verifies every file size against the index.

Pure stdlib, no repo imports.

Usage:
  python3 consolidate_regime_c.py SRC_SHARDS_DIR DST_DIR [--expect-tokens N]
  python3 consolidate_regime_c.py --verify-only DIR [--expect-tokens N]

Idempotent: when DST_DIR/index.json already verifies (and matches
--expect-tokens if given), the script prints ALREADY_CONSOLIDATED and exits 0.
Exit code 0 only when the destination fully verifies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SHARD_TOKENS = 134217728  # 256 MiB of uint16, same shard size as regime A
DTYPE_BYTES = 2


def verify_flat(dir_path: Path, expect_tokens: int | None) -> int:
    """Check index.json against the files on disk. Returns total tokens."""
    index = json.loads((dir_path / "index.json").read_text())
    if index["dtype"] != "uint16":
        raise SystemExit(f"VERIFY_FAIL {dir_path}: dtype {index['dtype']}")
    total = 0
    for entry in index["shards"]:
        path = dir_path / entry["file"]
        want = entry["num_tokens"] * DTYPE_BYTES
        have = path.stat().st_size
        if have != want:
            raise SystemExit(f"VERIFY_FAIL {path}: {have} bytes, index says {want}")
        total += entry["num_tokens"]
    if total != index.get("total_tokens"):
        raise SystemExit(
            f"VERIFY_FAIL {dir_path}: shard sum {total} != "
            f"index total {index.get('total_tokens')}"
        )
    if expect_tokens is not None and total != expect_tokens:
        raise SystemExit(f"VERIFY_FAIL {dir_path}: total {total}, expected {expect_tokens}")
    print(f"VERIFY_OK {dir_path} shards {len(index['shards'])} total_tokens {total}")
    return total


def collect_sources(src: Path) -> list[Path]:
    """Ordered list of chunk shard files, with per-chunk verification."""
    chunk_dirs = sorted(p for p in src.iterdir() if p.is_dir() and p.name.startswith("chunk-"))
    if not chunk_dirs:
        raise SystemExit(f"no chunk-* directories under {src}")
    files: list[Path] = []
    for chunk in chunk_dirs:
        done = src / (chunk.name + ".done")
        if not done.exists():
            raise SystemExit(f"chunk {chunk.name} has no .done marker; render incomplete?")
        index = json.loads((chunk / "index.json").read_text())
        for entry in index["shards"]:
            path = chunk / entry["file"]
            if path.stat().st_size != entry["num_tokens"] * DTYPE_BYTES:
                raise SystemExit(f"chunk shard size mismatch: {path}")
            files.append(path)
    print(f"sources: {len(chunk_dirs)} chunks, {len(files)} shard files")
    return files


def consolidate(src: Path, dst: Path, expect: int | None) -> None:
    files = collect_sources(src)
    dst.mkdir(parents=True, exist_ok=True)
    shards: list[dict] = []
    out_fh = None
    out_tokens = 0
    total = 0

    def roll() -> None:
        nonlocal out_fh, out_tokens
        if out_fh is not None:
            out_fh.close()
            shards.append(
                {"file": f"shard-{len(shards):05d}.bin", "num_tokens": out_tokens}
            )
        out_fh = open(dst / f"shard-{len(shards):05d}.bin", "wb")
        out_tokens = 0

    roll()
    for path in files:
        with open(path, "rb") as fh:
            while True:
                room = (SHARD_TOKENS - out_tokens) * DTYPE_BYTES
                if room == 0:
                    roll()
                    room = SHARD_TOKENS * DTYPE_BYTES
                buf = fh.read(min(room, 1 << 24))
                if not buf:
                    break
                if len(buf) % DTYPE_BYTES:
                    raise SystemExit(f"odd byte count reading {path}")
                out_fh.write(buf)
                out_tokens += len(buf) // DTYPE_BYTES
                total += len(buf) // DTYPE_BYTES
    out_fh.close()
    if out_tokens:
        shards.append({"file": f"shard-{len(shards):05d}.bin", "num_tokens": out_tokens})
    else:
        (dst / f"shard-{len(shards):05d}.bin").unlink()

    index = {
        "dtype": "uint16",
        "shards": shards,
        "total_tokens": total,
        "source": str(src),
        "note": "flat consolidation of chunked render_regime_c.py output",
    }
    (dst / "index.json").write_text(json.dumps(index, indent=2))
    print(f"wrote {len(shards)} shards, {total} tokens -> {dst}")
    verify_flat(dst, expect)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="chunked shards dir, or the dir to check with --verify-only")
    ap.add_argument("dst", nargs="?", default=None)
    ap.add_argument("--expect-tokens", type=int, default=None)
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    if args.verify_only:
        verify_flat(Path(args.src), args.expect_tokens)
        return 0
    if args.dst is None:
        ap.error("dst is required unless --verify-only")
    dst = Path(args.dst)
    if (dst / "index.json").exists():
        try:
            verify_flat(dst, args.expect_tokens)
            print("ALREADY_CONSOLIDATED")
            return 0
        except SystemExit as exc:
            print(f"existing destination failed verification, redoing: {exc}")
    consolidate(Path(args.src), dst, args.expect_tokens)
    return 0


if __name__ == "__main__":
    sys.exit(main())
