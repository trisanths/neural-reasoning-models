## Structure exact match, greedy
| rung | params | train | qframe | lexicon | mode | mixed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| l45 | 45,483,008 | 0.9209 | 0.9161 | 0.8181 | 0.5256 | 0.5834 |
| xl93 | 93,579,520 | 0.8907 | 0.8841 | 0.7004 | 0.5076 | 0.5047 |

## Structure exact match, sampled
| rung | params | train | qframe | lexicon | mode | mixed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| l45 | 45,483,008 | 0.9163 | 0.9093 | 0.8124 | 0.5167 | 0.5781 |
| xl93 | 93,579,520 | 0.8794 | 0.8731 | 0.6899 | 0.4997 | 0.5007 |

## Per shape, train, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 500 | 1.0000 | 0.1160 | 1.0000 | 1.0000 |
| lookup_general | 500 | 1.0000 | 0.5200 | 1.0000 | 1.0000 |
| classify | 500 | 1.0000 | 0.0040 | 0.9980 | 0.9320 |
| inverse | 500 | 1.0000 | 0.1420 | 1.0000 | 1.0000 |
| compose | 500 | 1.0000 | 0.0300 | 0.5540 | 0.5360 |
| iterate | 500 | 1.0000 | 0.0300 | 1.0000 | 0.9980 |
| pair | 500 | 1.0000 | 0.1280 | 1.0000 | 1.0000 |
| priority | 500 | 1.0000 | 0.0620 | 1.0000 | 1.0000 |
| exclusion | 500 | 1.0000 | 0.1440 | 1.0000 | 1.0000 |
| lookup_then_band | 500 | 1.0000 | 0.0020 | 0.9720 | 0.8140 |
| band_then_lookup | 500 | 1.0000 | 0.0060 | 0.9980 | 0.9840 |
| sum_chain | 500 | 1.0000 | 0.0020 | 0.4020 | 0.2620 |
| apply_n | 500 | 1.0000 | 0.0040 | 0.9680 | 0.9440 |
| precedence | 500 | 1.0000 | 0.1480 | 1.0000 | 1.0000 |

## Per shape, qframe, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 500 | 1.0000 | 0.1120 | 1.0000 | 1.0000 |
| lookup_general | 500 | 1.0000 | 0.5020 | 1.0000 | 1.0000 |
| classify | 500 | 1.0000 | 0.0040 | 0.9880 | 0.9320 |
| inverse | 500 | 1.0000 | 0.1580 | 1.0000 | 1.0000 |
| compose | 500 | 1.0000 | 0.0280 | 0.5360 | 0.5000 |
| iterate | 500 | 1.0000 | 0.0280 | 1.0000 | 1.0000 |
| pair | 500 | 1.0000 | 0.1340 | 1.0000 | 1.0000 |
| priority | 500 | 1.0000 | 0.0440 | 1.0000 | 1.0000 |
| exclusion | 500 | 1.0000 | 0.1420 | 1.0000 | 1.0000 |
| lookup_then_band | 500 | 1.0000 | 0.0020 | 0.9620 | 0.8180 |
| band_then_lookup | 500 | 1.0000 | 0.0060 | 1.0000 | 0.9920 |
| sum_chain | 500 | 1.0000 | 0.0020 | 0.3760 | 0.2580 |
| apply_n | 500 | 1.0000 | 0.0040 | 0.9640 | 0.8780 |
| precedence | 500 | 1.0000 | 0.1360 | 1.0000 | 1.0000 |

## Per shape, lexicon, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 500 | 1.0000 | 0.1140 | 0.9640 | 0.3600 |
| lookup_general | 500 | 1.0000 | 0.5240 | 1.0000 | 0.8860 |
| classify | 500 | 1.0000 | 0.0040 | 0.9700 | 0.8040 |
| inverse | 500 | 1.0000 | 0.1460 | 0.9560 | 0.9580 |
| compose | 500 | 1.0000 | 0.0280 | 0.3620 | 0.3900 |
| iterate | 500 | 1.0000 | 0.0260 | 0.9740 | 0.9020 |
| pair | 500 | 1.0000 | 0.1260 | 1.0000 | 0.8940 |
| priority | 500 | 1.0000 | 0.0540 | 0.8900 | 0.9160 |
| exclusion | 500 | 1.0000 | 0.1420 | 0.9800 | 0.8700 |
| lookup_then_band | 500 | 1.0000 | 0.0020 | 0.5060 | 0.3860 |
| band_then_lookup | 500 | 1.0000 | 0.0080 | 0.9700 | 0.8860 |
| sum_chain | 500 | 1.0000 | 0.0020 | 0.1720 | 0.0740 |
| apply_n | 500 | 1.0000 | 0.0040 | 0.7120 | 0.7780 |
| precedence | 500 | 1.0000 | 0.1560 | 0.9980 | 0.7020 |

