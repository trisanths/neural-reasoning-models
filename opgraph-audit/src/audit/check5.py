"""Check 5: is the plan readable off the packaging rather than the content?

Two separate questions, measured separately.

A. What does the plan prompt actually contain? A surface parser that sees only
   the two fields the scheduler is given (the operator signature line and the
   question string) and never a page, an operator body, or a gold answer, is
   run against the gold plans at every depth. If it is exact, the plan target
   carries no semantic content at all.

B. Do the packaging features the brief names (page order, page and answer
   lengths, token counts, rule names, glyph identity) predict the one bit that
   the plan turns on, namely which way the operator associates? A small
   decision tree is fit on training-range worlds using formatting counts only,
   with the sentence that states the associativity deleted from every feature,
   and tested on the eval worlds.
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter

from src.opgraph.data import eval_worlds, make_item
from src.opgraph.invent import make_world
from src.opgraph.opdef import Operator
from src.opgraph.plan import (Plan, Step, run_plan, serialize_plan,
                              signature_line)

N = 150
DEPTHS = [1, 2, 3, 4, 5, 6, 7, 8]


# ------------------------------------------------------------------ part A

def parse_signature(sig: str) -> dict:
    """Symbol -> (arity, assoc) read straight off the scheduler's ops line."""
    out = {}
    for tok in sig.split():
        bits = tok.split("/")
        if bits[-1] in ("left", "right"):
            assoc, arity, sym = bits[-1], bits[-2], "/".join(bits[:-2])
        else:
            assoc, arity, sym = None, bits[-1], "/".join(bits[:-1])
        out[sym] = (int(arity), assoc)
    return out


_NUM = re.compile(r"-?\d+")


def surface_plan(sig: str, question: str, use_assoc: bool = True,
                 force: str = "left") -> str:
    """Write a plan from the two prompt fields and nothing else.

    Knows the semicolon grammar and the shape of the two question templates.
    Knows no operator body, reads no page, and never sees a gold answer.
    """
    table = parse_signature(sig)
    syms = [s for s in table if table[s][0] == 2 and len(s) == 1]
    body = question.strip()
    if body.lower().startswith("evaluate"):
        body = body[len("evaluate"):].strip().rstrip(".")
        toks = _tokenize_expr(body, set(syms))
        tree, rest = _parse_infix(toks, table, use_assoc, force)
        if rest:
            return "ans 0"
        steps: list[Step] = []
        last = _emit(tree, [0], steps)
        return serialize_plan(Plan(tuple(steps), str(last)))
    m = re.match(r"How many (\S+) are (\d+) (\S+)\?", body)
    if m:
        return serialize_plan(Plan((Step("t1", m.group(3), (int(m.group(2)),)),), "t1"))
    m = re.search(r"value of (\d+)\.", body)
    if m and "score" in table:
        base = int(m.group(1))
        bits = tuple(x == "marked" for x in re.findall(r"It is (marked|not marked)", body))
        return serialize_plan(Plan((Step("t1", "score", (base,) + bits),), "t1"))
    return "ans 0"


def _tokenize_expr(s: str, syms: set) -> list[str]:
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "()":
            out.append(c)
            i += 1
        elif c.isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            out.append(s[i:j])
            i = j
        else:
            j = i
            while j < len(s) and not s[j].isspace() and s[j] not in "()":
                j += 1
            out.append(s[i:j])
            i = j
    return out


def _parse_infix(toks, table, use_assoc, force):
    """A flat run of one infix symbol, or a fully parenthesised tree."""
    node, i = _atom(toks, 0, table, use_assoc, force)
    items = [node]
    syms = []
    while i < len(toks) and toks[i] != ")":
        syms.append(toks[i])
        n, i = _atom(toks, i + 1, table, use_assoc, force)
        items.append(n)
    if not syms:
        return items[0], toks[i:]
    sym = syms[0]
    assoc = table.get(sym, (2, None))[1] if use_assoc else force
    if assoc == "right":
        tree = items[-1]
        for a in reversed(items[:-1]):
            tree = (sym, [a, tree])
    else:
        tree = items[0]
        for b in items[1:]:
            tree = (sym, [tree, b])
    return tree, toks[i:]


