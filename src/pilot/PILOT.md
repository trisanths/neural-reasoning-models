# The acquisition pilot

Inference only. Whether sub-1B base models acquire never-seen procedures from
textbook pages, and how much entity knowledge they hold, read off the same
records by the rules registered in `PREREGISTERED.md` under "Acquisition
pilot", with amendment 1 of 2026-10-06. This file says how to run it and what
the smoke run showed. It reports no pilot result.

## Pieces

    src/pilot/items.py       item set: refuniverse L1-L8, algebra L2-L5, four rule families;
                             per-condition floors from pools of guarded items
    src/pilot/skills.py      the skillacq rule families as bench.py universes, with siblings
    src/pilot/popqa.py       PopQA as a 4-way forced choice, rank-balanced distractors,
                             a subject-masked twin of every question
    src/pilot/grade.py       strict grader, hedge flag, lenient score, hedging canary
    src/pilot/vllm_model.py  the vLLM ModelFn: base completion, chat, capped thinking
    src/pilot/runner.py      models x thinking x conditions, resume-safe, mirrored to S3
    src/pilot/report.py      regrades the records, per-cell tables, the registered decision

The sibling and blank conditions, the guard run against what they serve and
the check that a sibling is a matched control (`sibling_match`) live in
`src/mathgen/bench.py`. The scoring rule lives in `src/evals/mc.py`.

## Running it on the pilot box

Two environments. Item generation, the report and the tests run in the repo
environment (`uv run`); anything that loads a model runs in
`/mnt/nvme/vllm-venv`, with `HF_HOME=/mnt/nvme/hf`.

    uv run python scripts/pilot_items.py --manifests /mnt/nvme/pilot/data-manifests \
        --floor-table /mnt/nvme/pilot/items/floor_table_v2.json \
        --out /mnt/nvme/pilot/items/items_v2.jsonl
    HF_HOME=/mnt/nvme/hf /mnt/nvme/vllm-venv/bin/python scripts/pilot_popqa.py \
        --out /mnt/nvme/pilot/items/popqa_fc_v2.jsonl

The floor table is computed (about 7 minutes, most of it the 400 algebra
universes) when the file does not exist, and read when it does, so the
smoke set and any rebuild use the same floors.

The full run, every model, both thinking modes where a model has them, all
four conditions and PopQA:

    cd /home/ec2-user/decoupled-reasoner && sudo -u ec2-user env HF_HOME=/mnt/nvme/hf \
      HF_HUB_OFFLINE=1 nohup /mnt/nvme/vllm-venv/bin/python scripts/pilot_run.py \
        --items /mnt/nvme/pilot/items/items_v2.jsonl \
        --popqa /mnt/nvme/pilot/items/popqa_fc_v2.jsonl \
        --out /mnt/nvme/pilot/records \
        --s3 s3://decoupled-reasoner-009398924577/runs/pilot-acq/records \
        --models all > /mnt/nvme/pilot/run.log 2>&1 &

Rerunning the same command resumes: keys already on disk are skipped. A
resume after a code change mixes commits within a configuration, which the
report refuses unless told `--allow-mixed-commits`. Then

    uv run python scripts/pilot_report.py --items /mnt/nvme/pilot/items/items_v2.jsonl \
        --popqa /mnt/nvme/pilot/items/popqa_fc_v2.jsonl \
        --records /mnt/nvme/pilot/records --out /mnt/nvme/pilot/report

which refuses while any `RUNNING*.lock` exists in the records directory. The
parent holds `RUNNING.lock` for the whole loop and each child holds
`RUNNING.<model>.lock`; a parent killed outright leaves its lock behind, to
be removed by hand once nothing is running. The report prints "not reached"
until all 12 configurations and all 8 PopQA files are complete.

## Things that bit during setup

FlashInfer's top-k/top-p sampler compiles itself on first use and needs nvcc,
which the box does not have; `vllm_model.py` sets
`VLLM_USE_FLASHINFER_SAMPLER=0` before vLLM is imported.

