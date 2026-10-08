"""Stratified samples of the corpus held-out plan band, plus an oracle check."""
import json, sys, collections
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")

SRC = "/home/ec2-user/corpus/v1/plan_heldout_whole.jsonl"
PER_LEN = 60
rows = [json.loads(l) for l in open(SRC)]
by_len = collections.defaultdict(list)
by_sym = collections.defaultdict(list)
for r in rows:
    by_len[r["n_steps"]].append(r)
    by_sym[r["n_symbols"]].append(r)
print("held-out whole plans:", len(rows))
print("lengths:", {k: len(v) for k, v in sorted(by_len.items())})
print("symbols:", {k: len(v) for k, v in sorted(by_sym.items())})

sample, seen = [], set()
for n in sorted(by_len):
    for r in by_len[n][:PER_LEN]:
        if r["hash"] not in seen:
            seen.add(r["hash"]); sample.append(r)
# make sure every symbol count is represented at >= 60
have = collections.Counter(r["n_symbols"] for r in sample)
for k in sorted(by_sym):
    for r in by_sym[k]:
        if have[k] >= 120:
            break
        if r["hash"] not in seen:
            seen.add(r["hash"]); sample.append(r); have[k] += 1
out = "/home/ec2-user/retrain/plan/heldout_whole_sample.jsonl"
with open(out, "w") as fh:
    for r in sample:
        fh.write(json.dumps(r) + "\n")
print("sample", len(sample), "lengths",
      dict(sorted(collections.Counter(r["n_steps"] for r in sample).items())),
      "symbols", dict(sorted(collections.Counter(r["n_symbols"] for r in sample).items())))

# oracle rows: the gold plan is what a perfect policy emits
for src, dst in ((out, "/home/ec2-user/retrain/plan/oracle_heldout.jsonl"),
                 ("/home/ec2-user/retrain/plan/extrap_whole.jsonl",
                  "/home/ec2-user/retrain/plan/oracle_extrap.jsonl")):
    with open(dst, "w") as fh:
        for line in open(src):
            r = json.loads(line)
            r["decode"] = "oracle"
            r["emitted"] = r["target"]
            r.pop("prompt", None)
            fh.write(json.dumps(r) + "\n")
    print("wrote", dst)
