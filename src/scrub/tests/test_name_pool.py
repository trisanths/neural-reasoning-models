import numpy as np
import pytest

from src.scrub.name_pool import (EntityPool, harvest_counts, harvest_pool,
                                 pool_from_counts)
from src.scrub.scrubber import scrub_text

# A small corpus with recurring real-style names. Every name appears
# mid-sentence somewhere, so the detector treats sentence-initial
# mentions as entities too.
NAMES = ["Einstein", "Paris", "Curie", "Lisbon", "Newton", "Vienna",
         "Berlin", "Tesla", "Bohr", "Kyiv", "Osaka", "Dublin",
         "Geneva", "Turin", "Prague"]
PAIR_NAMES = ["Marie Curie", "Isaac Newton", "Nikola Tesla",
              "Niels Bohr", "Albert Einstein"]


def make_corpus(n_docs=40):
    docs = []
    for d in range(n_docs):
        sents = []
        for i in range(6):
            a = NAMES[(d + i) % len(NAMES)]
            b = NAMES[(d + i + 3) % len(NAMES)]
            p = PAIR_NAMES[(d + i) % len(PAIR_NAMES)]
            sents.append(
                f"The ledger shows {a} met {p} near {b} on a cold day.")
        docs.append(" ".join(sents))
    return docs


def test_harvest_deterministic_and_frequency_ordered():
    docs = make_corpus()
    a = harvest_pool(docs)
    b = harvest_pool(docs)
    assert a.forms == b.forms
    counts = harvest_counts(docs)
    top = a.forms[0]
    assert counts[top] == max(counts.values())
    for name in NAMES:
        assert name in a.forms
    for name in PAIR_NAMES:
        assert name in a.forms


def test_min_count_filter_and_fallback():
    counts = harvest_counts(
        ["The clerk saw Boron twice, and Boron met Alba once."])
    # Boron appears twice, Alba once; min_count 2 alone leaves a single
    # distinct form, so the floor drops to keep the pool usable.
    assert counts == {"Boron": 2, "Alba": 1}
    pool = pool_from_counts(counts, min_count=2)
    assert set(pool.forms) == {"Alba", "Boron"}


def test_pick_matches_word_count_and_never_identity():
    pool = harvest_pool(make_corpus())
    rng = np.random.default_rng(0)
    for _ in range(50):
        single = pool.pick("Einstein", rng)
        assert " " not in single
        assert single.lower() != "einstein"
        double = pool.pick("Marie Curie", rng)
        assert len(double.split()) == 2
        assert double.lower() != "marie curie"


def test_shuffle_consistent_within_document():
    pool = harvest_pool(make_corpus())
    doc = ("Einstein wrote the first memo. Later Einstein signed it, "
           "and the clerk mailed it to Einstein directly.")
    res = scrub_text(doc, 11, entity_policy="shuffle", pool=pool)
    replacement = res.replacements["einstein"]
    assert replacement in pool.forms
    assert res.text.count(replacement) == 3
    assert "Einstein" not in res.text or replacement == "Einstein"


def test_shuffle_caps_shape_preserved():
    pool = harvest_pool(make_corpus())
    doc = "The reactor at NASA failed while NASA slept."
    res = scrub_text(doc, 11, entity_policy="shuffle", pool=pool)
    replacement = res.replacements["nasa"]
    assert replacement.isupper()
    assert replacement != "NASA"


def test_shuffle_differs_across_documents():
    pool = harvest_pool(make_corpus())
    frames = [
        "The clerk asked Einstein to file the {} report.",
        "The auditors praised Einstein for the {} ledger.",
        "Nobody expected Einstein to sign the {} order.",
        "A letter from Einstein reached the {} office.",
    ]
    picks = set()
    for i, frame in enumerate(frames):
        res = scrub_text(frame.format(i), 11, entity_policy="shuffle",
                         pool=pool)
        picks.add(res.replacements["einstein"])
    assert len(picks) > 1


def test_shuffle_deterministic():
    pool = harvest_pool(make_corpus())
    doc = "Curie and Newton argued in Vienna about the Lisbon ledger."
    a = scrub_text(doc, 5, entity_policy="shuffle", pool=pool)
    b = scrub_text(doc, 5, entity_policy="shuffle", pool=pool)
    c = scrub_text(doc, 6, entity_policy="shuffle", pool=pool)
    assert a.text == b.text and a.spans == b.spans
    assert c.text != a.text


def test_pool_coverage_of_frequent_names():
    """Frequent real names come back as replacements: scrub the corpus
    with its own pool and most of the top forms appear in the output."""
    docs = make_corpus()
    pool = harvest_pool(docs)
    out = " ".join(
        scrub_text(d, (3, i), entity_policy="shuffle", pool=pool).text
        for i, d in enumerate(docs))
    top = pool.forms[:10]
    covered = sum(1 for f in top if f in out)
    assert covered >= 7


def test_invent_default_unchanged():
    doc = "Curie and Newton argued in Vienna about the Lisbon ledger."
    assert scrub_text(doc, 5).text == scrub_text(
        doc, 5, entity_policy="invent").text


def test_shuffle_requires_pool_and_policy_validated():
    with pytest.raises(ValueError):
        scrub_text("Einstein slept.", 1, entity_policy="shuffle")
    with pytest.raises(ValueError):
        scrub_text("Einstein slept.", 1, entity_policy="bogus")
    with pytest.raises(ValueError):
        EntityPool(["Solo"])
