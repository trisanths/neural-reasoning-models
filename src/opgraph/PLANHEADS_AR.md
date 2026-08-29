# The autoregressive plan heads, P1 and P2

P1 writes a plan in the page's own operator symbols. P2 writes the same plan in
dedicated opcode tokens, one token per operator. Both decode causally through
the pretrained `lm_head`, both add no new parameters, and both are trained on
plans of at most three steps. Everything else in `src/opgraph/PLANHEADS.md`
holds: same base checkpoint, same reader, same worlds and seeds, same questions,
same executor, same optimizer steps, same sequences per step, same held-out
sets.

Depths one to three are in distribution. Everything past three, and all of
novel composition, is extrapolation.

## What is new here, in one paragraph

Neither head degrades with depth. Both write a plan of exactly three steps at
almost every question depth from four to thirty two, on 150 of 150 items, and
the plan is well typed and parses. The single exception is P1 at depth six,
where it writes one step. Over 34,200 scored items past the holdout, at
three temperatures and both page wordings, no plan longer than three steps was
ever produced. The compute spent is the same at depth thirty two as at depth
three: 28 forward passes and 27 generated tokens for P1, 31 and 30 for P2. So
the depth curve past three is not measuring composition capacity. It is
measuring a length prior that sits at exactly the maximum plan length in
training, and the same prior turns up again on the breadth axis as a cap on the
number of arguments a single step may take.

## The grid, and where it stops

Sequential depth runs 1 2 3 4 5 6 8 12 16 32. Thirty two is the ceiling of the
harness, not a choice: `plan.MAX_STEPS` is 32 and `parse_plan` rejects more than
`MAX_STEPS + 1` chunks, so a gold depth 32 plan fills the parser exactly and a
gold depth 40 plan raises `plan too long` before any head is involved. The world
generator itself has no limit; it produced depth 40 items fine. Nothing past 32
can be scored without changing the executor, so the extrapolation stops there
and 32 is reported as reached rather than as a target that was missed.

The generation cap is 320 tokens for both heads, raised from the shared default
of 160. A gold depth 32 plan costs up to 260 tokens in P1's spelling and 292 in
P2's, so a cap of 160 would have truncated the only correct answer and the deep
cells would have been reporting the cap. At 320, `at_generation_cap` is 0 in
every cell of the grid for both heads, so the cap never binds and no number
below is a truncation artifact.

## Harness check

`oracle_both` supplies the gold plan and the gold operators, so the executor
answers alone. `oracle_both_roundtrip` pushes the same gold plan through the
head's own plan representation and back first, which for P2 means the opcode
spelling and the mapping back.

| head | condition | cells | items | min accuracy over cells |
|---|---|---|---|---|
| p1 | oracle_both | 34 | 5100 | 1.0000 |
| p1 | oracle_both@para | 34 | 5100 | 1.0000 |
| p1 | oracle_both_roundtrip | 34 | 5100 | 1.0000 |
| p1 | oracle_both_roundtrip@para | 34 | 5100 | 1.0000 |
| p2 | oracle_both | 34 | 5100 | 1.0000 |
| p2 | oracle_both@para | 34 | 5100 | 1.0000 |
| p2 | oracle_both_roundtrip | 34 | 5100 | 1.0000 |
| p2 | oracle_both_roundtrip@para | 34 | 5100 | 1.0000 |

Both are 1.000 in all 34 cells of the grid, for both heads and both page
wordings. That is 40,800 gold executions with no failure, including every cell
at depth 32.

The reported forward count is checked against the model rather than against the
bookkeeping that produced it. `ForwardCounter` hooks `model.tok_emb`, which
every path through the backbone touches once per stack invocation.

| head | run | reported forward passes | observed at the model | match |
|---|---|---|---|---|
| p1 | p1@T0 | 12 | 12 | True |
| p1 | p1@T0.8 | 12 | 12 | True |
| p1 | p1@T1 | 12 | 12 | True |
| p1 | p1@T0@para | 12 | 12 | True |
| p1 | p1@T0.8@para | 12 | 12 | True |
| p1 | p1@T1@para | 12 | 12 | True |
| p2 | p2@T0 | 13 | 13 | True |
| p2 | p2@T0.8 | 13 | 13 | True |
| p2 | p2@T1 | 13 | 13 | True |
| p2 | p2@T0@para | 13 | 13 | True |
| p2 | p2@T0.8@para | 13 | 13 | True |
| p2 | p2@T1@para | 13 | 13 | True |

## Training, and the holdout it asserts

| head | steps | batch | worlds | lr | max_len | seed | training plans | plan depth histogram | max distinct operator symbols | induction seqs dropped | plan seqs dropped |
|---|---|---|---|---|---|---|---|---|---|---|---|
| p1 | 8000 | 32 | 40000 | 2e-05 | 1024 | 17 | 160000 | {"1": 93126, "2": 33154, "3": 33720} | 1 | 0 | 0 |
| p2 | 8000 | 32 | 40000 | 2e-05 | 1024 | 17 | 160000 | {"1": 93126, "2": 33154, "3": 33720} | 1 | 0 | 0 |

The holdout is asserted over the whole plan pool before the first optimizer
step. No training plan is deeper than three steps and no training plan uses two
distinct induced operator symbols. Both heads drew the same 160,000 plans in the
same order. The depth histogram matters for reading everything below: 58 percent
of training plans are one step long and none is longer than three.

No sequence was dropped for exceeding `max_len` in either arm, so the two heads
took the same number of sequences per optimizer step.

## Convergence check

The smoke run left an open question: at a matched step count an arm can look
worse because it is further from convergence. For P1 against P2 that risk is
small, since both reuse the pretrained `lm_head` and write a similar number of
tokens, but it is checked rather than assumed. Each head was trained twice, at
4000 and at 8000 steps, both under a full cosine schedule, so the shorter run is
an annealed run and not a prefix of the longer one.

| head | budget | wording | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p1 | 4000 steps | original | 1.000 | 1.000 | 1.000 | 0.020 | 0.027 | 0.027 | 0.020 | 0.020 | 0.013 | 0.027 |
| p1 | 4000 steps | paraphrase | 0.820 | 0.300 | 0.253 | 0.020 | 0.020 | 0.033 | 0.013 | 0.007 | 0.013 | 0.013 |
| p1 | 8000 steps | original | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.013 | 0.027 | 0.020 |
| p1 | 8000 steps | paraphrase | 0.700 | 0.213 | 0.193 | 0.020 | 0.027 | 0.007 | 0.013 | 0.007 | 0.007 | 0.007 |
| p2 | 4000 steps | original | 1.000 | 1.000 | 1.000 | 0.027 | 0.033 | 0.027 | 0.020 | 0.007 | 0.013 | 0.020 |
| p2 | 4000 steps | paraphrase | 0.873 | 0.387 | 0.393 | 0.033 | 0.013 | 0.027 | 0.013 | 0.007 | 0.000 | 0.013 |
| p2 | 8000 steps | original | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 | 8000 steps | paraphrase | 0.687 | 0.293 | 0.327 | 0.013 | 0.027 | 0.027 | 0.007 | 0.000 | 0.007 | 0.013 |

