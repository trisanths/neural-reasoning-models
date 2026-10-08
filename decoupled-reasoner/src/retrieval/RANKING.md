# The retrieval gate's tie break, and what page order does and does not explain

Run 2026-08-29 UTC on the g6e dev box, which is the stamp on every artifact
below. Checkpoint
`/home/ec2-user/minrepro/ckpt/final.pt`, which is
`rlsimple-503-921-final.pt`, tokenizer_v2, temperature 1.0, four samples per
question, the same episode files the depth curve and the E0 ladder were
measured on. No training. Artifacts under `results/retrieval/`, and every
table below is regenerated from them by `src/retrieval/report.py`.

Two questions are answered here and the answers point opposite ways.

Page order does not explain the composition wall. R0 sits at 0.0000 lenient
and 0.0000 forced at depths two and three under six different page orders, 400
rollouts each, while the table holding the answer goes from served 1 time in
400 to 33 times in 400. The needed page was made 33 times more reachable and
the accuracy did not move.

Page order does explain R1w. The re-keyed wide-page rung reads 0.0025 only
because two structurally identical tables tie exactly under BM25 and the tie
goes to whichever was written first. That is a measurement artifact, it is
fixed here, and fixing it moves the cell.

## The gate, and what is not wrong with it

One function decides which page the policy reads. `RetrievalService.top`
(`src/rl/env.py`) calls `BM25Index.top` (`src/train/retrieval.py:152`), which
walks the episode's documents in order and keeps the best score under a strict
comparison:

```
for i in range(self.n_docs):
    if i in excluded:
        continue
    s = self.score(query, i)
    if s > best_score:
        best_score = s
        best_idx = i
```

Strict `>` gives every exact tie to the lowest document index, and the
docstring says so: "Ties break toward the earliest document, so retrieval is
deterministic." The same call sat at `src/evals/interactive.py:175`, which is
the eval loop the RL environment is documented to follow exactly.

Three of the four faults the brief names are not present.

Okapi BM25 is implemented correctly. `term_score`
(`src/train/retrieval.py:137-147` before this work) computes
`idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))` with k1 1.5 and
b 0.75, the textbook formula with the textbook length normalization. `_idf` is
the smoothed `log(1 + (N - df + 0.5) / (df + 0.5))`, positive everywhere and
larger for rarer terms.

Nothing rounds or truncates a score before it is compared. No format string,
no `round`, no integer cast sits anywhere between `score` and `top`. The ties
are not manufactured by precision loss.

There is no top-k, so nothing can be off by one in it. The gate returns exactly
one document per round and holds without replacement across the rounds of a
rollout through the `served` set.

The diagnosis is not arithmetic. A deterministic order-dependent choice is
being made in the one place where BM25 has declined to choose.

## Why the tie is exact rather than near

`ta6-d*-minimal-ret.jsonl` writes every routing table from one template:

```
The Fexharv routing table.

Requests in the Fexharv office are routed by their type.

A harvka is handled by the zelmi desk.
... six rows
```

Two tables in one episode differ in the office name and in the twelve symbol
tokens in the rows, and in nothing else. Term counts match for every shared
term and so does the document length in normalized terms. For any query naming
no term unique to one of them, `score(query, table_i)` and
`score(query, table_j)` are equal in IEEE double, not merely close.
`src/retrieval/tests/test_tiebreak.py::test_two_templated_pages_tie_exactly`
pins that equality.

This is where the reading here differs from the E0 lane's, which called it a
near tie. The root cause is the same one that lane named and the mechanism it
described reproduces exactly, chain-ordered pages losing to the earlier table.
The correction is that the tie is exact, and exactness changes what can be
done about it. A near tie is a scoring problem and a better scorer could break
it. An exact tie cannot be broken by BM25 at any epsilon, because BM25 holds no
information that separates the two pages, so whatever picks one is not the
retriever and should not be the order the pages were written in.

Measured on the real thing rather than argued. Over the 400 first rounds of
R1w step one at depth two, with the queries the policy actually wrote, 222
rounds have no tie, 167 are two-way ties and 5 are three-way ties, and every
one of the 172 ties is a round the needed page lost on document index alone
(`results/retrieval/d2_before_rows.jsonl.gz`).

## R0 with the page order permuted

