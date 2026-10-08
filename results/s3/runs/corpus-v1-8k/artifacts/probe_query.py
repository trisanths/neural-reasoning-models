"""Which query policy surfaces the answering page, per component."""
import json, sys, re, itertools, random
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.train.tokenizer import load_tokenizer
from src.rl.env import make_service, build_prompt

TOK = load_tokenizer("/home/ec2-user/data/tokenizer_v2.json")
QMAX = 24

def gold_in(chunk, gold):
    return re.search(rf"(?<![A-Za-z]){re.escape(gold)}(?![A-Za-z])", chunk, re.I) is not None

def policies(qtext):
    ids = TOK.encode(qtext)
    return {
        "first24": TOK.decode(ids[:QMAX]),
        "last24": TOK.decode(ids[-QMAX:]),
        "full": qtext,
    }

for name, path, rounds, stride in [
    ("relation", "relation_train.jsonl", 4, 4000),
    ("external", "external_train.jsonl", 3, 400),
    ("mathgen", "mathgen_train.jsonl", 4, 60),
]:
    hit = {k: 0 for k in ("first24", "last24", "full")}
    n = 0
    plens = []
    dlens = []
    with open(f"/home/ec2-user/corpus/v1/{path}") as fh:
        for i, line in enumerate(fh):
            if i % stride:
                continue
            ep = json.loads(line)
            qs = ep["questions"][:2]
            for q in qs:
                n += 1
                p = build_prompt(ep, q, TOK)
                plens.append(len(p))
                for pol, qt in policies(q["text"]).items():
                    svc = make_service(ep["documents"])
                    got = False
                    for _ in range(rounds):
                        r = svc.top(qt)
                        if r is None:
                            break
                        if pol == "first24":
                            dlens.append(len(TOK.encode(r[1])))
                        if gold_in(r[1], q["answer"]):
                            got = True
                            break
                    hit[pol] += int(got)
            if n >= 600:
                break
    plens.sort(); dlens.sort()
    print(name, "n=", n,
          {k: round(v / max(1, n), 3) for k, v in hit.items()},
          "prompt p50/p95:", plens[len(plens)//2], plens[int(len(plens)*.95)],
          "doc p50/p95:", dlens[len(dlens)//2], dlens[int(len(dlens)*.95)])
