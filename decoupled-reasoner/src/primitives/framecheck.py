"""Does this suite's harness reproduce a number another harness published?

WHY.

The native-frame profile reads at chance on all seven faculties, and the
checkpoint emits a near-constant string with 0.85 to 1.00 of replies
naming no candidate. That is exactly the shape the wording ablation saw
in its DISTANT renderers, not its native one, even though the sentence
frame here was copied from the native one. Two explanations fit:

  1. the faculties really are absent in the native frame too, or
  2. this suite's harness does not put the model in the trained
     condition, so its "native frame" is native at the sentence level
     and foreign at the prompt level.

Nothing in the suite can tell those apart, and reporting the native-frame
zeros without settling it would repeat the exact mistake the native-frame
control was built to correct.

THE CHECK.

`src/disc/TEMPLATE.md` publishes forced-choice substitution_rule at 0.970
in the native wording against a 0.200 floor, measured through the
ablation's own harness. This module poses the identical task, built from
`src.skillacq.simple.SubstitutionRule` so the words and the gold come
from the same generator, and scores it through THIS suite's model
adapter and forced-choice channel.

  reproduces ~0.970  the harness is faithful, and the native-frame zeros
                     are a real reading about the faculties.
  reads ~0.200       the harness is the problem. Both columns of the
                     profile are then measuring prompt-format mismatch,
                     and no faculty claim survives until it is fixed.

KNOWN DIVERGENCES, WHICH THIS IS MEANT TO PRICE.

Two are already visible by inspection of `adapters.build_prompt_ids`
against `src.rl.env.build_prompt`:

  answer marker  training ends the prompt at the question and lets the
                 policy emit <|a|> or <|retrieve|> itself. This suite
                 appends <|a|>, so the model is placed in answer position
                 and never gets to retrieve, which is the behaviour the
                 RL stage spent its budget teaching.
  world domain   training passes the episode's own world dict. This suite
                 passes {"domain": "primitive_suite"}, a string no
                 training episode ever carried.

Both arms below are posed through the same adapter, so the comparison
isolates the sentence frame from those two.
"""

from __future__ import annotations

import random
import re

from src.disc.renderers import SIMPLE_RENDERERS
from src.primitives.common import parse_labels, proportion
from src.skillacq.simple import SIMPLE_FAMILIES

FAMILY = "substitution_rule"
PUBLISHED = {"native": 0.970, "personnel": 0.045, "abstract": 0.045,
             "inventory": 0.015}
CHANCE = 0.200


def build(n_systems: int = 10, per_system: int = 4, seed: int = 0,
          renderer: str = "native") -> list[dict]:
    """The ablation's own task, rendered by one of its own renderers.

    Five candidates, the four table values plus the unlisted default, so
    the floor is 0.200 exactly as TEMPLATE.md reports it.
    """
    rend = SIMPLE_RENDERERS[renderer]
    out = []
    for i in range(n_systems):
        rng = random.Random(seed * 1009 + i)
        sysm = SIMPLE_FAMILIES[FAMILY](rng)
        pages = rend.describe(FAMILY, sysm)
        options = list(dict.fromkeys(list(sysm.values) + [sysm.rng_default]))
        if len(options) < 5:
            continue
        for p in sysm.problems(rng, per_system):
            # problems() emits the native sentence but no key field, and
            # every renderer's question() needs one, so it is read back
            # out of the native text. For the native renderer this
            # reproduces problems()["text"] verbatim, which is asserted
            # below, and for a distant renderer it is the same key said
            # another way.
            m = re.match(r"A (\S+) request arrives", p["text"])
            if not m:
                continue
            p = {**p, "key": m.group(1)}
            q = rend.question(FAMILY, sysm, p)
            if renderer == "native" and q != p["text"]:
                raise AssertionError(
                    "native renderer drifted from the generator's own "
                    f"wording:\n  {q!r}\n  {p['text']!r}")
            if p["answer"] not in options:
                continue
            # Two prompt layouts, because that is the thing under test.
            # "docs" is the training layout: pages as <|doc|> blocks
            # before <|q|>, question alone in the question segment.
            # "inline" is what this suite has been doing: pages pasted
            # into the question, which makes build_prompt_ids drop them
            # as duplicates so no <|doc|> block is emitted at all.
            chunks = [{"id": f"p{j}", "text": t} for j, t in enumerate(pages)]
            out.append({
                "question": q, "chunks": chunks, "layout": "docs",
                "options": options, "gold": options.index(p["answer"]),
                "renderer": renderer})
            out.append({
                "question": "\n\n".join(pages) + "\n\n" + q,
                "chunks": chunks, "layout": "inline",
                "options": options, "gold": options.index(p["answer"]),
                "renderer": renderer})
    return out


def run_generation(answer_fn, n_systems: int = 12, per_system: int = 4,
                   seed: int = 0, renderers=("native", "inventory")) -> dict:
    """The published measurement, reproduced the way it was actually made.

    TEMPLATE.md's `forced` column is not likelihood scoring. It reads the
    model's generated text and requires exactly one distinct candidate
    named, which is this suite's strict rule applied to a rollout. And the
    rollout there is the trained one, where the policy retrieves before it
    answers. So this arm takes an answer_fn built from
    src.evals.interactive.make_retrieval_answer_fn, which is the shape the
    runner was documented to accept all along, and grades it strictly.
    """
    out: dict = {}
    for rname in renderers:
        tasks = [t for t in build(n_systems, per_system, seed, rname)
                 if t["layout"] == "docs"]
        hits = none = hedge = 0
        for t in tasks:
            text = str(answer_fn(t["question"], t["chunks"]))
            named = parse_labels(text, t["options"])
            gold = t["options"][t["gold"]]
            hits += int(len(named) == 1 and named[0] == gold)
            none += int(len(named) == 0)
            hedge += int(len(named) > 1)
        n = len(tasks)
        stat = proportion(hits, n, CHANCE, f"{rname}/generation")
        stat["published"] = PUBLISHED.get(rname)
        stat["delta_vs_published"] = (round(stat["acc"] - PUBLISHED[rname], 3)
                                      if rname in PUBLISHED else None)
        stat["named_nothing"] = round(none / n, 3) if n else None
        stat["hedge"] = round(hedge / n, 3) if n else None
        out[f"{rname}/generation"] = stat
    nat = out.get("native/generation")
    if nat is not None:
        out["verdict"] = (
            "harness faithful: the retrieval rollout reproduces the "
            "published native score"
            if nat["acc"] >= 0.5 * PUBLISHED["native"] else
            "still short of the published native score")
    return out


