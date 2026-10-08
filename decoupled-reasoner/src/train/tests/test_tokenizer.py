import random

import pytest

from src.train.tokenizer import (
    PROCGEN_OFFSET,
    PROCGEN_SYMBOLS,
    RESERVED_TOKENS,
    SPECIAL_TOKENS,
    TrainTokenizer,
    load_tokenizer,
    train_tokenizer,
)

WORDS = [
    "lomera", "acquired", "subsidiary", "company", "route", "capacity",
    "jurisdiction", "filing", "officer", "schedule", "kinship", "temporal",
    "the", "of", "and", "in", "reports", "that", "holds", "transfers",
]


@pytest.fixture(scope="module")
def tok(tmp_path_factory):
    base = tmp_path_factory.mktemp("tokcorpus")
    rng = random.Random(11)
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(2000):
            fh.write(" ".join(rng.choices(WORDS, k=12)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return load_tokenizer(str(path))


def test_special_token_ids_are_lowest(tok: TrainTokenizer):
    for i, name in enumerate(SPECIAL_TOKENS):
        assert tok.token_id(name) == i


def test_reserved_range_follows_specials(tok: TrainTokenizer):
    assert PROCGEN_OFFSET == len(SPECIAL_TOKENS)
    assert len(RESERVED_TOKENS) == PROCGEN_SYMBOLS
    for i, name in enumerate(RESERVED_TOKENS):
        assert tok.token_id(name) == PROCGEN_OFFSET + i


def test_round_trip_plain_text(tok: TrainTokenizer):
    text = "the company lomera acquired a subsidiary in the jurisdiction"
    assert tok.decode(tok.encode(text)) == text


def test_round_trip_with_special_tokens(tok: TrainTokenizer):
    text = (
        "<|world|>domain: corporate\n"
        "<|doc|>lomera acquired the company<|q|>who acquired the company"
        "<|a|>lomera<|eot|>"
    )
    ids = tok.encode(text)
    for name in ("<|world|>", "<|doc|>", "<|q|>", "<|a|>", "<|eot|>"):
        assert tok.token_id(name) in ids
    assert tok.decode(ids) == text


def test_special_tokens_encode_to_single_ids(tok: TrainTokenizer):
    for name in SPECIAL_TOKENS:
        assert tok.encode(name) == [tok.token_id(name)]


def test_save_load_stable(tok: TrainTokenizer, tmp_path):
    path = tmp_path / "again.json"
    tok.save(str(path))
    reloaded = load_tokenizer(str(path))
    text = "officers of the company <|retrieve|> filing <|result|> reports"
    assert reloaded.encode(text) == tok.encode(text)
    assert reloaded.decode(reloaded.encode(text)) == text
