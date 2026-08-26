# Phase 2: knowledge-free reasoning scaling curve

Eight single-GPU runs on the 8x H100 box, iso-data at 7.0B tokens
(max_steps 26700 x 262,144 tokens per step = 6,999,244,800). Iso-data is the
design: at the 20 tokens-per-parameter heuristic 150m would want 3.0B and
1300m would want 26B, so the 150m runs are over-trained and the 1300m runs
under-trained relative to that heuristic, deliberately, to hold data
constant across sizes.

## Run matrix

| run           | gpu | size  | regime | seed | data                          | warm-up | micro x accum | ckpt every |
|---------------|-----|-------|--------|------|-------------------------------|---------|---------------|------------|
| curve-150m-a  | 0   | 150m  | A      | 111  | ~/data/regime_a/shards        | no      | 16 x 4        | 2500 steps |
| curve-150m-c  | 1   | 150m  | C      | 211  | ~/data/regime_c/flat          | yes     | 16 x 4        | 2500 steps |
| curve-700m-a  | 2   | 700m  | A      | 111  | ~/data/regime_a/shards        | no      | 4 x 16        | 500 steps  |
| curve-700m-c  | 3   | 700m  | C      | 211  | ~/data/regime_c/flat          | yes     | 4 x 16        | 500 steps  |
| curve-1300m-a | 4   | 1300m | A      | 111  | ~/data/regime_a/shards        | no      | 2 x 32        | 300 steps  |
| curve-1300m-c | 5   | 1300m | C      | 211  | ~/data/regime_c/flat          | yes     | 2 x 32        | 300 steps  |
| curve-350m-b  | 6   | 350m  | B      | 311  | ~/data/regime_b               | no      | 8 x 8         | 1000 steps |
| curve-150m-b  | 7   | 150m  | B      | 311  | ~/data/regime_b               | no      | 16 x 4        | 2500 steps |

Seeds: 111 for every A run, 211 for every C run, 311 for every B run.
Global batch is 64 sequences x 4096 context = 262,144 tokens per step for
every size; only the micro-batch x grad-accum split differs. Regime C runs
get `--warmup-bin ~/data/proc_warmup_15m.bin` (front-loaded procedural
warm-up, warmup_phase_steps from each size config); A and B runs do not.
The 350m size is not re-run for A and C: the six kill-test runs (seeds
101-103 A, 201-203 C) are those curve points.

## Data

| regime | path on the training box       | tokens          | source |
|--------|--------------------------------|-----------------|--------|
| A      | ~/data/regime_a/shards         | 7,500,274,047   | already on the box (kill test) |
| C      | ~/data/regime_c/flat           | 7,503,140,562   | already on the box (kill test) |
| B      | ~/data/regime_b                | 7,113,848,789   | s3://decoupled-reasoner-009398924577/data/regime_b/ |

Warm-up stream: ~/data/proc_warmup_15m.bin (regime C runs only).
Tokenizer: ~/data/tokenizer_v2.json (all data pre-tokenized; nothing at
train time reads the tokenizer).

Regime B was rendered on the dev box (scripts/render_regime_b.py, seed
31337, mix natural 0.80 / worldgen 0.15 / procgen 0.05, 212 chunks,
7,113,848,789 tokens, DONE reason target_reached, measured shares exactly
0.8000/0.1500/0.0500) and staged to S3 by stage_regime_b.sh at
2026-08-25T23:42:42Z (1062 objects, 14,227,943,894 bytes, verified equal to
2 bytes per token plus metadata). The renderer writes a merged index.json
whose shard entries point into the chunk-XXXXX subdirectories, so the
directory is directly loadable by ShardReader after download; there is no
consolidation pass. launch_curve.sh raises the open-file limit because the
regime B index maps ~420 shard files.

## Config audit (L40S probes, 46,068 MiB, compile on, ctx 4096)

The batch numbers in configs/150m.yaml, 700m.yaml, and 1300m.yaml were
guesses. Measured with probe_l40s.sh (real compiled training against the
regime A shards, peak from nvidia-smi polling, tok/s from loss.jsonl
elapsed deltas after the compile steps):

| size  | micro x accum | L40S peak MiB | L40S tok/s | verdict |
|-------|---------------|---------------|------------|---------|
| 150m  | 8 x 8         | 20,629        | 138,353    | fits |
| 150m  | 16 x 4        | 39,945        | 139,903    | fits, chosen |
| 700m  | 2 x 32        | 27,741        | 26,843     | fits |
| 700m  | 4 x 16        | 39,963        | 26,272     | fits, chosen |
| 700m  | 8 x 8         | OOM           | -          | 45,383 MiB observed before OOM |
| 1300m | 1 x 64        | 33,145        | 15,976     | fits |
| 1300m | 2 x 32        | 41,633        | 16,945     | fits, chosen |
| 1300m | 4 x 16        | OOM           | -          | 44,601 MiB observed before OOM |

