"""Is the style-2/3/4 induction failure truncation, or a reading failure?

Re-induces style 2 and style 3 binop pages at the shipped max_new (288) and at
a much larger cap, and reports parse rate and generation length.
"""
import json
from collections import Counter
import torch
from src.audit.surfaces import restyle_world
from src.opgraph.data import eval_worlds, induce_prompt
from src.opgraph.opdef import OpError, parse_operators
from src.opgraph.run import Generator, load_model
from src.train.tokenizer import load_tokenizer

tok = load_tokenizer("/home/ec2-user/data/tokenizer_v2.json")
base = eval_worlds("sequential", 40, breadth=3, style=0)
model, _ = load_model("runs/opgraph.pt", "cuda")
gen = Generator(model, tok, "cuda", batch_size=32)

for style in (2, 3, 0):
    worlds = [restyle_world(w, style) for w in base]
    pages = [p for w in worlds for p in w.pages if p.key.startswith("binop:")]
    prompts = [induce_prompt(p.text) for p in pages]
    for cap in (288, 640):
        outs = gen.generate(prompts, max_new=cap)
        c = Counter()
        lens = []
        for o in outs:
            lens.append(len(tok.encode(o)))
            try:
                got = parse_operators(o)
                c["parsed"] += 1
            except OpError:
                c["failed"] += 1
        lens.sort()
        print(f"style {style} cap {cap}: {dict(c)} n={len(outs)} "
              f"len med={lens[len(lens)//2]} max={lens[-1]} "
              f"at_cap={sum(1 for l in lens if l >= cap - 2)}", flush=True)
    print("--- sample failures, style", style, flush=True)
    outs = gen.generate(prompts, max_new=640)
    shown = 0
    for p, o in zip(pages, outs):
        try:
            parse_operators(o)
            continue
        except OpError:
            pass
        print("PAGE:", p.text.replace("\n", " | ")[:200], flush=True)
        print("GOT :", o[:400], flush=True)
        shown += 1
        if shown >= 3:
            break
