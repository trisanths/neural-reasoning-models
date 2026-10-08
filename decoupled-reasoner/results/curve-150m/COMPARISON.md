# 150M curve models: eval battery comparison

Generated 2026-08-26 on the dev box (L40S) from the full battery at repo
commit 5878731a. Each model is the final step 26700 checkpoint of its lane.
Full sizes throughout: 250 naturalized items (contains-answer; clean,
contradiction 0.15, and OCR 0.05 variants), 244 knowledge probes, 500
held-out episodes, noise axis over 200 episodes for the C model only.
Killtest 350M rows are the exact per-variant numbers from
runs/killtest/evals/results.json, averaged over their three seeds.

## Table

| model | seed | elicitation | nat contains clean | contradiction | ocr | probes acc | leakage flag | heldout acc | heldout mode | noise slope |
|---|---|---|---|---|---|---|---|---|---|---|
| curve-150m-a | 111 | prose | 0.1080 | 0.1120 | 0.0440 | 0.4795 | true | 0.6634 | docs-in-context | n/a |
| curve-150m-b | 311 | prose | 0.1040 | 0.1000 | 0.0280 | 0.3033 | false | 0.8574 | docs-in-context | n/a |
| curve-150m-b | 311 | episode trace | 0.0440 | 0.0400 | 0.0360 | (same model) | (same) | (same) | (same) | n/a |
| curve-150m-c | 211 | episode trace | 0.0000 | 0.0000 | 0.0000 | 0.2459 | false | 0.7502 | interactive (0.87 mean rounds) | -0.3250 |
| killtest-350m-a (mean of 3) | 101/102/103 | prose | 0.2053 | 0.2027 | 0.0920 | 0.4822 | true (3/3) | 0.6619 | docs-in-context | n/a |
| killtest-350m-c (mean of 3) | 201/202/203 | episode trace | 0.0000 | 0.0000 | 0.0013 | 0.2514 | false (3/3) | 0.6957 | interactive (0.81 mean rounds) | -0.2911 |

Exact match on the clean variant is 0.0000 everywhere except curve-150m-b
under the episode trace, which reaches 0.0120.

## Reference detail: killtest 350M per seed

| run | nat clean | contradiction | ocr | probes | heldout | noise slope |
|---|---|---|---|---|---|---|
| killtest-a-101 | 0.2280 | 0.2160 | 0.1120 | 0.4836 | 0.6659 | n/a |
| killtest-a-102 | 0.1960 | 0.1880 | 0.0840 | 0.4754 | 0.6517 | n/a |
| killtest-a-103 | 0.1920 | 0.2040 | 0.0800 | 0.4877 | 0.6681 | n/a |
| killtest-c-201 | 0.0000 | 0.0000 | 0.0040 | 0.2377 | 0.7208 | -0.2713 |
| killtest-c-202 | 0.0000 | 0.0000 | 0.0000 | 0.2500 | 0.6646 | -0.2879 |
| killtest-c-203 | 0.0000 | 0.0000 | 0.0000 | 0.2664 | 0.7018 | -0.3141 |

## Elicitation decisions

- Regime B trained on natural text plus in-context worldgen QA episodes
  without retrieval tokens, so it saw both plain prose and the q/a
  special-token format. Naturalized ran both ways. Prose is the better
  elicitation for reading real text (0.1040 vs 0.0440 contains), and only
  the episode trace produces any exact matches (0.0120): the q/a format
  yields short clipped answers.
- Held-out worlds for B ran in documents-in-context mode. The interactive
  emit-query-read loop needs retrieval tokens B never saw, so that mode
  would measure format mismatch, not competence.
- Probes and heldout for B ran once, under the prose pass. Probes always
  use the training q/a format and take the model directly, so they do not
  depend on the naturalized elicitation.
- The battery parses regime from killtest-{a,c}-{seed} run names, so the
  checkpoint dirs are named to steer its elicitation: killtest-a-111 is
  curve-150m-a, killtest-c-211 is curve-150m-c, and curve-150m-b appears
  twice, as killtest-a-311 (prose, probes, heldout) and killtest-c-311
  (episode-trace naturalized only). results150.json keeps those names.

## Noise axis, curve-150m-c

Accuracy per corruption rate over 200 episodes (925 questions): 0.6141 at
0.0, 0.5892 at 0.1, 0.5697 at 0.25, 0.4497 at 0.5. Slope -0.3250,
degradation 0.1643. The 350M mean slope is -0.2911 with clean accuracy
0.5982.

## Notes and anomalies

- The A-vs-C picture replicates at 150M: A reads naturalized text at
  0.1080 contains while C is at zero across all three variants, so the
  kill-test outcome does not depend on the 350M scale.
- Scale halves A's naturalized score (0.1080 at 150M vs 0.2053 mean at
  350M) but barely moves heldout (0.6634 vs 0.6619).
- curve-150m-b's heldout 0.8574 is the best number in the table, above
  both C interactive scores. Held-out worlds with documents in context
  match its training distribution (in-context worldgen QA), so this reads
  as format familiarity plus reading skill, not retrieval.
- curve-150m-c's heldout 0.7502 beats the 350M C mean 0.6957, and its
  noise slope is somewhat steeper (-0.3250 vs -0.2911). Mean served
  rounds 0.87 per question, so as in the killtest, many answers come
  without a completed retrieval round and the noise numbers partly
  reflect closed-book behavior.
- Probes: A flags leakage as expected (0.4795 with real-text training).
  B sits at 0.3033, below the 3-sigma flag threshold of 0.3332 (1.9 sigma
  above chance); mild real-world knowledge from its natural-text share,
  benign for B. C is at chance (0.2459), clear.
- A's contradiction variant scores above its clean variant (0.1120 vs
  0.1080), within noise at n=250; killtest-a-103 showed the same
  inversion.

## Timings

Battery wall time 24.1 min on the L40S (16:36:41Z to 17:00:45Z), all
sequential on one GPU. Per checkpoint (total_s): a-111 288.2s, c-211
716.4s (heldout 331.3s, noise 337.9s), a-311 286.4s, c-311
naturalized-only 149.4s. Checkpoint download from S3 took under a minute
per 1.6 GB file.

## Provenance

- curve-150m-a: s3://decoupled-reasoner-009398924577/runs/curve/curve-150m-a/ckpt-0026700.pt, train seed 111
- curve-150m-b: .../curve-150m-b/ckpt-0026700.pt, train seed 311
- curve-150m-c: .../curve-150m-c/ckpt-0026700.pt, train seed 211
- battery: scripts/eval_battery.py at commit 5878731a, tokenizer_v2, heldout ~/data/regime_c/heldout.jsonl (5000 episodes, first 500 used)
