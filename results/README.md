# Results pulled out of S3

These two directories hold results that were produced after the last commit of
the original repository, so they existed nowhere in git until this repository was
assembled.

## stage-b

The E3 350M pretrain and the Stage A / Stage B comparison. Stage A is the
pretrain alone; Stage B applies the identical supervised fine-tuning pack to the
E3 checkpoint and to the earlier corpus-v1-8k checkpoint, so the pair differs
only in the pretrain beneath it. Files named `*_e3sft*` are the E3 arm and
`*_ref*` are the reference arm.

`loss.jsonl` and `eval/sft_e3_loss.jsonl` are the training curves. `eval/mmlu_*`
and `eval/ret_*` are the checkpoint sweeps. The 1.5 GB checkpoints themselves
stay in S3; see `../MANIFEST-s3.md`.

## pilot-acq

The acquisition pilot: eight models (LFM2.5-350M and its base, Qwen3 at 0.6B,
1.7B, 4B and 8B, with and without thinking) over a generated item set and PopQA.
`report/report.md` is the readable output. `records/` holds the per-item records
the report is computed from.

`box-final/` is the mirror written when the run completed. Its `records/` and
`report/` were byte-identical to the copies at the root of `pilot-acq/` and were
dropped rather than stored twice; everything unique to it is kept, including the
download logs, the data manifests, the throughput probe and the dev-box
inspection scripts.

`validity-review/` and `staging-scripts/` are the review and run scripts from the
staging area, kept because the review is part of the record.