Doubling the budget does not move the cliff, does not move the floor, and does
not change the shape. On the paraphrased wording it makes both heads worse, which
is the expected sign of a longer fit to the training page prose. The comparison
below is therefore about the plan representation and not about how far from
convergence each arm sits.

## Sequential depth, original page wording

Greedy decoding.

| head, condition | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|
| p1 plan_execute | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.013 | 0.027 | 0.020 |
| p1 oracle_ops | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.013 | 0.027 | 0.020 |
| p1 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_ops | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

Sampled at temperature 0.8.

| head, condition | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|
| p1 plan_execute | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.007 | 0.027 | 0.027 |
| p1 oracle_ops | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.007 | 0.027 | 0.027 |
| p1 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_ops | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

Sampled at temperature 1.0.

| head, condition | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|
| p1 plan_execute | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.007 | 0.027 | 0.020 |
| p1 oracle_ops | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.007 | 0.027 | 0.020 |
| p1 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_ops | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

The parenthesised family, which is a different tree shape over the same single
operator, gives the same picture.

| head, condition | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|
| p1 plan_execute | 1.000 | 1.000 | 0.040 | 0.040 | 0.033 | 0.007 | 0.000 | 0.020 | 0.020 |
| p1 oracle_ops | 1.000 | 1.000 | 0.040 | 0.040 | 0.033 | 0.007 | 0.000 | 0.020 | 0.020 |
| p1 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 1.000 | 1.000 | 0.053 | 0.027 | 0.040 | 0.020 | 0.000 | 0.047 | 0.000 |
| p2 oracle_ops | 1.000 | 1.000 | 0.053 | 0.027 | 0.040 | 0.020 | 0.000 | 0.047 | 0.000 |
| p2 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

The following hold at every depth on this grid.

`plan_execute` equals `oracle_ops` to three decimals in every sequential cell,
so gold operators change nothing and induction is not the sequential bottleneck.
This reproduces the earlier finding and extends it from depth eight to depth
thirty two.

`oracle_plan` is 1.000 at every depth from one to thirty two, under both heads,
at all three temperatures. Conditional on a correct plan the 350M substrate
induces the operators itself and the executor runs them, with no depth
degradation this grid can see, four times further out than before.

Greedy and sampled agree. The policy is close to deterministic on this task, and
the sampled columns exist so a greedy zero is never reported alone.

## The shape

| head | condition | temp | wording | shape | cliff D | plateau | floor | cliff SSE | geometric r | geometric SSE | first d below 0.5 | first d below 0.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p1 | plan_execute | T=0 | original | cliff at 3 | 3 | 1.000 | 0.021 | 0.0003 | 0.902 | 2.2825 | 4 | 4 |
| p1 | oracle_plan | T=0 | original | flat | 1 | 1.000 | 1.000 | 0.0000 | 1.000 | 0.0000 | never | never |
| p1 | plan_execute | T=0.8 | original | cliff at 3 | 3 | 1.000 | 0.021 | 0.0005 | 0.907 | 2.3333 | 4 | 4 |
| p1 | oracle_plan | T=0.8 | original | flat | 1 | 1.000 | 1.000 | 0.0000 | 1.000 | 0.0000 | never | never |
| p1 | plan_execute | T=1 | original | cliff at 3 | 3 | 1.000 | 0.020 | 0.0004 | 0.900 | 2.3134 | 4 | 4 |
| p1 | oracle_plan | T=1 | original | flat | 1 | 1.000 | 1.000 | 0.0000 | 1.000 | 0.0000 | never | never |
| p1 | plan_execute | T=0 | paraphrase | cliff at 1 | 1 | 0.700 | 0.055 | 0.0573 | 0.890 | 0.4370 | 2 | 4 |
| p1 | oracle_plan | T=0 | paraphrase | cliff at 1 | 1 | 0.700 | 0.428 | 0.0114 | 0.989 | 0.0556 | 2 | never |
| p1 | plan_execute | T=0.8 | paraphrase | cliff at 1 | 1 | 0.700 | 0.055 | 0.0573 | 0.890 | 0.4370 | 2 | 4 |
| p1 | oracle_plan | T=0.8 | paraphrase | cliff at 1 | 1 | 0.700 | 0.428 | 0.0114 | 0.989 | 0.0556 | 2 | never |
| p1 | plan_execute | T=1 | paraphrase | cliff at 1 | 1 | 0.700 | 0.055 | 0.0573 | 0.890 | 0.4370 | 2 | 4 |
| p1 | oracle_plan | T=1 | paraphrase | cliff at 1 | 1 | 0.700 | 0.428 | 0.0114 | 0.989 | 0.0556 | 2 | never |
| p2 | plan_execute | T=0 | original | cliff at 3 | 3 | 1.000 | 0.028 | 0.0010 | 0.906 | 2.1954 | 4 | 4 |
| p2 | oracle_plan | T=0 | original | flat | 1 | 1.000 | 1.000 | 0.0000 | 1.000 | 0.0000 | never | never |
| p2 | plan_execute | T=0.8 | original | cliff at 3 | 3 | 1.000 | 0.028 | 0.0010 | 0.906 | 2.1954 | 4 | 4 |
| p2 | oracle_plan | T=0.8 | original | flat | 1 | 1.000 | 1.000 | 0.0000 | 1.000 | 0.0000 | never | never |
| p2 | plan_execute | T=1 | original | cliff at 3 | 3 | 1.000 | 0.028 | 0.0010 | 0.906 | 2.1954 | 4 | 4 |
| p2 | oracle_plan | T=1 | original | flat | 1 | 1.000 | 1.000 | 0.0000 | 1.000 | 0.0000 | never | never |
| p2 | plan_execute | T=0 | paraphrase | cliff at 3 | 3 | 0.436 | 0.013 | 0.0958 | 0.906 | 0.4761 | 2 | 4 |
| p2 | oracle_plan | T=0 | paraphrase | flat | 1 | 0.680 | 0.618 | 0.0027 | 0.999 | 0.0058 | never | never |
| p2 | plan_execute | T=0.8 | paraphrase | cliff at 3 | 3 | 0.433 | 0.013 | 0.0977 | 0.906 | 0.4739 | 2 | 4 |
| p2 | oracle_plan | T=0.8 | paraphrase | flat | 1 | 0.680 | 0.618 | 0.0027 | 0.999 | 0.0058 | never | never |
| p2 | plan_execute | T=1 | paraphrase | cliff at 3 | 3 | 0.436 | 0.013 | 0.0958 | 0.906 | 0.4761 | 2 | 4 |
| p2 | oracle_plan | T=1 | paraphrase | flat | 1 | 0.680 | 0.618 | 0.0027 | 0.999 | 0.0058 | never | never |

