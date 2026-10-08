"""Oracle against distractor-only: the model reads the bank or it cannot answer.

Every example carries the same question, so the working sequence holds no
information about which answer is right. The answer token appears once, in
one gold chunk. With the gold chunk in the bank a tiny model drives the loss
to near zero; with the gold chunk removed the best it can do is the uniform
marginal over the answer set, and the gap between the two runs is the
evidence path doing work.
"""

import math

import torch

from src.train.evidence_data import EvidenceCollator
from src.train.evidence_model import EvidenceModelConfig, EvidenceTransformerLM
from src.train.evidence_trainer import train_evidence_steps
from src.train.tests.evidence_fixtures import StubTokenizer, marker_examples

N_EXAMPLES = 8
BANK = 8
CHUNK_LEN = 8
VOCAB = 128

OVERFIT_CFG = EvidenceModelConfig(
    vocab_size=VOCAB, d_model=64, n_layers=2, n_heads=4, d_ff=176,
    max_seq_len=32, d_enc=64, enc_layers=1, enc_heads=4, enc_d_ff=176,
    chunk_len=CHUNK_LEN, xattn_every=1, xattn_n_kv_heads=2, max_chunks=16,
    evidence_mode="tokens",
)

# Two supervised positions per example, the answer token and the closing
# eot. The eot is free, so a model that cannot see the evidence pays
# log(N_EXAMPLES) on one of the two positions and nothing on the other.
BLIND_FLOOR = math.log(N_EXAMPLES) / 2


def run(distractors_only: bool, steps: int = 400, seed: int = 0) -> list:
    tok = StubTokenizer(vocab_size=VOCAB)
    examples = marker_examples(N_EXAMPLES, BANK, CHUNK_LEN, VOCAB, seed=seed,
                               distractors_only=distractors_only)
    collator = EvidenceCollator(tok, bank_size=BANK, chunk_len=CHUNK_LEN,
                                max_seq_len=OVERFIT_CFG.max_seq_len)
    batch = collator(examples)
    torch.manual_seed(seed)
    model = EvidenceTransformerLM(OVERFIT_CFG)
    return train_evidence_steps(model, [batch], steps=steps, lr=3e-3,
                                device="cpu", seed=seed, warmup_steps=20)


def test_oracle_bank_lets_the_model_answer():
    losses = run(distractors_only=False)
    assert losses[-1] < 0.35 * BLIND_FLOOR, losses[-1]
    assert losses[-1] < losses[0]


def test_distractor_only_bank_leaves_the_model_at_the_blind_floor():
    losses = run(distractors_only=True)
    assert losses[-1] > 0.75 * BLIND_FLOOR, losses[-1]


def test_the_gap_between_the_two_regimes_is_large():
    oracle = run(distractors_only=False)[-1]
    blind = run(distractors_only=True)[-1]
    assert blind - oracle > 0.5 * BLIND_FLOOR, (oracle, blind)


def test_overfit_run_is_deterministic():
    a = run(distractors_only=False, steps=40, seed=3)
    b = run(distractors_only=False, steps=40, seed=3)
    assert a == b
    c = run(distractors_only=False, steps=40, seed=4)
    assert a != c


def test_a_trained_model_can_still_be_gated_off():
    """After training on evidence, forcing the gate shut removes the answer."""
    tok = StubTokenizer(vocab_size=VOCAB)
    examples = marker_examples(N_EXAMPLES, BANK, CHUNK_LEN, VOCAB, seed=0)
    collator = EvidenceCollator(tok, bank_size=BANK, chunk_len=CHUNK_LEN,
                                max_seq_len=OVERFIT_CFG.max_seq_len)
    batch = collator(examples)
    torch.manual_seed(0)
    model = EvidenceTransformerLM(OVERFIT_CFG)
    train_evidence_steps(model, [batch], steps=400, lr=3e-3, device="cpu", seed=0,
                         warmup_steps=20)
    model.eval()
    with torch.no_grad():
        _, open_loss = model(batch.input_ids, batch.evidence_ids,
                             batch.evidence_mask, batch.reliability,
                             batch.chunk_mask, targets=batch.targets)
        _, shut_loss = model(batch.input_ids, batch.evidence_ids,
                             batch.evidence_mask, batch.reliability,
                             batch.chunk_mask, targets=batch.targets,
                             gate_override=0.0)
    assert float(open_loss) < 0.35 * BLIND_FLOOR
    assert float(shut_loss) > float(open_loss) + 0.5 * BLIND_FLOOR
