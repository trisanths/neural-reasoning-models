"""Turn invented systems into RL tasks and into training episodes.

Two presentations. Textbook in context puts the relevant pages in the prompt.
Textbook by retrieval leaves the pages in a document store the model must query,
which is the presentation that matches how a deployed reasoner would meet a
manual it has never read.
"""

from __future__ import annotations

import json

from src.skillacq.systems import Episode, generate_episode


def to_rl_episode(ep: Episode, n_context: int = 0) -> dict:
    """Shape one invented-system episode like the RL environment expects.

    Documents are the textbook pages. With n_context zero the pages arrive only
    through retrieval, so the model must find the rule before it can apply it.
    """
    return {
        "episode_id": ep.episode_id,
        "seed": ep.seed,
        "world": {"domain": f"skill_{ep.family}"},
        "n_context": n_context,
        "documents": [{"text": page} for page in ep.textbook],
        "questions": [
            {
                "qid": p["qid"],
                "text": p["text"],
                "answer": p["answer"],
                "plan": [p["qid"]],
                "type": p["kind"],
            }
            for p in ep.problems
        ],
    }


def write_jsonl(path: str, seeds, n_context: int = 0, n_problems: int = 8,
                family: str | None = None) -> dict:
    """Write RL-shaped episodes for a seed range. Returns simple statistics."""
    n_eps = 0
    n_q = 0
    with open(path, "w") as fh:
        for s in seeds:
            ep = generate_episode(s, family=family, n_problems=n_problems)
            rec = to_rl_episode(ep, n_context=n_context)
            fh.write(json.dumps(rec) + "\n")
            n_eps += 1
            n_q += len(rec["questions"])
    return {"episodes": n_eps, "questions": n_q, "path": path}
