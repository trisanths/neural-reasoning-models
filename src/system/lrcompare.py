"""The control against the rung it controls, step for step, so far."""
import json
import os

ROOT = os.path.expanduser("~/decoupled-reasoner")


def series(tag, path=None):
    p = path or os.path.join(ROOT, f"results/system/train/log_{tag}.jsonl")
    st, ev = {}, {}
    for line in open(p):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "step":
            st[r["step"]] = r["loss"]
        if r.get("event") == "eval":
            ev[r["step"]] = r
    return st, ev


a, ae = series("xl93")
b, be = series("xl93lr40")
c, ce = series("l45", os.path.join(ROOT, "results/norm/train/log_l.jsonl"))
common = sorted(s for s in b if s in a and s % 3000 == 0)
print("training loss, lower is better")
print("step".rjust(7) + "l45 4.0e-4".rjust(13) + "xl93 3.2e-4".rjust(14)
      + "xl93 4.0e-4".rjust(14) + "  control ahead of xl93")
for s in common:
    print(f"{s:7d}{c.get(s, float('nan')):13.4f}{a[s]:14.4f}{b[s]:14.4f}"
          + ("   yes" if b[s] < a[s] else "   no"))
print()
print("in-training eval, 700 items, greedy exact")
print("step".rjust(7) + "  run".ljust(14) + "train".rjust(9)
      + "qframe".rjust(9) + "lexicon".rjust(9) + "mode".rjust(9))
for s in sorted(be):
    for lab, d in (("l45", ce.get(s)), ("xl93 3.2e-4", ae.get(s)),
                   ("xl93 4.0e-4", be.get(s))):
        if not d:
            continue
        print(f"{s:7d}  {lab:12s}" + "".join(
            f"{d[k]:9.4f}" for k in ("train_frames_eval", "qframe",
                                     "lexicon", "mode")))
    print()
