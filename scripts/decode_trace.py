"""Decode retrieval traces from shard directories and verify their shape.

Two modes.

Scan mode (--shards): scans the token stream for <|q|> markers, checks that
every trace runs question, retrieve, query, result, chunk, answer, eot in that
order with each marker appearing exactly once, prints the first decoded trace,
and exits nonzero when any trace is malformed.

Oracle mode (--manifest): reads a manifest written by scripts.render_regime_c,
picks random rendered episodes, regenerates each one from its seed, and checks
that the stored tokens equal the recomputed render exactly. It also checks the
first trace semantically: the query span encodes build_query of the question
and the result span encodes the BM25 oracle's top document for that query.

Usage:

    uv run python -m scripts.decode_trace --shards ~/data/retrieval_demo/shards \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json

    uv run python -m scripts.decode_trace \
        --manifest ~/data/regime_c/manifest.json \
        --tokenizer ~/runs/tokenizer_v2/tokenizer_v2.json --samples 3
"""

import argparse
import json
import random
from pathlib import Path

import numpy as np

from src.train.data import ShardReader
from src.train.retrieval import BM25Index, build_query, render_episode_retrieval
from src.train.tokenizer import load_tokenizer
from src.worldgen.engine import generate_episodes

TRACE_ORDER = ["<|q|>", "<|retrieve|>", "<|result|>", "<|a|>", "<|eot|>"]


def check_trace(ids: list[int], sid: dict) -> str | None:
    """Return a problem description, or None when the trace is well formed."""
    marker_ids = [sid[name] for name in TRACE_ORDER]
    positions = []
    for name, mid in zip(TRACE_ORDER, marker_ids):
        found = [i for i, t in enumerate(ids) if t == mid]
        if len(found) != 1:
            return f"{name} appears {len(found)} times"
        positions.append(found[0])
    if positions != sorted(positions):
        return f"markers out of order at positions {positions}"
    for name, lo, hi in (("query", positions[1], positions[2]),
                         ("chunk", positions[2], positions[3]),
                         ("answer", positions[3], positions[4])):
        if hi - lo < 2:
            return f"empty {name} span"
    return None


def scan_shards(shards: str, tok, max_traces: int) -> int:
    sid = tok.special_ids
    reader = ShardReader(shards)
    scan = min(reader.total_tokens, 2_000_000)
    stream = reader.get_slice(0, scan).tolist()

    q_id, eot_id = sid["<|q|>"], sid["<|eot|>"]
    checked = 0
    printed = False
    i = 0
    while i < len(stream) and checked < max_traces:
        if stream[i] != q_id:
            i += 1
            continue
        try:
            end = stream.index(eot_id, i)
        except ValueError:
            break
        trace = stream[i:end + 1]
        problem = check_trace(trace, sid)
        if problem is not None:
            print(f"BAD_TRACE at token {i}: {problem}")
            print(tok.decode(trace))
            return 1
        if not printed:
            print("first decoded trace:")
            print(tok.decode(trace))
            printed = True
        checked += 1
        i = end + 1

    if checked == 0:
        print("NO_TRACES_FOUND")
        return 1
    print(f"TRACE_OK checked {checked} traces over {scan:,} tokens")
    return 0


def verify_manifest(manifest_path: str, tok, samples: int,
                    sample_seed: int) -> int:
    with open(manifest_path) as fh:
        man = json.load(fh)
    out_dir = Path(manifest_path).parent
    chunks = man["chunks"]
    if not chunks:
        print("NO_CHUNKS_IN_MANIFEST")
        return 1
    rng = random.Random(sample_seed)
    sid = tok.special_ids
    world_id = sid["<|world|>"]

    for n in range(samples):
        ch = rng.choice(chunks)
        k = rng.randrange(ch["episodes"])
        index = ch["start_index"] + k
        reader = ShardReader(str(out_dir / f"chunk-{ch['id']:05d}"))
        stream = reader.get_slice(0, reader.total_tokens)
        bounds = np.flatnonzero(stream == world_id)
        if len(bounds) != ch["episodes"]:
            print(f"BOUNDARY_MISMATCH chunk {ch['id']}: "
                  f"{len(bounds)} episode starts, expected {ch['episodes']}")
            return 1
        start = int(bounds[k])
        end = int(bounds[k + 1]) if k + 1 < len(bounds) else reader.total_tokens
        got = [int(t) for t in stream[start:end]]

        episode = next(iter(generate_episodes(
            man["base_seed"], 1, domains=man["domains"],
            contradiction_rate=man["contradiction_rate"],
            filler_rate=man["filler_rate"], start_index=index,
        )))
        want = render_episode_retrieval(
            episode, tok, max_doc_tokens=man["max_doc_tokens"])
        if got != want:
            print(f"RENDER_MISMATCH chunk {ch['id']} episode {k} "
                  f"index {index}: {len(got)} stored vs "
                  f"{len(want)} recomputed tokens")
            return 1

        question = episode["questions"][0]
        query = build_query(question["text"])
        idx_r = got.index(sid["<|retrieve|>"])
        idx_res = got.index(sid["<|result|>"])
        idx_a = got.index(sid["<|a|>"])
        if got[idx_r + 1:idx_res] != tok.encode(query):
            print(f"QUERY_MISMATCH index {index}: span does not encode "
                  f"{query!r}")
            return 1
        oracle = BM25Index([d["text"] for d in episode["documents"]])
        top_text = episode["documents"][oracle.top(query)]["text"]
        if got[idx_res + 1:idx_a] != tok.encode(top_text):
            print(f"RESULT_MISMATCH index {index}: span does not encode "
                  f"the oracle top document")
            return 1
        print(f"sample {n}: chunk {ch['id']} episode {k} index {index} ok, "
              f"{len(got)} tokens, query {query!r}, "
              f"result doc {top_text[:60]!r}")

    print(f"ORACLE_VERIFY_OK {samples} samples")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.decode_trace")
    parser.add_argument("--shards", default=None)
    parser.add_argument("--manifest", default=None,
                        help="render_regime_c manifest.json for oracle mode")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--max-traces", type=int, default=200)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--sample-seed", type=int, default=0)
    args = parser.parse_args(argv)

    if args.shards is None and args.manifest is None:
        parser.error("need --shards or --manifest")
    tok = load_tokenizer(args.tokenizer)
    if args.manifest is not None:
        rc = verify_manifest(args.manifest, tok, args.samples,
                             args.sample_seed)
        if rc != 0 or args.shards is None:
            return rc
    return scan_shards(args.shards, tok, args.max_traces)


if __name__ == "__main__":
    raise SystemExit(main())
