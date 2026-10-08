"""Task registry, so scripts stay task-agnostic.

Both tasks expose the same interface (an ``Example`` with question/steps/answer
and a tokenizer with the marker ids), which is all the curriculum, Coconut loop
and pipeline depend on.
"""

from __future__ import annotations

from .compose import ComposeGenerator, ComposeTokenizer
from .data import ProsQAGenerator, Tokenizer, load, save

TASKS = ("prosqa", "compose")


def get_tokenizer(task: str):
    if task == "prosqa":
        return Tokenizer()
    if task == "compose":
        return ComposeTokenizer()
    raise ValueError(f"unknown task {task!r}; expected one of {TASKS}")


def chance_level(task: str) -> float:
    if task == "prosqa":
        return 0.5  # two candidates
    if task == "compose":
        return 0.1  # ten possible answers
    raise ValueError(f"unknown task {task!r}")


def make_generator(task: str, **kw):
    if task == "prosqa":
        return ProsQAGenerator(**kw)
    if task == "compose":
        return ComposeGenerator(**kw)
    raise ValueError(f"unknown task {task!r}")


__all__ = ["TASKS", "get_tokenizer", "chance_level", "make_generator", "load", "save"]
