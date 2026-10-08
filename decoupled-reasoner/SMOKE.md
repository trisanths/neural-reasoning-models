# Smoke run 001

First end to end run of the full pipeline on the L40S instance, 2026-08-23.
Everything below ran from the committed code with the commands shown.

## What ran

1. Procedural warm-up data: 5,000,000 tokens from src.procgen.cli, seed 1,
   default mix, written to ~/data/proc.bin.
2. Worlds: 2,000 episodes from src.worldgen.cli, seed 1234, all four domains
   cycled evenly (500 episodes each), 9,341 questions total, every episode
   validated, written to ~/data/worlds.jsonl.
3. Tokenizer: byte level BPE trained on a rendered text sample of 500
   episodes. The merge count saturated at 18,236 of the requested 32,768
   because the synthetic sample has limited surface diversity; the model
   keeps vocab_size 32768 so the layout matches SPEC.md. Full scale runs
   train the tokenizer on the mixed sample of all regimes, which will reach
   the full vocabulary.
4. Shards: the 2,000 episodes rendered to 915,160 uint16 tokens in one shard.
5. Training: configs/smoke.yaml on cuda with bf16 autocast. 23,204,096 total
   parameters, 6,426,880 non embedding. 20 warm-up phase steps on proc.bin,
   then the main phase on the shards, 2,000 optimizer steps total, batch 16,
   sequence length 1024.
6. Evals: knowledge probes and the held-out worlds suite from src.evals.cli
   against the final checkpoint, held-out seed 999, 40 fresh episodes.

## Numbers

- First logged loss (step 10): 9.5296. Final loss (step 2000): 0.2150,
  about 2.3 percent of the initial value. No NaN anywhere in loss.jsonl.
- Training wall time: 2 minutes 20 seconds, against a 45 minute budget.
- Held-out worlds: accuracy 0.3037 over 191 questions, chance rate 0.3128.
  At this scale and token budget the model is at chance, which is the
  expected result; the run only proves the suite is mechanical.
- Knowledge probes: accuracy 0.1750 on 40 four way probes, chance 0.25,
  leakage threshold 0.4554, leakage flag clear. The regime C requirement
  that the model knows nothing about the real world holds.

## Artifacts

s3://decoupled-reasoner-009398924577/runs/smoke-001/ holds the tokenizer,
the config, loss.jsonl, both eval report files, and the data meta files.
Raw data and checkpoints stay on the instance, per the repo policy that
nothing under data/ or checkpoints/ is committed.

## Notes for the next run

- The main phase saw the 915k shard tokens about 35 times over. Loss this
  low mostly reflects memorization, which is fine for a smoke but the real
  runs need episode counts matched to the token budget.
- The renderer does not yet emit retrieve and result loops; the special
  tokens exist and the oracle retriever is the next integration step.
- The naturalized reading suite and the retrieval-noise axis from SPEC.md
  section 6 are not implemented yet; evals currently covers the knowledge
  probes and held-out worlds.
