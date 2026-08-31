"""The project's own system on the general check, measured rather than asserted.

The external models are about to be shown beating this project on ordinary
questions, and a report that asserted that without a number would be worth
nothing. So the same 26 questions are put to the project's own reader, through
the same path `src/norm/opneural.py` uses: the input vocabulary encodes the
text, the network emits a target sequence, the deserializer turns it into a
program and `src/norm/interp.py` runs it.

What the input vocabulary refuses is reported apart from what the network gets
wrong, because a question the harness cannot even encode is a statement about
the interface and not about the reader.
"""
from __future__ import annotations

import argparse
import gzip
import json

import numpy as np
import torch

from src.norm import ndata, neval, nmodel, ntok
from src.norm.interp import run
from src.norm.ntok import TokenizeError
from src.norm.cmpwork.grade import forced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="results/norm/train/ckpt_l.pt")
    ap.add_argument("--items", default="results/extern/general_items.jsonl.gz")
    ap.add_argument("--out", default="results/extern/ours_general.json")
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()

    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = nmodel.build(ck["size"], len(iv), len(ov)).to(a.device)
    model.load_state_dict(ck["state"])
    model.eval()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    rows, enc = [], []
    for it in items:
        try:
            ids, slots, n_unk = iv.encode(it["text"])
        except TokenizeError as exc:
            rows.append({"id": it["id"], "state": "untokenizable",
                         "why": str(exc)[:120], "answer": ""})
            enc.append(None)
            continue
        if n_unk:
            rows.append({"id": it["id"], "state": "unknown_words",
                         "why": f"n_unk={n_unk} of {len(ids)}", "answer": ""})
            enc.append(None)
            continue
        enc.append({"ids": np.asarray(ids, dtype=np.int64), "slots": slots})
        rows.append({"id": it["id"], "state": "encoded", "answer": ""})

    live = [i for i, e in enumerate(enc) if e is not None]
    if live:
        em = neval.emit(model, [{"ids": enc[i]["ids"]} for i in live], ov,
                        a.device, "greedy", batch=8, max_len=ndata.MAX_OUT,
                        seed=0)
        for k, i in enumerate(live):
            try:
                prog = ntok.deserialize(ov.decode(em[k]), enc[i]["slots"])
            except Exception as exc:
                rows[i].update(state="malformed", why=str(exc)[:90])
                continue
            r = run(prog)
            rows[i].update(state="ran" if r.ok else "refused",
                           answer=r.text if r.ok else "",
                           why="" if r.ok else r.reason[:90])

    strict = lenient = 0
    for it, r in zip(items, rows):
        f = forced(r["answer"], it["options"], it["gold"])
        strict += f["strict_correct"]
        lenient += f["lenient_correct"]
        r["gold"] = it["gold"]
        r["family"] = it["family"]
    n = len(items)
    states = {}
    for r in rows:
        states[r["state"]] = states.get(r["state"], 0) + 1
    out = {"ckpt": a.ckpt, "params": ck["params"], "n": n,
           "strict": round(strict / n, 4), "lenient": round(lenient / n, 4),
           "floor": round(sum(it["floor"] for it in items) / n, 4),
           "states": states, "rows": rows}
    json.dump(out, open(a.out, "w"), indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    print("sample rows:", json.dumps(rows[:4], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
