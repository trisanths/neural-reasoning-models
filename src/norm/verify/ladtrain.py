"""A ladder item set drawn from TRAIN frames instead of held-out frames.

opladder.py draws every ladder item from the four held-out frame groups, so the
published ladder cannot separate "the network did not acquire the operation"
from "the network did not carry it into a wording it never trained on". This
builds the same 800 rows from the frames the normalizer did train on. Only the
frame pool differs.
"""
import argparse, gzip, json, os, random
from src.norm import ndata, opdata, opitems, opsay
from src.norm.opitems import N_ASK


def train_frames():
    return sorted(ndata.split_frames()["train"])


def build(manifest, items_by_inst, n_draws, seed):
    rows = []
    fids = train_frames()
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
                          "fid": fid, "split": "train",
                          "skeleton": "", "arity": info["arity"],
                          "inst_id": info["inst_id"],
                          "id": "ladder/%s/%d/%d" % (info["tag"], ki, d),
                          "item_key": "ladder/%s/%d/%d" % (info["tag"], ki, d)})
                rows.append(e)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/norm/oneshot/manifest.json")
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--out", default="results/norm/oneshot/verify/ladder_train_items.jsonl.gz")
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
            "frame_pool": "train", "n_train_frames": len(train_frames()),
            "n_by_inst": {i["inst_id"]: sum(1 for r in rows if r["inst_id"] == i["inst_id"])
                          for i in man["instances"]},
            "out": os.path.abspath(a.out)}
    with open(a.out.replace(".jsonl.gz", ".meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