## Per shape, mode, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 500 | 1.0000 | 0.1360 | 0.4980 | 0.5040 |
| lookup_general | 500 | 1.0000 | 0.5120 | 1.0000 | 1.0000 |
| classify | 500 | 1.0000 | 0.0080 | 0.8380 | 0.6800 |
| inverse | 500 | 1.0000 | 0.1380 | 0.5040 | 0.5040 |
| compose | 500 | 1.0000 | 0.0320 | 0.1960 | 0.1060 |
| iterate | 500 | 1.0000 | 0.0280 | 0.5020 | 0.4860 |
| pair | 500 | 1.0000 | 0.1300 | 0.9760 | 1.0000 |
| priority | 500 | 1.0000 | 0.0440 | 0.5040 | 0.5200 |
| exclusion | 500 | 1.0000 | 0.1460 | 0.2320 | 0.1820 |
| lookup_then_band | 500 | 1.0000 | 0.0020 | 0.5300 | 0.3800 |
| band_then_lookup | 500 | 1.0000 | 0.0100 | 0.7120 | 0.6440 |
| sum_chain | 500 | 1.0000 | 0.0020 | 0.0640 | 0.0520 |
| apply_n | 500 | 1.0000 | 0.0020 | 0.2980 | 0.5420 |
| precedence | 500 | 1.0000 | 0.1340 | 0.5040 | 0.5060 |

## Per shape, mixed, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 500 | 1.0000 | 0.1160 | 0.6060 | 0.3340 |
| lookup_general | 500 | 1.0000 | 0.5220 | 1.0000 | 0.8480 |
| classify | 500 | 1.0000 | 0.0060 | 0.8480 | 0.6580 |
| inverse | 500 | 1.0000 | 0.1500 | 0.6380 | 0.6360 |
| compose | 500 | 1.0000 | 0.0300 | 0.2140 | 0.1720 |
| iterate | 500 | 1.0000 | 0.0260 | 0.6320 | 0.5540 |
| pair | 500 | 1.0000 | 0.1420 | 0.9660 | 0.8800 |
| priority | 500 | 1.0000 | 0.0420 | 0.5880 | 0.6660 |
| exclusion | 500 | 1.0000 | 0.1400 | 0.4400 | 0.3760 |
| lookup_then_band | 500 | 1.0000 | 0.0020 | 0.3940 | 0.2960 |
| band_then_lookup | 500 | 1.0000 | 0.0080 | 0.8060 | 0.6840 |
| sum_chain | 500 | 1.0000 | 0.0020 | 0.0960 | 0.0460 |
| apply_n | 500 | 1.0000 | 0.0040 | 0.3060 | 0.4200 |
| precedence | 500 | 1.0000 | 0.1360 | 0.6340 | 0.4960 |

## Safe failure against wrong executable structure, greedy
| rung | group | exact | malformed | refused | wrong | safe/unsafe |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | train | 0.9209 | 0.0000 | 0.0000 | 0.0791 | 0.000 |
| l45 | qframe | 0.9161 | 0.0000 | 0.0000 | 0.0839 | 0.000 |
| l45 | lexicon | 0.8181 | 0.0197 | 0.0010 | 0.1611 | 0.128 |
| l45 | mode | 0.5256 | 0.0010 | 0.0471 | 0.4263 | 0.113 |
| l45 | mixed | 0.5834 | 0.0197 | 0.0343 | 0.3626 | 0.149 |
| xl93 | train | 0.8907 | 0.0000 | 0.0000 | 0.1093 | 0.000 |
| xl93 | qframe | 0.8841 | 0.0000 | 0.0001 | 0.1157 | 0.001 |
| xl93 | lexicon | 0.7004 | 0.0843 | 0.0041 | 0.2111 | 0.419 |
| xl93 | mode | 0.5076 | 0.0019 | 0.0593 | 0.4313 | 0.142 |
| xl93 | mixed | 0.5047 | 0.0727 | 0.0437 | 0.3789 | 0.307 |

## The held-out sentence mode by key_pos, greedy exact
| rung | key_first (n) | value_first (n) |
| --- | ---: | ---: |
| l45 | 0.7302 (3528) | 0.3177 (3472) |
| xl93 | 0.6959 (3528) | 0.3162 (3472) |

## The held-out sentence mode by qform, greedy exact
| rung | cloze (n) | imperative (n) | inverted (n) | wh (n) |
| --- | ---: | ---: | ---: | ---: |
| l45 | 0.5248 (2016) | 0.5312 (1988) | 0.5206 (1988) | 0.5258 (1008) |
| xl93 | 0.5129 (2016) | 0.5086 (1988) | 0.5101 (1988) | 0.4901 (1008) |

## The held-out sentence mode by scope_pos, greedy exact
| rung | scope_first (n) | scope_last (n) |
| --- | ---: | ---: |
| l45 | 0.5217 (2996) | 0.5285 (4004) |
| xl93 | 0.5087 (2996) | 0.5067 (4004) |

## The held-out sentence mode by lexicon, greedy exact
| rung | abstract (n) | assembly (n) | clinic (n) | depot (n) | ledger (n) | routing (n) | transit (n) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| l45 | 0.5357 (1064) | 0.5367 (1036) | 0.5235 (980) | 0.5133 (980) | 0.5327 (980) | 0.5214 (980) | 0.5143 (980) |
| xl93 | 0.5216 (1064) | 0.5087 (1036) | 0.4980 (980) | 0.5020 (980) | 0.5092 (980) | 0.5061 (980) | 0.5061 (980) |

