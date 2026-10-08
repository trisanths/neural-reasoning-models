"""Facts about the rebuilt instrument, for the amendment. Run on the box."""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")

from src.extern.stats import wilson  # noqa: E402
from src.pilot import report as rp  # noqa: E402

D = "/mnt/nvme/pilot/items"
items = [json.loads(line) for line in open(f"{D}/items_v2.jsonl")]
table = json.load(open(f"{D}/floor_table_v2.json"))
print("buckets")
for k, v in table["buckets"].items():
    print(" ", k, v)
cells = defaultdict(list)
for it in items:
    cells[rp.cell_name(it["family"], it["level"])].append(it)
m = 384
print("cell n open_floor closed_floor best_const_in_cell k_flag k_flag_floor_only wilson0 sib_ratio_min..max sib_none")
for name, its in sorted(cells.items()):
    n = len(its)
    fo = sum(i["floor"] for i in its) / n
    fc = [i["floors"]["closed_book"] for i in its]
    maj = Counter(i["answer"] for i in its).most_common(1)[0][1] / n
    k_flag = next(k for k in range(n + 2)
                  if rp.poisson_binomial_upper(k, [f + 0.03 for f in fc]) <= 0.05 / m)
    k_flag0 = next((k for k in range(n + 2)
                    if rp.poisson_binomial_upper(k, fc) <= 0.05 / m), None)
    ratios = []
    for i in its:
        o = sum(len(p["text"]) for p in i["pages"]["oracle"])
        s = sum(len(p["text"]) for p in i["pages"]["sibling"])
        ratios.append(s / o if o else 0)
    none = sum(i["sibling_answer"] is None for i in its)
    slots = sum([p["chapter_id"] for p in i["pages"]["sibling"]] !=
                [p["chapter_id"] for p in i["pages"]["oracle"]] for i in its)
    print(f"  {name:22s} {n:4d} {fo:.4f} {sum(fc) / n:.4f} {maj:.3f} "
          f"{k_flag:3d} {k_flag0} {wilson(0, n)[1]:.4f} "
          f"{min(ratios):.2f}..{max(ratios):.2f} {none} slots_differ={slots}")
print("algebra kinds", Counter((i["level"], i.get("algebra_kind")) for i in items
                               if i["family"] == "algebra"))
man = json.load(open(f"{D}/items_v2.manifest.json"))
print("universes", man["universes_used"])
print("seed ranges", man["seed_ranges_scanned"])
for fam, d in man["discards"].items():
    tot = Counter()
    for lv, e in d.items():
        for k, v in e.items():
            if k not in ("distinct_emitted", "kept"):
                tot[k] += v
    print("discards", fam, dict(tot))
pq = [json.loads(line) for line in open(f"{D}/popqa_fc_v2.jsonl")]
print("popqa", len(pq), Counter(i["quartile"] for i in pq),
      Counter(i["gold_index"] for i in pq), Counter(i["gold_frequency_rank"] for i in pq))
print("popqa props", Counter(i["prop"] for i in pq).most_common())
gl = sum(len(i["gold"]) for i in pq) / len(pq)
dl = sum(len(o) for i in pq for k, o in enumerate(i["options"]) if k != i["gold_index"]) / (3 * len(pq))
longest = sum(max(range(4), key=lambda k: len(i["options"][k])) == i["gold_index"] for i in pq) / len(pq)
print(f"popqa gold len {gl:.1f} distractor len {dl:.1f} gold longest {longest:.3f}")
