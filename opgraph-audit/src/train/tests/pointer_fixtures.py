"""Shared fixtures for the pointer head tests.

The copy task built here is the smallest thing that has the shape of the
measured failure. Every example carries a bank of documents, one of which
states the answer, and the answer is a token id drawn fresh per example from a
band that occurs nowhere outside a bank. That is the routing table of
src/skillacq/simple.py with the English removed.

The freshness is the part that makes the probe mean anything. If one question
always led to one answer, both arms could win by memorizing it into the
lm_head and never reading the bank at all, which is precisely the behaviour
under investigation. Drawing the answer per example, and reading accuracy off
held-out banks, leaves only one way through: emit the token you just read.
"""

import os
from pathlib import Path

import pytest
import torch

from src.train.model import ModelConfig, TransformerLM
from src.train.pointer_data import PointerCollator, PointerExample

SPECIALS = ["<|doc|>", "<|q|>", "<|a|>", "<|retrieve|>", "<|result|>",
            "<|world|>", "<|eot|>"]

VOCAB = 256
ARROW = 10           # opens a bank entry
ASK = 11             # opens the question
KEY_BASE, N_KEYS = 20, 60
FILLER_BASE, N_FILLER = 80, 20
VALUE_BASE, N_VALUES = 100, 120  # the rare band, never seen outside a bank


class IdTokenizer:
    """The bare interface the collator needs: special ids and an encoder.

    Examples in this module are built from raw token ids, so encode is only
    reached when an example carries answer_text, which none of them do.
    """

    def __init__(self, vocab_size: int = VOCAB):
        self.vocab_size = vocab_size
        self.special_ids = {name: i for i, name in enumerate(SPECIALS)}

    def encode(self, text: str) -> list:
        return [ord(c) % self.vocab_size for c in text]

    def decode(self, ids: list) -> str:
        return " ".join(str(i) for i in ids)


