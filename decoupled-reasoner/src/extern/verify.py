"""Two checks that have to pass before a model's benchmark numbers mean anything.

The template check asks trivial questions through the model's own chat
template and prints what came back, so a harness that dropped a header is
visible as nonsense before any benchmark is run rather than after.

The padding check runs the same prompts twice, once one at a time and once in
one left padded batch, and reports whether the greedy generations agree. LFM2
interleaves short convolutions with attention, and a convolution reads its own
left context, so a padded batch is exactly where this family could differ from
an unpadded single. A disagreement here would mean the batched benchmark
numbers are a harness artefact.
"""
from __future__ import annotations

import argparse
import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

CONTROLS = [
    "What is the capital of France?",
    "What is 17 plus 26?",
    "Name the largest planet in our solar system.",
    "If all bloops are razzles and all razzles are lazzles, are all bloops "
    "lazzles? Answer yes or no.",
    "A table lists: apple -> red, pear -> green. What colour is the pear? "
    "Answer with one word.",
]

# A short stand-in for a benchmark item, so the padding check runs on prompts
# of the shape the benchmark actually uses and of visibly different lengths.
LONGISH = [
    "The Alpha map.\n\nSend every kip token to the red value.\nSend every "
    "wug token to the blue value.\n\nThe Beta map.\n\nSend every kip token "
    "to the red value.\nSend every wug token to the green value.\n\n"
    "To give the zorp of a token, take its value at the Alpha map and its "
    "value at the Beta map. When the two readings are the same, give that "
    "shared reading as the zorp. In every other case give teal as the zorp."
    "\n\nWhat is the zorp of the kip token? Reply with one word.",
    "The Alpha map.\n\nSend every kip token to the red value.\nSend every "
    "wug token to the blue value.\n\nThe Beta map.\n\nSend every kip token "
    "to the red value.\nSend every wug token to the green value.\n\n"
    "To give the zorp of a token, take its value at the Alpha map and its "
    "value at the Beta map. When the two readings are the same, give that "
    "shared reading as the zorp. In every other case give teal as the zorp."
    "\n\nWhat is the zorp of the wug token? Reply with one word.",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()

    msgs = [[{"role": "user", "content": q}] for q in CONTROLS + LONGISH]
    rendered = [tok.apply_chat_template(m, tokenize=False,
                                        add_generation_prompt=True)
                for m in msgs]
    gkw = {"max_new_tokens": a.max_new, "do_sample": False,
           "temperature": None, "top_p": None, "top_k": None,
           "pad_token_id": tok.pad_token_id}

    singles = []
    for r in rendered:
        enc = tok([r], return_tensors="pt",
                  add_special_tokens=False).to(a.device)
        with torch.no_grad():
            g = model.generate(**enc, **gkw)
        singles.append(tok.decode(g[0, enc["input_ids"].shape[1]:],
                                  skip_special_tokens=True))

    enc = tok(rendered, return_tensors="pt", padding=True,
              add_special_tokens=False).to(a.device)
    with torch.no_grad():
        g = model.generate(**enc, **gkw)
    batched = [tok.decode(g[k, enc["input_ids"].shape[1]:],
                          skip_special_tokens=True)
               for k in range(len(rendered))]

    rows = []
    for q, s, b in zip(CONTROLS + LONGISH, singles, batched):
        rows.append({"q": q[:70], "single": s.strip()[:400],
                     "batched": b.strip()[:400], "same": s.strip() == b.strip()})
    agree = sum(r["same"] for r in rows)
    print(f"MODEL {a.model}")
    print(f"PAD_AGREE {agree}/{len(rows)}")
    print(f"RENDERED_EXAMPLE {rendered[0]!r}")
    for r in rows:
        print("-" * 70)
        print("Q       ", r["q"])
        print("SINGLE  ", r["single"].replace("\n", " | ")[:300])
        if not r["same"]:
            print("BATCHED ", r["batched"].replace("\n", " | ")[:300])
        print("SAME    ", r["same"])
    if a.out:
        json.dump({"model": a.model, "pad_agree": agree, "n": len(rows),
                   "rendered_example": rendered[0], "rows": rows},
                  open(a.out, "w"), indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
