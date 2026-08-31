"""ONESHOT.md, built from the record files rather than typed.

Every table in the document is rendered here out of
`results/norm/oneshot/report.json`, and the document is the template with those
tables substituted in. A number in the prose that is not in a table is one a
reader can find in the table beside it.
"""

from __future__ import annotations

import argparse
import json
import os
import time

FMT = "{:.4f}"


def f(x):
    return FMT.format(x) if isinstance(x, (int, float)) else str(x)


def table(head, rows) -> str:
    cols = len(head)
    widths = [max(len(str(head[i])),
                  max((len(str(r[i])) for r in rows), default=0))
              for i in range(cols)]
    out = ["| " + " | ".join(str(h).ljust(widths[i])
                             for i, h in enumerate(head)) + " |",
           "| " + " | ".join("-" * widths[i] for i in range(cols)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c).ljust(widths[i])
                                     for i, c in enumerate(r)) + " |")
    return "\n".join(out)


FAMS = (("a2c1", "two directories, one clause"),
        ("a3c1", "three directories, one clause"),
        ("a2c2", "two directories, two clauses"),
        ("a3c2", "three directories, two clauses"))


def t_acq(rep) -> str:
    rows = []
    for fam, label in FAMS:
        base = rep["acq"].get(f"{fam}|pages1|L")
        if not base:
            continue
        r = [label, base["n"], f(base["floor"])]
        for npg in (1, 2, 4):
            r.append(f(rep["acq"][f"{fam}|pages{npg}|L"]["strict"]))
        for s in ("S1", "S2", "P"):
            r.append(f(rep["acq"][f"{fam}|pages1|{s}"]["strict"]))
        rows.append(r)
    return table(["operation family", "n", "floor", "L 1 page", "L 2 pages",
                  "L 4 pages", "S1", "S2", "parser"], rows)


def t_split(rep) -> str:
    rows = []
    for k in sorted(rep["cells"]):
        if not k.endswith("|L"):
            continue
        _, fam, split, _ = k.split("|")
        c = rep["cells"][k]
        s1 = rep["cells"][f"acq|{fam}|{split}|S1"]
        rows.append([fam, split, c["n"], f(c["floor"]), f(c["strict"]),
                     f(s1["strict"])])
    return table(["family", "frame split", "n", "floor", "L strict",
                  "S1 strict"], rows)


def t_ladder(rep, tags, ks) -> str:
    rows = []
    lad = rep["ladder"]["all|L"]
    rows.append(["library, 1 page", "", lad["n"], f(lad["floor"]),
                 f(lad["strict"]), f(lad["strict"]), ""])
    base = rep["neural"].get("base_l|greedy|all")
    if base:
        sm = rep["neural"].get("base_l|sampled|all", {})
        rows.append(["network, no gradient", 0, base["n"], f(base["floor"]),
                     f(base["strict"]), f(sm.get("strict", 0)),
                     f(base.get("structure_exact", 0))])
    k0 = rep["neural"].get("k0|greedy|all")
    if k0:
        sm = rep["neural"].get("k0|sampled|all", {})
        rows.append(["network, control run", 0, k0["n"], f(k0["floor"]),
                     f(k0["strict"]), f(sm.get("strict", 0)),
                     f(k0.get("structure_exact", 0))])
    for tag in tags:
        for k in ks:
            key = f"{tag}_k{k}|greedy|all"
            if key not in rep["neural"]:
                continue
            g = rep["neural"][key]
            s = rep["neural"].get(f"{tag}_k{k}|sampled|all", {})
            rows.append([f"network, {tag}", k, g["n"], f(g["floor"]),
                         f(g["strict"]), f(s.get("strict", 0)),
                         f(g.get("structure_exact", 0))])
    fam = rep["neural"].get("family|greedy|all")
    if fam:
        s = rep["neural"].get("family|sampled|all", {})
        rows.append(["network, family trained", 1024, fam["n"],
                     f(fam["floor"]), f(fam["strict"]),
                     f(s.get("strict", 0)),
                     f(fam.get("structure_exact", 0))])
    return table(["system", "examples", "n", "floor", "strict greedy",
                  "strict sampled", "structure exact"], rows)


def t_ladder_own(rep, tags, ks) -> str:
    """Each fine tuned network on the operation it was trained on."""
    rows = []
    for tag in tags:
        iid = "acq/" + "/".join(tag.split("_")[1:])
        row0 = rep["neural"].get(f"base_l|greedy|{iid}")
        r = [tag, iid]
        for k in ks:
            c = rep["neural"].get(f"{tag}_k{k}|greedy|{iid}")
            r.append(f(c["strict"]) if c else "-")
        r.append(f(row0["strict"]) if row0 else "-")
        rows.append(r)
    return table(["pool", "operation"] + [f"k={k}" for k in ks]
                 + ["no gradient"], rows)


def t_depth(rep) -> str:
    rows = []
    for n in rep["depth"]["_depths"]:
        c = rep["depth"][f"n{n}|aligned|L"]
        r = [n, c["n"], f(c["floor"]), f(c["strict"])]
        for s in ("S1", "S2"):
            r.append(f(rep["depth"][f"n{n}|aligned|{s}"]["strict"]))
        for name in ("n_base_l", "n_family"):
            k = f"{name}|greedy|depth|n{n}|aligned"
            r.append(f(rep["neural"][k]["strict"])
                     if k in rep["neural"] else "-")
        rows.append(r)
    return table(["applications", "n", "floor", "L strict", "S1", "S2",
                  "network no gradient", "network family trained"], rows)


