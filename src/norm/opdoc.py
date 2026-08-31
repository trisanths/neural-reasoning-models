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
        r.append(f(base.get("structure_exact", 0)))
        for s in ("S1", "S2", "P"):
            r.append(f(rep["acq"][f"{fam}|pages1|{s}"]["strict"]))
        rows.append(r)
    return table(["operation family", "n", "floor", "L 1 page", "L 2 pages",
                  "L 4 pages", "L structure exact", "S1", "S2", "parser"],
                 rows)


def t_acq_net(rep) -> str:
    """The network on the same acquisition items, one row per family."""
    rows = []
    for fam, label2 in FAMS:
        for name, label in (("n_base_l", "no gradient"),
                            ("n_family", "family trained")):
            k = f"{name}|greedy|acq|{fam}|pages1"
            if k not in rep["neural"]:
                continue
            g = rep["neural"][k]
            sm = rep["neural"].get(f"{name}|sampled|acq|{fam}|pages1", {})
            rows.append([label, label2, g["n"], f(g["floor"]),
                         f(g["strict"]), f(sm.get("strict", 0)),
                         f(g.get("structure_exact", 0)), f(g["declined"])])
    return table(["network", "family", "n", "floor", "strict greedy",
                  "strict sampled", "structure exact", "declined"], rows)


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
    """One row per ladder operation, so nothing is pooled across operations."""
    rows = []
    iids = sorted({k.rsplit("|", 1)[0] for k in rep["ladder"]
                   if k.startswith("acq/") and k.endswith("|L")})
    for iid in iids:
        lib = rep["ladder"][f"{iid}|L"]
        s1 = rep["ladder"][f"{iid}|S1"]
        s2 = rep["ladder"][f"{iid}|S2"]
        base = rep["neural"].get(f"base_l|greedy|{iid}")
        fam = rep["neural"].get(f"family|greedy|{iid}")
        tag = "acq_" + "_".join(iid.split("/")[1:])
        best, at = 0.0, "-"
        for k in ks:
            c = rep["neural"].get(f"{tag}_k{k}|greedy|{iid}")
            if c and c["strict"] > best:
                best, at = c["strict"], str(k)
        rows.append([iid, lib["n"], f(lib["floor"]), f(lib["strict"]),
                     f(lib.get("structure_exact", 0)),
                     f(s1["strict"]), f(s2["strict"]),
                     f(base["strict"]) if base else "-",
                     f(fam["strict"]) if fam else "-",
                     f(best) if at != "-" else "-", at])
    return table(["operation", "n", "floor", "library", "library exact",
                  "S1", "S2", "network no gradient",
                  "network family trained", "network best on its own ladder",
                  "at k"], rows)


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


def t_cost(rep, tags, ks) -> str:
    """Examples per acquired operation, which is what this lane is named for.

    For the library the answer is one page and no examples. For the network it
    is the smallest k on the ladder whose strict score clears the item set's own
    chance floor, and the smallest that clears 0.9000.
    """
    rows = []
    lad = rep["ladder"]["all|L"]
    rows.append(["library", "one page, no examples", f(lad["strict"]),
                 f(lad["floor"]), "0", "0"])
    ks = list(ks)
    for tag in tags:
        iid = "acq/" + "/".join(tag.split("_")[1:])
        best, over, nine, seen = 0.0, None, None, []
        for k in ks:
            c = rep["neural"].get(f"{tag}_k{k}|greedy|{iid}")
            if not c:
                continue
            seen.append(k)
            best = max(best, c["strict"])
            if over is None and c["strict"] > c["floor"]:
                over = str(k)
            if nine is None and c["strict"] >= 0.9:
                nine = str(k)
        top = max(seen) if seen else 0
        c0 = rep["neural"].get(f"base_l|greedy|{iid}") or {}
        rows.append(["network", iid, f(best) if seen else "-",
                     f(c0.get("floor", 0)),
                     over or f"not within {top}", nine or f"not within {top}"])
    return table(["system", "operation", "best strict reached", "floor",
                  "examples to clear the floor",
                  "examples to reach 0.9000"], rows)





