# Does the policy ask at all

MMLU questions, the model driving its own retrieval through the live web tier. `issued a query` is the fraction of rollouts emitting at least one retrieve token; its denominator is `n`.

| checkpoint | n | issued a query | rollouts that asked | mean rounds | pages entered context | named a choice | live searches | file |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| corpus-v1-8k | 200 | 0.325 | 65 of 200 | 0.54 | 0.325 | 0.02 | 72 | `/mnt/nvme/realret/results/mmlu_agentic_corpus-v1-8k_n200.json` |
| real-v1-8k | 200 | 0.71 | 142 of 200 | 0.825 | 0.71 | 0.045 | 164 | `/mnt/nvme/realret/results/mmlu_agentic_real-v1-8k_n200.json` |

The same question on held-out real documents, where the pages come from the episode's own bundle rather than the web.

| checkpoint | source | decode | n | issued a query | mean rounds | file |
| --- | --- | --- | ---: | ---: | ---: | --- |
| corpus-v1-8k | hotpot_qa open | greedy | 568 | 0.9472 | 1.403 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa yesno | greedy | 32 | 0.9688 | 1.688 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa open | t1 | 1140 | 0.9211 | 1.422 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa yesno | t1 | 60 | 0.95 | 1.75 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions open | greedy | 599 | 0.2137 | 0.386 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions yesno | greedy | 1 | 0.0 | 0.0 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions open | t1 | 1200 | 0.3425 | 0.603 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | trivia_qa open | greedy | 600 | 0.9467 | 1.815 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | trivia_qa open | t1 | 1200 | 0.9225 | 1.742 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| real-v1-8k | hotpot_qa open | greedy | 568 | 1.0 | 2.114 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa yesno | greedy | 32 | 1.0 | 2.188 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa open | t1 | 1140 | 0.9965 | 2.134 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa yesno | t1 | 60 | 1.0 | 2.083 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions open | greedy | 599 | 1.0 | 1.217 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions yesno | greedy | 1 | 1.0 | 2.0 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions open | t1 | 1200 | 0.9983 | 1.308 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | trivia_qa open | greedy | 600 | 1.0 | 1.35 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | trivia_qa open | t1 | 1200 | 0.9983 | 1.381 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |

# The data

| pack | examples | tokens | mean tokens per example | rounds histogram | file |
| --- | ---: | ---: | ---: | --- | --- |
| hotpot_qa | 55982 | 17506306 | 312.7 | {"2": 47126, "3": 8856} | `/mnt/nvme/realret/pack/hotpot_qa.summary.json` |
| natural_questions | 36000 | 6304714 | 175.1 | {"1": 17401, "2": 18599} | `/mnt/nvme/realret/pack/natural_questions.summary.json` |
| trivia_qa | 35993 | 8379737 | 232.8 | {"1": 14489, "2": 21504} | `/mnt/nvme/realret/pack/trivia_qa.summary.json` |
| syn_relation | 64001 | 24957523 | 390.0 | {} | `/mnt/nvme/realret/pack/syn_relation.summary.json` |
| syn_plan_step | 24000 | 4596060 | 191.5 | {} | `/mnt/nvme/realret/pack/syn_plan_step.summary.json` |
| syn_plan_whole | 16000 | 4559358 | 285.0 | {} | `/mnt/nvme/realret/pack/syn_plan_whole.summary.json` |
| syn_external | 11489 | 1883437 | 163.9 | {} | `/mnt/nvme/realret/pack/syn_external.summary.json` |
| syn_mathgen | 11001 | 4334318 | 394.0 | {} | `/mnt/nvme/realret/pack/syn_mathgen.summary.json` |
| mix_real1 | 254466 | 72521453 | 285.0 | {"relation": 64001, "natural_questions": 36000, "mathgen": 11001, "hotpot_qa": 55982, "trivia_qa": 35993, "external": 11489, "plan_whole": 16000, "plan_step": 24000} | `/mnt/nvme/realret/pack/mix_real1.summary.json` |

## Episode build, per source and split

