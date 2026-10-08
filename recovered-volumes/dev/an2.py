import gzip, json, collections, sys
tag, mode, kp, cat = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
SH = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
      "precedence", "priority")
p = "results/norm/gap/records_%s_mode_%s.jsonl.gz" % (tag, mode)
n = 0
for line in gzip.open(p, "rt"):
    r = json.loads(line)
    if r["shape"] not in SH or r["key_position"] != kp or r["category"] != cat:
        continue
    n += 1
    if n > int(sys.argv[5] if len(sys.argv) > 5 else 3):
        break
    print("=" * 90)
    print(r["fid"], r["shape"], r["category"], "evidence:",
          json.dumps(r.get("evidence"))[:200])
    print("--- gold ---");     print(r["gold_pretty"])
    print("--- emitted ---");  print(r["pretty"])
    print("answer %r gold_answer %r" % (r["answer"], r["gold_answer"]))
