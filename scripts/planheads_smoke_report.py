"""Condense the smoke run into the four things it is allowed to establish.

  does the head train                loss at the first and last logged step
  does the executor accept its plan  parse rate and accuracy at depth one
  is oracle_both 1.000               under the head, and through its own codec
  is the forward counter right       reported against the count the model saw
  are the arms still matched         sequences dropped for not fitting max_len,
                                     which has to be zero for every head

Accuracy at any depth is printed for orientation only. The smoke trains on a few
hundred worlds for a few hundred steps and scores eight items a cell, so nothing
in the accuracy columns is a result.
"""

from __future__ import annotations

import glob
import json
import os
import sys


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "results/smoke"
    heads = ["p1", "p2", "p2s", "p3", "p4"]
    print("plan head smoke")
    print("=" * 78)
    print()
    print("train loss, first logged step to last")
    for h in heads:
        path = f"runs/smoke/{h}.pt.log.json"
        if not os.path.exists(path):
            print(f"  {h:4s} MISSING {path}")
            continue
        log = json.load(open(path))["log"]
        ind = [r for r in log if r["kind"] == "induce"]
        pl = [r for r in log if r["kind"] == "plan"]
        def span(rows):
            return f"{rows[0]['loss']:.3f} -> {rows[-1]['loss']:.3f}" if rows else "none"
        print(f"  {h:4s} induce {span(ind):18s} plan {span(pl):18s} "
              f"steps={log[-1]['step']} secs={log[-1]['secs']}")
    print()

    bad: list[str] = []
    print("sequences dropped for not fitting max_len, which must be zero")
    for h in heads:
        path = f"runs/smoke/{h}.pt.log.json"
        if not os.path.exists(path):
            continue
        d = json.load(open(path)).get("dropped")
        if d is None:
            print(f"  {h:4s} not recorded by this run")
            continue
        bad_drop = d["induce"] + d["plan"]
        print(f"  {h:4s} induce={d['induce']} plan={d['plan']} "
              f"of {d['sequences']} sequences "
              f"{'ok' if not bad_drop else 'ARMS NOT MATCHED'}")
        if bad_drop:
            bad.append(f"{h}/dropped")
    print()

    print("codec round trip over the evaluation grid, before any model ran")
    codec = os.path.join(os.path.dirname(root) or ".", "planheads_codec_check.json")
    if os.path.exists(codec):
        blob = json.load(open(codec))
        for h in heads:
            block = blob["heads"].get(h, {})
            tot = ok = 0
            for style in block.values():
                for kd in style.values():
                    for c in kd.values():
                        tot += c["n"]
                        ok += c["ok"]
            flag = "ok" if ok == tot and tot else "CAPPED"
            print(f"  {h:4s} {ok}/{tot} gold plans survive this head's "
                  f"representation {flag}")
            if ok != tot or not tot:
                bad.append(f"{h}/codec")
    else:
        print(f"  MISSING {codec}")
        bad.append("codec_check")
    print()

    print("oracle_both, which must be 1.000 everywhere or the harness is broken")
    for h in heads:
        path = os.path.join(root, f"{h}.json")
        if not os.path.exists(path):
            print(f"  {h:4s} MISSING {path}")
            bad.append(h)
            continue
        res = json.load(open(path))
        for name in ("oracle_both", "oracle_both_roundtrip"):
            cells = [(k, d, c) for k, kd in res.get(name, {}).items()
                     for d, c in kd.items()]
            accs = {c["acc"] for _, _, c in cells}
            n = sum(c["n"] for _, _, c in cells)
            worst = min(accs) if accs else 0.0
            flag = "ok" if accs == {1.0} else "BROKEN"
            print(f"  {h:4s} {name:24s} cells={len(cells)} n={n} "
                  f"min_acc={worst:.3f} {flag}")
            if accs != {1.0}:
                bad.append(f"{h}/{name}")
    print()

    print("forward pass counter, reported against the count the model saw")
    for h in heads:
        path = os.path.join(root, f"{h}.json")
        if not os.path.exists(path):
            continue
        res = json.load(open(path))
        for name, chk in res.get("counter_check", {}).items():
            flag = "ok" if chk["ok"] else "MISMATCH"
            print(f"  {name:24s} reported={chk['reported']:5d} "
                  f"observed={chk['observed']:5d} {flag}")
            if not chk["ok"]:
                bad.append(f"{h}/counter")
    print()

    print("plan construction: does the executor accept what the head writes")
    print(f"  {'head':6s} {'condition':34s} {'kind':12s} {'d':>2s} {'n':>3s} "
          f"{'acc':>6s} {'parse':>6s} {'typed':>6s} {'exact':>6s} {'fwd':>7s}")
    for h in heads:
        path = os.path.join(root, f"{h}.json")
        if not os.path.exists(path):
            continue
        res = json.load(open(path))
        for name in sorted(res):
            if not name.startswith(("plan_execute", "oracle_ops", "oracle_plan")):
                continue
            for kind in sorted(res[name]):
                for d in sorted(res[name][kind], key=int):
                    c = res[name][kind][d]
                    print(f"  {h:6s} {name:34s} {kind:12s} {d:>2s} {c['n']:>3d} "
                          f"{c['acc']:>6.3f} {c['parse_rate']:>6.3f} "
                          f"{c['well_typed_rate']:>6.3f} "
                          f"{c['exact_gold_plan_rate']:>6.3f} "
                          f"{c['fwd_passes_mean']:>7.1f}")
    print()
    print("compute per plan, averaged over every scored cell")
    print(f"  {'head':6s} {'condition':34s} {'fwd':>8s} {'decisions':>10s} "
          f"{'positions':>10s}")
    for h in heads:
        path = os.path.join(root, f"{h}.json")
        if not os.path.exists(path):
            continue
        res = json.load(open(path))
        for name in sorted(res):
            if not name.startswith(("plan_execute", "oracle_ops")):
                continue
            cells = [c for kd in res[name].values() for c in kd.values()]
            if not cells:
                continue
            f = sum(c["fwd_passes_mean"] for c in cells) / len(cells)
            dcn = sum(c["slot_decisions_mean"] for c in cells) / len(cells)
            p = sum(c["position_evals_mean"] for c in cells) / len(cells)
            print(f"  {h:6s} {name:34s} {f:>8.1f} {dcn:>10.1f} {p:>10.1f}")
    print()
    print("did the head learn anything: sequential depth one, the easiest cell")
    print("inside the training holdout. A head that is 0.000 here has not")
    print("learned to plan at this budget, whatever the harness checks say.")
    for h in heads:
        path = os.path.join(root, f"{h}.json")
        if not os.path.exists(path):
            continue
        res = json.load(open(path))
        best = None
        where = ""
        for name in sorted(res):
            if not name.startswith("plan_execute"):
                continue
            cell = res[name].get("sequential", {}).get("1")
            if cell is None:
                continue
            if best is None or cell["acc"] > best:
                best = cell["acc"]
                where = name
        if best is None:
            continue
        flag = "ok" if best > 0 else "HEAD DID NOT LEARN"
        print(f"  {h:4s} best depth-1 accuracy {best:.3f} at {where} {flag}")
        if best <= 0:
            bad.append(f"{h}/did-not-learn")
    print()
    print("corruption mixture actually drawn during training")
    for h in heads:
        path = f"runs/smoke/{h}.pt.log.json"
        if not os.path.exists(path):
            continue
        blob = json.load(open(path))
        counts = blob.get("corruption_counts") or {}
        if not counts:
            continue
        tot = sum(counts.values())
        got = {k: round(v / tot, 3) for k, v in sorted(counts.items())}
        print(f"  {h:4s} declared={json.dumps(blob['corruption_mixture'])}")
        print(f"       drawn   ={json.dumps(got)} over {tot} examples")
    print()
    print("VERDICT:", "smoke clean" if not bad else f"problems in {sorted(set(bad))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