## The held-out sentence mode, shape against key position
### l45

| shape | key_first | value_first |
| --- | ---: | ---: |
| lookup | 0.9881 (252) | 0.0000 (248) |
| lookup_general | 1.0000 (252) | 1.0000 (248) |
| classify | 0.8056 (252) | 0.8710 (248) |
| inverse | 1.0000 (252) | 0.0000 (248) |
| compose | 0.3889 (252) | 0.0000 (248) |
| iterate | 0.9960 (252) | 0.0000 (248) |
| pair | 0.9841 (252) | 0.9677 (248) |
| priority | 1.0000 (252) | 0.0000 (248) |
| exclusion | 0.4603 (252) | 0.0000 (248) |
| lookup_then_band | 0.5198 (252) | 0.5403 (248) |
| band_then_lookup | 0.6627 (252) | 0.7621 (248) |
| sum_chain | 0.1270 (252) | 0.0000 (248) |
| apply_n | 0.2897 (252) | 0.3065 (248) |
| precedence | 1.0000 (252) | 0.0000 (248) |

### xl93

| shape | key_first | value_first |
| --- | ---: | ---: |
| lookup | 1.0000 (252) | 0.0000 (248) |
| lookup_general | 1.0000 (252) | 1.0000 (248) |
| classify | 0.6310 (252) | 0.7298 (248) |
| inverse | 0.9841 (252) | 0.0161 (248) |
| compose | 0.2063 (252) | 0.0040 (248) |
| iterate | 0.9603 (252) | 0.0040 (248) |
| pair | 1.0000 (252) | 1.0000 (248) |
| priority | 0.9802 (252) | 0.0524 (248) |
| exclusion | 0.3611 (252) | 0.0000 (248) |
| lookup_then_band | 0.3849 (252) | 0.3750 (248) |
| band_then_lookup | 0.5952 (252) | 0.6935 (248) |
| sum_chain | 0.0992 (252) | 0.0040 (248) |
| apply_n | 0.5397 (252) | 0.5444 (248) |
| precedence | 1.0000 (252) | 0.0040 (248) |

## Tokens per parameter, and what a matched budget costs
| rung | parameters | target tokens per parameter | source tokens per parameter | steps to match l45 |
| --- | ---: | ---: | ---: | ---: |
| l45 | 45,483,008 | 5.24 | 21.36 | 30,000 |
| xl93 | 93,579,520 | 2.55 | 10.38 | 61,724 |
| xxl167 | 167,182,336 | 1.43 | 5.81 | 110,271 |
| xxxl355 | 355,127,936 | 0.67 | 2.74 | 234,238 |

## What each rung did to its own training file
| rung | peak lr | loss at 8,000 | at 15,000 | at 30,000 | peak GB |
| --- | ---: | ---: | ---: | ---: | ---: |
| l45 | 0.0004 | 0.0843 | 0.0417 | 0.0126 | n/a |
| xl93 | 0.00032 | 0.1009 | 0.0525 | 0.0182 | 20.69 |
| xl93lr40 | 0.0004 | 0.0832 | 0.039 | 0.0187 | 20.69 |
| xl93match | 0.0004 | 0.1063 | 0.0575 | 0.0188 | 20.69 |

## The learning rate control
| checkpoint | mode | train | qframe | lexicon | mode | mixed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | greedy | 0.9209 | 0.9161 | 0.8181 | 0.5256 | 0.5834 |
| l45 | sampled | 0.9163 | 0.9093 | 0.8124 | 0.5167 | 0.5781 |
| xl93 | greedy | 0.8907 | 0.8841 | 0.7004 | 0.5076 | 0.5047 |
| xl93 | sampled | 0.8794 | 0.8731 | 0.6899 | 0.4997 | 0.5007 |
| xl93lr40 | greedy | 0.9024 | 0.8991 | 0.8273 | 0.4637 | 0.5444 |
| xl93lr40 | sampled | 0.9009 | 0.8940 | 0.8227 | 0.4611 | 0.5411 |
| xl93match | greedy | 0.9574 | 0.9569 | 0.7951 | 0.5231 | 0.5644 |
| xl93match | sampled | 0.9560 | 0.9537 | 0.7906 | 0.5231 | 0.5629 |

## The three frame splits
| split | data | withheld question frame | withheld lexicon | withheld statement mode | training frames |
| --- | --- | --- | --- | --- | ---: |
| l45 | `data/norm` | band, every 8th | signal | relative_clause | 490 |
| c45 | `data/normC` | wh | signal | relative_clause | 420 |
| b45 | `data/normB` | band, every 8th | signal | table_row | 490 |