The cliff and the geometric decay are fitted to the same points. On the original
wording the cliff wins on residual by a factor of 7,600 for P1, 0.0003 against
2.2825, and by 2,200 for P2, 0.0010 against 2.1954. Both heads are plateau at
1.000 through depth three, then a floor of 0.021 and 0.028 that does not decline
further out to depth thirty two.

That flat floor is worth stating plainly. Accumulating per step error produces a
curve that keeps falling. This one stops falling at depth four and stays there:
P1 scores 0.020 at depth four and 0.020 at depth thirty two, P2 0.040 and 0.033,
with n = 150 in each cell. Everything past depth four costs nothing more because
there is nothing left to cost. What happens at depth four is a switch flipping
rather than a decay starting, and the two residuals say so.

## What the head actually writes

The step count separates two failures that bare accuracy folds together. A head
that writes three steps at depth sixteen has stopped early. A head that writes
sixteen wrong steps has planned wrongly.

| head | question depth | gold plan steps | mean steps written | steps written, count |
|---|---|---|---|---|
| p1 | 1 | 1 | 1.000 | 1:150 |
| p1 | 2 | 2 | 2.000 | 2:150 |
| p1 | 3 | 3 | 3.000 | 3:150 |
| p1 | 4 | 4 | 3.000 | 3:150 |
| p1 | 5 | 5 | 3.000 | 3:150 |
| p1 | 6 | 6 | 1.192 | 1:132, 3:14 |
| p1 | 8 | 8 | 3.000 | 3:150 |
| p1 | 12 | 12 | 3.000 | 3:150 |
| p1 | 16 | 16 | 3.000 | 3:150 |
| p1 | 32 | 32 | 3.000 | 3:150 |
| p2 | 1 | 1 | 1.000 | 1:150 |
| p2 | 2 | 2 | 2.000 | 2:150 |
| p2 | 3 | 3 | 3.000 | 3:150 |
| p2 | 4 | 4 | 3.000 | 3:150 |
| p2 | 5 | 5 | 3.000 | 3:150 |
| p2 | 6 | 6 | 3.000 | 3:150 |
| p2 | 8 | 8 | 3.000 | 3:150 |
| p2 | 12 | 12 | 3.000 | 3:150 |
| p2 | 16 | 16 | 3.000 | 3:150 |
| p2 | 32 | 32 | 3.000 | 3:150 |

Both heads write exactly three steps at every question depth from four to thirty
two, on 150 of 150 items, with one exception: P1 at depth six writes a one step
plan for 132 of 150 items. That anomaly is real and is not smoothed over; it has
no counterpart in P2 and no explanation here.

Sampling does not change it.

| head | temperature | wording | items at question depth above three | items whose plan had more than three steps | rate | longest plan written, in steps |
|---|---|---|---|---|---|---|
| p1 | T=0 | original | 2850 | 0 | 0.0000 | 3 |
| p1 | T=0 | paraphrase | 2850 | 0 | 0.0000 | 3 |
| p1 | T=0.8 | original | 2850 | 0 | 0.0000 | 3 |
| p1 | T=0.8 | paraphrase | 2850 | 0 | 0.0000 | 3 |
| p1 | T=1 | original | 2850 | 0 | 0.0000 | 3 |
| p1 | T=1 | paraphrase | 2850 | 0 | 0.0000 | 3 |
| p2 | T=0 | original | 2850 | 0 | 0.0000 | 3 |
| p2 | T=0 | paraphrase | 2850 | 0 | 0.0000 | 3 |
| p2 | T=0.8 | original | 2850 | 0 | 0.0000 | 3 |
| p2 | T=0.8 | paraphrase | 2850 | 0 | 0.0000 | 3 |
| p2 | T=1 | original | 2850 | 0 | 0.0000 | 3 |
| p2 | T=1 | paraphrase | 2850 | 0 | 0.0000 | 3 |

Over 2,850 items per cell, at temperatures 0.0, 0.8 and 1.0, on both page
wordings, on the sequential, parenthesised and novel families together, the
longest plan either head ever wrote is three steps. Not one item in 34,200
produced a fourth. The horizon is not an argmax artifact.

Here is what that looks like.

```
question depth 3
  question  Evaluate 12 # 8 # 6 # 10.
  gold      t1 = # 12 8 ; t2 = # t1 6 ; t3 = # t2 10 ; ans t3
  p1 wrote   t1 = # 12 8 ; t2 = # t1 6 ; t3 = # t2 10 ; ans t3
  p2 wrote   t1 = # 12 8 ; t2 = # t1 6 ; t3 = # t2 10 ; ans t3

question depth 4
  question  Evaluate 1 # 7 # 5 # 5 # 2.
  gold      t1 = # 1 7 ; t2 = # t1 5 ; t3 = # t2 5 ; t4 = # t3 2 ; ans t4
  p1 wrote   t1 = # 1 7 ; t2 = # t1 5 ; t3 = # t2 2 ; ans t3
  p2 wrote   t1 = # 1 7 ; t2 = # t1 5 ; t3 = # t2 2 ; ans t3

question depth 8
  question  Evaluate 3 # 8 # 12 # 2 # 2 # 9 # 5 # 2 # 4.
  gold      t1 = # 3 8 ; t2 = # t1 12 ; t3 = # t2 2 ; t4 = # t3 2 ; t5 = # t4 9 ; t6 = # t5 5 ; t7 = # t6 2 ; t8 = # t7 4 ; ans t8
  p1 wrote   t1 = # 3 8 ; t2 = # t1 12 ; t3 = # t2 4 ; ans t3
  p2 wrote   t1 = # 3 8 ; t2 = # t1 2 ; t3 = # t2 4 ; ans t3

question depth 32
  question  Evaluate 4 / 5 / 12 / 2 / 11 / 10 / 3 / 5 / 3 / 4 / 4 / 11 / 10 / 5 / 7 / 9 / 10 / 4 / 5 / 3 / 12 / 3 / 7 / 11 / 7 / 7 / 9 / 12 / 5 / 11 / 3 / 8 / 3.
  gold      t1 = / 4 5 ; t2 = / t1 12 ; t3 = / t2 2 ; t4 = / t3 11 ; t5 = / t4 10 ; t6 = / t5 3 ; t7 = / t6 5 ; t8 = / t7 3 ; t9 = / t8 4 ; t10 = / t9 4 ; t11 = / t10 11 ; t12 = / t11 10 ; t13 = / t12 5 ; t14 = / t13 7 ; t15 = / t14 9 ; t16 = / t15 10 ; t17 = / t16 4 ; t18 = / t17 5 ; t19 = / t18 3 ; t20 = / t19 12 ; t21 = / t20 3 ; t22 = / t21 7 ; t23 = / t22 11 ; t24 = / t23 7 ; t25 = / t24 7 ; t26 = / t25 9 ; t27 = / t26 12 ; t28 = / t27 5 ; t29 = / t28 11 ; t30 = / t29 3 ; t31 = / t30 8 ; t32 = / t31 3 ; ans t32
  p1 wrote   t1 = / 4 5 ; t2 = / t1 12 ; t3 = / t2 3 ; ans t3
  p2 wrote   t1 = / 4 5 ; t2 = / t1 12 ; t3 = / t2 3 ; ans t3
```

