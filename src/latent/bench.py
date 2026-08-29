"""What a latent step actually costs, in passes and in seconds.

The optimization lab's result on this hardware is that weight tied recurrence
does not turn a memory bound model into a compute bound one: their recurrent
trunk sat near ten percent utilisation and was overhead bound. A latent step
here is one forward pass at one new position, which is exactly the shape of one
decoded token, so R latent steps cost about what R written tokens cost and R is
not free in wall clock. This measures that rather than assuming it, at batch
one, where latency is the whole story, and at a batch, where throughput is.

Nothing here needs a trained checkpoint. It measures the backbone.
"""

from __future__ import annotations

import argparse
import json
import time

import torch

from src.latent.core import LatentHead
from src.latent.infer import LatentPolicy


def bench(model, head, device, prompt_len: int, r_steps: int, decode: int,
          batch: int, repeats: int = 3) -> dict:
    ids = [[7] * prompt_len for _ in range(batch)]
    cap = prompt_len + r_steps + decode + 2
    rows = []
    for _ in range(repeats):
        pol = LatentPolicy(model, device, max_len=cap, temperature=0.0)
        _sync(device)
        t0 = time.perf_counter()
        pol.begin(ids)
        _sync(device)
        t1 = time.perf_counter()
        for r in range(r_steps):
            with torch.no_grad():
                z = head(pol.last_hidden.float(), r)
            pol.advance_embed(z)
        _sync(device)
        t2 = time.perf_counter()
        nxt = [0] * batch
        for _ in range(decode):
            nxt = pol.advance(nxt)
        _sync(device)
        t3 = time.perf_counter()
        rows.append((t1 - t0, t2 - t1, t3 - t2))
    rows.sort(key=lambda x: sum(x))
    prompt_s, reason_s, decode_s = rows[len(rows) // 2]
    return {
        "batch": batch, "prompt_len": prompt_len, "r_steps": r_steps,
        "decode_tokens": decode,
        "prompt_ms": round(prompt_s * 1e3, 2),
        "reason_ms": round(reason_s * 1e3, 2),
        "decode_ms": round(decode_s * 1e3, 2),
        "ms_per_latent_step": round(reason_s * 1e3 / max(1, r_steps), 3),
        "ms_per_decoded_token": round(decode_s * 1e3 / max(1, decode), 3),
        "ms_per_example": round((prompt_s + reason_s + decode_s) * 1e3 / batch, 3),
        "reason_passes_per_example": r_steps,
        "reason_layer_apps_per_example": r_steps * model.cfg.effective_depth(),
    }


def _sync(device):
    if torch.device(device).type == "cuda":
        torch.cuda.synchronize()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--prompt-len", type=int, default=600)
    ap.add_argument("--r", default="0,1,2,4,8,16,32,64")
    ap.add_argument("--decode", type=int, default=16)
    ap.add_argument("--batches", default="1,16")
    args = ap.parse_args(argv)

    from src.train.model import ModelConfig, TransformerLM
    device = "cuda" if torch.cuda.is_available() else "cpu"
    state = torch.load(args.base, map_location="cpu", weights_only=False)
    model = TransformerLM(ModelConfig(**state["config"]["model"]))
    model.load_state_dict(state["model"])
    model.to(device).eval()
    head = LatentHead(model.cfg.d_model, slots=64, scale=0.0123).to(device).eval()

    rows = []
    for batch in (int(x) for x in args.batches.split(",")):
        for r in (int(x) for x in args.r.split(",")):
            row = bench(model, head, device, args.prompt_len, r, args.decode,
                        batch)
            rows.append(row)
            print(json.dumps(row), flush=True)
    if args.out:
        with open(args.out, "w") as fh:
            json.dump({"device": device, "prompt_len": args.prompt_len,
                       "rows": rows}, fh, indent=1)
        print(f"[done] -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
