"""Fine tune one arm of the composition experiment from the shared base.

Two arms, same base checkpoint, same worlds, same questions, same optimizer
steps, same batch size in sequences.

  direct    answer the question from the pages
  opgraph   induce an operator from each page, and write a plan for the question

The direct arm sees strictly more tokens per step, because its prompts carry
the pages while half the opgraph arm's prompts carry only an operator
signature line. That asymmetry is left in deliberately and reported, because
it favours the baseline: if the decomposed arm still wins, it did not win by
being fed more.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time

import torch

from src.opgraph.data import IGNORE, build_stream, encode_example
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer


def batches(pool, tok, max_len, batch_size):
    """Endless shuffled batches of padded (ids, labels)."""
    encoded = []
    for prompt, target in pool:
        e = encode_example(tok, prompt, target, max_len)
        if e is not None:
            encoded.append(e)
    if not encoded:
        raise SystemExit("no examples fit inside max_len")
    encoded.sort(key=lambda x: len(x[0]))
    groups = [encoded[i:i + batch_size] for i in range(0, len(encoded), batch_size)]
    order = list(range(len(groups)))
    rng = torch.Generator().manual_seed(1234)
    while True:
        perm = torch.randperm(len(groups), generator=rng).tolist()
        for gi in perm:
            g = groups[order[gi]]
            width = max(len(ids) for ids, _ in g)
            ids = torch.zeros(len(g), width, dtype=torch.long)
            lab = torch.full((len(g), width), IGNORE, dtype=torch.long)
            for i, (a, b) in enumerate(g):
                ids[i, :len(a)] = torch.tensor(a)
                lab[i, :len(b)] = torch.tensor(b)
            yield ids, lab


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--arm", required=True, choices=["direct", "opgraph"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--worlds", type=int, default=20000)
    ap.add_argument("--log-every", type=int, default=50)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    state = torch.load(args.base, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device)
    model.train()

    pool = build_stream(range(args.worlds), args.arm, rng_seed=17)
    stream = batches(pool, tok, args.max_len, args.batch_size)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95),
                            weight_decay=0.1)

    log: list[dict] = []
    seen_tokens = 0
    supervised = 0
    t0 = time.time()
    for step in range(1, args.steps + 1):
        ids, lab = next(stream)
        ids, lab = ids.to(device), lab.to(device)
        seen_tokens += int(ids.numel())
        supervised += int((lab != IGNORE).sum())
        lr = args.lr * (step / args.warmup if step < args.warmup else
                        0.5 * (1 + math.cos(math.pi * (step - args.warmup) /
                                            max(1, args.steps - args.warmup))))
        for g in opt.param_groups:
            g["lr"] = lr
        with torch.autocast(device_type=device, dtype=torch.bfloat16):
            _, loss = model(ids[:, :-1], lab[:, 1:])
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.log_every == 0 or step == 1:
            rec = {"step": step, "loss": float(loss.item()), "lr": lr,
                   "tokens": seen_tokens, "supervised": supervised,
                   "secs": round(time.time() - t0, 1)}
            log.append(rec)
            print(json.dumps(rec), flush=True)

    torch.save({"model": model.state_dict(), "config": state["config"],
                "step": args.steps, "arm": args.arm,
                "tokens": seen_tokens, "supervised_tokens": supervised,
                "examples": len(pool)}, args.out)
    with open(args.out + ".log.json", "w") as fh:
        json.dump({"arm": args.arm, "args": vars(args), "log": log}, fh, indent=1)
    print(f"[done] {args.arm} -> {args.out} tokens={seen_tokens} "
          f"supervised={supervised} examples={len(pool)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