| source, split | items seen | episodes kept | dropped | rounds | queries compressed | file |
| --- | ---: | ---: | --- | --- | ---: | --- |
| hotpot_qa train | 90029 | 80906 | {"unplannable": 9086, "answer_off_page": 37} | {"2": 68207, "3": 12699} | 25788 | `/mnt/nvme/realret/eps/hotpot_qa.train.jsonl.summary.json` |
| hotpot_qa validation | 7377 | 6733 | {"unplannable": 639, "answer_off_page": 5} | {"2": 5604, "3": 1129} | 1726 | `/mnt/nvme/realret/eps/hotpot_qa.validation.jsonl.summary.json` |
| natural_questions train | 56896 | 48733 | {"unplannable": 8163} | {"1": 23566, "2": 25167} | 16 | `/mnt/nvme/realret/eps/natural_questions.train.jsonl.summary.json` |
| natural_questions validation | 6897 | 6160 | {"unplannable": 737} | {"1": 3341, "2": 2819} | 0 | `/mnt/nvme/realret/eps/natural_questions.validation.jsonl.summary.json` |
| trivia_qa train | 61429 | 52917 | {"unplannable": 8512} | {"1": 21204, "2": 31713} | 7882 | `/mnt/nvme/realret/eps/trivia_qa.train.jsonl.summary.json` |
| trivia_qa validation | 7752 | 6790 | {"unplannable": 962} | {"1": 2836, "2": 3954} | 1014 | `/mnt/nvme/realret/eps/trivia_qa.validation.jsonl.summary.json` |

## Datasets staged onto the worker

| check | value | file |
| --- | --- | --- |
| files staged | 10 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| md5 re-verified after write | 10 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| mismatches | 0 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `relation_train.jsonl` | 2122933800 bytes, md5 f42960473c9d3d714df7654b3968a2de, from s3 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `plan_train_step.jsonl` | 148854679 bytes, md5 01986bd7645ea153b79173c812da7b5d, from s3 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `plan_train_whole.jsonl` | 29968167 bytes, md5 25780dad52f510aaf80c1b137c70ecc2, from s3 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `external_train.jsonl` | 147078487 bytes, md5 07e99b91d7bb8dec90aa484f0d4cfd5a, from s3 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `mathgen_train.jsonl` | 500241836 bytes, md5 b22a42a578dfb235ce3b34d3566b980b, from s3 | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `test-00000-of-00001.parquet` | 3504718 bytes, md5 4d0d6cea81f4907c2095f05449c1a801, from hub:cais/mmlu | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `dev-00000-of-00001.parquet` | 76504 bytes, md5 db35e77a5c3aaaf0c77468cd31698ba1, from hub:cais/mmlu | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `test-00000-of-00001.parquet` | 203808 bytes, md5 ea499852c2d1ae80b576c94615f6065d, from hub:allenai/ai2_arc | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `validation-00000-of-00001.parquet` | 85928 bytes, md5 fdcccf784910afee873d968dc21b71e5, from hub:allenai/winogrande | `/mnt/nvme/realret/reports/stage_manifest.json` |
| `test-00000-of-00001.parquet` | 419088 bytes, md5 204963167ec69cd5d500ecd79f6950e3, from hub:openai/gsm8k | `/mnt/nvme/realret/reports/stage_manifest.json` |

## Episodes removed before packing

| file | in | kept | benchmark exact | benchmark near | train/eval duplicate | report |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `hotpot_qa.train.jsonl` | 80906 | 80906 | 0 | 0 | 0 | `/mnt/nvme/realret/reports/decontam.json` |
| `natural_questions.train.jsonl` | 48733 | 48730 | 3 | 0 | 0 | `/mnt/nvme/realret/reports/decontam.json` |
| `trivia_qa.train.jsonl` | 52917 | 52879 | 29 | 1 | 8 | `/mnt/nvme/realret/reports/decontam.json` |
| total | 182556 | 182515 | 32 | 1 | 8 | `/mnt/nvme/realret/reports/decontam.json` |

## Train and eval split, leakage by content hash

| pair | train episodes | eval episodes | shared question hashes | shared as fraction of eval | shared document keys | file |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| hotpot_qa.train.jsonl|hotpot_qa.eval.jsonl | 80906 | 600 | 0 | 0.0 | 1670 of 5918 | `/mnt/nvme/realret/reports/leakage.json` |
| natural_questions.train.jsonl|natural_questions.eval.jsonl | 48730 | 600 | 0 | 0.0 | 973 of 3592 | `/mnt/nvme/realret/reports/leakage.json` |
| trivia_qa.train.jsonl|trivia_qa.eval.jsonl | 52879 | 600 | 0 | 0.0 | 352 of 6827 | `/mnt/nvme/realret/reports/leakage.json` |

