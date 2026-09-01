"""The automatic gate between building the data and training on it.

Three conditions, all read from the report files rather than from memory of
what the build printed. Any failure exits non-zero and the run stops.

  contamination   no MMLU, GSM8K, ARC or WinoGrande test item appears
                  verbatim in the training text. Exactly zero is required;
                  a single verbatim test item would make a benchmark number
                  a lookup and there is no threshold at which that is fine.

  verified        every episode file re-checks clean at or above the stated
                  rate, from the written file rather than from the object
                  that built it. Below that rate the traces do not describe
                  what the serving gate will actually do.

  packed          the mixture holds both halves, neither empty and neither
                  more than the stated share, so a run cannot silently train
                  on one component because the other failed to build.

The near-duplicate count is printed and not gated on: a paraphrase threshold
is a judgement call and a number to argue with, not a tripwire.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REQUIRED_CLEAN = 0.95
REAL_COMPONENTS = ("hotpot_qa", "natural_questions", "trivia_qa")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ec2-user/realret")
    ap.add_argument("--min-clean", type=float, default=REQUIRED_CLEAN)
    a = ap.parse_args()
    R = a.root
    fails: list[str] = []
    notes: list[str] = []

    cpath = os.path.join(R, "reports/contamination.json")
    if not os.path.exists(cpath):
        fails.append("contamination report missing")
    else:
        c = json.load(open(cpath))
        notes.append(f"contamination exact={c['exact_matches']} "
                     f"near={c['near_matches']} "
                     f"by_task_exact={json.dumps(c['exact_by_task'])} "
                     f"scanned_questions={c['training_questions_scanned']} "
                     f"scanned_documents={c['training_documents_scanned']}")
        if c["exact_matches"] != 0:
            fails.append(f"{c['exact_matches']} verbatim benchmark test items "
                         f"in the training data")

    vpath = os.path.join(R, "reports/verify.json")
    if not os.path.exists(vpath):
        fails.append("verify report missing")
    else:
        v = json.load(open(vpath))
        for path, r in v["files"].items():
            notes.append(f"verify {os.path.basename(path)} "
                         f"checked={r['checked']} clean={r['clean_rate']} "
                         f"reasons={json.dumps(r['reasons'])}")
            if r["clean_rate"] < a.min_clean:
                fails.append(f"{os.path.basename(path)} verifies at "
                             f"{r['clean_rate']}, under {a.min_clean}")

    mpath = os.path.join(R, "pack/mix_real1.summary.json")
    if not os.path.exists(mpath):
        fails.append("merged pack summary missing")
    else:
        m = json.load(open(mpath))
        per = m.get("per_component", {})
        total = sum(per.values()) or 1
        real = sum(v for k, v in per.items() if k in REAL_COMPONENTS)
        synth = total - real
        notes.append(f"pack n={m['n']} tokens={m['tokens']} "
                     f"per_component={json.dumps(per)} "
                     f"real={real} synthetic={synth} "
                     f"real_share={round(real / total, 4)}")
        if real == 0:
            fails.append("no real-document examples in the mixture")
        if synth == 0:
            fails.append("no synthetic examples in the mixture")
        if not 0.35 <= real / total <= 0.65:
            fails.append(f"real share {round(real / total, 4)} is outside "
                         f"the one-to-one mixture the run states")

    for n in notes:
        print(n)
    if fails:
        print("GATE FAILED")
        for f in fails:
            print("  " + f)
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