A vLLM engine core is its own process and outlives a parent that is killed,
keeping its GPU memory. The runner shuts each engine down, leaves the child
with `os._exit` (vLLM's teardown at interpreter exit aborted with "terminate
called without an active exception" after the records were written), and
the parent stops any engine process of its user that is still alive. That
also stops any other vLLM job run as ec2-user on this box.

The guard's `not_corpus_mode` broke ties in set iteration order, so the item
set changed with `PYTHONHASHSEED`. Fixed in 1b0a6d7; a test builds the smoke
set under three hash seeds, and the full set was rebuilt under hash seed 7
byte for byte.

## Smoke run, 2026-10-06

24 items from seeds 5,000,000 above the real ones (one refuniverse item per
level, two algebra items per level, two per rule family),
`/mnt/nvme/pilot/smoke/items_smoke_v2.jsonl`, sha256
`ce33ea70321732ba22a0102ae614c4f779f6fe9596afc35413b9bb25dd8b845b`, four
conditions each, plus the first 200 PopQA items of `popqa_fc_v2.jsonl`.
Records under `/mnt/nvme/pilot/smoke_v2/records`, mirrored to
`s3://decoupled-reasoner-009398924577/runs/pilot-acq/smoke_v2/`, all written at
commit f747ea9. These counts prove the path; at n = 24 per condition they say
nothing about the models.

| configuration | closed_book | oracle | sibling | blank | hedges (of 96) | names a candidate (of 96) | PopQA (of 200): mean NLL / subject masked / summed NLL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LFM2.5-350M-Base | 0/24 | 2/24 | 2/24 | 0/24 | 6 | 49 | 62 / 46 / 73 |
| Qwen3-0.6B, thinking off | 0/24 | 6/24 | 2/24 | 0/24 | 6 | 70 | 60 / 47 / 64 |
| Qwen3-0.6B, thinking on | 0/24 | 10/24 | 1/24 | 0/24 | 3 | 69 | (same model) |

Thinking on used 98,106 thinking tokens over 96 prompts and hit the 4,096
cap on 12 of them. Every child exited 0 and no mirror failed. The report
regraded all 288 generation records from their text with no disagreement,
passed rule 1 on the 96 cells present, and returned "not reached", as it
must with ten of twelve configurations and every full PopQA file absent.
The records carry `git_dirty` true because of an unrelated local edit to
`src/frames/sweep_drive.sh` on the box; the dirty check now looks only at
the paths the pilot runs.

## Throughput, and what the full run costs

`--probe 384` timed generation on the same 384 prompts drawn at random from
`items_v2.jsonl` (all families and conditions) for every configuration,
grading and recording nothing, at commit f747ea9 on 2026-10-06. Rows are in
`/mnt/nvme/pilot/probe_v2/throughput_probe.jsonl`, mirrored to
`s3://decoupled-reasoner-009398924577/runs/pilot-acq/probe_v2/`. Hours are the
probe's seconds per prompt times the 5,760 prompts of the full set.

| configuration | seconds for 384 | generated tokens | think cap hit | hours for 5,760 |
| --- | ---: | ---: | ---: | ---: |
| LFM2.5-350M-Base | 2.0 | 9,216 | - | 0.008 |
| LFM2.5-350M | 1.7 | 908 | - | 0.007 |
| Qwen3-0.6B-Base | 3.9 | 6,885 | - | 0.016 |
| Qwen3-0.6B, thinking off | 5.0 | 7,382 | - | 0.021 |
| Qwen3-0.6B, thinking on | 206.9 | 544,917 | 54 | 0.862 |
| Qwen3-1.7B-Base | 6.2 | 5,272 | - | 0.026 |
| Qwen3-1.7B, thinking off | 9.4 | 17,180 | - | 0.039 |
| Qwen3-1.7B, thinking on | 451.9 | 935,904 | 113 | 1.883 |
| Qwen3-4B, thinking off | 19.7 | 6,404 | - | 0.082 |
| Qwen3-4B, thinking on | 578.9 | 811,032 | 67 | 2.412 |
| Qwen3-8B, thinking off | 33.2 | 3,766 | - | 0.138 |
| Qwen3-8B, thinking on | 821.3 | 820,132 | 77 | 3.422 |

Generation sums to 8.9 hours. Loading the eight models took about 5
minutes in all on the probe, and PopQA, now 8,000 option scorings per model
with the subject-masked twins, takes about 6 seconds per model (1.1 seconds
per 200 items on the smoke run). The full run is about 9 GPU-hours on the
one L40S, 96% of it in the four thinking-on configurations.

The thinking cap binds often: 29% of Qwen3-1.7B's thinking runs on the probe
prompts hit 4,096 tokens, 20% of Qwen3-8B's, 17% of Qwen3-4B's and 14% of
Qwen3-0.6B's. Every record carries `think_truncated`, and the report prints
the rate per cell.

## Likelihoods: vLLM against transformers

PopQA likelihoods from vLLM were checked against a plain transformers
forward pass on the first 200 items of `popqa_fc_v2.jsonl` (800 option
scorings per model), scored by the pilot's own rule
(`/mnt/nvme/pilot/dev/ll_check2.py`):

| model | pick agreement | accuracy, vLLM / transformers | per-option NLL difference, median / p95 / max |
| --- | ---: | ---: | ---: |
| LFM2.5-350M-Base | 0.99 | 0.310 / 0.305 | 0.066 / 0.28 / 1.36 |
| Qwen3-0.6B-Base | 0.98 | 0.350 / 0.350 | 0.072 / 0.25 / 0.44 |

An earlier check on 24 option scorings found two vLLM calls on the same pairs
agree exactly, so prefix caching does not disturb prompt logprobs. The
differences are bfloat16 noise: one or two picks in 100 flip, and the
accuracies differ by 0.005 and 0.