Chosen (baked into the launch_curve.sh run table): 150m 16x4, 350m 8x8
(kill-test-proven, 43.3GB L40S, 148k tok/s live on the H100s now), 700m
4x16, 1300m 2x32. Reasoning: throughput is nearly flat in micro-batch at
ctx 4096 (the GPU saturates even at micro 1-2), so the pick is the largest
micro-batch that fits 46GB, which halves or quarters host-side loader
iterations per step for the H100 where per-step host overhead matters more.
Every chosen peak is at most 41.6GB on 46GB, strictly safe on 80GB.

1300m H100 micro-batch decision: kept at 2, no doubling. Micro 4 OOMed on
the L40S, so a doubling to 4 on the H100 would rest on extrapolation
(41,633 + 2 x 8,488 MiB per sequence, about 58.6GB, inside 80GB on paper)
rather than on a measured peak; and the measured 1 to 2 gain was only 6%,
so 2 to 4 is a couple of percent at best. An unattended OOM at launch costs
a whole GPU-lane overnight; empirical validation is the point of this
audit, so the H100 gets the L40S-validated value.

H100 projection uses the measured 350m anchor: 49,000 tok/s on the L40S in
kill-test tuning against 148,300 tok/s measured on the live kill-test H100
runs (loss.jsonl, late window), a ratio of 3.03x.

| size  | L40S tok/s | projected H100 tok/s | wall clock at 7.0B | ckpt cadence |
|-------|------------|----------------------|--------------------|--------------|
| 150m  | 139,903    | ~424,000             | ~4.6 h             | 2500 steps ~ 26 min |
| 350m  | 49,000     | 148,300 (measured)   | 13.1 h             | 1000 steps ~ 29 min |
| 700m  | 26,272     | ~79,600              | ~24.4 h            | 500 steps ~ 27 min |
| 1300m | 16,945     | ~51,300              | ~37.9 h            | 300 steps ~ 26 min |

The 150m projection is the least certain: the 3.03x ratio is anchored at
350m, and a 0.62s step leans harder on per-step host overhead, so treat
~424k as an upper band and read the real rate off loss.jsonl after launch.

The capacity block (cr-0fc31baec48544a59) ends 11:30 UTC Aug 26. Runs still
short of 26,700 steps at the boundary resume from the S3 checkpoint mirror:
pull runs/curve/ down and rerun launch_curve.sh, which is idempotent and
passes --resume on every run.

## Launch sequence (training box, after the eval battery finishes)

```
aws s3 sync s3://decoupled-reasoner-009398924577/data/regime_b/ ~/data/regime_b/ --only-show-errors
aws s3 sync s3://decoupled-reasoner-009398924577/code/phase2/ ~/phase2/ --only-show-errors
bash ~/phase2/launch_curve.sh
```

launch_curve.sh preflights the three data directories (index.json present
and total_tokens >= 6,999,244,800), generates one config per run through
make_run_config.py (which refuses any global-batch drift), writes cmd.txt
provenance into each run directory, launches each trainer detached with
CUDA_VISIBLE_DEVICES pinned per the matrix, logs to ~/logs/curve-<name>.log,
and starts the 30-minute sync-and-prune loop targeting
s3://decoupled-reasoner-009398924577/runs/curve/. Rerunning it is safe:
live runs are skipped, dead ones resume from latest.pt.

Package: s3://decoupled-reasoner-009398924577/code/phase2/
(launch_curve.sh, make_run_config.py, sync_loop.sh, stage_regime_b.sh,
probe_l40s.sh, CURVE.md). Dry-verified on the dev box with smoke configs at
DEVICE=cpu: all eight lanes generate correct configs and cmd.txt (warm-up
flag on exactly the C lanes) and the sync loop pushed run dirs to S3; the
trainer path was then proven serially per lane (done at step N, the SKIP
guard against a live trainer, and resumed-at-step-N relaunch idempotence),
with the curve-150m-b lane loading the real 7.11B-token regime B merged
index. Do not run all eight lanes concurrently on the 30GB dev box: eight
CPU torch processes exhaust RAM (it took the SSM agent down on 2026-08-26;
recovered by reboot). The p5.48xlarge with 2TB RAM is unaffected.
