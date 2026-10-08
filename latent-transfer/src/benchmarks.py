"""One place to resolve a benchmark name into train/val/test Example lists.

The training scripts were written against ProsQA and hard-coded its file layout.
Selecting a benchmark is a research decision that has already changed twice this
session, so it belongs behind one function rather than scattered through the
entry points.

Context lengths differ by more than an order of magnitude across these, which is
what decides whether the pipeline can save anything: the compute win comes from
compressing the input before the big model reads it, so a 62-token GSM8K prompt
leaves nothing to compress while a 1400-token HotpotQA context leaves a great
deal.
"""

from __future__ import annotations

from .data import Example

BENCHMARKS = ("prosqa", "gsm", "hotpot")


def load_benchmark(
    name: str,
    data_dir: str,
    n_train: int | None = None,
    n_val: int | None = None,
    n_test: int | None = None,
) -> tuple[list[Example], list[Example], list[Example]]:
    """Returns (train, val, test)."""
    if name == "prosqa":
        from .prosqa import load_prosqa

        return (
            load_prosqa(f"{data_dir}/prosqa_train.json", n_train),
            load_prosqa(f"{data_dir}/prosqa_valid.json", n_val),
            load_prosqa(f"{data_dir}/prosqa_test.json", n_test),
        )

    if name == "gsm":
        from .gsm import load_gsm

        return (
            load_gsm(f"{data_dir}/gsm_train.txt", n_train, max_steps=6),
            load_gsm(f"{data_dir}/gsm_valid.txt", n_val, max_steps=6),
            load_gsm(f"{data_dir}/gsm_test.txt", n_test, max_steps=6),
        )

    if name == "hotpot":
        from .hotpot import load_hotpot

        train = load_hotpot("train", n_train, max_steps=4)
        # HotpotQA's test split has no public answers, so the official
        # validation set is split: the front for model selection, the back for
        # the reported number. Disjoint, and never trained on.
        held = load_hotpot("validation", None, max_steps=4)
        nv = n_val or 200
        val = held[:nv]
        test = held[nv : nv + (n_test or 500)]
        return train, val, test

    raise ValueError(f"unknown benchmark {name!r}; expected one of {BENCHMARKS}")


def default_max_latent_stage(name: str) -> int:
    """Coconut needs one curriculum stage per reasoning step."""
    return {"prosqa": 6, "gsm": 6, "hotpot": 4}[name]
