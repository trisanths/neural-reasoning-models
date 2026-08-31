"""The item set the acquisition ladder is scored on, for both systems.

One ladder instance is one operation. Its five question keys are the ones the
main item set asks about and are disjoint from the three the network trains on.
Each key is asked in twenty (frame, wording, page order) combinations drawn from
the frames the normalizer never trained on, so an item is new on its wording as
well as on its key, and an operation that was memorised on one wording does not
score here for that.

The library system and the network answer these same rows, so the two sides of
the curve are the same denominators.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random

from src.norm import ndata, opdata, opitems, opsay
from src.norm.opitems import N_ASK

HELD = ("qframe", "lexicon", "mode", "mixed")


def held_frames():
    sp = ndata.split_frames()
    out = []
    for s in HELD:
        out.extend(sorted(sp[s]))
    return out


def build(manifest, items_by_inst, n_draws: int, seed: int):
    rows = []
    fids = held_frames()
    sp = ndata.split_frames()
    split_of = {}
    for s in HELD:
        for f in sp[s]:
            split_of[f] = s
    for i, info in enumerate(manifest["instances"]):
        row = items_by_inst[info["inst_id"]]
        inst = opdata.instance_of(row)
        inst["page_name"] = row["inst"]["page_name"]
        rng = random.Random(seed + i * 613)
        for ki, key in enumerate(inst["keys"][:N_ASK]):
            for d in range(n_draws):
                fid = rng.choice(fids)
                mode = rng.choice(opsay.READ_MODES)
                pos = rng.choice(("first", "last"))
                e = opitems.episode(inst, fid, "single", key, mode=mode,
                                    n_pages=1, def_pos=pos)
                if e is None:
                    continue
                e.update({"cond": "ladder", "family": info["family"],
                          "fid": fid, "split": split_of[fid],
                          "skeleton": "", "arity": info["arity"],
                          "inst_id": info["inst_id"],
                          "id": f"ladder/{info['tag']}/{ki}/{d}",
                          "item_key": f"ladder/{info['tag']}/{ki}/{d}"})
                rows.append(e)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/norm/oneshot/manifest.json")
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--out", default="results/norm/oneshot/ladder_items.jsonl.gz")
    ap.add_argument("--draws", type=int, default=20)
    ap.add_argument("--seed", type=int, default=771)
    a = ap.parse_args()

    man = json.load(open(a.manifest))
    by_inst = {}
    for line in gzip.open(a.items, "rt"):
        r = json.loads(line)
        if r["cond"] != "acq" or r["n_pages"] != 1:
            continue
        by_inst.setdefault(opdata.inst_id(r), r)
    rows = build(man, by_inst, a.draws, a.seed)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, "wt") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    meta = {"n_items": len(rows), "draws": a.draws, "seed": a.seed,
            "instances": [i["inst_id"] for i in man["instances"]],
            "n_by_inst": {i["inst_id"]:
                          sum(1 for r in rows if r["inst_id"] == i["inst_id"])
                          for i in man["instances"]},
            "held_splits": list(HELD), "out": os.path.abspath(a.out)}
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
