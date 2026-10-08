# What is in S3 and not in git

Every experiment in this repository ran on EC2 and wrote its artifacts to
`s3://decoupled-reasoner-009398924577`. The results that matter for reading the
work are committed here under `results/`. Three classes of artifact are not,
because git is the wrong store for them.

Model checkpoints are excluded by `.gitignore` (`*.pt`, `*.safetensors`). The
item banks and the thinking-on generation traces are excluded by size: both are
regenerable, the item banks deterministically from the build scripts and
manifests that are committed, the traces by re-running inference.

The instance stores on the training boxes (`/mnt/nvme`) were ephemeral and are
gone. Anything that was not uploaded to S3 or committed does not exist any more.

## Bucket by prefix

| prefix | objects | size |
|---|---:|---:|
| `runs/` | 3343 | 6.5 TB |
| `recovered/` | 17957 | 213.9 GB |
| `data/` | 33555 | 162.0 GB |
| `latent/` | 66 | 5.6 GB |
| `role-xfer/` | 21 | 2.1 GB |
| `staging/` | 1651 | 1.5 GB |
| `tmp/` | 34 | 116.9 MB |
| `results/` | 558 | 72.4 MB |
| `code/` | 119 | 22.8 MB |
| `frames-sweep/` | 52 | 9.6 MB |
| `xfer/` | 88 | 6.9 MB |
| `scratch/` | 3 | 4.4 MB |
| `role-back/` | 101 | 3.7 MB |
| `pilot-staging/` | 64 | 3.1 MB |
| `ladder_cd/` | 19 | 1.9 MB |
| `pull-eval-loop/` | 112 | 739.9 KB |
| `logs/` | 14 | 110.4 KB |
| `verify/` | 2 | 5.6 KB |
| **total** | **57759** | **6.9 TB** |

`recovered/2026-10-05/` is a rescue copy of the development box's training data,
taken before the box was reclaimed. `code/` holds dated source tarballs from
before the work was tracked in git. The rest follow the run names used in the
experiment documents.

## Large artifacts left in S3

### model checkpoints

1399 objects, 6.6 TB total.

| size | object |
|---:|---|
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0005400.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0005700.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0006000.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0006300.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0006600.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0006900.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0007200.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0007500.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0007800.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0008100.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0008400.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0008700.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0009000.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0009300.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0009600.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0009900.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0010200.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0010500.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0010800.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0011100.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0011400.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0011700.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0012000.pt` |
| 15.1 GB | `runs/curve/curve-1300m-a/ckpt-0012300.pt` |
| | ...and 1375 more |

### item banks

5 objects, 162.3 MB total.

| size | object |
|---:|---|
| 34.0 MB | `runs/pilot-acq/box-final/items/items.jsonl` |
| 34.0 MB | `runs/pilot-acq/items/items.jsonl` |
| 31.5 MB | `runs/pilot-acq/box-final/dev/items_v2_hashseed7.jsonl` |
| 31.5 MB | `runs/pilot-acq/box-final/items/items_v2.jsonl` |
| 31.5 MB | `runs/pilot-acq/items/items_v2.jsonl` |

### thinking-on generation traces

13 objects, 330.0 MB total.

| size | object |
|---:|---|
| 48.8 MB | `runs/pilot-acq/box-final/records/gen__qwen3-1.7b__think1.jsonl` |
| 48.8 MB | `runs/pilot-acq/records/gen__qwen3-1.7b__think1.jsonl` |
| 42.3 MB | `runs/pilot-acq/box-final/records/gen__qwen3-8b__think1.jsonl` |
| 42.3 MB | `runs/pilot-acq/records/gen__qwen3-8b__think1.jsonl` |
| 42.0 MB | `runs/pilot-acq/box-final/records/gen__qwen3-4b__think1.jsonl` |
| 42.0 MB | `runs/pilot-acq/records/gen__qwen3-4b__think1.jsonl` |
| 30.9 MB | `runs/pilot-acq/box-final/records/gen__qwen3-0.6b__think1.jsonl` |
| 30.9 MB | `runs/pilot-acq/records/gen__qwen3-0.6b__think1.jsonl` |
| 413.5 KB | `runs/pilot-acq/box-final/smoke/records/gen__qwen3-0.6b__think1.jsonl` |
| 413.5 KB | `runs/pilot-acq/smoke/records/gen__qwen3-0.6b__think1.jsonl` |
| 411.4 KB | `runs/pilot-acq/box-final/dev/gen__qwen3-0.6b__think1.jsonl` |
| 403.1 KB | `runs/pilot-acq/box-final/smoke_v2/records/gen__qwen3-0.6b__think1.jsonl` |
| 403.1 KB | `runs/pilot-acq/smoke_v2/records/gen__qwen3-0.6b__think1.jsonl` |