## Each alternative split on its own withheld group
| split | withheld | group | n | key_first | value_first |
| --- | --- | --- | ---: | ---: | ---: |
| c45 | one whole value of the question-form axis, `wh` | qframe | 7000 | 0.7440 (3500) | 0.7611 (3500) |
| c45 | one whole value of the question-form axis, `wh` | mode | 7000 | 0.6865 (3528) | 0.2736 (3472) |
| c45 | one whole value of the question-form axis, `wh` | train | 7000 | 0.8688 (3528) | 0.8652 (3472) |
| b45 | a different statement mode, `table_row` | mode | 7000 | 0.6165 (3528) | 0.2471 (3472) |
| b45 | a different statement mode, `table_row` | mode | 7000 | 0.6165 (3528) | 0.2471 (3472) |
| b45 | a different statement mode, `table_row` | train | 7000 | 0.9269 (3528) | 0.9332 (3472) |

## Alternative splits, shape against key position
**c45, the qframe group, one whole value of the question-form axis, `wh` withheld**

### c45

| shape | key_first | value_first |
| --- | ---: | ---: |
| lookup | 1.0000 (250) | 1.0000 (250) |
| lookup_general | 1.0000 (250) | 1.0000 (250) |
| classify | 0.6600 (250) | 0.5840 (250) |
| inverse | 0.5960 (250) | 0.8160 (250) |
| compose | 0.3080 (250) | 0.3200 (250) |
| iterate | 1.0000 (250) | 0.9840 (250) |
| pair | 1.0000 (250) | 0.9920 (250) |
| priority | 0.9960 (250) | 1.0000 (250) |
| exclusion | 0.9240 (250) | 1.0000 (250) |
| lookup_then_band | 0.7440 (250) | 0.7480 (250) |
| band_then_lookup | 0.9240 (250) | 0.9440 (250) |
| sum_chain | 0.1520 (250) | 0.1720 (250) |
| apply_n | 0.1120 (250) | 0.0960 (250) |
| precedence | 1.0000 (250) | 1.0000 (250) |

**b45, the mode group, a different statement mode, `table_row` withheld**

### b45

| shape | key_first | value_first |
| --- | ---: | ---: |
| lookup | 1.0000 (252) | 0.0000 (248) |
| lookup_general | 1.0000 (252) | 1.0000 (248) |
| classify | 0.7500 (252) | 0.7419 (248) |
| inverse | 0.9365 (252) | 0.0000 (248) |
| compose | 0.1587 (252) | 0.0000 (248) |
| iterate | 0.8810 (252) | 0.0000 (248) |
| pair | 0.9444 (252) | 0.9476 (248) |
| priority | 0.9008 (252) | 0.0000 (248) |
| exclusion | 0.4405 (252) | 0.0161 (248) |
| lookup_then_band | 0.0119 (252) | 0.0040 (248) |
| band_then_lookup | 0.4960 (252) | 0.6048 (248) |
| sum_chain | 0.0000 (252) | 0.0000 (248) |
| apply_n | 0.1151 (252) | 0.1452 (248) |
| precedence | 0.9960 (252) | 0.0000 (248) |

## Key position inside every frame group
| checkpoint | frame group | key_first | value_first |
| --- | --- | ---: | ---: |
| l45 | train | 0.9206 (3528) | 0.9211 (3472) |
| l45 | qframe | 0.9149 (3500) | 0.9174 (3500) |
| l45 | lexicon | 0.8294 (3528) | 0.8067 (3472) |
| l45 | mode | 0.7302 (3528) | 0.3177 (3472) |
| l45 | mixed | 0.7314 (3500) | 0.4354 (3500) |
| xl93 | train | 0.8900 (3528) | 0.8914 (3472) |
| xl93 | qframe | 0.8834 (3500) | 0.8849 (3500) |
| xl93 | lexicon | 0.6811 (3528) | 0.7200 (3472) |
| xl93 | mode | 0.6959 (3528) | 0.3162 (3472) |
| xl93 | mixed | 0.5523 (3500) | 0.4571 (3500) |
| xl93lr40 | train | 0.9031 (3528) | 0.9018 (3472) |
| xl93lr40 | qframe | 0.8986 (3500) | 0.8997 (3500) |
| xl93lr40 | lexicon | 0.8325 (3528) | 0.8220 (3472) |
| xl93lr40 | mode | 0.6375 (3528) | 0.2872 (3472) |
| xl93lr40 | mixed | 0.6700 (3500) | 0.4189 (3500) |
| xl93match | train | 0.9555 (3528) | 0.9594 (3472) |
| xl93match | qframe | 0.9563 (3500) | 0.9574 (3500) |
| xl93match | lexicon | 0.7494 (3528) | 0.8416 (3472) |
| xl93match | mode | 0.3243 (3528) | 0.7252 (3472) |
| xl93match | mixed | 0.4051 (3500) | 0.7237 (3500) |
| c45 | train | 0.8688 (3528) | 0.8652 (3472) |
| c45 | qframe | 0.7440 (3500) | 0.7611 (3500) |
| c45 | lexicon | 0.8220 (3528) | 0.8154 (3472) |
| c45 | mode | 0.6865 (3528) | 0.2736 (3472) |
| c45 | mixed | 0.6732 (3556) | 0.4126 (3444) |
| b45 | train | 0.9269 (3528) | 0.9332 (3472) |
| b45 | qframe | 0.9226 (3500) | 0.9257 (3500) |
| b45 | lexicon | 0.7378 (3528) | 0.6959 (3472) |
| b45 | mode | 0.6165 (3528) | 0.2471 (3472) |
| b45 | mixed | 0.6184 (3514) | 0.3328 (3486) |
| corpus_nosft | train | 0.0000 (704) | 0.0000 (696) |
| corpus_nosft | qframe | 0.0000 (700) | 0.0000 (700) |
| corpus_nosft | lexicon | 0.0000 (705) | 0.0000 (695) |
| corpus_nosft | mode | 0.0000 (705) | 0.0000 (695) |
| corpus_nosft | mixed | 0.0000 (712) | 0.0000 (688) |

