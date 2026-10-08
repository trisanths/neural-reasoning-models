"""1dCA serial-depth experiment: does the k-curve depend on where state lives?

Replicates the Beyond Memorization setup (arXiv 2508.16745): radius-2 1D cellular
automata, width 20, ten prior states shown, predict the state k steps ahead, with
train and test rule sets disjoint. Six arms differ only in where the intermediate
state is written and how it is supervised.

  os        outcome only via single-vector decoder (bottlenecked; kept as reference)
  os_tok    the paper's O-S: only x(T+k) emitted as tokens, no intermediates (known: 0.95/0.40/<0.25)
  oo_tok    every intermediate state emitted as bit tokens              (known: >0.9 at k<=4)
  oo_vq     every intermediate state written as a learned VQ code       (new)
  oo_split  every intermediate state written as two lossless 10-bit codes (new; discrete, no vocab)
  oo_lat    Coconut: hidden state fed back and appended to KV, linear decode per step (new)
  oo_rec    weight-tied loop on one fixed-width vector, linear decode per step (new)
  oo_bansal oo_rec + recall + truncated detached training (Bansal 2202.05826)   (new)
  oo_pause  learned slot per step appended to KV, no feedback, per-step decode  (new)
  oo_pause_a  oo_pause with the readout done by the main model attending over context; bits never carried
  oo_lat_a    oo_lat with the same context-attending readout
  oo_pause_s  oo_pause_a plus a probe loss pinning each slot to its step's state
  oo_mat    encoder emits a d x d fast-weight matrix once, loop applies it     (new)

Run:  python ca_arms.py --arm os --ks 1 --steps 20000 --tag perk_k1 --out results
"""
from __future__ import annotations

import json
import math
import os
import time



W = 20          # cells
T = 10          # prior states shown
RADIUS = 2      # neighbourhood 5 -> 32-entry rule table
BIT0, BIT1, SEP, BOS, PAD = 0, 1, 2, 3, 4
VOCAB = 5


# ----------------------------------------------------------------------------- data
def make_batch(n, k, split, gen, torch, dev):
    """Return input states (n,T,W), target states (n,k,W) on `dev`. Rules disjoint by split.
    Everything runs on the GPU so the CPU never becomes the bottleneck."""
    lo, hi = (0, 2**31) if split == "train" else (2**31, 2**32)
    rule_ids = torch.randint(lo, hi, (n,), generator=gen, device=dev, dtype=torch.int64)
    shifts = torch.arange(32, device=dev)
    tables = ((rule_ids[:, None] >> shifts) & 1)                       # (n, 32)
    x = torch.randint(0, 2, (n, W), generator=gen, device=dev, dtype=torch.int64)
    seq = [x]
    for _ in range(T + k - 1):
        idx = torch.zeros_like(x)
        for o in range(-RADIUS, RADIUS + 1):
            idx = idx * 2 + torch.roll(x, -o, dims=1)
        x = torch.gather(tables, 1, idx)
        seq.append(x)
    seq = torch.stack(seq, dim=1)                                      # (n, T+k, W)
    return seq[:, :T], seq[:, T:], tables


def encode_prior(prior, torch, tables=None):
    # prior: (n,T,W) on device -> tokens: BOS, [rule table bits + SEP if given], each state's bits + SEP
    n = prior.shape[0]; dev = prior.device
    sep = torch.full((n, T, 1), SEP, dtype=torch.long, device=dev)
    body = torch.cat([prior, sep], dim=2).reshape(n, T * (W + 1))
    bos = torch.full((n, 1), BOS, dtype=torch.long, device=dev)
    parts = [bos]
    if tables is not None:
        parts += [tables, torch.full((n, 1), SEP, dtype=torch.long, device=dev)]
    parts.append(body)
    return torch.cat(parts, dim=1)


