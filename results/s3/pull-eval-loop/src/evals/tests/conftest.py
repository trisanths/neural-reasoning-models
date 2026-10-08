import pytest
import torch

from src.train.data import render_world_preamble
from src.train.model import ModelConfig, TransformerLM
from src.train.tokenizer import load_tokenizer, train_tokenizer
from src.worldgen.engine import generate_episodes


@pytest.fixture(scope="session")
def episodes():
    return list(generate_episodes(4242, 4))


@pytest.fixture(scope="session")
def tok(tmp_path_factory, episodes):
    base = tmp_path_factory.mktemp("evaltok")
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
def tiny_model(tok):
    torch.manual_seed(0)
    cfg = ModelConfig(vocab_size=tok.vocab_size, d_model=32, n_layers=1,
                      n_heads=2, d_ff=64, max_seq_len=256)
    model = TransformerLM(cfg)
    model.eval()
    return model


@pytest.fixture(scope="session")
def tiny_ckpt(tmp_path_factory, tiny_model):
    path = tmp_path_factory.mktemp("ckpt") / "latest.pt"
    cfg = tiny_model.cfg
    state = {
        "model": tiny_model.state_dict(),
        "step": 7,
        "config": {"model": {
            "vocab_size": cfg.vocab_size, "d_model": cfg.d_model,
            "n_layers": cfg.n_layers, "n_heads": cfg.n_heads,
            "d_ff": cfg.d_ff, "max_seq_len": cfg.max_seq_len,
            "rope_theta": cfg.rope_theta, "norm_eps": cfg.norm_eps,
        }},
    }
    torch.save(state, path)
    return path
