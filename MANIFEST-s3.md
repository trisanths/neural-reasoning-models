# What is in S3 and not in git

Every experiment in this repository ran on EC2 and wrote its artifacts to
`s3://decoupled-reasoner-009398924577`. That bucket holds 57,759 objects and
6.87 TB. This repository carries the part of it that a reader needs and
leaves the rest where it is.

The filter is mechanical, so it can be checked: an object is committed unless it
is model weights or a binary shard, a generated corpus or tokenized shard, a
generated item bank, a thinking-on generation trace, a source tarball from
before the work was tracked in git, staging or scratch, an interrupted upload,
or larger than 20 MB.

The item banks and the generation traces are the only exclusions that are also
evidence. Both are reproducible: the item banks deterministically, from the
build scripts and manifests that are committed, after a commit on the pilot
branch removed their dependence on `PYTHONHASHSEED`; the traces by re-running
inference, which the pilot's own throughput probe puts at about ten GPU-hours on
an L40S, 96 percent of it in the four thinking-on configurations.

The instance stores on the training boxes, mounted at `/mnt/nvme`, were
ephemeral and are gone. Anything that was never uploaded to S3 and never
committed does not exist any more, and `decoupled-reasoner/src/STATE.md` names
the claims that rest on artifacts in that category.

## What is here

`results/s3/` holds 3333 objects, 493.1 MB, at the bucket's own
key layout. A path in that directory is the S3 key with `results/s3/` in front
of it, so anything here can be traced back to the object it came from.

| `results/s3/<prefix>` | objects | size |
|---|---:|---:|
| `runs/` | 2273 | 391.1 MB |
| `results/` | 558 | 72.4 MB |
| `frames-sweep/` | 52 | 9.6 MB |
| `role-xfer/` | 7 | 6.0 MB |
| `latent/` | 59 | 4.3 MB |
| `role-back/` | 101 | 3.7 MB |
| `xfer/` | 81 | 2.7 MB |
| `ladder_cd/` | 19 | 1.9 MB |
| `pull-eval-loop/` | 107 | 731.0 KB |
| `pilot-staging/` | 60 | 541.8 KB |
| `logs/` | 14 | 110.4 KB |
| `verify/` | 2 | 5.6 KB |

## What is not here, and why

| reason | objects | size |
|---|---:|---:|
| model weights and binary shards | 1077 | 6.5 TB |
| rescued training data | 17957 | 213.9 GB |
| generated corpora and tokenized shards | 33555 | 162.0 GB |
| interrupted uploads | 6 | 21.4 GB |
| staging and scratch | 1688 | 1.7 GB |
| thinking-on generation traces | 13 | 330.0 MB |
| generated item banks | 5 | 162.3 MB |
| over the 20 MB per-file cap | 1 | 30.6 MB |
| source tarballs predating git | 119 | 22.8 MB |
| test cache | 5 | 9.0 KB |
| **total excluded** | **54426** | **6.9 TB** |

Examples of the largest excluded object in each class:

- model weights and binary shards: `s3://decoupled-reasoner-009398924577/latent/xfer/base350.pt` (1.4 GB)
- rescued training data: `s3://decoupled-reasoner-009398924577/recovered/2026-10-05/dev/data/../../home/ec2-user/data/regime_a/parquet/000_00000.parquet` (2.0 GB)
- generated corpora and tokenized shards: `s3://decoupled-reasoner-009398924577/data/corpus/v1/external_heldout.jsonl` (16.2 MB)
- interrupted uploads: `s3://decoupled-reasoner-009398924577/runs/curve/curve-1300m-a/latest.pt.tmp` (9.3 GB)
- staging and scratch: `s3://decoupled-reasoner-009398924577/scratch/frames/drsrc.tgz` (3.3 MB)
- thinking-on generation traces: `s3://decoupled-reasoner-009398924577/runs/pilot-acq/box-final/records/gen__qwen3-1.7b__think1.jsonl` (48.8 MB)
- generated item banks: `s3://decoupled-reasoner-009398924577/runs/pilot-acq/box-final/items/items.jsonl` (34.0 MB)
- over the 20 MB per-file cap: `s3://decoupled-reasoner-009398924577/runs/corpus-v1-8k/artifacts/plan/extrap_step.jsonl` (30.6 MB)
- source tarballs predating git: `s3://decoupled-reasoner-009398924577/code/block2/autolaunch2.sh` (4.6 KB)
- test cache: `s3://decoupled-reasoner-009398924577/pull-eval-loop/.pytest_cache/README.md` (302 B)
