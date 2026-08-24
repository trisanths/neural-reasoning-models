import random

import numpy as np
import pytest

from src.evals.heldout import run_heldout
from src.evals.interactive import (
    generate_with_retrieval,
    make_checkpoint_step_fn,
    make_model_step_fn,
    make_retrieval_answer_fn,
)
from src.evals.noise_axis import corrupt_examples, run_noise_axis_interactive

DOCS = ["alpha beta gadget", "gamma delta widget", "epsilon zeta gizmo"]


def onehot(vocab_size, token_id):
    row = np.zeros(vocab_size, dtype=np.float32)
    row[token_id] = 1.0
    return row


class QueueStepFn:
    """Scripted emitter: pops the next planned token id on every step call
    and falls back to a filler token when the script runs out."""

    def __init__(self, vocab_size, script, filler):
        self.vocab_size = vocab_size
        self.script = list(script)
        self.filler = filler
        self.pos = 0

    def __call__(self, tokens):
        tid = self.script[self.pos] if self.pos < len(self.script) else self.filler
        self.pos += 1
        return onehot(self.vocab_size, tid)


class ChunkEchoStepFn:
    """Scripted reader: retrieves with the question as its query, then
    answers by echoing the served chunk verbatim and closing with <|eot|>.
    Stateless between calls; every decision reads the visible sequence."""

    def __init__(self, tokenizer):
        self.sid = tokenizer.special_ids
        self.vocab_size = tokenizer.vocab_size

    def __call__(self, tokens):
        tokens = list(tokens)
        sid = self.sid

        def rfind(tid):
            for i in range(len(tokens) - 1, -1, -1):
                if tokens[i] == tid:
                    return i
            return -1

        q = rfind(sid["<|q|>"])
        r = rfind(sid["<|retrieve|>"])
        if r < q:
            return onehot(self.vocab_size, sid["<|retrieve|>"])
        s = rfind(sid["<|result|>"])
        if s < r:
            question = tokens[q + 1:r]
            emitted = tokens[r + 1:]
            if len(emitted) < len(question):
                return onehot(self.vocab_size, question[len(emitted)])
            return onehot(self.vocab_size, sid["<|result|>"])
        a = rfind(sid["<|a|>"])
        if a < s:
            return onehot(self.vocab_size, sid["<|a|>"])
        chunk = tokens[s + 1:a]
        echoed = tokens[a + 1:]
        if len(echoed) < len(chunk):
            return onehot(self.vocab_size, chunk[len(echoed)])
        return onehot(self.vocab_size, sid["<|eot|>"])


def make_noise_examples(n_episodes=10, per_episode=2, chunks_per=4):
    """Examples whose gold answer is the chunk BM25 serves when clean."""
    examples = []
    for eid in range(n_episodes):
        for j in range(per_episode):
            qid = f"q{eid}x{j}"
            target = f"{qid} holds tok{eid}x{j}"
            chunks = [target]
            chunks += [f"filler ep{eid} c{k}" for k in range(chunks_per - 1)]
            examples.append({"question": qid, "answer": target,
                             "chunks": chunks, "episode_id": eid})
    return examples


def test_serves_right_chunk_for_known_query(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find gamma delta")]
    query_ids = tok.encode("gamma delta")
    done_ids = tok.encode("done")
    script = ([sid["<|retrieve|>"]] + query_ids + [sid["<|result|>"]]
              + [sid["<|a|>"]] + done_ids + [sid["<|eot|>"]])
    step = QueueStepFn(tok.vocab_size, script, filler=tok.encode("x")[0])

    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=2, max_new_tokens=64, seed=0)
    chunk_ids = tok.encode(DOCS[1])
    expected = (prompt + [sid["<|retrieve|>"]] + query_ids
                + [sid["<|result|>"]] + chunk_ids
                + [sid["<|a|>"]] + done_ids + [sid["<|eot|>"]])
    assert out["tokens"] == expected
    assert out["n_rounds"] == 1
    assert out["rounds"][0]["query"] == "gamma delta"
    assert out["rounds"][0]["doc_index"] == 1
    assert out["rounds"][0]["chunk"] == DOCS[1]
    assert out["answer_text"] == "done"
    assert out["stop_reason"] == "eot"
    assert out["answer_start"] == len(expected) - len(done_ids) - 1
    assert out["n_generated"] == len(script)
    assert out["seed"] == 0