At depth four both heads consume the first two operands and then reach for the
last one, closing in three steps. At depth thirty two, given a chain of thirty
three operands, both write the identical plan: the first two operands, then the
final operand, then `ans`. The head is reading the question, since it picks the
correct last operand out of thirty three, and it is applying a three step
template to it. It is not losing track partway through a long plan; it never
starts one.

## Sequential depth, paraphrased page wording

The plan prompt contains the operator signature line and the question, never the
page text. The page wording reaches these heads only through induction, and the
question text is generated from the world's glyphs, which style 1 does not
change. So `oracle_ops`, which supplies gold operators, should see the same input
under both wordings, and every paraphrase effect below should be an induction
effect. That is a claim about the harness, so it is checked.

| head | temperature | cells compared | largest accuracy difference between wordings |
|---|---|---|---|
| p1 | T=0 | 34 | 0.0000 |
| p1 | T=0.8 | 34 | 0.0000 |
| p1 | T=1 | 34 | 0.0000 |
| p2 | T=0 | 34 | 0.0000 |
| p2 | T=0.8 | 34 | 0.0000 |
| p2 | T=1 | 34 | 0.0000 |

The largest accuracy difference between the two wordings under `oracle_ops` is
0.000 over every cell of the grid, for both heads at all three temperatures.

| head, condition | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|
| p1 plan_execute | 0.700 | 0.213 | 0.193 | 0.020 | 0.027 | 0.007 | 0.013 | 0.007 | 0.007 | 0.007 |
| p1 oracle_ops | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.013 | 0.027 | 0.020 |
| p1 oracle_plan | 0.700 | 0.493 | 0.447 | 0.420 | 0.473 | 0.393 | 0.413 | 0.427 | 0.413 | 0.373 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 0.687 | 0.293 | 0.327 | 0.013 | 0.027 | 0.027 | 0.007 | 0.000 | 0.007 | 0.013 |
| p2 oracle_ops | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| p2 oracle_plan | 0.680 | 0.593 | 0.620 | 0.647 | 0.607 | 0.607 | 0.613 | 0.647 | 0.620 | 0.607 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

| head | wording | worlds | pages | page parse rate | gold operators | induced operators | exact text rate | behavioural match rate |
|---|---|---|---|---|---|---|---|---|
| p1 | original | 1650 | 6600 | 0.999 | 9897 | 9887 | 0.954 | 0.954 |
| p1 | paraphrase | 1650 | 6600 | 0.877 | 9897 | 8673 | 0.453 | 0.486 |
| p2 | original | 1650 | 6600 | 1.000 | 9897 | 9897 | 0.954 | 0.954 |
| p2 | paraphrase | 1650 | 6600 | 0.833 | 9897 | 8351 | 0.412 | 0.436 |

Induction on the original wording is identical between the heads at 0.954 exact
text, which is what a matched pair should give. On the paraphrase it falls to
0.453 for P1 and 0.412 for P2, and page parse rate falls to 0.877 and 0.833.
That difference between the heads is not about plan representation. The plan
objective is the only thing that differs between the two fine tunes, but it
moves the shared backbone, and induction rides on the shared backbone.

`oracle_plan` on the paraphrase is flat from depth two out to depth thirty two,
between 0.373 and 0.493 for P1 and between 0.593 and 0.647 for P2, against a
gold plan at every one of those depths. So the depth flatness of
`oracle_plan` survives the wording change; what the wording change costs is a
constant, and the constant is induction.

## Novel composition

Two operator symbols, each defined alone on its own page, never trained
together. The training holdout asserts that no training plan uses two distinct
induced symbols.

| head, condition | 2 | 3 | 4 | 5 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|
| p1 plan_execute | 0.027 | 0.007 | 0.020 | 0.007 | 0.000 | 0.000 | 0.000 |
| p1 oracle_ops | 0.027 | 0.007 | 0.020 | 0.007 | 0.000 | 0.000 | 0.000 |
| p1 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 0.013 | 0.013 | 0.000 | 0.000 | 0.000 | 0.007 | 0.013 |
| p2 oracle_ops | 0.013 | 0.013 | 0.000 | 0.000 | 0.000 | 0.007 | 0.013 |
| p2 oracle_plan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

```
question depth 2
  question  Evaluate 5 ^ (7 > 6).
  gold      t1 = > 7 6 ; t2 = ^ 5 t1 ; ans t2
  p1 wrote   t1 = > 7 6 ; t2 = > 5 t1 ; ans t2
  p2 wrote   t1 = ^ 7 6 ; t2 = ^ 5 t1 ; ans t2

question depth 3
  question  Evaluate ((10 ^ 3) > 12) > 3.
  gold      t1 = ^ 10 3 ; t2 = > t1 12 ; t3 = > t2 3 ; ans t3
  p1 wrote   t1 = ^ 10 3 ; t2 = ^ t1 12 ; t3 = ^ t2 3 ; ans t3
  p2 wrote   t1 = ^ 10 3 ; t2 = ^ t1 12 ; t3 = ^ t2 3 ; ans t3

question depth 6
  question  Evaluate ((8 ^ 3) > 1) ^ (7 ^ ((10 ^ 1) ^ 7)).
  gold      t1 = ^ 8 3 ; t2 = > t1 1 ; t3 = ^ 10 1 ; t4 = ^ t3 7 ; t5 = ^ 7 t4 ; t6 = ^ t2 t5 ; ans t6
  p1 wrote   t1 = ^ 10 1 ; t2 = ^ 7 t1 ; t3 = ^ t2 7 ; ans t3
  p2 wrote   t1 = ^ 8 3 ; t2 = ^ t1 7 ; t3 = ^ t2 7 ; ans t3
```