def t_compose(rep) -> str:
    rows = []
    c = rep["compose"]["L"]
    rows.append(["library, two pages", c["n"], f(c["floor"]),
                 f(c["strict"]), f(c["lenient"]), f(c["declined"]), ""])
    for s in ("S1", "S2", "P"):
        d = rep["compose"][s]
        rows.append([{"S1": "shortcut, first line",
                      "S2": "shortcut, last line",
                      "P": "corpus parser"}[s], d["n"], f(d["floor"]),
                     f(d["strict"]), f(d["lenient"]), f(d["declined"]), ""])
    for name, label in (("n_base_l", "network, no gradient"),
                        ("n_family", "network, family trained")):
        for mode in ("greedy", "sampled"):
            k = f"{name}|{mode}|compose"
            if k in rep["neural"]:
                d = rep["neural"][k]
                rows.append([f"{label} ({mode})", d["n"], f(d["floor"]),
                             f(d["strict"]), f(d["lenient"]),
                             f(d["declined"]),
                             f(d.get("structure_exact", 0))])
    return table(["system", "n", "floor", "strict", "lenient", "declined",
                  "structure exact"], rows)


def t_contra(rep) -> str:
    rows = []
    for fam in ("page_first", "page_second"):
        for s, label in (("L", "library"), ("S1", "shortcut, first line"),
                         ("S2", "shortcut, last line"),
                         ("P", "corpus parser")):
            c = rep["contra"][f"{fam}|{s}"]
            rows.append([fam, label, c["n"], f(c["floor"]),
                         f(c["follows_page"]), f(c["follows_training"]),
                         f(c["neither"])])
        for name, label in (("n_base_l", "network, no gradient"),
                            ("n_family", "network, family trained")):
            k = f"{name}|greedy|contra|{fam}"
            if k in rep["neural"]:
                c = rep["neural"][k]
                rows.append([fam, label, c["n"], f(c["floor"]),
                             f(c["follows_page"]), f(c["follows_training"]),
                             f(c["neither"])])
    return table(["page says", "system", "n", "floor", "follows page",
                  "follows training", "neither"], rows)


def t_stress(rep) -> str:
    rows = []
    labels = {"c3": "three clauses", "c4": "four clauses",
              "a4": "four directories", "a5": "five directories"}
    for fam in ("c3", "c4", "a4", "a5"):
        k = f"{fam}|L"
        if k not in rep["stress"]:
            continue
        c = rep["stress"][k]
        rows.append([labels[fam], c["n"], f(c["floor"]), f(c["strict"]),
                     f(rep["stress"][f"{fam}|S1"]["strict"]),
                     f(rep["stress"][f"{fam}|S2"]["strict"]),
                     f(rep["stress"][f"{fam}|P"]["strict"])])
    return table(["operation", "n", "floor", "L strict", "S1", "S2",
                  "parser"], rows)


def t_controls(rep) -> str:
    rows = []
    for cond, label in (("held_mode", "definition in the held out wording"),
                        ("unstated", "question names no defined operation")):
        c = rep["controls"][f"{cond}|L"]
        stage = ", ".join(f"{k} {v}" for k, v in sorted(c["stage"].items()))
        rows.append([label, c["n"], f(c["refused"]), stage or "-"])
    a = rep.get("attack", {})
    if a:
        m = a["mutate"]
        rows.append(["last case of the definition moved", m["n"],
                     f(m["followed_new"] / m["n"]),
                     f"followed the new page, {m['gold_differs']} golds moved"])
        s = a["strip"]
        rows.append(["definition page removed", s["n"],
                     f(s["refused"] / s["n"]),
                     ", ".join(f"{k} {v}"
                               for k, v in sorted(s["stages"].items()))])
        r = a["rename"]
        rows.append(["operation renamed on page and question", r["n"],
                     f(r["same_answer"] / r["n"]), "same answer"])
        w = a["row"]
        rows.append(["one directory row changed", w["n"],
                     f(w["followed_new"] / w["n"]),
                     f"followed the new row, {w['gold_differs']} golds moved"])
    return table(["check", "n", "rate", "where"], rows)


def t_paths(rep) -> str:
    rows = [[k, v] for k, v in sorted(rep["records"].items())]
    return table(["record", "path"], rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/norm/oneshot/report.json")
    ap.add_argument("--tmpl", default="src/norm/ONESHOT.tmpl.md")
    ap.add_argument("--out", default="src/norm/ONESHOT.md")
    ap.add_argument("--tags", default="acq_a2c1_2,acq_a3c1_26,"
                                      "acq_a3c2_144,acq_a2c2_157")
    ap.add_argument("--ks", default="1,2,4,16,64")
    a = ap.parse_args()

    rep = json.load(open(a.report))
    tags = a.tags.split(",")
    ks = [int(x) for x in a.ks.split(",")]
    subs = {
        "T_ACQ": t_acq(rep),
        "T_SPLIT": t_split(rep),
        "T_LADDER": t_ladder(rep, tags, ks),
        "T_LADDER_OWN": t_ladder_own(rep, tags, ks),
        "T_DEPTH": t_depth(rep),
        "T_COMPOSE": t_compose(rep),
        "T_CONTRA": t_contra(rep),
        "T_STRESS": t_stress(rep),
        "T_CONTROLS": t_controls(rep),
        "T_PATHS": t_paths(rep),
        "BUILT": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
    }
    doc = open(a.tmpl).read()
    for k, v in subs.items():
        doc = doc.replace("{{" + k + "}}", v)
    if "{{" in doc:
        import re
        miss = set(re.findall(r"\{\{([A-Z_]+)\}\}", doc))
        if miss:
            raise SystemExit(f"template slot with no table: {sorted(miss)}")
    with open(a.out, "w") as fh:
        fh.write(doc)
    print(json.dumps({"out": os.path.abspath(a.out), "bytes": len(doc)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
