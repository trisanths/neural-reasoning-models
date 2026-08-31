"""Which world header gives the checkpoint its best shot.

The gate says the header is not optional. It does not say which domain string
to put in it, and this checkpoint trained on one family per domain. Running the
same items under several headers and keeping the best is the condition A is
then reported in, so A is not penalised for a header choice.
"""
from __future__ import annotations
import collections, gzip, json, sys, time

from src.evals.interactive import make_checkpoint_step_fn, generate_with_retrieval
from src.train.data import render_world_preamble
from src.train.tokenizer import load_tokenizer
from src.norm.cmpwork.runa import CKPT, TOK, load_items
from src.norm.cmpwork.grade import forced

DOMAINS = ["", "unknown", "skill_substitution_rule", "skill_exception_rule",
           "skill_threshold_rule", "worldgen"]


def main():
    items = load_items("results/norm/compare/items.jsonl.gz", 0)
    by = collections.defaultdict(list)
    for it in items:
        by[it["shape"]].append(it)
    probe = []
    for sh in ("lookup", "lookup_general", "classify", "compose"):
        probe.extend(by[sh][:8])
    tok = load_tokenizer(TOK)
    step_fn, _m, _s = make_checkpoint_step_fn(CKPT, "cuda")
    sid = tok.special_ids
    out = {}
    for d in DOMAINS:
        world = {} if d == "" else {"domain": d}
        head = [sid["<|world|>"], *tok.encode(render_world_preamble(world))]
        rounds, hits, none, hedge, n = 0, 0, 0, 0, 0
        t0 = time.time()
        for it in probe:
            prompt = head + [sid["<|q|>"], *tok.encode(it["question"])]
            chunks = [{"text": p, "reliability": 1.0} for p in it["pages"]]
            r = generate_with_retrieval(step_fn, tok, chunks, prompt,
                                        max_rounds=6, max_new_tokens=256, seed=0)
            g = forced(r["answer_text"], it["options"], it["gold"])
            rounds += r["n_rounds"]; n += 1
            hits += g["strict_correct"]; none += g["named_none"]; hedge += g["hedged"]
        out[d or "(empty world dict)"] = {
            "n": n, "mean_rounds": round(rounds / n, 3),
            "strict_acc": round(hits / n, 4), "none_rate": round(none / n, 4),
            "hedge_rate": round(hedge / n, 4), "seconds": round(time.time() - t0, 1)}
        print(d or "(empty)", json.dumps(out[d or "(empty world dict)"]), flush=True)
    with open("results/norm/compare/header_ablation.json", "w") as fh:
        json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
