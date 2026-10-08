import json, collections
srcs = (("n=500 s3", "/tmp/n500.json"),
        ("n=200 checkout", "results/extern/bench/ours_corpus-v1-8k_mmlu.json"),
        ("n=200 eot", "results/extern/bench/ours_mmlu_eotprefix_n200.json"))
for lab, p in srcs:
    d = json.load(open(p)); r = d["records"]; n = len(r)
    c = collections.Counter(x["pred"] for x in r)
    g = collections.Counter(x["gold"] for x in r)
    acc = sum(1 for x in r if x["pred"] == x["gold"]) / n
    dist = "/".join(str(c.get(i, 0)) for i in range(4))
    fileacc = d["acc"]
    print("%-16s n=%d acc=%.4f file=%s preds=%s modal=%.4f goldA=%.4f eot=%s"
          % (lab, n, acc, fileacc, dist, max(c.values()) / n, g.get(0, 0) / n,
             d.get("eot_prefix")))
