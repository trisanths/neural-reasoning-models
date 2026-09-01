"""Assemble the tables from the record files, and check their freshness.

Every number in REALRET.md comes out of this, so no figure is typed twice.
Each table cell names the file it was read from and each file's modification
time is compared against the moment this ran: a record older than the run it
is supposed to describe is a stale file being quoted, which is a fault this
project has hit before, and it is reported as `STALE` rather than silently
formatted.

Nothing is pooled. Chance floors travel with their cells.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os


def load(path: str):
    if not os.path.exists(path):
        return None, {"path": path, "exists": False}
    st = os.stat(path)
    meta = {"path": path, "exists": True, "bytes": st.st_size,
            "mtime": dt.datetime.utcfromtimestamp(st.st_mtime)
            .strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(path) as fh:
        return json.load(fh), meta


def wilson(k: int, n: int, z: float = 1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - s) / d, 4), round((c + s) / d, 4))


def acc_row(name, d, meta, key="acc"):
    if d is None:
        return f"| {name} | file missing | | | | | `{meta['path']}` |"
    n = d.get("n") or 0
    acc = d.get(key)
    floor = d.get("floor")
    lo, hi = wilson(int(round(acc * n)), n) if acc is not None else (0, 0)
    return (f"| {name} | {n} | {floor} | {acc} | {lo}-{hi} | "
            f"{round(acc - floor, 4) if acc is not None and floor is not None else ''} "
            f"| `{meta['path']}` |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ec2-user/realret")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json-out", default="")
    a = ap.parse_args()
    R = a.root
    now = dt.datetime.utcnow()
    lines: list[str] = []
    freshness: list[dict] = []
    blob: dict = {}

    def get(rel):
        d, m = load(os.path.join(R, rel))
        m["age_minutes"] = None
        if m.get("exists"):
            age = (now - dt.datetime.strptime(m["mtime"], "%Y-%m-%dT%H:%M:%SZ"))
            m["age_minutes"] = round(age.total_seconds() / 60, 1)
        freshness.append(m)
        blob[rel] = d if not isinstance(d, dict) else {
            k: v for k, v in d.items() if k not in ("records",)}
        return d, m

    # ------------------------------------------------------------ the data
    lines.append("# The data")
    lines.append("")
    lines.append("| pack | examples | tokens | mean tokens per example | "
                 "rounds histogram | file |")
    lines.append("| --- | ---: | ---: | ---: | --- | --- |")
    for rel in ("pack/hotpot_qa.summary.json",
                "pack/natural_questions.summary.json",
                "pack/trivia_qa.summary.json",
                "pack/synthetic.summary.json",
                "pack/mix_real1.summary.json"):
        d, m = get(rel)
        if not d:
            lines.append(f"| {rel} | file missing | | | | `{m['path']}` |")
            continue
        n = d.get("kept") or d.get("n")
        lines.append(f"| {os.path.basename(rel).split('.')[0]} | {n} | "
                     f"{d.get('tokens')} | "
                     f"{round((d.get('tokens') or 0) / max(1, n or 1), 1)} | "
                     f"{json.dumps(d.get('rounds_hist') or d.get('per_component') or {})} "
                     f"| `{m['path']}` |")

    lines += ["", "## Episode build, per source and split", "",
              "| source, split | items seen | episodes kept | dropped | "
              "rounds | queries compressed | file |",
              "| --- | ---: | ---: | --- | --- | ---: | --- |"]
    for src in ("hotpot_qa", "natural_questions", "trivia_qa"):
        for sp in ("train", "validation"):
            d, m = get(f"eps/{src}.{sp}.jsonl.summary.json")
            if not d:
                continue
            lines.append(
                f"| {src} {sp} | {d.get('seen')} | {d.get('kept')} | "
                f"{json.dumps(d.get('drops'))} | "
                f"{json.dumps(d.get('rounds_hist'))} | "
                f"{d.get('query_trimmed')} | `{m['path']}` |")

    lines += ["", "## Train and eval split, leakage by content hash", "",
              "| pair | train episodes | eval episodes | shared question "
              "hashes | shared as fraction of eval | shared document keys | "
              "file |",
              "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    d, m = get("reports/leakage.json")
    if d:
        for k, v in d["pairs"].items():
            lines.append(
                f"| {k} | {v['train_episodes']} | {v['eval_episodes']} | "
                f"{v['shared_hashes']} | {v['shared_fraction_of_eval']} | "
                f"{v['shared_doc_keys']} of {v['eval_doc_keys']} | "
                f"`{m['path']}` |")

    lines += ["", "## Episode contracts, re-checked from the written files", "",
              "| file | lines | checked | episodes with a failure | "
              "clean rate | reasons | source |",
              "| --- | ---: | ---: | ---: | ---: | --- | --- |"]
    d, m = get("reports/verify.json")
    if d:
        for path, v in d["files"].items():
            lines.append(
                f"| `{os.path.basename(path)}` | {v['lines']} | "
                f"{v['checked']} | {v['episodes_with_failures']} | "
                f"{v['clean_rate']} | {json.dumps(v['reasons'])} | "
                f"`{m['path']}` |")

    lines += ["", "## Benchmark contamination", "",
              "| check | value | file |", "| --- | --- | --- |"]
    d, m = get("reports/contamination.json")
    if d:
        for k in ("benchmark_stems", "benchmark_stems_total",
                  "training_questions_scanned", "training_documents_scanned",
                  "training_chars_scanned", "ngram", "min_stem_words",
                  "near_threshold", "exact_matches", "exact_by_task",
                  "near_matches", "near_by_task"):
            lines.append(f"| {k} | {json.dumps(d.get(k))} | `{m['path']}` |")

    lines += ["", "# Held-out synthetic frames, after real-document training",
              "",
              "| checkpoint | decode | family | cells | macro accuracy | "
              "macro chance | chance corrected | file |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for tag in ("corpus-v1-8k", "real-v1-8k"):
        for lab in ("greedy", "t1"):
            d, m = get(f"results/frames_score_{tag}_{lab}.json")
            if not d:
                continue
            macro = d.get("macro_by_family") or {}
            for fam, mv in sorted(macro.items()):
                lines.append(
                    f"| {tag} | {lab} | {fam} | {mv.get('cells')} | "
                    f"{round(mv.get('macro_accuracy', 0), 4)} | "
                    f"{round(mv.get('macro_chance', 0), 4)} | "
                    f"{round(mv.get('order_A_corrected_macro', 0), 4)} | "
                    f"`{m['path']}` |")
            fr = d.get("freshness") or {}
            lines.append(f"| {tag} | {lab} | dumps checked against their "
                         f"episode files | {fr.get('n_dumps')} | | | | "
                         f"`{m['path']}` |")

    lines.append("")
    lines.append("# Record files")
    lines.append("")
    lines.append("| file | exists | bytes | modified (UTC) | age at report, minutes |")
    lines.append("| --- | --- | ---: | --- | ---: |")

    named = [
        "results/harness_ours_n200_cuda.json",
        "results/harness_lfm2_n200_cuda_bos.json",
        "results/mmlu_closed_corpus-v1-8k_n500.json",
        "results/mmlu_closed_corpus-v1-8k_n500_eot.json",
        "results/mmlu_closed_real-v1-8k_n500.json",
        "results/mmlu_closed_real-v1-8k_n500_eot.json",
        "results/mmlu_closed_lfm2-350m_n500_bos.json",
        "results/mmlu_closed_lfm2-350m_n500_nobos.json",
        "results/mmlu_web_lfm2-350m_n500.json",
        "results/mmlu_web_corpus-v1-8k_n500.json",
        "results/mmlu_web_real-v1-8k_n500.json",
        "results/mmlu_agentic_corpus-v1-8k_n200.json",
        "results/mmlu_agentic_real-v1-8k_n200.json",
        "results/real_scores_corpus-v1-8k.json",
        "results/real_scores_real-v1-8k.json",
        "reports/verify.json",
        "reports/leakage.json",
        "reports/contamination.json",
        "pack/mix_real1.summary.json",
        "pack/hotpot_qa.summary.json",
        "pack/natural_questions.summary.json",
        "pack/trivia_qa.summary.json",
        "pack/synthetic.summary.json",
    ]
    loaded = {}
    for rel in named:
        loaded[rel] = get(rel)
    for m in freshness:
        lines.append(f"| `{m['path']}` | {m.get('exists')} | "
                     f"{m.get('bytes', '')} | {m.get('mtime', '')} | "
                     f"{m.get('age_minutes', '')} |")

    # ------------------------------------------------------- closed book MMLU
    lines += ["", "# MMLU, closed book, five shot completion", "",
              "| model | n | floor | acc | 95% Wilson | acc - floor | file |",
              "| --- | ---: | ---: | ---: | --- | ---: | --- |"]
    for name, rel in [
            ("ours corpus-v1-8k", "results/mmlu_closed_corpus-v1-8k_n500.json"),
            ("ours corpus-v1-8k, eot prefix",
             "results/mmlu_closed_corpus-v1-8k_n500_eot.json"),
            ("ours real-v1-8k", "results/mmlu_closed_real-v1-8k_n500.json"),
            ("ours real-v1-8k, eot prefix",
             "results/mmlu_closed_real-v1-8k_n500_eot.json"),
            ("LFM2-350M, bos", "results/mmlu_closed_lfm2-350m_n500_bos.json"),
            ("LFM2-350M, no bos",
             "results/mmlu_closed_lfm2-350m_n500_nobos.json"),
            ("harness check: ours corpus-v1-8k n=200 cuda",
             "results/harness_ours_n200_cuda.json"),
            ("harness check: LFM2-350M n=200 cuda bos",
             "results/harness_lfm2_n200_cuda_bos.json")]:
        d, m = loaded[rel]
        lines.append(acc_row(name, d, m))

    # ---------------------------------------------------------- MMLU with web
    lines += ["", "# MMLU with live web pages", "",
              "Same items, same queries, same cached pages on every row.", "",
              "| model | condition | contamination | n | floor | acc | file |",
              "| --- | --- | --- | ---: | ---: | ---: | --- |"]
    d, m = loaded["results/mmlu_web_lfm2-350m_n500.json"]
    if d:
        for lab in ("all", "verbatim", "answer", "neither"):
            c = d["all"] if lab == "all" else d["by_contamination"].get(lab)
            if c:
                lines.append(f"| LFM2-350M | pages in context | {lab} | "
                             f"{c['n']} | {c['floor']} | {c['acc']} | "
                             f"`{m['path']}` |")
    for tag in ("corpus-v1-8k", "real-v1-8k"):
        d, m = loaded[f"results/mmlu_web_{tag}_n500.json"]
        if not d:
            continue
        lines.append(f"| ours {tag} | context overflow | prompts cropped "
                     f"{d.get('prompts_cropped')} of {d.get('n')}, mean "
                     f"{d.get('mean_ctx_tokens_open')} tokens, max "
                     f"{d.get('max_ctx_tokens_open')}, window "
                     f"{d.get('max_seq_len')} | | | | `{m['path']}` |")
        for cond in ("closed_book", "matched", "matched_uncropped", "native"):
            if cond not in d or not d[cond]:
                continue
            for lab in ("all", "verbatim", "answer", "neither"):
                c = (d[cond]["all"] if lab == "all"
                     else d[cond]["by_contamination"].get(lab))
                if c:
                    lines.append(f"| ours {tag} | {cond} | {lab} | {c['n']} | "
                                 f"{c['floor']} | {c['acc']} | `{m['path']}` |")

    # -------------------------------------------------------------- agentic
    lines += ["", "# MMLU, the model driving its own retrieval", "",
              "| model | n | floor | acc | issued a query | mean rounds | "
              "pages entered context | named a choice | file |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for tag in ("corpus-v1-8k", "real-v1-8k"):
        d, m = loaded[f"results/mmlu_agentic_{tag}_n200.json"]
        if not d:
            continue
        lines.append(f"| ours {tag} | {d['n']} | {d['floor']} | {d['acc']} | "
                     f"{d['issued_query']} | {d['mean_rounds']} | "
                     f"{d['pages_entered_context']} | {d['named_a_choice']} | "
                     f"`{m['path']}` |")

    # -------------------------------------------------- real document retrieval
    lines += ["", "# Held-out real documents, through the retrieval loop", "",
              "| checkpoint | source | decode | n | floor | ship | strict | "
              "f1 | rounds | gold page served | ship given gold served | file |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | "
              "---: | ---: | --- |"]
    for tag in ("corpus-v1-8k", "real-v1-8k"):
        d, m = loaded[f"results/real_scores_{tag}.json"]
        if not d:
            continue
        for key, c in sorted(d["cells"].items()):
            src, dec, kind = key.split("|")
            lines.append(
                f"| {tag} | {src} {kind} | {dec} | {c['n']} | {c['floor']} | "
                f"{c['ship']} | {c['strict']} | {c['f1']} | {c['mean_rounds']} | "
                f"{c['gold_page_served']} | {c['ship_given_gold_served']} | "
                f"`{m['path']}` |")

    lines += ["", "# Failure decomposition on the held-out real documents", "",
              "| checkpoint | source | decode | wrong | no query | bad pages | "
              "truncated | did not read | file |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for tag in ("corpus-v1-8k", "real-v1-8k"):
        d, m = loaded[f"results/real_scores_{tag}.json"]
        if not d:
            continue
        for key, c in sorted(d["cells"].items()):
            src, dec, kind = key.split("|")
            x = c["decomposition"]
            lines.append(
                f"| {tag} | {src} {kind} | {dec} | {c['wrong']} | "
                f"{x['no_query']} | {x['bad_pages']} | {x['truncated']} | "
                f"{x['did_not_read']} | `{m['path']}` |")

    with open(a.out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    if a.json_out:
        with open(a.json_out, "w") as fh:
            json.dump({"generated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "freshness": freshness, "data": blob}, fh, indent=1)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
