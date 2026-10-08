"""Generates the ProsQA-style dataset splits."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data import ProsQAGenerator, Tokenizer, dedup_split, save  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data")
    p.add_argument("--n", type=int, default=44000)
    p.add_argument("--n_layers", type=int, default=6)
    p.add_argument("--width", type=int, default=4)
    p.add_argument("--n_hops", type=int, default=4)
    p.add_argument("--extra_edges", type=int, default=10)
    p.add_argument("--n_val", type=int, default=1000)
    p.add_argument("--n_test", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    os.makedirs(a.out, exist_ok=True)
    gen = ProsQAGenerator(a.n_layers, a.width, a.n_hops, a.extra_edges, a.seed)
    examples = gen.generate(a.n)
    train, val, test = dedup_split(examples, a.n_val, a.n_test)
    for name, split in [("train", train), ("val", val), ("test", test)]:
        save(split, os.path.join(a.out, f"{name}.json"))
        print(f"{name}: {len(split)}")

    tok = Tokenizer()
    lens = [len(tok.encode(e.question)) for e in train[:1000]]
    print(f"vocab={len(tok)} question_tokens_mean={sum(lens) / len(lens):.0f}")


if __name__ == "__main__":
    main()
