# The experiment registry

One row per run, in an append-only file, with a frontier command that finds
the runs worth arguing about.

The problem it solves: this project has produced dozens of runs across
pretraining regimes, RL lanes and one-off benchmarks, and their numbers live
in a dozen artefact shapes scattered over an S3 bucket. Comparing two of them
meant reading two JSON files by hand and remembering which knob differed.

```
registry/runs.jsonl   the record of truth, append only, one JSON object per line
registry/index.db     a derived sqlite cache, safe to delete and rebuild
src/registry/         schema, store, ingesters, FLOPs, theory, frontier
scripts/exp.py        the command line
```

## Adding a row

Every row needs three things nothing on disk knows: which **lane** it belonged
to (`exploit` pushes a lever already known to work, `explore` opens a
direction with no prior, `falsify` tries to kill something we believe),
what the run's **objective** actually optimised, and one sentence of
**belief changed**. That last field is required. Writing `none` is a normal
and honest answer; leaving it blank is not, because a run whose effect on the
project's beliefs was never written down is a run nobody can read later.

### From an artefact

Check what an ingester sees before writing anything:

```bash
uv run python -m scripts.exp ingest rl ~/runs/rlsimple-503-921
uv run python -m scripts.exp ingest ablation ~/ablate/rlskill-.../ablation.json
uv run python -m scripts.exp ingest battery results/killtest-2026-08-26/results.json
uv run python -m scripts.exp ingest config ~/runs/curve-350me-503/config.yaml
```

`rl` reads `rl.jsonl` and `eval.jsonl` from a run directory. `battery` reads
`results.json` from `scripts/eval_battery.py`. `ablation` reads either
`rule_test.json` or `ablation.json`. `config` turns a training config into
parameter counts and training FLOPs. `nrm` and `webdemo` read the two web
benchmarks.

Then either extend `src/registry/backfill.py` (for a run family that will
recur) or append the row directly:

```bash
uv run python -m scripts.exp add \
  --run-id rlsimple-503-922 --lane exploit --family rlsimple --branch E \
  --objective "GRPO against a programmatic verifier, retrieval in the rollout" \
  --arch "24L x 1024d dense decoder" \
  --arch-field params_total=375440384 --arch-field params_non_embedding=308331520 \
  --metric reasoning=0.994 --metric novel_system_acquisition=0.994 \
  --compute latency_s_per_answer=0.104 \
  --source ~/runs/rlsimple-503-922/eval.jsonl \
  --belief-changed "none; replication of 921 at a second seed"
```

`add` stamps the current git commit automatically. Anything you cannot
measure, leave out: the field stays null, and the frontier will skip the row
on that axis rather than pretend it scored zero.

### Rebuilding everything

```bash
aws s3 sync s3://decoupled-reasoner-009398924577/runs/ ~/registry-mirror/runs/ \
  --exclude "*.pt" --exclude "*.tmp"
uv run python -m scripts.exp backfill --mirror ~/registry-mirror --repo .
```

The store is append-only, so a second backfill writes revision 1 of every row
rather than overwriting revision 0. `exp list` and the frontier read the
highest revision; the old lines stay on disk so a frontier printed last month
can still be reproduced.

A revision replaces the whole row, it does not patch it. Correcting one metric
with `exp add` means passing every field again, or the fields you left out come
back as null. To start over, delete `registry/` and re-run the backfill.

## Reading the table

```bash
uv run python -m scripts.exp list                  # everything
uv run python -m scripts.exp list --lane falsify   # only the kill attempts
uv run python -m scripts.exp list --family rlskill
uv run python -m scripts.exp show rule-test-rlsimple-503-921
```

`show` prints the whole row and then every theory claim's verdict on it.

## Reading the frontier

```bash
uv run python -m scripts.exp objectives            # what can go on an axis
uv run python -m scripts.exp pareto retrieval_dependency inference_flops
uv run python -m scripts.exp pareto novel_system params
uv run python -m scripts.exp pareto reasoning train_flops --verbose
```

A row is on the frontier when nothing else in the table is at least as good
on every chosen objective and better on one. More than two objectives work;
the printed table just gets wider.

Three things to read carefully.

**The skipped count.** The header says how many rows had all the objectives
and how many were set aside. A frontier over five rows out of forty is a
frontier over what we happened to measure, not over what we ran. `--verbose`
names the missing fields.

**The star.** A starred row is on the frontier *and* contradicts a claim in
`src/registry/theory.py`. Those are the rows to promote: cheap, undominated
evidence against something the programme is currently spending money on. The
output prints the claim, and what the row says instead.