## What the value-first failures are made of
| rung | key position | n | exact | wrong | refused | malformed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | key_first | 749 | 528 / 749 = 0.7049 | 221 / 749 = 0.2951 | 0 / 749 = 0.0000 | 0 / 749 = 0.0000 |
| l45 | value_first | 651 | 0 / 651 = 0.0000 | 531 / 651 = 0.8157 | 120 / 651 = 0.1843 | 0 / 651 = 0.0000 |
| xl93 | key_first | 749 | 489 / 749 = 0.6529 | 256 / 749 = 0.3418 | 4 / 749 = 0.0053 | 0 / 749 = 0.0000 |
| xl93 | value_first | 651 | 0 / 651 = 0.0000 | 491 / 651 = 0.7542 | 159 / 651 = 0.2442 | 1 / 651 = 0.0015 |

## The reference parser on the same split
| frame group | key position | n | parser exact |
| --- | --- | ---: | ---: |
| train | key_first | 1386 | 1386 / 1386 = 1.0000 |
| train | value_first | 1414 | 1414 / 1414 = 1.0000 |
| mode | key_first | 1498 | 1498 / 1498 = 1.0000 |
| mode | value_first | 1302 | 1302 / 1302 = 1.0000 |

## The reference parser on every split, by key position
| split | frame group | key_first | value_first |
| --- | --- | ---: | ---: |
| `norm` | train | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |
| `norm` | qframe | 3500 / 3500 = 1.0000 | 3500 / 3500 = 1.0000 |
| `norm` | lexicon | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |
| `norm` | mode | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |
| `norm` | mixed | 3500 / 3500 = 1.0000 | 3500 / 3500 = 1.0000 |
| `normB` | mode | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |
| `normB` | qframe | 3500 / 3500 = 1.0000 | 3500 / 3500 = 1.0000 |
| `normB` | train | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |
| `normC` | qframe | 3500 / 3500 = 1.0000 | 3500 / 3500 = 1.0000 |
| `normC` | mode | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |
| `normC` | train | 3528 / 3528 = 1.0000 | 3472 / 3472 = 1.0000 |

## Key position in the training draw
| shape | key_first | value_first | value_first share | scores 0.0000 on value_first |
| --- | ---: | ---: | ---: | --- |
| apply_n | 42,781 | 43,122 | 0.5020 |  |
| band_then_lookup | 42,858 | 42,599 | 0.4985 |  |
| classify | 42,723 | 42,920 | 0.5011 |  |
| compose | 42,801 | 42,776 | 0.4999 | yes |
| exclusion | 42,817 | 42,917 | 0.5006 | yes |
| inverse | 42,900 | 42,820 | 0.4995 | yes |
| iterate | 42,895 | 42,572 | 0.4981 | yes |
| lookup | 42,748 | 42,567 | 0.4989 | yes |
| lookup_general | 43,026 | 42,870 | 0.4991 |  |
| lookup_then_band | 42,730 | 42,969 | 0.5014 |  |
| pair | 42,689 | 42,737 | 0.5003 |  |
| precedence | 43,105 | 42,918 | 0.4989 | yes |
| priority | 43,131 | 42,950 | 0.4989 |  |
| sum_chain | 43,216 | 42,843 | 0.4978 | yes |

## Value-first items per trained sentence mode
| shape | conditional | imperative | mapping | passive_decl | table_row |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 8,522 | 8,614 | 8,412 | 8,434 | 8,585 |
| inverse | 8,740 | 8,511 | 8,519 | 8,393 | 8,657 |
| iterate | 8,444 | 8,402 | 8,617 | 8,494 | 8,615 |
| compose | 8,573 | 8,765 | 8,362 | 8,577 | 8,499 |
| exclusion | 8,389 | 8,526 | 8,408 | 8,910 | 8,684 |
| sum_chain | 8,532 | 8,564 | 8,662 | 8,508 | 8,577 |
| precedence | 8,514 | 8,587 | 8,545 | 8,587 | 8,685 |

## Operand order in the grid draws
| draw | pages | row-major key order | another key order |
| --- | ---: | ---: | ---: |
| `grid_train` | 4,096 | 4,096 | 0 |
| `grid_both` | 1,024 | 512 | 512 |

