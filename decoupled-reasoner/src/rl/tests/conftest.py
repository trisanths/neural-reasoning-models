import json

import numpy as np
import pytest
import torch

from src.rl.env import EnvConfig, EpisodeEnv, build_prompt
from src.train.data import render_world_preamble
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer, train_tokenizer
from src.worldgen.engine import generate_episodes


@pytest.fixture(scope="session")
def episodes():
    return list(generate_episodes(1717, 6))


@pytest.fixture(scope="session")
def tok(tmp_path_factory, episodes):
    base = tmp_path_factory.mktemp("rltok")
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for ep in episodes:
            fh.write(render_world_preamble(ep["world"]) + "\n")
            for doc in ep["documents"]:
                fh.write(doc["text"] + "\n")
            for q in ep["questions"]:
                fh.write(q["text"] + " " + q["answer"] + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return load_tokenizer(str(path))


@pytest.fixture(scope="session")
def episodes_jsonl(tmp_path_factory, episodes):
    path = tmp_path_factory.mktemp("rlep") / "episodes.jsonl"
    with open(path, "w") as fh:
        for ep in episodes:
            fh.write(json.dumps(ep) + "\n")
    return str(path)


@pytest.fixture
def env(tok):
    return EpisodeEnv(tok, EnvConfig(max_rounds=3, max_new_tokens=64,
                                     query_max_tokens=12, max_len=512))


@pytest.fixture(scope="session")
def tiny_model(tok):
    torch.manual_seed(3)
    cfg = ModelConfig(vocab_size=tok.vocab_size, d_model=32, n_layers=2,
                      n_heads=4, d_ff=64, max_seq_len=512)
    model = TransformerLM(cfg)
    model.eval()
    return model


@pytest.fixture(scope="session")
def tiny_ckpt(tmp_path_factory, tiny_model):
    path = tmp_path_factory.mktemp("rlckpt") / "latest.pt"
    c = tiny_model.cfg
    torch.save({
        "model": tiny_model.state_dict(),
        "step": 11,
        "config": {"model": {
            "vocab_size": c.vocab_size, "d_model": c.d_model,
            "n_layers": c.n_layers, "n_heads": c.n_heads, "d_ff": c.d_ff,
            "max_seq_len": c.max_seq_len, "rope_theta": c.rope_theta,
            "norm_eps": c.norm_eps,
        }},
    }, path)
    return str(path)


def make_scripted_step_fn(tok, query_text: str, answer_text: str,
                          target_rounds: int = 1):
    """A policy that is a pure function of its own token history.

    It emits target_rounds retrieval rounds with a fixed query, then the
    answer marker, the answer text, and <|eot|>. Being a pure function of
    the history means the rollout loop and src/evals/interactive.py can
    call it a different number of times and still walk the same trace.
    """
    sid = tok.special_ids
    retrieve_id, result_id = sid["<|retrieve|>"], sid["<|result|>"]
    answer_id, eot_id = sid["<|a|>"], sid["<|eot|>"]
    query_ids = tok.encode(query_text)
    answer_ids = tok.encode(answer_text)
    vocab = tok.vocab_size

    def next_token(hist):
        hist = list(hist)
        if answer_id in hist:
            emitted = hist[hist.index(answer_id) + 1:]
            if len(emitted) < len(answer_ids):
                return answer_ids[len(emitted)]
            return eot_id
        if retrieve_id in hist:
            rpos = len(hist) - 1 - hist[::-1].index(retrieve_id)
            after = hist[rpos + 1:]
            if result_id not in after:
                if len(after) < len(query_ids):
                    return query_ids[len(after)]
                return result_id
        if hist.count(retrieve_id) < target_rounds:
            return retrieve_id
        return answer_id

    def step_fn(hist):
        scores = np.full(vocab, -50.0, dtype=np.float64)
        scores[next_token(hist)] = 10.0
        return scores

    return step_fn


def first_task(env: EpisodeEnv, episode, tok):
    """Build a Task for the episode's first question with a derivation."""
    from src.rl.env import Task

    for q in episode["questions"]:
        if q.get("derivation"):
            return Task(
                episode_index=0, qid=q["qid"], question=q["text"],
                gold=q["answer"], prompt=build_prompt(episode, q, tok),
                documents=episode["documents"],
                domain=episode["world"]["domain"],
                hops=len(q["derivation"]))
    raise AssertionError("episode has no derived question")
