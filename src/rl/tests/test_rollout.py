"""The rollout loop: agreement with the eval loop, masking, batching."""

import pytest

from src.evals.interactive import generate_with_retrieval
from src.rl.env import EnvConfig, EpisodeEnv, make_service
from src.rl.sampler import ScriptedPolicy
from src.rl.tests.conftest import first_task, make_scripted_step_fn


def _query_for(episode, question):
    """A query built from the question's own words, which is what the
    scripted policy writes."""
    return question


def test_rollout_matches_the_eval_loop_token_for_token(env, episodes, tok):
    for episode in episodes[:3]:
        task = first_task(env, episode, tok)
        step_fn = make_scripted_step_fn(tok, _query_for(episode, task.question),
                                        task.gold, target_rounds=2)
        want = generate_with_retrieval(
            step_fn, tok, task.documents, task.prompt,
            max_rounds=env.cfg.max_rounds,
            max_new_tokens=env.cfg.max_new_tokens,
            query_max_tokens=env.cfg.query_max_tokens)
        got = env.rollout(ScriptedPolicy(step_fn), [task])[0]
        assert got.tokens == want["tokens"]
        assert got.stop_reason == want["stop_reason"]
        assert got.n_generated == want["n_generated"]
        assert got.answer_text == want["answer_text"]
        assert [r["query"] for r in got.rounds] == [r["query"] for r in want["rounds"]]
        assert [r["doc_index"] for r in got.rounds] == [r["doc_index"]
                                                        for r in want["rounds"]]


def test_rollout_agrees_when_the_query_cap_truncates(episodes, tok):
    env = EpisodeEnv(tok, EnvConfig(max_rounds=2, max_new_tokens=64,
                                    query_max_tokens=3, max_len=512))
    episode = episodes[0]
    task = first_task(env, episode, tok)
    step_fn = make_scripted_step_fn(tok, task.question, task.gold,
                                    target_rounds=1)
    want = generate_with_retrieval(
        step_fn, tok, task.documents, task.prompt, max_rounds=2,
        max_new_tokens=64, query_max_tokens=3)
    got = env.rollout(ScriptedPolicy(step_fn), [task])[0]
    assert got.tokens == want["tokens"]
    assert got.stop_reason == want["stop_reason"]
    assert len(got.rounds[0]["query"].split()) <= 3


def test_scripted_policy_answers_correctly_and_scores_one(env, episodes, tok):
    episode = episodes[1]
    task = first_task(env, episode, tok)
    step_fn = make_scripted_step_fn(tok, task.question, task.gold,
                                    target_rounds=1)
    roll = env.rollout(ScriptedPolicy(step_fn), [task])[0]
    assert roll.correct
    assert roll.stop_reason == "eot"
    assert roll.n_rounds == 1
    assert roll.reward == pytest.approx(1.0 + 0.05 + 0.05)


def test_mask_covers_only_policy_tokens(env, episodes, tok):
    episode = episodes[2]
    task = first_task(env, episode, tok)
    step_fn = make_scripted_step_fn(tok, task.question, task.gold,
                                    target_rounds=2)
    roll = env.rollout(ScriptedPolicy(step_fn), [task])[0]

    assert len(roll.mask) == len(roll.tokens)
    assert sum(roll.mask) == roll.n_generated
    # The prompt is never trained on.
    assert set(roll.mask[:roll.prompt_len]) == {0}

    # Every served chunk appears verbatim in the trace with a zero mask.
    result_id = tok.special_ids["<|result|>"]
    positions = [i for i, t in enumerate(roll.tokens) if t == result_id]
    assert len(positions) == roll.n_rounds
    for pos, round_ in zip(positions, roll.rounds):
        span = slice(pos + 1, pos + 1 + round_["n_chunk_tokens"])
        assert roll.tokens[span] == tok.encode(round_["chunk"])
        assert set(roll.mask[span]) == {0}

    # The query tokens between <|retrieve|> and <|result|> are trained on.
    retrieve_id = tok.special_ids["<|retrieve|>"]
    rpos = roll.tokens.index(retrieve_id)
    assert set(roll.mask[rpos + 1:positions[0]]) == {1}


def test_batched_rollouts_match_one_at_a_time(env, episodes, tok):
    tasks = [first_task(env, ep, tok) for ep in episodes[:4]]
    step_fns = [make_scripted_step_fn(tok, t.question, t.gold, target_rounds=1)
                for t in tasks]

    singles = [env.rollout(ScriptedPolicy(fn), [t])[0]
               for fn, t in zip(step_fns, tasks)]

    class Multi:
        """One scripted policy per lane, driven in lockstep."""

        def __init__(self, fns):
            self.inner = [ScriptedPolicy(fn) for fn in fns]

        def begin(self, prompts):
            return [p.begin([pr])[0] for p, pr in zip(self.inner, prompts)]

        def advance(self, tokens):
            return [p.advance([t])[0] for p, t in zip(self.inner, tokens)]

    batched = env.rollout(Multi(step_fns), tasks)
    for one, many in zip(singles, batched):
        assert one.tokens == many.tokens
        assert one.mask == many.mask
        assert one.reward == pytest.approx(many.reward)


def test_group_rollouts_keep_independent_served_sets(env, episodes, tok):
    task = first_task(env, episodes[0], tok)
    step_fn = make_scripted_step_fn(tok, task.question, task.gold,
                                    target_rounds=2)
    tasks = [task, task]
    services = [make_service(task.documents) for _ in tasks]
    rolls = env.rollout(ScriptedPolicy(step_fn), tasks, services)
    assert rolls[0].tokens == rolls[1].tokens
    # Same policy, same question, but each lane excluded only its own hits.
    assert ([r["doc_index"] for r in rolls[0].rounds]
            == [r["doc_index"] for r in rolls[1].rounds])
    assert len(set(r["doc_index"] for r in rolls[0].rounds)) == 2


def test_round_cap_stops_the_rollout(episodes, tok):
    env = EpisodeEnv(tok, EnvConfig(max_rounds=1, max_new_tokens=64,
                                    query_max_tokens=8, max_len=512))
    task = first_task(env, episodes[0], tok)
    step_fn = make_scripted_step_fn(tok, task.question, task.gold,
                                    target_rounds=3)
    roll = env.rollout(ScriptedPolicy(step_fn), [task])[0]
    assert roll.n_rounds == 1
    assert roll.stop_reason == "max_rounds"


def test_token_budget_stops_the_rollout(episodes, tok):
    env = EpisodeEnv(tok, EnvConfig(max_rounds=4, max_new_tokens=4,
                                    query_max_tokens=8, max_len=512))
    task = first_task(env, episodes[0], tok)
    step_fn = make_scripted_step_fn(tok, task.question, task.gold,
                                    target_rounds=2)
    roll = env.rollout(ScriptedPolicy(step_fn), [task])[0]
    assert roll.n_generated == 4
    assert roll.stop_reason == "max_new_tokens"