`oracle_plan` is 1.000 at every novel depth from two to twelve under both heads,
so induction and execution both handle these worlds. `plan_execute` is 0.027 and
below. The whole of novel composition fails in plan construction.

The mechanism is visible in the diagnostics. At novel depth two P1 writes a two
step plan on every item, gets the first step right on 0.927 of them, and scores
an exact gold plan rate of 0.000. It writes the right number of steps and then
uses the first step's operator again for the second. Each head picks one symbol
and commits to it for the whole plan, which is exactly what a head trained only
on single symbol plans would do.

| metric | 2 | 3 | 4 | 5 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|
| acc | 0.027 | 0.007 | 0.020 | 0.007 | 0.000 | 0.000 | 0.000 |
| parse_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| well_typed_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.980 | 0.993 |
| exact_gold_plan_rate | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| parsed_but_wrong_rate | 0.973 | 0.993 | 0.980 | 0.993 | 1.000 | 1.000 | 1.000 |
| emitted_steps_mean | 2.000 | 3.000 | 2.520 | 3.000 | 3.000 | 3.000 | 3.000 |
| emitted_steps_eq_gold_rate | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| prefix_of_gold_rate | 0.000 | 0.000 | 0.147 | 0.007 | 0.007 | 0.000 | 0.000 |
| first_step_correct_rate | 0.927 | 0.800 | 0.727 | 0.640 | 0.513 | 0.387 | 0.393 |
| matched_prefix_len_mean | 0.927 | 1.133 | 0.873 | 0.740 | 0.587 | 0.413 | 0.473 |
| fwd_passes_mean | 20.0 | 28.0 | 24.0 | 27.9 | 28.0 | 28.0 | 27.9 |
| position_evals_mean | 66.5 | 78.1 | 77.6 | 85.2 | 88.9 | 96.2 | 110.8 |
| gen_tokens_mean | 19.0 | 27.0 | 23.0 | 26.9 | 27.0 | 27.0 | 26.9 |
| at_generation_cap | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| n | 150 | 150 | 150 | 150 | 150 | 150 | 150 |

| metric | 2 | 3 | 4 | 5 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|
| acc | 0.013 | 0.013 | 0.000 | 0.000 | 0.000 | 0.007 | 0.013 |
| parse_rate | 1.000 | 1.000 | 0.993 | 0.893 | 0.973 | 1.000 | 1.000 |
| well_typed_rate | 1.000 | 1.000 | 0.993 | 0.893 | 0.973 | 1.000 | 1.000 |
| exact_gold_plan_rate | 0.000 | 0.007 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| parsed_but_wrong_rate | 0.987 | 0.987 | 0.993 | 0.893 | 0.973 | 0.993 | 0.987 |
| emitted_steps_mean | 2.000 | 3.000 | 2.859 | 2.149 | 2.993 | 3.000 | 3.000 |
| emitted_steps_eq_gold_rate | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| prefix_of_gold_rate | 0.000 | 0.007 | 0.013 | 0.100 | 0.000 | 0.000 | 0.000 |
| first_step_correct_rate | 0.480 | 0.707 | 0.633 | 0.553 | 0.507 | 0.487 | 0.353 |
| matched_prefix_len_mean | 0.480 | 1.000 | 0.718 | 0.731 | 0.610 | 0.507 | 0.400 |
| fwd_passes_mean | 22.0 | 31.0 | 29.6 | 23.3 | 30.6 | 30.8 | 30.7 |
| position_evals_mean | 95.8 | 108.4 | 110.5 | 107.8 | 118.8 | 126.2 | 140.9 |
| gen_tokens_mean | 21.0 | 30.0 | 28.6 | 22.2 | 29.6 | 29.8 | 29.8 |
| at_generation_cap | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| n | 150 | 150 | 150 | 150 | 150 | 150 | 150 |

## Relational breadth

The registered prediction is that breadth does not move, because it fails at
induction. On the accuracy numbers the prediction holds.

| head, condition | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| p1 plan_execute | 1.000 | 1.000 | 1.000 | 0.300 | 0.240 | 0.133 |
| p1 oracle_ops | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| p1 oracle_plan | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| p1 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| p2 plan_execute | 1.000 | 1.000 | 1.000 | 0.433 | 0.280 | 0.173 |
| p2 oracle_ops | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| p2 oracle_plan | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| p2 oracle_both | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

n = [150] per cell.

`oracle_plan` is 1.000 at breadth one to three and 0.000 at breadth four and
above, while `oracle_both` is 1.000 throughout. Breadth did not move. Neither
head touched it.

The localisation underneath that number needs correcting, and this is the part
that was not predicted. `oracle_ops` hands the head a perfect operator table and
is also 0.000 at breadth four and above, on 150 of 150 items, with every failure
recorded as an execution error rather than a wrong value. Planning fails at
breadth too, independently of induction.

```
question depth 3
  question  An application has a brapyr value of 56. It is marked nakfex. It is not marked zelovi. It is marked misol. What is its adjusted value?
  gold      t1 = score 56 true false true ; ans t1
  p1 wrote   t1 = score 56 true false true ; ans t1
  p2 wrote   t1 = score 56 true false true ; ans t1

question depth 4
  question  An application has a zelqen value of 57. It is marked fexmi. It is marked wrenovi. It is marked dribra. It is not marked tezpyr. What is its adjusted value?
  gold      t1 = score 57 true true true false ; ans t1
  p1 wrote   t1 = score 57 true true true ; ans t1
  p2 wrote   t1 = score 57 true true false ; ans t1

question depth 6
  question  An application has a kami value of 40. It is marked oviyuk. It is not marked nakbra. It is not marked naksol. It is marked vormi. It is not marked qenwren. It is not marked solsol. What is its adjusted value?
  gold      t1 = score 40 true false false true false false ; ans t1
  p1 wrote   t1 = score 40 true false false ; ans t1
  p2 wrote   t1 = score 40 true false false ; ans t1
```

Training draws breadth from one, two or three, so the widest `score` call a head
ever saw takes a value and three flags. At breadth four the question lists four
flags and both heads write three. At breadth six it lists six and both heads
still write three. This is the same length prior as the three step cap, applied
to argument count instead of step count.

Induction truncates in the same place. The head's four argument call is scored
well typed on 1.000 of items at breadth four, and well typed is an exact arity
match, so the induced `score` operator has arity four there as well. That is why
`oracle_plan`, holding a gold plan with five or seven arguments, raises against
the induced table on 150 of 150 items.

So breadth fails twice over, at induction and at planning, and each failure
alone is sufficient. The earlier reading, that breadth fails at induction and
not at planning, rested on `oracle_plan` against `oracle_both`; that comparison
shows induction fails but says nothing about whether planning would have
succeeded. `oracle_ops` is the comparison that answers it, and it says planning
fails as well.

