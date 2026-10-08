from src.pilot.grade import answer_line, canary_reply, grade, named_ints

INT_ITEM = {"answer": "42", "answer_kind": "int", "answer_space": 101}
NAMES_ITEM = {"answer": "vorka, mizel", "answer_kind": "names",
              "candidates": ["vorka", "mizel", "tubra", "solqen"]}
LABEL_ITEM = {"answer": "kavor", "answer_kind": "names",
              "candidates": ["kavor", "zeltu"]}


def test_last_answer_line_wins_for_an_instruct_reply():
    text = "Let me think.\nAnswer: 17\nWait, recomputing.\nAnswer: 42"
    assert answer_line(text) == ("42", True)


def test_answer_on_the_line_after_the_cue():
    assert answer_line("Some working.\n**Answer:**\n42\n") == ("42", True)


def test_markdown_and_boxed_answers_are_read():
    assert grade("**Answer**: \\boxed{42}", INT_ITEM)["correct"]
    assert grade("Final answer: 42.", INT_ITEM)["correct"]


def test_missing_answer_line_falls_back_and_says_so():
    g = grade("I think it is 42", INT_ITEM)
    assert g["answer_found"] is False
    assert g["correct"]


def test_base_completion_reads_the_first_nonempty_line():
    g = grade(" 42\n\nProblem.\nAnswer: 17", INT_ITEM, completion=True)
    assert g["correct"] and g["parsed"] == "42"
    assert answer_line("\n\n 42\nmore", completion=True) == ("42", True)


def test_two_numbers_on_the_answer_line_are_a_hedge():
    g = grade("Answer: 42 or 17", INT_ITEM)
    assert g["hedge"] and not g["correct"]
    assert g["correct_lenient"]


def test_a_modulus_clause_is_not_a_second_answer():
    assert named_ints("42 (mod 101)") == ["42"]
    assert grade("Answer: 42 mod 101", INT_ITEM)["correct"]


def test_names_need_the_exact_gold_set():
    assert grade("Answer: mizel, vorka", NAMES_ITEM)["correct"]
    over = grade("Answer: vorka, mizel, tubra", NAMES_ITEM)
    assert over["hedge"] and not over["correct"] and over["correct_lenient"]
    under = grade("Answer: vorka", NAMES_ITEM)
    assert not under["correct"] and not under["hedge"]


def test_a_name_inside_a_longer_word_is_not_named():
    assert not grade("Answer: kavorish", LABEL_ITEM)["correct"]


def test_hedging_canary_scores_zero_on_every_kind():
    for item in (INT_ITEM, NAMES_ITEM, LABEL_ITEM):
        g = grade(canary_reply(item), item)
        assert not g["correct"]
        assert g["hedge"]


def test_negative_integers_survive():
    item = {"answer": "-7", "answer_kind": "int", "answer_space": 50}
    assert grade("Answer: -7", item)["correct"]
    assert not grade("Answer: 7", item)["correct"]