**The direction.** `closed_book_probe` is minimised, not maximised: knowledge
belongs in the retrieval fabric, so a low probe score is the goal and a high
one means the weights are hoarding facts.

**The suite warning.** `reasoning` means "task accuracy with the evidence the
run is entitled to", and the task is not the same across families: a
pretraining run is graded on held-out worlds, an RL run on its own episode
pool. Each row records which evaluation produced its `reasoning`, and the
frontier prints a warning when it has put more than one on the same axis.
Restrict with `--suite` to compare like with like:

```bash
uv run python -m scripts.exp pareto reasoning train_flops \
  --suite skillacq_invented_systems
```

A pooled accuracy can also hide the thing the experiment was about. RL rows
carry `detail.per_domain`, the accuracy split by task family across the
sampled eval episodes. `rlarith-calc-931` pools to 0.156, which reads as
partial success until the split shows `skill_binary_op` and `skill_units`
both at 0.000 and the whole score sitting in `skill_procedure`, whose easy
items answer with a number copied out of the question. Claim T3 checks that
split before it decides whether a row contradicts it.

## The metrics

| field | means |
|---|---|
| `reading` | naturalized reading, contains-answer, clean variant. The pre-registered gate. |
| `reasoning` | task accuracy with the evidence the run is entitled to |
| `retrieval_dependency` | acc(correct evidence) minus acc(**wrong** evidence). The strict test: the wrong page is as long, as well formed and as retrievable, so only reading tells them apart. |
| `evidence_lift` | acc(correct evidence) minus acc(**no** evidence). The weak test: a model can score here just by noticing it has documents. |
| `closed_book_probe` | four-way knowledge probe with nothing retrieved. Chance is 0.25, the battery flags leakage above 0.3332. Lower is better. |
| `novel_system_acquisition` | accuracy on a system invented after the training data, given its page |
| `ood_generalization` | accuracy on a distribution the run never trained on |

`reasoning_suite` names the evaluation behind `reasoning`. Two rows are only
comparable on that axis when it matches.

`retrieval_dependency` and `evidence_lift` are derived from the three raw
accuracies whenever those are present, and the schema refuses a row where
they disagree with their parts.

## The cost numbers

`src/registry/flops.py` holds the formulas and the assumptions behind them.

- **training FLOPs** is `6 * P * T` over non-embedding parameters, with
  tokens read off the schedule as `max_steps x batch x grad_accum x
  max_seq_len`. For the curve runs that comes to 7.0e9 tokens, matching
  CURVE.md.
- **inference FLOPs per answer** is `2 * P * (context + generated)` and needs
  a *measured* context length, which only the NRM bench records. Everywhere
  else it is null.
- **decode FLOPs per answer** is `2 * P * generated`, available from any
  `eval.jsonl`, and a strict lower bound on the number above. Use it when the
  full figure is too sparse to draw a frontier.
- **an RL run's training FLOPs** is the update pass plus the rollout decode,
  `6 * P * update_tokens + 2 * P * generated_tokens`. The rollout prompt
  prefill is not logged anywhere, so this is a lower bound and the row says so
  in `detail.train_flops_is_lower_bound`. It is still the right order of
  magnitude for the comparison that matters: the RL lanes cost 1e14 to 1e16
  against 1e19 for a pretraining run.
- **latency** and **GPU utilization** are never derived. Latency comes from an
  eval's own wall clock over its own rollout count, so it is a batched
  per-answer latency, not single-stream. Nothing in the current artefacts
  records GPU utilization, so that column is null everywhere until a run
  starts logging it.

The parameter count is exact for the project's llama-style block and is
checked against the independent count `scripts/bench_evidence.py` printed on
the L40S: 375,440,384 total and 308,331,520 non-embedding for the 350M shape.
A weight-tied looped core does not change the parameter count but does change
the compute, so `effective_layer_passes` multiplies the FLOPs and leaves the
parameters alone.

## The theory file

`src/registry/theory.py` states what the project currently believes, as
predicates, each with the observation that would falsify it. Editing it is
expected. When a run overturns a claim, change the claim there and say so in
that run's `belief_changed`.

```bash
uv run python -m scripts.exp theory
```

## Provenance

Numbers come out of artefacts through `src/registry/ingest.py` and are never
typed by hand. Labels, lanes and belief sentences are editorial and live in
`src/registry/backfill.py`, each traceable to a line in PLAN.md, CURVE.md,
ARCH.md, or the run's own command. Two rows in the backfill are exceptions
and say so in their `notes`: `skill-ablation-arithmetic`, whose raw
`ablation.json` never landed in the bucket, and the RL rows whose base
checkpoint the launch scripts did not record.