| pair | shared pages |
| --- | ---: |
| `grid_both` and `grid_train` | 0 |
| `grid_train` and the transposed items | 0 |
| `grid_both` and the transposed items | 0 |
| `grid_both` and the original items | 0 |

## The transposed operand test
| rung | grids seen | version | n | exact | keys in the untransposed order | malformed | other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | 1024 | original | 750 | 672 / 750 = 0.8960 | 0 / 750 = 0.0000 | 20 / 750 = 0.0267 | 58 / 750 = 0.0773 |
| l45 | 1024 | transposed | 750 | 0 / 750 = 0.0000 | 733 / 750 = 0.9773 | 17 / 750 = 0.0227 | 0 / 750 = 0.0000 |
| xl93 | 1024 | original | 750 | 534 / 750 = 0.7120 | 0 / 750 = 0.0000 | 20 / 750 = 0.0267 | 196 / 750 = 0.2613 |
| xl93 | 1024 | transposed | 750 | 0 / 750 = 0.0000 | 721 / 750 = 0.9613 | 22 / 750 = 0.0293 | 7 / 750 = 0.0093 |

## The transposed operand test, per frame group
| rung | version | frame group | n | exact | keys in the untransposed order | malformed | other |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | original | lexicon | 150 | 130 / 150 = 0.8667 | 0 / 150 = 0.0000 | 5 / 150 = 0.0333 | 15 / 150 = 0.1000 |
| l45 | original | mixed | 150 | 114 / 150 = 0.7600 | 0 / 150 = 0.0000 | 15 / 150 = 0.1000 | 21 / 150 = 0.1400 |
| l45 | original | mode | 150 | 134 / 150 = 0.8933 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 16 / 150 = 0.1067 |
| l45 | original | qframe | 150 | 145 / 150 = 0.9667 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 5 / 150 = 0.0333 |
| l45 | original | train | 150 | 149 / 150 = 0.9933 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 1 / 150 = 0.0067 |
| l45 | transposed | lexicon | 150 | 0 / 150 = 0.0000 | 145 / 150 = 0.9667 | 5 / 150 = 0.0333 | 0 / 150 = 0.0000 |
| l45 | transposed | mixed | 150 | 0 / 150 = 0.0000 | 138 / 150 = 0.9200 | 12 / 150 = 0.0800 | 0 / 150 = 0.0000 |
| l45 | transposed | mode | 150 | 0 / 150 = 0.0000 | 150 / 150 = 1.0000 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |
| l45 | transposed | qframe | 150 | 0 / 150 = 0.0000 | 150 / 150 = 1.0000 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |
| l45 | transposed | train | 150 | 0 / 150 = 0.0000 | 150 / 150 = 1.0000 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |
| xl93 | original | lexicon | 150 | 122 / 150 = 0.8133 | 0 / 150 = 0.0000 | 15 / 150 = 0.1000 | 13 / 150 = 0.0867 |
| xl93 | original | mixed | 150 | 67 / 150 = 0.4467 | 0 / 150 = 0.0000 | 5 / 150 = 0.0333 | 78 / 150 = 0.5200 |
| xl93 | original | mode | 150 | 82 / 150 = 0.5467 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 68 / 150 = 0.4533 |
| xl93 | original | qframe | 150 | 115 / 150 = 0.7667 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 35 / 150 = 0.2333 |
| xl93 | original | train | 150 | 148 / 150 = 0.9867 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 2 / 150 = 0.0133 |
| xl93 | transposed | lexicon | 150 | 0 / 150 = 0.0000 | 132 / 150 = 0.8800 | 11 / 150 = 0.0733 | 7 / 150 = 0.0467 |
| xl93 | transposed | mixed | 150 | 0 / 150 = 0.0000 | 139 / 150 = 0.9267 | 11 / 150 = 0.0733 | 0 / 150 = 0.0000 |
| xl93 | transposed | mode | 150 | 0 / 150 = 0.0000 | 150 / 150 = 1.0000 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |
| xl93 | transposed | qframe | 150 | 0 / 150 = 0.0000 | 150 / 150 = 1.0000 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |
| xl93 | transposed | train | 150 | 0 / 150 = 0.0000 | 150 / 150 = 1.0000 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |

## The same test after a fine tune that showed both operand orders
| rung | grids seen | version | n | exact | keys in the untransposed order | malformed | other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | 1024 | original | 750 | 404 / 750 = 0.5387 | 0 / 750 = 0.0000 | 1 / 750 = 0.0013 | 345 / 750 = 0.4600 |
| l45 | 1024 | transposed | 750 | 462 / 750 = 0.6160 | 258 / 750 = 0.3440 | 1 / 750 = 0.0013 | 29 / 750 = 0.0387 |

