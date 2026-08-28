"""The corpus stays natural: that is the claim the whole package rests on."""

import numpy as np
import pytest

from src.lossmask.build import render_document
from src.lossmask.shards import TaggedShardReader, TaggedShardWriter
from src.lossmask.tags import TAG_ENTITY, TAG_PLAIN


@pytest.fixture(scope="module")
def tokenizer(tmp_path_factory):
    from src.train.tokenizer import train_tokenizer

    corpus = tmp_path_factory.mktemp("tok") / "c.txt"
    corpus.write_text(
        ("the plant near the river reported units and filings on a quiet "
         "day in the valley and the report was filed by the office\n") * 300)
    return train_tokenizer([str(corpus)], vocab_size=800)


DOCS = [
    "the plant near Ohio reported 4,200 units on March 12, 1998.",
    "a quiet day in the valley, and the office filed the report.",
    "see https://example.com/x or write to bob@example.com about 1987.",
]


def test_the_token_stream_is_what_a_plain_render_would_write(tokenizer):
    """render_regime_a.py writes each document's BPE tokens then one <|eot|>.
    A tagged render must write exactly that, or the arms are not reading the
    same corpus every other run in this project read."""
    eot = tokenizer.special_ids["<|eot|>"]
    for text in DOCS:
        ids, tags = render_document(text, tokenizer, eot)
        assert ids == tokenizer.encode(text) + [eot]
        assert len(tags) == len(ids)
        assert tags[-1] == TAG_PLAIN, "the document separator is not a fact"


def test_a_document_with_no_anchors_is_all_plain(tokenizer):
    eot = tokenizer.special_ids["<|eot|>"]
    _, tags = render_document(
        "a quiet day in the valley and the office filed the report.",
        tokenizer, eot)
    assert set(tags) == {TAG_PLAIN}


def test_a_round_trip_through_shards_keeps_the_tags_on_their_tokens(
        tokenizer, tmp_path):
    eot = tokenizer.special_ids["<|eot|>"]
    writer = TaggedShardWriter(tmp_path, shard_size=32)
    every_id, every_tag = [], []
    for text in DOCS:
        ids, tags = render_document(text, tokenizer, eot)
        writer.write(ids, tags)
        every_id += ids
        every_tag += tags
    writer.close()

    reader = TaggedShardReader(tmp_path)
    assert reader.total_tokens == len(every_id)
    assert list(reader.get_slice(0, reader.total_tokens)) == every_id
    assert list(reader.get_tag_slice(0, reader.total_tokens)) == every_tag
    assert np.count_nonzero(every_tag) > 0


def test_an_entity_only_document_tags_the_name_and_nothing_else(tokenizer):
    eot = tokenizer.special_ids["<|eot|>"]
    ids, tags = render_document("the plant near Ohio filed the report.",
                                tokenizer, eot)
    marked = [i for i, t in enumerate(tags) if t]
    assert marked, "Ohio must be tagged"
    assert all(tags[i] == TAG_ENTITY for i in marked)
    assert "Ohio" in tokenizer.decode([ids[i] for i in marked])
