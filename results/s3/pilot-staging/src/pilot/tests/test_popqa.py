import json
import random

from src.pilot.popqa import (FLOOR, MASK, build_items, loo_frequency_pick,
                             masked_question, object_counts, pairs_of,
                             quartile_edges, quartile_of, score_item)

PROPS = {"occupation": ["actor", "singer", "politician", "painter", "poet",
                        "farmer", "lawyer", "monk", "baker"],
         "country": ["France", "Peru", "Chad", "Laos", "Fiji", "Oman", "Mali",
                     "Iran"],
         "sport": ["association football", "tennis", "golf", "rugby", "polo",
                   "chess", "curling", "judo"]}


def _rows(n=1600, seed=0):
    """Rows whose gold objects are skewed the way PopQA's are: the first
    object of each relation is the gold far more often than the rest."""
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        prop = rng.choice(sorted(PROPS))
        objs = PROPS[prop]
        weights = [2.0 ** -k for k in range(len(objs))]
        obj = rng.choices(objs, weights)[0]
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


def test_a_question_free_frequency_reader_sits_at_the_floor():
    rows = _rows()
    counts = object_counts(rows)
    # On skewed golds, distractors drawn uniformly from the distinct objects
    # let the commonest-object reader far above 0.25; rank balance holds it
    # to a quarter in every band.
    items = build_items(rows, n=200, seed=3)
    hits = [loo_frequency_pick(it, counts) == it["gold_index"] for it in items]
    assert abs(sum(hits) / len(hits) - 0.25) <= 0.02
    for q in (1, 2, 3, 4):
        band = [h for h, it in zip(hits, items) if it["quartile"] == q]
        assert abs(sum(band) / len(band) - 0.25) <= 0.04
    ranks = [it["gold_frequency_rank"] for it in items]
    assert sorted(set(ranks)) == [0, 1, 2, 3]


def test_masked_question_replaces_the_subject_once():
    row = {"subj": "Paris", "question": "What is Paris the capital of?"}
    assert masked_question(row) == f"What is {MASK} the capital of?"
    assert masked_question({"subj": "e", "question": "Who was the producer of e?"}) \
        is None
    assert masked_question({"subj": "Bo", "question": "Is Bo Bo?"}) is None
    items = build_items(_rows(), n=40, seed=4)
    for it in items:
        assert it["masked_question"].startswith("What is X's")
        assert pairs_of(it, masked=True)[0][0] == f"Q: {it['masked_question']}\nA:"


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
    assert "correct_masked" not in s
    assert len(pairs_of(item)) == 4
    assert pairs_of(item)[1] == ("Q: Q?\nA:", " e")
    m = score_item(item, stats, [(9.0, 4), (1.0, 1), (9.0, 2), (9.0, 2)])
    assert m["pick_masked"] == 1 and not m["correct_masked"]
