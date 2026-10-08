import gzip, json, sys
from src.norm import neval
from src.norm.lang import program_json
import os
tag, mode = sys.argv[1], sys.argv[2]
want = [tuple(x.split(":")) for x in sys.argv[3].split(",")]  # shape:kp:cat
lim = int(sys.argv[4]) if len(sys.argv) > 4 else 1
items = neval.load_eval("data/norm/mode", 7000)
cls = json.load(open("results/norm/gap/class_%s_mode_%s.json" % (tag, mode)))
recs = [json.loads(l) for l in
        gzip.open("results/norm/gap/records_%s_mode_%s.jsonl.gz" % (tag, mode), "rt")]
from collections import Counter
def leaves(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k != "kind": leaves(v, out)
    elif isinstance(o, list):
        for v in o: leaves(v, out)
    elif o is not None: out[repr(o)] += 1
    return out
def arity(d):
    if d.get("kind") in ("table","weights") and d.get("entries"):
        k=d["entries"][0][0]; return len(k["$tuple"]) if isinstance(k,dict) else 1
    return 0
def sig(pj): return (tuple((d["kind"],arity(d)) for d in pj["defs"]), tuple(s["op"] for s in pj["steps"]))
seen = Counter()
for i, r in enumerate(recs):
    for sh, kp, cat in want:
        if r["shape"] != sh or r["key_position"] != kp: continue
        gj = program_json(items[i]["prog"]); pj = r.get("emitted")
        if r["exact"] or r["malformed"]: c = "exact/malformed"
        elif r["refused"]: c = "refused"
        elif sig(pj) != sig(gj): c = "wrong kind"
        elif leaves(pj, Counter()) == leaves(gj, Counter()): c = "wrong binding"
        else: c = "wrong content"
        if c != cat: continue
        seen[(sh, kp, cat)] += 1
        if seen[(sh, kp, cat)] > lim: continue
        print("=" * 92)
        print(sh, kp, cat, r["fid"])
        print("gold sig  :", sig(gj))
        print("emit sig  :", sig(pj))
        print("--- gold ---"); print(r["gold_pretty"])
        print("--- emitted ---"); print(r["pretty"])
        print("answer %r gold %r reason %r" % (r["answer"], r["gold_answer"], r["reason"][:100]))
