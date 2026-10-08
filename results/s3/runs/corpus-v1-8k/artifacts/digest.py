"""Compact digest of every score file, small enough to print."""
import json, os, sys, glob
R = "/home/ec2-user/retrain"

def jload(p):
    try:
        return json.load(open(p))
    except Exception:
        return None

what = sys.argv[1] if len(sys.argv) > 1 else "all"

if what in ("all", "gate"):
    print("=" * 78); print("GATE")
    for w in ("base", "new"):
        d = jload(f"{R}/gate/strict_gate_{w}.json")
        if not d:
            print(f"  {w}: not ready"); continue
        for k in sorted(d["cells"]):
            c = d["cells"][k]
            print("  %-6s %-42s nQ %4s nR %5s floor %.3f ship %.4f forced %.4f "
                  "first %.4f hedge %.3f none %.3f"
                  % (w, k, c.get("n_questions"), c.get("n_rollouts"),
                     c.get("floor", 0), c.get("acc_shipped", 0),
                     c.get("acc_forced", 0), c.get("acc_first", 0),
                     c.get("hedge_rate", 0), c.get("none_rate", 0)))

if what in ("all", "transposed"):
    print("=" * 78); print("TRANSPOSED RULE")
    for w in ("base", "new"):
        rows = jload(f"{R}/transposed/score_{w}.json")
        if not rows:
            print(f"  {w}: not ready"); continue
        for r in rows:
            print("  %-5s %-7s d=%-4s n %4d chance %.3f  page %.4f  train %.4f"
                  "  other %.4f hedge %.3f none %.3f rounds %.2f gen %.1f"
                  % (w, r["decode"], r["depth"], r["n"], r["chance"],
                     r["forced_page"], r["forced_train"], r["forced_other"],
                     r["hedge"], r["none"], r["mean_rounds"],
                     r["mean_generated"]))

if what in ("all", "plan"):
    print("=" * 78); print("PLAN")
    for w in ("base", "new"):
        for s in ("heldout_whole_sample", "extrap_whole"):
            d = jload(f"{R}/plan/score_{w}_{s}.json")
            if not d:
                print(f"  {w}/{s}: not ready"); continue
            print("  -- %s %s  determinate rate %.3f" % (w, s, d["determinate_rate"]))
            for r in d["determinate_by_required_steps"]:
                print("     %-7s req %3d n %4d acc %.3f emit %6.2f max %3d "
                      "long %.3f noplan %.3f"
                      % (r["decode"], r["required_steps"], r["n"], r["accuracy"],
                         r["emitted_steps_mean"], r["emitted_steps_max"],
                         r["long_enough"], r["no_plan_rate"]))
            for r in d["determinate_by_required_symbols"]:
                print("     %-7s syms %d n %4d acc %.3f emitSyms %.3f enough %.3f"
                      % (r["decode"], r["required_symbols"], r["n"],
                         r["accuracy"], r["emitted_symbols_mean"],
                         r["enough_symbols"]))

if what in ("all", "relation"):
    print("=" * 78); print("RELATION")
    for w in ("base", "new"):
        for band in ("heldout", "train"):
            d = jload(f"{R}/relation/score_{w}_{band}.json")
            if not d:
                print(f"  {w}/{band}: not ready"); continue
            print("  -- %s %s" % (w, band))
            for k in sorted(d["records"]):
                s = d["records"][k]
                print("     %-30s n %4d forced %.3f first %.3f chance %.3f "
                      "hedge %.3f none %.3f served %.3f exact %.3f"
                      % (k, s["n"], s["acc_forced"], s["acc_first"],
                         s["chance_cand"], s["hedge_rate"], s["none_rate"],
                         s["served_rate"], s.get("acc_exact", 0)))
            for k in sorted(d.get("open_answer_records", {})):
                s = d["open_answer_records"][k]
                print("     %-30s n %4d exact %.3f shipped %.3f rounds %.2f"
                      % (k + " [open]", s["n"], s["acc_exact"],
                         s["acc_shipped"], s["mean_rounds"]))
            for dec, mv in d["macro_over_families"].items():
                print("     macro %-8s cells %d acc %.3f chance %.3f A %.3f B %.3f"
                      % (dec, mv["cells"], mv["macro_accuracy"],
                         mv["macro_chance"], mv["order_A_corrected_macro"],
                         mv["order_B_mean_of_corrected"]))

if what in ("all", "frames"):
    print("=" * 78); print("FRAMES  (run framecurve.py first)")
    d = jload(f"{R}/frames/curve.json")
    if not d:
        print("  not ready")
    else:
        for k in sorted(d["buckets"]):
            b = d["buckets"][k]
            print("  %-34s frames %2d n %5d forced %.3f first %.3f chance %.3f "
                  "hedge %.3f none %.3f served %.3f"
                  % (k, b["frames"], b["n"], b["acc_forced"], b["acc_first"],
                     b["chance_cand"], b["hedge_rate"], b["none_rate"],
                     b["served_rate"]))
