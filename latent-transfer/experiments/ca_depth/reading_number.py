"""The reading number: teacher-forced single-step rule application, page in context.

The existing three-condition test (scripts/skill_rule_test.py) samples from an RL
policy with retrieval in the loop, so its 0.680 folds together query formulation,
retrieval, sampling, and reading. This isolates reading: the page is placed in the
prompt, <|a|> is forced so the model cannot retrieve, and the answer is greedy.

Four conditions on the computation-free simple families (held-out seeds):
  doc        textbook pages in context under <|doc|>      (the n_context path in build_prompt)
  wrong_doc  a different invented system's pages
  no_doc     no pages at all
  result     the same pages injected as <|retrieve|><|result|>page, the retrieval-channel
             format the model was trained to read from. If doc << result on identical
             text, the in-context degradation is a format mismatch, not a reading failure.

Run from the decoupled-reasoner repo root:
  python reading_number.py --checkpoint ckpt/rlsimple_final.pt --tokenizer data/tokenizer_v2.json \
      --start 900000 --count 200 --out results_reading/rlsimple.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import torch

sys.path.insert(0, ".")
from src.evals.mc import load_checkpoint_model            # noqa: E402
from src.rl.env import build_prompt                        # noqa: E402
from src.skillacq.episodes import to_rl_episode            # noqa: E402
from src.skillacq.simple import SIMPLE_FAMILIES            # noqa: E402
from src.skillacq.systems import generate_episode          # noqa: E402
from src.train.tokenizer import load_tokenizer             # noqa: E402

from src.evals.naturalized import contains_answer     # noqa: E402  (the grader RL used)


def logits_of(model, ids: torch.Tensor) -> torch.Tensor:
    out = model(ids)
    if torch.is_tensor(out):
        return out
    for attr in ("logits",):
        if hasattr(out, attr):
            return getattr(out, attr)
    if isinstance(out, (tuple, list)):
        return out[0]
    raise TypeError(type(out))


@torch.no_grad()
def greedy(model, ids: list[int], eot: int, max_new: int, dev, stop_ids=()) -> tuple[list[int], bool]:
    x = torch.tensor([ids], device=dev)
    out = []
    for _ in range(max_new):
        lg = logits_of(model, x)[0, -1]
        t = int(lg.argmax())
        if t == eot:
            return out, True
        if t in stop_ids:
            return out, False
        out.append(t)
        x = torch.cat([x, torch.tensor([[t]], device=dev)], 1)
    return out, False


def make_prompt(cond: str, ep: dict, wrong_pages: list[str], q: dict, tok) -> list[int]:
    sid = tok.special_ids
    if cond == "doc":
        e = dict(ep); e["n_context"] = len(ep["documents"])
        return build_prompt(e, q, tok)
    if cond == "wrong_doc":
        e = dict(ep); e["documents"] = [{"text": p} for p in wrong_pages]; e["n_context"] = len(wrong_pages)
        return build_prompt(e, q, tok)
    if cond == "no_doc":
        e = dict(ep); e["n_context"] = 0
        return build_prompt(e, q, tok)
    if cond == "result":
        # world preamble + question first (as the policy would see it), then an empty
        # retrieval whose result is the page, exactly the channel the model reads from
        e = dict(ep); e["n_context"] = 0
        ids = build_prompt(e, q, tok)
        for p in ep["documents"]:
            ids.append(sid["<|retrieve|>"])
            ids.append(sid["<|result|>"])
            ids.extend(tok.encode(p["text"]))
        return ids
    raise ValueError(cond)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--start", type=int, default=900000)
    ap.add_argument("--count", type=int, default=200)
    ap.add_argument("--n-problems", type=int, default=4)
    ap.add_argument("--max-new", type=int, default=24)
    ap.add_argument("--max-prompt", type=int, default=1500)
    ap.add_argument("--out", required=True)
    ap.add_argument("--free-run", action="store_true",
                    help="do not force <|a|>; let the policy decide to answer, retrieve, or ramble. "
                         "Measures well-formedness the way the RL harness saw it. Retrieval is "
                         "still disabled (no service), so <|retrieve|> just ends the answer.")
    ap.add_argument("--families", default="simple",
                    help="'simple' (threshold/substitution/exception, computation-free), "
                         "'arith' (binary_op/units/procedure, the families at 0.000), or a comma list")
    a = ap.parse_args()
    dev = "cuda"
    tok = load_tokenizer(a.tokenizer)
    sid = tok.special_ids
    model, state = load_checkpoint_model(a.checkpoint, dev)
    if a.families == "simple":
        fams = sorted(SIMPLE_FAMILIES)
    elif a.families == "arith":
        fams = ["binary_op", "units", "procedure"]
    else:
        fams = a.families.split(",")
    conds = ["doc", "wrong_doc", "no_doc", "result"]
    stats = {c: {"n": 0, "correct": 0, "well_formed": 0, "prompt_toks": 0, "examples": [], "by_fam": {}} for c in conds}
    t0 = time.time()
    for i, s in enumerate(range(a.start, a.start + a.count)):
        fam = fams[s % len(fams)]
        ep = to_rl_episode(generate_episode(s, family=fam, n_problems=a.n_problems), n_context=0)
        other = generate_episode(s + 777000, family=fams[(s + 1) % len(fams)], n_problems=a.n_problems)
        for q in ep["questions"]:
            for c in conds:
                ids = make_prompt(c, ep, list(other.textbook), q, tok)
                if len(ids) > a.max_prompt:
                    continue
                if a.free_run:
                    out, wf = greedy(model, ids, sid["<|eot|>"], a.max_new * 3, dev, stop_ids=(sid["<|retrieve|>"],))
                    # answer = whatever follows the first <|a|> the policy chose to emit
                    a_id = sid["<|a|>"]
                    pred = tok.decode(out[out.index(a_id) + 1:]) if a_id in out else ""
                    wf = wf and (a_id in out)
                else:
                    ids = ids + [sid["<|a|>"]]
                    out, wf = greedy(model, ids, sid["<|eot|>"], a.max_new, dev)
                    pred = tok.decode(out)
                ok = contains_answer(pred, q["answer"])
                st = stats[c]
                st["n"] += 1; st["correct"] += int(ok); st["well_formed"] += int(wf); st["prompt_toks"] += len(ids)
                bf = st["by_fam"].setdefault(fam, {"n": 0, "correct": 0}); bf["n"] += 1; bf["correct"] += int(ok)
                if len(st["examples"]) < 6:
                    st["examples"].append({"fam": fam, "q": q["text"][:120], "gold": q["answer"], "pred": pred[:80], "ok": ok, "wf": wf})
        if i % 20 == 0:
            print(f"[{i}/{a.count}] " + " ".join(f"{c}={stats[c]['correct']}/{stats[c]['n']}" for c in conds)
                  + f" t={time.time()-t0:.0f}s", flush=True)
    summary = {c: {"acc": stats[c]["correct"] / max(stats[c]["n"], 1),
                   "well_formed": stats[c]["well_formed"] / max(stats[c]["n"], 1),
                   "n": stats[c]["n"],
                   "mean_prompt_toks": stats[c]["prompt_toks"] / max(stats[c]["n"], 1),
                   "by_fam": {f: round(v["correct"] / max(v["n"], 1), 3) for f, v in stats[c]["by_fam"].items()}} for c in conds}
    print("SUMMARY", json.dumps(summary, indent=1), flush=True)
    with open(a.out, "w") as f:
        json.dump({"checkpoint": a.checkpoint, "start": a.start, "count": a.count,
                   "summary": summary, "stats": stats}, f, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
