import json
import random

from src.pilot.popqa import (FLOOR, build_items, pairs_of, quartile_edges,
                             quartile_of, score_item)


def _rows(n=400, seed=0):
    rng = random.Random(seed)
    props = {"occupation": ["actor", "singer", "politician", "painter", "poet",
                            "farmer", "lawyer"],
             "country": ["France", "Peru", "Chad", "Laos", "Fiji", "Oman"],
             "genre": ["jazz", "punk", "opera", "folk", "techno"]}
    rows = []
    for i in range(n):
        prop = rng.choice(sorted(props))
        obj = rng.choice(props[prop])
        rows.append({"id": i, "subj": f"Subj{i}", "prop": prop, "obj": obj,
                     "question": f"What is Subj{i}'s {prop}?",
                     "possible_answers": json.dumps([obj, obj.upper()]),
                     "o_aliases": "[]", "s_pop": rng.randint(1, 100000)})
    return rows


def test_items_are_stratified_and_distractors_share_the_relation():
    rows = _rows()
    items = build_items(rows, n=100, seed=1)
    assert len(items) == 100
    assert sorted({it["quartile"] for it in items}) == [1, 2, 3, 4]
    for q in (1, 2, 3, 4):
        assert sum(it["quartile"] == q for it in items) == 25
    by_id = {r["id"]: r for r in rows}
    pools = {}
    for r in rows:
        pools.setdefault(r["prop"], set()).add(r["obj"])
    for it in items:
        r = by_id[int(it["item_id"].split("-")[1])]
        assert it["options"][it["gold_index"]] == r["obj"]
        assert len(set(o.lower() for o in it["options"])) == 4
        for k, o in enumerate(it["options"]):
            assert o in pools[r["prop"]]
            if k != it["gold_index"]:
                assert o.lower() != r["obj"].lower()
        assert it["floor"] == FLOOR == 0.25


def test_gold_position_is_spread_by_the_shuffle():
    items = build_items(_rows(), n=100, seed=2)
    counts = [sum(it["gold_index"] == k for it in items) for k in range(4)]
    assert min(counts) > 10


def test_quartiles_split_evenly():
    pops = list(range(100))
    edges = quartile_edges(pops)
    assert [sum(quartile_of(p, edges) == q for p in pops) for q in (1, 2, 3, 4)] \
        == [25, 25, 25, 25]


def test_scoring_is_length_normalised_and_records_the_old_rule():
    item = {"item_id": "popqa-1", "question": "Q?",
            "options": ["a b c d", "e", "f g", "h i"], "gold_index": 0}
    stats = [(4.0, 4), (2.0, 1), (3.0, 2), (2.4, 2)]
    s = score_item(item, stats)
    assert s["pick"] == 0 and s["correct"]
    assert s["pick_summed_nll"] == 1 and not s["correct_summed_nll"]
    assert len(pairs_of(item)) == 4
    assert pairs_of(item)[1] == ("Q: Q?\nA:", " e")
