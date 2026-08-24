"""Train the 32k BPE tokenizer on a rendered text sample of worldgen episodes.

Usage:

    uv run python -m scripts.train_tokenizer --worlds data/worlds.jsonl \
        --out runs/smoke-001/tokenizer.json --sample-episodes 500
"""

import argparse
import json
import tempfile

from src.train.data import render_world_preamble
from src.train.tokenizer import DEFAULT_VOCAB_SIZE, train_tokenizer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.train_tokenizer")
    parser.add_argument("--worlds", required=True, help="episodes JSONL")
    parser.add_argument("--out", required=True, help="tokenizer.json path")
    parser.add_argument("--sample-episodes", type=int, default=500)
    parser.add_argument("--vocab-size", type=int, default=DEFAULT_VOCAB_SIZE)
    args = parser.parse_args(argv)

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as sample:
        n = 0
        with open(args.worlds) as fh:
            for line in fh:
                if n >= args.sample_episodes:
                    break
                episode = json.loads(line)
                sample.write(render_world_preamble(episode["world"]) + "\n")
                for doc in episode["documents"]:
                    sample.write(doc["text"] + "\n")
                for q in episode["questions"]:
                    sample.write(q["text"] + " " + q["answer"] + "\n")
                n += 1
        sample_path = sample.name

    tok = train_tokenizer([sample_path], out_path=args.out,
                          vocab_size=args.vocab_size)
    print(f"trained tokenizer on {n} episodes, vocab {tok.vocab_size}, "
          f"saved to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
