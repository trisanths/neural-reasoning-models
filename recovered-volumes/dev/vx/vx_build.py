"""Counter-experiment: a grid fine-tuning set that contains both operand orders.

xdata.main draws every training grid with transpose=False, so all 4,096 rows
state the canonical row-major key order. This builds the same number of rows
from the same 490 training frames, alternating untransposed and transposed, so
the first k rows ftune samples are half of each.
"""
import sys
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")
from src.norm import ndata
from src.norm.cmpwork.xdata import example, save

N = 1024
sp = ndata.split_frames()
fids = sorted(sp["train"])
rows, tries, i = [], 0, 0
while len(rows) < N and tries < N * 25:
    tries += 1
    tr = bool(len(rows) % 2)          # alternate: even canonical, odd transposed
    e = example(fids[i % len(fids)], 90210 + tries * 7919, tr)
    i += 1
    if e is not None:
        e["transposed"] = int(tr)
        rows.append(e)
save("/home/ec2-user/decoupled-reasoner/data/norm/grid_both", rows)
print("rows", len(rows), "transposed", sum(r["transposed"] for r in rows))