def run(model, n_systems: int = 10, per_system: int = 4, seed: int = 0,
        renderers=("native", "inventory")) -> dict:
    """Forced choice on each renderer, reported against the published row."""
    out: dict = {}
    for rname in renderers:
        tasks = build(n_systems, per_system, seed, rname)
        for layout in ("docs", "inline"):
            sel = [t for t in tasks if t["layout"] == layout]
            hits = 0
            for t in sel:
                pick = model.choose(t["question"], t["chunks"], t["options"])
                hits += int(int(pick) == t["gold"])
            stat = proportion(hits, len(sel), CHANCE,
                              f"{rname}/{layout}/forced")
            stat["published"] = PUBLISHED.get(rname)
            stat["delta_vs_published"] = (
                round(stat["acc"] - PUBLISHED[rname], 3)
                if rname in PUBLISHED else None)
            out[f"{rname}/{layout}"] = stat
    nat = max((out[k] for k in out if k.startswith("native")),
              key=lambda s: s["acc"], default=None)
    if nat is not None:
        # The verdict, stated rather than left to the reader. Half the
        # published native score is the line: above it the harness is
        # reproducing the effect, below it the harness is the finding.
        out["verdict"] = ("harness faithful in at least one layout"
                          if nat["acc"] >= 0.5 * PUBLISHED["native"]
                          else "harness does not reproduce the published "
                               "native score, so the profile measures prompt "
                               "format and not faculties")
    return out


def render(rep: dict) -> str:
    lines = ["# Harness fidelity against the published wording ablation", "",
             f"Family {FAMILY}, five candidates, chance {CHANCE:.3f}. "
             f"Posed through this suite's adapter and forced-choice channel.",
             "",
             "| renderer | this harness | published | delta |",
             "|---|---|---|---|"]
    for name, s in rep.items():
        if not isinstance(s, dict):
            continue
        pub = s.get("published")
        lines.append(
            f"| {name} | {s['acc']:.3f} [{s['ci_lo']:.3f}, {s['ci_hi']:.3f}] "
            f"n={s['n']} | " + (f"{pub:.3f}" if pub is not None else "-")
            + " | " + (f"{s['delta_vs_published']:+.3f}"
                       if s.get("delta_vs_published") is not None else "-")
            + " |")
    if rep.get("mean_retrieval_rounds") is not None:
        lines += ["", f"Mean retrieval rounds per item: "
                  f"{rep['mean_retrieval_rounds']}."]
    if "verdict" in rep:
        lines += ["", f"Verdict: {rep['verdict']}."]
    return "\n".join(lines) + "\n"


def make_trained_answer_fn(ckpt: str, tokenizer_path: str, device: str = "cuda",
                           max_rounds: int = 4, max_new_tokens: int = 256,
                           seed: int = 0):
    """predict(question, chunks) in the condition the checkpoint was trained in.

    src.evals.interactive.make_retrieval_answer_fn builds its prompt as
    <|q|> question, with no world header. Every training prompt starts
    <|world|> preamble, and on this checkpoint the header is not cosmetic:
    without it the policy issues no retrieval at all, never emits <|a|>,
    and runs to the token cap emitting degenerate filler. With it, the
    same item retrieves once, stops at <|eot|>, and names the gold. So the
    header is restored here, matching src.rl.env.build_prompt.
    """
    from src.evals.interactive import (make_checkpoint_step_fn,
                                       generate_with_retrieval)
    from src.train.data import render_world_preamble
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(tokenizer_path)
    step_fn, _model, _state = make_checkpoint_step_fn(ckpt, device)
    sid = tok.special_ids
    head = [sid["<|world|>"], *tok.encode(render_world_preamble({}))]

    def answer_fn(question: str, chunks) -> str:
        prompt = head + [sid["<|q|>"], *tok.encode(str(question))]
        out = generate_with_retrieval(step_fn, tok, list(chunks), prompt,
                                      max_rounds=max_rounds,
                                      max_new_tokens=max_new_tokens, seed=seed)
        answer_fn.rounds.append(out["n_rounds"])
        return out["answer_text"]

    answer_fn.rounds = []
    return answer_fn


def main(argv=None) -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--systems", type=int, default=12)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    a = ap.parse_args(argv)

    afn = make_trained_answer_fn(a.ckpt, a.tokenizer, a.device,
                                 max_new_tokens=a.max_new_tokens,
                                 seed=a.seed)
    rep = run_generation(afn, n_systems=a.systems, per_system=4, seed=a.seed)
    rep["mean_retrieval_rounds"] = (
        round(sum(afn.rounds) / len(afn.rounds), 3) if afn.rounds else None)
    text = render(rep)
    print(text)
    if a.out:
        from pathlib import Path
        o = Path(a.out); o.parent.mkdir(parents=True, exist_ok=True)
        o.with_suffix(".md").write_text(text)
        o.with_suffix(".json").write_text(json.dumps(rep, indent=2,
                                                     default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
