"""The headline check: does a copy route reach the answer faster than a vocabulary route.

Each example carries a bank of eight documents, one of which states the answer:
a token id drawn fresh from a band of 120 that appears nowhere outside a bank.
Nothing in the question, the prior, or the vocabulary favours the right one, and
the id is different in every example, so there is nothing to memorize. Accuracy
is read off held-out banks the model never trains on.

The other documents are filler, deliberately. This is a unit test of the output
head, so it isolates selection: can the model emit a token it has just read,
rather than a plausible-looking token it has not. Choosing which document to
read is a separate ability that scripts/pointer_copy_bench.py measures on the
real invented systems.

The two arms share the seed, the data, the optimizer and the budget. The pointer
arm's parameters are drawn after every shared parameter, so the two models start
from identical values wherever they overlap. The only difference is whether
selection is an available output. Both step counts are printed, not just
asserted, because the number is the result.
"""

import pytest

from src.train.tests.pointer_fixtures import run_copy_probe

STEPS = 500
N_DOCS = 8
N_EXAMPLES = 32
N_BATCHES = 8


@pytest.fixture(scope="module")
def probes():
    kwargs = {"steps": STEPS, "n_docs": N_DOCS, "n_examples": N_EXAMPLES,
              "n_batches": N_BATCHES, "seed": 0}
    return {
        "pointer": run_copy_probe(True, **kwargs),
        "plain": run_copy_probe(False, **kwargs),
    }


def test_the_pointer_head_learns_to_copy_in_far_fewer_steps(probes, capsys):
    pointer, plain = probes["pointer"], probes["plain"]
    with capsys.disabled():
        print(f"\n  copy probe: {N_BATCHES} training batches of {N_EXAMPLES} "
              f"examples, {N_DOCS} documents, {STEPS} steps, seed 0")
        for name, run in (("with pointer", pointer), ("without pointer", plain)):
            print(f"    {name:16s} steps to held-out accuracy 1.0: "
                  f"{run['steps_to_threshold']}, "
                  f"held-out loss {run['final_loss']:.4f}, "
                  f"held-out accuracy {run['final_accuracy']:.3f}, "
                  f"best {run['best_accuracy']:.3f}")
    assert pointer["steps_to_threshold"] is not None, (
        "the pointer arm never reached full accuracy, which makes the comparison "
        f"meaningless: best was {pointer['best_accuracy']}"
    )
    if plain["steps_to_threshold"] is None:
        return  # the plain arm never got there at all, the strongest form of the result
    assert pointer["steps_to_threshold"] * 2 <= plain["steps_to_threshold"], (
        f"pointer {pointer['steps_to_threshold']} against plain {plain['steps_to_threshold']}"
    )


def test_the_pointer_arm_ends_at_a_lower_loss(probes):
    assert probes["pointer"]["final_loss"] < probes["plain"]["final_loss"]


def test_both_arms_actually_trained(probes):
    for run in probes.values():
        assert run["history"][0]["train_loss"] > run["history"][-1]["train_loss"]
