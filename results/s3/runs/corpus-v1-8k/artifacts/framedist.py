"""Distance from each evaluation frame to the nearest frame the corpus trained.

The corpus external component uses `split_frames("both")["train"]`, 72 of the
156 frames in `src/frames/generate.py`. An evaluation frame in that set is
seen; every other frame is held out, and its distance is the smallest distance
to anything in the set. Shape and lexicon are kept apart: the ablation on
record found a lexicon swap costs 0.13 and a shape swap costs 0.94, and one
scalar would mix them.
"""
import json, sys
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.frames.generate import FRAMES, split_frames
from src.frames.distance import signature, shape_distance, lex_distance

sp = split_frames("both")
TRAIN = set(sp["train"])
manifest = json.load(open("/home/ec2-user/sweep/eval/gen/manifest.json"))
eval_frames = sorted({m["frame"] for m in manifest})
families = sorted({m["family"] for m in manifest})

out = {}
for fam in families:
    sig = {n: signature(FRAMES[n], fam) for n in set(eval_frames) | TRAIN}
    for ev in eval_frames:
        best = None
        for tr in TRAIN:
            if tr == ev:
                best = {"nearest": tr, "shape": 0.0, "lex": 0.0}
                break
            sd = shape_distance(sig[ev]["skeleton"], sig[tr]["skeleton"])
            ld = lex_distance(set(sig[ev]["words"]), set(sig[tr]["words"]))
            if best is None or (sd, ld) < (best["shape"], best["lex"]):
                best = {"nearest": tr, "shape": round(sd, 4), "lex": round(ld, 4)}
        split = ("train" if ev in TRAIN else
                 "test" if ev in set(sp["test"]) else
                 "bridge" if ev in set(sp["bridge"]) else "other")
        out[f"{fam}|{ev}"] = {"family": fam, "frame": ev, "split": split,
                              "seen_by_corpus": ev in TRAIN, **best}
path = "/home/ec2-user/retrain/frames/frame_distance.json"
json.dump({"n_train_frames": len(TRAIN), "eval_frames": eval_frames,
           "rows": out}, open(path, "w"), indent=1)
print("train frames:", len(TRAIN), "| eval frames:", len(eval_frames))
print("%-24s %-18s %-7s %-5s %7s %7s  %s" %
      ("frame", "family", "split", "seen", "shape", "lex", "nearest trained"))
for k in sorted(out):
    r = out[k]
    print("%-24s %-18s %-7s %-5s %7.3f %7.3f  %s" %
          (r["frame"], r["family"], r["split"], str(r["seen_by_corpus"]),
           r["shape"], r["lex"], r["nearest"]))
print("wrote", path)
