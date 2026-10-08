"""Eval report assembly: one JSON file plus a short markdown summary."""

import json
from pathlib import Path


def build_report(heldout: dict, probes: dict, meta: dict) -> dict:
    return {"meta": meta, "heldout_worlds": heldout, "knowledge_probes": probes}


def render_markdown(report: dict) -> str:
    meta = report["meta"]
    heldout = report["heldout_worlds"]
    probes = report["knowledge_probes"]
    lines = [
        "# Eval report",
        "",
        f"Checkpoint: {meta.get('checkpoint', 'unknown')} "
        f"(step {meta.get('step', '?')})",
        f"Held out seed: {meta.get('heldout_seed', '?')}, "
        f"episodes: {heldout['n_episodes']}, "
        f"questions: {heldout['n_questions']}",
        "",
        "## Held out worlds",
        "",
        f"Accuracy {heldout['accuracy']:.4f} against a chance rate of "
        f"{heldout['chance']:.4f}.",
        "",
        "| domain | n | accuracy |",
        "|---|---|---|",
    ]
    for domain in sorted(heldout["per_domain"]):
        stats = heldout["per_domain"][domain]
        lines.append(f"| {domain} | {stats['n']} | {stats['accuracy']:.4f} |")
    lines += [
        "",
        "| question type | n | accuracy |",
        "|---|---|---|",
    ]
    for qtype in sorted(heldout["per_type"]):
        stats = heldout["per_type"][qtype]
        lines.append(f"| {qtype} | {stats['n']} | {stats['accuracy']:.4f} |")
    lines += [
        "",
        "## Knowledge probes",
        "",
        f"Accuracy {probes['accuracy']:.4f} on {probes['n']} probes, "
        f"chance {probes['chance']:.2f}, leakage threshold "
        f"{probes['leakage_threshold']:.4f}.",
        "",
        "Leakage flag: " + ("RAISED, investigate before using this run."
                            if probes["leakage_flag"] else
                            "clear, the score is consistent with chance."),
        "",
    ]
    return "\n".join(lines)


def write_report(report: dict, out_dir: str) -> tuple:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "eval_report.json"
    md_path = out / "eval_report.md"
    with open(json_path, "w") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    md_path.write_text(render_markdown(report))
    return json_path, md_path
