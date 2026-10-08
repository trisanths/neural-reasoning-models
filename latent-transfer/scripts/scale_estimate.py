"""Compute estimate for running this pipeline at Qwen2.5 1.5B -> 7B scale.

Uses the real architectures (GQA, SwiGLU) rather than the simplified Arch in
src/flops.py, which assumes MHA and a 2-matrix MLP.
"""

from dataclasses import dataclass


@dataclass
class Model:
    name: str
    d: int
    layers: int
    heads: int
    kv_heads: int
    ffn: int
    vocab: int
    params: float  # total, for training-cost estimates

    @property
    def d_kv(self) -> int:
        return self.d * self.kv_heads // self.heads

    @property
    def macs_per_token(self) -> int:
        """Per layer: q + k + v + o projections, then SwiGLU (gate, up, down)."""
        attn = self.d * self.d + 2 * self.d * self.d_kv + self.d * self.d
        mlp = 3 * self.d * self.ffn
        return self.layers * (attn + mlp)


QWEN_1_5B = Model("Qwen2.5-1.5B", 1536, 28, 12, 2, 8960, 151936, 1.54e9)
QWEN_7B = Model("Qwen2.5-7B", 3584, 28, 28, 4, 18944, 152064, 7.62e9)


def prefill(m: Model, n: int) -> float:
    proj = n * m.macs_per_token
    attn = m.layers * 2 * (n * (n + 1) / 2) * m.d  # causal QK^T and AV
    return 2 * (proj + attn)


def step(m: Model, ctx: int) -> float:
    return 2 * (m.macs_per_token + m.layers * 2 * ctx * m.d)


def decode(m: Model, ctx: int, n: int) -> float:
    total = 0.0
    for i in range(n):
        total += step(m, ctx + i)
    total += 2 * n * m.d * m.vocab  # lm_head
    return total


def fmt(x: float) -> str:
    for u, s in [("E", 1e18), ("P", 1e15), ("T", 1e12), ("G", 1e9), ("M", 1e6)]:
        if abs(x) >= s:
            return f"{x / s:.2f}{u}"
    return f"{x:.0f}"


def hours(flops: float, tflops_effective: float) -> float:
    return flops / (tflops_effective * 1e12) / 3600


# ---------------------------------------------------------------- inference --
import sys
L = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
COT = int(sys.argv[2]) if len(sys.argv) > 2 else 800
DEC = int(sys.argv[3]) if len(sys.argv) > 3 else 200
K = 6
print("=" * 74)
print(f"INFERENCE, per query ({L}-token prompt, {K} latents, "
      f"{COT}-token CoT, {DEC}-token answer)")
print("=" * 74)

small_only = prefill(QWEN_1_5B, L) + decode(QWEN_1_5B, L, DEC)
big_only = prefill(QWEN_7B, L) + decode(QWEN_7B, L, DEC)
big_cot = prefill(QWEN_7B, L) + decode(QWEN_7B, L, COT + DEC)

print(f"1.5B alone, no reasoning        {fmt(small_only):>10}")
print(f"7B alone, CoT                   {fmt(big_cot):>10}   {big_cot / small_only:5.1f}x small")
print(f"7B alone, latent (Coconut)      {fmt(big_only):>10}   {big_only / small_only:5.1f}x small")

for m in (None, 32, 8):
    n_up = L if m is None else m
    pipe = (
        prefill(QWEN_1_5B, L)
        + sum(step(QWEN_1_5B, L + i) for i in range(K))
        + decode(QWEN_1_5B, L + K, DEC)
        + prefill(QWEN_7B, n_up)
        + sum(step(QWEN_7B, n_up + i) for i in range(K))
        + 2 * (n_up * QWEN_1_5B.d * QWEN_7B.d + K * QWEN_7B.d * QWEN_1_5B.d)
    )
    tag = "all states" if m is None else f"m = {m}"
    print(
        f"pipeline, {tag:<12}          {fmt(pipe):>10}   {pipe / small_only:5.1f}x small"
        f"   {pipe / big_cot:5.2f}x 7B-CoT"
    )

# ----------------------------------------------------------------- training --
print()
print("=" * 74)
print("TRAINING (LoRA on the 7B receiver: ~4 x params x tokens)")
print("=" * 74)
# LoRA still backprops through every frozen layer to reach earlier activations,
# so ~2N forward + ~2N backward-to-input. Weight grads are negligible.
BOTH = QWEN_1_5B.params + QWEN_7B.params
H100 = 400  # TFLOP/s sustained, ~40% MFU on bf16

for label, tokens in [
    ("GSM8K replication (~7.5k ex, 25 epochs)", 56e6),
    ("multi-dataset (~200k ex, 10 epochs)", 600e6),
    ("serious run", 5e9),
]:
    f = 4 * BOTH * tokens
    h = hours(f, H100)
    print(f"{label:<42} {fmt(f):>9}  {h:6.1f} H100-hours  (${h * 2.5:6.0f} at $2.50/h)")

print()
print("Memory (bf16, LoRA, gradient checkpointing):")
w = (QWEN_7B.params + QWEN_1_5B.params) * 2 / 1e9
print(f"  weights, both models resident        {w:5.1f} GB")
print("  activations + latent-chain graph      ~15-25 GB")
print("  -> one 80GB H100/A100 is enough; 40GB is tight")