def _atom(toks, i, table, use_assoc, force):
    if toks[i] == "(":
        node, rest = _parse_infix(toks[i + 1:], table, use_assoc, force)
        j = i + 1 + (len(toks[i + 1:]) - len(rest))
        return node, j + 1
    return int(toks[i]), i + 1


def _emit(node, ctr, steps):
    if isinstance(node, int):
        return node
    sym, kids = node
    args = [_emit(k, ctr, steps) for k in kids]
    ctr[0] += 1
    t = f"t{ctr[0]}"
    steps.append(Step(t, sym, tuple(args)))
    return t


def part_a(style: int = 0) -> dict:
    out = {}
    for kind, depths in (("sequential", DEPTHS), ("sequential_paren", [2, 3, 4, 5, 6]),
                         ("breadth", [1, 2, 3]), ("units", [1])):
        for d in depths:
            breadth = d if kind == "breadth" else 3
            ws = eval_worlds(kind, N, breadth=breadth, style=style)
            items = [make_item(kind, w, d, i) for i, w in enumerate(ws)]
            hit_full = hit_noassoc = ans_full = ans_noassoc = 0
            for it in items:
                sig = signature_line(it.world.ops)
                gold = serialize_plan(it.plan)
                p1 = surface_plan(sig, it.text, use_assoc=True)
                p0 = surface_plan(sig, it.text, use_assoc=False, force="left")
                hit_full += p1 == gold
                hit_noassoc += p0 == gold
                try:
                    v = run_plan(_reparse(p1), it.world.ops)
                    ans_full += str(v).strip().lower() == it.gold.strip().lower()
                except Exception:
                    pass
                try:
                    v = run_plan(_reparse(p0), it.world.ops)
                    ans_noassoc += str(v).strip().lower() == it.gold.strip().lower()
                except Exception:
                    pass
            out[f"{kind}/{d}"] = {
                "n": len(items),
                "plan_exact_surface": round(hit_full / len(items), 4),
                "plan_exact_surface_no_assoc": round(hit_noassoc / len(items), 4),
                "answer_acc_surface_plan_gold_ops": round(ans_full / len(items), 4),
                "answer_acc_no_assoc_always_left": round(ans_noassoc / len(items), 4),
            }
    return out


def _reparse(text):
    from src.opgraph.plan import parse_plan
    return parse_plan(text)


# ------------------------------------------------------------------ part B

ASSOC_RE = re.compile(
    r"(associates (left to right|right to left)\.?|A run of \S+ with no brackets is read "
    r"(left to right|right to left)\.?)")


def packaging_features(world) -> tuple[list[float], int, list[str]]:
    """Formatting counts only, with the associativity sentence deleted."""
    binops = [p for p in world.pages if p.key.startswith("binop:")]
    p = binops[0]
    scrub = ASSOC_RE.sub("", p.text)
    order_pos = world.order.index(world.pages.index(p))
    feats = [
        float(len(p.text)),                       # raw page length
        float(len(scrub)),                        # page length, assoc line cut
        float(len(p.text.split())),               # word count
        float(len(scrub.split())),
        float(p.text.count("\n")),                # line count
        float(order_pos),                         # where the page sits in the set
        float(len(world.pages)),
        float(ord(p.glyph[0])),                   # operator identifier
        float(len(p.text.split("\n")[0])),        # rule name length
        float(sum(len(x.text) for x in world.pages)),
        float(len(scrub) % 2),
        float(len(p.text) % 2),
    ]
    return feats, 1 if p.right_assoc else 0, [
        "page_len", "page_len_scrubbed", "words", "words_scrubbed", "lines",
        "page_order_pos", "n_pages", "glyph_code", "title_len", "total_len",
        "scrub_len_parity", "page_len_parity"]


def _gini(rows):
    if not rows:
        return 0.0
    n = len(rows)
    p = sum(y for _, y in rows) / n
    return 1 - p * p - (1 - p) * (1 - p)