| metric | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| acc | 1.000 | 1.000 | 1.000 | 0.300 | 0.240 | 0.133 |
| parse_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| well_typed_rate | 1.000 | 1.000 | 1.000 | 1.000 | 0.987 | 0.980 |
| exact_gold_plan_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| parsed_but_wrong_rate | 0.000 | 0.000 | 0.000 | 0.700 | 0.760 | 0.867 |
| emitted_steps_mean | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| emitted_steps_eq_gold_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| prefix_of_gold_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| first_step_correct_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| matched_prefix_len_mean | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| fwd_passes_mean | 12.0 | 13.0 | 14.0 | 14.0 | 14.0 | 14.0 |
| position_evals_mean | 73.8 | 82.7 | 91.3 | 99.0 | 106.8 | 114.2 |
| gen_tokens_mean | 11.0 | 12.0 | 13.0 | 13.0 | 13.0 | 13.0 |
| at_generation_cap | 0 | 0 | 0 | 0 | 0 | 0 |
| n | 150 | 150 | 150 | 150 | 150 | 150 |

| metric | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| acc | 1.000 | 1.000 | 1.000 | 0.433 | 0.280 | 0.173 |
| parse_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| well_typed_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.907 |
| exact_gold_plan_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| parsed_but_wrong_rate | 0.000 | 0.000 | 0.000 | 0.567 | 0.720 | 0.827 |
| emitted_steps_mean | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| emitted_steps_eq_gold_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| prefix_of_gold_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| first_step_correct_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| matched_prefix_len_mean | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| fwd_passes_mean | 13.0 | 14.0 | 15.0 | 15.0 | 15.0 | 15.0 |
| position_evals_mean | 102.2 | 111.0 | 119.7 | 127.2 | 135.2 | 142.6 |
| gen_tokens_mean | 12.0 | 13.0 | 14.0 | 14.0 | 14.0 | 14.0 |
| at_generation_cap | 0 | 0 | 0 | 0 | 0 | 0 |
| n | 150 | 150 | 150 | 150 | 150 | 150 |

The known no-op trap is present and is caught by the diagnostics rather than
hidden by them. `plan_execute` scores 0.300 for P1 and 0.433 for P2 at breadth
four, above the 0.000 those same heads score with gold operators. Those correct
answers come from a wrong plan evaluated against an equally wrong induced
operator, where the flag the head dropped happened not to change the score.
`exact_gold_plan_rate` and `first_step_correct_rate` are both 0.000 in those
cells. Accuracy alone would have read as partial success.

## Plan level diagnostics

Kept apart from accuracy and never folded into it.

P1, sequential, `plan_execute`, greedy, original wording.

| metric | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|
| acc | 1.000 | 1.000 | 1.000 | 0.020 | 0.033 | 0.013 | 0.020 | 0.013 | 0.027 | 0.020 |
| parse_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.973 | 1.000 | 1.000 | 1.000 | 1.000 |
| well_typed_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.973 | 1.000 | 1.000 | 1.000 | 1.000 |
| exact_gold_plan_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| parsed_but_wrong_rate | 0.000 | 0.000 | 0.000 | 0.980 | 0.967 | 0.960 | 0.980 | 0.987 | 0.973 | 0.980 |
| emitted_steps_mean | 1.000 | 2.000 | 3.000 | 3.000 | 3.000 | 1.192 | 3.000 | 3.000 | 3.000 | 3.000 |
| emitted_steps_eq_gold_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| prefix_of_gold_rate | 1.000 | 1.000 | 1.000 | 0.073 | 0.073 | 0.780 | 0.027 | 0.080 | 0.040 | 0.033 |
| first_step_correct_rate | 1.000 | 1.000 | 1.000 | 1.000 | 0.893 | 0.813 | 0.873 | 0.893 | 0.907 | 0.647 |
| matched_prefix_len_mean | 1.000 | 2.000 | 3.000 | 2.073 | 1.860 | 0.911 | 1.553 | 1.813 | 1.527 | 1.193 |
| fwd_passes_mean | 12.0 | 20.0 | 28.0 | 28.0 | 28.0 | 14.1 | 28.0 | 28.0 | 28.0 | 28.0 |
| position_evals_mean | 55.0 | 65.0 | 75.0 | 77.0 | 79.0 | 67.1 | 85.0 | 93.0 | 101.0 | 133.0 |
| gen_tokens_mean | 11.0 | 19.0 | 27.0 | 27.0 | 27.0 | 13.1 | 27.0 | 27.0 | 27.0 | 27.0 |
| at_generation_cap | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| n | 150 | 150 | 150 | 150 | 150 | 150 | 150 | 150 | 150 | 150 |

P2, same.

| metric | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|
| acc | 1.000 | 1.000 | 1.000 | 0.040 | 0.047 | 0.027 | 0.013 | 0.013 | 0.020 | 0.033 |
| parse_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| well_typed_rate | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| exact_gold_plan_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| parsed_but_wrong_rate | 0.000 | 0.000 | 0.000 | 0.960 | 0.953 | 0.973 | 0.987 | 0.987 | 0.980 | 0.967 |
| emitted_steps_mean | 1.000 | 2.000 | 3.000 | 3.000 | 3.000 | 3.000 | 3.000 | 3.000 | 3.000 | 3.000 |
| emitted_steps_eq_gold_rate | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| prefix_of_gold_rate | 1.000 | 1.000 | 1.000 | 0.033 | 0.027 | 0.047 | 0.020 | 0.147 | 0.100 | 0.033 |
| first_step_correct_rate | 1.000 | 1.000 | 1.000 | 0.960 | 0.733 | 0.553 | 0.547 | 0.680 | 0.833 | 0.887 |
| matched_prefix_len_mean | 1.000 | 2.000 | 3.000 | 1.540 | 1.247 | 1.033 | 0.947 | 1.200 | 1.460 | 1.467 |
| fwd_passes_mean | 13.0 | 22.0 | 31.0 | 31.0 | 31.0 | 31.0 | 31.0 | 31.0 | 31.0 | 31.0 |
| position_evals_mean | 83.3 | 94.3 | 105.3 | 107.3 | 109.3 | 111.3 | 115.3 | 123.3 | 131.3 | 163.3 |
| gen_tokens_mean | 12.0 | 21.0 | 30.0 | 30.0 | 30.0 | 30.0 | 30.0 | 30.0 | 30.0 | 30.0 |
| at_generation_cap | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| n | 150 | 150 | 150 | 150 | 150 | 150 | 150 | 150 | 150 | 150 |

