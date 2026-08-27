# 350M regime D models: eval battery and gate comparison

Generated 2026-08-27T02:28:16Z on the block-2 H100 box, GPU 7. Checkpoints curve-350md-401/402/403 at step 26700, graded with scripts/eval_battery.py under both dir-name elicitations: killtest-a-40x for prose naturalized, probes, and documents-in-context heldout, killtest-c-40x for episode-trace naturalized, interactive heldout, and the noise axis. Full sizes: 250 naturalized items with contradiction 0.15 and OCR 0.05 variants, 244 probes, 500 held-out episodes, noise rates 0/0.1/0.25/0.5 on 200 episodes. D models trained with retrieval tokens, so interactive mode is valid for them.

| model | seed | elicitation | nat contains clean | contradiction | ocr | probes acc | leakage flag | heldout acc | heldout mode | mean rounds | noise slope |
|---|---|---|---|---|---|---|---|---|---|---|---|
| curve-350md-401 | 401 | prose | 0.2000 | 0.2080 | 0.0880 | 0.3893 | true | 0.6305 | docs-in-context | n/a | n/a |
| curve-350md-401 | 401 | episode trace | 0.0280 | 0.0280 | 0.0320 | n/a | n/a | 0.7878 | interactive | 0.9309 | -0.2840 |
| curve-350md-402 | 402 | prose | 0.2200 | 0.2240 | 0.0720 | 0.4180 | true | 0.6184 | docs-in-context | n/a | n/a |
| curve-350md-402 | 402 | episode trace | 0.0280 | 0.0280 | 0.0080 | n/a | n/a | 0.7576 | interactive | 0.9028 | -0.3154 |
| curve-350md-403 | 403 | prose | 0.1520 | 0.1520 | 0.0640 | 0.3852 | true | 0.6366 | docs-in-context | n/a | n/a |
| curve-350md-403 | 403 | episode trace | 0.0120 | 0.0160 | 0.0160 | n/a | n/a | 0.7398 | interactive | 0.8596 | -0.2977 |
| killtest-350m-a (mean of 3) | 101/102/103 | prose | 0.2053 | 0.2027 | 0.0920 | 0.4822 | see killtest | 0.6619 | docs-in-context | n/a | n/a |
| killtest-350m-c (mean of 3) | 201/202/203 | episode trace | 0.0000 | 0.0000 | 0.0013 | 0.2514 | see killtest | 0.6957 | interactive | 0.8077 | -0.2911 |

## Gate comparison

The gate number is the killtest regime A seed-mean naturalized contains, 0.2053 (seeds 101/102/103: 0.2280, 0.1960, 0.1920).

D naturalized contains under prose elicitation: 401 at 0.2000, 402 at 0.2200, 403 at 0.1520; mean 0.1907. Under episode-trace elicitation: 401 at 0.0280, 402 at 0.0280, 403 at 0.0120; mean 0.0227. The better elicitation by the numbers is prose at 0.1907, which is 0.929x the regime A gate mean. Per-seed spread under the better elicitation: min 0.1520, max 0.2200, range 0.0680, stdev 0.0349.

Probes sit at 401 at 0.3893, 402 at 0.4180, 403 at 0.3852 (mean 0.3975) against the 0.3332 leakage threshold; all three cross it.

Held-out worlds, interactive mode: 401 at 0.7878 with 0.9309 mean rounds, 402 at 0.7576 with 0.9028 mean rounds, 403 at 0.7398 with 0.8596 mean rounds; mean accuracy 0.7617, mean rounds 0.8978. Documents-in-context mode: 401 at 0.6305, 402 at 0.6184, 403 at 0.6366; mean 0.6285. Killtest references: A 0.6619 docs-in-context, C 0.6957 interactive.

Noise axis slopes: 401 at -0.2840, 402 at -0.3154, 403 at -0.2977; mean -0.2990 against the killtest C mean -0.2911.

## Timings

Battery wall clock on GPU 7 of the block-2 box: phase A (three a-40x entries) 00:39:59 to 01:11:26 UTC, phase C (three c-40x entries) 01:11:26 to 02:26:46 UTC, combine finished 02:26 UTC on 2026-08-27; 1h47m end to end.

Per-entry battery totals in seconds: killtest-a-401 634, killtest-c-401 1587, killtest-a-402 629, killtest-c-402 1527, killtest-a-403 622, killtest-c-403 1404.

