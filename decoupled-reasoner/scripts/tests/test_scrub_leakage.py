from collections import Counter

from scripts.scrub_leakage import (cooccurring_pairs, form_coverage,
                                   pair_survival)
from src.scrub.name_pool import harvest_counts, pool_from_counts
from src.scrub.scrubber import scrub_document

# Multiword names paired within documents, so raw entity pairs exist.
# The name space is wide enough that chance reassignment under the
# shuffle policy cannot recreate most raw pairs.
FIRST = ["Marie", "Albert", "Isaac", "Nikola", "Niels", "Rosa", "Emmy",
         "Clara", "Viktor", "Selma", "Anton", "Freya", "Bruno", "Ilse",
         "Casimir", "Dagny", "Elmar", "Greta", "Hugo", "Ingrid", "Joris",
         "Karla", "Ludvig", "Mirela"]
NAMES = [f"{FIRST[i]} {FIRST[(i + 7) % 24]}sen" for i in range(24)]


def make_docs(n=40):
    docs = []
    for d in range(n):
        a = NAMES[d % len(NAMES)]
        b = NAMES[(d + 1) % len(NAMES)]
        docs.append(
            f"The record says {a} wrote to {b} about the {d} ledger. "
            f"Later {b} joined {a} at the archive desk.")
    return docs


def name_forms(docs, k=24):
    counts = harvest_counts(docs)
    return [f for f, _ in counts.most_common() if " " in f][:k]


def test_pair_metrics_on_raw_docs():
    docs = make_docs()
    forms = name_forms(docs)
    assert set(forms) == set(NAMES)
    assert form_coverage(forms, docs) == 1.0
    pairs = cooccurring_pairs(docs, forms, max_pairs=50)
    assert pairs
    assert pair_survival(pairs, docs) == 1.0


def test_invent_policy_collapses_names_and_pairs():
    docs = make_docs()
    forms = name_forms(docs)
    pairs = cooccurring_pairs(docs, forms, max_pairs=50)
    scrubbed = [scrub_document(doc, (1, i)) for i, doc in enumerate(docs)]
    assert form_coverage(forms, scrubbed) == 0.0
    assert pair_survival(pairs, scrubbed) == 0.0


def test_shuffle_policy_keeps_name_tokens_and_breaks_pairs():
    docs = make_docs()
    counts = harvest_counts(docs)
    forms = name_forms(docs)
    pool = pool_from_counts(counts)
    scrubbed = [scrub_document(doc, (1, i), entity_policy="shuffle",
                               pool=pool) for i, doc in enumerate(docs)]
    # Real name forms keep appearing in the scrubbed output as
    # reassigned names; that is the whole point of the policy.
    assert form_coverage(forms, scrubbed) >= 0.75
    # And reassignment is per document, so raw pairings collapse far
    # below their baseline of 1.0; only chance pairings remain.
    pairs = cooccurring_pairs(docs, forms, max_pairs=50)
    assert pair_survival(pairs, scrubbed) < 0.5


def test_word_bounded_matching():
    assert form_coverage(["Ann Rose"], ["The Ann Rosetta file."]) == 0.0
    assert form_coverage(["Ann Rose"], ["We met Ann Rose today."]) == 1.0
    pairs = cooccurring_pairs(["Ann Rose spoke to Bel Marn."],
                              ["Ann Rose", "Bel Marn"])
    assert pairs == [("Ann Rose", "Bel Marn")]
    assert pair_survival(pairs, ["Ann Rosetta met Bel Marn."]) == 0.0


def test_empty_inputs():
    assert form_coverage([], ["doc"]) == 0.0
    assert pair_survival([], ["doc"]) == 0.0
    assert cooccurring_pairs(["doc"], []) == []


def test_counter_shapes():
    counts = harvest_counts(make_docs(4))
    assert isinstance(counts, Counter)
    assert all(" ".join(f.split()) == f for f in counts)