def t_second(rep, tags, ks) -> str:
    """The same ladder started from the family trained network.

    This network already knows the notation and has read a thousand examples of
    other operations of the same family, so k here buys this operation and
    nothing else.
    """
    rows = []
    for tag in tags:
        iid = "acq/" + "/".join(tag.split("_")[1:])
        r = [tag, iid]
        c0 = rep["neural"].get(f"family|greedy|{iid}")
        r.append(f(c0["strict"]) if c0 else "-")
        for k in ks:
            c = rep["neural"].get(f"second_{tag}_k{k}|greedy|{iid}")
            r.append(f(c["strict"]) if c else "-")
        rows.append(r)
    return table(["pool", "operation", "k=0 (family trained)"]
                 + [f"k={k}" for k in ks], rows)


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


def t_deep(rep) -> str:
    """Depth past the corpus plan length ceiling, with what it cost."""
    rows = []
    us = rep.get("attack", {}).get("deep", {}).get("microseconds_per_run", {})
    for n in rep["deep"].get("_depths", []):
        c = rep["deep"][f"n{n}|L"]
        rows.append([n, c["n"], f(c["floor"]), f(c["strict"]),
                     f(c.get("structure_exact", 0)),
                     f(rep["deep"][f"n{n}|S1"]["strict"]),
                     f(rep["deep"][f"n{n}|S2"]["strict"]),
                     us.get(str(n), "-")])
    return table(["applications", "n", "floor", "L strict",
                  "L structure exact", "S1", "S2",
                  "microseconds to run the plan"], rows)


def t_compose(rep) -> str:
    rows = []
    c = rep["compose"]["L"]
    rows.append(["library, two pages", c["n"], f(c["floor"]),
                 f(c["strict"]), f(c["lenient"]), f(c["declined"]),
                 f(c.get("structure_exact", 0))])
    for s in ("S1", "S2", "P"):
        d = rep["compose"][s]
        rows.append([{"S1": "shortcut, first line",
                      "S2": "shortcut, last line",
                      "P": "corpus parser"}[s], d["n"], f(d["floor"]),
                     f(d["strict"]), f(d["lenient"]), f(d["declined"]), "-"])
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


def t_diag(rep) -> str:
    """How much of the needed structure the network actually writes down."""
    rows = []
    labels = {"base_compose": "network, no gradient",
              "family_compose": "network, family trained"}
    keys = ("ops", "calls", "distinct_called", "tables", "steps")
    for tag in sorted(rep.get("diag", {})):
        d = rep["diag"][tag]
        g, e = d["means_over_gold"], d["means_over_emitted_that_read"]
        rows.append(["what the item needs", d["n"], "-"]
                    + [f(g[k]) for k in keys])
        rows.append([labels.get(tag, tag), d["n"] - d["n_malformed"],
                     d["n_malformed"]]
                    + [f(e[k]) if e[k] is not None else "-" for k in keys])
    return table(["row", "n", "malformed", "operator definitions", "calls",
                  "distinct operators called", "directories", "plan steps"],
                 rows)


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
              "a4": "four directories", "a5": "five directories",
              "distract": "a directory the question never names"}
    for fam in ("c3", "c4", "a4", "a5", "distract"):
        k = f"{fam}|L"
        if k not in rep["stress"]:
            continue
        c = rep["stress"][k]
        rows.append([labels[fam], c["n"], f(c["floor"]), f(c["strict"]),
                     f(c.get("structure_exact", 0)),
                     f(rep["stress"][f"{fam}|S1"]["strict"]),
                     f(rep["stress"][f"{fam}|S2"]["strict"]),
                     f(rep["stress"][f"{fam}|P"]["strict"])])
    return table(["operation", "n", "floor", "L strict", "L structure exact",
                  "S1", "S2", "parser"], rows)


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
        al = a.get("alpha")
        if al and al["n"]:
            rows.append(["every invented word renamed", al["n"],
                         f(al["renamed_gold"] / al["n"]),
                         "answered the renamed gold"])
        ic = a.get("incomplete")
        if ic and ic["n"]:
            rows.append(["the last case cut off the definition", ic["n"],
                         f(ic["refused"] / ic["n"]),
                         ", ".join(f"{k} {v}"
                                   for k, v in sorted(ic["stages"].items()))])
        ex = a.get("extra_definition")
        if ex and ex["n"]:
            rows.append(["a second operation the question never names",
                         ex["n"], f(ex["same_answer"] / ex["n"]),
                         "same answer"])
    return table(["check", "n", "rate", "where"], rows)


