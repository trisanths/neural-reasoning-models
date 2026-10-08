"""Command line entry point for procedural warm-up stream generation.

Example:

    uv run python -m src.procgen.cli --tokens 1000000 --seed 1 \
        --mix dyck=0.3,shuffle_dyck=0.2,stack=0.15,seqops=0.15,ca=0.1,graph=0.1 \
        --out data/procgen/warmup.bin

Writes a raw uint16 token stream to the output path and a description of
the run, including the integer vocabulary layout, to <out>.meta.json.
"""

import argparse
import json
import os

import numpy as np

from src.procgen import ca, dyck, graph, seqops, stackops, vocab

GENERATORS = {
    "dyck": dyck.sample_dyck_example,
    "shuffle_dyck": dyck.sample_shuffle_dyck_example,
    "stack": stackops.sample_example,
    "seqops": seqops.sample_example,
    "ca": ca.sample_example,
    "graph": graph.sample_example,
}

GENERATOR_RANGES = {
    "dyck": dyck.VOCAB_RANGES,
    "shuffle_dyck": dyck.VOCAB_RANGES,
    "stack": stackops.VOCAB_RANGES,
    "seqops": seqops.VOCAB_RANGES,
    "ca": ca.VOCAB_RANGES,
    "graph": graph.VOCAB_RANGES,
}

DEFAULT_MIX = "dyck=0.3,shuffle_dyck=0.2,stack=0.15,seqops=0.15,ca=0.1,graph=0.1"


def parse_mix(spec):
    """Parse 'name=weight,...' into a dict of normalized positive weights."""
    weights = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"bad mix component {part!r}, expected name=weight")
        name, _, raw = part.partition("=")
        name = name.strip()
        if name not in GENERATORS:
            known = ", ".join(sorted(GENERATORS))
            raise ValueError(f"unknown generator {name!r}, known: {known}")
        if name in weights:
            raise ValueError(f"generator {name!r} listed twice")
        weight = float(raw)
        if weight <= 0:
            raise ValueError(f"weight for {name!r} must be positive, got {weight}")
        weights[name] = weight
    if not weights:
        raise ValueError("mix is empty")
    total = sum(weights.values())
    return {name: w / total for name, w in weights.items()}


def generate_stream(tokens, seed, mix):
    """Return (uint16 array of exactly `tokens` ids, stats dict).

    The next example always comes from the generator furthest below its
    target token share, so the mix is honored tightly. The final example is
    truncated to hit the exact token count.
    """
    if tokens < 1:
        raise ValueError(f"tokens must be positive, got {tokens}")
    rng = np.random.default_rng(seed)
    names = sorted(mix)
    token_counts = {name: 0 for name in names}
    example_counts = {name: 0 for name in names}
    parts = []
    emitted = 0
    while emitted < tokens:
        name = min(names, key=lambda n: (token_counts[n] / mix[n], n))
        example = GENERATORS[name](rng)
        token_counts[name] += len(example)
        example_counts[name] += 1
        parts.append(np.asarray(example, dtype=np.uint16))
        emitted += len(example)
    truncated = emitted - tokens
    arr = np.concatenate(parts)[:tokens]
    stats = {
        "token_counts": token_counts,
        "example_counts": example_counts,
        "truncated_tail_tokens": truncated,
    }
    return arr, stats


def build_meta(tokens, seed, mix, stats):
    return {
        "format": "raw uint16 token ids, native little-endian byte order",
        "tokens": tokens,
        "seed": seed,
        "mix": {name: mix[name] for name in sorted(mix)},
        "token_counts_before_truncation": stats["token_counts"],
        "example_counts": stats["example_counts"],
        "truncated_tail_tokens": stats["truncated_tail_tokens"],
        "vocab": vocab.describe(),
        "generator_ranges": {
            name: GENERATOR_RANGES[name] for name in sorted(mix)
        },
        "notes": (
            "Every example ends with EOS. The stream is truncated to the exact "
            "token count, so the final example may be incomplete. Ranges are "
            "half-open [start, end)."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.procgen.cli",
        description="Generate a procedural warm-up token stream.",
    )
    parser.add_argument("--tokens", type=int, required=True, help="exact stream length")
    parser.add_argument("--seed", type=int, required=True, help="rng seed")
    parser.add_argument("--mix", type=str, default=DEFAULT_MIX, help="name=weight,... mix")
    parser.add_argument("--out", type=str, required=True, help="output .bin path")
    args = parser.parse_args(argv)

    mix = parse_mix(args.mix)
    arr, stats = generate_stream(args.tokens, args.seed, mix)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    arr.tofile(args.out)
    meta_path = args.out + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(build_meta(args.tokens, args.seed, mix, stats), f, indent=2)
        f.write("\n")

    print(f"wrote {arr.size} tokens to {args.out}")
    print(f"wrote metadata to {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