The arm the ladder never ran. R0 is the depth-d question exactly
as generated against the minimal page set. `src/retrieval/ordercurve.py`
permutes the tables and touches nothing else. The question text is untouched,
because a control on this lane showed that appending any sentence at all
collapses retrieval rounds from 0.98 to 0.01. The preamble is held at position
zero and only the tables move. The tie break is pinned to `first` for the whole
sweep, so page order is the only variable and the fix below cannot leak into
it; the two experiments are orthogonal by construction.

Arms: `chain` is the order on record, table i at position i+1. `reverse` puts
the last step's table at position one. `goldfirst` moves only the table holding
the final answer to position one and leaves the rest in chain order, which is
R1o's manipulation applied to R0. `rand1` to `rand3` shuffle the tables.

The `chain` arm is the control and it reproduces the record: depth two pass@1
0.0000, mean rounds 0.6925 against the recorded 0.69, the final table served 1
time in 400 against the recorded 1, the preamble served 0.4025 against the
recorded 161 of 400.

Artifact `results/retrieval/r0_order.json`. Lenient / forced.

| page order | d2 | d3 | d4 |
|---|---|---|---|
| chain | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0000 / 0.0000 |
| reverse | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0075 / 0.0075 |
| goldfirst | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0075 / 0.0075 |
| rand1 | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0075 / 0.0075 |
| rand2 | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0000 / 0.0000 |
| rand3 | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0075 / 0.0075 |

Served final table, mean rounds, hedge rate.

| page order | depth | served final table | mean rounds | hedge | n |
|---|---|---|---|---|---|
| chain | 2 | 0.0025 | 0.693 | 0.0025 | 400 |
| chain | 3 | 0.0075 | 0.585 | 0.0000 | 400 |
| chain | 4 | 0.0125 | 0.530 | 0.0025 | 400 |
| reverse | 2 | 0.0825 | 0.693 | 0.0000 | 400 |
| reverse | 3 | 0.0825 | 0.552 | 0.0050 | 400 |
| reverse | 4 | 0.0850 | 0.575 | 0.0000 | 400 |
| goldfirst | 2 | 0.0825 | 0.693 | 0.0000 | 400 |
| goldfirst | 3 | 0.0825 | 0.552 | 0.0050 | 400 |
| goldfirst | 4 | 0.0850 | 0.575 | 0.0000 | 400 |
| rand1 | 2 | 0.0825 | 0.693 | 0.0000 | 400 |
| rand1 | 3 | 0.0025 | 0.583 | 0.0000 | 400 |
| rand1 | 4 | 0.0850 | 0.575 | 0.0000 | 400 |
| rand2 | 2 | 0.0825 | 0.693 | 0.0000 | 400 |
| rand2 | 3 | 0.0025 | 0.583 | 0.0000 | 400 |
| rand2 | 4 | 0.0075 | 0.573 | 0.0025 | 400 |
| rand3 | 2 | 0.0825 | 0.693 | 0.0000 | 400 |
| rand3 | 3 | 0.0025 | 0.583 | 0.0000 | 400 |
| rand3 | 4 | 0.0850 | 0.575 | 0.0000 | 400 |

### Reading the sweep

At depths two and three every arm is 0.0000 on 400 rollouts, lenient and
forced, upper bound 0.0095. The manipulation worked on retrieval and only on
retrieval: at depth two the final table goes from served 1 time in 400 under
chain order to 33 in every other arm, and at depth three from 3 to 33 under
reverse and goldfirst. The three random arms at depth three happen to land that
table late and serve it 1 time in 400, which is a useful accident: the served
rate ranges over a factor of 33 across arms and the accuracy does not budge
from zero anywhere in that range. Given the page, the answer is right 0 times
out of 33 at both depths.

Depth four reads 0.0075 in the four arms that serve the final table on 0.085
of rollouts and 0.0000 in the two that do not. Attacked rather than reported:
all three correct chains came from rollouts that were handed the final table,
3 of 34. A policy that reads the page it was just shown and names one of the
six desks printed on it scores 0.167 on those rollouts. Three in 34 is 0.088,
below that. The interval is 0.0026 to 0.0219 against 0.0000 to 0.0095, which
overlap. This is guessing off a served page, not a chain completing.

Mean rounds does not move with the order at any depth, 0.69 at depth two and
near 0.55 elsewhere, which rules out the alternative that a different page
changes how long the policy keeps going.

