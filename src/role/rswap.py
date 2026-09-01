"""Is the wrong structure the right one with key and value exchanged.

`src/norm/neval.py` counts a failure as wrong-but-executable, which says the
emission was a well formed structure that ran, and not what it said. The
positional account makes a sharper claim than that. Copy slots are numbered by
order of first appearance, so in a key-first page the first invented word of a
rule line is the key and in a value-first page it is the value. A reader that
binds role to that order emits, on a value-first page, exactly the gold
structure with the two exchanged, and nothing else about it changes.

That structure is computable from gold, so the claim is checkable item by item
rather than by category. This decodes, deserialises the emission and sorts it
into exact, the exchanged structure, some other executable structure, refused,
or malformed. The exchange is only defined where a page states pairs, so shapes
with no table and no rule are reported separately and never folded in.

Exact equality with the exchanged structure is a strict test and an emission can
carry the inverted binding without meeting it, by getting a default or an entry
order wrong as well. So a looser figure runs beside it: over the symbols gold
uses as a key and not as a value, the share the emission uses as a value and not
as a key. That is the binding on its own, with entry order and defaults taken
out, and it is the number to read when the strict cell is small.

Greedy and sampled both run, because greedy has produced false zeros here.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import Counter

import torch

from src.norm import ndata, neval
from src.norm.lang import Program, Rule, Table
from src.norm.ntok import deserialize
from src.role.rlabels import roles
from src.system import sizes

SEVEN = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
         "precedence")


def exchange(p: Program):
    """The gold structure with every stated pair written the other way round.

    Only `Table` and `Rule` state a pair of symbols in one sentence, so only
    those move. Returns None when the structure states no such pair, which is
    where the positional account makes no prediction.
    """
    defs, touched = [], 0
    for d in p.defs:
        if d.kind == "table":
            ent = tuple((v, k) for k, v in d.entries)
            touched += 1
            defs.append(Table(d.name, ent, d.default, d.ordered))
        elif d.kind == "rule" and d.exceptions:
            touched += 1
            defs.append(Rule(d.name, d.general,
                             tuple((v, k) for k, v in d.exceptions)))
        else:
            defs.append(d)
    if not touched:
        return None
    return Program(tuple(defs), p.inputs, p.steps, p.answer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--split", default="mode")
    ap.add_argument("--n", type=int, default=7000)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--out", default="results/role")
    a = ap.parse_args()

    device = "cuda"
    iv, ov = ndata._vocab()
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=False)
    model = sizes.build_any(ck["size"], len(iv), len(ov)).to(device)
    model.load_state_dict(ck["state"])
    items = neval.load_eval(os.path.join(a.data, a.split), a.n)
    os.makedirs(a.out, exist_ok=True)
    rep = {"ckpt": os.path.abspath(a.ckpt), "tag": a.tag, "split": a.split,
           "n": len(items), "modes": {}}
    rolls = os.path.join(a.out, f"swap_{a.tag}_{a.split}.jsonl.gz")
    fh = gzip.open(rolls, "wt")
    for dm in ("greedy", "sampled"):
        em = neval.emit(model, items, ov, device, dm, batch=a.batch)
        c = Counter()
        for it, e in zip(items, em):
            kp = it["fid"].split(".")[2]
            gold = it["prog"]
            sw = exchange(gold)
            try:
                prog = deserialize(ov.decode(e), it["slots"])
            except Exception:
                cat = "malformed"
            else:
                if prog == gold:
                    cat = "exact"
                elif sw is not None and prog == sw:
                    cat = "exchanged"
                elif not neval.run(prog).ok:
                    cat = "refused"
                else:
                    cat = "other_wrong"
            groups = [kp, f"{kp}|pairs_stated" if sw is not None
                      else f"{kp}|no_pair_stated"]
            if it["shape"] in SEVEN:
                groups.append(f"{kp}|seven")
            gk, gv = roles(gold)
            only_k, only_v = gk - gv, gv - gk
            flip = keep = 0
            if cat != "malformed":
                ek, ev = roles(prog)
                flip = (len([s for s in only_k if s in ev and s not in ek])
                        + len([s for s in only_v if s in ek and s not in ev]))
                keep = (len([s for s in only_k if s in ek and s not in ev])
                        + len([s for s in only_v if s in ev and s not in ek]))
            for g in groups:
                c[(g, "n")] += 1
                c[(g, cat)] += 1
                c[(g, "sym_one_role")] += len(only_k) + len(only_v)
                c[(g, "sym_flipped")] += flip
                c[(g, "sym_kept")] += keep
            fh.write(json.dumps({"fid": it["fid"], "shape": it["shape"],
                                 "mode": dm, "cat": cat}) + "\n")
        rep["modes"][dm] = {}
        print(f"== {a.tag} {a.split} {dm}")
        for g in sorted({k[0] for k in c}):
            n = c[(g, "n")]
            row = {"n": n, **{k: c[(g, k)] for k in
                              ("exact", "exchanged", "other_wrong", "refused",
                               "malformed")}}
            row["exchanged_rate"] = round(c[(g, "exchanged")] / n, 4)
            row["exact_rate"] = round(c[(g, "exact")] / n, 4)
            ns = max(1, c[(g, "sym_one_role")])
            row["n_symbols_with_one_role"] = c[(g, "sym_one_role")]
            row["symbol_role_flipped"] = round(c[(g, "sym_flipped")] / ns, 4)
            row["symbol_role_kept"] = round(c[(g, "sym_kept")] / ns, 4)
            rep["modes"][dm][g] = row
            print(f"   {g:26s} n={n:5d}  exact {row['exact_rate']:.4f}  "
                  f"exchanged {row['exchanged_rate']:.4f}  "
                  f"role kept {row['symbol_role_kept']:.4f}  "
                  f"role flipped {row['symbol_role_flipped']:.4f}  "
                  f"other {c[(g, 'other_wrong')]:4d}  "
                  f"refused {c[(g, 'refused')]:4d}  "
                  f"malformed {c[(g, 'malformed')]:4d}")
    fh.close()
    rep["records"] = os.path.abspath(rolls)
    dest = os.path.join(a.out, f"swap_{a.tag}_{a.split}.json")
    with open(dest, "w") as f:
        json.dump(rep, f, indent=1)
    print("wrote", os.path.abspath(dest))


if __name__ == "__main__":
    main()
