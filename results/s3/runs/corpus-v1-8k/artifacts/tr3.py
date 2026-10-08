"""Score induced operators against the page and against the training identity.

Two levels, both from one set of induced operators.

  operator  the induced body's behaviour on eight probe pairs, against the
            transposed page's operator and against the canonical binding the
            template always had. This is the 0 of 290 toward the page and 290
            of 290 toward training that `src/audit/VERDICT.md` reports.
  item      `oracle_plan`: the gold plan is handed over and executed with the
            induced operators, so the only thing the model supplies is the
            induction. This is the 0 of 678 and 678 of 678.
"""
from __future__ import annotations
import argparse, json, sys, random, collections
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")

from src.corpus.transposed import transpose_page
from src.opgraph.invent import make_world, seq_flat
from src.opgraph.opdef import parse_operators
from src.opgraph.plan import run_plan

PROBES = [(7, 4), (12, 5), (5, 9), (8, 3), (2, 11), (11, 2), (6, 6), (9, 1)]


def behaviour(op):
    out = []
    for a in PROBES:
        try:
            out.append(op(*a))
        except Exception:
            out.append(None)
    return out


def world_cache(seed, cache):
    if seed not in cache:
        w = make_world(seed, breadth=3, style=0)
        binops = [p for p in w.pages if p.key.startswith("binop:")]
        cache[seed] = {
            "world": w,
            "pages": [(p.ops[0], transpose_page(p)[1]) for p in binops],
        }
    return cache[seed]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rolls", required=True)
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cache = {}
    cells = collections.defaultdict(collections.Counter)
    induced = collections.defaultdict(dict)     # (decode, seed) -> {symbol: op}

    for line in open(args.rolls):
        if not line.strip():
            continue
        r = json.loads(line)
        seed, j, dec = int(r["seed"]), int(r["page"]), r.get("decode", "?")
        w = world_cache(seed, cache)
        train_op, page_op = w["pages"][j]
        b_train, b_page = behaviour(train_op), behaviour(page_op)
        distinguishable = b_train != b_page
        text = r.get("emitted", "")
        try:
            ops = {o.symbol: o for o in parse_operators(text)}
        except Exception:
            ops = {}
        op = ops.get(train_op.symbol)
        if op is None and len(ops) == 1:
            op = next(iter(ops.values()))
        c = cells[dec]
        c["n"] += 1
        c["distinguishable"] += int(distinguishable)
        c["parsed"] += int(bool(ops))
        c["right_symbol"] += int(train_op.symbol in ops)
        c["empty"] += int(not text.strip())
        if op is not None:
            induced[(dec, seed)][train_op.symbol] = op
            if distinguishable:
                b = behaviour(op)
                c["d_parsed"] += 1
                c["follows_page"] += int(b == b_page)
                c["follows_train"] += int(b == b_train)
                c["follows_neither"] += int(b != b_page and b != b_train)

    # oracle_plan at the item level
    items = collections.defaultdict(collections.Counter)
    for line in open(args.episodes):
        ep = json.loads(line)
        q = ep["questions"][0]
        seed, depth = int(ep["seed"]), int(ep["depth"])
        w = world_cache(seed, cache)
        item = seq_flat(w["world"], random.Random(seed * 131 + depth), depth)
        for dec in sorted({d for d, s in induced}):
            ops = induced.get((dec, seed), {})
            k = items[(dec, depth)]
            k["n"] += 1
            if not ops:
                k["no_ops"] += 1
                continue
            try:
                ans = str(run_plan(item.plan, ops))
            except Exception:
                k["exec_failed"] += 1
                continue
            k["ran"] += 1
            k["page"] += int(ans == str(q["page_answer"]))
            k["train"] += int(ans == str(q["train_answer"]))
            k["neither"] += int(ans not in (str(q["page_answer"]),
                                            str(q["train_answer"])))

    out = {"operator": {}, "oracle_plan": {}}
    print("operator level")
    print("%-8s %5s %8s %7s %8s %10s %10s %10s"
          % ("decode", "n", "distingu", "parsed", "rightsym", "page", "train",
             "neither"))
    for dec in sorted(cells):
        c = cells[dec]
        d = max(1, c["d_parsed"])
        out["operator"][dec] = dict(c)
        out["operator"][dec]["page_rate"] = c["follows_page"] / d
        out["operator"][dec]["train_rate"] = c["follows_train"] / d
        print("%-8s %5d %8d %7d %8d %4d/%-5d %4d/%-5d %4d/%-5d"
              % (dec, c["n"], c["distinguishable"], c["parsed"],
                 c["right_symbol"], c["follows_page"], c["d_parsed"],
                 c["follows_train"], c["d_parsed"], c["follows_neither"],
                 c["d_parsed"]))
    print("oracle_plan, item level")
    print("%-8s %6s %5s %5s %8s %8s %9s %9s"
          % ("decode", "depth", "n", "ran", "no_ops", "execfail", "page", "train"))
    for key in sorted(items):
        k = items[key]
        out["oracle_plan"]["|".join(map(str, key))] = dict(k)
        print("%-8s %6s %5d %5d %8d %8d %4d/%-4d %4d/%-4d"
              % (key[0], key[1], k["n"], k["ran"], k["no_ops"],
                 k["exec_failed"], k["page"], k["n"], k["train"], k["n"]))
    for dec in sorted({d for d, _ in items}):
        tot = collections.Counter()
        for key in items:
            if key[0] == dec:
                tot.update(items[key])
        out["oracle_plan"][f"{dec}|all"] = dict(tot)
        print("%-8s %6s %5d %5d %8d %8d %4d/%-4d %4d/%-4d"
              % (dec, "all", tot["n"], tot["ran"], tot["no_ops"],
                 tot["exec_failed"], tot["page"], tot["n"], tot["train"],
                 tot["n"]))
    json.dump(out, open(args.out, "w"), indent=1)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
