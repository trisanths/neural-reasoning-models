"""Generates splits for the sequential-composition task."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.compose import ComposeGenerator, ComposeTokenizer  # noqa: E402
from src.data import dedup_split, save  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data_compose")
    p.add_argument("--n", type=int, default=60000)
    p.add_argument("--n_steps", type=int, default=6)
    p.add_argument("--n_val", type=int, default=1000)
    p.add_argument("--n_test", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    os.makedirs(a.out, exist_ok=True)
    examples = ComposeGenerator(a.n_steps, a.seed).generate(a.n)
    train, val, test = dedup_split(examples, a.n_val, a.n_test)
    for name, split in [("train", train), ("val", val), ("test", test)]:
        save(split, os.path.join(a.out, f"{name}.json"))
        print(f"{name}: {len(split)}")

    tok = ComposeTokenizer()
    lens = [len(tok.encode(e.question)) for e in train[:500]]
    print(f"vocab={len(tok)} question_tokens={sum(lens) / len(lens):.0f} steps={a.n_steps}")
    print("example:", train[0].question)
    print("  steps:", train[0].steps)
    print("  answer:", train[0].answer)


if __name__ == "__main__":
    main()
