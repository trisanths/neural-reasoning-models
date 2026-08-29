"""Follow ups to check 6.

  B1  what the induced operator table actually contains, clause by clause,
      and in particular whether the associativity annotation survives induction
  B2  the associativity contingency under BOTH plan conditions, so the case
      where the prompt states the answer is separated from the case where the
      prompt does not
  B3  the breadth no-op family: correct answers reached from a plan that drops
      arguments whose contribution happens to be zero
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from math import sqrt

from src.opgraph.opdef import (OpError, parse_operator, serialize,
                               serialize_expr)
from src.opgraph.plan import PlanError, parse_plan, signature_line


def load(p):
    with open(p) as fh:
        return json.load(fh)


def b1(dump) -> dict:
    st = Counter()
    for seed, w in dump["worlds"].items():
        gold = {k: parse_operator(v) for k, v in w["gold"].items()}
        ind = {k: parse_operator(v) for k, v in w["induced"].items()}
        for sym, g in gold.items():
            binop = g.arity == 2 and g.assoc is not None
            st["gold_ops"] += 1
            st["gold_binops"] += binop
            i = ind.get(sym)
            if i is None:
                st["missing_from_induced"] += 1
                continue
            same_body = serialize_expr(i.body) == serialize_expr(g.body)
            same_params = i.params == g.params
            st["induced_present"] += 1
            st["body_exact"] += same_body
            st["params_exact"] += same_params
            st["assoc_present_in_gold"] += g.assoc is not None
            st["assoc_present_in_induced"] += i.assoc is not None
            if binop:
                st["binop_body_exact"] += same_body
                st["binop_assoc_present"] += i.assoc is not None
                st["binop_assoc_correct"] += (i.assoc == g.assoc)
                if same_body and i.assoc is None:
                    st["binop_body_right_assoc_dropped"] += 1
            if g.arity != i.arity:
                st["arity_mismatch"] += 1
                st["arity_mismatch_%s_g%d_i%d" % (sym if not sym.isalpha() else sym,
                                                  g.arity, i.arity)] += 1
    return dict(st)


def sig_check(dump) -> dict:
    """Does the scheduler's ops line carry an assoc field at all?"""
    st = Counter()
    for seed, w in dump["worlds"].items():
        ind = {k: parse_operator(v) for k, v in w["induced"].items()}
        gold = {k: parse_operator(v) for k, v in w["gold"].items()}
        st["induced_line_has_assoc"] += "/left" in signature_line(ind) or \
            "/right" in signature_line(ind)
        st["gold_line_has_assoc"] += "/left" in signature_line(gold) or \
            "/right" in signature_line(gold)
        st["worlds"] += 1
    return dict(st)


def _chi2_phi(a, b, c, d):
    n = a + b + c + d
    r1, r2, c1, c2 = a + b, c + d, a + c, b + d
    if min(r1, r2, c1, c2) == 0:
        return 0.0, 0.0
    exp = [r1 * c1 / n, r1 * c2 / n, r2 * c1 / n, r2 * c2 / n]
    x2 = sum((o - e) ** 2 / e for o, e in zip([a, b, c, d], exp))
    phi = (a * d - b * c) / sqrt(r1 * r2 * c1 * c2)
    return x2, phi


def b2(dump) -> dict:
    out = {}
    for d, rec in dump["items"].items():
        if int(d) not in (2, 3):
            continue
        for cond in ("plan_execute", "oracle_ops"):
            tab = Counter()
            for plan_text, assoc in zip(rec["conds"][cond]["plans"], rec["assoc"]):
                try:
                    p = parse_plan(plan_text)
                except PlanError:
                    tab[(assoc, "unparsable")] += 1
                    continue
                if len(p.steps) < 2:
                    tab[(assoc, "short")] += 1
                    continue
                a0 = p.steps[1].args[0]
                got = "left" if isinstance(a0, str) and a0.startswith("t") else "right"
                tab[(assoc, got)] += 1
            ll, lr = tab[("left", "left")], tab[("left", "right")]
            rl, rr = tab[("right", "left")], tab[("right", "right")]
            n = ll + lr + rl + rr
            x2, phi = _chi2_phi(ll, lr, rl, rr)
            out[f"{cond}/d{d}"] = {
                "n_classified": n,
                "gold_left_model_left": ll, "gold_left_model_right": lr,
                "gold_right_model_left": rl, "gold_right_model_right": rr,
                "agreement": round((ll + rr) / n, 4) if n else None,
                "chi2": round(x2, 4), "phi": round(phi, 4),
                "model_chose_left_rate": round((ll + rl) / n, 4) if n else None,
                "gold_left_rate": round((ll + lr) / n, 4) if n else None,
            }
    return out


def b3(dump) -> dict:
    """breadth only: correct answers from a plan that dropped arguments."""
    out = {}
    for d, rec in dump["items"].items():
        st = Counter()
        gold_arity = None
        for plan_text, ok, qtext, seed in zip(rec["conds"]["plan_execute"]["plans"],
                                              rec["conds"]["plan_execute"]["ok"],
                                              rec["texts"], rec["seeds"]):
            w = dump["worlds"][str(seed)]
            g = parse_operator(w["gold"]["score"])
            i = parse_operator(w["induced"]["score"]) if "score" in w["induced"] else None
            gold_arity = g.arity
            st["items"] += 1
            st["correct"] += bool(ok)
            st["induced_arity_%s" % (i.arity if i else "missing")] += 1
            try:
                p = parse_plan(plan_text)
            except PlanError:
                st["unparsable"] += 1
                continue
            step = next((s for s in p.steps if s.symbol == "score"), None)
            if step is None:
                st["no_score_step"] += 1
                continue
            st["plan_score_args_%d" % len(step.args)] += 1
            if len(step.args) < g.arity:
                st["plan_dropped_args"] += 1
                bits = [x == "marked" for x in _flags(qtext)]
                dropped = bits[len(step.args) - 1:]
                if ok:
                    st["CORRECT_with_dropped_args"] += 1
                    if all(not b for b in dropped):
                        st["CORRECT_dropped_args_all_false"] += 1
                if all(not b for b in dropped):
                    st["dropped_args_all_false"] += 1
        st["gold_arity"] = gold_arity or 0
        out[d] = dict(st)
    return out


def _flags(text):
    import re
    return re.findall(r"It is (marked|not marked)", text)


def main() -> int:
    dump = load(sys.argv[1])
    kind = sys.argv[2] if len(sys.argv) > 2 else "sequential"
    out = {"b1_induced_table": b1(dump), "b1_signature": sig_check(dump)}
    if kind in ("sequential", "sequential_paren"):
        out["b2_assoc"] = b2(dump)
    if kind == "breadth":
        out["b3_breadth_noop"] = b3(dump)
    dest = sys.argv[3] if len(sys.argv) > 3 else sys.argv[1].replace(".json", "_b.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))
    print("[written]", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