## Episode contracts, re-checked from the written files

| file | lines | checked | episodes with a failure | clean rate | reasons | source |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `hotpot_qa.train.jsonl` | 80906 | 4046 | 1 | 0.9998 | {"rendered": 1} | `/mnt/nvme/realret/reports/verify.json` |
| `natural_questions.train.jsonl` | 48730 | 4061 | 0 | 1.0 | {} | `/mnt/nvme/realret/reports/verify.json` |
| `trivia_qa.train.jsonl` | 52879 | 4068 | 2 | 0.9995 | {"rendered": 2} | `/mnt/nvme/realret/reports/verify.json` |
| `hotpot_qa.eval.jsonl` | 600 | 600 | 0 | 1.0 | {} | `/mnt/nvme/realret/reports/verify.json` |
| `natural_questions.eval.jsonl` | 600 | 600 | 0 | 1.0 | {} | `/mnt/nvme/realret/reports/verify.json` |
| `trivia_qa.eval.jsonl` | 600 | 600 | 0 | 1.0 | {} | `/mnt/nvme/realret/reports/verify.json` |

## Benchmark contamination

Both scans cover every document of every bundle, not only the ones a planned trace serves. `before` is the raw build; `after` is what is packed and trained on.

| check | before | after | files |
| --- | --- | --- | --- |
| benchmark_stems | {"mmlu": 12936, "arc": 1108, "winogrande": 1267, "gsm8k": 1319} | {"mmlu": 12936, "arc": 1108, "winogrande": 1267, "gsm8k": 1319} | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| benchmark_stems_total | 16630 | 16630 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| training_questions_scanned | 182556 | 182515 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| training_documents_scanned | 2027405 | 2026913 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| training_chars_scanned | 920490119 | 920287184 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| ngram | 5 | 5 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| min_stem_words | 8 | 8 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| near_threshold | 0.5 | 0.5 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| exact_matches | 37 | 0 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| exact_by_task | {"mmlu": 29, "arc": 8, "winogrande": 0, "gsm8k": 0} | {"mmlu": 0, "arc": 0, "winogrande": 0, "gsm8k": 0} | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| near_matches | 19 | 17 | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |
| near_by_task | {"mmlu": 19, "arc": 0, "winogrande": 0, "gsm8k": 0} | {"mmlu": 17, "arc": 0, "winogrande": 0, "gsm8k": 0} | `/mnt/nvme/realret/reports/contamination_before.json`, `/mnt/nvme/realret/reports/contamination.json` |

# The named surviving failure: synthetic two-hop chaining

`src/corpus/RETRAIN.md` records `chain_rule` at 0.220 against a 0.250 floor and `weighted_chain` at 0.039 against 0.000 as the cells the diversity corpus did not move. `weighted_chain` carries no candidates, so it has a generation cell only, which is how that document reports it too.

| cell | instrument | n | floor | acc | 95% Wilson | chance corrected | issued a query | mean rounds | file |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| gen_rule_corpus-v1-8k | generation, env grader | 384 | 0.0 | 0.4922 | 0.4425-0.542 |  | 1.0 | 1.021 | `/mnt/nvme/realret/results/chain_summary.json` |
| gen_rule_real-v1-8k | generation, env grader | 384 | 0.0 | 0.4609 | 0.4117-0.5109 |  | 1.0 | 1.021 | `/mnt/nvme/realret/results/chain_summary.json` |
| gen_weighted_corpus-v1-8k | generation, env grader | 1536 | 0.0 | 0.2051 | 0.1856-0.226 |  | 1.0 | 3.311 | `/mnt/nvme/realret/results/chain_summary.json` |
| gen_weighted_real-v1-8k | generation, env grader | 1536 | 0.0 | 0.1849 | 0.1663-0.2051 |  | 1.0 | 3.304 | `/mnt/nvme/realret/results/chain_summary.json` |
| mc_rule_corpus-v1-8k | forced choice | 1536 | 0.25 | 0.252 | 0.2309-0.2743 | 0.0026 |  |  | `/mnt/nvme/realret/results/chain_summary.json` |
| mc_rule_real-v1-8k | forced choice | 1536 | 0.25 | 0.2441 | 0.2233-0.2662 | -0.0078 |  |  | `/mnt/nvme/realret/results/chain_summary.json` |