def find_tokenizer() -> Path | None:
    """The trained 32k BPE, if this machine has one.

    Copyability statistics are a property of the tokenization, so the family
    tests that measure them want the real byte level BPE rather than a stub
    that splits on whitespace and would call an answer uncopyable because the
    page happens to put a full stop after it. The tests that check layout,
    masking and gradients use raw ids and need nothing of the kind.
    """
    candidates = [
        os.environ.get("TOKENIZER_JSON"),
        Path.home() / "data" / "tokenizer_v2.json",
        Path.home() / "runs" / "tokenizer_v2" / "tokenizer_v2.json",
        Path.home() / "runs" / "smoke-001" / "tokenizer.json",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    return None


def real_tokenizer():
    from src.train.tokenizer import load_tokenizer

    path = find_tokenizer()
    if path is None:
        raise RuntimeError("no trained tokenizer on this machine")
    return load_tokenizer(str(path))


requires_tokenizer = pytest.mark.skipif(
    find_tokenizer() is None,
    reason="needs a trained byte level BPE; set TOKENIZER_JSON to point at one",
)


def copy_task_examples(n_docs: int = 8, seed: int = 0, filler: int = 2,
                       n_examples: int | None = None) -> list:
    """A bank of documents, one of which states the answer, and a question.

    The key and the value are drawn fresh per example from pools far larger
    than a bank, so no value belongs to any particular key and no key belongs
    to any particular example. That is what makes the vocabulary route
    expensive: to answer without pointing, the lm_head has to produce one of
    120 rare ids on the strength of having read it, while the copy route only
    has to select the position it is sitting at. It is the small hermetic
    version of an invented system whose words are regenerated every episode.

    The other documents are filler, deliberately. This is a unit test of the
    output head, so it isolates selection: can the model emit a token it has
    read, rather than a plausible-looking token it has not. Choosing which
    document to read is a different ability, it needs a relational match that
    a two layer model does not learn at this budget, and it is what
    scripts/pointer_copy_bench.py measures on the real invented systems.
    """
    gen = torch.Generator().manual_seed(seed)
    n_examples = n_docs if n_examples is None else n_examples
    examples = []
    for i in range(n_examples):
        key = int(torch.randint(0, N_KEYS, (1,), generator=gen)) + KEY_BASE
        value = int(torch.randint(0, N_VALUES, (1,), generator=gen)) + VALUE_BASE
        gold = int(torch.randint(0, n_docs, (1,), generator=gen))
        documents = []
        for j in range(n_docs):
            noise = (torch.randint(0, N_FILLER, (filler + 1,), generator=gen)
                     + FILLER_BASE).tolist()
            if j == gold:
                documents.append([ARROW, key, value] + noise[:filler])
            else:
                documents.append([ARROW, noise[0], noise[1]] + noise[2:])
        examples.append(PointerExample(
            document_ids=documents,
            question_ids=[ASK, key],
            answer_ids=[value],
            copy_scope="evidence",
            family="copy_probe",
            episode_id=f"probe-{i}",
        ))
    return examples


def copy_task_batch(n_docs: int = 8, seed: int = 0, max_seq_len: int = 256,
                    n_examples: int | None = None):
    tokenizer = IdTokenizer()
    collator = PointerCollator(tokenizer, max_seq_len=max_seq_len, copy_scope="evidence")
    return collator(copy_task_examples(n_docs=n_docs, seed=seed, n_examples=n_examples))


def probe_config(pointer: dict | None = None, max_seq_len: int = 256) -> ModelConfig:
    return ModelConfig(
        vocab_size=VOCAB, d_model=64, n_layers=2, n_heads=4, d_ff=176,
        max_seq_len=max_seq_len, pointer=pointer,
    )


def answer_accuracy(log_probs: torch.Tensor, targets: torch.Tensor,
                    ignore_index: int = -100, first_only: bool = False) -> float:
    """Fraction of supervised positions whose argmax is the target.

    first_only scores the answer token alone rather than averaging it with the
    closing <|eot|>, which any model learns immediately and which would
    otherwise put a floor of one half under a model that never answers.
    """
    if first_only:
        log_probs, targets = log_probs[:, :1], targets[:, :1]
    keep = targets != ignore_index
    if not bool(keep.any()):
        return float("nan")
    predicted = log_probs.argmax(dim=-1)
    return float((predicted[keep] == targets[keep]).float().mean())


def probe_step(model, batch, with_pointer: bool):
    kwargs = {"select": batch.authored_positions}
    if with_pointer:
        kwargs["evidence_positions"] = batch.evidence_positions
    return model(batch.input_ids, batch.authored_targets, **kwargs)


def run_copy_probe(with_pointer: bool, steps: int = 500, lr: float = 3e-3,
                   seed: int = 0, n_docs: int = 8, n_examples: int = 32,
                   n_batches: int = 8, threshold: float = 1.0,
                   eval_every: int = 10, device: str = "cpu") -> dict:
    """Train one tiny model on the copy task and report when it got there.

    Accuracy is measured on a held-out batch of banks the model never trains
    on, not on the training batch. Held out is the only measurement that means
    anything here: with a fixed batch both arms eventually memorize which of
    eight rare ids goes with which sequence, and memorizing is the behaviour
    the pointer head exists to make unnecessary. Generalizing means having
    learned to find the key and take what follows it, which is the thing.

    Both arms share the seed, the data, the optimizer and the budget. The
    pointer head's parameters are drawn after every other parameter, so the two
    models start from identical values everywhere they overlap; the only
    difference is whether selection is available as an output route.

    steps_to_threshold is the first evaluated step at which held-out answer
    accuracy reaches `threshold`, or None if it never does within the budget.
    """
    shared = {"n_docs": n_docs, "n_examples": n_examples}
    train_batches = [copy_task_batch(seed=seed * 1000 + i, **shared)
                     for i in range(n_batches)]
    held_out = copy_task_batch(seed=seed * 1000 + 90210, **shared)
    if device != "cpu":
        train_batches = [b.to(device) for b in train_batches]
        held_out = held_out.to(device)
    torch.manual_seed(seed)
    model = TransformerLM(probe_config(pointer={} if with_pointer else None)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0)

    history = []
    steps_to_threshold = None
    best = 0.0
    accuracy = 0.0
    for step in range(1, steps + 1):
        batch = train_batches[(step - 1) % len(train_batches)]
        out, loss = probe_step(model, batch, with_pointer)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % eval_every == 0 or step == steps:
            with torch.no_grad():
                eval_out, eval_loss = probe_step(model, held_out, with_pointer)
            accuracy = answer_accuracy(eval_out, held_out.authored_targets, first_only=True)
            best = max(best, accuracy)
            history.append({"step": step, "train_loss": float(loss.detach()),
                            "held_out_loss": float(eval_loss), "accuracy": accuracy})
            if steps_to_threshold is None and accuracy >= threshold:
                steps_to_threshold = step
    return {
        "with_pointer": with_pointer,
        "steps": steps,
        "steps_to_threshold": steps_to_threshold,
        "final_loss": history[-1]["held_out_loss"],
        "final_train_loss": history[-1]["train_loss"],
        "final_accuracy": history[-1]["accuracy"],
        "best_accuracy": best,
        "history": history,
    }
