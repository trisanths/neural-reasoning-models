"""GSM8K in the same Example format as ProsQA.

Chosen because ProsQA turned out to be the wrong instrument: the 0.5B does not
degrade with chain length there (0.723 at 3 hops, 0.833 at 6), so it has no
capacity deficit for a larger model to supply, and no architecture could have
demonstrated transfer. Multi-step arithmetic is where small models genuinely
run out of capacity rather than retrieval.

Source is the Internalize-CoT release the Coconut paper preprocesses, where a
line looks like:

    <question>||<<600*30/100=180>> <<600*10/100=60>> #### 360

so each ``<<...>>`` group is one reasoning step and the value after ``####`` is
the answer. The same '### ' answer marker as ProsQA is used downstream, so
evaluation and the curriculum need no special-casing.
"""

from __future__ import annotations

from .data import Example


def load_gsm(path: str, limit: int | None = None, max_steps: int | None = None) -> list[Example]:
    """Reads a gsm_*.txt file.

    ``max_steps`` drops longer chains, which keeps the curriculum's stage count
    bounded; Coconut needs one stage per reasoning step, and GSM8K has a long
    tail that would otherwise dominate the schedule.
    """
    out: list[Example] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "||" not in line or "####" not in line:
                continue
            q, rest = line.split("||", 1)
            steps_part, answer = rest.split("####", 1)
            steps = steps_part.strip().split()
            answer = answer.strip()
            if not steps or not answer:
                continue
            if max_steps is not None and len(steps) > max_steps:
                continue
            out.append(
                Example(
                    question=q.strip(),
                    steps=steps,
                    answer=answer,
                    n_hops=len(steps),
                    meta={"target": answer},
                )
            )
            if limit is not None and len(out) >= limit:
                break
    return out
