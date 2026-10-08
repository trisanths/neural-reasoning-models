"""Per-family samples of the relation component, held-out band and train band.

Twelve structures are in training and four are held out; the held-out four are
the relation-type generalisation test that replaces the retired probe. Each
family gets its own file so nothing is ever pooled across families.
"""
import json, collections, os, sys

OUT = "/home/ec2-user/retrain/relation"
os.makedirs(OUT, exist_ok=True)
PER_FAMILY = 100          # episodes; load_tasks takes 2 questions from each

TRAINED = {"substitution", "threshold", "exception_rule", "inverse_table",
           "chain_rule", "band_rule", "inverse_chain", "transitive",
           "lookup_then_band", "band_then_lookup", "weighted_chain",
           "modular_apply"}

for band, src, stride in (("heldout", "/home/ec2-user/corpus/v1/relation_heldout.jsonl", 1),
                          ("train", "/home/ec2-user/corpus/v1/relation_train.jsonl", 37)):
    kept = collections.defaultdict(list)
    with open(src) as fh:
        for i, line in enumerate(fh):
            if i % stride:
                continue
            # the training pack took every fifth episode of this file; keep
            # the train-band anchor off the exact items the run trained on
            if band == "train" and i % 5 == 0:
                continue
            d = json.loads(line)
            f = d["family"]
            if len(kept[f]) >= PER_FAMILY:
                if all(len(v) >= PER_FAMILY for v in kept.values()) and len(kept) >= 12:
                    if band == "train" and len(kept) >= 12:
                        break
                continue
            kept[f].append(d)
    path = os.path.join(OUT, f"rel_{band}.jsonl")
    frames = collections.Counter()
    with open(path, "w") as fh:
        for f in sorted(kept):
            for d in kept[f]:
                frames[d.get("frame")] += 1
                fh.write(json.dumps(d) + "\n")
    print(band, "families", len(kept),
          {k: len(v) for k, v in sorted(kept.items())},
          "distinct frames", len(frames))
    print("  in-training families present:",
          sorted(set(kept) & TRAINED), "| held-out:", sorted(set(kept) - TRAINED))