# Held-out synthetic frames, after real-document training

| checkpoint | decode | family | cells | macro accuracy | macro chance | chance corrected | file |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| corpus-v1-8k | greedy | exception_rule | 12 | 0.8156 | 0.5 | 0.6312 | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_greedy.json` |
| corpus-v1-8k | greedy | substitution_rule | 12 | 0.8021 | 0.2 | 0.7526 | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_greedy.json` |
| corpus-v1-8k | greedy | threshold_rule | 12 | 0.9062 | 0.5 | 0.8125 | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_greedy.json` |
| corpus-v1-8k | greedy | dumps checked against their episode files | 36 | | | | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_greedy.json` |
| corpus-v1-8k | t1 | exception_rule | 12 | 0.7422 | 0.5 | 0.4844 | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_t1.json` |
| corpus-v1-8k | t1 | substitution_rule | 12 | 0.8005 | 0.2 | 0.7507 | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_t1.json` |
| corpus-v1-8k | t1 | threshold_rule | 12 | 0.8807 | 0.5 | 0.7615 | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_t1.json` |
| corpus-v1-8k | t1 | dumps checked against their episode files | 36 | | | | `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_t1.json` |
| real-v1-8k | greedy | exception_rule | 12 | 0.824 | 0.5 | 0.6479 | `/mnt/nvme/realret/results/frames_score_real-v1-8k_greedy.json` |
| real-v1-8k | greedy | substitution_rule | 12 | 0.7865 | 0.2 | 0.7331 | `/mnt/nvme/realret/results/frames_score_real-v1-8k_greedy.json` |
| real-v1-8k | greedy | threshold_rule | 12 | 0.9083 | 0.5 | 0.8167 | `/mnt/nvme/realret/results/frames_score_real-v1-8k_greedy.json` |
| real-v1-8k | greedy | dumps checked against their episode files | 36 | | | | `/mnt/nvme/realret/results/frames_score_real-v1-8k_greedy.json` |
| real-v1-8k | t1 | exception_rule | 12 | 0.75 | 0.5 | 0.5 | `/mnt/nvme/realret/results/frames_score_real-v1-8k_t1.json` |
| real-v1-8k | t1 | substitution_rule | 12 | 0.774 | 0.2 | 0.7174 | `/mnt/nvme/realret/results/frames_score_real-v1-8k_t1.json` |
| real-v1-8k | t1 | threshold_rule | 12 | 0.8745 | 0.5 | 0.749 | `/mnt/nvme/realret/results/frames_score_real-v1-8k_t1.json` |
| real-v1-8k | t1 | dumps checked against their episode files | 36 | | | | `/mnt/nvme/realret/results/frames_score_real-v1-8k_t1.json` |

# Record files

| file | exists | bytes | modified (UTC) | age at report, minutes |
| --- | --- | ---: | --- | ---: |
| `/mnt/nvme/realret/results/mmlu_agentic_corpus-v1-8k_n200.json` | True | 69909 | 2026-09-02T02:22:06Z | 329.6 |
| `/mnt/nvme/realret/results/mmlu_agentic_real-v1-8k_n200.json` | True | 77223 | 2026-09-02T05:09:27Z | 162.2 |
| `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` | True | 6299 | 2026-09-02T02:53:49Z | 297.8 |
| `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` | True | 5973 | 2026-09-02T05:34:57Z | 136.7 |
| `/mnt/nvme/realret/pack/hotpot_qa.summary.json` | True | 311 | 2026-09-02T02:16:49Z | 334.8 |
| `/mnt/nvme/realret/pack/natural_questions.summary.json` | True | 318 | 2026-09-02T02:17:01Z | 334.6 |
| `/mnt/nvme/realret/pack/trivia_qa.summary.json` | True | 310 | 2026-09-02T02:17:17Z | 334.4 |
| `/mnt/nvme/realret/pack/syn_relation.summary.json` | True | 277 | 2026-09-02T02:18:17Z | 333.4 |
| `/mnt/nvme/realret/pack/syn_plan_step.summary.json` | True | 272 | 2026-09-02T02:18:23Z | 333.3 |
| `/mnt/nvme/realret/pack/syn_plan_whole.summary.json` | True | 273 | 2026-09-02T02:18:28Z | 333.2 |
| `/mnt/nvme/realret/pack/syn_external.summary.json` | True | 271 | 2026-09-02T02:18:35Z | 333.1 |
| `/mnt/nvme/realret/pack/syn_mathgen.summary.json` | True | 270 | 2026-09-02T02:19:44Z | 331.9 |
| `/mnt/nvme/realret/pack/mix_real1.summary.json` | True | 601 | 2026-09-02T02:19:56Z | 331.7 |
| `/mnt/nvme/realret/eps/hotpot_qa.train.jsonl.summary.json` | True | 428 | 2026-09-02T02:00:33Z | 351.1 |
| `/mnt/nvme/realret/eps/hotpot_qa.validation.jsonl.summary.json` | True | 428 | 2026-09-02T02:00:47Z | 350.9 |
| `/mnt/nvme/realret/eps/natural_questions.train.jsonl.summary.json` | True | 424 | 2026-09-02T02:02:37Z | 349.0 |
| `/mnt/nvme/realret/eps/natural_questions.validation.jsonl.summary.json` | True | 424 | 2026-09-02T02:02:48Z | 348.9 |
| `/mnt/nvme/realret/eps/trivia_qa.train.jsonl.summary.json` | True | 402 | 2026-09-02T02:05:32Z | 346.1 |
| `/mnt/nvme/realret/eps/trivia_qa.validation.jsonl.summary.json` | True | 404 | 2026-09-02T02:05:50Z | 345.8 |
| `/mnt/nvme/realret/reports/stage_manifest.json` | True | 1967 | 2026-09-02T01:55:45Z | 355.9 |
| `/mnt/nvme/realret/reports/decontam.json` | True | 11599 | 2026-09-02T02:13:52Z | 337.8 |
| `/mnt/nvme/realret/reports/leakage.json` | True | 1284 | 2026-09-02T02:16:14Z | 335.4 |
| `/mnt/nvme/realret/reports/verify.json` | True | 2056 | 2026-09-02T02:16:04Z | 335.6 |
| `/mnt/nvme/realret/reports/contamination_before.json` | True | 16357 | 2026-09-02T02:11:58Z | 339.7 |
| `/mnt/nvme/realret/reports/contamination.json` | True | 7157 | 2026-09-02T02:15:46Z | 335.9 |
| `/mnt/nvme/realret/results/chain_summary.json` | True | 1204 | 2026-09-02T07:47:55Z | 3.7 |
| `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_greedy.json` | True | 24879 | 2026-09-02T03:08:04Z | 283.6 |
| `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_t1.json` | True | 25540 | 2026-09-02T03:20:31Z | 271.1 |
| `/mnt/nvme/realret/results/frames_score_real-v1-8k_greedy.json` | True | 24923 | 2026-09-02T05:45:06Z | 126.6 |
| `/mnt/nvme/realret/results/frames_score_real-v1-8k_t1.json` | True | 25674 | 2026-09-02T05:57:28Z | 114.2 |
| `/mnt/nvme/realret/results/harness_ours_n200_cuda.json` | False |  |  | None |
| `/mnt/nvme/realret/results/harness_lfm2_n200_cuda_bos.json` | False |  |  | None |
| `/mnt/nvme/realret/results/mmlu_closed_corpus-v1-8k_n500.json` | True | 132455 | 2026-09-02T02:54:13Z | 297.4 |
| `/mnt/nvme/realret/results/mmlu_closed_corpus-v1-8k_n500_eot.json` | True | 132443 | 2026-09-02T02:54:37Z | 297.0 |
| `/mnt/nvme/realret/results/mmlu_closed_real-v1-8k_n500.json` | True | 131975 | 2026-09-02T05:35:20Z | 136.3 |
| `/mnt/nvme/realret/results/mmlu_closed_real-v1-8k_n500_eot.json` | True | 131948 | 2026-09-02T05:35:45Z | 135.9 |
| `/mnt/nvme/realret/results/mmlu_closed_lfm2-350m_n500_bos.json` | True | 132830 | 2026-09-02T02:55:02Z | 296.6 |
| `/mnt/nvme/realret/results/mmlu_closed_lfm2-350m_n500_nobos.json` | True | 132749 | 2026-09-02T02:55:22Z | 296.3 |
| `/mnt/nvme/realret/results/mmlu_web_lfm2-350m_n500.json` | True | 412684 | 2026-09-02T07:16:11Z | 35.5 |
| `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` | True | 600136 | 2026-09-02T03:01:26Z | 290.2 |
| `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` | True | 599871 | 2026-09-02T05:38:40Z | 133.0 |
| `/mnt/nvme/realret/results/mmlu_agentic_corpus-v1-8k_n200.json` | True | 69909 | 2026-09-02T02:22:06Z | 329.6 |
| `/mnt/nvme/realret/results/mmlu_agentic_real-v1-8k_n200.json` | True | 77223 | 2026-09-02T05:09:27Z | 162.2 |
| `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` | True | 6299 | 2026-09-02T02:53:49Z | 297.8 |
| `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` | True | 5973 | 2026-09-02T05:34:57Z | 136.7 |
| `/mnt/nvme/realret/results/chain_summary.json` | True | 1204 | 2026-09-02T07:47:55Z | 3.7 |
| `/mnt/nvme/realret/results/frames_score_corpus-v1-8k_greedy.json` | True | 24879 | 2026-09-02T03:08:04Z | 283.6 |
| `/mnt/nvme/realret/results/frames_score_real-v1-8k_greedy.json` | True | 24923 | 2026-09-02T05:45:06Z | 126.6 |
| `/mnt/nvme/realret/reports/verify.json` | True | 2056 | 2026-09-02T02:16:04Z | 335.6 |
| `/mnt/nvme/realret/reports/stage_manifest.json` | True | 1967 | 2026-09-02T01:55:45Z | 355.9 |
| `/mnt/nvme/realret/reports/decontam.json` | True | 11599 | 2026-09-02T02:13:52Z | 337.8 |
| `/mnt/nvme/realret/reports/contamination_before.json` | True | 16357 | 2026-09-02T02:11:58Z | 339.7 |
| `/mnt/nvme/realret/reports/leakage.json` | True | 1284 | 2026-09-02T02:16:14Z | 335.4 |
| `/mnt/nvme/realret/reports/contamination.json` | True | 7157 | 2026-09-02T02:15:46Z | 335.9 |
| `/mnt/nvme/realret/pack/mix_real1.summary.json` | True | 601 | 2026-09-02T02:19:56Z | 331.7 |
| `/mnt/nvme/realret/pack/hotpot_qa.summary.json` | True | 311 | 2026-09-02T02:16:49Z | 334.8 |
| `/mnt/nvme/realret/pack/natural_questions.summary.json` | True | 318 | 2026-09-02T02:17:01Z | 334.6 |
| `/mnt/nvme/realret/pack/trivia_qa.summary.json` | True | 310 | 2026-09-02T02:17:17Z | 334.4 |
| `/mnt/nvme/realret/pack/syn_relation.summary.json` | True | 277 | 2026-09-02T02:18:17Z | 333.4 |

# MMLU, closed book, five shot completion

| model | n | floor | acc | 95% Wilson | acc - floor | file |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| ours corpus-v1-8k | 500 | 0.25 | 0.264 | 0.2273-0.3043 | 0.014 | `/mnt/nvme/realret/results/mmlu_closed_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k, eot prefix | 500 | 0.25 | 0.262 | 0.2254-0.3023 | 0.012 | `/mnt/nvme/realret/results/mmlu_closed_corpus-v1-8k_n500_eot.json` |
| ours real-v1-8k | 500 | 0.25 | 0.282 | 0.2443-0.323 | 0.032 | `/mnt/nvme/realret/results/mmlu_closed_real-v1-8k_n500.json` |
| ours real-v1-8k, eot prefix | 500 | 0.25 | 0.288 | 0.25-0.3292 | 0.038 | `/mnt/nvme/realret/results/mmlu_closed_real-v1-8k_n500_eot.json` |
| LFM2-350M, bos | 500 | 0.25 | 0.436 | 0.3932-0.4798 | 0.186 | `/mnt/nvme/realret/results/mmlu_closed_lfm2-350m_n500_bos.json` |
| LFM2-350M, no bos | 500 | 0.25 | 0.314 | 0.2749-0.356 | 0.064 | `/mnt/nvme/realret/results/mmlu_closed_lfm2-350m_n500_nobos.json` |
| harness check: ours corpus-v1-8k n=200 cuda | file missing | | | | | `/mnt/nvme/realret/results/harness_ours_n200_cuda.json` |
| harness check: LFM2-350M n=200 cuda bos | file missing | | | | | `/mnt/nvme/realret/results/harness_lfm2_n200_cuda_bos.json` |