def _fit(rows, depth, max_depth):
    n = len(rows)
    maj = 1 if sum(y for _, y in rows) * 2 >= n else 0
    if depth >= max_depth or n < 8 or _gini(rows) == 0:
        return ("leaf", maj)
    best = None
    nf = len(rows[0][0])
    for f in range(nf):
        vals = sorted({r[0][f] for r in rows})
        for a, b in zip(vals, vals[1:]):
            thr = (a + b) / 2
            L = [r for r in rows if r[0][f] <= thr]
            R = [r for r in rows if r[0][f] > thr]
            if not L or not R:
                continue
            score = (len(L) * _gini(L) + len(R) * _gini(R)) / n
            if best is None or score < best[0]:
                best = (score, f, thr, L, R)
    if best is None or best[0] >= _gini(rows) - 1e-12:
        return ("leaf", maj)
    _, f, thr, L, R = best
    return ("split", f, thr, _fit(L, depth + 1, max_depth), _fit(R, depth + 1, max_depth))


def _pred(tree, x):
    while tree[0] == "split":
        tree = tree[3] if x[tree[1]] <= tree[2] else tree[4]
    return tree[1]


def part_b(max_depth: int = 4) -> dict:
    rng = random.Random(0)
    train = []
    for s in range(4000):
        w = make_world(s, breadth=rng.choice([1, 2, 3]))
        f, y, names = packaging_features(w)
        train.append((f, y))
    tree = _fit(train, 0, max_depth)
    out = {"feature_names": names, "train_n": len(train),
           "train_base_rate": round(sum(y for _, y in train) / len(train), 4)}
    tr_acc = sum(_pred(tree, f) == y for f, y in train) / len(train)
    out["train_acc"] = round(tr_acc, 4)
    for style in (0, 1):
        ws = eval_worlds("sequential", N, breadth=3, style=style)
        rows = [packaging_features(w)[:2] for w in ws]
        acc = sum(_pred(tree, f) == y for f, y in rows) / len(rows)
        base = max(sum(y for _, y in rows), len(rows) - sum(y for _, y in rows)) / len(rows)
        out[f"eval_style{style}_acc"] = round(acc, 4)
        out[f"eval_style{style}_majority"] = round(base, 4)
        out[f"eval_style{style}_n"] = len(rows)
    out["tree"] = _describe(tree, names)
    return out


def _describe(tree, names, ind=0):
    if tree[0] == "leaf":
        return "  " * ind + f"-> {tree[1]}"
    return ("  " * ind + f"if {names[tree[1]]} <= {tree[2]}\n"
            + _describe(tree[3], names, ind + 1) + "\n"
            + _describe(tree[4], names, ind + 1))


# ------------------------------------------------------------------ part C

def part_c() -> dict:
    """Single-feature check: does raw page length alone carry the assoc bit?"""
    lens = {0: Counter(), 1: Counter()}
    for s in range(4000):
        w = make_world(s, breadth=3)
        p = [x for x in w.pages if x.key.startswith("binop:")][0]
        lens[1 if p.right_assoc else 0][len(p.text) % 2] += 1
    return {"page_len_parity_by_assoc": {k: dict(v) for k, v in lens.items()}}


def main() -> int:
    out = {"part_a_style0": part_a(0), "part_a_style1": part_a(1),
           "part_b": part_b(), "part_c": part_c()}
    path = sys.argv[1] if len(sys.argv) > 1 else "results/audit_check5.json"
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    for k, v in out["part_a_style0"].items():
        print(f"{k:24s} exact={v['plan_exact_surface']:.3f} "
              f"exact_noassoc={v['plan_exact_surface_no_assoc']:.3f} "
              f"ans={v['answer_acc_surface_plan_gold_ops']:.3f}")
    print()
    print("part_b", json.dumps({k: v for k, v in out["part_b"].items()
                                if k != "tree"}))
    print(out["part_b"]["tree"])
    print("part_c", json.dumps(out["part_c"]))
    print("[written]", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
