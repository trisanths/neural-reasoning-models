"""Tests for the fact scrubber, toolkit item 4."""

import re
import time

from src.scrub import scrub_document
from src.scrub.common_words import COMMON_WORDS

DOC = "We adore Paris. Paris has charm. They left Paris quickly."


def test_determinism_per_seed():
    a = scrub_document(DOC, 7)
    b = scrub_document(DOC, 7)
    assert a == b
    c = scrub_document(DOC, 8)
    assert c != a


def test_within_document_consistency():
    out = scrub_document(DOC, 3)
    assert "Paris" not in out
    words = re.findall(r"\b[A-Z][a-z]+\b", out)
    reps = [w for w in words if w not in {"We", "They"}]
    assert len(reps) == 3
    assert len(set(reps)) == 1


def test_across_document_inconsistency():
    d1 = "We adore Paris today."
    d2 = "They left Paris behind."
    o1 = scrub_document(d1, 5)
    o2 = scrub_document(d2, 5)
    assert "Paris" not in o1
    assert "Paris" not in o2
    r1 = [w for w in re.findall(r"\b[A-Z][a-z]+\b", o1) if w != "We"]
    r2 = [w for w in re.findall(r"\b[A-Z][a-z]+\b", o2) if w != "They"]
    assert len(r1) == 1 and len(r2) == 1
    assert r1[0] != r2[0]


def test_capitalization_shape():
    out = scrub_document(
        "The rocket from NASA reached orbit near Paris today.", 11)
    assert "NASA" not in out
    assert "Paris" not in out
    toks = re.findall(r"[A-Za-z]+", out)
    allcaps = [w for w in toks if w.isupper() and len(w) >= 2]
    assert len(allcaps) == 1
    assert 2 <= len(allcaps[0]) <= 8
    titled = [w for w in toks
              if w.istitle() and w not in {"The", "Paris"}]
    assert len(titled) == 1
    assert 3 <= len(titled[0]) <= 8


def test_number_perturbation():
    out = scrub_document(
        "There were 4500 birds in 1987 and 12 dogs and 7 cats.", 2)
    nums = re.findall(r"\d+", out)
    assert sorted(len(n) for n in nums) == [1, 2, 4, 4]
    assert "7" in nums
    assert "4500" not in nums
    assert "1987" not in nums
    assert "12" not in nums
    four = [int(n) for n in nums if len(n) == 4]
    # 1987 stays year shaped, 4500 stays in its magnitude class.
    assert any(1000 <= v <= 2199 for v in four)
    assert any(v > 2400 for v in four)


def test_common_word_preservation():
    assert len(COMMON_WORDS) == 200
    assert len(set(COMMON_WORDS)) == 200
    assert all(w == w.lower() for w in COMMON_WORDS)
    text = " ".join(COMMON_WORDS)
    assert scrub_document(text, 1) == text


def test_common_words_in_context():
    out = scrub_document(
        "The people will make time to work in Paris today.", 9)
    for w in ["people", "make", "time", "work", "today"]:
        assert w in out
    assert "Paris" not in out


def test_sentence_start_word_kept_unless_seen_mid_sentence():
    out = scrub_document("Green is a color. Green looks calm.", 6)
    assert "Green" in out
    out2 = scrub_document("Paris is large. We adore Paris.", 6)
    assert "Paris" not in out2


def test_honorific_and_corporate_suffix():
    out = scrub_document("Dr. Smith arrived late.", 6)
    assert "Smith" not in out
    out2 = scrub_document("Acme Corp posted results.", 6)
    assert "Acme" not in out2


def test_url_email_handle():
    out = scrub_document(
        "Visit https://example.com/page now, mail bob@test.org, "
        "ping @bobby.", 4)
    assert "example.com" not in out
    assert "bob@test.org" not in out
    assert "@bobby" not in out


def test_throughput_smoke():
    para = (
        "The committee met in Vienna on 14 March 1988 to review the "
        "annual budget of 4500 dollars. Local officials said the plan "
        "would help schools and families across the region. Dr. Halden "
        "of the Meridian Group argued that the numbers were too low, "
        "while others wanted more time to study the report. In the end "
        "the vote passed by 52 votes, and work began the next morning. ")
    text = para * 2500
    t0 = time.perf_counter()
    scrub_document(text, 0)
    dt = time.perf_counter() - t0
    words = len(text.split())
    rate = words / dt
    # Real throughput is measured on FineWeb text by scrub_leakage.py.
    # This floor only guards against a slow regression.
    assert rate > 300_000, f"scrub rate {rate:.0f} words/s"
