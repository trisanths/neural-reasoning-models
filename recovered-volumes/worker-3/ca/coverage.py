
# Coverage ceiling: for held-out rules, how often does every neighbourhood needed to
# compute x(T+k) appear somewhere in the ten prior states? An oracle that knows the
# rule for seen neighbourhoods and guesses the rest cannot beat this on exact match.
import torch, sys
sys.path.insert(0, "/home/ec2-user/ca")
from ca_arms import make_batch, W, T, RADIUS
dev = "cuda"
gen = torch.Generator(device=dev); gen.manual_seed(0)
def nbhd(x):
    idx = torch.zeros_like(x)
    for o in range(-RADIUS, RADIUS + 1):
        idx = idx * 2 + torch.roll(x, -o, dims=1)
    return idx
for k in (1, 2, 4):
    prior, target, tables = make_batch(4000, k, "test", gen, torch, dev)
    # neighbourhoods observed as INPUTS to a transition in the history: states 0..T-2
    seen = torch.zeros(4000, 32, dtype=torch.bool, device=dev)
    for t in range(T - 1):
        seen.scatter_(1, nbhd(prior[:, t]), True)
    # neighbourhoods NEEDED: inputs to each of the k transitions from state T-1 onward
    chain = torch.cat([prior[:, -1:], target[:, :-1]], 1)          # states T-1 .. T+k-2
    needed = torch.zeros(4000, 32, dtype=torch.bool, device=dev)
    for t in range(k):
        needed.scatter_(1, nbhd(chain[:, t]), True)
    full = (needed & ~seen).sum(1) == 0
    n_unseen = (needed & ~seen).sum(1).float()
    # oracle exact-match ceiling: each unseen needed neighbourhood is a coin flip per cell it touches
    print(f"k={k}: fraction of test examples with full coverage = {full.float().mean():.3f}; "
          f"mean unseen-needed nbhds = {n_unseen.mean():.2f}; mean distinct seen = {seen.sum(1).float().mean():.1f}/32")
