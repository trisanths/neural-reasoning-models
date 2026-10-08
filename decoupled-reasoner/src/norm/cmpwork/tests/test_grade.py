"""The grader, pinned. Three of these shapes were found broken on this project.

The prefix case is the one that matters most: invented words on one page share
stems, so a grader that asks whether the answer contains an option scores `emb`
correct on an answer of `embqen`.
"""

from src.norm.cmpwork.grade import forced


def test_one_option_named_is_forced_correct():
    g = forced("embqen", ["embqen", "tuwisk", "gestmi"], "embqen")
    assert g["strict_correct"] == 1 and g["lenient_correct"] == 1
    assert g["hedged"] == 0 and g["named_none"] == 0
    assert abs(g["floor"] - 1 / 3) < 1e-9


def test_naming_two_is_wrong_however_the_first_falls():
    g = forced("embqen or tuwisk", ["embqen", "tuwisk"], "embqen")
    assert g["hedged"] == 1
    assert g["strict_correct"] == 0
    assert g["lenient_correct"] == 1


def test_a_prefix_of_another_option_is_not_a_naming():
    g = forced("the answer is embqen", ["emb", "embqen"], "embqen")
    assert g["named"] == ["embqen"]
    assert g["strict_correct"] == 1 and g["hedged"] == 0


def test_the_shorter_option_still_counts_when_it_stands_alone():
    g = forced("the answer is emb", ["emb", "embqen"], "emb")
    assert g["named"] == ["emb"] and g["strict_correct"] == 1


def test_a_substring_inside_a_longer_word_is_not_a_naming():
    g = forced("embqen", ["emb", "qen"], "emb")
    assert g["named"] == [] and g["named_none"] == 1
    assert g["strict_correct"] == 0


def test_nothing_named_is_zero_and_not_a_guess():
    g = forced("", ["a1", "b2", "c3"], "a1")
    assert g["named_none"] == 1 and g["strict_correct"] == 0


def test_integers_are_matched_as_tokens():
    g = forced("the value is 95", ["31", "95"], "95")
    assert g["strict_correct"] == 1
    g2 = forced("the value is 951", ["31", "95"], "95")
    assert g2["named_none"] == 1
