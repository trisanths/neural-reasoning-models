# Results recovered from S3

Two things live here. `STAGE-B.md` is a result the repository could not contain
when it was last committed. `s3/` is the part of the project's S3 bucket that
belongs in git.

## STAGE-B.md

The pretrain comparison the program was waiting on. It finished about ninety
minutes after the last commit of the original repository, and the driver that
was supposed to record it had already died, so every lane report under
`decoupled-reasoner/` still describes it as outstanding. The artifacts survived
in S3 and that document reads them.

## s3/

A filtered mirror of `s3://decoupled-reasoner-009398924577` with the key layout
preserved. A path here is the S3 key with `results/s3/` in front of it, so
every file can be traced to the object it came from, and `../MANIFEST-s3.md`
accounts for everything the filter dropped.

The directories worth knowing about:

- `s3/runs/e3-350m/eval/` is the E3 pretrain and the Stage A and Stage B
  evaluations. Arms named `e3final` are the pretrain alone, `e3sft` is the
  pretrain plus fine-tuning, and `ref` is the earlier corpus-v1-8k checkpoint
  carrying the identical fine-tuning pack. `loss.jsonl` is the pretrain curve.
- `s3/runs/pilot-acq/` is the acquisition pilot: eight models, LFM2.5-350M and
  its base plus Qwen3 at 0.6B, 1.7B, 4B and 8B, over a generated item set and
  PopQA, with and without thinking. `report/report.md` is the readable output
  and `records/` holds the per-item records it is computed from. `box-final/` is
  the mirror written when the run completed; its `records/` and `report/` were
  byte-identical to the copies at the root and were dropped rather than stored
  twice, so what remains under it is the download logs, data manifests,
  throughput probe and dev-box inspection scripts. `validity-review/` under
  `pilot-staging/` holds the review scripts that found the registered decision
  rule could not pass, which is why amendment 1 exists.
- `s3/results/mathgen-h8/` is the answer-source experiment, with the own,
  sibling and blank episode arms.
- `s3/results/role/lfm2/` is the LFM2 role-binding comparison.
- `s3/frames-sweep/` is the frame sweep behind the renderer-swap result, which
  is the measurement that reduced rule acquisition to frame-conditioned value
  binding.
- `s3/latent/live/` is the latent handoff sweep, with the direct, opgraph and
  trace arms at two seeds.
- `s3/role-back/` and `s3/role-xfer/` are the role-arm swap and split records.
- `s3/ladder_cd/` is the typed and opcode ladder report.
- `s3/xfer/realret2/` is the real-retrieval MMLU comparison.
- `s3/logs/` is the fleet bootstrap and autolaunch record, kept because the
  CPU-contention outage and the silent driver death are both visible in it.

Nothing here was regenerated or reformatted. Several files are logs with
progress output in them, and several runs were superseded by later ones; the
documents under `decoupled-reasoner/` and `src/STATE.md` say which.
