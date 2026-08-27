E-501 two-gate result: reading gate FAIL at ratio 0.818 (naturalized contains 0.1680 under prose elicitation against the regime A mean 0.2053, criterion 0.90), fact gate PASS at probes 0.2828 against the leakage threshold 0.3332 (chance 0.25); the extreme version does not work at seed 501.

# E-501 verdict

Generated 2026-08-27T07:21:04Z on the block-2 H100 box. Model curve-350me-501 (350m params, regime E: 0.70 scrubbed natural text, 0.15 extractive QA traces, 0.10 worldgen retrieval traces, 0.05 procgen; train seed 501), final checkpoint step 26700. Graded with scripts/eval_battery.py at full sizes under both elicitations via dir naming: killtest-a-501 for prose naturalized, probes, and documents-in-context heldout on one GPU, killtest-c-501 for episode-trace naturalized, interactive heldout, and the noise axis on another. 250 naturalized items per variant (clean, contradiction 0.15, OCR 0.05), 244 probes, 500 held-out episodes, noise rates 0/0.1/0.25/0.5 on 200 episodes.

## Reading gate

The pre-registered reference is the killtest regime A seed-mean naturalized contains, 0.2053 (seeds 101/102/103: 0.2280, 0.1960, 0.1920). E-501 naturalized contains: prose 0.1680 clean, 0.1640 contradiction, 0.1000 OCR; episode trace 0.0160 clean, 0.0160 contradiction, 0.0200 OCR. The better elicitation is prose at 0.1680 clean, which is 0.818x the reference. The gate needs 0.90 or better, so this is a FAIL. Regime A per-variant references for comparison: contradiction 0.2027, OCR 0.0920. Exact match clean: prose 0.0000, trace 0.0120.

## Fact gate

Probes accuracy 0.2828 over 244 items against chance 0.25. The leakage threshold is 0.3332; the battery leakage flag reads false. Accuracy sits below the threshold, so the fact gate is a PASS.

## Verdict

The reading gate fails, so the extreme version does not work at seed 501 by the pre-registered criterion.
Seed replication is pending: curve-350me-502 and curve-350me-503 are still training on the live lanes and reach step 26700 roughly five hours after their boundary resume. This verdict is single seed until they are graded.

## Verbatim answer samples, better elicitation

First 8 raw decoded answers on the clean naturalized variant under prose elicitation, next to the gold answers. Model output is quoted verbatim as a JSON string (escapes are literal).

1. filing-001 (filing), question: Which lot of turnbuckles was subject to the voluntary recall?
   gold: "lot 2214"
   model: "The company has not yet filed a voluntary recall."
   contains false, em false
2. filing-002 (filing), question: What maximum daily discharge rate does the applicant seek?
   gold: "120,000 gallons per day"
   model: "The applicant seeks a maximum daily discharge rate of 120,000 gallons per day. The maximum daily discharge rate is the maximum rate that the applicant can discharge treated water"
   contains true, em false
3. filing-003 (filing), question: What percentage of dispensers tested at the 24 month mark were outside tolerance?
   gold: "6.1 percent"
   model: "The percentage of dispensers tested at the 24 month mark was 99.2 percent. The percentage of dispensers tested at the 24 month mark was 99"
   contains false, em false
4. filing-004 (filing), question: What caused the seven hour unscheduled stoppage on November 9?
   gold: "a faulty brake sensor"
   model: "The accident occurred on the night of May 9, when a passenger was killed when a passenger was struck by a car on the right side of the passenger car."
   contains false, em false
5. filing-005 (filing), question: How many parking spaces does the gravel lot contain?
   gold: "eleven"
   model: "The gravel lot contains a total of 999 parking spaces, including a parking space for the dairy processing kitchen, a parking space for the creamery, a parking"
   contains false, em false
6. filing-006 (filing), question: What was found to be the cause of the pressure drop on line 4?
   gold: "a leaking gasket"
   model: "The gasket was found to be leaking at a location where bolt tension measurements taken after the event were found to be below specification on three of eight studs."
   contains false, em false
7. filing-007 (filing), question: What interest rate do the offered notes bear?
   gold: "4.5 percent"
   model: "The Fomdru notes are offered at a discount of 1.8 percent. The Fomdru notes are offered at a discount of 1.8"
   contains false, em false
8. filing-008 (filing), question: What vehicle fare does the commission's staff analysis recommend?
   gold: "21 dollars"
   model: "The commission's staff analysis suggests that the company's fleet of four passenger ferries, the Vruvrax, the Vruvrax-Vruv"
   contains false, em false

## Held-out worlds and noise

Documents-in-context heldout 0.6746 (killtest A mean 0.6619). Interactive heldout 0.8250 at 0.9235 mean rounds (killtest C mean 0.6957 at 0.8077 rounds). Noise slope -0.2591 with clean accuracy 0.5751 (killtest C mean slope -0.2911).

Noise accuracy by corruption rate: 0.5751 at 0, 0.5524 at 0.1, 0.5297 at 0.25, 0.4443 at 0.5. Degradation 0.1308.

## Anomalies

Sample 6 shows the contains metric undercounting a grounded paraphrase: the model answers "The gasket was found to be leaking" against gold "a leaking gasket" and scores false. The measured 0.1680 is therefore a floor on grounded reading, though the same metric graded the regime A reference, so the gate ratio compares like with like. E-501 beats the regime A OCR mean (0.1000 against 0.0920) while losing on clean and contradiction. Its probes accuracy 0.2828 sits about 1.2 sigma above chance, a mild residue of the scrubbed natural text share, similar in kind to the 150m B model at 0.3033 and well under the flag. Its interactive heldout 0.8250 is the best interactive score of any lane graded so far (killtest C mean 0.6957, 150m C 0.7502, 700m C 0.7442), and its trace-elicitation naturalized numbers are nonzero (0.0160 contains, 0.0120 em) where pure C models sit at zero, both consistent with a model that saw both prose and trace formats. Mean served rounds 0.9235 per interactive question, so some answers still come without a completed retrieval round.

## Timings

All four battery entries ran in parallel on the free H100s, GPUs 0 (killtest-a-501), 1 (killtest-c-501), 4 (killtest-a-111), and 7 (killtest-c-211), launched 2026-08-27T06:53:43Z. The a-side jobs finished at 07:04:12Z and 07:07:11Z, the c-side jobs at 07:17:05Z and 07:18:13Z, so the battery wall time was 24.5 minutes. A probes-only pass for killtest-c-211 ran on GPU 0 after the a-501 job freed it (17.2s of scoring) and was merged into the c-211 entry before the final combine at 07:20:23Z. The live training lanes on GPUs 2, 3, 5, 6 were untouched throughout.

Per-entry battery totals: killtest-a-501 627s, killtest-c-501 1468s, killtest-a-111 806s, killtest-c-211 1417s.

## Provenance

Checkpoint /home/ec2-user/runs/curve-350me-501/ckpt-0026700.pt, synced to s3://decoupled-reasoner-009398924577/runs/curve/curve-350me-501/. Battery scripts/eval_battery.py, tokenizer_v2, heldout ~/data/regime_c/heldout.jsonl (first 500 episodes). Reference numbers from runs/killtest/evals/results.json. Full per-item output in results-e501-700m.json alongside this file.