# MMLU with live web pages

Same items, same queries, same cached pages on every row.

| model | condition | contamination | n | floor | acc | file |
| --- | --- | --- | ---: | ---: | ---: | --- |
| LFM2-350M | pages in context | all | 500 | 0.25 | 0.478 | `/mnt/nvme/realret/results/mmlu_web_lfm2-350m_n500.json` |
| LFM2-350M | pages in context | verbatim | 24 | 0.25 | 0.375 | `/mnt/nvme/realret/results/mmlu_web_lfm2-350m_n500.json` |
| LFM2-350M | pages in context | answer | 57 | 0.25 | 0.6316 | `/mnt/nvme/realret/results/mmlu_web_lfm2-350m_n500.json` |
| LFM2-350M | pages in context | neither | 419 | 0.25 | 0.463 | `/mnt/nvme/realret/results/mmlu_web_lfm2-350m_n500.json` |
| ours corpus-v1-8k | context overflow | prompts cropped 4 of 500, mean 2193.7 tokens, max 4840, window 4096 | | | | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | closed_book | all | 500 | 0.25 | 0.264 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | closed_book | verbatim | 24 | 0.25 | 0.125 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | closed_book | answer | 57 | 0.25 | 0.3684 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | closed_book | neither | 419 | 0.25 | 0.2578 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched | all | 500 | 0.25 | 0.26 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched | verbatim | 24 | 0.25 | 0.2917 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched | answer | 57 | 0.25 | 0.2982 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched | neither | 419 | 0.25 | 0.253 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched_uncropped | all | 496 | 0.25 | 0.2601 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched_uncropped | verbatim | 24 | 0.25 | 0.2917 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched_uncropped | answer | 57 | 0.25 | 0.2982 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | matched_uncropped | neither | 415 | 0.25 | 0.253 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | native | all | 500 | 0.25 | 0.234 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | native | verbatim | 24 | 0.25 | 0.3333 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | native | answer | 57 | 0.25 | 0.3158 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours corpus-v1-8k | native | neither | 419 | 0.25 | 0.2172 | `/mnt/nvme/realret/results/mmlu_web_corpus-v1-8k_n500.json` |
| ours real-v1-8k | context overflow | prompts cropped 4 of 500, mean 2193.7 tokens, max 4840, window 4096 | | | | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | closed_book | all | 500 | 0.25 | 0.282 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | closed_book | verbatim | 24 | 0.25 | 0.2083 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | closed_book | answer | 57 | 0.25 | 0.2982 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | closed_book | neither | 419 | 0.25 | 0.284 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched | all | 500 | 0.25 | 0.27 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched | verbatim | 24 | 0.25 | 0.25 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched | answer | 57 | 0.25 | 0.2807 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched | neither | 419 | 0.25 | 0.2697 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched_uncropped | all | 496 | 0.25 | 0.2702 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched_uncropped | verbatim | 24 | 0.25 | 0.25 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched_uncropped | answer | 57 | 0.25 | 0.2807 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | matched_uncropped | neither | 415 | 0.25 | 0.2699 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | native | all | 500 | 0.25 | 0.262 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | native | verbatim | 24 | 0.25 | 0.25 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | native | answer | 57 | 0.25 | 0.3158 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |
| ours real-v1-8k | native | neither | 419 | 0.25 | 0.2554 | `/mnt/nvme/realret/results/mmlu_web_real-v1-8k_n500.json` |

