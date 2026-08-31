from __future__ import annotations
import json
from src.evals.interactive import make_checkpoint_step_fn, generate_with_retrieval
from src.train.data import render_world_preamble
from src.train.tokenizer import load_tokenizer
from src.norm.cmpwork.runa import CKPT, TOK, load_items

items = load_items("results/norm/compare/items.jsonl.gz", 0)
by = {}
for it in items:
    by.setdefault(it["shape"], []).append(it)

print("### three questions and their pages")
for sh in ("lookup", "lookup_general", "classify"):
    it = by[sh][0]
    print("---", sh, it["fid"])
    print("Q:", it["question"])
    print("P0:", it["pages"][0][:400].replace("\n", " | "))
    print("gold:", it["gold"], "opts:", it["options"])

tok = load_tokenizer(TOK)
step_fn, _m, _s = make_checkpoint_step_fn(CKPT, "cuda")
sid = tok.special_ids
sid_vals = set(sid.values())
head = [sid["<|world|>"], *tok.encode(render_world_preamble({"domain": "skill_exception_rule"}))]
print("\n### trajectories")
for sh in ("lookup", "lookup_general", "classify"):
    for it in by[sh][:2]:
        prompt = head + [sid["<|q|>"], *tok.encode(it["question"])]
        chunks = [{"text": p, "reliability": 1.0} for p in it["pages"]]
        r = generate_with_retrieval(step_fn, tok, chunks, prompt, max_rounds=6,
                                    max_new_tokens=256, seed=0)
        print("---", sh, "gold", it["gold"], "rounds", r["n_rounds"], "stop", r["stop_reason"])
        print("   gen:", repr(tok.decode([t for t in r["generated"] if t not in set(sid.values())]))[:300])
        print("   ans:", repr(r["answer_text"])[:200])
        for rd in r["rounds"]:
            print("   q:", repr(rd["query"])[:120], "-> doc", rd["doc_index"])
