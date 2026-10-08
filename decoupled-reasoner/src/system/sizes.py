"""The rungs of the parameter ladder, above the 45M the normalizer stopped at.

`src/norm/nmodel.py` defines four sizes and the largest of them, `l`, is
45,483,008 parameters. On a held-out lexicon it reads 0.5150 to 0.8125 and on a
held-out sentence shape it does not move. The 350M checkpoint of
`src/corpus/RETRAIN.md` reads held-out frames at 0.990 to 1.000 on a comparable
split, so surface generalisation is somewhere between the two and nobody has
put a number on it.

These are the rungs that look for it. Every one is the same encoder-decoder as
`src/norm/nmodel.py:Normalizer`, built from the same `Config`, trained on the
same data with the same frame split, and scored by the same
`src/norm/neval.py`. Only width and depth change, so the ladder is a parameter
axis and nothing else.

    l45      d 512,  6+6 layers   45,483,008   the existing rung, restated
    xl93     d 640,  8+8 layers   93,579,520
    xxl167   d 768, 10+10 layers  167,182,336
    xxxl355  d 1024, 12+12 layers 355,127,936

The 93M line is the count the built model reported. The two above it are
`counts()`, which is a formula and is close rather than exact, and each is
replaced by its checkpoint's own number once that rung has run. Every number
in `src/system/THRESHOLD.md` comes from the checkpoint and not from here.

The top rung sits in the same class as `configs/350m.yaml`, which is
375,440,384 parameters, so the ladder reaches the size the corpus checkpoint
already generalises at.

Learning rates continue the schedule the norm lane used, which is inverse in
`d_model`: 512 x 4.0e-4 is 0.205, and each rung takes that constant over its
own width.
"""

from __future__ import annotations

from src.norm import nmodel

LADDER = {
    "l45": dict(d_model=512, n_head=8, n_enc=6, n_dec=6, d_ff=2048),
    "xl93": dict(d_model=640, n_head=10, n_enc=8, n_dec=8, d_ff=2560),
    "xxl167": dict(d_model=768, n_head=12, n_enc=10, n_dec=10, d_ff=3072),
    "xxxl355": dict(d_model=1024, n_head=16, n_enc=12, n_dec=12, d_ff=4096),
}

LR = {
    "l45": 4.0e-4,
    "xl93": 3.2e-4,
    "xxl167": 2.7e-4,
    "xxxl355": 2.0e-4,
}


def build(size: str, src_vocab: int, tgt_vocab: int, **kw):
    """One rung, as the norm lane's own model class."""
    cfg = nmodel.Config(src_vocab=src_vocab, tgt_vocab=tgt_vocab,
                        **{**LADDER[size], **kw})
    return nmodel.Normalizer(cfg)


def build_any(size: str, src_vocab: int, tgt_vocab: int, **kw):
    """A rung of this ladder, or a checkpoint the norm lane's sizes wrote.

    Both tables name the same model class built from the same `Config`, so a
    checkpoint from either lane rebuilds here.
    """
    if size in LADDER:
        return build(size, src_vocab, tgt_vocab, **kw)
    return nmodel.build(size, src_vocab, tgt_vocab, **kw)


def ft_lr(size: str) -> float:
    """The continuation rate for the transposed-operand fine tune.

    A tenth of the rung's peak. `results/norm/compare/ft_l_k1024.pt` was
    written at 4e-5 against a 4.0e-4 peak, so the 45M rung keeps its recorded
    value and every new rung takes the same ratio over its own peak.
    """
    return round(0.1 * LR[size], 8) if size in LR else None


def counts(src_vocab: int = 923, tgt_vocab: int = 155) -> dict:
    """Parameter counts without building anything on a device."""
    out = {}
    for name, s in LADDER.items():
        d, ff = s["d_model"], s["d_ff"]
        enc = s["n_enc"] * (4 * d * d + 2 * d * ff + ff + d + 2 * 2 * d)
        dec = s["n_dec"] * (8 * d * d + 2 * d * ff + ff + d + 3 * 2 * d)
        emb = (src_vocab + tgt_vocab + 1288 + 328) * d
        head = 0                      # tied to tgt_emb
        norms = 2 * 2 * d
        out[name] = {"total": enc + dec + emb + head + norms,
                     "embeddings": emb,
                     "non_embedding": enc + dec + norms}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(counts(), indent=1))
