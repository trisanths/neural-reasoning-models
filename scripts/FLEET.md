# GPU fleet

Four g6e.xlarge boxes, one NVIDIA L40S each, so independent lanes stop queueing
behind one card. Everything runs over SSM. There are no key pairs and no inbound
ports: the security group sg-05ae7cbcedfdccff3 has no ingress rules at all.

## The boxes

| worker | Name tag | instance | zone | what it is for |
|---|---|---|---|---|
| dev | decoupled-reasoner-dev | i-00b1114be36214a6c | us-east-1c | the original box, built by hand, 300 GB root, no instance store mounted |
| 1 | nrm-worker-1 | i-07781a7e6ee1537ca | us-east-1c | role-representation training arms, 45M models |
| 2 | nrm-worker-2 | i-0abbda48fb718e7a2 | us-east-1c | real-document retrieval training |
| 3 | nrm-worker-3 | i-03cb7b22112ee874d | us-east-1a | E3 pretrain at 350M, 13.36B tokens |

Workers 1 to 3 are identical hardware built from one script. The dev box is not:
it was set up by hand, it has no `~/BOOTSTRAP_OK` marker, and its large
directories sit on the root volume rather than on instance store.

That is 16 G and VT vCPUs against a quota of 16. There is no room for a fifth
GPU box until one of these is terminated.

## Addressing a worker

    export AWS_PROFILE=chronos
    bash scripts/worker_run.sh 2 'nvidia-smi'

The first argument is a worker number, `dev` for the original box, any Name tag,
or an `i-` instance id. The command runs as ec2-user under `bash -lc`, so
`~/.bashrc` and `~/.exa_env` apply.

SSM gives up near 300 seconds and truncates the reply near 24 KB, so start
anything long detached and poll it in separate calls:

    bash scripts/worker_run.sh 2 'cd ~/decoupled-reasoner && setsid nohup uv run python -m src.corpus.cli ... > ~/logs/lane.log 2>&1 < /dev/null & echo started'
    bash scripts/worker_run.sh 2 'tail -20 ~/logs/lane.log'

`worker_run.sh`, `fleet_status.sh` and `launch_worker.sh` run from wherever you
drive the fleet, with `AWS_PROFILE=chronos`. They are not meant to run on a
worker.

## Seeing the whole fleet

    bash scripts/fleet_status.sh

One row per box: instance id, type, state, zone, SSM ping, GPU utilisation and
memory, one-minute load, free space on the root volume and on the instance
store, and the bootstrap marker. `--json` for scripting. The on-box numbers come
from a single SSM command fanned out to every reachable instance, so it stays
one round trip however many workers there are, and it skips boxes SSM cannot
reach rather than failing the whole call. It takes about four seconds.

The BOOT column reads `ok`, `running`, `FAILED`, or `manual` for a box this
fleet's bootstrap never touched, which is what the dev box will always say.

## What a worker has

Built from the Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.12 on Amazon
Linux 2023 (ami-0eb4d8bc9eb48d8ae), 200 GB gp3 root, 250 GB instance store.

    ~/decoupled-reasoner        the code snapshot, no .git, commit in .snapshot_commit
    ~/decoupled-reasoner/.venv  uv sync --frozen against the snapshot uv.lock
    ~/data                      tokenizer_v2.json plus whatever datasets it was told to pull
    ~/ckpt                      whatever checkpoints it was told to pull
    ~/runs ~/results ~/logs     outputs
    ~/BOOTSTRAP_OK              JSON marker: commit, python, torch, GPU, timings
    ~/bootstrap.log             the whole bootstrap transcript

Python 3.12.14, torch 2.13.0+cu130. A worker has no GitHub credentials and
cannot clone; it gets code from the S3 snapshot only.

## How long a worker takes to come up

From `run-instances` to `~/BOOTSTRAP_OK`, measured on the boxes above:

| stage | time |
|---|---|
| run-instances to the bootstrap's first log line | about 2 minutes 30 seconds |
| code, uv sync, tokenizer, one 4.2 GB checkpoint | 78 seconds |
| the same plus 26.7 GB of regime_e3 across 1,990 objects | 182 seconds |
| re-running it on a box that is already set up | 5 to 20 seconds |

So about 4 minutes end to end for a plain worker and about 5 minutes 30 seconds
for one that pulls the big pretraining set. Poll `~/BOOTSTRAP_OK`, or watch the
BOOT column, rather than guessing.

## The instance store is ephemeral

`~/data`, `~/runs`, `~/results`, `~/logs`, `~/ckpt`, `~/.cache/huggingface` and
the repo's own `data/ results/ runs/ logs/` are symlinks into `/mnt/nvme`, which
is the 250 GB instance store. That disk is wiped when the instance stops and
does not come back on start.

The root volume filling up killed four training lanes on this project before,
and the dev box is at 90% with an 11 GB HuggingFace cache on it, which is why
the big directories live on the instance store. The trade is real: never leave
the only copy of a result there. Sync anything worth keeping to S3 as you go,
the way `code/mirror_all.sh` does.

The uv cache stays on the root volume on purpose. uv hardlinks out of it into
`.venv`, and a cache on another filesystem turns every install into a copy.

The dev box has no instance store mounted, so its `/ FREE` column is the number
that matters there.

## Giving a worker its payload

The bootstrap pulls only what it is told to, because worker 3's dataset is
26.7 GB and worker 1 has no use for it. Both knobs take space separated S3 URIs;
a prefix ending in `/` is synced, anything else is copied.

    CKPTS="s3://decoupled-reasoner-009398924577/runs/corpus-v1-8k/final.pt"
    DATASETS="s3://decoupled-reasoner-009398924577/data/regime_e3/"

