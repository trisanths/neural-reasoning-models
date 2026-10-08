"""Which (small, big) pair gives the most impressive savings?

The pipeline costs roughly the small model plus a compressed slice of the big
one, so the headline ratio is driven by the capacity gap between them. A 5x gap
(1.5B -> 7B) cannot produce a dramatic number no matter how well compression
works; a 64x gap can.

Also reports whether each pair fits in one H200 (141 GB) for LoRA training with
both models in a single backward graph.
"""

from dataclasses import dataclass


@dataclass
class M:
    name: str
    d: int
    layers: int
    heads: int
    kv: int
    ffn: int
    params: float
    vocab: int = 152064

    @property
    def macs(self) -> int:
        dk = self.d * self.kv // self.heads
        attn = 2 * self.d * self.d + 2 * self.d * dk
        return self.layers * (attn + 3 * self.d * self.ffn)


QWEN = {
    "0.5B": M("Qwen2.5-0.5B", 896, 24, 14, 2, 4864, 0.49e9),
    "1.5B": M("Qwen2.5-1.5B", 1536, 28, 12, 2, 8960, 1.54e9),
    "3B": M("Qwen2.5-3B", 2048, 36, 16, 2, 11008, 3.09e9),
    "7B": M("Qwen2.5-7B", 3584, 28, 28, 4, 18944, 7.62e9),
    "14B": M("Qwen2.5-14B", 5120, 48, 40, 8, 13824, 14.8e9),
    "32B": M("Qwen2.5-32B", 5120, 64, 40, 8, 27648, 32.8e9),
    "72B": M("Qwen2.5-72B", 8192, 80, 64, 8, 29568, 72.7e9),
}


def prefill(m: M, n: int) -> float:
    return 2 * (n * m.macs + m.layers * 2 * (n * (n + 1) / 2) * m.d)


def step(m: M, ctx: int) -> float:
    return 2 * (m.macs + m.layers * 2 * ctx * m.d)


def decode(m: M, ctx: int, n: int) -> float:
    return sum(step(m, ctx + i) for i in range(n)) + 2 * n * m.d * m.vocab


L, K, DEC, COT = 400, 6, 8, 49  # ProsQA shape


def analyse(s: M, b: M, m_compress: int):
    small_only = prefill(s, L) + decode(s, L, DEC)
    big_cot = prefill(b, L) + decode(b, L, COT + DEC)
    pipe = (
        prefill(s, L)
        + sum(step(s, L + i) for i in range(K))
        + decode(s, L + K, DEC)
        + prefill(b, m_compress)
        + sum(step(b, m_compress + i) for i in range(K))
        + 2 * (m_compress * s.d * b.d + K * b.d * s.d)
    )
    return small_only, big_cot, pipe


print("=" * 92)
print(f"ProsQA shape: {L}-token prompt, {K} latents, {COT}-token CoT baseline, m=32 compression")
print("=" * 92)
print(f"{'pair':<16} {'ratio':>6}  {'pipe/small':>10} {'pipe vs big-CoT':>16} {'H200 bf16 LoRA':>16}")
print("-" * 92)

H200_GB = 141
for sk, bk in [
    ("1.5B", "7B"),
    ("0.5B", "7B"),
    ("1.5B", "14B"),
    ("0.5B", "14B"),
    ("1.5B", "32B"),
    ("0.5B", "32B"),
    ("0.5B", "72B"),
]:
    s, b = QWEN[sk], QWEN[bk]
    small_only, big_cot, pipe = analyse(s, b, 32)
    # bf16 weights for both, plus activations/optimizer headroom for LoRA.
    gb = (s.params + b.params) * 2 / 1e9
    fits = "fits" if gb + 25 < H200_GB else ("4-bit only" if gb / 4 + 25 < H200_GB else "no")
    print(
        f"{sk + ' -> ' + bk:<16} {b.params / s.params:5.0f}x  "
        f"{pipe / small_only:9.2f}x {big_cot / pipe:14.1f}x cheaper  "
        f"{gb:6.0f} GB  {fits:>9}"
    )

print()
print("Training cost for the big model, LoRA on reduced ProsQA (2000 ex, 8 stages):")
tokens = 2000 * 400 * 8
for k in ["7B", "14B", "32B", "72B"]:
    f = 4 * QWEN[k].params * tokens
    print(f"  {k:>4}  {f / 450e12 / 3600:5.2f} h on H200   {f / 80e12 / 3600:5.2f} h on L40S")
