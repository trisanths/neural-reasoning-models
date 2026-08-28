"""Rendering the seven-way profile and the rescue matrix.

Nothing here pools. Each faculty gets its own block with its own sample
size, its own chance rate and its own interval, because the whole reason
the suite exists is to be able to say which faculty broke.
"""

from __future__ import annotations

import json
from pathlib import Path


def _pct(stat) -> str:
    if not stat:
        return "n/a"
    return (f"{stat['acc']:.3f} [{stat['ci_lo']:.3f}, {stat['ci_hi']:.3f}] "
            f"n={stat['n']}")


def _adj(stat) -> str:
    if not stat:
        return "n/a"
    flag = "" if stat.get("above_chance") else "  (at chance)"
    return f"{stat['adjusted']:+.3f} vs chance {stat['chance']:.3f}{flag}"


def _line(label, stat) -> str:
    return f"| {label} | {_pct(stat)} | {_adj(stat)} |"


def _parse_rates(report: dict) -> dict:
    out = {}
    for name, rep in report.items():
        if not isinstance(rep, dict):
            continue
        pr = rep.get("parse_rate")
        if isinstance(pr, dict):
            out[name] = pr["acc"]
        else:
            for sub in rep.values():
                if isinstance(sub, dict) and isinstance(
                        sub.get("parse_rate"), dict):
                    out[name] = sub["parse_rate"]["acc"]
                    break
    return out


def _expressibility_note(report: dict) -> str:
    """Say plainly when the profile is bounded by expression, not faculty.

    Graders here read a formatless reply generously, so a low score is not
    automatically a format failure. But a model that writes the requested
    fields on almost no item is a model whose faculties this instrument
    cannot see, and that has to be stated in the report rather than left
    for a reader to infer from a table of zeros.
    """
    rates = _parse_rates(report)
    if not rates:
        return ""
    worst = sorted(rates.items(), key=lambda kv: kv[1])
    mean = sum(rates.values()) / len(rates)
    if mean >= 0.5:
        return (f"Requested answer format produced on {mean:.0%} of items on "
                f"average. Scores below read as faculty.")
    low = ", ".join(f"{k} {v:.0%}" for k, v in worst[:4])
    return (
        f"Format warning. The requested answer format was produced on only "
        f"{mean:.0%} of items on average ({low}). Every grader here falls "
        f"back to reading the whole reply, and binary fields are read "
        f"through a synonym list, so these numbers are not pure format "
        f"failures. They are still an upper bound on what this instrument "
        f"can see of this model: a faculty the model cannot express is a "
        f"faculty this suite cannot measure, and the profile below should "
        f"be read as a floor rather than an estimate.")