The answer classes say what does change. Under chain order at depth two the
first table is served on 0.2875 of rollouts and 0.265 of answers name the first
intermediate. Under the permuted arms the first table is served on 0.195 and
`stopped_at_1` falls to 0.188. The policy performs the first lookup and stops.
Handing it the last table earlier buys nothing, because the last table is keyed
by an intermediate the policy never wrote down. R1o's rescue works for a
different reason: there the environment had already put the intermediate into
the question.

One asymmetry worth naming, because it shows the sweep is measuring what it
claims. At depth three under reverse order the tables sit at positions 3, 2, 1
for chain steps 0, 1, 2, and the step-zero table is still served most often, on
0.1125 against 0.0825 for the step-two table at position one. The question
names the first office, so that table wins on score rather than on position.
Position decides only among the tables the query does not name, and there the
step-one table in the middle is served 0 times in 400.

So the depth curve is not substantially a ranking artifact and the composition
wall at R0 stands. The null is the finding. What it eliminates is that depths
two to four read zero because the needed page was unreachable.

Narrowly scoped. This tests page order under the tie break on record with the
preamble held at position zero. It does not test moving the preamble, which
wins 0.40 of all rounds, and it does not test more retrieval rounds.

## The fix

Four commits, so the effect is attributable to one of them.

`f19d1f9` adds `BM25Index.top_group`, which returns every document holding the
best score instead of the first of them, and routes `RetrievalService` through
a named policy. Rollout rounds gain `n_tied`, the size of the group the served
page came from. The default is `first` and nothing observable changes.

`02ce8d0` moves the policy to `src/train/retrieval.py` so one setting serves
both loops, and puts `src/evals/interactive.py` through it. Still `first`,
still nothing observable changes. This mattered: the two loops are documented
to serve retrieval identically and only one went through the policy, so
changing the policy would have split them silently.

`532f5ad` is one line. `RETRIEVAL_TIE_BREAK` becomes `content`, which hashes
the query together with each tied page's own text and takes the smallest
digest.

`1f36477` and the commits around it carry measurements only. No commit changes
retrieval behaviour and scoring together, and no commit in this work touches a
grader.

What the fix is. A pure function of the query and the page contents, so a run
still reproduces exactly, and one that carries no information about position.
Over a spread of queries a page tied k ways is served about one time in k. The
queries in the measured cells are 385 and 394 distinct out of 400 with the most
common taking 0.003 of the mass, so there is a spread to average over;
`src/retrieval/rowstats.py` reports that on every cell for exactly this reason.

One in k is checked rather than assumed. On the two tables of a depth-two
episode, the hash sends 1184 of the 2337 real queries in the before rows to one
and 1153 to the other, and 10071 of 20000 synthetic queries to one and 9929 to
the other.

What the fix is not. It is not a better retriever and it does not rank. Any
query that separates the documents at all never reaches it, and the tests pin
that. What it removes is a systematic bias, not an error: a page tied k ways
was served either always or never depending on where it was written, and is now
served about one time in k either way. Under a query that carries no
information the ceiling is 1/k and no tie break can beat it.

No semantic reranker and no embedding retriever was considered. The gate stays
BM25 over normalized terms, auditable by reading it.

## The prediction, written before the after run

Committed at `b0c554e`, before either after-run cell existed.
Counted from `results/retrieval/d2_before_rows.jsonl.gz`, first round of each
rollout:

| cell | no tie | tied 2 ways | tied 3 ways | ties the needed page wins | ties it loses |
|---|---|---|---|---|---|
| R1 step 0 | 388 | 5 | 0 | 0 | 5 |
| R1 step 1 | 381 | 6 | 0 | 0 | 6 |
| R1w step 0 | 343 | 40 | 2 | 40 | 2 |
| R1w step 1 | 222 | 167 | 5 | 0 | 172 |
| R1o step 0 | 330 | 49 | 9 | 49 | 9 |
| R1o step 1 | 220 | 166 | 4 | 166 | 4 |

Every tie the needed page currently wins, it wins for sitting earlier; every
tie it loses, it loses for sitting later. A position-blind break puts both at
one in k, which fixes the arithmetic before any rollout runs: R1w step one
should go from 0.008 served to 0.224, R1o step one should fall from 0.4175 to
about 0.21, R1w step zero should fall from 0.4775 to about 0.446, and R1 should
barely move either way.


