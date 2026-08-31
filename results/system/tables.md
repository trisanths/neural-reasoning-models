## Structure exact match, greedy
| rung | params | train | qframe | lexicon | mode | mixed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| l45 | 45,483,008 | 0.9211 | 0.9129 | 0.8125 | 0.5389 | 0.5525 |
| xl93 | 93,579,520 | 0.8889 | 0.8839 | 0.6921 | 0.5221 | 0.4714 |

## Structure exact match, sampled
| rung | params | train | qframe | lexicon | mode | mixed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| l45 | 45,483,008 | 0.9139 | 0.9075 | 0.8039 | 0.5357 | 0.5454 |
| xl93 | 93,579,520 | 0.8779 | 0.8686 | 0.6796 | 0.5182 | 0.4675 |

## Per shape, train, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 200 | 1.0000 | 0.1250 | 1.0000 | 1.0000 |
| lookup_general | 200 | 1.0000 | 0.5700 | 1.0000 | 1.0000 |
| classify | 200 | 1.0000 | 0.0100 | 0.9950 | 0.9300 |
| inverse | 200 | 1.0000 | 0.1500 | 1.0000 | 1.0000 |
| compose | 200 | 1.0000 | 0.0350 | 0.5450 | 0.5300 |
| iterate | 200 | 1.0000 | 0.0300 | 1.0000 | 1.0000 |
| pair | 200 | 1.0000 | 0.1400 | 1.0000 | 1.0000 |
| priority | 200 | 1.0000 | 0.0700 | 1.0000 | 1.0000 |
| exclusion | 200 | 1.0000 | 0.1400 | 1.0000 | 1.0000 |
| lookup_then_band | 200 | 1.0000 | 0.0050 | 0.9750 | 0.8150 |
| band_then_lookup | 200 | 1.0000 | 0.0100 | 0.9950 | 0.9850 |
| sum_chain | 200 | 1.0000 | 0.0050 | 0.4200 | 0.2450 |
| apply_n | 200 | 1.0000 | 0.0050 | 0.9650 | 0.9400 |
| precedence | 200 | 1.0000 | 0.1600 | 1.0000 | 1.0000 |

## Per shape, qframe, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 200 | 1.0000 | 0.2400 | 1.0000 | 1.0000 |
| lookup_general | 200 | 1.0000 | 0.5350 | 1.0000 | 1.0000 |
| classify | 200 | 1.0000 | 0.0100 | 0.9900 | 0.9350 |
| inverse | 200 | 1.0000 | 0.3050 | 1.0000 | 1.0000 |
| compose | 200 | 1.0000 | 0.0450 | 0.5250 | 0.5000 |
| iterate | 200 | 1.0000 | 0.0500 | 1.0000 | 1.0000 |
| pair | 200 | 1.0000 | 0.1450 | 1.0000 | 1.0000 |
| priority | 200 | 1.0000 | 0.0900 | 1.0000 | 1.0000 |
| exclusion | 200 | 1.0000 | 0.2700 | 1.0000 | 1.0000 |
| lookup_then_band | 200 | 1.0000 | 0.0050 | 0.9700 | 0.8100 |
| band_then_lookup | 200 | 1.0000 | 0.0150 | 1.0000 | 0.9850 |
| sum_chain | 200 | 1.0000 | 0.0050 | 0.3200 | 0.2350 |
| apply_n | 200 | 1.0000 | 0.0050 | 0.9750 | 0.9100 |
| precedence | 200 | 1.0000 | 0.2800 | 1.0000 | 1.0000 |

## Per shape, lexicon, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 200 | 1.0000 | 0.1350 | 0.9600 | 0.3100 |
| lookup_general | 200 | 1.0000 | 0.5500 | 1.0000 | 0.8850 |
| classify | 200 | 1.0000 | 0.0100 | 0.9550 | 0.7750 |
| inverse | 200 | 1.0000 | 0.1850 | 0.9600 | 0.9600 |
| compose | 200 | 1.0000 | 0.0250 | 0.3100 | 0.3350 |
| iterate | 200 | 1.0000 | 0.0300 | 0.9800 | 0.8700 |
| pair | 200 | 1.0000 | 0.1500 | 1.0000 | 0.8650 |
| priority | 200 | 1.0000 | 0.0500 | 0.8850 | 0.9450 |
| exclusion | 200 | 1.0000 | 0.1600 | 0.9750 | 0.8800 |
| lookup_then_band | 200 | 1.0000 | 0.0050 | 0.4950 | 0.4050 |
| band_then_lookup | 200 | 1.0000 | 0.0100 | 0.9650 | 0.8850 |
| sum_chain | 200 | 1.0000 | 0.0050 | 0.2000 | 0.0800 |
| apply_n | 200 | 1.0000 | 0.0050 | 0.6900 | 0.7900 |
| precedence | 200 | 1.0000 | 0.1500 | 1.0000 | 0.7050 |