def test_round_cap_zero_blocks_serving(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find gamma")]
    step = QueueStepFn(tok.vocab_size, [sid["<|retrieve|>"]],
                       filler=tok.encode("x")[0])
    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=0, max_new_tokens=32, seed=0)
    assert out["stop_reason"] == "max_rounds"
    assert out["n_rounds"] == 0
    assert sid["<|result|>"] not in out["tokens"]
    assert out["generated"] == []
    assert out["tokens"] == prompt


def test_retrieve_with_no_documents_stops(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find gamma")]
    step = QueueStepFn(tok.vocab_size, [sid["<|retrieve|>"]],
                       filler=tok.encode("x")[0])
    out = generate_with_retrieval(step, tok, [], prompt,
                                  max_rounds=4, max_new_tokens=32, seed=0)
    assert out["stop_reason"] == "max_rounds"
    assert out["n_rounds"] == 0


def test_round_cap_one_allows_single_round(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find gamma")]
    query_ids = tok.encode("gamma")
    script = ([sid["<|retrieve|>"]] + query_ids + [sid["<|result|>"]]
              + [sid["<|retrieve|>"]])
    step = QueueStepFn(tok.vocab_size, script, filler=tok.encode("x")[0])
    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=1, max_new_tokens=64, seed=0)
    assert out["stop_reason"] == "max_rounds"
    assert out["n_rounds"] == 1
    assert out["rounds"][0]["doc_index"] == 1
    # the blocked second <|retrieve|> is not appended to the trace
    assert out["tokens"][-1] != sid["<|retrieve|>"]


def test_terminates_on_token_budget(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find gamma")]
    step = QueueStepFn(tok.vocab_size, [], filler=tok.encode("x")[0])
    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=2, max_new_tokens=17, seed=0)
    assert out["stop_reason"] == "max_new_tokens"
    assert out["n_generated"] == 17
    assert out["n_rounds"] == 0


def test_query_cap_forces_result(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find zzz")]
    filler = tok.encode("z")[0]
    step = QueueStepFn(tok.vocab_size, [sid["<|retrieve|>"]], filler=filler)
    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=1, max_new_tokens=12, seed=0,
                                  query_max_tokens=4)
    assert out["n_rounds"] == 1
    # the marker was inserted by the loop, not emitted by the model
    assert sid["<|result|>"] in out["tokens"]
    assert sid["<|result|>"] not in out["generated"]
    assert out["tokens"][len(prompt) + 1 + 4] == sid["<|result|>"]
    # a query with no matching terms falls back to the earliest document
    assert out["rounds"][0]["doc_index"] == 0
    assert out["stop_reason"] == "max_new_tokens"


def test_eot_during_query_stops(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("find gamma")]
    part = tok.encode("gam")[0]
    script = [sid["<|retrieve|>"], part, sid["<|eot|>"]]
    step = QueueStepFn(tok.vocab_size, script, filler=tok.encode("x")[0])
    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=2, max_new_tokens=32, seed=0)
    assert out["stop_reason"] == "eot"
    assert out["n_rounds"] == 0
    assert out["tokens"] == prompt + [sid["<|retrieve|>"], part, sid["<|eot|>"]]


def test_answer_boundary_stops(tok):
    sid = tok.special_ids
    prompt = [sid["<|q|>"], *tok.encode("what color")]
    blue_ids = tok.encode("blue")
    script = [sid["<|a|>"]] + blue_ids + [sid["<|q|>"]]
    step = QueueStepFn(tok.vocab_size, script, filler=tok.encode("x")[0])
    out = generate_with_retrieval(step, tok, DOCS, prompt,
                                  max_rounds=2, max_new_tokens=32, seed=0)
    assert out["stop_reason"] == "answer_boundary"
    assert out["answer_text"] == "blue"
    # the boundary token is not appended
    assert out["tokens"] == prompt + [sid["<|a|>"]] + blue_ids