Checkpoints land in `~/ckpt`. A generic name keeps its run directory on the
front, so `runs/corpus-v1-8k/final.pt` becomes `~/ckpt/corpus-v1-8k-final.pt`
and two runs cannot collide.

To add a payload to a worker that is already up, run the bootstrap again with
the extra URIs. It is safe to re-run: every step checks for its own result
first. Run it from the copy outside the repo, since a run started from
`scripts/bootstrap_worker.sh` would be overwriting its own file as it unpacks
the snapshot:

    bash scripts/worker_run.sh 1 'aws s3 cp s3://decoupled-reasoner-009398924577/code/bootstrap_worker.sh ~/bootstrap_worker.sh --region us-east-1 --quiet && chmod +x ~/bootstrap_worker.sh && setsid nohup env WORKER_NAME=nrm-worker-1 DATASETS="s3://decoupled-reasoner-009398924577/data/skillacq/" bash ~/bootstrap_worker.sh > /dev/null 2>&1 < /dev/null & echo started'

## The Exa key

`NEED_EXA=1` makes the bootstrap read `/decoupled-reasoner/exa-api-key` from
Parameter Store through the instance role and write `~/.exa_env` mode 600. The
key never appears in a launch command, a tag, or a log. `NEED_EXA=0`, the
default, deletes `~/.exa_env` instead. Only `src/retrieval_web` reads
`EXA_API_KEY`, so none of workers 1 to 3 carry one today.

## Checking that a worker actually works

    bash scripts/worker_run.sh 1 'cd ~/decoupled-reasoner && setsid nohup bash scripts/worker_selftest.sh 8 > ~/logs/selftest.log 2>&1 < /dev/null & echo started'
    bash scripts/worker_run.sh 1 'tail -20 ~/logs/selftest.log'

This puts the RL base checkpoint on the GPU and scores a slice of the primitives
suite, 224 items in about 35 seconds. It needs `~/ckpt/*rlsimple*final.pt`, so
stage that checkpoint on any worker you want to run it on. A worker that only
proves it can import torch has not proved anything.

## Publishing new code

Workers follow `s3://decoupled-reasoner-009398924577/code/LATEST`, which holds
the key of the newest snapshot. From a box that has the repo:

    bash scripts/publish_code.sh

That tars the worktree minus `.venv`, `__pycache__`, `data`, `results`, `runs`,
`logs` and anything gitignored, names it by the HEAD commit, and writes a
manifest recording whether the worktree was dirty. It also refreshes
`code/bootstrap_worker.sh`, which is the copy a fresh box downloads before it
has any code. New workers pick the snapshot up automatically; existing workers
take it on their next bootstrap run.

To pin a worker to a specific snapshot rather than the newest, pass
`CODE_KEY=code/repo-<sha>.tar.gz`.

## Bringing up a replacement

If a worker dies, terminate it and launch its number again. This is the whole
command, for worker 3:

    export AWS_PROFILE=chronos
    cd ~/decoupled-reasoner
    aws ec2 terminate-instances --region us-east-1 --instance-ids i-03cb7b22112ee874d
    DATASETS="s3://decoupled-reasoner-009398924577/data/regime_e3/" bash scripts/launch_worker.sh 3

For worker 1 and worker 2 the payload argument is the `CKPTS` line from the
table below instead:

    worker 1  CKPTS="s3://decoupled-reasoner-009398924577/runs/final/rlsimple-503-921/final.pt"
    worker 2  CKPTS="s3://decoupled-reasoner-009398924577/runs/corpus-v1-8k/final.pt"
    worker 3  DATASETS="s3://decoupled-reasoner-009398924577/data/regime_e3/"

Give it the payload it had, or it comes up with code and tokenizer only.

`launch_worker.sh` refuses to start a second box with the same Name tag and
refuses to start anything that would put the account over its G and VT vCPU
quota, so the terminate has to land first. Terminating releases the quota within
a few seconds; stopping does not, because a stopped G instance still counts
against it.

## Capacity

g6e.xlarge is offered in us-east-1a, us-east-1b, us-east-1c and us-east-1d only.
1e and 1f do not sell it at all, so there is no point trying them.

On 2026-09-01 every one of those four zones refused g6e.xlarge on every targeted
request, all day. All three workers were placed by the fallback that asks for no
subnet at all and lets EC2 choose:

| worker | rounds of sweeping | landed in |
|---|---|---|
| 1 | 3 | us-east-1c |
| 3 | 1 | us-east-1a |
| 2 | 9, about nine minutes | us-east-1c |

Not one targeted `--subnet-id` request succeeded, including requests for the
same zone that the no-subnet request then placed the instance in seconds later.
Keep that fallback, and do not read a zone's refusal as that zone being full.

`launch_worker.sh` sweeps the zones, makes the no-subnet request, waits 60
seconds and sweeps again until `LAUNCH_DEADLINE` (default 1800 seconds). If a
launch is still failing after half an hour, raise `LAUNCH_DEADLINE` and leave it
running rather than sitting on it.

## Cost

| item | rate |
|---|---|
| g6e.xlarge on demand, us-east-1 Linux | $1.861 per hour |
| 200 GB gp3 root | $0.022 per hour |
| 250 GB instance store | included in the instance |
| one worker | $1.883 per hour |

The dev box carries a 300 GB root instead, so it is $1.894 per hour.

| | per hour | per day |
|---|---|---|
| the three new workers | $5.649 | $135.58 |
| the whole fleet of four | $7.543 | $181.03 |

Nothing here is on a savings plan or a reservation, so the meter stops when the
instances stop. A stopped instance still bills for its EBS root, $0.022 per
hour, and loses everything on its instance store. Terminate a worker you are
finished with rather than stopping it, and the quota comes back too.