## The rescue rungs, before and after

Depth 2. Artifacts `results/retrieval/d2_before.json` and `results/retrieval/d2_after.json`.

| rung | tie break | chain pass@1 | 95 pct | forced | pass@4 | hedge | n |
|---|---|---|---|---|---|---|---|
| R1W | first | 0.0025 | 0.0004 to 0.0140 | 0.0025 | 0.010 | 0.0025 | 400 |
| R1O | first | 0.1875 | 0.1523 to 0.2287 | 0.1875 | 0.590 | 0.0050 | 400 |
| R1 | first | 0.2050 | 0.1683 to 0.2473 | 0.2050 | 0.560 | 0.0050 | 400 |
| R1W | content | 0.0925 | 0.0679 to 0.1249 | 0.0925 | 0.340 | 0.0075 | 400 |
| R1O | content | 0.0550 | 0.0366 to 0.0819 | 0.0575 | 0.200 | 0.0100 | 400 |
| R1 | content | 0.2075 | 0.1706 to 0.2499 | 0.2075 | 0.560 | 0.0050 | 400 |

Per step, served needed page and the ranking behind it.

| rung | tie break | step | acc | forced | served page | acc given page | miss on tie | miss on score | n |
|---|---|---|---|---|---|---|---|---|---|
| R1W | first | 0 | 0.4500 | 0.4500 | 0.4775 | 0.942 | 0.005 | 0.499 | 400 |
| R1W | first | 1 | 0.0050 | 0.0050 | 0.0075 | 0.667 | 0.437 | 0.556 | 400 |
| R1O | first | 0 | 0.4425 | 0.4425 | 0.4725 | 0.937 | 0.023 | 0.490 | 400 |
| R1O | first | 1 | 0.3825 | 0.3825 | 0.4175 | 0.916 | 0.010 | 0.562 | 400 |
| R1 | first | 0 | 0.4850 | 0.4850 | 0.5350 | 0.907 | 0.013 | 0.443 | 400 |
| R1 | first | 1 | 0.4575 | 0.4575 | 0.5000 | 0.915 | 0.016 | 0.468 | 400 |
| R1W | content | 0 | 0.4125 | 0.4075 | 0.4425 | 0.932 | 0.005 | 0.503 | 400 |
| R1W | content | 1 | 0.2000 | 0.2025 | 0.2175 | 0.920 | 0.424 | 0.574 | 400 |
| R1O | content | 0 | 0.4100 | 0.4125 | 0.4325 | 0.948 | 0.005 | 0.513 | 400 |
| R1O | content | 1 | 0.1750 | 0.1775 | 0.1900 | 0.921 | 0.005 | 0.557 | 400 |
| R1 | content | 0 | 0.4850 | 0.4850 | 0.5375 | 0.902 | 0.013 | 0.443 | 400 |
| R1 | content | 1 | 0.4625 | 0.4625 | 0.5075 | 0.911 | 0.016 | 0.468 | 400 |


Depth 3. Artifacts `results/retrieval/d3_before.json` and `results/retrieval/d3_after.json`.

| rung | tie break | chain pass@1 | 95 pct | forced | pass@4 | hedge | n |
|---|---|---|---|---|---|---|---|
| R1W | first | 0.0000 | 0.0000 to 0.0095 | 0.0000 | 0.000 | 0.0075 | 400 |
| R1W | content | 0.0100 | 0.0039 to 0.0254 | 0.0100 | 0.040 | 0.0100 | 400 |

Per step, served needed page and the ranking behind it.

| rung | tie break | step | acc | forced | served page | acc given page | miss on tie | miss on score | n |
|---|---|---|---|---|---|---|---|---|---|
| R1W | first | 0 | 0.4300 | 0.4300 | 0.4575 | 0.940 | 0.005 | 0.519 | 400 |
| R1W | first | 1 | 0.0050 | 0.0050 | 0.0075 | 0.667 | 0.442 | 0.551 | 400 |
| R1W | first | 2 | 0.0075 | 0.0050 | 0.0075 | 1.000 | 0.427 | 0.565 | 400 |
| R1W | content | 0 | 0.3800 | 0.3850 | 0.4050 | 0.932 | 0.015 | 0.505 | 400 |
| R1W | content | 1 | 0.1725 | 0.1750 | 0.1900 | 0.908 | 0.429 | 0.568 | 400 |
| R1W | content | 2 | 0.1650 | 0.1675 | 0.1850 | 0.892 | 0.420 | 0.565 | 400 |