## Per shape, mode, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 200 | 1.0000 | 0.1450 | 0.5300 | 0.5350 |
| lookup_general | 200 | 1.0000 | 0.5100 | 1.0000 | 1.0000 |
| classify | 200 | 1.0000 | 0.0100 | 0.8500 | 0.7150 |
| inverse | 200 | 1.0000 | 0.1500 | 0.5350 | 0.5300 |
| compose | 200 | 1.0000 | 0.0350 | 0.2200 | 0.1150 |
| iterate | 200 | 1.0000 | 0.0350 | 0.5350 | 0.5150 |
| pair | 200 | 1.0000 | 0.1500 | 0.9900 | 1.0000 |
| priority | 200 | 1.0000 | 0.0500 | 0.5350 | 0.5600 |
| exclusion | 200 | 1.0000 | 0.1650 | 0.2150 | 0.1600 |
| lookup_then_band | 200 | 1.0000 | 0.0050 | 0.5350 | 0.4000 |
| band_then_lookup | 200 | 1.0000 | 0.0100 | 0.7100 | 0.6250 |
| sum_chain | 200 | 1.0000 | 0.0050 | 0.0700 | 0.0550 |
| apply_n | 200 | 1.0000 | 0.0050 | 0.2850 | 0.5650 |
| precedence | 200 | 1.0000 | 0.1600 | 0.5350 | 0.5350 |

## Per shape, mixed, greedy exact
| shape | n | parser | modal/shape | l45 | xl93 |
| --- | ---: | ---: | ---: | ---: | ---: |
| lookup | 200 | 1.0000 | 0.1600 | 0.5450 | 0.2600 |
| lookup_general | 200 | 1.0000 | 0.5700 | 1.0000 | 0.8450 |
| classify | 200 | 1.0000 | 0.0100 | 0.8750 | 0.6600 |
| inverse | 200 | 1.0000 | 0.1900 | 0.5650 | 0.5950 |
| compose | 200 | 1.0000 | 0.0350 | 0.1500 | 0.1400 |
| iterate | 200 | 1.0000 | 0.0300 | 0.5600 | 0.4750 |
| pair | 200 | 1.0000 | 0.1350 | 0.9550 | 0.8850 |
| priority | 200 | 1.0000 | 0.0500 | 0.5050 | 0.5750 |
| exclusion | 200 | 1.0000 | 0.1800 | 0.3900 | 0.3250 |
| lookup_then_band | 200 | 1.0000 | 0.0050 | 0.4000 | 0.3300 |
| band_then_lookup | 200 | 1.0000 | 0.0150 | 0.8100 | 0.6600 |
| sum_chain | 200 | 1.0000 | 0.0050 | 0.1050 | 0.0450 |
| apply_n | 200 | 1.0000 | 0.0050 | 0.3050 | 0.3850 |
| precedence | 200 | 1.0000 | 0.1500 | 0.5700 | 0.4200 |

## Safe failure against wrong executable structure, greedy
| rung | group | exact | malformed | refused | wrong | safe/unsafe |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| l45 | train | 0.9211 | 0.0000 | 0.0000 | 0.0789 | 0.000 |
| l45 | qframe | 0.9129 | 0.0000 | 0.0000 | 0.0871 | 0.000 |
| l45 | lexicon | 0.8125 | 0.0207 | 0.0011 | 0.1657 | 0.132 |
| l45 | mode | 0.5389 | 0.0007 | 0.0429 | 0.4175 | 0.104 |
| l45 | mixed | 0.5525 | 0.0175 | 0.0439 | 0.3861 | 0.159 |
| xl93 | train | 0.8889 | 0.0000 | 0.0000 | 0.1111 | 0.000 |
| xl93 | qframe | 0.8839 | 0.0000 | 0.0004 | 0.1157 | 0.003 |
| xl93 | lexicon | 0.6921 | 0.0875 | 0.0054 | 0.2150 | 0.432 |
| xl93 | mode | 0.5221 | 0.0004 | 0.0582 | 0.4193 | 0.140 |
| xl93 | mixed | 0.4714 | 0.0707 | 0.0511 | 0.4068 | 0.299 |

## The held-out sentence mode by key_pos, greedy exact
| rung | key_first (n) | value_first (n) |
| --- | ---: | ---: |
| l45 | 0.7223 (1498) | 0.3280 (1302) |
| xl93 | 0.6976 (1498) | 0.3203 (1302) |

## The held-out sentence mode by qform, greedy exact
| rung | cloze (n) | imperative (n) | inverted (n) | wh (n) |
| --- | ---: | ---: | ---: | ---: |
| l45 | 0.5000 (770) | 0.5488 (840) | 0.5512 (840) | 0.5714 (350) |
| xl93 | 0.5026 (770) | 0.5202 (840) | 0.5345 (840) | 0.5400 (350) |

