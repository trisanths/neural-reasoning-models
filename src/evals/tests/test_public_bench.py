"""Tests for the external comparison harness, all on scripted fake models.

No network and no HuggingFace downloads: the SQuAD loader is exercised
against a synthetic file pre seeded into its cache directory, and every
predict_fn here is a plain closure. The only real model in this file is
the tiny random checkpoint from conftest, used to smoke the direction
two adapters.
"""

import json

import pytest

from src.evals.public_bench import (
    SQUAD_V2_DEV_URL,
    chunk_passage,
    clean_generation,
    episode_passage,
    fetch_cached,
    heldout_items,
    load_squad_v2,
    make_ours_predict_fn,
    naturalized_items,
    parse_squad_v2,
    run_heldout_bench,
    run_naturalized_bench,
    run_public_qa,
    score_qa,
    subsample_items,
)


def scripted_predict(mapping, default="completely wrong"):
    """A fake model that answers by question lookup."""

    def predict_fn(passage, question):
        return mapping.get(question, default)

    return predict_fn


TOY_ITEMS = [
    {"id": "t1", "passage": "The valve opens at dawn.", "question": "When?",
     "answers": ["dawn"], "group": "a"},
    {"id": "t2", "passage": "Mara filed the report.", "question": "Who?",
     "answers": ["Mara"], "group": "a"},
    {"id": "t3", "passage": "The depot is in Girona.", "question": "Where?",
     "answers": ["Girona"], "group": "b"},
]


def test_score_qa_em_and_contains():
    preds = {"When?": "Dawn.", "Who?": "it was Mara who filed",
             "Where?": "somewhere else"}
    result = score_qa(TOY_ITEMS, scripted_predict(preds))
    assert result["n"] == 3
    assert result["em"] == pytest.approx(1 / 3, abs=1e-4)
    assert result["contains"] == pytest.approx(2 / 3, abs=1e-4)
    assert result["per_group"]["a"] == {"n": 2, "em": 0.5, "contains": 1.0}
    assert result["per_group"]["b"] == {"n": 1, "em": 0.0, "contains": 0.0}
    recs = result["predictions"]
    assert [r["id"] for r in recs] == ["t1", "t2", "t3"]
    assert recs[0]["em"] and recs[0]["contains"]
    assert not recs[1]["em"] and recs[1]["contains"]


def test_score_qa_multiple_golds_and_empty():
    items = [
        {"passage": "p", "question": "q1",
         "answers": ["the annex", "annex building"]},
        {"passage": "p", "question": "q2", "answers": []},
        {"passage": "p", "question": "q3", "answers": []},
    ]
    preds = {"q1": "Annex Building", "q2": "", "q3": "an actual guess"}
    result = score_qa(items, scripted_predict(preds))
    recs = result["predictions"]
    assert recs[0]["em"]
    assert recs[1]["em"] and recs[1]["contains"]
    assert not recs[2]["em"] and not recs[2]["contains"]


def test_score_qa_rejects_empty():
    with pytest.raises(ValueError):
        score_qa([], scripted_predict({}))


def test_score_qa_keep_predictions_off():
    preds = {"When?": "dawn"}
    result = score_qa(TOY_ITEMS[:1], scripted_predict(preds),
                      keep_predictions=False)
    assert "predictions" not in result


def test_subsample_deterministic_and_order_preserving():
    items = [{"id": i} for i in range(50)]
    a = subsample_items(items, 10, seed=7)
    b = subsample_items(items, 10, seed=7)
    c = subsample_items(items, 10, seed=8)
    assert a == b
    assert a != c
    ids = [x["id"] for x in a]
    assert ids == sorted(ids)
    assert subsample_items(items, None, seed=0) == items
    assert subsample_items(items, 99, seed=0) == items


def test_naturalized_bench_with_perfect_fake():
    items, metadata = naturalized_items()
    assert len(items) == metadata["n_items"]
    from src.evals.naturalized import load_suite

    gold = {it["question"]: it["answer"] for it in load_suite()["items"]}
    result = run_naturalized_bench(scripted_predict(gold), n_items=25, seed=3)
    assert result["suite"] == "naturalized_reading"
    assert result["n"] == 25
    assert result["em"] == 1.0
    assert result["contains"] == 1.0
    again = run_naturalized_bench(scripted_predict(gold), n_items=25, seed=3)
    assert [r["id"] for r in result["predictions"]] == \
           [r["id"] for r in again["predictions"]]


def test_naturalized_bench_with_wrong_fake():
    result = run_naturalized_bench(scripted_predict({}), n_items=10, seed=0)
    assert result["em"] == 0.0


def test_episode_passage_holds_documents(episodes):
    ep = episodes[0]
    passage = episode_passage(ep)
    assert f"domain: {ep['world']['domain']}" in passage
    for doc in ep["documents"]:
        assert doc["text"] in passage


def test_heldout_bench_with_perfect_fake(episodes):
    gold = {}
    for ep in episodes:
        for q in ep["questions"]:
            gold[q["text"]] = q["answer"]
    result = run_heldout_bench(scripted_predict(gold), episodes=episodes)
    assert result["suite"] == "heldout_worlds_in_context"
    assert result["n_episodes"] == len(episodes)
    assert result["n"] == sum(len(ep["questions"]) for ep in episodes)
    assert result["em"] == 1.0
    assert result["contains"] == 1.0
    assert result["per_group"]
    ids = [r["id"] for r in result["predictions"]]
    assert len(ids) == len(set(ids))