### Reading the before and after

How to read the last two columns first, because they are easy to misread. They
describe the BM25 ranking of that round, computed identically in both halves of
the table: a round counts as a tie miss when the needed page holds the served
page's score exactly and sits later, and as a score miss when it is genuinely
below. They are not the outcome. The outcome is the served-page column.

Those ranking columns barely move between the halves, and that is the check
that the fix did what it claims. R1w step one at depth two reads 0.437 tie
misses under `first` and 0.424 under `content`, on different rollouts of the
same questions. BM25 ranks exactly as it did. What changed is that the served
page column went from 0.0075 to 0.2175.

The before run reproduces the record to the digit, which is the only reason
the after run means anything: R1w 0.0025, R1o 0.1875, R1 0.2050 chain pass@1
at depth two on 400 chains each, with the per-step served-page histograms
matching `rescue_order.json` as well. At depth three R1w reproduces 0.0000 with
step accuracies 0.4300, 0.0050, 0.0075.

R1w rises and R1o falls, and they meet.

| depth two, chain pass@1 | tie break first | tie break content |
|---|---|---|
| R1w | 0.0025 | 0.0925 |
| R1o | 0.1875 | 0.0550 |
| R1  | 0.2050 | 0.2075 |

R1w rising is expected and proves little on its own, because almost anything
that serves more pages would raise it. R1o falling is the half that is hard to
get by accident, and it is what settles the question: R1o read 0.1875 because
its needed page won every tie for sitting early, exactly as R1w read 0.0025
for losing every one of them. The 75x gap between the two rungs was page order
and nothing else.

The direct measurement, without the chain pairing in the way, is the served
page at step one. R1w goes from 0.0075 to 0.2175 and R1o from 0.4175 to
0.1900, and those intervals overlap; so do the step-one accuracies, 0.2000 and
0.1750. The values predicted before the run from the tie group counts were
0.224 and about 0.21.

R1 is the control and it does not move: 0.2050 to 0.2075. Its page set is the
preamble and one table, which tie on 5 and 6 first rounds out of about 390, so
there is nothing there for a tie break to change.

Accuracy given the needed page does not move on any cell, staying between 0.90
and 0.95 throughout. Nothing here is the model getting better at the lookup.
The whole effect is which page the gate hands it.

The brief set the target as R1w rising toward R1o's 0.1875. That target was
itself inflated. What both rungs were groping at is near 0.06 to 0.09, and R1's
0.2050 is the ceiling when the page set holds no twin for the needed table to
tie with.

## Which recorded numbers are understated, and by how much

Measured here, both runs on the same questions, seeds and graders.

| recorded | was | is | denominator |
|---|---|---|---|
| R1w chain pass@1, depth two | 0.0025 | 0.0925 | 400 chains |
| R1w step one, depth two | 0.0050 | 0.2000 | 400 rollouts |
| R1w chain pass@1, depth three | 0.0000 | 0.0100 | 400 chains |
| R1w step one, depth three | 0.0050 | 0.1725 | 400 rollouts |
| R1w step two, depth three | 0.0075 | 0.1650 | 400 rollouts |
| R1o chain pass@1, depth two | 0.1875 | 0.0550 | 400 chains |
| R1 chain pass@1, depth two | 0.2050 | 0.2075 | 400 chains |

Depth three needs a caveat that depth two does not. Its chain number goes
0.0000 to 0.0100, interval 0.0039 to 0.0254, against a chain floor of 0.0046.
Three steps near 0.17 compound to about 0.01, so that reading sits just above
chance and carries little. The step readings are where the signal is, and they
are the same 30x to 40x lift depth two shows.

R1o is overstated, not understated, and by more than R1w is understated. Any
conclusion that leaned on R1o standing three quarters of the way to R1 needs
rereading; the reordering it performed was not neutral.

Inferred, and marked as such because it was not re-run.

