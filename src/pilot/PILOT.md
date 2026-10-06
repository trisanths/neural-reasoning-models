# The acquisition pilot

Inference only. Whether sub-1B base models acquire never-seen procedures from
textbook pages, and how much entity knowledge they hold, read off the same
records by the rules registered in `PREREGISTERED.md` under "Acquisition
pilot". This file says how to run it and what the smoke run showed. It
reports no pilot result.

## Pieces

    src/pilot/items.py       item set: refuniverse L1-L8, algebra L2-L5, four rule families
    src/pilot/skills.py      the skillacq rule families as bench.py universes, with siblings
    src/pilot/popqa.py       PopQA as a 4-way forced choice by length-normalised likelihood
    src/pilot/grade.py       strict grader, hedge flag, lenient score, hedging canary
    src/pilot/vllm_model.py  the vLLM ModelFn: base completion, chat, capped thinking
    src/pilot/runner.py      models x thinking x conditions, resume-safe, mirrored to S3
    src/pilot/report.py      per-cell tables and the preregistered decision

The sibling and blank conditions, and the guard run against what they serve,
live in `src/mathgen/bench.py`. The scoring rule lives in `src/evals/mc.py`.

## Running it on the pilot box

Two environments. Item generation and tests run in the repo environment
(`uv run`); anything that loads a model runs in `/mnt/nvme/vllm-venv`, with
`HF_HOME=/mnt/nvme/hf`.

    uv run python scripts/pilot_items.py --manifests /mnt/nvme/pilot/data-manifests \
        --out /mnt/nvme/pilot/items/items.jsonl
    HF_HOME=/mnt/nvme/hf /mnt/nvme/vllm-venv/bin/python scripts/pilot_popqa.py \
        --out /mnt/nvme/pilot/items/popqa_fc.jsonl

The full run, every model, both thinking modes where a model has them, all
four conditions and PopQA:

    cd /home/ec2-user/decoupled-reasoner && HF_HOME=/mnt/nvme/hf HF_HUB_OFFLINE=1 \
      nohup /mnt/nvme/vllm-venv/bin/python scripts/pilot_run.py \
        --items /mnt/nvme/pilot/items/items.jsonl \
        --popqa /mnt/nvme/pilot/items/popqa_fc.jsonl \
        --out /mnt/nvme/pilot/records \
        --s3 s3://decoupled-reasoner-009398924577/runs/pilot-acq/records \
        --models all > /mnt/nvme/pilot/run.log 2>&1 &

Rerunning the same command resumes: keys already on disk are skipped. Then

    uv run python scripts/pilot_report.py --items /mnt/nvme/pilot/items/items.jsonl \
        --popqa /mnt/nvme/pilot/items/popqa_fc.jsonl \
        --records /mnt/nvme/pilot/records --out /mnt/nvme/pilot/report

which refuses while `RUNNING.lock` exists.

## Things that bit during setup

FlashInfer's top-k/top-p sampler compiles itself on first use and needs nvcc,
which the box does not have; `vllm_model.py` sets
`VLLM_USE_FLASHINFER_SAMPLER=0` before vLLM is imported.

A vLLM engine core is its own process and outlives a parent that is killed,
keeping its GPU memory. The runner shuts each engine down, leaves the child
with `os._exit` (vLLM's teardown at interpreter exit aborted with "terminate
called without an active exception" after the records were written), and
the parent stops any engine process of its user that is still alive.

The guard's `not_corpus_mode` broke ties in set iteration order, so the item
set changed with `PYTHONHASHSEED`. Fixed in 1b0a6d7; a test builds the smoke
set under three hash seeds.

## Smoke run, 2026-10-05

24 items from seeds 5,000,000 above the real ones (one refuniverse item per
level, two algebra items per level, two per rule family), sha256
`92ad2d22462ef23a58d84ca2b32e7a3ef8b9af22c294bc6c1c49427f644e92dd`, four
conditions each, plus the first 200 PopQA items. Records under
`/mnt/nvme/pilot/smoke/records`, mirrored to
`s3://decoupled-reasoner-009398924577/runs/pilot-acq/smoke/`. These counts
prove the path; at n = 24 per condition they say nothing about the models.

| configuration | closed_book | oracle | sibling | blank | hedges (of 96) | PopQA (of 200), mean NLL / summed NLL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LFM2.5-350M-Base | 0/24 | 2/24 | 2/24 | 0/24 | 7 | 66 / 70 |
| Qwen3-0.6B, thinking off | 0/24 | 6/24 | 3/24 | 0/24 | 6 | 54 / 66 |
| Qwen3-0.6B, thinking on | 0/24 | 11/24 | 4/24 | 0/24 | 2 | (same model) |

Thinking on used 105,381 thinking tokens over 96 prompts and hit the 4,096
cap on 13 of them. The report built from these records and returned "not
reached: records incomplete", as it should with two base models absent, and
failed rule 1 on every cell, as it must at n = 1 or 2 per cell.

## Throughput, and what the full run costs

`--probe 384` timed generation on the same 384 prompts drawn at random from
the full item set (all families and conditions) for every configuration,
grading and recording nothing. Rows are in
`/mnt/nvme/pilot/probe/throughput_probe.jsonl`, mirrored to
`s3://decoupled-reasoner-009398924577/runs/pilot-acq/probe/`. Hours are the
probe's seconds per prompt times the 5,760 prompts of the full set.

| configuration | seconds for 384 | generated tokens | think cap hit | hours for 5,760 |
| --- | ---: | ---: | ---: | ---: |
| LFM2.5-350M-Base | 2.2 | 9,216 | - | 0.009 |
| LFM2.5-350M | 2.1 | 920 | - | 0.009 |
| Qwen3-0.6B-Base | 4.2 | 6,923 | - | 0.018 |
| Qwen3-0.6B, thinking off | 5.4 | 8,150 | - | 0.022 |
| Qwen3-0.6B, thinking on | 209.1 | 532,239 | 56 | 0.871 |
| Qwen3-1.7B-Base | 6.8 | 5,351 | - | 0.028 |
| Qwen3-1.7B, thinking off | 9.8 | 15,890 | - | 0.041 |
| Qwen3-1.7B, thinking on | 493.7 | 954,120 | 126 | 2.057 |
| Qwen3-4B, thinking off | 20.6 | 5,725 | - | 0.086 |
| Qwen3-4B, thinking on | 609.7 | 806,006 | 74 | 2.540 |
| Qwen3-8B, thinking off | 35.3 | 3,742 | - | 0.147 |
| Qwen3-8B, thinking on | 898.1 | 825,161 | 84 | 3.742 |

Generation sums to 9.6 hours. Loading eight models adds about 10 minutes
(30 to 75 seconds each, measured), and PopQA takes under a minute per
model. The full run is about 10 GPU-hours on the one L40S, 96% of it in the
four thinking-on configurations.

The thinking cap binds often: 33% of Qwen3-1.7B's thinking runs on the probe
prompts hit 4,096 tokens, 22% of Qwen3-8B's and 19% of Qwen3-4B's. Every
record carries `think_truncated`, and the report prints the rate per cell.

PopQA likelihoods from vLLM were checked against a plain transformers
forward pass on LFM2.5-350M-Base for 24 option scorings: two vLLM calls agree
exactly, so prefix caching does not disturb prompt logprobs, and vLLM and
transformers differ by at most 0.52 nats per option (median under 0.1),
bfloat16 noise.
