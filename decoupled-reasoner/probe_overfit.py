"""Probe: tune the oracle vs distractor overfit test before fixing thresholds."""
import math, sys
import numpy as np
import torch

from src.train.evidence_data import Chunk, EvidenceExample, EvidenceCollator
from src.train.evidence_model import EvidenceModelConfig, EvidenceTransformerLM
from src.train.evidence_trainer import train_evidence_steps
from src.train.tests.evidence_fixtures import StubTokenizer

N_SLOTS = 8
N_VALUES = 8
MARKER0 = 20
VALUE0 = 60
VOCAB = 128


def lookup_examples(n_examples, seed, drop_gold=False):
    rng = np.random.default_rng(seed)
    markers = [MARKER0 + j for j in range(N_SLOTS)]
    values = [VALUE0 + v for v in range(N_VALUES)]
    out = []
    for i in range(n_examples):
        assign = [int(rng.integers(0, N_VALUES)) for _ in range(N_SLOTS)]
        target = int(rng.integers(0, N_SLOTS))
        chunks = []
        for j in range(N_SLOTS):
            if drop_gold and j == target:
                continue
            chunks.append(Chunk(token_ids=[markers[j], values[assign[j]]],
                                text=f"slot {j}", reliability=1.0,
                                source="gold" if j == target else "distractor",
                                doc_index=j, supports=("f0",) if j == target else ()))
        order = rng.permutation(len(chunks))
        chunks = [chunks[k] for k in order]
        gold = tuple(p for p, c in enumerate(chunks) if c.source == "gold")
        out.append(EvidenceExample(question_ids=[markers[target]],
                                   answer_ids=[values[assign[target]]],
                                   chunks=chunks, gold_positions=gold,
                                   mode="distractors" if drop_gold else "oracle"))
    return out


CFG = EvidenceModelConfig(
    vocab_size=VOCAB, d_model=64, n_layers=2, n_heads=4, d_ff=176,
    max_seq_len=16, d_enc=64, enc_layers=2, enc_heads=4, enc_d_ff=176,
    chunk_len=2, xattn_every=1, xattn_n_kv_heads=2, max_chunks=16,
    evidence_mode="tokens",
)


def run(drop_gold, steps, lr, n_examples, seed=0):
    tok = StubTokenizer(vocab_size=VOCAB)
    ex = lookup_examples(n_examples, seed=seed, drop_gold=drop_gold)
    col = EvidenceCollator(tok, bank_size=N_SLOTS, chunk_len=2, max_seq_len=16)
    batch = col(ex)
    torch.manual_seed(seed)
    m = EvidenceTransformerLM(CFG)
    return train_evidence_steps(m, [batch], steps=steps, lr=lr, device="cpu",
                                seed=seed, warmup_steps=20)


if __name__ == "__main__":
    floor = math.log(N_VALUES) / 2
    for steps, lr, n in [(400, 3e-3, 32), (600, 3e-3, 32), (600, 5e-3, 32)]:
        a = run(False, steps, lr, n)
        b = run(True, steps, lr, n)
        print(f"steps={steps} lr={lr} n={n} floor={floor:.3f} "
              f"oracle={a[-1]:.4f} blind={b[-1]:.4f} start={a[0]:.3f}", flush=True)
