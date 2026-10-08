"""Reward correctness, retrieval serving, and task loading."""

import pytest

from src.rl.env import (EnvConfig, EpisodeEnv, Rollout, Task, build_prompt,
                        load_tasks, make_service, rollout_stats)


def make_roll(env, answer, gold, rounds=(), stop_reason="eot"):
    task = Task(episode_index=0, qid="q1", question="who?", gold=gold,
                prompt=[1, 2, 3], documents=[])
    roll = Rollout(task=task, tokens=[1, 2, 3], mask=[0, 0, 0], prompt_len=3,
                   rounds=[{"query": q, "doc_index": i, "chunk": "c",
                            "n_chunk_tokens": 1}
                           for i, q in enumerate(rounds)],
                   answer_text=answer, stop_reason=stop_reason)
    return env.score(roll)


def test_exact_match_earns_the_full_reward(env):
    roll = make_roll(env, "Vanban Systems", "Vanban Systems", rounds=("who",))
    assert roll.correct
    assert roll.reward == pytest.approx(1.0 + 0.05 + 0.05)


def test_normalizer_ignores_articles_case_and_punctuation(env):
    roll = make_roll(env, "  the VANBAN systems. ", "Vanban Systems")
    assert roll.correct


def test_contains_fallback_accepts_a_short_wrapper(env):
    roll = make_roll(env, "it is Vanban Systems", "Vanban Systems")
    assert roll.correct


def test_contains_fallback_rejects_a_long_list(env):
    padding = " ".join(f"cand{i}" for i in range(12))
    roll = make_roll(env, f"{padding} Vanban Systems", "Vanban Systems")
    assert not roll.correct


def test_yes_no_admits_no_contains_fallback(env):
    assert env.is_correct("yes", "yes")
    assert not env.is_correct("yes no", "no")
    assert not env.is_correct("the answer is no", "no")


def test_wrong_answer_still_earns_shaping_only(env):
    roll = make_roll(env, "Momge Logistics", "Vanban Systems", rounds=("who",))
    assert not roll.correct
    assert roll.reward == pytest.approx(0.05 + 0.05)


def test_no_retrieval_forfeits_the_retrieval_bonus(env):
    roll = make_roll(env, "Vanban Systems", "Vanban Systems")
    assert roll.reward == pytest.approx(1.0 + 0.05)


def test_unterminated_trace_forfeits_the_format_bonus(env):
    roll = make_roll(env, "Vanban Systems", "Vanban Systems",
                     rounds=("who",), stop_reason="max_new_tokens")
    assert roll.reward == pytest.approx(1.0 + 0.05)


def test_repeated_and_empty_queries_are_penalized(env):
    roll = make_roll(env, "wrong", "Vanban Systems",
                     rounds=("who runs it", "who runs it", ""))
    # retrieval bonus and format bonus, minus two degenerate queries
    assert roll.info["degenerate_queries"] == 2
    assert roll.reward == pytest.approx(0.05 + 0.05 - 0.10)


def test_shaping_can_be_switched_off(tok):
    plain = EpisodeEnv(tok, EnvConfig(format_bonus=0.0, retrieval_bonus=0.0,
                                      degenerate_query_penalty=0.0))
    roll = make_roll(plain, "Vanban Systems", "Vanban Systems",
                     rounds=("a", "a"))
    assert roll.reward == pytest.approx(1.0)


def test_service_serves_without_replacement(episodes):
    documents = episodes[0]["documents"]
    service = make_service(documents)
    query = documents[0]["text"]
    first = service.top(query)
    second = service.top(query)
    assert first is not None and second is not None
    assert first[0] != second[0]
    assert first[0] in service.served and second[0] in service.served


def test_service_reports_exhaustion(episodes):
    service = make_service(episodes[0]["documents"][:2])
    assert service.top("a") is not None
    assert service.top("a") is not None
    assert service.exhausted()
    assert service.top("a") is None


def test_prompt_holds_the_question_and_no_documents(episodes, tok):
    ep = episodes[0]
    q = ep["questions"][0]
    prompt = build_prompt(ep, q, tok)
    sid = tok.special_ids
    assert prompt[0] == sid["<|world|>"]
    assert sid["<|doc|>"] not in prompt
    assert prompt.count(sid["<|q|>"]) == 1
    assert prompt[-len(tok.encode(q["text"])):] == tok.encode(q["text"])


def test_web_style_prompt_keeps_its_context_prefix(episodes, tok):
    ep = dict(episodes[0])
    ep["n_context"] = 2
    prompt = build_prompt(ep, ep["questions"][0], tok)
    assert prompt.count(tok.special_ids["<|doc|>"]) == 2


def test_load_tasks_is_deterministic_and_filters(episodes_jsonl, tok):
    a = load_tasks(episodes_jsonl, tok, questions_per_episode=2, seed=5)
    b = load_tasks(episodes_jsonl, tok, questions_per_episode=2, seed=5)
    assert [t.qid for t in a] == [t.qid for t in b]
    assert all(t.hops >= 1 for t in a)
    assert all(t.gold for t in a)
    c = load_tasks(episodes_jsonl, tok, questions_per_episode=1, seed=5)
    assert len(c) < len(a)
    d = load_tasks(episodes_jsonl, tok, limit_episodes=2, seed=5)
    assert len({t.episode_index for t in d}) <= 2


def test_load_tasks_drops_overlong_prompts(episodes_jsonl, tok):
    assert load_tasks(episodes_jsonl, tok, max_prompt_tokens=5, seed=5) == []


def test_rollout_stats_aggregate(env):
    rolls = [make_roll(env, "Vanban Systems", "Vanban Systems", rounds=("q",)),
             make_roll(env, "nope", "Vanban Systems")]
    stats = rollout_stats(rolls)
    assert stats["n_rollouts"] == 2
    assert stats["accuracy"] == pytest.approx(0.5)
    assert stats["mean_rounds"] == pytest.approx(0.5)
    assert stats["any_retrieval"] == pytest.approx(0.5)
