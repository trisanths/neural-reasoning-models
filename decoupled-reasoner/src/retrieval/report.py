"""Emit the RANKING.md tables from the persisted artifacts, never by hand.

Every table this prints names the file it came from. Run it after any of the
drivers and paste the output; nothing in the report should be a number typed
from a terminal.
"""

from __future__ import annotations

import argparse
import json
import os


def load(path):
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def order_table(res: dict) -> str:
    if not res:
        return "_no order sweep artifact_\n"
    by = {}
    orders = []
    depths = []
    for c in res["cells"]:
        by[(c["order"], c["depth"])] = c
        if c["order"] not in orders:
            orders.append(c["order"])
        if c["depth"] not in depths:
            depths.append(c["depth"])
    depths.sort()
    out = ["| page order | " + " | ".join(f"d{d}" for d in depths) + " |",
           "|---|" + "---|" * len(depths)]
    for o in orders:
        row = []
        for d in depths:
            c = by.get((o, d))
            row.append("" if c is None
                       else f"{c['pass_at_1']:.4f} / {c['pass_at_1_forced']:.4f}")
        out.append(f"| {o} | " + " | ".join(row) + " |")
    out.append("")
    out.append("Served final table, mean rounds, hedge rate.")
    out.append("")
    out.append("| page order | depth | served final table | mean rounds | "
               "hedge | n |")
    out.append("|---|---|---|---|---|---|")
    for o in orders:
        for d in depths:
            c = by.get((o, d))
            if c is None:
                continue
            out.append(f"| {o} | {d} | {c['served_final_table']:.4f} | "
                       f"{c['mean_rounds']:.3f} | {c['hedge_rate']:.4f} | "
                       f"{c['n_rollouts']} |")
    return "\n".join(out) + "\n"


def rung_table(before: dict, after: dict) -> str:
    if not before:
        return "_no rung artifact_\n"
    out = ["| rung | tie break | chain pass@1 | 95 pct | forced | pass@4 | "
           "hedge | n |", "|---|---|---|---|---|---|---|---|"]
    for res, tag in ((before, "first"), (after, "content")):
        if not res:
            continue
        for c in res["cells"]:
            hedge = max(s["hedge_rate"] for s in c["per_step"])
            ci = c["chain_pass_at_1_ci95"]
            out.append(
                f"| {c['rung'].upper()} | {tag} | {c['chain_pass_at_1']:.4f} | "
                f"{ci[0]:.4f} to {ci[1]:.4f} | "
                f"{c['chain_pass_at_1_forced']:.4f} | "
                f"{c['chain_pass_at_k']:.3f} | {hedge:.4f} | "
                f"{c['n_chains']} |")
    out.append("")
    out.append("Per step, served needed page and the ranking behind it.")
    out.append("")
    out.append("| rung | tie break | step | acc | forced | served page | "
               "acc given page | miss on tie | miss on score | n |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for res, tag in ((before, "first"), (after, "content")):
        if not res:
            continue
        for c in res["cells"]:
            for s in c["per_step"]:
                fr = s["first_round_ranking"]
                out.append(
                    f"| {c['rung'].upper()} | {tag} | {s['step']} | "
                    f"{s['step_accuracy']:.4f} | "
                    f"{s['step_accuracy_forced']:.4f} | "
                    f"{s['served_gold_page']:.4f} | "
                    f"{s['acc_given_gold_page']:.3f} | "
                    f"{fr['tie_loss']:.3f} | {fr['score_loss']:.3f} | "
                    f"{s['n']} |")
    return "\n".join(out) + "\n"


def skill_table(res: dict) -> str:
    if not res:
        return "_no skillacq artifact_\n"
    out = ["| family | episodes | problems | hit@1 problem query | 95 pct | "
           "miss on tie | miss on score | mean rank | hit@1 shared query | "
           "miss on tie, shared |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for c in res["families"]:
        p, s = c["problem_query"], c["shared_only_query"]
        ci = c["problem_hit_ci95"]
        out.append(
            f"| {c['family']} | {c['n_episodes']} | {c['n_problems']} | "
            f"{p['hit_at_1']:.3f} | {ci[0]:.3f} to {ci[1]:.3f} | "
            f"{p['tie_loss']:.3f} | {p['score_loss']:.3f} | "
            f"{p['mean_gold_rank']:.2f} | {s['hit_at_1']:.3f} | "
            f"{s['tie_loss']:.3f} |")
    return "\n".join(out) + "\n"


def pageset_table(res: dict) -> str:
    if not res:
        return "_no pageset artifact_\n"
    out = ["| episodes file | pages | serves needed page | miss on tie | "
           "miss on score | mean rank | tied at all | position blind |",
           "|---|---|---|---|---|---|---|---|"]
    for path, s in res["files"].items():
        out.append(
            f"| {os.path.basename(path)} | {s['mean_pages']:.0f} | "
            f"{s['hit_at_1']:.3f} | {s['tie_loss']:.3f} | "
            f"{s['score_loss']:.3f} | {s['mean_gold_rank']:.2f} | "
            f"{s['tied_at_all']:.3f} | "
            f"{s['expected_served_position_blind']:.3f} |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/retrieval")
    args = ap.parse_args()
    d = args.dir
    print("## R0 with the page order permuted\n")
    print(f"Artifact `{d}/r0_order.json`. Lenient / forced.\n")
    print(order_table(load(f"{d}/r0_order.json")))
    print("\n## The rescue rungs, before and after the tie break\n")
    for depth in (2, 3):
        b = load(f"{d}/d{depth}_before.json")
        a = load(f"{d}/d{depth}_after.json")
        if not b:
            continue
        print(f"Depth {depth}. Artifacts `{d}/d{depth}_before.json` and "
              f"`{d}/d{depth}_after.json`.\n")
        print(rung_table(b, a))
        print()
    print("\n## skillacq families\n")
    print(f"Artifact `{d}/skillrank_before.json`.\n")
    print(skill_table(load(f"{d}/skillrank_before.json")))
    print("\n## Page sets under the policy's own queries\n")
    print(f"Artifact `{d}/pagesets.json`.\n")
    print(pageset_table(load(f"{d}/pagesets.json")))


if __name__ == "__main__":
    main()
