from src.pilot.vllm_model import (MODELS, seed_for, strip_thinking,
                                  user_content)


def test_closed_think_blocks_are_removed():
    assert strip_thinking("<think>\nwork 1+1\n</think>\n\nAnswer: 2") == "Answer: 2"


def test_an_unclosed_think_block_runs_to_the_end():
    assert strip_thinking("Answer: 3\n<think>still going") == "Answer: 3"


def test_a_bare_close_tag_keeps_what_follows():
    assert strip_thinking("rambling\n</think>\nAnswer: 4") == "Answer: 4"


def test_user_content_drops_only_the_trailing_cue():
    p = "Problem.\nWhat?\n\nGive only the answer, on one line, after the word Answer.\nAnswer:"
    got = user_content(p)
    assert got.endswith("after the word Answer.")
    assert user_content("no cue here") == "no cue here"


def test_seed_is_a_stable_function_of_the_prompt():
    assert seed_for("abc") == seed_for("abc") != seed_for("abd")
    assert 0 <= seed_for("abc") < 2 ** 32


def test_model_roster_matches_the_plan():
    assert set(MODELS) == {"lfm2.5-350m-base", "lfm2.5-350m", "qwen3-0.6b-base",
                           "qwen3-0.6b", "qwen3-1.7b-base", "qwen3-1.7b",
                           "qwen3-4b", "qwen3-8b"}
    for name, spec in MODELS.items():
        if spec.kind == "base":
            assert spec.thinking_modes == (False,)
        if name.startswith("qwen3") and spec.kind == "instruct":
            assert spec.thinking_modes == (False, True)