## That test per frame group
| rung | version | frame group | n | exact | keys in the untransposed order | malformed | other |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | original | lexicon | 150 | 68 / 150 = 0.4533 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 82 / 150 = 0.5467 |
| l45 | original | mixed | 150 | 63 / 150 = 0.4200 | 0 / 150 = 0.0000 | 1 / 150 = 0.0067 | 86 / 150 = 0.5733 |
| l45 | original | mode | 150 | 86 / 150 = 0.5733 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 64 / 150 = 0.4267 |
| l45 | original | qframe | 150 | 98 / 150 = 0.6533 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 52 / 150 = 0.3467 |
| l45 | original | train | 150 | 89 / 150 = 0.5933 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 | 61 / 150 = 0.4067 |
| l45 | transposed | lexicon | 150 | 110 / 150 = 0.7333 | 31 / 150 = 0.2067 | 0 / 150 = 0.0000 | 9 / 150 = 0.0600 |
| l45 | transposed | mixed | 150 | 76 / 150 = 0.5067 | 59 / 150 = 0.3933 | 1 / 150 = 0.0067 | 14 / 150 = 0.0933 |
| l45 | transposed | mode | 150 | 55 / 150 = 0.3667 | 92 / 150 = 0.6133 | 0 / 150 = 0.0000 | 3 / 150 = 0.0200 |
| l45 | transposed | qframe | 150 | 108 / 150 = 0.7200 | 42 / 150 = 0.2800 | 0 / 150 = 0.0000 | 0 / 150 = 0.0000 |
| l45 | transposed | train | 150 | 113 / 150 = 0.7533 | 34 / 150 = 0.2267 | 0 / 150 = 0.0000 | 3 / 150 = 0.0200 |

## What the 1,024 grids cost the groups already read
| rung | frame group | n | before the fine tune | after |
| --- | --- | ---: | ---: | ---: |
| l45 | train | 700 | 0.9171 | 0.9043 |
| l45 | qframe | 700 | 0.9086 | 0.8957 |
| l45 | lexicon | 700 | 0.7971 | 0.7957 |
| l45 | mode | 700 | 0.5657 | 0.5500 |
| xl93 | train | 700 | 0.8900 | 0.8614 |
| xl93 | qframe | 700 | 0.8857 | 0.8514 |
| xl93 | lexicon | 700 | 0.6871 | 0.6986 |
| xl93 | mode | 700 | 0.5529 | 0.5186 |

## The 350M arm, structure exact match
| checkpoint | mode | train | qframe | lexicon | mode | mixed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| corpus_nosft | greedy | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## The 350M arm, safe failure, greedy
| checkpoint | group | n | exact | malformed | refused | wrong | safe/unsafe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| corpus_nosft | train | 1400 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | inf |
| corpus_nosft | qframe | 1400 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | inf |
| corpus_nosft | lexicon | 1400 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | inf |
| corpus_nosft | mode | 1400 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | inf |
| corpus_nosft | mixed | 1400 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | inf |

## Per shape, corpus_nosft, train, greedy exact
| shape | n | parser | modal/shape | corpus_nosft |
| --- | ---: | ---: | ---: | ---: |
| lookup | 100 | 1.0000 | 0.1800 | 0.0000 |
| lookup_general | 100 | 1.0000 | 0.5100 | 0.0000 |
| classify | 100 | 1.0000 | 0.0200 | 0.0000 |
| inverse | 100 | 1.0000 | 0.1600 | 0.0000 |
| compose | 100 | 1.0000 | 0.0500 | 0.0000 |
| iterate | 100 | 1.0000 | 0.0400 | 0.0000 |
| pair | 100 | 1.0000 | 0.1500 | 0.0000 |
| priority | 100 | 1.0000 | 0.0800 | 0.0000 |
| exclusion | 100 | 1.0000 | 0.2000 | 0.0000 |
| lookup_then_band | 100 | 1.0000 | 0.0100 | 0.0000 |
| band_then_lookup | 100 | 1.0000 | 0.0200 | 0.0000 |
| sum_chain | 100 | 1.0000 | 0.0100 | 0.0000 |
| apply_n | 100 | 1.0000 | 0.0100 | 0.0000 |
| precedence | 100 | 1.0000 | 0.1600 | 0.0000 |

## Per shape, corpus_nosft, qframe, greedy exact
| shape | n | parser | modal/shape | corpus_nosft |
| --- | ---: | ---: | ---: | ---: |
| lookup | 100 | 1.0000 | 0.1200 | 0.0000 |
| lookup_general | 100 | 1.0000 | 0.5100 | 0.0000 |
| classify | 100 | 1.0000 | 0.0200 | 0.0000 |
| inverse | 100 | 1.0000 | 0.2200 | 0.0000 |
| compose | 100 | 1.0000 | 0.0600 | 0.0000 |
| iterate | 100 | 1.0000 | 0.0400 | 0.0000 |
| pair | 100 | 1.0000 | 0.1600 | 0.0000 |
| priority | 100 | 1.0000 | 0.0600 | 0.0000 |
| exclusion | 100 | 1.0000 | 0.1500 | 0.0000 |
| lookup_then_band | 100 | 1.0000 | 0.0100 | 0.0000 |
| band_then_lookup | 100 | 1.0000 | 0.0200 | 0.0000 |
| sum_chain | 100 | 1.0000 | 0.0100 | 0.0000 |
| apply_n | 100 | 1.0000 | 0.0100 | 0.0000 |
| precedence | 100 | 1.0000 | 0.1400 | 0.0000 |

