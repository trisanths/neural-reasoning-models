import json
import random

import pytest

from src.train.data import ShardReader
from src.train.retrieval import (
    BM25Index,
    plan_episode_traces,
    plan_question_trace,
    render_episode_retrieval,
    render_jsonl_to_shards_retrieval,
    terms,
)
from src.train.tokenizer import load_tokenizer, train_tokenizer
from src.worldgen.engine import generate_episodes


@pytest.fixture(scope="module")
def tok(tmp_path_factory):
    base = tmp_path_factory.mktemp("retrievalcorpus")
    rng = random.Random(7)
    words = [
        "lomera", "vantrix", "korath", "acquired", "shipped", "company",
        "officer", "route", "the", "of", "reports", "that", "cargo", "who",
        "ultimately", "which", "quarter", "third", "fourth", "in",
    ]
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1500):
            fh.write(" ".join(rng.choices(words, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return load_tokenizer(str(path))


def make_episode():
    """Two-hop acquisition chain plus a filler document."""
    docs = [
        ("the officer reports that cargo shipped on the route", []),
        ("lomera acquired vantrix in the third quarter", ["f1"]),
        ("korath acquired lomera in the fourth quarter", ["f2"]),
    ]
    return {
        "episode_id": "ep-000000",
        "seed": 1,
        "world": {
            "domain": "corporate",
            "entities": [
                {"id": "e1", "type": "company", "name": "Lomera"},
                {"id": "e2", "type": "company", "name": "Vantrix"},
                {"id": "e3", "type": "company", "name": "Korath"},
            ],
            "rules": ["acquisition transfers subsidiaries"],
            "facts": [
                {"id": "f1", "s": "e1", "p": "acquired", "o": "e2", "t": 3},
                {"id": "f2", "s": "e3", "p": "acquired", "o": "e1", "t": 4},
            ],
        },
        "documents": [
            {
                "doc_id": f"d{i + 1}",
                "text": text,
                "reliability": 0.9,
                "style": "filing",
                "supports": supports,
                "contradicts": [],
            }
            for i, (text, supports) in enumerate(docs)
        ],
        "questions": [
            {
                "qid": "q1",
                "text": "who acquired vantrix",
                "answer": "lomera",
                "type": "lookup",
                "derivation": ["f1"],
                "hops": 1,
            },
            {
                "qid": "q2",
                "text": "which company ultimately acquired vantrix",
                "answer": "korath",
                "type": "multi_hop",
                "derivation": ["f1", "f2"],
                "hops": 2,
            },
        ],
    }


def episode_index(episode):
    return BM25Index([d["text"] for d in episode["documents"]])


def test_terms_are_deterministic():
    assert terms("Who Acquired Vantrix?") == ["who", "acquired", "vantrix"]


def test_bm25_ranks_matching_document_first():
    docs = [d["text"] for d in make_episode()["documents"]]
    index = BM25Index(docs)
    assert index.top("who acquired vantrix") == 1
    assert index.top("cargo shipped route") == 0


def test_bm25_tie_breaks_toward_earliest():
    index = BM25Index(["alpha beta", "alpha beta"])
    assert index.top("alpha") == 0


def test_bm25_exclude_skips_documents():
    index = BM25Index(["alpha beta", "alpha beta", "gamma"])
    assert index.top("alpha", exclude={0}) == 1
    assert index.top("alpha", exclude={0, 1}) == 2


def test_plan_single_hop():
    episode = make_episode()
    plan = plan_question_trace(
        episode["questions"][0], episode["documents"], episode_index(episode))
    assert plan is not None and len(plan) == 1
    query, target = plan[0]
    assert target == 1
    assert set(terms(query)) <= set(terms("who acquired vantrix"))


def test_plan_multi_hop_no_clairvoyance_and_exclusion():
    episode = make_episode()
    question = episode["questions"][1]
    plan = plan_question_trace(
        question, episode["documents"], episode_index(episode))
    assert plan is not None and len(plan) == 2
    assert [t for _, t in plan] == [1, 2]
    available = set(terms(question["text"]))
    seen_targets = set()
    for k, (query, target) in enumerate(plan):
        # Containment: hop k uses only question terms and terms from the
        # chunks earlier hops returned.
        assert set(terms(query)) <= available
        assert target not in seen_targets
        seen_targets.add(target)
        available |= set(terms(episode["documents"][target]["text"]))


def test_plan_verifies_under_real_retriever():
    episode = make_episode()
    index = episode_index(episode)
    for question in episode["questions"]:
        plan = plan_question_trace(question, episode["documents"], index)
        exclude = set()
        for (query, target), fid in zip(plan, question["derivation"]):
            assert fid in episode["documents"][target]["supports"]
            assert index.top(query, exclude) == target
            exclude.add(target)


def test_unreachable_hop_drops_question():
    episode = make_episode()
    episode["questions"].append({
        "qid": "q3",
        "text": "zzz qqq",
        "answer": "nobody",
        "type": "lookup",
        "derivation": ["f2"],
        "hops": 1,
    })
    plans, stats = plan_episode_traces(episode)
    assert plans[2] is None
    assert stats["dropped"] == 1
    assert stats["rendered"] == 2


def test_empty_derivation_renders_zero_rounds(tok):
    episode = make_episode()
    episode["questions"] = [{
        "qid": "q1",
        "text": "who shipped cargo",
        "answer": "no",
        "type": "yes_no",
        "derivation": [],
        "hops": 1,
    }]
    plans, stats = plan_episode_traces(episode)
    assert plans == [[]]
    assert stats["no_derivation"] == 1
    ids = render_episode_retrieval(episode, tok)
    sid = tok.special_ids
    assert ids.count(sid["<|retrieve|>"]) == 0
    assert ids.count(sid["<|result|>"]) == 0
    assert ids.count(sid["<|q|>"]) == 1
    assert ids[-1] == sid["<|eot|>"]


def test_retrieval_trace_structure_multi_hop(tok):
    episode = make_episode()
    ids = render_episode_retrieval(episode, tok)
    sid = tok.special_ids
    # One round for q1 plus two rounds for q2.
    assert ids.count(sid["<|q|>"]) == 2
    assert ids.count(sid["<|retrieve|>"]) == 3
    assert ids.count(sid["<|result|>"]) == 3
    assert ids.count(sid["<|a|>"]) == 2
    assert ids[-1] == sid["<|eot|>"]

    # The second trace's spans encode the planned queries and chunks in order.
    plans, _ = plan_episode_traces(episode)
    q_positions = [i for i, t in enumerate(ids) if t == sid["<|q|>"]]
    trace = ids[q_positions[1]:]
    r_pos = [i for i, t in enumerate(trace) if t == sid["<|retrieve|>"]]
    res_pos = [i for i, t in enumerate(trace) if t == sid["<|result|>"]]
    a_pos = trace.index(sid["<|a|>"])
    for k, (query, target) in enumerate(plans[1]):
        assert trace[r_pos[k] + 1:res_pos[k]] == tok.encode(query)
        next_stop = r_pos[k + 1] if k + 1 < len(r_pos) else a_pos
        chunk = episode["documents"][target]["text"]
        assert trace[res_pos[k] + 1:next_stop] == tok.encode(chunk)


def test_retrieval_reaches_past_doc_budget(tok):
    episode = make_episode()
    # A budget of zero keeps every document out of the context.
    ids = render_episode_retrieval(episode, tok, max_doc_tokens=0)
    sid = tok.special_ids
    assert ids.count(sid["<|doc|>"]) == 0
    assert ids.count(sid["<|result|>"]) == 3


def test_no_clairvoyance_on_generated_episodes():
    episodes = list(generate_episodes(123, 8))
    checked = 0
    for episode in episodes:
        documents = episode["documents"]
        index = BM25Index([d["text"] for d in documents])
        for question in episode["questions"]:
            plan = plan_question_trace(question, documents, index)
            if plan is None:
                continue
            available = set(terms(question["text"]))
            exclude = set()
            for (query, target), fid in zip(plan, question["derivation"]):
                assert set(terms(query)) <= available
                assert fid in documents[target]["supports"]
                assert index.top(query, exclude) == target
                exclude.add(target)
                available |= set(terms(documents[target]["text"]))
                checked += 1
    assert checked > 0


def test_hit_rate_on_generated_episodes():
    totals = {"questions": 0, "rendered": 0, "dropped": 0,
              "no_derivation": 0, "hops": 0}
    for episode in generate_episodes(20260824, 40):
        _, stats = plan_episode_traces(episode)
        for key in totals:
            totals[key] += stats[key]
    with_deriv = totals["questions"] - totals["no_derivation"]
    supported = totals["rendered"] - totals["no_derivation"]
    assert with_deriv > 100
    assert supported / with_deriv >= 0.85


def test_render_jsonl_to_shards_retrieval(tok, tmp_path):
    jsonl = tmp_path / "episodes.jsonl"
    with open(jsonl, "w") as fh:
        for _ in range(3):
            fh.write(json.dumps(make_episode()) + "\n")
    out = tmp_path / "shards"
    total = render_jsonl_to_shards_retrieval(str(jsonl), tok, out, shard_size=256)
    reader = ShardReader(out)
    assert reader.total_tokens == total
    assert total == 3 * len(render_episode_retrieval(make_episode(), tok))
