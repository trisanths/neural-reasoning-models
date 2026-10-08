import json

import numpy as np
import pytest

from src.worldgen.domains import DOMAIN_ORDER, DOMAINS
from src.worldgen.engine import (
    episode_seed,
    generate_episodes,
    make_episode,
    validate_episode,
)


@pytest.mark.parametrize("domain", DOMAIN_ORDER)
def test_episode_matches_schema(domain):
    ep = make_episode(42, "ep-000000", domain)
    assert set(ep) == {"episode_id", "seed", "world", "documents", "questions"}
    world = ep["world"]
    assert world["domain"] == domain
    assert world["entities"] and world["rules"] and world["facts"]
    for ent in world["entities"]:
        assert set(ent) == {"id", "type", "name"}
    for fact in world["facts"]:
        assert {"id", "s", "p", "o", "t"} <= set(fact)
    for doc in ep["documents"]:
        assert {"doc_id", "text", "reliability", "style",
                "supports", "contradicts"} <= set(doc)
        assert 0.0 < doc["reliability"] <= 1.0
    for q in ep["questions"]:
        assert {"qid", "text", "answer", "type", "derivation", "hops"} <= set(q)
        assert q["hops"] >= 1


@pytest.mark.parametrize("domain", DOMAIN_ORDER)
def test_episode_validates(domain):
    ep = make_episode(7, "ep-000000", domain)
    assert validate_episode(ep) == []


@pytest.mark.parametrize("domain", DOMAIN_ORDER)
def test_same_seed_identical(domain):
    a = make_episode(123, "ep-000000", domain)
    b = make_episode(123, "ep-000000", domain)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_different_seeds_differ():
    a = make_episode(1, "ep-000000", "corporate")
    b = make_episode(2, "ep-000000", "corporate")
    assert json.dumps(a) != json.dumps(b)


def test_episode_is_json_native():
    for domain in DOMAIN_ORDER:
        ep = make_episode(99, "ep-000000", domain)
        json.dumps(ep)


def test_generate_episodes_cycles_domains():
    eps = list(generate_episodes(5, 8))
    domains = [e["world"]["domain"] for e in eps]
    assert domains == DOMAIN_ORDER * 2
    assert [e["episode_id"] for e in eps[:2]] == ["ep-000000", "ep-000001"]
    assert eps[0]["seed"] == episode_seed(5, 0)


def test_multi_hop_questions_exist():
    found = 0
    for ep in generate_episodes(11, 20):
        for q in ep["questions"]:
            if q["type"] == "multi_hop":
                assert q["hops"] >= 2
                assert len(q["derivation"]) == q["hops"]
                found += 1
    assert found > 0


def test_contradiction_rate_zero_means_no_contradictions():
    ep = make_episode(3, "ep-000000", "corporate", contradiction_rate=0.0)
    assert all(not d["contradicts"] for d in ep["documents"])


def test_contradictions_marked_and_low_reliability():
    rng = np.random.default_rng(0)
    seen = 0
    for seed in rng.integers(0, 10_000, size=10):
        ep = make_episode(int(seed), "ep-000000", "regulatory",
                          contradiction_rate=0.9)
        for doc in ep["documents"]:
            if doc["contradicts"]:
                assert not doc["supports"]
                assert doc["reliability"] < 0.5
                seen += 1
    assert seen > 0


def test_answers_use_entity_names_not_ids():
    ep = make_episode(21, "ep-000000", "corporate")
    ids = {e["id"] for e in ep["world"]["entities"]}
    for q in ep["questions"]:
        assert q["answer"] not in ids


def test_unknown_domain_rejected():
    with pytest.raises(ValueError):
        make_episode(0, "ep-000000", "astrology")


def test_all_domains_registered():
    assert set(DOMAINS) == set(DOMAIN_ORDER)
    assert len(DOMAIN_ORDER) == 4
