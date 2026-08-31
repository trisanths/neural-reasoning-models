"""Is the balanced grid draw disjoint from the transposed test's item set.

`data/norm/grid_both.npz` carries both operand orders and would be the data
fix for the transposed-operand failure. It is only usable as that fix if none
of its pages are the pages the test scores on, so the two are compared as
whole programs rather than by name.
"""
import gzip
import json
import os

ROOT = os.path.expanduser("~/decoupled-reasoner")


def prog_key(prog, slots):
    return json.dumps({"p": prog, "s": slots}, sort_keys=True)


both = set()
n_both = 0
for line in open(os.path.join(ROOT, "data/norm/grid_both.meta.jsonl")):
    d = json.loads(line)
    if d.get("prog"):
        both.add(prog_key(d["prog"], d.get("slots")))
        n_both += 1

train = set()
n_train = 0
for line in open(os.path.join(ROOT, "data/norm/grid_train.meta.jsonl")):
    d = json.loads(line)
    if d.get("prog"):
        train.add(prog_key(d["prog"], d.get("slots")))
        n_train += 1

items = {"original": set(), "transposed": set()}
n_items = 0
for line in gzip.open(os.path.join(ROOT,
                                   "results/norm/compare/x_items.jsonl.gz"),
                      "rt"):
    d = json.loads(line)
    items[d["version"]].add(prog_key(d["prog"], d.get("slots")))
    n_items += 1

print(f"grid_both pages {n_both}, distinct {len(both)}")
print(f"grid_train pages {n_train}, distinct {len(train)}")
print(f"x_items rows {n_items}, distinct original {len(items['original'])}, "
      f"transposed {len(items['transposed'])}")
for v in ("original", "transposed"):
    print(f"grid_both  n x_items[{v}] = {len(both & items[v])}")
    print(f"grid_train n x_items[{v}] = {len(train & items[v])}")
print(f"grid_both n grid_train = {len(both & train)}")

out = os.path.join(ROOT, "results/system/grid_overlap.json")
with open(out, "w") as fh:
    json.dump({"grid_both": n_both, "grid_train": n_train,
               "x_items": n_items,
               "overlap_both_original": len(both & items["original"]),
               "overlap_both_transposed": len(both & items["transposed"]),
               "overlap_train_original": len(train & items["original"]),
               "overlap_train_transposed": len(train & items["transposed"]),
               "overlap_both_train": len(both & train)}, fh, indent=1)
print("wrote", out)
