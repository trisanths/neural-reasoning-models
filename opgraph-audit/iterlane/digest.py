"""A small digest of every result file, sized to be read in one go."""
from __future__ import annotations
import glob, json, os, sys

R = "results/iter"


def blocks(r):
    return {k: v for k, v in r.items() if isinstance(v, dict)}


def c(r, cond, kind, d):
    return r.get(cond, {}).get(kind, {}).get(str(d))


def curve(r, cond, kind, f="acc"):
    b = r.get(cond, {}).get(kind, {})
    return " ".join(f"{d}:{b[d][f]:.3f}" for d in sorted(b, key=int))


def n_of(r, cond, kind):
    b = r.get(cond, {}).get(kind, {})
    return next(iter(b.values()))["n"] if b else 0


def main():
    for f in sorted(glob.glob(f"{R}/main_*.json") + glob.glob(f"{R}/wide_*.json")):
        r = json.load(open(f))
        h = r["head"]
        print(f"\n######## {os.path.basename(f)} head={h} steps={r.get('train_step')} "
              f"nodes={r.get('schema_nodes')} slots={r.get('n_slots')}")
        for tag in ("induction", "induction@para"):
            if tag in r:
                v = r[tag]
                print(f"  {tag}: pages={v['pages']} parsed={v['pages_parsed']} "
                      f"gold_ops={v['gold_ops']} induced={v['induced_ops']} "
                      f"exact={v['exact_text']} behav={v['behavioural']}")
        if "counter_check" in r:
            print("  counter:", json.dumps(r["counter_check"]))
        cod = r.get("codec", {}).get("sequential", {})
        print("  codec seq:", " ".join(f"{d}:{cod[d]['codec_rate']:.2f}"
                                       for d in sorted(cod, key=int)))
        B = blocks(r)
        for kind in ("sequential", "novel", "breadth", "sequential_paren",
                     "same_page_pair", "units"):
            if kind not in B.get("oracle_both", {}):
                continue
            print(f"  -- {kind} n={n_of(r,'oracle_both',kind)}")
            for cond in sorted(x for x in B if kind in B[x]):
                if cond in ("codec",):
                    continue
                b = B[cond].get(kind, {})
                if not b or "acc" not in next(iter(b.values())):
                    continue
                print(f"     {cond:32s} acc  {curve(r,cond,kind)}")
            for cond in ("plan_execute@T0@it8", "plan_execute@T0@it8@para"):
                if kind in B.get(cond, {}):
                    for fld in ("parse_rate", "well_typed_rate",
                                "exact_gold_plan_rate", "parsed_but_wrong_rate",
                                "fwd_passes_mean", "position_evals_mean"):
                        print(f"     {cond:32s} {fld:22s} {curve(r,cond,kind,fld)}")
    for f in sorted(glob.glob(f"{R}/iters_*.json")):
        r = json.load(open(f))
        print(f"\n######## {os.path.basename(f)} head={r['head']}")
        for cond in sorted(x for x in blocks(r) if x.startswith("plan_execute")):
            print(f"  {cond:30s} acc {curve(r,cond,'sequential')}")
        for cond in sorted(x for x in blocks(r) if x.startswith("plan_execute")):
            b = r[cond].get("sequential", {})
            for d in sorted(b, key=int):
                v = b[d].get("revision")
                if v:
                    print(f"  REV {cond:26s} d={d:<3} early/item={v['slots_committed_early_per_item']:.1f} "
                          f"chg={v['value_changed_rate']:.4f} mask={v['returned_to_mask_rate']:.4f} "
                          f"fin={v['final_differs_from_first_rate']:.4f} "
                          f"any={v['items_with_any_revision_rate']:.3f} "
                          f"ansfin={v['answer_slot_final_differs_rate']:.3f}")
    for f in sorted(glob.glob(f"{R}/conv_*.json")):
        r = json.load(open(f))
        print(f"CONV {os.path.basename(f):26s} step={r.get('train_step')} "
              f"{curve(r,'plan_execute@T0@it8','sequential')}")
    for f in sorted(glob.glob(f"{R}/peaked_*.json") + glob.glob(f"{R}/planlen_*.json")):
        print(f"\n######## {os.path.basename(f)}")
        print(json.dumps(json.load(open(f))["cells"])[:2500])
    for f in sorted(glob.glob(f"{R}/cond_*.json") + glob.glob(f"{R}/slotdiag_*.json")):
        print(f"\n######## {os.path.basename(f)}")
        print(json.dumps(json.load(open(f)))[:1800])


if __name__ == "__main__":
    main()
