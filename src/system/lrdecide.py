"""Which peak rate the two expensive rungs run at, decided by the control.

The 93M rung was trained twice: once at the inverse-width rate the ladder
inherited, 3.2e-4, and once at the 45M rung's own peak, 4.0e-4, with the same
seed, the same 30,000 steps and the same 32,768 token batch. If the second fits
its training file better, the inverse-width rule is what put the 93M rung
behind the 45M rung and the ladder's parameter axis is confounded by it, so the
rungs above run at the 45M rung's rate and the ladder becomes one rate across
four widths. If it does not fit better, the rule stands and the fit gap is a
property of the width rather than of the rate.

The comparison is training loss, because that is what the confound is about.
The held-out numbers are written down beside it and are not what decides.

This runs detached and writes `results/system/lr_xxl167` and
`results/system/lr_xxxl355`, which `src/system/queue2.sh` reads at the moment
each rung starts. A missing file means `src/system/sizes.py:LR`.
"""
from __future__ import annotations

import json
import os
import time

ROOT = os.path.expanduser("~/decoupled-reasoner")
CTL = "xl93lr40"
BASE = "xl93"
PEAK_45M = 4.0e-4


TAIL_STEPS = 5000


def final_loss(tag, tail=TAIL_STEPS):
    """The mean loss over the last `tail` steps, not the last logged window.

    strain.py logs the mean over each 200 steps, so the final logged value is
    one sample of a noisy quantity. On this pair the two orderings disagree:
    the last window puts the control behind at 0.0187 against 0.0182, and the
    last 5,000 steps put it ahead at 0.01779 against 0.02007. A rate for
    thirteen hours of training should not turn on which window it landed in.
    """
    path = os.path.join(ROOT, f"results/system/train/log_{tag}.jsonl")
    if not os.path.exists(path):
        return None
    steps = []
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("event") == "step":
            steps.append((r["step"], r["loss"]))
    if not steps:
        return None
    steps.sort()
    k = max(1, tail // 200)
    window = steps[-k:]
    mean = sum(l for _, l in window) / len(window)
    return (steps[-1][0], round(mean, 6))


def mode_exact(tag):
    p = os.path.join(ROOT, f"results/system/eval/{tag}/summary.json")
    if not os.path.exists(p):
        return None
    s = json.load(open(p))
    try:
        return s["splits"]["mode"]["modes"]["greedy"][
            "pooled_do_not_headline"]["exact"]
    except KeyError:
        return None


def main():
    log = open(os.path.join(ROOT, "logs/system/lrdecide.log"), "a")

    def say(d):
        log.write(json.dumps(d) + "\n")
        log.flush()

    say({"event": "start", "t": time.strftime("%H:%M:%S")})
    target = os.path.join(ROOT, f"results/system/eval/{CTL}/summary.json")
    while not os.path.exists(target):
        time.sleep(60)
    time.sleep(10)

    b, c = final_loss(BASE), final_loss(CTL)
    mb, mc = mode_exact(BASE), mode_exact(CTL)
    if b is None or c is None:
        say({"event": "abort", "reason": "a training log is missing",
             "base": b, "control": c})
        return 1
    better = c[1] < b[1]
    rate = PEAK_45M if better else 0.0
    for rung in ("xxl167", "xxxl355"):
        with open(os.path.join(ROOT, f"results/system/lr_{rung}"), "w") as fh:
            fh.write(f"{rate}\n")
    say({"event": "decided", "t": time.strftime("%H:%M:%S"),
         "base_tag": BASE, "base_final": b, "base_mode_exact": mb,
         "control_tag": CTL, "control_final": c, "control_mode_exact": mc,
         "control_fits_better": better,
         "comparison": f"mean training loss over the last {TAIL_STEPS} steps",
         "rate_for_xxl167_and_xxxl355": rate,
         "meaning": ("the 45M rung's own peak, one rate across the ladder"
                     if better else "src/system/sizes.py:LR, unchanged")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
