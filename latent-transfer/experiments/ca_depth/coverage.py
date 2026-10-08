"""Coverage ceiling on held-out 1dCA rules.

For each test example, does every neighbourhood needed to compute x(T+k) appear as
the input to some transition among the ten prior states? An oracle that knows the
rule for seen neighbourhoods and guesses the rest cannot beat this on exact match.
Measured: k=1 0.925, k=2 0.880, k=4 0.834, with 28.8 to 29.0 of 32 neighbourhoods
seen on average. The data supports the paper's 0.95 at k=1; the gap is the model.

Run from the ca_depth directory on a GPU box:  python coverage.py
"""
import sys
import torch

sys.path.insert(0, ".")
from ca_arms import make_batch, W, T, RADIUS  # noqa: E402

dev = "cuda"
gen = torch.Generator(device=dev); gen.manual_seed(0)


def nbhd(x):
    idx = torch.zeros_like(x)
    for o in range(-RADIUS, RADIUS + 1):
        idx = idx * 2 + torch.roll(x, -o, dims=1)
    return idx


for k in (1, 2, 4):
    prior, target, tables = make_batch(4000, k, "test", gen, torch, dev)
    seen = torch.zeros(4000, 32, dtype=torch.bool, device=dev)
    for t in range(T - 1):
        seen.scatter_(1, nbhd(prior[:, t]), True)
    chain = torch.cat([prior[:, -1:], target[:, :-1]], 1)
    needed = torch.zeros(4000, 32, dtype=torch.bool, device=dev)
    for t in range(k):
        needed.scatter_(1, nbhd(chain[:, t]), True)
    unseen = (needed & ~seen).sum(1).float()
    print(f"k={k}: full coverage {((unseen == 0).float().mean()):.3f}; "
          f"mean unseen-needed {unseen.mean():.2f}; mean seen {seen.sum(1).float().mean():.1f}/32")