The gap between "a plan parses" and "the answer is right" is where the remaining
failure lives, and past depth three it is the whole of it. Parse rate is 1.000 or
near it at every depth. Well typed rate is 1.000 or near it at every depth. Exact
gold plan rate is 0.000 at every depth past three. Parsed but wrong rate is 0.96
to 0.99. Nothing is malformed; everything is the wrong plan.

`prefix_of_gold_rate` rules out the gentlest reading of the three step cap. If
the head wrote the first three steps of the gold plan and stopped, the three
steps it produced would be a correct prefix and only the stopping rule would
have failed. It is 0.073 for P1 at depth four and 0.033 for P2. The head does
not truncate a correct plan; it writes a three step plan whose last step reaches
for the end of the question.

## Compute spent on plan construction

`fwd_passes` is stack invocations, `slot_decisions` is discrete symbols
committed, and `position_evals` is positions whose hidden states were newly
computed. For these two heads a forward pass is one cached decode step, so
`fwd_passes` is the prompt pass plus the tokens the item generated before its own
end of text.

The per cell numbers are in the diagnostic tables above. The summary is that
compute is flat past depth three. P1 spends 28 forward passes and generates 27
tokens at question depth 3, 4, 8, 12, 16 and 32 alike. P2 spends 31 and 30 in the
same cells. Only `position_evals` grows with depth, from 75 to 133 for P1, and
that growth is entirely the question getting longer in the prompt, not the plan
getting longer in the output.

This is the compute reading of the same fact. The head does not run out of
budget at depth four. It declines to spend more.

Every cell, greedy, original wording.

| head | kind | depth | n | forward passes | symbols committed | positions evaluated |
|---|---|---|---|---|---|---|
| p1 | sequential | 1 | 150 | 12.0 | 11.0 | 55.0 |
| p1 | sequential | 2 | 150 | 20.0 | 19.0 | 65.0 |
| p1 | sequential | 3 | 150 | 28.0 | 27.0 | 75.0 |
| p1 | sequential | 4 | 150 | 28.0 | 27.0 | 77.0 |
| p1 | sequential | 5 | 150 | 28.0 | 27.0 | 79.0 |
| p1 | sequential | 6 | 150 | 14.1 | 13.1 | 67.1 |
| p1 | sequential | 8 | 150 | 28.0 | 27.0 | 85.0 |
| p1 | sequential | 12 | 150 | 28.0 | 27.0 | 93.0 |
| p1 | sequential | 16 | 150 | 28.0 | 27.0 | 101.0 |
| p1 | sequential | 32 | 150 | 28.0 | 27.0 | 133.0 |
| p1 | sequential_paren | 2 | 150 | 20.0 | 19.0 | 66.7 |
| p1 | sequential_paren | 3 | 150 | 28.0 | 27.0 | 78.3 |
| p1 | sequential_paren | 4 | 150 | 24.1 | 23.1 | 77.9 |
| p1 | sequential_paren | 5 | 150 | 27.9 | 26.9 | 85.3 |
| p1 | sequential_paren | 6 | 150 | 27.9 | 26.9 | 88.9 |
| p1 | sequential_paren | 8 | 150 | 27.9 | 26.9 | 96.3 |
| p1 | sequential_paren | 12 | 150 | 28.0 | 27.0 | 110.9 |
| p1 | sequential_paren | 16 | 150 | 28.0 | 27.0 | 125.4 |
| p1 | sequential_paren | 32 | 150 | 27.9 | 26.9 | 184.1 |
| p1 | novel | 2 | 150 | 20.0 | 19.0 | 66.5 |
| p1 | novel | 3 | 150 | 28.0 | 27.0 | 78.1 |
| p1 | novel | 4 | 150 | 24.0 | 23.0 | 77.6 |
| p1 | novel | 5 | 150 | 27.9 | 26.9 | 85.2 |
| p1 | novel | 6 | 150 | 28.0 | 27.0 | 88.9 |
| p1 | novel | 8 | 150 | 28.0 | 27.0 | 96.2 |
| p1 | novel | 12 | 150 | 27.9 | 26.9 | 110.8 |
| p1 | breadth | 1 | 150 | 12.0 | 11.0 | 73.8 |
| p1 | breadth | 2 | 150 | 13.0 | 12.0 | 82.7 |
| p1 | breadth | 3 | 150 | 14.0 | 13.0 | 91.3 |
| p1 | breadth | 4 | 150 | 14.0 | 13.0 | 99.0 |
| p1 | breadth | 5 | 150 | 14.0 | 13.0 | 106.8 |
| p1 | breadth | 6 | 150 | 14.0 | 13.0 | 114.2 |
| p1 | same_page_pair | 2 | 150 | 14.0 | 13.0 | 91.4 |
| p1 | units | 1 | 150 | 13.2 | 12.2 | 61.8 |
| p2 | sequential | 1 | 150 | 13.0 | 12.0 | 83.3 |
| p2 | sequential | 2 | 150 | 22.0 | 21.0 | 94.3 |
| p2 | sequential | 3 | 150 | 31.0 | 30.0 | 105.3 |
| p2 | sequential | 4 | 150 | 31.0 | 30.0 | 107.3 |
| p2 | sequential | 5 | 150 | 31.0 | 30.0 | 109.3 |
| p2 | sequential | 6 | 150 | 31.0 | 30.0 | 111.3 |
| p2 | sequential | 8 | 150 | 31.0 | 30.0 | 115.3 |
| p2 | sequential | 12 | 150 | 31.0 | 30.0 | 123.3 |
| p2 | sequential | 16 | 150 | 31.0 | 30.0 | 131.3 |
| p2 | sequential | 32 | 150 | 31.0 | 30.0 | 163.3 |
| p2 | sequential_paren | 2 | 150 | 22.0 | 21.0 | 96.0 |
| p2 | sequential_paren | 3 | 150 | 31.0 | 30.0 | 108.6 |
| p2 | sequential_paren | 4 | 150 | 29.5 | 28.5 | 110.6 |
| p2 | sequential_paren | 5 | 150 | 23.0 | 22.0 | 107.7 |
| p2 | sequential_paren | 6 | 150 | 30.8 | 29.8 | 119.0 |
| p2 | sequential_paren | 8 | 150 | 30.7 | 29.7 | 126.3 |
| p2 | sequential_paren | 12 | 150 | 30.8 | 29.8 | 141.0 |
| p2 | sequential_paren | 16 | 150 | 30.8 | 29.8 | 155.5 |
| p2 | sequential_paren | 32 | 150 | 30.9 | 29.9 | 214.4 |
| p2 | novel | 2 | 150 | 22.0 | 21.0 | 95.8 |
| p2 | novel | 3 | 150 | 31.0 | 30.0 | 108.4 |
| p2 | novel | 4 | 150 | 29.6 | 28.6 | 110.5 |
| p2 | novel | 5 | 150 | 23.3 | 22.3 | 107.8 |
| p2 | novel | 6 | 150 | 30.6 | 29.6 | 118.8 |
| p2 | novel | 8 | 150 | 30.8 | 29.8 | 126.2 |
| p2 | novel | 12 | 150 | 30.7 | 29.7 | 140.9 |
| p2 | breadth | 1 | 150 | 13.0 | 12.0 | 102.2 |
| p2 | breadth | 2 | 150 | 14.0 | 13.0 | 111.0 |
| p2 | breadth | 3 | 150 | 15.0 | 14.0 | 119.7 |
| p2 | breadth | 4 | 150 | 15.0 | 14.0 | 127.2 |
| p2 | breadth | 5 | 150 | 15.0 | 14.0 | 135.2 |
| p2 | breadth | 6 | 150 | 15.0 | 14.0 | 142.6 |
| p2 | same_page_pair | 2 | 150 | 15.0 | 14.0 | 119.6 |
| p2 | units | 1 | 150 | 12.0 | 11.0 | 87.8 |