def render_markdown(report: dict) -> str:
    meta = report.get("meta", {})
    out = [
        "# Capability primitive profile",
        "",
        f"Mode: {meta.get('mode', '?')}. "
        f"{meta.get('n_per_primitive', '?')} items per primitive, seed "
        f"{meta.get('seed', '?')}, {meta.get('n_items', '?')} model calls, "
        f"{meta.get('seconds', '?')}s.",
        "",
        "Never pooled. Every faculty carries its own sample size, its own",
        "chance rate and its own Wilson interval.",
        "",
        _expressibility_note(report),
        "",
        "## Headline, one line per faculty",
        "",
        "| faculty | headline | reading |",
        "|---|---|---|",
    ]
    readings = {
        "intent": "mean chance-adjusted score over the five extracted fields",
        "gap": "chance-adjusted blocked against solvable detection",
        "acquisition": "query recall at 1 minus the verbatim-copy baseline",
        "abstraction": "transfer accuracy minus the copy baseline, per structure",
        "composition": "greatest depth still above chance, per kind",
        "memory": "mean chance-adjusted score over retain-far, interfere, update",
        "verification": "chance-adjusted trap detection",
    }
    for name, reading in readings.items():
        rep = report.get(name)
        if not rep:
            continue
        h = rep.get("headline")
        h = (", ".join(f"{k}={v}" for k, v in h.items())
             if isinstance(h, dict) else f"{h:+.3f}")
        out.append(f"| {name} | {h} | {reading} |")

    if "intent" in report:
        r = report["intent"]
        out += ["", "## Intent understanding", "",
                f"n={r['n']}, parse rate {r['parse_rate']['acc']:.3f}.", "",
                "| field | accuracy | adjusted |", "|---|---|---|"]
        for k in ("goal", "conflict", "success", "constraints_exact"):
            out.append(_line(k, r["fields"].get(k)))
        for k in ("constraints", "uncertain"):
            s = r["fields"].get(k)
            if s:
                out.append(f"| {k} (mean overlap) | {s['mean']:.3f} "
                           f"[{s['ci_lo']:.3f}, {s['ci_hi']:.3f}] n={s['n']} | |")
        out += ["", "Conflict detection split by whether the request really",
                "contradicts itself, so a model that always reports one is",
                "visible:", "",
                "| arm | accuracy | adjusted |", "|---|---|---|"]
        for var, st in sorted(r.get("per_variant", {}).items()):
            out.append(_line(var, st))

    if "gap" in report:
        r = report["gap"]
        out += ["", "## Missing-capability recognition", "",
                "| measure | accuracy | adjusted |", "|---|---|---|",
                _line("detection", r["detection"]),
                _line("gap type", r["gap_type"])]
        if r.get("step_localisation"):
            out.append(_line("step localisation", r["step_localisation"]))
        out += [_line("false alarm on solvable", r["false_alarm"]),
                _line("miss on blocked", r["miss"]),
                _line("named a value it could not know", r["leak_named"]),
                "",
                f"Parse rate {r['parse_rate']['acc']:.3f}."]

    if "acquisition" in report:
        r = report["acquisition"]
        out += ["", "## Information acquisition", "",
                "The score reads the query, not an answer.", "",
                "| measure | value | adjusted |", "|---|---|---|"]
        for variant in ("direct", "recursive"):
            v = r.get(variant)
            if not v:
                continue
            out += [_line(f"{variant}: source selection", v["source_selection"]),
                    _line(f"{variant}: recall@1", v["recall_at1"]),
                    _line(f"{variant}: recall@3", v["recall_at3"]),
                    _line(f"{variant}: copy baseline@1", v["copy_baseline_at1"]),
                    _line(f"{variant}: empty query", v["empty_query"])]
            if v.get("hop_recall_at1"):
                out.append(_line(f"{variant}: second-hop recall@1 (reads the "
                                 f"served page, contaminated)",
                                 v["hop_recall_at1"]))

    if "abstraction" in report:
        r = report["abstraction"]
        out += ["", "## Abstraction construction", "",
                f"Transfer cost, same surface minus transfer: "
                f"{r['transfer_cost']:+.3f}.", "",
                "| condition | accuracy | copy baseline | beats copy |",
                "|---|---|---|---|"]
        for c in ("same_surface", "transfer"):
            v = r.get(c)
            if v:
                out.append(f"| {c} | {_pct(v['accuracy'])} | "
                           f"{_pct(v['copy_baseline'])} | "
                           f"{'yes' if v['beats_copy'] else 'no'} |")
        out += ["", "| condition and rule | accuracy | copy | margin |",
                "|---|---|---|---|"]
        for c in ("same_surface", "transfer"):
            for st, v in sorted(r.get(c, {}).get("per_structure", {}).items()):
                out.append(f"| {c}/{st} | {_pct(v['accuracy'])} | "
                           f"{_pct(v['copy_baseline'])} | {v['delta']:+.3f} |")

    if "composition" in report:
        r = report["composition"]
        out += ["", "## Composition depth, three curves, never pooled", ""]
        for kind in ("sequential", "relational", "novel"):
            v = r.get(kind)
            if not v:
                continue
            out += [f"### {kind}", "",
                    f"Depth still above chance: k*={v['k_star']}"
                    + (f", step-conditioned k*={v['k_star_step_clean']}"
                       if "k_star_step_clean" in v else "") + ".", ""]
            if v.get("step_probe_accuracy"):
                out.append(
                    f"Per-step probe accuracy {_pct(v['step_probe_accuracy'])}; "
                    f"items whose every step was answered correctly on its own: "
                    f"{v['items_with_all_steps_correct']['acc']:.3f}.")
                out.append("")
            out += ["| k | accuracy | adjusted | step-clean accuracy |",
                    "|---|---|---|---|"]
            for k in sorted(v["curve"], key=int):
                s = v["curve"][k]
                sc = v.get("curve_step_clean", {}).get(k)
                out.append(f"| {k} | {_pct(s)} | {_adj(s)} | "
                           f"{_pct(sc) if sc else 'n/a'} |")
            out.append("")

    if "memory" in report:
        r = report["memory"]
        out += ["", "## Temporary knowledge", "",
                f"Distance cost, near minus far: "
                f"{r['distance_cost']:+.3f}." if r.get("distance_cost") is not None
                else "", "",
                "| arm | accuracy | adjusted |", "|---|---|---|"]
        for var, st in sorted(r["per_variant"].items()):
            out.append(_line(var, st))
        if r.get("intrusion_rate"):
            out.append(_line("intrusion, answered the interfering value",
                             r["intrusion_rate"]))
        if r.get("leak_rate"):
            out.append(_line("leak, answered the voided episode's value",
                             r["leak_rate"]))
        out += ["", f"Median prompt length {r['median_prompt_words']} words."]

    if "verification" in report:
        r = report["verification"]
        out += ["", "## Verification and action", "",
                "Detection and correction are scored apart.", "",
                "| measure | value | adjusted |", "|---|---|---|",
                _line("detection", r["detection"]),
                _line("correction, all items", r["correction"])]
        if r.get("correction_given_detection"):
            out.append(_line("correction given detection",
                             r["correction_given_detection"]))
        out += [_line("trap recall", r["trap_recall"]),
                _line("false alarm on controls", r["false_alarm"]),
                _line("overcorrected a correct candidate", r["overcorrection"])]
        out += ["", "| trap shape | detection | correction |", "|---|---|---|"]
        for sh, v in sorted(r["per_shape"].items()):
            out.append(f"| {sh} | {_pct(v['detection'])} | "
                       f"{_pct(v['correction'])} |")

    if report.get("forced_choice"):
        out += ["", "## Forced choice, the same items scored by preference", "",
                "Producing an answer and preferring the right one are",
                "different abilities. This channel scores the option texts by",
                "likelihood, the way the held-out suite scores multiple",
                "choice, so a model that cannot write the requested format is",
                "still asked the same question. It is reported beside the",
                "generation channel and never instead of it.", "",
                "| faculty | field | accuracy | adjusted |",
                "|---|---|---|---|"]
        for prim in sorted(report["forced_choice"]):
            for field, stat in sorted(report["forced_choice"][prim].items()):
                out.append(f"| {prim} | {field} | {_pct(stat)} | {_adj(stat)} |")

    if "rescue_matrix" in report:
        r = report["rescue_matrix"]
        out += ["", "## Causal rescue matrix", "",
                f"{r['n_episodes']} integrated episodes, each rendered under "
                f"every intervention, so every lift is paired.",
                f"No oracle: {_pct(r['baseline'])}. Every oracle: "
                f"{_pct(r['ceiling'])}. Chance {r['chance']:.3f}.", "",
                "gained and lost count the episodes the oracle flipped in "
                "each direction; rescue share is gained over the two, and an "
                "interval clearing one half is a real rescue.", "",
                "| intervention | accuracy | lift | gained | lost | "
                "rescue share | rescued |", "|---|---|---|---|---|---|---|"]
        for cond in ["none"] + list(r["ranking"]) + ["oracle_all"]:
            row = r["rows"].get(cond)
            if not row:
                continue
            lift = row.get("lift")
            share = row.get("rescue_share")
            ci = row.get("rescue_ci")
            out.append(
                f"| {cond} | {_pct(row['accuracy'])} | "
                f"{f'{lift:+.3f}' if lift is not None else '-'} | "
                f"{row.get('gained', '-')} | {row.get('lost', '-')} | "
                + (f"{share:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"
                   if share is not None and ci else "-")
                + f" | {'yes' if row.get('rescued') else 'no'} |")
        if r.get("largest_rescue"):
            out += ["", f"Largest single rescue: {r['largest_rescue']}."]

    out.append("")
    return "\n".join(x for x in out if x is not None)


def write_report(bundle: dict, out_dir: str, stem: str = "primitives") -> tuple:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    jp = out / f"{stem}.json"
    mp = out / f"{stem}.md"
    rp = out / f"{stem}_records.jsonl"
    with open(jp, "w") as fh:
        json.dump(bundle["report"], fh, indent=2, default=str)
        fh.write("\n")
    mp.write_text(render_markdown(bundle["report"]))
    with open(rp, "w") as fh:
        for rec in bundle.get("records", []):
            fh.write(json.dumps(rec, default=str) + "\n")
    return jp, mp, rp
