"""HotpotQA (distractor) in the Example format.

Chosen after measuring how the pipeline's economics depend on context length.
The saving comes from compressing the input before the big model reads it, so
short-prompt benchmarks defeat the architecture: at GSM8K's 62 tokens the
pipeline costs 10.5x the small model, while at HotpotQA's ~1200 it costs 1.53x
and is 11.9x cheaper than running the big model with chain of thought.

The distractor setting gives ten paragraphs of which eight are irrelevant, so
compressing to a few dozen vectors has real work to do rather than merely
discarding signal.

Reasoning steps are the annotated supporting facts, in the order they appear in
the context. They are genuine sentences from the input rather than free-form
rationales, which suits the Coconut curriculum: each stage replaces one of them
with a continuous thought.
"""

from __future__ import annotations

from .data import Example

ANSWER_MARKER = "### "


def _format_context(titles: list[str], sentences: list[list[str]]) -> str:
    parts = []
    for t, sents in zip(titles, sentences):
        parts.append(f"{t}: " + " ".join(s.strip() for s in sents))
    return "\n".join(parts)


def load_hotpot(
    split: str = "validation",
    limit: int | None = None,
    max_steps: int | None = 4,
    cache_dir: str | None = None,
) -> list[Example]:
    """Loads via HuggingFace datasets.

    ``max_steps`` caps the chain length; Coconut needs one curriculum stage per
    step, and a long tail of supporting facts would otherwise stretch the
    schedule for a handful of examples.
    """
    from datasets import load_dataset

    ds = load_dataset("hotpotqa/hotpot_qa", "distractor", split=split, cache_dir=cache_dir)
    out: list[Example] = []
    for row in ds:
        ctx = row["context"]
        titles, sentences = ctx["title"], ctx["sentences"]
        by_title = dict(zip(titles, sentences))

        sup = row["supporting_facts"]
        steps: list[str] = []
        for t, sid in zip(sup["title"], sup["sent_id"]):
            sents = by_title.get(t)
            if sents is None or sid >= len(sents):
                continue
            s = sents[sid].strip()
            if s:
                steps.append(s)
        if not steps:
            continue
        if max_steps is not None and len(steps) > max_steps:
            continue

        question = _format_context(titles, sentences) + "\n\nQuestion: " + row["question"].strip()
        answer = row["answer"].strip()
        if not answer:
            continue
        out.append(
            Example(
                question=question,
                steps=steps,
                answer=answer,
                n_hops=len(steps),
                meta={"target": answer, "level": row.get("level", "")},
            )
        )
        if limit is not None and len(out) >= limit:
            break
    return out
