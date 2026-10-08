"""Training examples for one operation, for the network's side of the ladder.

The library is given a page. The network is given labelled pairs: the same
episode text on one side and the structure that wrote it on the other, target
included. That is strictly more than a page carries, and it is the right thing
to give it, because the question is how many examples a gradient learner needs
to acquire one operation and a weaker condition would answer an easier question.

Every example is the same operation: the same operator name, the same
directories, the same rows, the same clauses. What varies is the question key,
the wording mode, where the definition page sits, and which of the 490 training
frames writes the pages. The question keys used for training are disjoint from
the five the item set asks about, so an example never carries a test answer.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random

import numpy as np

from src.norm import ndata, oplang, opsay, optok
from src.norm.lang import def_load
from src.norm.ntok import TokenizeError
from src.norm.opitems import N_ASK

MAX_IN = ndata.MAX_IN
MAX_OUT = 512


def instance_of(row: dict) -> dict:
    """The operation, its directories and its keys, as the item recorded them."""
    b = row["inst"]
    return {"spec": oplang.spec_load(b["spec"]),
            "tables": tuple(def_load(t) for t in b["tables"]),
            "keys": list(b["keys"]), "page_name": b["page_name"]}


def inst_id(row: dict) -> str:
    return "/".join(row["id"].split("/")[:3])


def one_example(inst, fid, key, mode, def_pos, n_pages=1):
    """One (text, target) pair for this operation, or None if it will not fit."""
    spec, tables = inst["spec"], inst["tables"]
    prog = oplang.program_single(spec, tables, key)
    pages = [opsay.directory_page(t, fid) for t in tables]
    defs = [opsay.definition_page(spec, fid, mode, inst["page_name"])]
    for i in range(1, n_pages):
        defs.append(opsay.definition_page(
            spec, fid, opsay.READ_MODES[(opsay.READ_MODES.index(mode) + i)
                                        % len(opsay.READ_MODES)],
            inst["page_name"]))
    text = opsay.episode_text(pages, defs,
                              opsay.question_single(spec, fid, key), def_pos)
    iv, _ = ndata._vocab()
    try:
        ids, slots, n_unk = iv.encode(text)
    except TokenizeError:
        return None
    if n_unk or len(ids) > MAX_IN:
        return None
    ov = optok.OpVocab()
    try:
        toks = optok.serialize(prog, slots, [spec])
    except (TokenizeError, Exception):
        return None
    out = [ov.bos] + ov.encode(toks) + [ov.eos]
    if len(out) > MAX_OUT:
        return None
    return {"in": ids, "out": out, "text": text, "fid": fid}


def pool_for(inst, n: int, seed: int):
    """Up to n examples of this operation, drawn over frames, keys and wording."""
    groups = ndata.split_frames()
    fids = sorted(groups["train"])
    rng = random.Random(seed)
    train_keys = inst["keys"][N_ASK:]
    if not train_keys:
        raise ValueError("the instance keeps no key back for training")
    rows, tries = [], 0
    while len(rows) < n and tries < n * 8:
        tries += 1
        e = one_example(inst, rng.choice(fids), rng.choice(train_keys),
                        rng.choice(opsay.READ_MODES),
                        rng.choice(("first", "last")))
        if e is not None:
            rows.append(e)
    return rows


def write_npz(path: str, rows) -> dict:
    ins = np.concatenate([np.asarray(r["in"], dtype=np.uint16) for r in rows])
    outs = np.concatenate([np.asarray(r["out"], dtype=np.uint16)
                           for r in rows])
    ioff = np.cumsum([0] + [len(r["in"]) for r in rows]).astype(np.int64)
    ooff = np.cumsum([0] + [len(r["out"]) for r in rows]).astype(np.int64)
    np.savez(path, ins=ins, outs=outs, ioff=ioff, ooff=ooff)
    return {"path": os.path.abspath(path), "n": len(rows),
            "in_max": int(np.max([len(r["in"]) for r in rows])),
            "out_max": int(np.max([len(r["out"]) for r in rows]))}


def pick_instances(items, n_each=2):
    """A few instances per family, taken in a fixed order from the item set."""
    seen, out = {}, []
    for r in items:
        if r["cond"] != "acq" or r["n_pages"] != 1:
            continue
        iid = inst_id(r)
        if iid in seen:
            continue
        seen[iid] = True
        fam = r["family"]
        if sum(1 for o in out if o["family"] == fam) >= n_each:
            continue
        out.append({"inst_id": iid, "family": fam, "fid": r["fid"],
                    "split": r["split"], "row": r})
    return out


def family_pool(items, n: int, seed: int, exclude=()):
    """A pool drawn over many different operations rather than one.

    This is the condition that asks what the network can do once it has been
    trained on the family at length: it sees a thousand examples of agreement
    operations, each a different operation, all at one application, and is then
    asked for depth and for composition. What it cannot do after that is a
    ceiling of the network and not a shortage of examples.
    """
    rng = random.Random(seed)
    pool = [r for r in items
            if r["cond"] == "acq" and r["n_pages"] == 1
            and inst_id(r) not in set(exclude)]
    groups = ndata.split_frames()
    fids = sorted(groups["train"])
    rows, tries = [], 0
    while len(rows) < n and tries < n * 8:
        tries += 1
        row = rng.choice(pool)
        inst = instance_of(row)
        keys = inst["keys"][N_ASK:]
        e = one_example(inst, rng.choice(fids), rng.choice(keys),
                        rng.choice(opsay.READ_MODES),
                        rng.choice(("first", "last")))
        if e is not None:
            rows.append(e)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="results/norm/oneshot/items.jsonl.gz")
    ap.add_argument("--out", default="data/norm/oneshot")
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--each", type=int, default=2)
    ap.add_argument("--seed", type=int, default=99)
    ap.add_argument("--family", type=int, default=1024)
    a = ap.parse_args()

    items = [json.loads(l) for l in gzip.open(a.items, "rt")]
    os.makedirs(a.out, exist_ok=True)
    picked = pick_instances(items, a.each)
    man = {"items": os.path.abspath(a.items), "n": a.n, "seed": a.seed,
           "instances": []}
    for i, p in enumerate(picked):
        inst = instance_of(p["row"])
        rows = pool_for(inst, a.n, a.seed + i * 977)
        tag = p["inst_id"].replace("/", "_")
        info = write_npz(os.path.join(a.out, f"{tag}.npz"), rows)
        info.update({"inst_id": p["inst_id"], "family": p["family"],
                     "fid": p["fid"], "split": p["split"], "tag": tag,
                     "op": inst["spec"].name, "arity": inst["spec"].arity,
                     "n_eval_items": sum(1 for r in items
                                         if r["cond"] == "acq"
                                         and inst_id(r) == p["inst_id"])})
        man["instances"].append(info)
        print(json.dumps(info), flush=True)
    if a.family:
        rows = family_pool(items, a.family, a.seed + 31,
                           [p["inst_id"] for p in picked])
        man["family"] = write_npz(os.path.join(a.out, "family.npz"), rows)
        man["family"]["n_operations"] = a.family
        print(json.dumps(man["family"]), flush=True)
    with open(os.path.join(a.out, "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=2)
    print(json.dumps({"n_instances": len(man["instances"]),
                      "out": os.path.abspath(a.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