def t_states(rep) -> str:
    """Where a wrong answer went wrong, for each system on each condition."""
    rows = []
    labels = {"L": "library", "n_base_l|greedy": "network, no gradient",
              "n_family|greedy": "network, family trained"}
    for who, label in labels.items():
        for cond in ("acq", "depth", "compose", "contra", "held_mode",
                     "unstated"):
            k = f"{who}|{cond}"
            if k not in rep["states"]:
                continue
            c = rep["states"][k]
            rows.append([label, cond, c["n"], f(c["malformed"]),
                         f(c["refused"]), f(c["ran_wrong"]),
                         f(c["ran_right"])])
    return table(["system", "condition", "n", "no structure produced",
                  "interpreter refused", "ran the wrong structure",
                  "ran the right one"], rows)


def t_paths(rep) -> str:
    rows = [[k, v] for k, v in sorted(rep["records"].items())]
    return table(["record", "path"], rows)


def check_fresh(report_path: str, rep: dict, d: str) -> dict:
    """Refuse to build a document from a report older than its own records.

    A rescore run against stale record files mixed two differently graded runs
    on this project once. The document is the place that costs the most, so the
    check lives here and it is an error rather than a warning.
    """
    import glob as _g
    t = os.path.getmtime(report_path)
    stale = []
    paths = list(rep.get("records", {}).values())
    paths += _g.glob(os.path.join(d, "*.jsonl.gz"))
    paths += _g.glob(os.path.join(d, "attack.json"))
    paths = sorted({os.path.realpath(p) for p in paths})
    for p in paths:
        if os.path.exists(p) and os.path.getmtime(p) > t:
            stale.append(os.path.basename(p))
    if stale:
        raise SystemExit("the report is older than its records, rebuild it "
                         "first: " + ", ".join(sorted(set(stale))))
    return {"report_mtime": time.strftime("%Y-%m-%d %H:%M UTC",
                                          time.gmtime(t)),
            "n_records_checked": len(paths)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/norm/oneshot/report.json")
    ap.add_argument("--tmpl", default="src/norm/ONESHOT.tmpl.md")
    ap.add_argument("--out", default="src/norm/ONESHOT.md")
    ap.add_argument("--tags", default="acq_a2c1_2,acq_a3c1_26,"
                                      "acq_a3c2_144,acq_a2c2_157")
    ap.add_argument("--ks", default="1,2,4,16,64,256,1024")
    a = ap.parse_args()

    rep = json.load(open(a.report))
    fresh = check_fresh(a.report, rep, os.path.dirname(a.report))
    tags = a.tags.split(",")
    ks = [int(x) for x in a.ks.split(",")]
    subs = {
        "T_ACQ": t_acq(rep),
        "T_ACQ_NET": t_acq_net(rep),
        "T_SPLIT": t_split(rep),
        "T_LADDER": t_ladder(rep, tags, ks),
        "T_LADDER_OWN": t_ladder_own(rep, tags, ks),
        "T_COST": t_cost(rep, tags, ks),
        "T_SECOND": t_second(rep, tags, [1, 2, 4]),
        "T_DEPTH": t_depth(rep),
        "T_DEEP": t_deep(rep),
        "T_COMPOSE": t_compose(rep),
        "T_CONTRA": t_contra(rep),
        "T_DIAG": t_diag(rep),
        "T_STRESS": t_stress(rep),
        "T_CONTROLS": t_controls(rep),
        "T_STATES": t_states(rep),
        "T_PATHS": t_paths(rep),
        "BUILT": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "FRESH": (f"{fresh['n_records_checked']} record files, none newer "
                  f"than the report of {fresh['report_mtime']}"),
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
