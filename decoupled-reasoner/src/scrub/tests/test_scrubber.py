import re

from src.scrub.common_words import COMMON_WORDS
from src.scrub.scrubber import (FUNCTION_WORDS, entity_runs, number_literals,
                                scrub_document, scrub_text)

DOC = (
    "Albert Einstein moved to Princeton in 1933. The institute paid him "
    "10,000 dollars a year, which Einstein considered too much. However, "
    "his colleague Kurt Godel arrived later from Vienna. The office of "
    "Einstein overlooked a small garden of 3.5 acres."
)


def test_entities_do_not_survive():
    out = scrub_text(DOC, 7).text
    for name in ("Albert", "Einstein", "Princeton", "Kurt", "Godel",
                 "Vienna"):
        assert name not in out


def test_function_words_survive():
    out = scrub_text(DOC, 7).text
    assert "The " in out
    assert "However, " in out
    assert " to " in out


def test_numbers_perturbed_and_format_kept():
    out = scrub_text(DOC, 7).text
    assert "1933" not in out
    assert "10,000" not in out
    assert "3.5" not in out
    years = re.findall(r"\b(1[89]\d\d|20\d\d)\b", out)
    assert years, "year stays year-like"
    assert re.search(r"\b\d{1,3},\d{3}\b", out), "comma grouping kept"
    assert re.search(r"\b\d+\.\d\b", out), "one decimal place kept"


def test_consistent_replacement_within_document():
    res = scrub_text(DOC, 7)
    replacement = res.replacements["einstein"]
    # Einstein appears alone twice after the multiword run; both occurrences
    # scrub to the same synthetic name.
    assert res.text.count(replacement) == 2


def test_deterministic_and_seed_sensitive():
    a = scrub_text(DOC, 7)
    b = scrub_text(DOC, 7)
    c = scrub_text(DOC, 8)
    assert a.text == b.text and a.spans == b.spans
    assert c.text != a.text


def test_spans_match_text():
    res = scrub_text(DOC, 7)
    assert res.spans
    kinds = {s["kind"] for s in res.spans}
    assert kinds == {"entity", "number"}
    for span in res.spans:
        assert res.text[span["start"]:span["end"]] == span["text"]


def test_possessive_and_multiword_runs():
    doc = "Marie Curie's laboratory in Paris was famous."
    out = scrub_text(doc, 3).text
    assert "Marie" not in out and "Curie" not in out and "Paris" not in out
    assert "'s laboratory in " in out


def test_replacement_capitalized_synthetic():
    res = scrub_text(DOC, 7)
    for span in res.spans:
        if span["kind"] == "entity":
            for word in span["text"].split():
                assert word[0].isupper()
                assert word.lower() not in FUNCTION_WORDS


def test_run_and_number_detection():
    doc = "Bramor Corp bought 4 sites near Lake Toma in 1988."
    runs = [doc[s:e] for s, e in entity_runs(doc)]
    assert runs == ["Bramor Corp", "Lake Toma"]
    nums = [doc[s:e] for s, e in number_literals(doc)]
    assert nums == ["4", "1988"]


def test_common_words_pass_through_unchanged():
    # The full common word list survives scrub_document verbatim, both
    # lowercase and as lone capitalized sentence starters.
    lower = " ".join(COMMON_WORDS) + "."
    assert scrub_document(lower, 5) == lower
    for word in ("Time", "People", "Company", "Report"):
        doc = f"{word} was mentioned in the note."
        assert scrub_document(doc, 5) == doc


def test_extreme_numbers_do_not_overflow():
    doc = ("The constant is 3.14159265358979323846264338327950288 and the "
           "count reached 123456789012345678901234567890 units in 2010.")
    out = scrub_document(doc, 5)
    assert "3.14159265358979323846264338327950288" not in out
    assert "123456789012345678901234567890" not in out
    assert "2010" not in out
    nums = re.findall(r"\d+(?:\.\d+)?", out)
    lens = sorted(len(n) for n in nums)
    # Digit counts survive: 4 for the year, 30 for the count, 37 with the
    # dot for the constant.
    assert lens == [4, 30, 37]


def test_common_word_inside_entity_run_still_scrubbed():
    # "Home" is a common word but "Home Depot" is an entity run.
    doc = "Workers visited Home Depot on foot."
    out = scrub_document(doc, 5)
    assert "Home" not in out and "Depot" not in out
    assert " on foot." in out