# ----------------------------------------------------------------------------- model
def build_models(torch, nn, F, d=128, n_layers=4, n_heads=4, max_len=1024, vq_codes=4096, vq_dim=64, pos="abs", block="seq"):
    hd = d // n_heads
    _rope_cache = {}
    def rope(q, k, start):
        # q,k: (B,H,L,hd). Rotate pairs by position-dependent angles; the paper's GPT-NeoX
        # backbone uses this, and it makes "attend to a fixed offset back" one learnable pattern.
        L = q.shape[2]
        key = (start, L, q.device)
        if key not in _rope_cache:
            inv = 1.0 / (10000 ** (torch.arange(0, hd, 2, device=q.device).float() / hd))
            t = torch.arange(start, start + L, device=q.device).float()
            fr = torch.outer(t, inv)                                   # (L, hd/2)
            _rope_cache[key] = (fr.cos()[None, None], fr.sin()[None, None])
        cos, sin = _rope_cache[key]
        def rot(x):
            x1, x2 = x[..., 0::2], x[..., 1::2]
            return torch.stack([x1 * cos - x2 * sin, x1 * sin + x2 * cos], -1).flatten(-2)
        return rot(q), rot(k)
    class Attn(nn.Module):
        def __init__(self):
            super().__init__()
            self.qkv = nn.Linear(d, 3 * d)
            self.proj = nn.Linear(d, d)
        def forward(self, x, past=None):
            B, L, _ = x.shape
            q, k, v = self.qkv(x).split(d, dim=-1)
            q = q.view(B, L, n_heads, d // n_heads).transpose(1, 2)
            k = k.view(B, L, n_heads, d // n_heads).transpose(1, 2)
            v = v.view(B, L, n_heads, d // n_heads).transpose(1, 2)
            if pos == "rope":
                start = 0 if past is None else past[0].shape[2]
                q, k = rope(q, k, start)
            if past is not None:
                k = torch.cat([past[0], k], dim=2)
                v = torch.cat([past[1], v], dim=2)
            y = F.scaled_dot_product_attention(q, k, v, is_causal=(past is None))
            y = y.transpose(1, 2).reshape(B, L, d)
            return self.proj(y), (k, v)

    class Block(nn.Module):
        def __init__(self):
            super().__init__()
            self.ln1 = nn.LayerNorm(d); self.attn = Attn()
            self.ln2 = nn.LayerNorm(d)
            self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        def forward(self, x, past=None):
            if block == "parallel":
                # GPT-NeoX: attention and MLP both read one normed input and are summed
                h = self.ln1(x)
                a, kv = self.attn(h, past)
                return x + a + self.mlp(h), kv
            a, kv = self.attn(self.ln1(x), past)
            x = x + a
            x = x + self.mlp(self.ln2(x))
            return x, kv

    class GPT(nn.Module):
        """Tiny causal transformer. Accepts token ids or raw input embeddings."""
        def __init__(self):
            super().__init__()
            self.wte = nn.Embedding(VOCAB, d)
            self.wpe = nn.Embedding(max_len, d)
            self.blocks = nn.ModuleList([Block() for _ in range(n_layers)])
            self.ln_f = nn.LayerNorm(d)
            nn.init.normal_(self.wte.weight, std=0.02)
            nn.init.normal_(self.wpe.weight, std=0.02)
            for m in self.modules():
                if isinstance(m, nn.Linear):
                    nn.init.normal_(m.weight, std=0.02)
                    if m.bias is not None: nn.init.zeros_(m.bias)
        def forward(self, ids=None, embeds=None, past=None):
            x = self.wte(ids) if embeds is None else embeds
            B, L, _ = x.shape
            start = 0 if past is None else past[0][0].shape[2]
            if pos == "abs":
                x = x + self.wpe(torch.arange(start, start + L, device=x.device))[None]
            new = []
            for i, blk in enumerate(self.blocks):
                x, kv = blk(x, None if past is None else past[i])
                new.append(kv)
            return self.ln_f(x), new

    class VQ(nn.Module):
        """State (W bits) -> one code from a learned codebook -> W bits."""
        def __init__(self):
            super().__init__()
            self.enc = nn.Sequential(nn.Linear(W, 256), nn.ReLU(), nn.Linear(256, vq_dim))
            self.book = nn.Embedding(vq_codes, vq_dim)
            nn.init.uniform_(self.book.weight, -1 / vq_codes, 1 / vq_codes)
            self.dec = nn.Sequential(nn.Linear(vq_dim, 256), nn.ReLU(), nn.Linear(256, W))
        def encode(self, bits):
            z = self.enc(bits.float())
            dist = (z.pow(2).sum(-1, keepdim=True) - 2 * z @ self.book.weight.t()
                    + self.book.weight.pow(2).sum(-1)[None])
            idx = dist.argmin(-1)
            return z, idx
        def forward(self, bits):
            z, idx = self.encode(bits)
            e = self.book(idx)
            zq = z + (e - z).detach()
            logits = self.dec(zq)
            recon = F.binary_cross_entropy_with_logits(logits, bits.float())
            commit = F.mse_loss(z, e.detach()) + 0.25 * F.mse_loss(e, z.detach())
            return recon + commit, logits, idx

    class BitDecoder(nn.Module):
        """Autoregressive readout: one latent vector -> W bits, emitted as tokens.

        Replaces a single linear map so every arm reads its answer out the same
        way tokens do: each output bit conditions on the latent and on the bits
        before it. The carry between steps is untouched; only the readout changes.
        """
        def __init__(self, n_dec_layers=2):
            super().__init__()
            self.inp = nn.Linear(d, d)
            self.bit_emb = nn.Embedding(2, d)
            self.pos = nn.Embedding(W + 1, d)
            self.blocks = nn.ModuleList([Block() for _ in range(n_dec_layers)])
            self.ln = nn.LayerNorm(d)
            self.out = nn.Linear(d, 2)
            for m in self.modules():
                if isinstance(m, nn.Linear):
                    nn.init.normal_(m.weight, std=0.02)
                    if m.bias is not None: nn.init.zeros_(m.bias)
        def _run(self, x):
            x = x + self.pos(torch.arange(x.shape[1], device=x.device))[None]
            for b in self.blocks: x, _ = b(x)
            return self.out(self.ln(x))
        def loss(self, z, bits):
            x = torch.cat([self.inp(z)[:, None], self.bit_emb(bits[:, :-1])], 1)
            logits = self._run(x)
            return F.cross_entropy(logits.reshape(-1, 2), bits.reshape(-1))
        @torch.no_grad()
        def decode(self, z):
            x = self.inp(z)[:, None]
            out = []
            for i in range(W):
                b = self._run(x)[:, -1].argmax(-1)
                out.append(b)
                if i < W - 1:
                    x = torch.cat([x, self.bit_emb(b)[:, None]], 1)
            return torch.stack(out, 1)

    class RecCell(nn.Module):
        """Weight-tied state update s -> s, no memory growth."""
        def __init__(self):
            super().__init__()
            self.ln = nn.LayerNorm(d)
            self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
            self.ln2 = nn.LayerNorm(d)
            self.mlp2 = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        def forward(self, s):
            s = s + self.mlp(self.ln(s))
            s = s + self.mlp2(self.ln2(s))
            return s

    return GPT, VQ, RecCell, BitDecoder


# ----------------------------------------------------------------------------- arms
def run_arm(arm: str, k_train, k_eval, steps: int, seed: int, tag: str, out_dir: str, spec: str = "orbit", batch: int = 256, pos: str = "abs", block: str = "seq", eval_only: str = ""):
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    torch.manual_seed(seed); np.random.seed(seed)
    dev = "cuda"
    gen = torch.Generator(device=dev); gen.manual_seed(seed)
    GPT, VQ, RecCell, BitDecoder = build_models(torch, nn, F, pos=pos, block=block)
    d = 128
    BATCH, LR, WARM = batch, 3e-4, 1000
    ks_train = list(k_train)
    k_max = max(max(ks_train), max(k_eval))
    log = {"arm": arm, "k_train": ks_train, "k_eval": list(k_eval), "steps": steps, "seed": seed, "spec": spec, "batch": batch, "pos": pos, "block": block, "readout": "autoregressive", "train": []}

    gpt = GPT().to(dev)
    head_bits = BitDecoder().to(dev)               # autoregressive readout: latent -> W bits
    extra = nn.ModuleList([head_bits])
    vq = None
    if arm == "oo_vq":
        vq = VQ().to(dev)
        # pretrain the codebook on train-rule states, then freeze
        opt_vq = torch.optim.Adam(vq.parameters(), lr=1e-3)
        for it in range(4000):
            pr, tg, _ = make_batch(512, 1, "train", gen, torch, dev)
            bits = torch.cat([pr.reshape(-1, W), tg.reshape(-1, W)])
            loss, logits, _ = vq(bits)
            opt_vq.zero_grad(); loss.backward(); opt_vq.step()
        with torch.no_grad():
            pr, tg, _ = make_batch(2000, 1, "test", gen, torch, dev)
            bits = tg.reshape(-1, W)
            _, logits, idx = vq(bits)
            rec_bit = ((logits > 0).long() == bits).float().mean().item()
            rec_exact = ((logits > 0).long() == bits).all(-1).float().mean().item()
            used = idx.unique().numel()
        log["vq"] = {"bit_acc": rec_bit, "exact_acc": rec_exact, "codes_used": used}
        for p in vq.parameters(): p.requires_grad_(False)
        code_in = nn.Linear(64, d).to(dev)          # codebook vector -> model input
        code_head = nn.Linear(d, 4096).to(dev)      # predict next code
        extra = nn.ModuleList([head_bits, code_in, code_head])
    if arm == "oo_split":
        split_in = nn.Embedding(2 * 1024, d).to(dev)   # two codebooks of 1024 (hi/lo 10 bits)
        split_head = nn.Linear(d, 1024).to(dev)
        extra = nn.ModuleList([head_bits, split_in, split_head])
    if arm in ("oo_lat", "oo_lat_a"):
        lat_in = nn.Linear(d, d).to(dev)               # hidden -> next input embedding
        extra = nn.ModuleList([head_bits, lat_in])
    if arm == "oo_rec":
        cell = RecCell().to(dev)
        extra = nn.ModuleList([head_bits, cell])
    if arm == "oo_bansal":
        # Bansal et al. 2202.05826 recipe on the fixed-vector loop: RECALL (the cell sees the
        # encoder summary at every iteration, so the problem cannot be forgotten) and
        # PROGRESSIVE / truncated detached training (a random number of leading iterations run
        # without gradient, so the cell learns behaviour that repeats rather than counts).
        recall_cell = nn.Sequential(nn.Linear(2 * d, 4 * d), nn.GELU(), nn.Linear(4 * d, d)).to(dev)
        recall_ln = nn.LayerNorm(d).to(dev)
        extra = nn.ModuleList([head_bits, recall_cell, recall_ln])
    if arm == "oo_pause_s":
        # oo_pause_a plus a probe loss pinning each slot's hidden state to its step's CA
        # state, so the latent carried in the KV is forced to be state-shaped rather than
        # free to entangle the training rules. head_bits doubles as the probe.
        slot = nn.Parameter(torch.randn(1, 1, d, device=dev) * 0.02)
        extra = nn.ModuleList([head_bits]); extra.register_parameter("slot", slot)
    if arm in ("oo_pause", "oo_pause_a"):
        # Memory without feedback: k learned slot embeddings appended to context, one per
        # step, each supervised to decode its step's state. Nothing is fed back; the only
        # thing carrying state between steps is the KV cache. Single forward pass.
        slot = nn.Parameter(torch.randn(1, 1, d, device=dev) * 0.02)
        extra = nn.ModuleList([head_bits]); extra.register_parameter("slot", slot)
    if arm == "oo_mat":
        # Matrix state, the OverEncoder-S analog: the encoder emits a d x d fast-weight
        # matrix once (the loaded rule), then the loop applies it to a d-vector state.
        # No memory growth, like oo_rec, but the rule lives in d*d values instead of d.
        mat_gen = nn.Linear(d, d * d).to(dev)
        s_init = nn.Linear(d, d).to(dev)
        mat_ln = nn.LayerNorm(d).to(dev)
        extra = nn.ModuleList([head_bits, mat_gen, s_init, mat_ln])

    params = list(gpt.parameters()) + list(extra.parameters())
    opt = torch.optim.Adam(params, lr=LR)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / WARM) * max(0.0, 1 - s / steps))

    def bits_to_split(bits):        # (n,W) -> (n,2) code ids in [0,1024)
        hi = (bits[:, :10] * (2 ** torch.arange(9, -1, -1, device=bits.device))).sum(-1)
        lo = (bits[:, 10:] * (2 ** torch.arange(9, -1, -1, device=bits.device))).sum(-1)
        return torch.stack([hi, lo], -1)

    def split_to_bits(codes):        # (n,2) -> (n,W)
        hi = ((codes[:, :1] >> torch.arange(9, -1, -1, device=codes.device)) & 1)
        lo = ((codes[:, 1:] >> torch.arange(9, -1, -1, device=codes.device)) & 1)
        return torch.cat([hi, lo], -1)

    # ---------------------------------------------------- context-attending readout
    # The main model emits the W bits of one state autoregressively from a latent
    # position's output, attending over everything in `past` (prefix + latent positions
    # so far). The bits' own KV is never returned, so they are readout only: the carry
    # between steps is whatever the arm put in `past`, never the emitted bits.
    def _tied(h):
        return (gpt.wte.weight @ h.transpose(-1, -2)).transpose(-1, -2)    # (..., VOCAB)

    def readout_loss(h_t, past_t, bits):
        # h_t: (B,d) output at the latent position; past_t: KV up to and including it;
        # bits: (B,W) targets. First bit from h_t, the rest teacher-forced through gpt.
        logits0 = _tied(h_t)[:, None]                                       # (B,1,V)
        h_rest, _ = gpt(embeds=gpt.wte(bits[:, :-1]), past=past_t)          # (B,W-1,d)
        logits = torch.cat([logits0, _tied(h_rest)], 1)                     # (B,W,V)
        return F.cross_entropy(logits.reshape(-1, VOCAB), bits.reshape(-1))

    @torch.no_grad()
    def readout_decode(h_t, past_t):
        b = _tied(h_t)[:, :2].argmax(-1)
        out = [b]; past = past_t
        for _ in range(W - 1):
            h, past = gpt(embeds=gpt.wte(b)[:, None], past=past)
            b = _tied(h[:, -1])[:, :2].argmax(-1); out.append(b)
        return torch.stack(out, 1)

    # ------------------------------------------------------------------ train step
    def train_step(k):
        prior, target, tabs = make_batch(BATCH, k, "train", gen, torch, dev)   # (B,T,W), (B,k,W), (B,32)
        ids = encode_prior(prior, torch, tabs if spec == "table" else None)
        B = ids.shape[0]

        if arm == "os":
            # predict x(T+k) bits from final prefix position; single target, no intermediates
            h, _ = gpt(ids)
            return head_bits.loss(h[:, -1], target[:, -1])

        if arm == "os_tok":
            # the paper's O-S: only x(T+k) is emitted, as bits + SEP, no intermediates
            body = torch.cat([target[:, -1:], torch.full((B, 1, 1), SEP, device=dev)], 2).reshape(B, W + 1)
            full = torch.cat([ids, body], 1)
            h, _ = gpt(full[:, :-1])
            logits = (gpt.wte.weight @ h.transpose(1, 2)).transpose(1, 2)
            lab = full[:, 1:].clone(); lab[:, : ids.shape[1] - 1] = -100
            return F.cross_entropy(logits.reshape(-1, VOCAB), lab.reshape(-1), ignore_index=-100)

        if arm == "oo_tok":
            # emit every intermediate state as bits + SEP; standard next-token CE on those
            body = torch.cat([target, torch.full((B, k, 1), SEP, device=dev)], 2).reshape(B, k * (W + 1))
            full = torch.cat([ids, body], 1)
            h, _ = gpt(full[:, :-1])
            logits = gpt.wte.weight @ h.transpose(1, 2)        # tied head: (V,d)@(B,d,L) -> (B,V,L)
            logits = logits.transpose(1, 2)
            lab = full[:, 1:].clone(); lab[:, : ids.shape[1] - 1] = -100
            return F.cross_entropy(logits.reshape(-1, VOCAB), lab.reshape(-1), ignore_index=-100)

        if arm == "oo_split":
            codes = bits_to_split(target.reshape(-1, W)).reshape(B, k, 2)   # (B,k,2)
            codes_flat = codes.reshape(B, 2 * k)
            code_ids = codes_flat + torch.tensor([0, 1024], device=dev).repeat(k)  # offset lo codebook
            emb_prefix = gpt.wte(ids)
            emb_codes = split_in(code_ids)
            x = torch.cat([emb_prefix, emb_codes[:, :-1]], 1)
            h, _ = gpt(embeds=x)
            hc = h[:, ids.shape[1] - 1:]                          # positions that predict codes
            logits = split_head(hc)                                # (B, 2k, 1024)
            return F.cross_entropy(logits.reshape(-1, 1024), codes_flat.reshape(-1))

        if arm == "oo_vq":
            with torch.no_grad():
                _, idx = vq.encode(target.reshape(-1, W))          # (B*k,)
            idx = idx.reshape(B, k)
            emb_prefix = gpt.wte(ids)
            emb_codes = code_in(vq.book(idx))
            x = torch.cat([emb_prefix, emb_codes[:, :-1]], 1)
            h, _ = gpt(embeds=x)
            hc = h[:, ids.shape[1] - 1:]
            logits = code_head(hc)                                 # (B,k,4096)
            return F.cross_entropy(logits.reshape(-1, 4096), idx.reshape(-1))

        if arm == "oo_lat":
            # sequential latent steps with KV cache; per-step linear decode supervision
            h, past = gpt(ids)
            loss = 0.0
            cur = h[:, -1]
            for t in range(k):
                loss = loss + head_bits.loss(cur, target[:, t])
                if t < k - 1:
                    nxt = lat_in(cur)[:, None]
                    h2, past = gpt(embeds=nxt, past=past)
                    cur = h2[:, -1]
            return loss / k

        if arm == "oo_rec":
            h, _ = gpt(ids)
            s = h[:, -1]
            loss = 0.0
            for t in range(k):
                s = cell(s)
                loss = loss + head_bits.loss(s, target[:, t])
            return loss / k

        if arm == "oo_bansal":
            h, _ = gpt(ids)
            r = h[:, -1]                                            # recall vector
            s = r
            n_detach = int(torch.randint(0, k, (1,), generator=gen, device=dev).item()) if k > 1 else 0
            loss = 0.0; n_graded = 0
            for t in range(k):
                if t < n_detach:
                    with torch.no_grad():
                        s = recall_ln(s + recall_cell(torch.cat([s, r], -1)))
                    continue
                s = recall_ln(s + recall_cell(torch.cat([s, r], -1)))
                loss = loss + head_bits.loss(s, target[:, t])
                n_graded += 1
            return loss / max(n_graded, 1)

        if arm == "oo_pause_s":
            x = torch.cat([gpt.wte(ids), slot.expand(B, k, d)], 1)
            h, past = gpt(embeds=x)
            P = ids.shape[1]; loss = 0.0
            for t in range(k):
                past_t = [(kk[:, :, :P + t + 1], vv[:, :, :P + t + 1]) for kk, vv in past]
                loss = loss + readout_loss(h[:, P + t], past_t, target[:, t])
            probe = head_bits.loss(h[:, P:P + k].reshape(-1, d), target.reshape(-1, W))
            return loss / k + probe

        if arm == "oo_pause_a":
            # one forward over prefix + k slots gives every slot's output and the full KV;
            # readout for slot t uses the KV sliced to positions <= slot t
            x = torch.cat([gpt.wte(ids), slot.expand(B, k, d)], 1)
            h, past = gpt(embeds=x)
            P = ids.shape[1]; loss = 0.0
            for t in range(k):
                past_t = [(kk[:, :, :P + t + 1], vv[:, :, :P + t + 1]) for kk, vv in past]
                loss = loss + readout_loss(h[:, P + t], past_t, target[:, t])
            return loss / k

        if arm == "oo_lat_a":
            h, past = gpt(ids)
            cur = h[:, -1]; loss = 0.0
            for t in range(k):
                nxt = lat_in(cur)[:, None]
                h2, past = gpt(embeds=nxt, past=past)       # latent position t; its KV is the carry
                cur = h2[:, -1]
                loss = loss + readout_loss(cur, past, target[:, t])
            return loss / k

        if arm == "oo_pause":
            x = torch.cat([gpt.wte(ids), slot.expand(B, k, d)], 1)
            h, _ = gpt(embeds=x)
            hs = h[:, ids.shape[1]:]                               # (B,k,d) slot outputs
            return head_bits.loss(hs.reshape(-1, d), target.reshape(-1, W))

        if arm == "oo_mat":
            h, _ = gpt(ids)
            hh = h[:, -1]
            Wf = mat_gen(hh).view(B, d, d) / math.sqrt(d)     # fast weights, generated once
            s = s_init(hh)
            loss = 0.0
            for t in range(k):
                s = mat_ln(s + F.gelu(torch.bmm(Wf, s[:, :, None])[:, :, 0]))
                loss = loss + head_bits.loss(s, target[:, t])
            return loss / k
        raise ValueError(arm)

    # ------------------------------------------------------------------ eval
    @torch.no_grad()
    def _eval_chunk(k, n):
        prior, target, tabs = make_batch(n, k, "test", gen, torch, dev)
        ids = encode_prior(prior, torch, tabs if spec == "table" else None)
        B = ids.shape[0]
        final = target[:, -1]

        if arm == "os":
            h, _ = gpt(ids); pred = head_bits.decode(h[:, -1])
        elif arm == "os_tok":
            h, past = gpt(ids)
            nxt = (gpt.wte.weight @ h[:, -1].t()).t()[:, :2].argmax(-1)
            outs = [nxt]
            for _ in range(W - 1):
                h, past = gpt(nxt[:, None], past=past)
                nxt = (gpt.wte.weight @ h[:, -1].t()).t()[:, :2].argmax(-1); outs.append(nxt)
            pred = torch.stack(outs, 1)
        elif arm == "oo_tok":
            # Type-constrained decoding: at bit positions the argmax is over {0,1}; the SEP
            # after each state is forced. A stray token type would otherwise shift every
            # later bit against the wrong state, which is an eval artefact, not a model one.
            h, past = gpt(ids)
            cur = h[:, -1]
            for t in range(k):
                bits = []
                for i in range(W):
                    b = (gpt.wte.weight @ cur.t()).t()[:, :2].argmax(-1); bits.append(b)
                    h, past = gpt(b[:, None], past=past); cur = h[:, -1]
                sep = torch.full((B,), SEP, device=dev, dtype=torch.long)
                if t < k - 1:
                    h, past = gpt(sep[:, None], past=past); cur = h[:, -1]
            pred = torch.stack(bits, 1)
        elif arm == "oo_split":
            emb = gpt.wte(ids)
            h, past = gpt(embeds=emb)
            cur = h[:, -1]
            codes = []
            for j in range(2 * k):
                c = split_head(cur).argmax(-1)
                codes.append(c)
                if j < 2 * k - 1:
                    e = split_in(c + (0 if j % 2 == 0 else 1024))[:, None]
                    h2, past = gpt(embeds=e, past=past); cur = h2[:, -1]
            codes = torch.stack(codes, 1).reshape(B, k, 2)
            pred = split_to_bits(codes[:, -1])
        elif arm == "oo_vq":
            emb = gpt.wte(ids)
            h, past = gpt(embeds=emb)
            cur = h[:, -1]
            for t in range(k):
                c = code_head(cur).argmax(-1)
                if t < k - 1:
                    e = code_in(vq.book(c))[:, None]
                    h2, past = gpt(embeds=e, past=past); cur = h2[:, -1]
            pred = (vq.dec(vq.book(c)) > 0).long()
        elif arm == "oo_lat":
            h, past = gpt(ids); cur = h[:, -1]
            for t in range(k - 1):
                h2, past = gpt(embeds=lat_in(cur)[:, None], past=past); cur = h2[:, -1]
            pred = head_bits.decode(cur)
        elif arm == "oo_rec":
            h, _ = gpt(ids); s = h[:, -1]
            for t in range(k): s = cell(s)
            pred = head_bits.decode(s)
        elif arm in ("oo_pause_a", "oo_pause_s"):
            x = torch.cat([gpt.wte(ids), slot.expand(B, k, d)], 1)
            h, past = gpt(embeds=x)
            P = ids.shape[1]
            past_t = [(kk[:, :, :P + k], vv[:, :, :P + k]) for kk, vv in past]
            pred = readout_decode(h[:, P + k - 1], past_t)
        elif arm == "oo_lat_a":
            h, past = gpt(ids); cur = h[:, -1]
            for t in range(k):
                h2, past = gpt(embeds=lat_in(cur)[:, None], past=past); cur = h2[:, -1]
            pred = readout_decode(cur, past)
        elif arm == "oo_pause":
            x = torch.cat([gpt.wte(ids), slot.expand(B, k, d)], 1)
            h, _ = gpt(embeds=x)
            pred = head_bits.decode(h[:, -1])
        elif arm == "oo_bansal":
            h, _ = gpt(ids); r = h[:, -1]; s = r
            for t in range(k): s = recall_ln(s + recall_cell(torch.cat([s, r], -1)))
            pred = head_bits.decode(s)
        elif arm == "oo_mat":
            h, _ = gpt(ids); hh = h[:, -1]
            Wf = mat_gen(hh).view(B, d, d) / math.sqrt(d)
            s = s_init(hh)
            for t in range(k):
                s = mat_ln(s + F.gelu(torch.bmm(Wf, s[:, :, None])[:, :, 0]))
            pred = head_bits.decode(s)
        return (pred == final).all(-1).float().sum().item(), (pred == final).float().sum().item(), n * W

    @torch.no_grad()
    def evaluate(k, n=2000, chunk=250):
        # chunked so a k=32 eval (sequences near 900 tokens for the token arm, with a KV
        # cache per position) fits alongside the other jobs on the card
        gpt.eval(); extra.eval()
        ex = bits = tot_bits = 0.0; done = 0
        while done < n:
            m = min(chunk, n - done)
            e, b, tb = _eval_chunk(k, m)
            ex += e; bits += b; tot_bits += tb; done += m
        gpt.train(); extra.train()
        return {"k": k, "exact": ex / n, "bit": bits / tot_bits}

    # ------------------------------------------------------------------ loop
    ckpt_path = f"{out_dir}/{tag}_{arm}_s{seed}.pt"
    if eval_only:
        st = torch.load(eval_only, map_location=dev)
        gpt.load_state_dict(st["gpt"]); extra.load_state_dict(st["extra"])
        log["reeval_of"] = eval_only; tag = tag + "_reeval"; steps = 0
    t0 = time.time()
    for step in range(steps):
        k = ks_train[step % len(ks_train)] if len(ks_train) > 1 else ks_train[0]
        loss = train_step(k)
        opt.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sched.step()
        if step % 1000 == 0 or step == steps - 1:
            log["train"].append({"step": step, "loss": loss.item(), "t": time.time() - t0})
            print(f"[{arm} {tag}] step {step} loss {loss.item():.4f} t={time.time()-t0:.0f}s", flush=True)
    if not eval_only:
        os.makedirs(out_dir, exist_ok=True)
        torch.save({"gpt": gpt.state_dict(), "extra": extra.state_dict(), "arm": arm, "pos": pos, "block": block}, ckpt_path)
    log["eval"] = [evaluate(k) for k in k_eval]
    print(f"[{arm} {tag}] EVAL", json.dumps(log["eval"]), flush=True)
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/{tag}_{arm}_s{seed}.json", "w") as f:
        json.dump(log, f, indent=1)
    return log


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--ks", default="1")
    ap.add_argument("--k-eval", default="")
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="run")
    ap.add_argument("--out", default="results")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--pos", default="abs", choices=["abs", "rope"], help="learned absolute positions, or rotary as in the paper's GPT-NeoX")
    ap.add_argument("--block", default="seq", choices=["seq", "parallel"], help="sequential attn then MLP, or GPT-NeoX parallel from one norm")
    ap.add_argument("--eval-only", default="", help="path to a saved .pt; skip training, re-run the eval, write <tag>_reeval")
    ap.add_argument("--spec", default="orbit", choices=["orbit", "table"],
                    help="orbit: infer the rule from 10 prior states (paper setup); table: the 32-bit rule is given")
    a = ap.parse_args()
    ks = tuple(int(x) for x in a.ks.split(","))
    ke = tuple(int(x) for x in a.k_eval.split(",")) if a.k_eval else ks
    run_arm(a.arm, ks, ke, a.steps, a.seed, a.tag, a.out, a.spec, a.batch, a.pos, a.block, a.eval_only)
