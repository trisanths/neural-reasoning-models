# Public benchmarks, closed book

Built 2026-09-03 01:58 UTC by `src/extern/bench_report.py` from every record file under `results/extern/bench`. Every cell states its own n and chance floor. Nothing is pooled across benchmarks. `published` is Liquid's figure for the model named in that row and is blank where that model's card publishes no such figure.

The `bos` column is the one to read before quoting any LFM2-350M number, and a dash in it means the run did not record the flag rather than that the token was absent. The bos token is worth 7.5 points at n=200 on this benchmark, and the row marked calibrated is the only one that reproduces the 43.43 the model card publishes. The other two MMLU rows for that model are measurements of a prompt format, not of the model, and neither may stand in for it in a comparison.

| model                | task       | format     | shots | bos | n   | floor  | acc    | acc % | published | delta | other       | parameters  | note       | record file                           | written              |
| -------------------- | ---------- | ---------- | ----- | --- | --- | ------ | ------ | ----- | --------- | ----- | ----------- | ----------- | ---------- | ------------------------------------- | -------------------- |
| LiquidAI/LFM2.5-350M | arc        | completion | 0     | no  | 200 | 0.2500 | 0.2100 | 21.00 | -         | -     | norm 0.2100 | 354,483,968 |            | lfm25_350m_arc_completion.json        | 2026-09-01 00:48 UTC |
| LiquidAI/LFM2.5-350M | mmlu       | completion | 5     | no  | 200 | 0.2500 | 0.3700 | 37.00 | -         | -     | norm 0.3700 | 354,483,968 |            | lfm25_350m_mmlu_completion.json       | 2026-09-01 00:41 UTC |
| LiquidAI/LFM2.5-350M | winogrande | completion | 0     | no  | 200 | 0.5000 | 0.5200 | 52.00 | -         | -     | norm 0.5200 | 354,483,968 |            | lfm25_350m_winogrande_completion.json | 2026-09-01 00:54 UTC |
| LiquidAI/LFM2-350M   | arc        | completion | 0     | no  | 200 | 0.2500 | 0.2750 | 27.50 | -         | -     | norm 0.2750 | 354,483,968 |            | lfm2_350m_arc_completion.json         | 2026-09-01 00:45 UTC |
| LiquidAI/LFM2-350M   | mmlu       | chat       | 0     | -   | 200 | 0.2500 | 0.3950 | 39.50 | 43.43     | -3.93 | norm 0.3950 | 354,483,968 |            | lfm2_350m_mmlu_chat.json              | 2026-09-01 00:13 UTC |
| LiquidAI/LFM2-350M   | mmlu       | completion | 5     | -   | 200 | 0.2500 | 0.3550 | 35.50 | 43.43     | -7.93 | norm 0.3550 | 354,483,968 |            | lfm2_350m_mmlu_completion.json        | 2026-09-01 00:08 UTC |
| LiquidAI/LFM2-350M   | mmlu       | completion | 5     | yes | 200 | 0.2500 | 0.4300 | 43.00 | 43.43     | -0.43 | norm 0.4300 | 354,483,968 | calibrated | lfm2_350m_mmlu_completion_bos.json    | 2026-09-01 00:37 UTC |
| LiquidAI/LFM2-350M   | winogrande | completion | 0     | no  | 200 | 0.5000 | 0.4800 | 48.00 | -         | -     | norm 0.4800 | 354,483,968 |            | lfm2_350m_winogrande_completion.json  | 2026-09-01 00:51 UTC |
| ours:corpus-v1-8k    | arc        | completion | 0     | -   | 200 | 0.2500 | 0.1900 | 19.00 | -         | -     | norm 0.1900 | 375,440,384 |            | ours_corpus-v1-8k_arc.json            | 2026-09-01 00:56 UTC |
| ours:corpus-v1-8k    | mmlu       | completion | 5     | -   | 200 | 0.2500 | 0.2750 | 27.50 | -         | -     | norm 0.2750 | 375,440,384 |            | ours_corpus-v1-8k_mmlu.json           | 2026-09-01 00:54 UTC |
| ours:corpus-v1-8k    | winogrande | completion | 0     | -   | 200 | 0.5000 | 0.5400 | 54.00 | -         | -     | norm 0.5400 | 375,440,384 |            | ours_corpus-v1-8k_winogrande.json     | 2026-09-01 00:58 UTC |
| ours:corpus-v1-8k    | mmlu       | completion | 5     | -   | 200 | 0.2500 | 0.2700 | 27.00 | -         | -     | norm 0.2700 | 375,440,384 |            | ours_mmlu_eotprefix_n200.json         | 2026-09-01 03:11 UTC |

## Record files that do not make a closed book row

These are measurements of something else, and they are named here rather than dropped so that a file going missing from the table above is visible.

| record file                         | why not                                                                     |
| ----------------------------------- | --------------------------------------------------------------------------- |
| cell2_ours_mmlu_retrieval_n400.json | carries no n, acc or strict_match; holds arms                               |
| cell4_lfm2_mmlu_retrieval_n200.json | carries no floor, acc or strict_match; holds records                        |
| cell4b_lfm2_mmlu_passages_n200.json | carries no floor, acc or strict_match; holds records                        |
| cell4c_lfm2_mmlu_seq5_n200.json     | carries no floor, acc or strict_match; holds records                        |
| gsm4_controls.json                  | carries no model, task, floor, acc or strict_match; holds no per item block |
| gsm4_lfm2_350m_bos_n200.json        | carries no acc or strict_match; holds arms                                  |
| gsm4_lfm2_350m_nobos_n200.json      | carries no acc or strict_match; holds arms                                  |
| gsm4_ours_native_a_n200.json        | carries no acc or strict_match; holds arms                                  |
| gsm4_ours_native_n200.json          | carries no acc or strict_match; holds arms                                  |
| gsm4_ours_shots_a_n200.json         | carries no acc or strict_match; holds arms                                  |
| gsm_lfm2_350m_n60.json              | carries no floor, acc or strict_match; holds no per item block              |

