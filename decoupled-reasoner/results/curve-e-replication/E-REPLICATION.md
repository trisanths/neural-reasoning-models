Three-seed regime E result: the reading gate fails on all three seeds (ratios 0.818, 0.799, 0.877 against the 0.90 criterion, prose naturalized contains 0.1680, 0.1640, 0.1800 against the regime A mean 0.2053) and the fact gate passes on all three (probes 0.2828, 0.2459, 0.2869 under the 0.3332 threshold). The E-501 verdict replicates: the extreme version does not work at 350m.

# Regime E replication, seeds 502 and 503

Generated 2026-08-27T22:12:48Z on the block-3 H100 box. Models curve-350me-502 and curve-350me-503 (350m params, regime E: 0.70 scrubbed natural text, 0.15 extractive QA traces, 0.10 worldgen retrieval traces, 0.05 procgen; train seeds 502/503), final checkpoints step 26700. Graded with scripts/eval_battery.py at full sizes under both elicitations via dir naming, killtest-a-<seed> for prose naturalized, probes, and documents-in-context heldout, killtest-c-<seed> for episode-trace naturalized, interactive heldout, and the noise axis. 250 naturalized items per variant (clean, contradiction 0.15, OCR 0.05), 244 probes, 500 held-out episodes, noise rates 0/0.1/0.25/0.5 on 200 episodes. Seed 501 numbers come from the block-2 grading in runs/curve/evals-e501/results-e501-700m.json; the battery, sizes, and step match.

## Pooled three-seed table

| seed | nat contains prose | ratio vs A mean | reading gate | probes acc | fact gate | docs heldout | interactive heldout | mean rounds | noise slope |
|---|---|---|---|---|---|---|---|---|---|
| 501 | 0.1680 | 0.818 | FAIL | 0.2828 | PASS | 0.6746 | 0.8250 | 0.9235 | -0.2591 |
| 502 | 0.1640 | 0.799 | FAIL | 0.2459 | PASS | 0.6608 | 0.7615 | 0.8902 | -0.2525 |
| 503 | 0.1800 | 0.877 | FAIL | 0.2869 | PASS | 0.6370 | 0.8332 | 1.0246 | -0.2867 |
| mean | 0.1707 | 0.831 | FAIL (0/3) | 0.2719 | PASS (3/3) | 0.6575 | 0.8066 | 0.9461 | -0.2661 |

Reference: killtest regime A seed-mean naturalized contains 0.2053 (seeds 101/102/103: 0.2280, 0.1960, 0.1920); probes leakage threshold 0.3332, chance 0.25.

## Reading gate

- Seed 501: prose 0.1680 clean, 0.1640 contradiction, 0.1000 OCR; episode trace 0.0160 clean. Better elicitation prose at 0.1680, ratio 0.818, FAIL.
- Seed 502: prose 0.1640 clean, 0.1600 contradiction, 0.0520 OCR; episode trace 0.0040 clean. Better elicitation prose at 0.1640, ratio 0.799, FAIL.
- Seed 503: prose 0.1800 clean, 0.1760 contradiction, 0.0560 OCR; episode trace 0.0240 clean. Better elicitation prose at 0.1800, ratio 0.877, FAIL.

Per-seed prose ratios sit at 0.818, 0.799, 0.877; the three-seed mean prose contains 0.1707 is 0.831x the regime A reference. The gate needs 0.90 or better on the better elicitation.

## Fact gate

- Seed 501: probes 0.2828 over 244 items, leakage flag false, PASS.
- Seed 502: probes 0.2459 over 244 items, leakage flag false, PASS.
- Seed 503: probes 0.2869 over 244 items, leakage flag false, PASS.

## Replication statement

The E-501 result replicates across seeds 502 and 503: the reading gate fails on every seed (ratios 0.818, 0.799, 0.877 against the 0.90 criterion) and the fact gate passes on every seed (probes 0.2828, 0.2459, 0.2869 under the 0.3332 threshold). The extreme version does not work at 350m by the pre-registered two-gate criterion, on any of the three seeds.

## Held-out worlds and noise

Documents-in-context heldout per seed 0.6746, 0.6608, 0.6370, mean 0.6575 (killtest A mean 0.6619). Interactive heldout per seed 0.8250, 0.7615, 0.8332, mean 0.8066 at mean rounds 0.9235, 0.8902, 1.0246 (killtest C mean 0.6957 at 0.8077 rounds). Noise slopes -0.2591, -0.2525, -0.2867, mean -0.2661 (killtest C mean -0.2911), clean accuracy 0.5751, 0.5816, 0.5827.

Seed 502 noise accuracy by corruption rate: 0.5816 at 0, 0.5546 at 0.1, 0.5481 at 0.25, 0.4508 at 0.5. Degradation 0.1308.

Seed 503 noise accuracy by corruption rate: 0.5827 at 0, 0.5589 at 0.1, 0.5373 at 0.25, 0.4378 at 0.5. Degradation 0.1449.

## Verbatim answer samples, prose elicitation

First 4 raw decoded answers per new seed on the clean naturalized variant under prose elicitation, next to the gold answers. Model output is quoted verbatim as a JSON string (escapes are literal). The full first 8 per entry are in results-e-replication.json.

Seed 502:

1. filing-001 (filing), question: Which lot of turnbuckles was subject to the voluntary recall?
   gold: "lot 2214"
   model: "The company reported a total of 3,960 units shipped, with a total of 1,000 units sold. The company reported a total of 1,000"
   contains false, em false
