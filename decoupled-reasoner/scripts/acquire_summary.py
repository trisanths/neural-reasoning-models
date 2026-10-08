"""Print one run's cells, per level and phrasing and per chapter.

There is no headline number here on purpose. A pooled score once hid a whole
task family sitting at zero in this project, so every row carries its own n
and a caller who wants a single figure has to name the cell it comes from.
"""

from __future__ import annotations

import argparse
import json


def _fmt(v, nd=3):
    if v is None:
        return "  n/a"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def print_report(rep: dict, title: str) -> None:
    print(f"\n=== {title}  n={rep.get('n_traces')} ===")
    header = ("cell            n  base  after  gated  abst  fire  fire|blk  "
              "saved  cost  nrec  erec  ord   card/raw")
    for group in ("by_level_and_phrasing", "by_chapter"):
        if group not in rep:
            continue
        print(f"-- {group}")
        print(header)
        for key, c in rep[group].items():
            cu = c.get("curriculum", {})
            print(f"{key:<14} {c['n']:>2}  "
                  f"{_fmt(c['baseline_accuracy'], 2)}  "
                  f"{_fmt(c['after_acquisition_accuracy'], 2)}   "
                  f"{_fmt(c['gated_accuracy'], 2)}   "
                  f"{_fmt(c['abstain_rate'], 2)}  "
                  f"{_fmt(c['gap_fire_rate'], 2)}  "
                  f"{_fmt(c['gap_fire_rate_when_blocked'], 2):>8}  "
                  f"{_fmt(c['gate_saved_a_wrong_answer'], 2)}   "
                  f"{_fmt(c['gate_withheld_a_right_answer'], 2)}  "
                  f"{_fmt(cu.get('node_recall'), 2)}  "
                  f"{_fmt(cu.get('edge_recall'), 2)}  "
                  f"{_fmt(cu.get('order_valid'), 2)}  "
                  f"{c['card_chars']:.0f}/{c['raw_chars']:.0f}")
    print("blockages:", json.dumps(rep.get("blockage_counts", {})))
    for key, c in rep.get("by_level_and_phrasing", {}).items():
        r = c.get("retrieval", {})
        if not r:
            continue
        print(f"retrieval {key:<12} "
              f"naive top1={_fmt(r['naive']['top1_required'], 2)} "
              f"bulk={_fmt(r['naive']['bulk_hit_rate'], 2)} | "
              f"structural top1={_fmt(r['structural']['top1_required'], 2)} "
              f"bulk={_fmt(r['structural']['bulk_hit_rate'], 2)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    for path in args.files:
        with open(path) as fh:
            data = json.load(fh)
        if "loop" in data:
            print(f"\n########## {path}")
            print("proofs:", json.dumps(data.get("proofs", {})))
            rt = data.get("rule_test")
            if rt:
                print("rule test (right pages / other chapter / blank):")
                for k, v in rt.items():
                    print(f"  {k:<14} n={v['n']:>3} "
                          f"textbook={_fmt(v['textbook'], 3)} "
                          f"wrong_chapter={_fmt(v['wrong_chapter'], 3)} "
                          f"blank={_fmt(v['blank'], 3)}")
            cal = data.get("gap_calibration")
            if cal:
                print("gap calibration (fires when blocked, quiet when not):")
                for k, v in sorted(cal.items()):
                    print(f"  {k:<14} n={v['n']:>3} blocked={v['n_blocked']:>3} "
                          f"recall_on_blocked={_fmt(v['recall_on_blocked'], 2)} "
                          f"free={v['n_free']:>3} "
                          f"false_alarm={_fmt(v['false_alarm_when_free'], 2)}")
            print_report(data["loop"], path)
        elif "per_seed" in data:
            print(f"\n########## {path}")
            print_report(data["pooled_across_seeds_only"],
                         f"{path} (across seeds)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