# MMLU, the model driving its own retrieval

| model | n | floor | acc | issued a query | mean rounds | pages entered context | named a choice | file |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ours corpus-v1-8k | 200 | 0.25 | 0.01 | 0.325 | 0.54 | 0.325 | 0.02 | `/mnt/nvme/realret/results/mmlu_agentic_corpus-v1-8k_n200.json` |
| ours real-v1-8k | 200 | 0.25 | 0.005 | 0.71 | 0.825 | 0.71 | 0.045 | `/mnt/nvme/realret/results/mmlu_agentic_real-v1-8k_n200.json` |

# Held-out real documents, through the retrieval loop

| checkpoint | source | decode | n | floor | ship | strict | f1 | rounds | gold page served | ship given gold served | file |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| corpus-v1-8k | hotpot_qa open | greedy | 568 | 0.0 | 0.0035 | 0.0035 | 0.0073 | 1.403 | 0.4208 | 0.0084 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa yesno | greedy | 32 | 0.5 | 0.0 | 0.0 | 0.0 | 1.688 | 0.0 | None | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa open | t1 | 1140 | 0.0 | 0.0018 | 0.0018 | 0.0036 | 1.422 | 0.3746 | 0.0047 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa yesno | t1 | 60 | 0.5 | 0.0 | 0.0 | 0.0 | 1.75 | 0.0167 | 0.0 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions open | greedy | 599 | 0.0 | 0.0033 | 0.0033 | 0.0004 | 0.386 | 0.1452 | 0.0 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions yesno | greedy | 1 | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | None | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions open | t1 | 1200 | 0.0 | 0.0 | 0.0 | 0.002 | 0.603 | 0.1825 | 0.0 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | trivia_qa open | greedy | 600 | 0.0 | 0.02 | 0.0183 | 0.022 | 1.815 | 0.7 | 0.0286 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | trivia_qa open | t1 | 1200 | 0.0 | 0.0083 | 0.0083 | 0.0093 | 1.742 | 0.64 | 0.013 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| real-v1-8k | hotpot_qa open | greedy | 568 | 0.0 | 0.2782 | 0.25 | 0.3512 | 2.114 | 0.6866 | 0.4051 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa yesno | greedy | 32 | 0.5 | 0.5625 | 0.5625 | 0.5625 | 2.188 | 0.0312 | 0.0 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa open | t1 | 1140 | 0.0 | 0.1579 | 0.1377 | 0.2258 | 2.134 | 0.6439 | 0.2452 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa yesno | t1 | 60 | 0.5 | 0.5667 | 0.5667 | 0.5667 | 2.083 | 0.0667 | 0.75 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions open | greedy | 599 | 0.0 | 0.2788 | 0.2354 | 0.3541 | 1.217 | 0.6177 | 0.4514 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions yesno | greedy | 1 | 0.5 | 0.0 | 0.0 | 0.0 | 2.0 | 1.0 | 0.0 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions open | t1 | 1200 | 0.0 | 0.1358 | 0.1133 | 0.1967 | 1.308 | 0.5942 | 0.2286 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | trivia_qa open | greedy | 600 | 0.0 | 0.4167 | 0.3983 | 0.4651 | 1.35 | 0.7367 | 0.5611 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | trivia_qa open | t1 | 1200 | 0.0 | 0.2517 | 0.24 | 0.2871 | 1.381 | 0.71 | 0.3521 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |

