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
               lower-cased) and all distinct, chosen so the gold's rank among
               the four by object frequency is balanced (build_items)
  sampling     1,000 items, 250 from each quartile of s_pop over the whole
               dataset, so the score can be read per popularity band, at
               most REL_CAP_PER_BAND per relation in a band
  order        options shuffled per item with a seeded RNG; gold_index is
               the gold's position after the shuffle
  masked       the question with its subject replaced by X, scored the same
               way: what the model gets from the relation and the options
               alone, printed beside the real score

Scoring is by likelihood: the context is "Q: <question>\\nA:", each option is
" <option>", and the winner is chosen by src/evals/mc.choose with
length-normalised NLL and a per-item seeded tie break. The floor is 0.25 for
every item. The same context works for base and instruct models because
nothing is generated.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict

from src.evals.mc import choose

N_ITEMS = 1000
N_OPTIONS = 4
FLOOR = 1.0 / N_OPTIONS
SEED = 20261005
MASK = "X"
REL_CAP_PER_BAND = 40


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


def masked_question(row: dict) -> str | None:
    """The question with its subject replaced by X, or None when the subject
    is not printed in it exactly once as a whole phrase."""
    subj = (row.get("subj") or "").strip()
    q = row["question"]
    if len(subj) < 2:
        return None
    hits = list(re.finditer(rf"(?<![\w]){re.escape(subj)}(?![\w])", q))
    if len(hits) != 1:
        return None
    h = hits[0]
    return q[:h.start()] + MASK + q[h.end():]


def object_counts(rows: list[dict]) -> dict:
    """How often each object is the gold of its relation, lower-cased."""
    out: dict = defaultdict(Counter)
    for r in rows:
        out[r["prop"]][r["obj"].strip().lower()] += 1
    return out


def loo_frequency_pick(item: dict, counts: dict) -> int:
    """The question-free baseline: the option that is the gold of its
    relation most often across the dataset, the item's own row left out.
    Ties go to the first option in item order."""
    c = counts[item["prop"]]
    gold = item["gold"].strip().lower()
    freq = [c.get(o.strip().lower(), 0) - (o.strip().lower() == gold)
            for o in item["options"]]
    return max(range(len(freq)), key=lambda i: (freq[i], -i))


