"""Diagnostic: does a checkpoint drive the retrieve loop, in and out of
distribution? No web access; dummy documents catch emitted queries."""
import os, sys

from src.evals.interactive import make_checkpoint_step_fn, generate_with_retrieval
from src.train.data import render_world_preamble
from src.train.tokenizer import load_tokenizer
from src.worldgen.engine import generate_episodes

CKPTS = {
    "curve-350me-501": os.path.expanduser("~/runs/webdemo/ckpt-curve-350me-501.pt"),
    "killtest-c-201": os.path.expanduser("~/runs/webdemo/ckpt-killtest-c-201.pt"),
}
tok = load_tokenizer(os.path.expanduser("~/runs/tokenizer_v2/tokenizer_v2.json"))
sid = tok.special_ids

REAL = [
    "What is the capital city of Australia?",
    "In what year did the Titanic sink?",
    "Who painted the Mona Lisa?",
]
DUMMY = ["placeholder record one about nothing in particular",
         "placeholder record two about nothing in particular",
         "placeholder record three about nothing in particular"]

eps = list(generate_episodes(987654, 2))

for name, path in CKPTS.items():
    if not os.path.exists(path):
        print(f"{name}: checkpoint missing, skipped"); continue
    step_fn, model, state = make_checkpoint_step_fn(path, "cuda")
    print(f"=== {name} step {state.get('step')}")
    for ep in eps:
        q = ep["questions"][0]
        prompt = [sid["<|world|>"], *tok.encode(render_world_preamble(ep["world"])),
                  sid["<|q|>"], *tok.encode(q["text"])]
        out = generate_with_retrieval(step_fn, tok, ep["documents"], prompt,
                                      max_rounds=3, max_new_tokens=128)
        print(f"  worldgen | rounds={out['n_rounds']} stop={out['stop_reason']} "
              f"q={q['text'][:48]!r} queries={[r['query'][:40] for r in out['rounds']]} "
              f"ans={out['answer_text'][:32]!r} gold={q['answer'][:32]!r}")
    variants = {
        "world":    lambda q: [sid["<|world|>"], *tok.encode("domain: world"), sid["<|q|>"], *tok.encode(q)],
        "q-only":   lambda q: [sid["<|q|>"], *tok.encode(q)],
        "corp":     lambda q: [sid["<|world|>"], *tok.encode("domain: corporate"), sid["<|q|>"], *tok.encode(q)],
    }
    for vname, build in variants.items():
        for q in REAL:
            out = generate_with_retrieval(step_fn, tok, DUMMY, build(q),
                                          max_rounds=3, max_new_tokens=96)
            print(f"  real/{vname:7s}| rounds={out['n_rounds']} stop={out['stop_reason']} "
                  f"q={q[:36]!r} queries={[r['query'][:48] for r in out['rounds']]} "
                  f"ans={out['answer_text'][:40]!r}")
    del step_fn, model, state
    import torch, gc; gc.collect(); torch.cuda.empty_cache()
