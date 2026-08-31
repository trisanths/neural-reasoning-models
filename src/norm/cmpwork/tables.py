"""Every markdown table in COMPARE.md, generated from the summary files.

No number in the document is typed by hand. Each function reads one report
JSON and writes one fragment under results/norm/compare/tables/.
"""
from __future__ import annotations

import json
import os
import statistics as st

ROOT = "results/norm/compare"
OUT = f"{ROOT}/tables"
SPLITS = ("train", "qframe", "lexicon", "mode", "mixed")
SHAPES = ("lookup", "lookup_general", "classify", "inverse", "compose",
          "iterate", "pair", "priority", "exclusion", "lookup_then_band",
          "band_then_lookup", "precedence")


def load(name):
    p = f"{ROOT}/{name}"
    return json.load(open(p)) if os.path.exists(p) else None


def w(name, lines):
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{name}", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote", f"{OUT}/{name}", len(lines), "lines")


def cellval(row, sysname, field="strict"):
    if sysname not in row:
        return "-"
    return f"{row[sysname][field]:.4f}"


def t_main(rep, cols, name, field="strict"):
    head = ["| split | shape | n | floor | " + " | ".join(c[1] for c in cols) + " |",
            "|---|---|---|---|" + "---|" * len(cols)]
    body = []
    for sp in SPLITS:
        for sh in SHAPES:
            k = f"{sp}|{sh}"
            row = rep["cells"].get(k)
            if not row:
                continue
            anysys = next(v for s, v in row.items() if s != "_distance")
            body.append(f"| `{sp}` | `{sh}` | {anysys['n']} | "
                        f"{anysys['floor']:.3f} | "
                        + " | ".join(cellval(row, c[0], field) for c in cols) + " |")
    w(name, head + body)


def t_range(rep, cols, name):
    head = ["| split | shape distance | lexical distance | cells | "
            + " | ".join(c[1] for c in cols) + " |",
            "|---|---|---|---|" + "---|" * len(cols)]
    body = []
    for sp in SPLITS:
        keys = [k for k in rep["cells"] if k.startswith(sp + "|")]
        if not keys:
            continue
        d = rep["cells"][keys[0]].get("_distance", {})
        vals = []
        for c, _ in cols:
            xs = [rep["cells"][k][c]["strict"] for k in keys
                  if c in rep["cells"][k]]
            vals.append(f"{min(xs):.3f} / {st.median(xs):.3f} / {max(xs):.3f}"
                        if xs else "-")
        body.append(f"| `{sp}` | {d.get('shape_median', 0):.3f} | "
                    f"{d.get('lex_median', 0):.3f} | {len(keys)} | "
                    + " | ".join(vals) + " |")
    w(name, head + body)


def t_depth(rep, cols, name, split="train"):
    head = ["| depth | n | floor | " + " | ".join(c[1] for c in cols) + " | C `l` structure exact |",
            "|---|---|---|" + "---|" * (len(cols) + 1)]
    body = []
    keys = sorted((k for k in rep["cells"] if k.startswith(split + "|")),
                  key=lambda k: int(k.split("|")[1]))
    for k in keys:
        row = rep["cells"][k]
        anysys = next(v for s, v in row.items() if s != "_distance")
        ex = row.get("C_l_greedy", {}).get("structure_exact")
        body.append(f"| {k.split('|')[1]} | {anysys['n']} | {anysys['floor']:.3f} | "
                    + " | ".join(cellval(row, c[0]) for c in cols)
                    + f" | {'-' if ex is None else f'{ex:.4f}'} |")
    w(name, head + body)


def t_transpose(rep, name):
    head = ["| version | split | system | n | follows the page | follows the other reading | names neither | declines |",
            "|---|---|---|---|---|---|---|---|"]
    body = []
    for k in sorted(rep["cells"]):
        ver, sp = k.split("|")
        if sp != "all":
            continue
        for s, r in sorted(rep["cells"][k].items()):
            body.append(f"| {ver} | all | `{s}` | {r['n']} | "
                        f"{r['page_count']} = {r['follows_page']:.4f} | "
                        f"{r['alt_count']} = {r['follows_alt']:.4f} | "
                        f"{r['neither']:.4f} | {r['declined']:.4f} |")
    w(name, head + body)


