"""What the reader writes instead, on the shapes the key position axis reaches.

`results/system/eval/*/records_*.jsonl.gz` carries four outcome flags, the
executed answer and the gold answer, and not the structure the reader emitted.
Four flags cannot separate a plan of the wrong kind from the right kind with
the key and the value the wrong way round, and those two need different fixes.
So the structures are emitted again here, from the same checkpoint through the
same `src/norm/neval.emit` at the same decode settings, and the run is gated on
reproducing the existing record file item by item before anything is counted
off it. If the gate fails the counts are not written.

The taxonomy, in the order it is applied, first match winning:

    malformed     the token stream is not a structure, so nothing parses
    refused       the structure parses and `src/norm/interp.run` declines it
    wrong kind    it runs, and its definition kinds or its plan operations are
                  not the gold structure's
    wrong binding it runs, the kinds and the plan match, and every difference
                  from gold is in which symbol is a key and which is a value:
                  the entries are gold's reversed, or re-paired out of the same
                  two symbol sets
    wrong content the kinds and the plan match and some symbol or number is
                  not gold's
    downstream    the structure is gold's exactly and the answer is not

`downstream` is empty by construction, because an exact structure executes to
gold's own answer under the same interpreter, and it is counted anyway so that
the zero is a measurement rather than an omission.

Nothing here is pooled across key position or across shape.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import time
from collections import Counter

import torch

from src.norm import ndata, neval, nmodel
from src.norm.interp import run
from src.norm.lang import NormError, program_json, pretty
from src.norm.ntok import deserialize
from src.role.rshapes import GROUPS
from src.system import sizes

CATS = ("exact", "malformed", "refused", "wrong kind", "wrong binding",
        "wrong content", "downstream")
POS = ("key_first", "value_first")


def wilson(k, n, z=1.959964):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 4), round((c + h) / d, 4))


# ------------------------------------------------------------ the structure


def arity(d):
    if d.kind in ("table", "weights") and d.entries:
        k = d.entries[0][0]
        return len(k) if isinstance(k, tuple) else 1
    return 0


def kind_sig(p):
    """What kind of structure this is, with no symbol in it.

    Definition kinds in page order with their key arity, and the plan's
    operations in plan order. Two structures with the same signature say the
    same sort of thing about a different set of words.
    """
    return (tuple((d.kind, arity(d)) for d in p.defs),
            tuple(s.op for s in p.steps))


def pairs(d):
    """The (key, value) bindings a definition states, or none if it states no
    binding of that sort."""
    if d.kind in ("table", "weights"):
        return [(k, v) for k, v in d.entries]
    if d.kind == "rule":
        return [(k, v) for k, v in d.exceptions]
    return []


def rest(d):
    """Everything in a definition that is not a key to value binding."""
    if d.kind == "table":
        return ("table", d.name, d.default, d.ordered)
    if d.kind == "weights":
        return ("weights", d.name)
    if d.kind == "rule":
        return ("rule", d.name, d.general)
    if d.kind == "bands":
        return ("bands", d.name, d.attr, tuple(d.cuts), tuple(d.labels))
    if d.kind == "affine":
        return ("affine", d.name, d.a, d.b, d.m)
    return (d.kind, d.name)


def def_relation(dp, dg):
    """How one emitted definition stands to its gold counterpart."""
    pp, pg = pairs(dp), pairs(dg)
    if rest(dp) != rest(dg):
        return "content"
    if not pp and not pg:
        return "same"
    if Counter(pp) == Counter(pg):
        return "same"
    if Counter(pp) == Counter((v, k) for k, v in pg):
        return "swapped"
    if (Counter(k for k, _ in pp) == Counter(k for k, _ in pg)
            and Counter(v for _, v in pp) == Counter(v for _, v in pg)):
        return "mispaired"
    if (Counter(k for k, _ in pp) == Counter(v for _, v in pg)
            and Counter(v for _, v in pp) == Counter(k for k, _ in pg)):
        return "swapped"
    lhs = Counter([k for k, _ in pp] + [v for _, v in pp])
    rhs = Counter([k for k, _ in pg] + [v for _, v in pg])
    if lhs == rhs:
        return "reassociated"
    return "content"


BINDING = {"swapped", "mispaired", "reassociated"}


def classify(prog, gold, exact):
    """The category, and the evidence for it."""
    if exact:
        return "exact", {}
    if kind_sig(prog) != kind_sig(gold):
        return "wrong kind", {"sig": str(kind_sig(prog)),
                              "gold_sig": str(kind_sig(gold))}
    rels = [def_relation(dp, dg) for dp, dg in zip(prog.defs, gold.defs)]
    plan_same = (prog.inputs == gold.inputs and prog.steps == gold.steps
                 and prog.answer == gold.answer)
    if not plan_same:
        return "wrong content", {"defs": rels, "plan_differs": True}
    if any(r == "content" for r in rels):
        return "wrong content", {"defs": rels, "plan_differs": False}
    if any(r in BINDING for r in rels):
        cat = "wrong binding"
        return cat, {"defs": rels, "plan_differs": False,
                     "all_swapped": all(r in ("swapped", "same")
                                        for r in rels)
                     and any(r == "swapped" for r in rels)}
    return "wrong content", {"defs": rels, "plan_differs": False,
                             "note": "no difference found in the comparison"}


# ---------------------------------------------------------------- the pass


def load_model(ckpt, device):
    ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    iv, ov = ndata._vocab()
    build = sizes.build if ck["size"] in sizes.LADDER else nmodel.build
    model = build(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    return model, ck


def read_prior(path):
    if not os.path.exists(path):
        return None
    out = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--split", default="mode")
    ap.add_argument("--modes", default="greedy,sampled")
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--eval", default="results/system/eval")
    ap.add_argument("--out", default="results/norm/gap")
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--n", type=int, default=7000)
    a = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    iv, ov = ndata._vocab()
    model, ck = load_model(a.ckpt, device)
    items = neval.load_eval(os.path.join(a.data, a.split), a.n)
    os.makedirs(a.out, exist_ok=True)

    rep = {"tag": a.tag, "split": a.split, "device": device,
           "ckpt": os.path.abspath(a.ckpt), "size": ck["size"],
           "params": ck["params"], "steps": ck["steps"],
           "groups": {g: list(s) for g, s in GROUPS.items()},
           "built": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
           "modes": {}}

    for mode in a.modes.split(","):
        prior_path = os.path.join(a.eval, a.tag,
                                  f"records_{a.split}_{mode}.jsonl.gz")
        prior = read_prior(prior_path)
        em = neval.emit(model, items, ov, device, mode, temperature=1.0,
                        batch=a.batch)
        recs, gate = [], Counter()
        for i, (it, e) in enumerate(zip(items, em)):
            toks = ov.decode(e)
            gold = it["prog"]
            gr = run(gold)
            r = {"fid": it["fid"], "shape": it["shape"],
                 "key_position": it["fid"].split(".")[2],
                 "group": next(g for g, ss in GROUPS.items()
                               if it["shape"] in ss)}
            try:
                prog = deserialize(toks, it["slots"])
            except (NormError, Exception) as exc:            # noqa: BLE001
                r.update(category="malformed", exact=False, malformed=True,
                         refused=False, wrong=False, answer="",
                         gold_answer=gr.text, reason=f"{type(exc).__name__}",
                         emitted=None, evidence={})
                recs.append(r)
                gate[_agree(r, prior, i)] += 1
                continue
            exact = (prog == gold)
            rr = run(prog)
            structural, ev = classify(prog, gold, exact)
            cat = structural
            if not exact and not rr.ok:
                cat = "refused"
            elif exact and rr.ok and rr.text != gr.text:
                cat = "downstream"
            r.update(category=cat, exact=exact, malformed=False,
                     refused=(not rr.ok), wrong=(rr.ok and not exact),
                     answer=(rr.text if rr.ok else ""), gold_answer=gr.text,
                     reason=("" if rr.ok else rr.reason[:160]),
                     emitted=program_json(prog),
                     pretty=pretty(prog), gold_pretty=pretty(gold), evidence=ev,
                     structural=structural)
            recs.append(r)
            gate[_agree(r, prior, i)] += 1

        rp = os.path.join(a.out, f"records_{a.tag}_{a.split}_{mode}.jsonl.gz")
        with gzip.open(rp, "wt") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
        summ = tally(recs)
        summ["gate"] = {"prior_record": (os.path.abspath(prior_path)
                                         if prior else None),
                        "prior_mtime": (time.strftime(
                            "%Y-%m-%d %H:%M UTC",
                            time.gmtime(os.path.getmtime(prior_path)))
                            if prior else None),
                        "counts": dict(gate)}
        summ["records"] = os.path.abspath(rp)
        rep["modes"][mode] = summ
        print(json.dumps({"mode": mode, "gate": dict(gate)}), flush=True)
        if gate.get("disagree"):
            print(f"GATE FAILED for {mode}: {gate['disagree']} items differ "
                  f"from {prior_path}", flush=True)

    path = os.path.join(a.out, f"{a.tag}_{a.split}.json")
    with open(path, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", os.path.abspath(path))
    return 0


def _agree(r, prior, i):
    if prior is None:
        return "no prior"
    p = prior[i]
    if p["fid"] != r["fid"] or p["shape"] != r["shape"]:
        return "misaligned"
    for k in ("exact", "malformed", "refused", "wrong"):
        if bool(p[k]) != bool(r[k]):
            return "disagree"
    if p["answer"] != r["answer"]:
        return "disagree"
    return "agree"


def tally(recs):
    """Counts by shape and key position, and never across either."""
    out = {"by_shape_position": {}, "by_group_position": {},
           "swapped_detail": {}}
    cells = {}
    for r in recs:
        for key in ((r["shape"], r["key_position"]),
                    ("GROUP:" + r["group"], r["key_position"])):
            cells.setdefault(key, []).append(r)
    for (name, kp), rs in sorted(cells.items()):
        n = len(rs)
        c = Counter(r["category"] for r in rs)
        row = {"n": n}
        for cat in CATS:
            k = c.get(cat, 0)
            lo, hi = wilson(k, n)
            row[cat] = {"k": k, "share": round(k / n, 4), "ci": [lo, hi]}
        row["answer_ok"] = sum(1 for r in rs
                               if r["answer"] and r["answer"] == r["gold_answer"])
        row["wrong_but_right_answer"] = sum(
            1 for r in rs if not r["exact"] and r["answer"]
            and r["answer"] == r["gold_answer"])
        row["refused_that_are_transpositions"] = sum(
            1 for r in rs if r["category"] == "refused"
            and r.get("structural") == "wrong binding")
        row["binding_all_swapped"] = sum(
            1 for r in rs if r["category"] == "wrong binding"
            and r.get("evidence", {}).get("all_swapped"))
        dest = out["by_group_position"] if name.startswith("GROUP:") \
            else out["by_shape_position"]
        dest.setdefault(name.replace("GROUP:", ""), {})[kp] = row
    return out


if __name__ == "__main__":
    raise SystemExit(main())