def test_heldout_items_group_by_question_type(episodes):
    items = heldout_items(episodes)
    types = {q["type"] for ep in episodes for q in ep["questions"]}
    assert {it["group"] for it in items} == types


SYNTH_SQUAD = {
    "version": "v2.0-synthetic",
    "data": [
        {
            "title": "Fictional_Depot",
            "paragraphs": [
                {
                    "context": "The depot in Girona opened in 1987 and "
                               "stores canned goods.",
                    "qas": [
                        {"id": "q-open", "question": "When did the depot open?",
                         "is_impossible": False,
                         "answers": [{"text": "1987", "answer_start": 25},
                                     {"text": "1987", "answer_start": 25}]},
                        {"id": "q-none", "question": "Who owns the depot?",
                         "is_impossible": True, "answers": [],
                         "plausible_answers": [{"text": "Girona",
                                                "answer_start": 13}]},
                    ],
                },
                {
                    "context": "Mara Voss inspects the depot every March.",
                    "qas": [
                        {"id": "q-who", "question": "Who inspects the depot?",
                         "is_impossible": False,
                         "answers": [{"text": "Mara Voss", "answer_start": 0},
                                     {"text": "Mara", "answer_start": 0}]},
                    ],
                },
            ],
        }
    ],
}


@pytest.fixture()
def squad_cache(tmp_path):
    """Pre seed the loader cache so no network request happens."""
    path = tmp_path / "dev-v2.0.json"
    path.write_text(json.dumps(SYNTH_SQUAD))
    return tmp_path


def test_fetch_cached_prefers_existing_file(squad_cache):
    path = fetch_cached(SQUAD_V2_DEV_URL, cache_dir=squad_cache)
    assert path == squad_cache / "dev-v2.0.json"


def test_parse_squad_v2_shapes():
    items, stats = parse_squad_v2(SYNTH_SQUAD)
    assert stats == {"n_total_qas": 3, "n_impossible": 1,
                     "include_impossible": False}
    assert [it["id"] for it in items] == ["q-open", "q-who"]
    assert items[0]["answers"] == ["1987"]
    assert items[1]["answers"] == ["Mara Voss", "Mara"]
    assert items[0]["group"] == "Fictional_Depot"
    with_imp, _ = parse_squad_v2(SYNTH_SQUAD, include_impossible=True)
    assert [it["id"] for it in with_imp] == ["q-open", "q-none", "q-who"]
    assert with_imp[1]["answers"] == []


def test_load_squad_v2_from_cache(squad_cache):
    loaded = load_squad_v2(cache_dir=squad_cache)
    assert loaded["metadata"]["dataset"] == "squad_v2"
    assert loaded["metadata"]["source_version"] == "v2.0-synthetic"
    assert len(loaded["items"]) == 2


def test_run_public_qa_with_perfect_fake(squad_cache):
    gold = {"When did the depot open?": "1987",
            "Who inspects the depot?": "Mara"}
    result = run_public_qa(scripted_predict(gold), dataset="squad_v2",
                           cache_dir=squad_cache, seed=0)
    assert result["suite"] == "public_qa"
    assert result["dataset"] == "squad_v2"
    assert result["n"] == 2
    assert result["em"] == 1.0
    assert result["metadata"]["n_impossible"] == 1


def test_run_public_qa_unknown_dataset():
    with pytest.raises(KeyError):
        run_public_qa(scripted_predict({}), dataset="nope")


def test_chunk_passage_lossless_and_bounded():
    passage = ("One two three four five. Six seven eight nine. "
               "Ten eleven twelve thirteen fourteen fifteen sixteen.")
    chunks = chunk_passage(passage, chunk_words=6)
    assert chunks == chunk_passage(passage, chunk_words=6)
    assert all(len(c.split()) <= 6 for c in chunks)
    assert " ".join(chunks).split() == passage.split()
    long_sentence = " ".join(f"w{i}" for i in range(15))
    hard = chunk_passage(long_sentence, chunk_words=4)
    assert all(len(c.split()) <= 4 for c in hard)
    assert " ".join(hard).split() == long_sentence.split()
    with pytest.raises(ValueError):
        chunk_passage(passage, chunk_words=0)


def test_clean_generation():
    assert clean_generation("<think>steps here</think>\n rome \n") == "rome"
    assert clean_generation("<think>never closes so no answer") == ""
    assert clean_generation("  first line \n second line ") == "first line"
    assert clean_generation("\n\n") == ""


def test_make_ours_predict_fn_modes(tiny_ckpt, tok):
    passage = ("The relay hums in the north shed. The clerk logs every "
               "reading at noon. Nobody visits the south shed in winter.")
    for mode in ("context", "retrieval"):
        predict_fn = make_ours_predict_fn(
            tiny_ckpt, tok, device="cpu", mode=mode, max_new_tokens=12,
            chunk_words=8, seed=0)
        meta = predict_fn.metadata
        assert meta["backend"] == "ours"
        assert meta["mode"] == mode
        assert meta["step"] == 7
        out = predict_fn(passage, "Where does the relay hum?")
        assert isinstance(out, str)
        again = predict_fn(passage, "Where does the relay hum?")
        assert out == again


def test_make_ours_predict_fn_rejects_bad_mode(tiny_ckpt, tok):
    with pytest.raises(ValueError):
        make_ours_predict_fn(tiny_ckpt, tok, device="cpu", mode="banana")