def t_ladder(rep, name):
    head = ["| checkpoint | grids seen | transposed page followed | original page followed | "
            "structure exact, original | structure exact, transposed | "
            "twelve shape set, median cell | its lowest cell |",
            "|---|---|---|---|---|---|---|---|"]
    body = []

    def kof(e):
        ft = e.get("finetune")
        return -1 if not ft else ft["k"]

    for tag, e in sorted(rep["runs"].items(), key=lambda kv: kof(kv[1])):
        g, o = e["grid_greedy"]["transposed|all"], e["grid_greedy"]["original|all"]
        cells = sorted(v["strict"] for v in e["main_greedy"].values())
        worst = cells[0]
        med = st.median(cells)
        k = kof(e)
        body.append(f"| `{tag}` | {'none, shipped' if k < 0 else k} | "
                    f"{g['page_count']} = {g['follows_page']:.4f} | "
                    f"{o['page_count']} = {o['follows_page']:.4f} | "
                    f"{o['structure_exact']:.4f} | {g['structure_exact']:.4f} | "
                    f"{med:.4f} | {worst:.4f} |")
    w(name, head + body)


def t_ladder_split(rep, name):
    head = ["| checkpoint | grids seen | " + " | ".join(f"`{s}`" for s in SPLITS) + " |",
            "|---|---|" + "---|" * len(SPLITS)]
    body = []

    def kof(e):
        ft = e.get("finetune")
        return -1 if not ft else ft["k"]

    for tag, e in sorted(rep["runs"].items(), key=lambda kv: kof(kv[1])):
        cells = []
        for sp in SPLITS:
            c = e["grid_greedy"].get(f"transposed|{sp}")
            cells.append("-" if not c else f"{c['page_count']}")
        k = kof(e)
        body.append(f"| `{tag}` | {'none, shipped' if k < 0 else k} | "
                    + " | ".join(cells) + " |")
    w(name, head + body)


def t_xmode(name):
    rep = load("xmode.json")
    if not rep:
        return
    head = ["| checkpoint | grids seen | version | n | exact | keys in the untransposed order | malformed | other |",
            "|---|---|---|---|---|---|---|---|"]
    body = []

    def kof(e):
        ft = e.get("finetune")
        return -1 if not ft else ft["k"]

    for tag, e in sorted(rep["runs"].items(), key=lambda kv: (kv[1]["size"], kof(kv[1]))):
        c = e["counts"]
        for ver in ("original", "transposed"):
            n = sum(v for k, v in c.items() if k.startswith(ver + "|"))
            if not n:
                continue
            g = lambda w: c.get(f"{ver}|{w}", 0)
            k = kof(e)
            body.append(f"| `{tag}` | {'none, shipped' if k < 0 else k} | {ver} | {n} | "
                        f"{g('exact')} | {g('key_order_canonical')} | "
                        f"{g('malformed')} | {g('other')} |")
    w(name, head + body)


def t_wdepth(name):
    rep = load("wdepth.json")
    if not rep:
        return
    head = ["| ring width | plan depth | n | floor | C 45.5M forced | C 45.5M structure exact | "
            "B given the frame | the seam can write it | median input tokens |",
            "|---|---|---|---|---|---|---|---|---|"]
    body = []
    for k in sorted(rep["cells"], key=lambda x: (int(x.split("|")[0]), int(x.split("|")[1]))):
        c = rep["cells"][k]
        body.append(f"| {c['width']} | {c['depth']} | {c['n']} | {c['floor']:.3f} | "
                    f"{c['C_strict']:.4f} | {c['C_structure_exact']:.4f} | "
                    f"{c['parser_exact']:.4f} | {c['seam_can_write']:.2f} | "
                    f"{c['median_input_tokens']} |")
    w(name, head + body)


def t_interp(name):
    rep = load("../depth/summary.json")
    if not rep:
        return
    head = ["| plan depth | steps | answer exact | microseconds per step |",
            "|---|---|---|---|"]
    body = []
    for r in rep.get("plan_depth", []):
        body.append(f"| {r['depth']} | {r['steps']} | "
                    f"{'yes' if r['exact'] else 'no'} | {r['us_per_step']:.1f} |")
    if body:
        w(name, head + body)


def t_aheader(name):
    rep = load("header_ablation.json")
    if not rep:
        return
    head = ["| world header domain | n | mean retrieval rounds | forced | names nothing | hedges |",
            "|---|---|---|---|---|---|"]
    body = []
    for k, v in rep.items():
        body.append(f"| `{k}` | {v['n']} | {v['mean_rounds']} | {v['strict_acc']:.4f} | "
                    f"{v['none_rate']:.4f} | {v['hedge_rate']:.4f} |")
    w(name, head + body)


