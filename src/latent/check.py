"""Does the latent segment change anything, and is R doing work?

A trained condition that scores the same at R=0 as at R=4 has either learned to
ignore the latent segment or is not injecting it at all, and those two look
identical in an accuracy table. This separates them.

  live      the trained head, at each R
  zeroed    the injected vector replaced by zeros of the same shape, which
            leaves R positions of scaffold and no state in them
  shuffled  each example given another example's latent vector, so the segment
            still carries a state and it is the wrong one

If live and zeroed produce the same text, nothing is being read out of the
state. If live and shuffled produce the same text, the state that is read
carries nothing about this example. Either one makes an accuracy difference at
larger R impossible to attribute, so it is worth knowing before a sweep, not
after it.
"""

from __future__ import annotations

import argparse
import json

import torch

from src.latent.eval import load_latent
from src.latent.data import latent_answer_prompt, latent_plan_prompt
from src.latent.infer import latent_generate
from src.opgraph.data import eval_items
from src.train.tokenizer import load_tokenizer


class ZeroHead:
    def __init__(self, head):
        self.head = head

    def __call__(self, h, step):
        return torch.zeros_like(self.head(h, step))


class ShuffleHead:
    """The real head, then the batch's vectors rolled by one row."""

    def __init__(self, head):
        self.head = head

    def __call__(self, h, step):
        return torch.roll(self.head(h, step), shifts=1, dims=0)


def prompts_for(arm, items):
    if arm == "latent_answer":
        return [latent_answer_prompt(it.world, it.text, None) for it in items]
    return [latent_plan_prompt(it.world.ops, it.text) for it in items]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--r", default="2,4,8")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--kind", default="sequential")
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--batch-size", type=int, default=12)
    args = ap.parse_args(argv)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = load_tokenizer(args.tokenizer)
    model, head, state = load_latent(args.ckpt, device)
    arm = state["arm"]
    items = eval_items(args.kind, args.depth, args.n)
    prompts = prompts_for(arm, items)
    max_new = 64 if arm == "latent_answer" else 144

    def gen(h, r):
        out, _ = latent_generate(model, h, tok, prompts, r, max_new=max_new,
                                 device=device, batch_size=args.batch_size)
        return out

    base = gen(head, 0)
    rows = []
    for r in (int(x) for x in args.r.split(",")):
        live = gen(head, r)
        zeroed = gen(ZeroHead(head), r)
        shuffled = gen(ShuffleHead(head), r)
        rows.append({
            "r": r, "n": len(items),
            "differs_from_r0": sum(a != b for a, b in zip(live, base)) / len(live),
            "differs_from_zeroed": sum(a != b for a, b in zip(live, zeroed)) / len(live),
            "differs_from_shuffled": sum(a != b for a, b in zip(live, shuffled)) / len(live),
            "example_live": live[0][:160],
            "example_zeroed": zeroed[0][:160],
        })
        print(json.dumps({k: v for k, v in rows[-1].items()
                          if not k.startswith("example")}), flush=True)
    payload = {"ckpt": args.ckpt, "arm": arm, "kind": args.kind,
               "depth": args.depth, "rows": rows}
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"[done] -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