# Failure decomposition on the held-out real documents

| checkpoint | source | decode | wrong | no query | bad pages | truncated | did not read | file |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| corpus-v1-8k | hotpot_qa open | greedy | 566 | 30 | 299 | 1 | 236 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa yesno | greedy | 32 | 1 | 31 | 0 | 0 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa open | t1 | 1138 | 90 | 623 | 0 | 425 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | hotpot_qa yesno | t1 | 60 | 3 | 56 | 0 | 1 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions open | greedy | 597 | 469 | 41 | 1 | 86 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions yesno | greedy | 1 | 1 | 0 | 0 | 0 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | natural_questions open | t1 | 1200 | 789 | 192 | 2 | 217 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | trivia_qa open | greedy | 588 | 32 | 148 | 8 | 400 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| corpus-v1-8k | trivia_qa open | t1 | 1190 | 93 | 339 | 0 | 758 | `/mnt/nvme/realret/results/real_scores_corpus-v1-8k.json` |
| real-v1-8k | hotpot_qa open | greedy | 410 | 0 | 178 | 0 | 232 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa yesno | greedy | 14 | 0 | 13 | 0 | 1 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa open | t1 | 960 | 4 | 402 | 0 | 554 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | hotpot_qa yesno | t1 | 26 | 0 | 25 | 0 | 1 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions open | greedy | 432 | 0 | 229 | 0 | 203 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions yesno | greedy | 1 | 0 | 0 | 0 | 1 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | natural_questions open | t1 | 1037 | 2 | 485 | 0 | 550 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | trivia_qa open | greedy | 350 | 0 | 156 | 0 | 194 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
| real-v1-8k | trivia_qa open | t1 | 898 | 2 | 344 | 0 | 552 | `/mnt/nvme/realret/results/real_scores_real-v1-8k.json` |
