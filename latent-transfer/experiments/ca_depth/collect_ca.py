"""Render the 1dCA sweep: one row per (arm, positions, recipe), columns per k,
cells as mean [min-max] over seeds. Reads any results dir; v2 and v3 file names both work.

Usage: python collect_ca.py <results_dir> [<results_dir> ...]
"""
import glob, json, sys
from collections import defaultdict

LABEL = {
    "oo_tok": "O-O tokens (every state emitted)",
    "os_tok": "O-S tokens (only x(T+k) emitted)",
    "oo_pause_a": "slots in KV, context readout",
    "oo_lat_a": "hidden fed back, context readout",
    "oo_pause_s": "slots pinned to state, context readout",
    "oo_split": "2 lossless codes -> KV",
    "oo_pause": "slots -> KV, vector readout",
    "oo_lat": "hidden fed back, vector readout",
    "oo_rec": "fixed-vector loop, vector readout",
    "oo_bansal": "loop + recall + trunc BPTT",
    "oo_mat": "d x d matrix loop, vector readout",
    "os": "no intermediates, vector readout",
}
ORDER = list(LABEL)
cells = defaultdict(lambda: defaultdict(list))   # (arm,pos,recipe,mixed) -> k -> [exact]
for d in sys.argv[1:] or ["results"]:
    for f in glob.glob(f"{d}/*.json"):
        r = json.load(open(f))
        key = (r["arm"], r.get("pos", "abs"), f"{r.get('batch', 256)}x{r['steps'] // 1000}k",
               "mixed" if len(r["k_train"]) > 1 else "per-k", r.get("spec", "orbit"))
        for e in r["eval"]:
            cells[key][e["k"]].append(e["exact"])

def fmt(v):
    if not v: return "     --    "
    if len(v) == 1: return f"   {v[0]:.3f}   "
    return f"{sum(v)/len(v):.3f}[{min(v):.2f}-{max(v):.2f}]"

for mixed in ("per-k", "mixed"):
    ks = [1, 2, 4] if mixed == "per-k" else [1, 2, 4, 8, 16, 32]
    rows = [k for k in cells if k[3] == mixed]
    if not rows: continue
    print(f"\n== {'ONE MODEL PER k' if mixed == 'per-k' else 'TRAINED ON k<=4, EVALUATED TO k=32'} ==")
    print(f"{'arm':12s} {'pos':5s} {'recipe':9s} {'rule':6s} {'what is carried / how read out':34s} " + " ".join(f"{'k='+str(k):>13s}" for k in ks))
    for key in sorted(rows, key=lambda k: (ORDER.index(k[0]) if k[0] in ORDER else 99, k[1] != "rope", k[2], k[4] != "orbit")):
        arm, pos, recipe, _, spec = key
        print(f"{arm:12s} {pos:5s} {recipe:9s} {'given' if spec == 'table' else 'inferred':6s} {LABEL.get(arm, ''):34s} " + " ".join(f"{fmt(cells[key].get(k, [])):>13s}" for k in ks))
print("\nexact-match on 2000 held-out-rule examples; [min-max] over seeds. rule = whether the 32-bit table is given in the prefix or must be inferred from the orbit. Paper (4L d128 GPT-NeoX): O-S 0.95/0.40/<0.25, O-O >0.9 at k<=4.")
