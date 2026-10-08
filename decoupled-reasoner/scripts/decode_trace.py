"""Decode retrieval traces from shard directories and verify their shape.

Two modes.

Scan mode (--shards): scans the token stream for <|q|> markers and checks that
every trace follows the multi-hop grammar: question, zero or more
retrieve-query result-chunk rounds, answer, eot, with every span nonempty. It
prints the first decoded trace and a hop histogram, and exits nonzero when any
trace is malformed.

Oracle mode (--manifest): reads a manifest written by scripts.render_regime_c,
picks random rendered episodes, regenerates each one from its seed, and checks
that the stored tokens equal the recomputed render exactly. It then verifies
every trace in the episode semantically against the recomputed plan: the
number of traces matches the non-dropped questions, each hop's query span
encodes the planned query, each result span encodes a document that supports
that hop's derivation fact, and the oracle BM25 retriever, excluding the
chunks earlier hops of the same question returned, ranks that document top-1
for the query.

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
from collections import Counter
from pathlib import Path

import numpy as np

from src.train.data import ShardReader
from src.train.retrieval import (
    BM25Index,
    plan_episode_traces,
    render_episode_retrieval,
)
from src.train.tokenizer import load_tokenizer
from src.worldgen.engine import generate_episodes


def parse_trace(ids: list[int], sid: dict):
    """Split one trace into spans.

    Returns (question, [(query, chunk), ...], answer) as token id lists, or a
    problem string when the trace violates the grammar. The trace must start
    at <|q|> and end at <|eot|>.
    """
    special = {v: k for k, v in sid.items()}
    if not ids or ids[0] != sid["<|q|>"] or ids[-1] != sid["<|eot|>"]:
        return "trace does not run from <|q|> to <|eot|>"
    marks = [(i, special[t]) for i, t in enumerate(ids) if t in special]
    names = [name for _, name in marks]
    expect = ["<|q|>"]
    n_rounds = (len(names) - 3) // 2
    if len(names) != 3 + 2 * n_rounds or n_rounds < 0:
        return f"unexpected marker count {len(names)}"
    expect += ["<|retrieve|>", "<|result|>"] * n_rounds + ["<|a|>", "<|eot|>"]
    if names != expect:
        return f"marker sequence {names} != {expect}"
    spans = []
    for (lo, _), (hi, _) in zip(marks, marks[1:]):
        if hi - lo < 2:
            return f"empty span after {special[ids[lo]]} at {lo}"
        spans.append(ids[lo + 1:hi])
    question = spans[0]
    rounds = [(spans[1 + 2 * k], spans[2 + 2 * k]) for k in range(n_rounds)]
    answer = spans[-1]
    return question, rounds, answer


def iter_traces(stream: list[int], sid: dict):
    """Yield (start, trace token list) for each <|q|> ... <|eot|> run."""
    q_id, eot_id = sid["<|q|>"], sid["<|eot|>"]
    i = 0
    while i < len(stream):
        if stream[i] != q_id:
            i += 1
            continue
        try:
            end = stream.index(eot_id, i)
        except ValueError:
            return
        yield i, stream[i:end + 1]
        i = end + 1


def scan_shards(shards: str, tok, max_traces: int) -> int:
    sid = tok.special_ids
    reader = ShardReader(shards)
    scan = min(reader.total_tokens, 2_000_000)
    stream = reader.get_slice(0, scan).tolist()

    checked = 0
    printed = False
    hops = Counter()
    for start, trace in iter_traces(stream, sid):
        if checked >= max_traces:
            break
        parsed = parse_trace(trace, sid)
        if isinstance(parsed, str):
            print(f"BAD_TRACE at token {start}: {parsed}")
            print(tok.decode(trace))
            return 1
        _, rounds, _ = parsed
        hops[len(rounds)] += 1
        if not printed:
            print("first decoded trace:")
            print(tok.decode(trace))
            printed = True
        checked += 1

    if checked == 0:
        print("NO_TRACES_FOUND")
        return 1
    histo = " ".join(f"{h}:{n}" for h, n in sorted(hops.items()))
    mean = sum(h * n for h, n in hops.items()) / checked
    print(f"TRACE_OK checked {checked} traces over {scan:,} tokens, "
          f"hops {histo}, mean {mean:.2f}")
    return 0


def verify_episode_semantics(episode: dict, got: list[int], tok) -> str | None:
    """Check every trace in a rendered episode against the recomputed plan.

    Returns a problem string or None. got is the episode's full token run
    starting at <|world|>.
    """
    sid = tok.special_ids
    documents = episode.get("documents", [])
    plans, _ = plan_episode_traces(episode)
    rendered = [
        (q, plan) for q, plan in zip(episode.get("questions", []), plans)
        if plan is not None
    ]
    traces = list(iter_traces(got, sid))
    if len(traces) != len(rendered):
        return (f"{len(traces)} traces in stream but {len(rendered)} "
                f"rendered questions")
    index = BM25Index.for_documents(documents) if documents else None
    for (start, trace), (question, plan) in zip(traces, rendered):
        parsed = parse_trace(trace, sid)
        if isinstance(parsed, str):
            return f"{question['qid']}: {parsed}"
        q_span, rounds, a_span = parsed
        if q_span != tok.encode(question["text"]):
            return f"{question['qid']}: question span mismatch"
        if a_span != tok.encode(question["answer"]):
            return f"{question['qid']}: answer span mismatch"
        if len(rounds) != len(plan):
            return (f"{question['qid']}: {len(rounds)} rounds but plan "
                    f"has {len(plan)} hops")
        derivation = question.get("derivation") or []
        exclude: set = set()
        for k, ((query_span, chunk_span), (query, doc_idx)) in enumerate(
                zip(rounds, plan)):
            if query_span != tok.encode(query):
                return f"{question['qid']} hop {k + 1}: query span mismatch"
            doc = documents[doc_idx]
            if chunk_span != tok.encode(doc["text"]):
                return f"{question['qid']} hop {k + 1}: chunk span mismatch"
            if derivation[k] not in doc.get("supports", []):
                return (f"{question['qid']} hop {k + 1}: result does not "
                        f"support fact {derivation[k]}")
            if index.top(query, exclude) != doc_idx:
                return (f"{question['qid']} hop {k + 1}: query is not "
                        f"top-1 for its document")
            exclude.add(doc_idx)
    return None


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

        problem = verify_episode_semantics(episode, got, tok)
        if problem is not None:
            print(f"SEMANTIC_MISMATCH index {index}: {problem}")
            return 1
        n_traces = sum(1 for _ in iter_traces(got, sid))
        print(f"sample {n}: chunk {ch['id']} episode {k} index {index} ok, "
              f"{len(got)} tokens, {n_traces} traces verified per hop")

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
