A general model of this size does not acquire a new operation from one page,
and this is the first externally validated result the project has.

LFM2.5-350M read the same definition page the project's own reader was given,
under the formulation that scored best of the five tried, and answered 850
questions at 0.2459 strict against its own measured chance floor of 0.3085. It
names none of the candidate answers at all on 0.4965 of the items. Split by
operation family, and these are never pooled, it is above its own floor on two
of the four and below it on two: 0.4364 against a 0.3735 floor at n=110 and
0.3600 against 0.3567 at n=25, then 0.1935 against 0.3086 at n=310 and 0.2272
against 0.2879 at n=405. The second of the two above-floor cells sits a third
of a point over its floor on 25 items and carries no weight. The two families
with the item counts to say anything are both below chance.

That is not a statement about these models being weak. On 26 ordinary factual,
numeric and commonsense questions put through the same harness and graded by
the same function, the same checkpoint scores 0.5769 against a 0.2500 floor
where this project's reader scores 0.0000. That 0.0000 needs its states beside
it. Of the 26 items handed to the reader, 7 produced a structure the
interpreter ran, 17 came back malformed and 2 were refused, so the cell is
mostly items the reader could not be prompted on rather than items it answered
wrongly. LFM2.5-350M wins the general axis, and it wins it on a comparison
whose losing arm rests on 7 scored answers. The two numbers belong beside each
other, because a report carrying only the first would be advocacy.

The retrieval lane adds a second finding, and an earlier version of this
paragraph had it backwards. On MMLU the project's reader emits the retrieval
token on 102 of 400 items, a rate of 0.2550 with a 95 percent interval of
[0.215, 0.300], and chunks reach its trace on 88 of those. What was once read
as evidence of near silence is the spend: 73 live Exa searches beside 255 cache
hits, and a cache hit is invisible to a spend counter by construction, so the
cost of a retrieval cell says nothing about the rate at which it was asked for.
The reader asks on about one item in four. What the paired arms show is that
asking buys nothing. The cell scores 0.0100 with a live web index and 0.0100
with retrieval unavailable, 4 of 400 either way, and on the 88 items where a
chunk entered the trace the reader named an option zero times with pages and
zero times without. The failure is downstream of the request, not upstream of
it.

What the result does not do is settle the architecture question. The library
system's 1.0000 comes from an exact interpreter running a parsed definition,
and the comparison here is against a model that was never built to parse one.
The finding is narrower than the thesis and worth exactly what it says: the
capability is not free at this scale, and something has to supply it.

<!--checks-->

The block below binds every numeral in the prose above to the record file it
came from. `src/extern/md.py` recomputes each one at build time and refuses to
write `LIQUID.md` if any of them disagrees, if a numeral appears above that is
not listed here, or if a listed value no longer appears above. It is not
spliced into the generated document.

```verdict-checks
# value    artifact                                                    field or derived metric
0.2459     results/extern/report.json                                  full.lfm350m_worked_p1.all.strict
850        results/extern/report.json                                  full.lfm350m_worked_p1.all.n
0.3085     results/extern/report.json                                  full.lfm350m_worked_p1.all.floor
0.4965     results/extern/report.json                                  full.lfm350m_worked_p1.all.none
0.4364     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a2c1.strict
0.3735     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a2c1.floor
110        results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a2c1.n
0.3600     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a2c2.strict
0.3567     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a2c2.floor
25         results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a2c2.n
0.1935     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a3c1.strict
0.3086     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a3c1.floor
310        results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a3c1.n
0.2272     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a3c2.strict
0.2879     results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a3c2.floor
405        results/extern/report.json                                  full.lfm350m_worked_p1.by_family.a3c2.n
0.5769     results/extern/report.json                                  general.lfm350m.all.strict
26         results/extern/report.json                                  general.lfm350m.all.n
0.2500     results/extern/report.json                                  general.lfm350m.all.floor
0.0000     results/extern/report.json                                  ours_general.strict
7          results/extern/report.json                                  ours_general.states.ran
17         results/extern/report.json                                  ours_general.states.malformed
2          results/extern/report.json                                  ours_general.states.refused
102        results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #count(web_greedy,emitted_retrieve)
400        results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    n_items
0.2550     results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #rate(web_greedy,emitted_retrieve)
0.215      results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #wilson_lo(web_greedy,emitted_retrieve)
0.300      results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #wilson_hi(web_greedy,emitted_retrieve)
88         results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #count(web_greedy,context_entered)
73         results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    live_searches
255        results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    cache_hits
0.0100     results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #rate(web_greedy,strict)
0.0100     results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #rate(none_greedy,strict)
4          results/extern/bench/cell2_ours_mmlu_retrieval_n400.json    #count(none_greedy,strict)
1.0000     results/extern/ours_oneshot.json                            a3c2.L
95         literal                                                     the confidence level of the Wilson interval, not a measurement
```
