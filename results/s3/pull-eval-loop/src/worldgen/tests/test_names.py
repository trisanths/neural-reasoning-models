import numpy as np

from src.worldgen import names


def test_names_deterministic():
    a = names.unique_names(np.random.default_rng(9), "company", 20)
    b = names.unique_names(np.random.default_rng(9), "company", 20)
    assert a == b


def test_names_unique():
    got = names.unique_names(np.random.default_rng(1), "person", 50)
    assert len(set(got)) == 50


def test_blocklist_enforced():
    rng = np.random.default_rng(2)
    for _ in range(500):
        word = names.make_word(rng)
        assert word.lower() not in names.BLOCKLIST


def test_company_names_have_suffix():
    rng = np.random.default_rng(3)
    for _ in range(20):
        name = names.company_name(rng)
        assert name.split()[-1] in names.COMPANY_SUFFIXES


def test_person_names_two_words():
    rng = np.random.default_rng(4)
    for _ in range(20):
        assert len(names.person_name(rng).split()) == 2