def t_aform(name):
    rep = load("a_diagnostic.json")
    if not rep:
        return
    head = ["| question form | n | rounds, retrieval | forced, retrieval | names nothing, retrieval | "
            "forced, pages in context | forced, pages in context and the answer marker forced |",
            "|---|---|---|---|---|---|---|"]
    body = []
    for qf in sorted(rep):
        c = rep[qf]
        body.append(f"| `{qf}` | {c['retrieval']['n']} | {c['retrieval']['rounds']} | "
                    f"{c['retrieval']['strict']:.4f} | {c['retrieval']['none']:.4f} | "
                    f"{c['in_context']['strict']:.4f} | "
                    f"{c['in_context_forced_a']['strict']:.4f} |")
    w(name, head + body)


def t_distance(name):
    d = load("frame_distance.json")
    if not d:
        return
    head = ["| group | frames | shape distance min / median / max | lexical distance min / median / max |",
            "|---|---|---|---|"]
    from src.norm import ndata
    sp = ndata.split_frames()
    body = []
    for g in SPLITS:
        fs = sorted(sp[g])
        s = [d["frames"][f]["shape_distance"] for f in fs]
        lx = [d["frames"][f]["lex_distance_at_nearest"] for f in fs]
        body.append(f"| `{g}` | {len(fs)} | {min(s):.4f} / {st.median(s):.4f} / {max(s):.4f} | "
                    f"{min(lx):.4f} / {st.median(lx):.4f} / {max(lx):.4f} |")
    w(name, head + body)


def t_bcoverage(name):
    import gzip
    from collections import Counter
    c = Counter()
    for l in gzip.open(f"{ROOT}/b.jsonl.gz", "rt"):
        r = json.loads(l)
        sp = r["split"]
        c[(sp, "n")] += 1
        bt = r["b_train"]
        c[(sp, "read")] += bt["read"]
        if bt["read"]:
            c[(sp, "right")] += int(bt["answer"] == r["gold"])
            c[(sp, "self")] += bt.get("self", 0)
        c[(sp, "oracle_right")] += int(r["b_oracle"]["answer"] == r["gold"])
    head = ["| split | n | B restricted reads | of those, right | matched its own frame | B given the frame, right |",
            "|---|---|---|---|---|---|"]
    body = []
    for sp in SPLITS:
        n = c[(sp, "n")]
        if not n:
            continue
        rd = c[(sp, "read")]
        body.append(f"| `{sp}` | {n} | {rd} / {n} = {rd/n:.4f} | "
                    f"{c[(sp,'right')]} / {rd if rd else 0}"
                    + (f" = {c[(sp,'right')]/rd:.4f}" if rd else "")
                    + f" | {c[(sp,'self')]} | "
                    f"{c[(sp,'oracle_right')]} / {n} = {c[(sp,'oracle_right')]/n:.4f} |")
    w(name, head + body)


ALL = [("A_greedy", "A greedy"), ("A_sampled", "A sampled"),
       ("B_train", "B training frames"), ("B_oracle", "B given the frame"),
       ("C_l_greedy", "C 45.5M greedy"), ("C_l_sampled", "C 45.5M sampled"),
       ("C_xs_greedy", "C 0.40M greedy"), ("C_xs_sampled", "C 0.40M sampled")]


def main():
    m = load("report_main.json")
    if m:
        t_main(m, ALL, "t_main.md")
        t_main(m, [c for c in ALL if c[0].startswith("C")], "t_main_exact.md",
               field="structure_exact")
        t_range(m, ALL, "t_range.md")
        t_main(m, ALL, "t_main_hedge.md", field="none")
    h = load("report_home.json")
    if h:
        t_main(h, ALL, "t_home.md")
        t_range(h, ALL, "t_home_range.md")
    d = load("report_depth.json")
    if d:
        for sp in SPLITS:
            t_depth(d, ALL, f"t_depth_{sp}.md", sp)
    dn = load("report_depth_narrow.json")
    if dn:
        t_depth(dn, ALL, "t_depth_narrow_train.md", "train")
        t_depth(dn, ALL, "t_depth_narrow_lexicon.md", "lexicon")
    x = load("report_transpose.json")
    if x:
        t_transpose(x, "t_transpose.md")
    for tag in ("xs", "l"):
        lr = load(f"ladder_{tag}.json")
        if lr:
            t_ladder(lr, f"t_ladder_{tag}.md")
            t_ladder_split(lr, f"t_ladder_{tag}_split.md")
    t_distance("t_distance.md")
    t_bcoverage("t_bcoverage.md")
    t_wdepth("t_wdepth.md")
    t_xmode("t_xmode.md")
    t_interp("t_interp.md")
    t_aheader("t_aheader.md")
    t_aform("t_aform.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
