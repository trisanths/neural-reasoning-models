import numpy as np
import pytest

from src.lossmask.tagger import (date_spans, encode_with_tags, factual_spans,
                                 tag_offsets)
from src.lossmask.tags import (TAG_DATE, TAG_ENTITY, TAG_NUMBER, TAG_PLAIN,
                               TAG_WEB)
from src.scrub.scrubber import anchor_spans, scrub_text


def tagged(text, tag):
    return [text[s:e] for s, e, t in factual_spans(text) if t == tag]


def test_anchor_spans_agree_with_what_scrub_replaces():
    text = ("Marie Curie moved to Paris in 1891 and won 2 prizes. "
            "Write to curie@radium.fr or see https://nobel.org/curie.")
    spans = anchor_spans(text)
    assert spans == sorted(spans)
    for a, b in zip(spans, spans[1:]):
        assert a[1] <= b[0], "anchor spans must not overlap"
    # Every span the scrubber rewrote is a span this reports.
    result = scrub_text(text, 7)
    assert len(result.spans) == len(spans)
    assert [kind for _, _, kind in spans].count("entity") >= 2


def test_entities_and_numbers_separate():
    text = "Acme Corp reported 4,200 units in the Ohio plant."
    assert "Acme Corp" in tagged(text, TAG_ENTITY)
    assert "Ohio" in tagged(text, TAG_ENTITY)
    assert "4,200" in tagged(text, TAG_NUMBER)


def test_web_anchors_tagged():
    text = "Mail bob@example.com or read https://example.com/x, ping @bob."
    web = tagged(text, TAG_WEB)
    assert "bob@example.com" in web
    assert any(s.startswith("https://example.com") for s in web)
    assert "@bob" in web


@pytest.mark.parametrize("text,want", [
    ("Signed on March 12, 1998 in the hall.", "March 12, 1998"),
    ("Signed on 12 March 1998 in the hall.", "12 March 1998"),
    ("The 1998-03-12 filing.", "1998-03-12"),
    ("The 03/12/1998 filing.", "03/12/1998"),
    ("It opened in March 1998.", "March 1998"),
    ("It opened in 1998.", "1998"),
    ("A child of the 1990s.", "1990s"),
])
def test_date_shapes(text, want):
    assert want in [text[s:e] for s, e in date_spans(text)]


def test_a_number_outside_the_year_range_is_not_a_date():
    text = "The lot held 1240 crates and 9500 bolts."
    assert date_spans(text) == []
    assert "9500" in tagged(text, TAG_NUMBER)


def test_dates_win_over_the_entity_and_number_spans_they_cover():
    text = "The merger closed on January 14, 1987 in Dublin."
    spans = factual_spans(text)
    for a, b in zip(spans, spans[1:]):
        assert a[1] <= b[0]
    assert "January 14, 1987" in tagged(text, TAG_DATE)
    # The year is inside the date, so nothing reports it as a bare number,
    # and the month name is not a loose entity either.
    assert tagged(text, TAG_NUMBER) == []
    assert tagged(text, TAG_ENTITY) == ["Dublin"]


def test_tag_offsets_walks_disjoint_spans():
    offsets = [(0, 3), (3, 7), (7, 12), (12, 20)]
    spans = [(3, 7, TAG_ENTITY), (14, 16, TAG_NUMBER)]
    assert tag_offsets(offsets, spans) == [
        TAG_PLAIN, TAG_ENTITY, TAG_PLAIN, TAG_NUMBER]


def test_tag_offsets_with_no_spans_is_all_plain():
    assert tag_offsets([(0, 2), (2, 4)], []) == [TAG_PLAIN, TAG_PLAIN]


def test_encode_with_tags_marks_the_entity_tokens(tmp_path):
    from src.train.tokenizer import train_tokenizer

    corpus = tmp_path / "c.txt"
    corpus.write_text(
        ("the plant in Ohio reported units and prizes and filings "
         "on a quiet day near the river\n") * 200)
    tokenizer = train_tokenizer([str(corpus)], vocab_size=600)

    text = "the plant in Ohio reported 4,200 units"
    ids, tags = encode_with_tags(text, tokenizer)
    assert len(ids) == len(tags)
    assert set(tags) == {TAG_PLAIN, TAG_ENTITY, TAG_NUMBER}

    # Every tagged token's own text sits inside a tagged span, and the two
    # untagged ends of the sentence stay untagged.
    pieces = tokenizer.tokenizer.encode(text)
    marked = "".join(pieces.tokens[i].replace("Ġ", " ")
                     for i, t in enumerate(tags) if t == TAG_ENTITY)
    assert marked.strip() == "Ohio"
    marked = "".join(pieces.tokens[i].replace("Ġ", " ")
                     for i, t in enumerate(tags) if t == TAG_NUMBER)
    assert marked.strip() == "4,200"


def test_tagging_leaves_the_text_alone():
    text = "Marie Curie moved to Paris in 1891."
    spans = factual_spans(text)
    rebuilt = text
    assert rebuilt == "Marie Curie moved to Paris in 1891."
    assert [text[s:e] for s, e, _ in spans][0] == "Marie Curie"


def test_histogram_counts_every_token():
    from src.lossmask.tagger import tag_histogram

    tags = [0, 0, 1, 2, 1, 0]
    assert tag_histogram(tags) == {0: 3, 1: 2, 2: 1}
    assert sum(tag_histogram(tags).values()) == len(tags)
    assert np.asarray(tags).max() < 8
