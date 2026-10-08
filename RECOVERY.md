# What came off the volumes

Every experiment in this program ran on EC2. The instance stores those boxes
trained on were ephemeral and are gone, and that was known. What was not
accounted for is the root volumes: five of them outlived their instances, four
attached to stopped boxes and one detached and unattached after its instance was
terminated.

On 2026-10-08 all five were snapshotted, restored into one availability zone,
mounted read only and compared against this repository by content. Every file
under 20 MB with a source, document or result extension was hashed as a git blob
and checked against all 4,523 distinct blobs then reachable from `main`. What
follows is what had no copy here.

## The repository that was never pushed

The detached volume was the root disk of the p5.48xlarge that ran the
operator-graph audit. On it, `/home/ec2-user/opg` was a git repository with 26
commits from 2026-08-29, no remote, and 272 uncommitted entries in its working
tree.

It is now `opgraph-audit/` on `main`, and `history/opgraph-audit` holds it
unmodified. The 26 commits are the audit as it was committed. One further commit
holds what the box still had uncommitted: three modified files under
`src/latent` and `src/opgraph`, and the untracked results, logs, runs and lane
directories whose content appears nowhere else here. Untracked copies of the main
program's documents, rsync artifacts, caches and the 92 GB of checkpoints under
`runs/` were left out.

### The eight training-ceiling arms

`src/STATE.md` listed the training-ceiling arms as having no artifact at all,
which made H12 the hypothesis that killed H10 while resting on a table nobody
could find. The arms are in that repository, at
`opgraph-audit/results/ceiling/`: eight summaries, their per-item records, and
the generated tables.

`TABLES_full.md` is unambiguous on the point the result turns on. Mean emitted
plan length saturates at each arm's training maximum and does not pass it, and
the control for decoding hitting the token budget reads 0.000 in all 88 cells,
so a short plan is a short plan rather than a truncated one.

One internal disagreement is worth naming rather than smoothing over. Section 2
of that table reports the largest plan emitted by the depth-six arm as 6, while
the max-over-cell table in section 1 shows that arm reaching 9 at required depth
8 and 10 at required depth 32. The two cannot both be describing the same
quantity. Nothing in this repository resolves it, and no number here should be
quoted as that arm's maximum until something does.

## Material from the other four

`recovered-volumes/` holds what was on the stopped boxes and nowhere else,
grouped by box, at the paths it occupied.

- `dev/` is the development box: the loose verification and sweep scripts from
  its home directory, the fleet bootstrap packages under `stg/`, and the frames
  sweep's working directory. 672 files. Most of the volume is the per-item
  rollout dumps under `sweep/dumps/`, 370 files whose scored summaries are in
  `sweep/res/`. They are kept because this volume was the only copy; the
  equivalent material was excluded from `results/s3/` precisely because S3 still
  held it.
- `worker-3/` is the cellular-automaton study's job lists and per-arm logs, 123
  files. `latent-transfer/experiments/ca_depth/` already has that study's result
  JSON; these are the sweep definitions and the run logs beside them.
- `pilot/` is four files: how the full acquisition pilot run was launched, and
  its output.
- `latent-handoff/` is five files from the cross-model pipeline that are newer
  than their counterparts in `latent-transfer/`, including `src/engine.py` and
  the two training scripts.

## What this does not establish

The comparison covered source, document and result files under 20 MB. It did not
hash checkpoints, tokenized shards or anything larger, so a result sitting only
in a `.pt` file on one of those volumes would not have been noticed. The git
repositories on the development and pilot boxes were both exactly at the commits
already here, so nothing was lost from those.

The snapshots and the restored volumes created for this audit were deleted after
it. The five original volumes were left alone.