2. filing-002 (filing), question: What maximum daily discharge rate does the applicant seek?
   gold: "120,000 gallons per day"
   model: "The applicant seeks a discharge rate of 120,000 gallons per day, an increase from the 85,000 gallons per day authorized under the expiring permit. The"
   contains true, em false
3. filing-003 (filing), question: What percentage of dispensers tested at the 24 month mark were outside tolerance?
   gold: "6.1 percent"
   model: "The percentage of dispensers tested at the 24 month mark was 99.1 percent."
   contains false, em false
4. filing-004 (filing), question: What caused the seven hour unscheduled stoppage on November 9?
   gold: "a faulty brake sensor"
   model: "The accident occurred on a stretch of track between the two stations, which was not designed to handle the traffic. The accident occurred at a time when the traffic was"
   contains false, em false

Seed 503:

1. filing-001 (filing), question: Which lot of turnbuckles was subject to the voluntary recall?
   gold: "lot 2214"
   model: "The turnbuckles were subject to the voluntary recall."
   contains false, em false
2. filing-002 (filing), question: What maximum daily discharge rate does the applicant seek?
   gold: "120,000 gallons per day"
   model: "The maximum daily discharge rate is the maximum discharge rate that the applicant would receive if the discharge were to be discharged at a rate of 120,000 gallons per day"
   contains true, em false
3. filing-003 (filing), question: What percentage of dispensers tested at the 24 month mark were outside tolerance?
   gold: "6.1 percent"
   model: "The rule will require testing of each retail dispenser once every 12 months, replacing the current 24 month cycle. The average error at failing dispensers at failing"
   contains false, em false
4. filing-004 (filing), question: What caused the seven hour unscheduled stoppage on November 9?
   gold: "a faulty brake sensor"
   model: "The cause of the accident was a faulty brake sensor, which was installed on the counterweight carriage and was the subject of corrective action. The brake sensor was replaced"
   contains true, em false

## 1300m pair

curve-1300m-a and curve-1300m-c finished at step 26700 during this grading and were graded on the freed GPUs with the same battery: 1300m A naturalized contains 0.2800 with probes 0.5000 (flag true) and docs-in-context heldout 0.7161; 1300m C naturalized contains 0.0000 with probes 0.2213 (flag false), interactive heldout 0.7269 at 0.9386 mean rounds, noise slope -0.3039. The full curve through 1300m is in CURVE-TABLE.md alongside this file.

## Anomalies

1300m-a scores its contradiction variant 0.3000 above clean 0.2800; the within-noise inversion seen at 150m, in killtest-a-103, and at 700m (where the two were equal) appears again, now with contradiction exceeding clean. Its probes accuracy 0.5000 sits at the 700m level (0.5123) rather than above it, so A-regime leakage looks to plateau near 0.51 while naturalized contains keeps rising, 0.2280 to 0.2800.

1300m-c breaks the noise-slope flattening pattern: -0.3039 against -0.2697 at 700m and -0.2911 at 350m, with clean accuracy 0.5859 still near the 0.58 level of the smaller sizes. Its interactive heldout 0.7269 also lands below the 700m 0.7442. Its probes accuracy 0.2213 is about one sigma below chance 0.25, the same direction as every C model graded.

On the E side, the trace-elicitation naturalized contains varies noticeably by seed: 0.0040 (502), 0.0160 (501), 0.0240 (503), so the residual prose-format ability of the E mix under the wrong elicitation is seed dependent where pure C models sit at exactly zero. Seed 503's interactive mean rounds 1.0246 is the first graded lane above one served round per question, and its interactive heldout 0.8332 is the best of any lane graded so far, ahead of E-501's 0.8250; seed 502's 0.7615 still beats the killtest C mean 0.6957. The contains-metric paraphrase undercount noted in the E-501 grading applies unchanged here; the same metric graded the regime A reference, so the gate ratios compare like with like.

## Timings

The four replication entries ran in parallel on the free H100s of the block-3 box, launched 2026-08-27T19:31:51Z: killtest-c-502 on GPU 2, killtest-c-503 on GPU 3, and killtest-a-502 then killtest-a-503 sequentially on GPU 7. The a-side jobs finished at 19:42:01Z and 19:52:35Z, the c-side at 19:54:52Z and 19:55:42Z, a 23.9 minute wall for the replication battery. The 1300m lanes on GPUs 0 and 1 wrote their final checkpoints at 20:18Z (a) and 21:39Z (c) and printed done at step 26700; killtest-a-111 was graded on the freed GPU 2 from 20:20:55Z to 20:40:38Z, killtest-c-211 on GPU 3 from 21:41:52Z to 22:10:07Z, and the six-entry combine ran at 22:11:34Z. End to end the grading spanned 19:31:51Z to 22:11:34Z, gated by the 1300m-c lane finish. The live E2 lanes on GPUs 4, 5, and 6 were untouched throughout.

Per-entry battery totals: killtest-a-502 608s, killtest-c-502 1379s, killtest-a-503 633s, killtest-c-503 1429s, killtest-a-111 1182s, killtest-c-211 1693s.

## Provenance

Checkpoints /home/ec2-user/runs/curve-350me-502/ckpt-0026700.pt, curve-350me-503/ckpt-0026700.pt, curve-1300m-a/ckpt-0026700.pt, and curve-1300m-c/ckpt-0026700.pt on the block-3 box. Battery scripts/eval_battery.py, tokenizer_v2, heldout ~/data/regime_c/heldout.jsonl (first 500 episodes). Reference numbers from runs/killtest/evals/results.json; seed 501 numbers from runs/curve/evals-e501/results-e501-700m.json. Full per-item output in results-e-replication.json alongside this file.

