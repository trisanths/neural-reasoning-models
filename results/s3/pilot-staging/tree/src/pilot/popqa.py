"""PopQA as a four-way forced choice, for measuring how much entity knowledge a model holds.

PopQA (akariasai/PopQA, 14,267 questions) asks for one object of one Wikidata
relation about one subject, with the subject's Wikipedia page views (s_pop)
as a popularity score. Free generation on it is graded by containment of any
alias, which is the grader shape DISCOVERY.md bans. So each question becomes
a forced choice instead:

  gold         the item's object label (obj)
  distractors  three objects of other questions with the same relation
               (prop), so every option has the right type, none matching any
               alias of the gold (possible_answers or o_aliases, compared
               lower-cased) and all distinct
  sampling     1,000 items, 250 from each quartile of s_pop over the whole
               dataset, so the score can be read per popularity band
  order        options shuffled per item with a seeded RNG; gold_index is
               the gold's position after the shuffle

Scoring is by likelihood: the context is "Q: <question>\\nA:", each option is
" <option>", and the winner is chosen by src/evals/mc.choose with
length-normalised NLL and a per-item seeded tie break. The floor is 0.25 for
every item. The same context works for base and instruct models because
nothing is generated.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict

from src.evals.mc import choose

N_ITEMS = 1000
N_OPTIONS = 4
FLOOR = 1.0 / N_OPTIONS
SEED = 20261005


def _aliases(row: dict) -> set[str]:
    out = {row["obj"].strip().lower()}
    for key in ("possible_answers", "o_aliases"):
        val = row.get(key)
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except json.JSONDecodeError:
                val = [val]
        for a in val or []:
            if isinstance(a, str) and a.strip():
                out.add(a.strip().lower())
    return out


def quartile_edges(pops: list[float]) -> list[float]:
    s = sorted(pops)
    n = len(s)
    return [s[(n * q) // 4] for q in (1, 2, 3)]


def quartile_of(pop: float, edges: list[float]) -> int:
    for i, e in enumerate(edges):
        if pop < e:
            return i + 1
    return 4


def build_items(rows: list[dict], n: int = N_ITEMS, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    edges = quartile_edges([r["s_pop"] for r in rows])
    by_prop: dict = defaultdict(list)
    for r in rows:
        by_prop[r["prop"]].append(r["obj"].strip())
    pools = {p: sorted(set(v)) for p, v in by_prop.items()}

    bands: dict = defaultdict(list)
    for r in rows:
        bands[quartile_of(r["s_pop"], edges)].append(r)
    per_band = n // 4
    items = []
    for q in (1, 2, 3, 4):
        band = sorted(bands[q], key=lambda r: r["id"])
        rng.shuffle(band)
        took = 0
        for r in band:
            if took >= per_band:
                break
            gold = r["obj"].strip()
            if not gold or gold.lower() in r["question"].lower():
                continue
            bad = _aliases(r)
            pool = [o for o in pools[r["prop"]] if o.lower() not in bad]
            if len(pool) < N_OPTIONS - 1:
                continue
            distractors: list[str] = []
            for o in rng.sample(pool, min(len(pool), 12)):
                if o.lower() not in {d.lower() for d in distractors}:
                    distractors.append(o)
                if len(distractors) == N_OPTIONS - 1:
                    break
            if len(distractors) < N_OPTIONS - 1:
                continue
            options = [gold] + distractors
            rng.shuffle(options)
            items.append({
                "item_id": f"popqa-{r['id']}",
                "question": r["question"],
                "options": options,
                "gold_index": options.index(gold),
                "gold": gold,
                "prop": r["prop"],
                "s_pop": r["s_pop"],
                "quartile": q,
                "floor": FLOOR,
            })
            took += 1
        if took < per_band:
            raise RuntimeError(f"quartile {q}: only {took} usable items")
    return items


def context_of(item: dict) -> str:
    return f"Q: {item['question']}\nA:"


def pairs_of(item: dict) -> list[tuple[str, str]]:
    ctx = context_of(item)
    return [(ctx, " " + o) for o in item["options"]]


def item_rng(item: dict) -> random.Random:
    return random.Random(f"popqa-fc:{item['item_id']}")


def score_item(item: dict, stats: list[tuple[float, int]]) -> dict:
    """Pick an option from (summed NLL, n tokens) per option."""
    sums = [s for s, _ in stats]
    counts = [n for _, n in stats]
    pick = choose(sums, counts, rng=item_rng(item), normalize=True)
    legacy = choose(sums, counts, legacy=True)
    return {"pick": pick, "correct": pick == item["gold_index"],
            "pick_summed_nll": legacy,
            "correct_summed_nll": legacy == item["gold_index"],
            "nll_sums": sums, "n_tokens": counts}


def main(argv=None) -> int:
    import argparse
    import os

    ap = argparse.ArgumentParser(description="build the PopQA forced-choice set")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=N_ITEMS)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args(argv)
    from datasets import load_dataset

    rows = [dict(r) for r in load_dataset("akariasai/PopQA", split="test")]
    items = build_items(rows, n=args.n, seed=args.seed)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as fh:
        for it in items:
            fh.write(json.dumps(it, sort_keys=True) + "\n")
    edges = quartile_edges([r["s_pop"] for r in rows])
    print(json.dumps({"n": len(items), "rows": len(rows), "s_pop_edges": edges,
                      "props": len({i["prop"] for i in items})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