## Per shape, corpus_nosft, lexicon, greedy exact
| shape | n | parser | modal/shape | corpus_nosft |
| --- | ---: | ---: | ---: | ---: |
| lookup | 100 | 1.0000 | 0.1400 | 0.0000 |
| lookup_general | 100 | 1.0000 | 0.5000 | 0.0000 |
| classify | 100 | 1.0000 | 0.0200 | 0.0000 |
| inverse | 100 | 1.0000 | 0.1600 | 0.0000 |
| compose | 100 | 1.0000 | 0.0400 | 0.0000 |
| iterate | 100 | 1.0000 | 0.0500 | 0.0000 |
| pair | 100 | 1.0000 | 0.1500 | 0.0000 |
| priority | 100 | 1.0000 | 0.0800 | 0.0000 |
| exclusion | 100 | 1.0000 | 0.1500 | 0.0000 |
| lookup_then_band | 100 | 1.0000 | 0.0100 | 0.0000 |
| band_then_lookup | 100 | 1.0000 | 0.0200 | 0.0000 |
| sum_chain | 100 | 1.0000 | 0.0100 | 0.0000 |
| apply_n | 100 | 1.0000 | 0.0100 | 0.0000 |
| precedence | 100 | 1.0000 | 0.1800 | 0.0000 |

## Per shape, corpus_nosft, mode, greedy exact
| shape | n | parser | modal/shape | corpus_nosft |
| --- | ---: | ---: | ---: | ---: |
| lookup | 100 | 1.0000 | 0.1500 | 0.0000 |
| lookup_general | 100 | 1.0000 | 0.5100 | 0.0000 |
| classify | 100 | 1.0000 | 0.0200 | 0.0000 |
| inverse | 100 | 1.0000 | 0.1800 | 0.0000 |
| compose | 100 | 1.0000 | 0.0300 | 0.0000 |
| iterate | 100 | 1.0000 | 0.0600 | 0.0000 |
| pair | 100 | 1.0000 | 0.1600 | 0.0000 |
| priority | 100 | 1.0000 | 0.0600 | 0.0000 |
| exclusion | 100 | 1.0000 | 0.1600 | 0.0000 |
| lookup_then_band | 100 | 1.0000 | 0.0100 | 0.0000 |
| band_then_lookup | 100 | 1.0000 | 0.0200 | 0.0000 |
| sum_chain | 100 | 1.0000 | 0.0100 | 0.0000 |
| apply_n | 100 | 1.0000 | 0.0100 | 0.0000 |
| precedence | 100 | 1.0000 | 0.1600 | 0.0000 |

## Per shape, corpus_nosft, mixed, greedy exact
| shape | n | parser | modal/shape | corpus_nosft |
| --- | ---: | ---: | ---: | ---: |
| lookup | 100 | 1.0000 | 0.1400 | 0.0000 |
| lookup_general | 100 | 1.0000 | 0.5600 | 0.0000 |
| classify | 100 | 1.0000 | 0.0200 | 0.0000 |
| inverse | 100 | 1.0000 | 0.2200 | 0.0000 |
| compose | 100 | 1.0000 | 0.0300 | 0.0000 |
| iterate | 100 | 1.0000 | 0.0400 | 0.0000 |
| pair | 100 | 1.0000 | 0.1700 | 0.0000 |
| priority | 100 | 1.0000 | 0.0600 | 0.0000 |
| exclusion | 100 | 1.0000 | 0.2500 | 0.0000 |
| lookup_then_band | 100 | 1.0000 | 0.0100 | 0.0000 |
| band_then_lookup | 100 | 1.0000 | 0.0200 | 0.0000 |
| sum_chain | 100 | 1.0000 | 0.0100 | 0.0000 |
| apply_n | 100 | 1.0000 | 0.0100 | 0.0000 |
| precedence | 100 | 1.0000 | 0.2000 | 0.0000 |

## Held-out frames, forced choice, before and after the structure fine tune
| split | n | floor | strict, before | corrected, before | strict, after | corrected, after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| lexicon | 300 | 0.2686 | 0.5300 | 0.3574 | n/a | n/a |
| mixed | 300 | 0.2686 | 0.5133 | 0.3346 | n/a | n/a |
| mode | 300 | 0.2686 | 0.5633 | 0.4030 | n/a | n/a |
| qframe | 300 | 0.2686 | 0.5333 | 0.3620 | n/a | n/a |
| train | 300 | 0.2686 | 0.5367 | 0.3665 | n/a | n/a |

## Records against the reports beside them
| report | written | records | newest record | ok |
| --- | --- | ---: | --- | --- |
| l45 | 2026-08-31 22:51 | 10 | 2026-08-31 22:51 | yes |
| xl93 | 2026-08-31 23:11 | 10 | 2026-08-31 23:11 | yes |
| ftl45 | 2026-08-31 20:01 | 10 | 2026-08-31 20:01 | yes |
| ftxl93 | 2026-08-31 20:06 | 10 | 2026-08-31 20:06 | yes |
| corpus_nosft | 2026-09-01 07:19 | 5 | 2026-09-01 07:19 | yes |