R2w at every depth is the wide-page rung driven by the model's own key. Its
page sets are the same chain-ordered sets as R1w and its tie structure is
identical, so its recorded 0.0000 at depths two to four is understated by the
same mechanism. The lift should be smaller than R1w's because about half of
R2's chains break before the step in question, and the recorded values are
zeros with an upper bound of 0.0095 rather than a measured 0.0025, so there is
less room to be wrong about. A guess of 0.03 to 0.06 at depth two follows from
R1w's step-one lift times R2's surviving fraction, and it is a guess.

Not understated, and this is measured rather than assumed.

R0 at every depth. The order sweep moved the served page by a factor of 33 and
moved the accuracy by nothing. R0 was then re-run under the fix itself, chain
order held, so that the new gate cannot be said to move the baseline the sweep
was measured against (`results/retrieval/r0_content.json`). It does not: depth
two reads 0.0025 against 0.0000 and depth three 0.0000 against 0.0000, on 400
rollouts each, while the final table goes from served 0.0025 to 0.0475 and from
0.0075 to 0.0150. The one correct chain at depth two came from a rollout handed
that table, 1 of 19, against the 0.167 a policy naming a desk off the page
would score.

The depth curve in `CURVE.md`. Same evidence. Its depths two to four sit at
zero for the reason the E0 lane gave.

The depth-one anchor. 0.4850 in this harness against the recorded 0.4850, with
5 ties out of 393 first rounds on its two-page set. There is almost nothing for
the tie break to touch.

The six-page condition, and this one is worth stating plainly because the brief
suspected it. `system.pages` shuffles, so it is in the unbiased class: with a
shuffled order the earliest tied page is the needed one about one time in k
already, which is what a position-blind break gives. Applying 60 queries this
checkpoint actually wrote to those page sets
(`results/retrieval/pagesets.json`), the expected served rate for the needed
page moves from 0.038 to 0.051 on the depth-one correct-pages file, against
0.007 to 0.163 on the depth-two chain-ordered file. Those are transferred
queries applied across page sets, so they size an effect rather than measure a
cell. The drop from 0.5375 on two pages to 0.125 on seven is the needed page
being outscored, not outsorted.

The skillacq families, for the same reason and with the same evidence. Under a
query built only from shared vocabulary, hit@1 across the six families is
0.465, 0.520, 0.270, 0.460, 0.460, 0.710 against a position-blind 0.493, 0.492,
0.318, 0.491, 0.492, 0.703. Under the problem text as the query the gate is at
0.951 to 1.000 and no miss is a tie at all.

The scoping rule behind all of this: chain-ordered page sets are biased,
shuffled page sets are not. Only `minimal_pages` orders its tables, and it puts
the table needed at step i behind the table needed at step 0 in every episode
of every file.

### The skillacq families

`src/retrieval/skillrank.py`. Six families, 200 episodes and 1600
problems each. The needed pages are every page of the episode's own family,
recovered by replaying the generator's random stream, which is the lenient
labelling: a hit means the family's textbook was reached at all rather than the
one page carrying the needed rule, so these miss rates are lower bounds.

Artifact `results/retrieval/skillrank_before.json`.

| family | episodes | problems | hit@1 problem query | 95 pct | miss on tie | miss on score | mean rank | hit@1 shared query | miss on tie, shared |
|---|---|---|---|---|---|---|---|---|---|
| units | 200 | 1600 | 0.992 | 0.986 to 0.995 | 0.000 | 0.008 | 1.01 | 0.465 | 0.535 |
| procedure | 200 | 1600 | 1.000 | 0.998 to 1.000 | 0.000 | 0.000 | 1.00 | 0.520 | 0.480 |
| binary_op | 200 | 1600 | 0.951 | 0.940 to 0.961 | 0.000 | 0.049 | 1.05 | 0.270 | 0.330 |
| threshold_rule | 200 | 1600 | 1.000 | 0.998 to 1.000 | 0.000 | 0.000 | 1.00 | 0.460 | 0.535 |
| substitution_rule | 200 | 1600 | 1.000 | 0.998 to 1.000 | 0.000 | 0.000 | 1.00 | 0.460 | 0.360 |
| exception_rule | 200 | 1600 | 1.000 | 0.998 to 1.000 | 0.000 | 0.000 | 1.00 | 0.710 | 0.290 |