def test_checkpoint_adapter_runs_and_is_deterministic(tok, tiny_ckpt, episodes):
    step_fn, model, state = make_checkpoint_step_fn(str(tiny_ckpt), "cpu")
    assert state["step"] == 7
    sid = tok.special_ids
    scores = step_fn([sid["<|q|>"], *tok.encode("hello")])
    assert scores.shape == (tok.vocab_size,)

    ep = episodes[0]
    prompt = [sid["<|q|>"], *tok.encode(ep["questions"][0]["text"])]
    kwargs = dict(max_rounds=2, max_new_tokens=8, seed=3)
    a = generate_with_retrieval(step_fn, tok, ep["documents"], prompt, **kwargs)
    b = generate_with_retrieval(step_fn, tok, ep["documents"], prompt, **kwargs)
    assert a == b
    assert a["stop_reason"] in {"eot", "answer_boundary", "max_rounds",
                                "max_new_tokens"}
    assert a["n_generated"] <= 8

    other = make_model_step_fn(model, "cpu")
    c = generate_with_retrieval(other, tok, ep["documents"], prompt, **kwargs)
    assert c == a


def test_heldout_use_retrieval_structure_and_determinism(episodes, tok, tiny_model):
    subset = episodes[:2]
    a = run_heldout(tiny_model, tok, subset, "cpu", seed=1,
                    use_retrieval=True, max_rounds=2, max_new_tokens=12)
    b = run_heldout(tiny_model, tok, subset, "cpu", seed=1,
                    use_retrieval=True, max_rounds=2, max_new_tokens=12)
    assert a == b
    assert a["use_retrieval"] is True
    assert a["n_episodes"] == 2
    assert a["n_questions"] == sum(len(e["questions"]) for e in subset)
    assert 0.0 <= a["accuracy"] <= 1.0
    assert 0.0 <= a["mean_rounds"] <= 2.0

    plain = run_heldout(tiny_model, tok, subset, "cpu", seed=1)
    assert plain["use_retrieval"] is False
    assert "mean_rounds" not in plain


def test_noise_axis_corruption_changes_served_chunks(tok):
    examples = make_noise_examples()
    step = ChunkEchoStepFn(tok)
    rates = (0.0, 0.5, 1.0)
    seed = 5
    report = run_noise_axis_interactive(step, tok, examples,
                                        rates=rates, seed=seed,
                                        max_rounds=1, max_new_tokens=64)
    assert report["accuracy_per_rate"]["0"] == 1.0
    assert report["accuracy_per_rate"]["1"] == 0.0
    assert report["slope"] < 0.0

    # Replicate the rate 0.5 corruption stream. The clean loop always
    # serves position 0, the only chunk holding the query term, so the
    # served chunk changes exactly when that position was swapped, and
    # accuracy drops one for one with those swaps.
    rng = random.Random(seed * 1000003 + rates.index(0.5))
    corrupted = corrupt_examples(examples, 0.5, rng)
    changed = sum(1 for orig, cur in zip(examples, corrupted)
                  if cur["chunks"][0] != orig["chunks"][0])
    frac = changed / len(examples)
    assert 0.2 <= frac <= 0.8
    assert report["accuracy_per_rate"]["0.5"] == pytest.approx(1.0 - frac)


def test_retrieval_answer_fn_echoes_served_chunk(tok):
    examples = make_noise_examples(n_episodes=2, per_episode=1)
    answer_fn = make_retrieval_answer_fn(ChunkEchoStepFn(tok), tok,
                                         max_rounds=1, max_new_tokens=64)
    for ex in examples:
        assert answer_fn(ex["question"], ex["chunks"]) == ex["answer"]