## The held-out sentence mode by scope_pos, greedy exact
| rung | scope_first (n) | scope_last (n) |
| --- | ---: | ---: |
| l45 | 0.4736 (1176) | 0.5862 (1624) |
| xl93 | 0.4694 (1176) | 0.5603 (1624) |

## The held-out sentence mode by lexicon, greedy exact
| rung | abstract (n) | assembly (n) | clinic (n) | depot (n) | ledger (n) | routing (n) | transit (n) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| l45 | 0.5952 (420) | 0.5276 (434) | 0.5635 (378) | 0.4877 (406) | 0.5688 (378) | 0.4828 (406) | 0.5503 (378) |
| xl93 | 0.5786 (420) | 0.4885 (434) | 0.5582 (378) | 0.4828 (406) | 0.5423 (378) | 0.4778 (406) | 0.5317 (378) |

## The held-out sentence mode, shape against key position
### l45

| shape | key_first | value_first |
| --- | ---: | ---: |
| lookup | 0.9907 (107) | 0.0000 (93) |
| lookup_general | 1.0000 (107) | 1.0000 (93) |
| classify | 0.7944 (107) | 0.9140 (93) |
| inverse | 1.0000 (107) | 0.0000 (93) |
| compose | 0.4112 (107) | 0.0000 (93) |
| iterate | 1.0000 (107) | 0.0000 (93) |
| pair | 1.0000 (107) | 0.9785 (93) |
| priority | 1.0000 (107) | 0.0000 (93) |
| exclusion | 0.4019 (107) | 0.0000 (93) |
| lookup_then_band | 0.5047 (107) | 0.5699 (93) |
| band_then_lookup | 0.6262 (107) | 0.8065 (93) |
| sum_chain | 0.1308 (107) | 0.0000 (93) |
| apply_n | 0.2523 (107) | 0.3226 (93) |
| precedence | 1.0000 (107) | 0.0000 (93) |

### xl93

| shape | key_first | value_first |
| --- | ---: | ---: |
| lookup | 1.0000 (107) | 0.0000 (93) |
| lookup_general | 1.0000 (107) | 1.0000 (93) |
| classify | 0.6636 (107) | 0.7742 (93) |
| inverse | 0.9907 (107) | 0.0000 (93) |
| compose | 0.2150 (107) | 0.0000 (93) |
| iterate | 0.9626 (107) | 0.0000 (93) |
| pair | 1.0000 (107) | 1.0000 (93) |
| priority | 0.9907 (107) | 0.0645 (93) |
| exclusion | 0.2991 (107) | 0.0000 (93) |
| lookup_then_band | 0.3832 (107) | 0.4194 (93) |
| band_then_lookup | 0.5794 (107) | 0.6774 (93) |
| sum_chain | 0.1028 (107) | 0.0000 (93) |
| apply_n | 0.5794 (107) | 0.5484 (93) |
| precedence | 1.0000 (107) | 0.0000 (93) |

## What each rung did to its own training file
| rung | peak lr | loss at 8,000 | at 15,000 | at 30,000 | peak GB |
| --- | ---: | ---: | ---: | ---: | ---: |
| l45 | 0.0004 | 0.0843 | 0.0417 | 0.0126 | n/a |
| xl93 | 0.00032 | 0.1009 | 0.0525 | 0.0182 | 20.69 |

## The three frame splits
| split | data | withheld question frame | withheld lexicon | withheld statement mode | training frames |
| --- | --- | --- | --- | --- | ---: |
| l45 | `data/norm` | band, every 8th | signal | relative_clause | 490 |
| c45 | `data/normC` | wh | signal | relative_clause | 420 |
| b45 | `data/normB` | band, every 8th | signal | table_row | 490 |

## Key position inside every frame group
| checkpoint | frame group | key_first | value_first |
| --- | --- | ---: | ---: |
| l45 | train | 0.9264 (1386) | 0.9158 (1414) |
| l45 | lexicon | 0.8245 (1470) | 0.7992 (1330) |
| l45 | mode | 0.7223 (1498) | 0.3280 (1302) |
| l45 | mixed | 0.7345 (1190) | 0.4180 (1610) |
| xl93 | train | 0.8918 (1386) | 0.8861 (1414) |
| xl93 | lexicon | 0.6721 (1470) | 0.7143 (1330) |
| xl93 | mode | 0.6976 (1498) | 0.3203 (1302) |
| xl93 | mixed | 0.5328 (1190) | 0.4261 (1610) |

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

## Records against the reports beside them
| report | written | records | newest record | ok |
| --- | --- | ---: | --- | --- |
| l45 | 2026-08-31 17:41 | 10 | 2026-08-31 17:41 | yes |
| xl93 | 2026-08-31 19:59 | 10 | 2026-08-31 19:59 | yes |
| ftl45 | 2026-08-31 20:01 | 10 | 2026-08-31 20:01 | yes |
| ftxl93 | 2026-08-31 20:06 | 10 | 2026-08-31 20:06 | yes |