P2's prompt is wider than P1's by the opcode binding column, which shows up as
28 to 30 extra position evaluations per item in every cell. That is stated below
rather than corrected for.

## What is not matched

Both of these are inherited from the shared design and neither is hidden.

P2 carries the opcode binding column in the prompt, 53 tokens against P1's 26 on
a six operator world, because it writes a plan in opcodes rather than in the
page's own symbol. The column adds no semantics: the symbol, the arity and the
associativity are the same facts P1 gets. It costs positions, and the difference
is visible in `position_evals_mean` throughout.

The two fine tunes produce two different backbones, so induction quality differs
between the heads even though the induction objective and data are identical.
On the original wording the difference is nil, 0.954 against 0.954. On the
paraphrase it is 0.453 against 0.412, and in one place it is much larger than
that: on paraphrased breadth one worlds P1's `oracle_plan` scores 0.940 and P2's
scores 0.000, which is induction failing on 150 of 150 worlds for one head and
almost none for the other. Any comparison of `oracle_plan` on the paraphrase
between the heads is reading that difference and not the plan representation.

## What this licenses and what it does not

Established by this run.

Conditional on a correct externally supplied plan, the 350M substrate induces
the operators from the page and the executor runs them, with no depth
degradation from one step to thirty two, on 150 items a cell, under both heads
and at three temperatures. That is `oracle_plan` at 1.000 across the whole
sequential grid. It is a stronger version of what was already known, and it is
still conditional on a gold plan.

Not established, and specifically not what the depth curve past three shows.

The `plan_execute` collapse at depth four is not evidence that the substrate
cannot compose past three steps. Both heads emit a fixed three step plan at every
depth past the training maximum, never attempt a fourth, and spend constant
compute doing it. The measurement cannot distinguish "cannot compose deeper" from
"learned to stop at three", because the head never produces a plan long enough
for the first hypothesis to be tested. H10 as registered says the wall may belong
to the number of sequential discrete planning decisions; for P1 and P2 the wall
sits at exactly the largest number of decisions the training distribution
contained, which is the reading a length prior predicts and does not separate
from the reading H10 proposes.

The same caveat applies to breadth. Both heads write exactly three flags whatever
the question asks, which is the widest they were trained on.

What would separate them. `data.step_prompt` and the `opgraph_step` arm already
exist in this repo and were built for this: asking for one step at a time removes
plan length as something the decoder has to predict, so a plan of any length
becomes the same short decision taken repeatedly and the length prior has nothing
to attach to. Scoring a stepwise scheduler against P1 on this same grid would
say whether the horizon is the length prior or the composition. Until that is
run, the depth curve of an autoregressive plan head past its training maximum
should be read as a statement about the training distribution.

Also unlicensed here. Nothing in this report compares P1 or P2 to P2s, P3 or P4.
The refinement pass and slot revision measurements the brief asks for belong to
those heads and are not attempted.

## Files

Every number above comes from these artifacts.

| path | what it holds |
|---|---|
| `scripts/planheads_ar_eval.py` | the eval: the shared planners and grader, with the extended depth grid, the generation cap as an argument, and the per cell length diagnostics |
| `scripts/planheads_ar_blocks.py` | every table and every fit in this document, built from the result files |
| `scripts/planheads_ar_doc.py` | splices those blocks into `scripts/planheads_ar_template.md` to produce this file |
| `scripts/planheads_ar_template.md` | the prose, with the tables as placeholders |
| `results/ar/p1_s8000.json`, `results/ar/p2_s8000.json` | every cell of the full grid, both wordings, three temperatures |
| `results/ar/p1_s4000.json`, `results/ar/p2_s4000.json` | the sequential curve at the shorter budget |
| `results/ar/blocks.json` | the tables above as data |
| `runs/ar/p1_s8000.pt`, `runs/ar/p2_s8000.pt` | the two arms, 8000 steps, not tracked |
| `runs/ar/p1_s4000.pt`, `runs/ar/p2_s4000.pt` | the convergence controls, 4000 steps, not tracked |
| `runs/ar/*.pt.log.json` | loss curve, holdout assertion, dropped sequence counts |
| `logs/ar_train_*.log`, `logs/ar_eval_*.log` | the runs themselves |

No shared head code was modified. `planheads_ar_eval.py` imports `grade`,
`make_planner`, `GoldPlanner`, `SlotPlanHead`, `ForwardCounter` and
`mixture_for` from `src.opgraph.planheads`, so a plan is built and judged by
exactly the shared path; what it changes is the depth grid, the generation cap
and the per cell length diagnostics.

Commands, for reproduction.

```
cd ~/opg && export PYTHONPATH=$PWD
CUDA_VISIBLE_DEVICES=N uv run python scripts/planheads_train.py \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --head p1 --out runs/ar/p1_s8000.pt --steps 8000 --batch-size 32 --worlds 40000
CUDA_VISIBLE_DEVICES=N uv run python scripts/planheads_ar_eval.py \
  --ckpt runs/ar/p1_s8000.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/ar/p1_s8000.json --n 150 --batch-size 96 --max-new 320 \
  --styles 0,1 --temperatures 0.0,0.8,1.0 --verify-counter
uv run python scripts/planheads_ar_blocks.py results/ar/blocks.json \
  results/ar/p1_s8000.json results/ar/p2_s8000.json \
  results/ar/p1_s4000.json results/ar/p2_s4000.json
python3 scripts/planheads_ar_doc.py scripts/planheads_ar_template.md \
  results/ar/blocks.json src/opgraph/PLANHEADS_AR.md
```
