import random

import pytest

from src.scrub.web_retrieval import (DOMAIN, build_web_episode,
                                     render_web_episode, verify_web_episode)
from src.train.retrieval import BM25Index, terms
from src.train.tokenizer import train_tokenizer

# Each bundle document carries distinctive entity and number spans plus a
# shared topic phrase, so BM25 can separate documents while bridges for
# two-hop plans exist.
SUBJECTS = ["Varek", "Domel", "Kastor", "Lomira", "Petrin", "Solvag",
            "Tibran", "Quorel", "Mirand", "Helvet", "Norvik", "Ostrel",
            "Palver", "Rukan", "Sellim", "Tarvod"]
PLACES = ["Trelso", "Umbrav", "Vintor", "Wellac", "Xandor", "Yorvel",
          "Zelmat", "Arkano", "Brontel", "Cervak", "Drovin", "Elbram",
          "Fornt", "Grellon", "Hastel", "Ivrock"]


# Cargo pairs shared by every fourth document: two informative terms in
# each first sentence, so two-hop bridges exist between same-cargo docs.
CARGO = [("amber", "resin"), ("basalt", "gravel"), ("cobalt", "ingots"),
         ("verdant", "timber")]


def make_bundle(n=14, seed=3):
    rng = random.Random(seed)
    docs = []
    for i in range(n):
        subject = f"{SUBJECTS[i]} {PLACES[(i + 5) % len(PLACES)]}or"
        place = PLACES[i]
        c1, c2 = CARGO[i % len(CARGO)]
        year = 1900 + 7 * i + rng.randint(0, 4)
        crates = 100 + 13 * i + rng.randint(0, 6)
        docs.append(
            f"{subject} shipped {crates} crates of {c1} {c2} to "
            f"{place}ia in {year}. The harbor ledger listed the cargo "
            f"beside the customs desk. A clerk from {place}ia counted "
            f"every crate at the gate.")
    return docs


@pytest.fixture(scope="module")
def tok(tmp_path_factory):
    base = tmp_path_factory.mktemp("webretcorpus")
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for doc in make_bundle(16, seed=9):
            fh.write(doc + "\n")
        fh.write("what who when where how many domain scrubbed web\n" * 50)
    return train_tokenizer([str(corpus)], vocab_size=512)


def test_build_deterministic():
    docs = make_bundle()
    a = build_web_episode(docs, (7, 1))
    b = build_web_episode(docs, (7, 1))
    c = build_web_episode(docs, (7, 2))
    assert a == b
    assert a != c


def test_episode_contracts_hold():
    docs = make_bundle()
    episode = build_web_episode(docs, (7, 1), n_questions=4)
    assert episode["world"]["domain"] == DOMAIN
    assert episode["questions"]
    assert verify_web_episode(episode) == []
    for question in episode["questions"]:
        final = question["plan"][-1][1]
        assert question["answer"] in docs[final]
        assert final >= episode["n_context"]


def test_no_clairvoyance_explicit():
    docs = make_bundle()
    episode = build_web_episode(docs, (7, 4), n_questions=4,
                                two_hop_share=1.0)
    for question in episode["questions"]:
        available = set(terms(question["text"]))
        for query, doc_idx in question["plan"]:
            assert set(terms(query)) <= available
            available |= set(terms(docs[doc_idx]))


def test_two_hop_plans_appear_and_verify():
    docs = make_bundle()
    hops = []
    for s in range(6):
        episode = build_web_episode(docs, (11, s), n_questions=4,
                                    two_hop_share=1.0)
        assert verify_web_episode(episode) == []
        hops.extend(len(q["plan"]) for q in episode["questions"])
    assert any(h == 2 for h in hops)
    assert all(1 <= h <= 2 for h in hops)


def test_query_verifies_top1_under_fresh_index():
    docs = make_bundle()
    episode = build_web_episode(docs, (7, 1), n_questions=4)
    index = BM25Index(docs)
    for question in episode["questions"]:
        served = set()
        for query, doc_idx in question["plan"]:
            assert index.top(query, exclude=served) == doc_idx
            served.add(doc_idx)


def test_query_first_renders_without_context_docs(tok):
    docs = make_bundle()
    episode = build_web_episode(docs, (7, 1), query_first=True)
    assert episode["n_context"] == 0
    assert episode["questions"]
    tokens = render_web_episode(episode, tok)
    sid = tok.special_ids
    first_q = tokens.index(sid["<|q|>"])
    assert sid["<|doc|>"] not in tokens[:first_q]
    assert sid["<|retrieve|>"] in tokens
    assert sid["<|result|>"] in tokens


def test_context_render_layout_and_round_trip(tok):
    docs = make_bundle()
    episode = build_web_episode(docs, (7, 1), n_context=3)
    assert episode["n_context"] == 3
    tokens = render_web_episode(episode, tok)
    sid = tok.special_ids
    first_q = tokens.index(sid["<|q|>"])
    assert tokens[:first_q].count(sid["<|doc|>"]) == 3
    text = tok.decode(tokens)
    assert text.startswith(f"<|world|>domain: {DOMAIN}")
    for block in text.split("<|q|>")[1:]:
        answer = block.partition("<|a|>")[2].partition("<|eot|>")[0]
        last_result = block.rpartition("<|result|>")[2]
        assert answer in last_result


def test_dropped_questions_counted():
    # A bundle of two near-identical documents cannot verify top-1
    # queries for both targets, so drops are counted rather than hidden.
    docs = ["The clerk counted the crates near the gate all day.",
            "The clerk counted the crates near the gate all night."]
    episode = build_web_episode(docs, (1, 1), n_questions=4, n_context=0)
    stats = episode["stats"]
    assert stats["questions"] + stats["dropped"] >= 1
    assert verify_web_episode(episode) == []


def test_small_bundle_rejected():
    with pytest.raises(ValueError):
        build_web_episode(["only one document"], 3)