def build_items(rows: list[dict], n: int = N_ITEMS, seed: int = SEED) -> list[dict]:
    """1,000 items, 250 per s_pop quartile, rank balanced, relations capped.

    Rank balance: the gold of an item is its relation's commonest object far
    more often than chance (most sports in PopQA are association football),
    so a reader that always picks the commonest kind of answer beats 0.25
    without knowing anything about the subject. Each item is therefore
    given a target rank r for its gold among its four options by how often
    each option is the gold of its relation (leave-one-out, ties excluded),
    with r - 1 distractors commoner than the gold and 4 - r rarer. Ranks are
    capped at a quarter of each band, so the question-free frequency
    baseline sits at 0.25 by construction. Relations are capped at
    REL_CAP_PER_BAND items per band so no relation dominates a band.
    """
    rng = random.Random(seed)
    edges = quartile_edges([r["s_pop"] for r in rows])
    counts = object_counts(rows)
    names: dict = defaultdict(dict)       # prop -> lower -> one spelling
    for r in sorted(rows, key=lambda r: r["id"]):
        names[r["prop"]].setdefault(r["obj"].strip().lower(), r["obj"].strip())

    bands: dict = defaultdict(list)
    for r in rows:
        bands[quartile_of(r["s_pop"], edges)].append(r)
    per_band = n // 4
    rank_cap = -(-per_band // N_OPTIONS)
    items = []
    for q in (1, 2, 3, 4):
        band = sorted(bands[q], key=lambda r: r["id"])
        rng.shuffle(band)
        took = 0
        rank_used: Counter = Counter()
        rel_used: Counter = Counter()
        for r in band:
            if took >= per_band:
                break
            gold = r["obj"].strip()
            if not gold or gold.lower() in r["question"].lower():
                continue
            if rel_used[r["prop"]] >= REL_CAP_PER_BAND:
                continue
            masked = masked_question(r)
            if masked is None:
                continue
            bad = _aliases(r)
            c = counts[r["prop"]]
            g_freq = c[gold.lower()] - 1
            above = sorted(o for o in names[r["prop"]]
                           if o not in bad and c[o] > g_freq)
            below = sorted(o for o in names[r["prop"]]
                           if o not in bad and c[o] < g_freq)
            feasible = [k for k in range(N_OPTIONS)
                        if len(above) >= k and len(below) >= N_OPTIONS - 1 - k
                        and rank_used[k] < rank_cap]
            if not feasible:
                continue
            low = min(rank_used[k] for k in feasible)
            k = rng.choice([k for k in feasible if rank_used[k] == low])
            picked = rng.sample(above, k) + rng.sample(below, N_OPTIONS - 1 - k)
            distractors = [names[r["prop"]][o] for o in picked]
            options = [gold] + distractors
            rng.shuffle(options)
            items.append({
                "item_id": f"popqa-{r['id']}",
                "question": r["question"],
                "masked_question": masked,
                "options": options,
                "gold_index": options.index(gold),
                "gold": gold,
                "gold_frequency_rank": k,
                "prop": r["prop"],
                "s_pop": r["s_pop"],
                "quartile": q,
                "floor": FLOOR,
            })
            rank_used[k] += 1
            rel_used[r["prop"]] += 1
            took += 1
        if took < per_band:
            raise RuntimeError(f"quartile {q}: only {took} usable items")
    return items


def context_of(item: dict, masked: bool = False) -> str:
    return f"Q: {item['masked_question'] if masked else item['question']}\nA:"


def pairs_of(item: dict, masked: bool = False) -> list[tuple[str, str]]:
    ctx = context_of(item, masked)
    return [(ctx, " " + o) for o in item["options"]]


def item_rng(item: dict) -> random.Random:
    return random.Random(f"popqa-fc:{item['item_id']}")


def score_item(item: dict, stats: list[tuple[float, int]],
               masked_stats: list[tuple[float, int]] | None = None) -> dict:
    """Pick an option from (summed NLL, n tokens) per option, and, given the
    same for the subject-masked question, the masked pick beside it."""
    sums = [s for s, _ in stats]
    counts = [n for _, n in stats]
    pick = choose(sums, counts, rng=item_rng(item), normalize=True)
    legacy = choose(sums, counts, legacy=True)
    out = {"pick": pick, "correct": pick == item["gold_index"],
           "pick_summed_nll": legacy,
           "correct_summed_nll": legacy == item["gold_index"],
           "nll_sums": sums, "n_tokens": counts}
    if masked_stats is not None:
        msums = [s for s, _ in masked_stats]
        mcounts = [n for _, n in masked_stats]
        mpick = choose(msums, mcounts, rng=random.Random(
            f"popqa-fc-masked:{item['item_id']}"), normalize=True)
        out.update({"pick_masked": mpick,
                    "correct_masked": mpick == item["gold_index"],
                    "nll_sums_masked": msums})
    return out


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
    counts = object_counts(rows)
    loo = [loo_frequency_pick(it, counts) == it["gold_index"] for it in items]
    by_q = {q: round(sum(x for x, it in zip(loo, items) if it["quartile"] == q)
                     / sum(1 for it in items if it["quartile"] == q), 3)
            for q in (1, 2, 3, 4)}
    print(json.dumps({"n": len(items), "rows": len(rows), "s_pop_edges": edges,
                      "props": dict(Counter(i["prop"] for i in items)),
                      "gold_rank": dict(Counter(i["gold_frequency_rank"]
                                                for i in items)),
                      "loo_frequency_baseline": round(sum(loo) / len(loo), 3),
                      "loo_frequency_baseline_by_quartile": by_q}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