Transferred queries against four page sets, 60 queries this
checkpoint actually wrote, applied to every question of each file. The last
column is what the same queries would serve under a position-blind break.

Artifact `results/retrieval/pagesets.json`.

| episodes file | pages | serves nee

## What is left, and the change not made

Between 0.55 and 0.82 of the misses in every cell measured here are score
losses, not tie losses, and most are to the preamble, which wins 0.40 of all
rounds under R0. On the R1 page set of two, with the sub-question as the query,
the preamble scores 3.06674 and the routing table that literally contains the
office the question names scores 3.036587, a margin of one percent
(`results/retrieval/rank_d2_before.json`). The preamble is shorter than the
tables and shares the question's generic vocabulary, and b is 0.75, so length
normalization pays it.

That is a ranking-function problem and it is stated here rather than fixed.
Lowering b, raising the idf floor, or moving to BM25+ would each change the
ranking of every document in every measurement this project has recorded,
which is a different experiment and needs its own before and after against a
fixed tie break and a fixed page order. The same harness runs it:
`src/retrieval/rungeval.py` with both pinned. It is proposed, not done.

Not considered at all: a semantic reranker or an embedding retriever. The gate
is meant to be readable and every existing measurement is against this gate.

## Integrity

Chance floors. The universe is six desks, so a guesser naming one desk scores
0.1667 on a step and 0.1667 to the power d on a chain: 0.0278 at depth two,
0.0046 at depth three, 0.0008 at depth four. Every accuracy here is a chain
accuracy against the chain floor or a step accuracy against the step floor, and
the two are never merged. Depths are never pooled and rungs are never pooled.

Denominators. Every rung cell is 100 questions by four samples, so 400 chains,
and every step within a cell is 400 rollouts. Every order-sweep cell is 400
rollouts. The skillacq cells are 200 episodes by eight problems, 1600 problems
per family, never pooled across families.

Both graders on every row. The lenient column is `hits_target`, the rule the
environment trains against, which accepts a prediction containing the gold with
six tokens of slack. The forced-choice column takes the universe tokens the
answer names and counts it correct only when it names exactly one and that one
is the gold. The hedge rate is the fraction naming more than one, and it is the
only thing that can separate the two columns. On this family it is 0.0100 and
below on every cell measured, so the two columns agree to within 0.005
everywhere. That is a property of this checkpoint on this family and not a
reason to drop the forced column anywhere else.

No grader changed. `hits_target` and the forced-choice rule are imported from
`src/disc/minrepro.py` and `src/disc/rekey.py` unchanged. No commit in this
work changes retrieval behaviour and scoring together, and the one commit that
changes retrieval behaviour, `532f5ad`, changes one line and nothing else.

Artifacts, all under `results/retrieval/`:

    r0_order.json             the page-order sweep, 18 cells
    r0_order_rows.jsonl.gz    every rollout of it
    r0_order_d1.json          the depth-one anchor through the same harness
    r0_content.json           R0 re-run under the fix, chain order held
    d2_before.json            the rungs under the tie break on record
    d2_after.json             the same rungs under the position-blind one
    d2_before_rows.jsonl.gz   every before rollout, its query, the page served,
                              and the score vector behind it
    d2_after_rows.jsonl.gz    the same for the after run
    d3_before.json            R1w at depth three, both tie breaks
    d3_after.json
    skillrank_before.json     six skillacq families
    pagesets.json             page sets under transferred policy queries
    rank_d2_before.json       the static diagnosis of the E0 page sets

`src/retrieval/report.py` regenerates every table in this file from those
files.

## What this does not settle

One checkpoint, one notation family, one surface form, temperature 1.0.

The order sweep holds the preamble at position zero and permutes only the
tables. The preamble wins 0.40 of all rounds, so moving it is the obvious next
arm and it was not run.

The position-blind tie break is a fair coin among pages BM25 cannot separate.
It puts R1w at the value it should always have read and it does not make the
retriever better. The gap between R1w's 0.0925 and R1's 0.2075 is the query
carrying almost no information, and no tie break addresses that.

The transferred-query analysis in `pagesets.json` applies queries the policy
wrote on one page set to a different page set. That is defensible only because
those queries carry almost no information about the question, and it sizes an
effect rather than measuring a cell.

R2w was not re-run. Its number in the table above is inferred and labelled.
