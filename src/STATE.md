# What this project has established

Written 2026-09-02 against the record files rather than the prose above them.
Every claim carries the artifact it rests on and whether that artifact was
opened and the number recovered from it. A claim whose artifact could not be
located is in its own section rather than in the tables.

Claims are organised by claim, not by lane. Where a claim was corrected, the
superseded version and the number that killed it are given, because on this
project the corrections are the content and a reader needs to know which
reading they are looking at.

Three conventions from `DISCOVERY.md` are applied throughout: no accuracy
without its denominator and its own chance floor, nothing pooled across
families, and no lenient grader score without the forced-choice score beside it.

## What we would tell someone outside this project

Eight statements, each at the strength its interval supports and no further.

1. A 45M encoder-decoder trained to read invented rule pages into a typed
   structure reads them at 0.9209 exact on trained sentence forms and 0.8181 on
   a held-out symbol lexicon, against a hand-written parser at 1.0000 on every
   cell. That headline is pooled over an item set half of which the reader has
   already seen: split, it is 0.9997 on structures present in the training file
   and 0.7859 on structures absent from it. The second number is the one about
   reading. Surface generalisation over vocabulary is real at this size, and
   smaller than the headline.

2. On a sentence form it has never seen, that reader binds which word is the key
   and which is the value to where the words sit rather than to what the
   sentence says, and it does so on eight of fourteen question shapes: 0.7450
   key-first against 0.0000 value-first, n=2,016 and 1,984. Balanced data does
   not prevent it, minimal pairs do not, an auxiliary role objective does not.
   Above roughly 167M parameters it stops: the same split reads 0.3938 against
   0.3392. The asymmetry resolves with capacity somewhere between 93M and 167M.
   It resolves by the model ceasing to commit to a position, not by its becoming
   good at both.

3. Reading role off the syntax of an unfamiliar rule sentence is taught by this
   task and is not inherited from English pretraining. LFM2-350M, with 354M
   parameters, a full pretraining budget and no exposure to this task, writes
   0.8805 of key-first pairs the right way round and 0.3479 of value-first ones
   against a 0.5 floor, on the same items. A 167M model trained on the task does
   not show that split.

4. A model can read values off a page it has never seen and answer with them: a
   page with identical wording and permuted values moves the answer with the
   page. It cannot tell which system's page it is reading, it does not
   generalise to relation types it was not trained on, and a fifty-line regex
   over the same pages beats it. What is supported is frame-conditioned value
   binding, not inference-time skill acquisition.

5. A symbolic library, with no gradient step anywhere in its path, reads an
   operation defined on one page of prose and applies it at 1.0000 forced choice
   against floors of 0.29 to 0.37, on 850 items over 170 distinct operations,
   where the neural reader on the same items is at 0.00 to 0.12 and never once
   emits the right structure in 6,736 attempts. This is the clearest positive
   result on the project and it is a result about a symbolic reader, not about a
   network. Its gold answers and its own answers come from the same interpreter.

6. Chaining is the failure that has survived every intervention tried on it.
   Widening the training distribution fixed frame boundedness and fixed the
   plan-length ceiling and did not fix this. Training on real multi-hop
   retrieval moved HotpotQA from 0.004 to 0.278 and left `chain_rule` at its
   floor, 0.2520 before and 0.2441 after against 0.250, n=1,536. Making the
   needed page 33 times more reachable moved accuracy by nothing. A step whose
   input must come from a previous step's retrieved result is where this
   architecture stops.

7. The strict form of the thesis is dead by its own pre-registered rule. A
   substrate trained with no natural language at all, only synthetic worlds with
   within-episode retrieval, scores 0.0000 on naturalized reading against 0.2053
   for the same size trained on ordinary text, three seeds each, bootstrap
   interval [0.0000, 0.0000]. Everything measured since runs on a model that has
   read ordinary text.

8. Nothing here beats a comparable off-the-shelf model at anything. On MMLU our
   375M checkpoint is at chance at every sample size measured, and LFM2-350M,
   which is smaller, reads 0.4300.

Everything else in this document is either a measurement of how something fails,
a correction to a claim we made, or an account of an instrument.

## The pre-registered kill test

### Claim K1. The strict form of the thesis was killed by its own pre-registered rule on 2026-08-26

Confirmed, and it is the most consequential result in the repository.

`SPEC.md` section 7 fixes the rule before the test: compare regime C against
regime A at the 350M class on the naturalized reading suite; at or above 90
percent of A's score the strict form survives, between 60 and 90 percent it is
weakened, below 60 percent "the strict form is dead; Phase 2 tests only the
weakened form and the writeup says so plainly."

Regime C is the thesis in its strict form: procedural warm-up, then randomized
synthetic worlds with within-episode retrieval, no natural corpus and no
real-world entities, with facts mutated every episode so memorising them has
zero expected value. Regime A is the conventional baseline, FineWeb-Edu plus
Wikipedia.

Gate metric, naturalized reading, contains-answer, clean variant, 250 items,
three seeds per regime, from `results/killtest-2026-08-26/verdict.json`:

| regime | per seed | mean | std |
|---|---|---:|---:|
| A, natural text | 0.2280, 0.1960, 0.1920 | 0.2053 | 0.0197 |
| C, the strict thesis | 0.0000, 0.0000, 0.0000 | 0.0000 | 0.0000 |

Ratio of means 0.0000, bootstrap 95 percent interval over items and seeds
[0.0000, 0.0000] on 10,000 replicates with 0 dropped. Exact match on the same
variant gives A 0.0027 and C 0.0000, so A's own score is small and C is at zero
either way. The leakage rule was applied and every regime C checkpoint's
knowledge probes read at chance, so C's zero is not being masked by
contamination in the other direction.

Zero is below 0.6. Under the pre-registered rule the strict form is dead, and
the verdict file says so.

Two things this does and does not settle. It does not say a small substrate
cannot reason; it says a substrate trained with no natural language at all
cannot read a naturalized page, which is the input side of every downstream
experiment. And it is why everything measured since runs on the weakened form,
a model that has seen ordinary text. Any statement in `THESIS.md` about a
"fact-free" model should be read against this: the checkpoints in current use
are not fact-free, and the fact-free ones scored zero.

## Role order and key position

### Claim R1. A reader that has seen a sentence mode binds role correctly in both orders; on a sentence mode it has never seen, it binds role to position instead

Confirmed. `src/norm` 45M encoder-decoder (`l45`, 45,483,008 parameters, 30,000
steps), structure exact match, greedy, held-out sentence mode `relative_clause`.

On the five trained sentence modes the two orders are level, 0.9206 key-first
(n=3,528) against 0.9211 value-first (n=3,472). On the held-out mode the same
reader reads 0.7302 (2,576/3,528) key-first and 0.3177 (1,103/3,472)
value-first.

Recounted from `results/system/eval/l45/records_mode_greedy.jsonl.gz`, splitting
on the frame id's key-position field. Reproduces the reported cells to the digit.
Sampled decoding gives 0.7171/0.3131, same direction.

Three controls hold. The hand-written parser `src/norm/parse.py` reads every cell
of every split at 1.0000, including 1,302 of 1,302 value-first items of the
held-out mode, so the binding is in the text and unambiguous. The training draw
is balanced on key position: 0.4978 to 0.5006 value-first per shape, 42,567 to
42,918 items each, and 8,362 to 8,910 value-first items inside every one of the
five trained modes, counted off `data/norm/train.meta.jsonl.gz`, the file the
network saw. And the failure is confident rather than confused: on the affected
shapes 531 of 651 value-first failures are a well-formed structure the
interpreter executes to a wrong answer, 120 are refusals, 0 are malformed.

### Claim R2. The collapse is specific to the axis that carries the role-order template, and this was predicted from the generator's code before either arm ran

Confirmed. `src/corpus/frames_default.py` renders the rule sentence from `ASSOC`,
a twelve-entry table keyed on the pair (statement mode, key position). The
question comes from a different table that does not key on key position at all.
So withholding a statement mode removes both of that mode's role-order templates;
withholding a question form removes none.

| split | withheld | group scored | key first | value first |
|---|---|---|---:|---:|
| b45 | statement mode `table_row` | mode | 0.6165 (3,528) | 0.2471 (3,472) |
| c45 | question form `wh` | qframe | 0.7440 (3,500) | 0.7611 (3,500) |

Recounted from `results/system/eval/b45/records_mode_greedy.jsonl.gz` and
`results/system/eval/c45/`. Both predictions held. Trained frames stay balanced
in both splits (b45 0.9269/0.9332, c45 0.8688/0.8652).

The pre-registration is verifiable and was checked rather than taken on trust.
The prediction text entered `src/system/THRESHOLD.tmpl.md` in commit `e58ffcf`,
"What the frame grammar says the two new splits should do, written first", at
2026-08-31 20:46:33 UTC. `results/system/eval/c45/summary.json` was written
2026-09-01 00:40 and `results/system/eval/b45/summary.json` 2026-09-01 02:05, so
the prediction predates the first result by three hours fifty-four minutes and
the second by five hours nineteen. It is the strongest methodological result on
the project: a prediction derived from generator source, committed before either
arm returned, and confirmed on both.

The grouping used here and in claim R4 is the generator's, not the scores'.
`src/role/rshapes.py` fixes the eight shapes in a constant, `new keys`, defined
as those whose rule lines state a key that appears nowhere else, so the sentence
wording is the only channel carrying role. The other six are four whose two
renderings are byte identical, one whose key is a band label an earlier page
already named, and one where the axis reaches only a column header. Read from
`results/role/shapes_l45_mode.json`, field `definition`.

### Claim R3, superseded. The collapse is a property of the substrate

Dead. It was argued from three flips: `xl93match` reverses against `l45`, arm D
reverses against its own baseline, and four training-signal interventions moved
which convention was chosen without removing the choice.

Killed by the 167M rung. `xxl167` (167,376,384 parameters, 110,271 steps at a
matched tokens-per-parameter budget) reads 0.6341 key-first against 0.6063
value-first on the same items, a gap of 0.028 against `l45`'s 0.413. Recounted
from `results/system/eval/xxl167/records_mode_greedy.jsonl.gz`. The property does
not survive scale, so it is not a property of the substrate.

### Claim R4, and this corrects Correction 4. The asymmetry closes between 93M and 167M, but 167M reaches symmetry by getting worse at the order it used to get right

Confirmed, and stated here more precisely than `THESIS.md` correction 4 states
it. Correction 4 quotes the aggregate held-out-mode figure, 0.6341 against
0.6063, and reads it as the larger reader handling both orders. The aggregate
pools fourteen question shapes, and key position only reaches eight of them: it
selects the `ASSOC` rule sentence and the `table_row` column header and nothing
else, so on the other six the two renderings are byte identical and cannot show
the effect either way. Splitting on that, greedy:

| rung | steps | axis-reached, key first | axis-reached, value first | gap | not reached, key / value |
|---|---:|---:|---:|---:|---|
| l45, 45M | 30,000 | 0.7450 (1,502/2,016) | 0.0000 (0/1,984) | +0.745 | 0.7103 / 0.7413 |
| xl93, 93M | 30,000 | 0.6989 (1,409/2,016) | 0.0106 (21/1,984) | +0.688 | 0.6918 / 0.7238 |
| xl93lr40, 93M | 30,000 | 0.6290 (1,268/2,016) | 0.0000 (0/1,984) | +0.629 | 0.6488 / 0.6700 |
| xl93match, 93M | 61,724 | 0.0084 (17/2,016) | 0.6976 (1,384/1,984) | -0.689 | 0.7454 / 0.7621 |
| xxl167, 167M | 110,271 | 0.3938 (794/2,016) | 0.3392 (673/1,984) | +0.055 | 0.9544 / 0.9624 |

Computed from each rung's `records_mode_greedy.jsonl.gz` under
`results/system/eval/`. Sampled decoding reproduces every cell to within 0.002,
so this is not a greedy artifact.

Three things follow, and only the first is in the record already.

The gap does close, from 0.745 to 0.055, between 93M and 167M. That much of
correction 4 stands.

The 167M rung does not become competent at both orders. It becomes symmetric at
0.39 and 0.34, where the 45M rung was at 0.7450 on the order it could do. On the
shapes this finding is about, more parameters cost 0.35 on key-first and bought
0.34 on value-first. Nothing here shows a reader that has learned role is
distinct from position; it shows one that has stopped committing to either
position.

The aggregate improvement Correction 4 reports, 0.5256 to 0.6203, is carried
almost entirely by the six shapes the axis does not reach, which go from
0.7103/0.7413 to 0.9544/0.9624. Reading 0.6203 as progress on axis composition
attributes to the compositional axis a gain that happened elsewhere.

So the honest statement is narrower than correction 4's: the positional
commitment disappears between 93M and 167M, and the competence it was hiding
does not appear with it.

### Claim R5. Four interventions on the training signal changed which convention was chosen and none removed the choice

Confirmed. Four arms from the same 45M base, same data volume, same 30,000
steps, same seed, changing only how role order is supplied. Held-out sentence
mode, structure exact match, greedy.

| arm | key first | value first | gap | trained frames |
|---|---:|---:|---:|---|
| A, reproduction and gate | 0.7112 (2,509/3,528) | 0.3119 (1,083/3,472) | +0.399 | 0.9354 / 0.9404 |
| B, minimal pairs | 0.7863 (2,774/3,528) | 0.3787 (1,315/3,472) | +0.408 | 0.9243 / 0.9248 |
| C, auxiliary role head | 0.5519 (1,947/3,528) | 0.2632 (914/3,472) | +0.289 | 0.8537 / 0.8450 |
| D, pairs plus head | 0.2639 (931/3,528) | 0.5942 (2,063/3,472) | -0.330 | 0.8688 / 0.8701 |

Read from `s3://decoupled-reasoner-009398924577/role-back/results/role/split_role{A,B,C,D}.json`,
each of which names the per-item records it was computed from and their write
times. Every cell reproduces the table in `THESIS.md` exactly. Arm A is the gate
and it lands within 0.02 of the published baseline, so the rest is interpretable.

Arm B is the arm to read. Minimal pairs lift both positions by about five points
and leave the gap where it was. The draw was verified on every row rather than
on a sample: 394,367 pairs over all 600,000 slots, every pair differing in the
key-position field alone, same shape, same structure, same invented words, and
342,796 of them with differing gold targets. Arm C lowers both cells, so its
narrower gap is two numbers falling rather than a repair.

After correction 4 these four arms are still four valid measurements, and their
reading changes: at 45M nothing done to the training signal substitutes for
capacity. They are not evidence about the architecture.

Two provenance notes. The arm artifacts, including per-item records, are in S3
under `role-back/` and are not in the git checkout, so a reader of the repository
cannot find them from the repository. And `src/role/ROLE.md`'s results section
still reads "Pending" while `THESIS.md` reports all four arms; the lane report
was never updated after the arms landed.

The planned control for arm B was to run only if arm B moved the split. Arm B
did not, and no qpaired run appears in `role-back/`. That is correct by the
pre-registered rule, and it means the repetition confound arm B carries, that
seeing the same structure twice in a batch is a different training signal
whatever axis the two renderings differ on, was never separately measured. The
draw itself was built and survives at
`s3://decoupled-reasoner-009398924577/role-xfer/data/role/qpaired_train.npz`;
it is not in the checkout, where `data/role/qpaired_train` no longer exists.

### Claim R6. Reading role off the syntax of an unfamiliar rule sentence is taught by this task, not inherited from English pretraining

Confirmed, and this is the claim that survives the substrate correction.

`LiquidAI/LFM2-350M`, 354,483,968 parameters summed over the loaded tensors, is
put on the same items. It cannot emit the typed structure language, so the
measured quantity moves: of the rule pairs it reproduces, what share does it
write key-on-the-left, which is the direction the prompt asks for identically in
both cells. Held-out sentence mode, greedy:

| parser | key first | value first | floor |
|---|---|---|---:|
| strict arrow parse | 0.8814 (1,018/1,155) | 0.3514 (414/1,178) | 0.5 |
| generous re-parse, same generations | 0.8805 (1,068/1,213) | 0.3479 (429/1,233) | 0.5 |

Read from `results/role/lfm2/report.json` and `results/role/lfm2/rescore.json`.
Both parsings give the same answer, so the reading does not depend on the parser.
Sampled at the settings `src/extern/models.py` carries for this model gives
0.9151/0.2798, same direction.

The harness is calibrated rather than assumed: `results/role/lfm2/control.json`
records the chat template, the bos token id, and the five control questions
answered correctly with the token and degenerating into repetition without it.
Truncation is 0.0286 and 0.0210 across the two cells, far too small to carry a
0.53 gap. The denominators are near equal, 1,213 against 1,233.

LFM2 collapses on all six statement modes, 0.8805 to 0.9777 key-first against
0.0905 to 0.6453 value-first, so this is not about a withheld mode. It has no
trained mode here.

Put beside `xxl167`, which reads 0.6341/0.6063 at less than half the parameters,
the pair licenses one statement and not more: a 354M model with a full English
budget and no training on this task binds role by surface order; a 167M model
with the task and a third of the parameters does not. English pretraining is not
what supplies role-independent reading.

Three limits carried. The two measurements are not the same statistic, and the
levels are not comparable: `xxl167` emits a typed structure after 110,271 steps
on this corpus and LFM2 writes arrows zero-shot. Only the shape of the split is
being compared. Four of the seven LFM2 formulations sit at their floor in both
cells and cannot discriminate a balanced reader from a collapsed one; they are
reported as floors, not as results. And the open-generation formulation runs
opposite in sign to the arrow formulation, so which convention LFM2 commits to
depends on the prompt, while whether it commits to one does not.

### Claim R7. The transposed-operand failure is a hole in a training draw and has a data fix

Confirmed, and it is the case that contrasts with R1.

A rung shown 1,024 examples of a grid page shape reads 750 transposed pages at
0 of 750 exact and writes the untransposed key order on 733 of 750, while
reading the untransposed version at 672 of 750. The fine-tuning draw
`grid_train` lists its key pairs in row-major order on 4,096 of 4,096 pages, so
it never showed the layout the test asks for.

Fine tuning on `grid_both`, the same construction with 512 of 1,024 pages in
the other order and no page shared with `grid_train` or with either item set,
moves transposed exact from 0 of 750 to 462 of 750 and the untransposed key
order from 733 of 750 to 258 of 750.

The fix is not free and the record says so: the original page falls from 672 of
750 to 404 of 750, and the group where the untransposed order still wins is the
held-out sentence mode, 92 of 150 against 55 of 150 exact. Balancing the layout
does not reach the positional binding that a new sentence mode breaks.

From `results/system/tpose/xmode_{l45,xl93,xxl167}.json` and the per-group tables
in `src/system/THRESHOLD.md` section 6.

## One-shot acquisition

### Claim N1. The reported one-shot figure of 0.9644 does not exist

The number 0.9644 appears in no document in this repository, in no record file,
and in no commit. `git log --all -S"0.9644"` returns nothing. Grepping every
markdown file returns nothing. The only matches for the digit string `9644`
anywhere under `results/` are substrings inside longer floats in unrelated lanes
(`results/killtest-2026-08-26`, `results/curve-350md`, `results/latentret`,
`results/pointer`).

This was checked twice, independently. It is the third number on this project to
have been quoted after the records stopped supporting it, alongside the 0.680
headline and the one-in-twenty query rate, and it is recorded here in the same
terms.

The one-shot lane's actual headline is 1.0000, not 0.9644, and it is a stronger
number attached to a much narrower claim. It is set out next.

### Claim N2. An operation stated on one page of prose is installed and applied at 1.0000 forced choice, with no gradient step

Confirmed by recount from
`results/norm/oneshot/sys.jsonl.gz`.

The task: an operation is defined on a single page of English prose, in one of
four wording modes. The system reads the page, installs the operation in an
episode-scoped library, and answers a question requiring it. Nothing in the
corpus, renderer, parser or normalizer target vocabulary could previously state
such an operation. No gradient step anywhere in the library path.

Forced-choice strict, floors computed per item from that item's own option count
and averaged:

| family | n | floor | 1 page | 2 pages | 4 pages | structure exact | hedge | declined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 directories, 1 clause | 110 | 0.3735 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| 3 directories, 1 clause | 310 | 0.3086 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| 2 directories, 2 clauses | 25 | 0.3567 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| 3 directories, 2 clauses | 405 | 0.2879 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |

The network on the same items is the contrast that makes the row worth having:
greedy 0.0000, 0.0194, 0.1200 and 0.0173 by family, and structure exact 0 of
6,736 greedy and 0 of 6,736 sampled, from
`results/norm/oneshot/n_base_l.jsonl.gz`.

The grader is the one place on this project where the containment bug is
properly defended. `src/norm/cmpwork/grade.py` matches word tokens rather than
substrings, explicitly so that `emb` does not score correct on a page whose
answer is `embqen`, handles multi-token candidates as contiguous runs, and
suppresses a candidate wholly contained in a longer one at the same position.

### The caveats, which are large enough that the 1.0000 must not travel alone

Five, and the first three are not in the lane's own document.

The effective denominator is 170, not 850. The 850 items are 170 distinct
operations at 5 items each, one frame id per operation. For the question "did it
acquire the operation" the independent unit is the operation.

The parser baseline is vacuous rather than passed. `src/norm/parse.py` scores
0.0000 with declined at 1.0000, because it has no template for a definition page
and never attempts an answer. Reporting 0.0000 as a trivial-program baseline
beaten by 1.0000 overstates the comparison. The informative trivial baselines are
the shortcut readers S1 and S2, which take the first or last line stating the
question key: they read 0.2182 to 0.4129 against floors of 0.2879 to 0.3735, so
they sit at or barely above chance, and against those the 1.0000 is genuinely far
above every trivial competitor on this item set.

On the eight-operation ladder set, however, the shortcut wins. S2 scores 0.6000,
0.8000 and 0.8000 on three of the ladder operations, against the fine-tuned
network's best ladder score of 0.5500. `ONESHOT.md` prints those S2 numbers and
does not remark that a one-line heuristic outscores the gradient learner on the
learner's own test.

Gold and the library's answer come from the same interpreter.
`src/norm/opitems.py` takes the gold answer to be what `src/norm/interp.py`
returns for the generator's program, and `src/norm/opread.py` imports `run` from
that same `src/norm/interp.py`. So the 1.0000 certifies that the reader recovered
the generator's program. It does not independently verify the semantics. The
round-trip gate is the only thing in the lane that breaks a shared-code path and
it does not cover the definition pages.

The circularity check is narrower than it reads. `~/verify_oneshot_circularity.py`
replaces the definition grammar's English with nonsense, regenerates and re-reads,
and returns strict 1.0 on 200 episodes, which does establish that no branch of
the reader is keyed to the particular English words. But it reads the first 200
rows of an ordered 800-row file, and those rows are two operations from one of
the four families. It is an uncommitted file in `$HOME` whose output was never
persisted; it had to be re-run to learn what it says.

### Claim N3. The round-trip gate passes at 10,752 of 10,752, and it is the strongest artifact in the lane

Confirmed by recount from `results/norm/roundtrip/records.jsonl.gz`: 10,752
items, 768 distinct frames, 14 shapes, exactly 768 per shape, four checks each
at 1.0000 and their conjunction at 1.0000.

The four checks are parse, structural identity, re-render and execute. The
re-render leg is the one that matters, because it requires the recovered
structure to re-render byte-identical text and so does not pass through shared
generator and parser code. No chance floor applies; it is a self-consistency
gate and `CORE.md` says so rather than dressing it as an accuracy.

### Claim N4. The typed core is exact everywhere except one relation family, and that exception is disclosed

Confirmed. `results/norm/corpus/`: 161,280 items, 768 frames, 16 relation
families, depths 1 to 8. All 41 cells read 1.000 on unambiguous items except
`inverse_chain`, which reads 1.000 at depth 1 and 0.000 at depths 2, 3, 4, 6 and
8. Exactly 114 items of 161,280 carry a "two pages are called X" refusal. Overall
raw accuracy 145,830 of 161,280 = 0.9042, and the entire 15,336 shortfall is
`inverse_chain` at depth 2 and above.

`CORE.md` also states in bold that the interpreter does not beat the hand-written
parser on `substitution_rule`, 0.988 against 0.992 over 23,400 items with hedge
rate 0.000 and a hedging canary at 0.000 forced. An honest negative, correctly
reported, and rarer than it should be.

### Claim N5, corrected. The reader's exactness on trained frames is pooled over an item set that is half memorisation-eligible

`src/norm/TRAIN.md` reports the 0.40M reader at 0.8982 and the 45M reader at
0.9211 exact on trained frames, and 0.5150 and 0.8125 on a held-out lexicon,
2,800 items each. All four recounted from
`results/norm/eval/{xs,l}/records_*_greedy.jsonl.gz` and confirmed.

What is not in that document, and exists on disk in `results/norm/verify/`
written four hours after it:

- `fresh.json` gives the rate at which a freshly drawn evaluation structure is
  already present in the 1,200,000-item training file: `lookup_general` 1.0000,
  `precedence` 1.0000, `exclusion` 0.9993, `inverse` 0.9987, `pair` 0.9987,
  `lookup` 0.9807, `priority` 0.7400, then falling away to `sum_chain` 0.0000.
- `novel.json` splits the headline: 3,674 seen items at 0.9997 exact, 3,326
  unseen items at 0.7859, pooling to the reported 0.8982.

The seven shapes `TRAIN.md` reports at 1.000 for the small reader on trained
frames are the same seven that `fresh.json` says are 74 to 100 percent already in
the training file. The words leak, novel, seen-in-training and duplicate appear
in none of `TRAIN.md`, `COMPARE.md` or `ONESHOT.md`.

So the correct statement of claim 1 in the outward-facing list is not 0.9209 flat.
It is 0.9997 on structures the reader has already seen and 0.7859 on structures it
has not, and the second number is the one that means anything about reading.

One thing checked and benign: `novel.json` carries both the first-2,800 pooled
value 0.898214 and the full-7,000 value 0.898143, so the prefix-reading practice
did not distort this particular number.

### Claim N6. The safe-failure result holds only for a page shape the reader has never seen

Confirmed at artifact level, and this bounds a claim that reads much more
broadly than it is.

`COMPARE.md` section 8 reports the shipped normalizer declining on 750 of 750
rather than naming a cell, and calls that a safe failure. Those 750 items are
shared-domain `pair` grids, a page shape the reader has never seen; `COMPARE.md`
says so two paragraphs earlier.

On trained frames the refusal rate is 0.0000. Over all twelve `train`-split cells
in `results/norm/compare/report_main.json`, the 45M reader has maximum none rate
0.0000, maximum hedge 0.0000, maximum declined 0.0000. On the frames it trained
on the normalizer answers every item and never declines. The safe-failure
property belongs to the unseen page shape, not to the system.

## Retrieval and the external comparison

### Claim T0. The external harness is calibrated, and it was wrong before it was

Confirmed, and this is what makes every LFM2 comparison in this document
readable. All figures n=200 seed 1234 unless stated, floor 0.2500, read directly
from the record files in `results/extern/bench/`.

| configuration | shots | accuracy | artifact |
|---|---:|---:|---|
| LFM2-350M, completion, bos token present | 5 | 0.4300 | `lfm2_350m_mmlu_completion_bos.json` |
| LFM2-350M, completion, no bos token | 5 | 0.3550 | `lfm2_350m_mmlu_completion.json` |
| LFM2-350M, chat template | 0 | 0.3950 | `lfm2_350m_mmlu_chat.json` |

The bos token is worth 7.5 points at n=200 and 12.2 at n=500 (0.4360 against
0.3140). The check that the calibrated configuration is the right one is that it
reproduces the model's published MMLU figure, 43.43, at 0.4300 and 0.4360. Every
comparison against LFM2 in this document uses the calibrated row.

Two things this calibration does not cover, and both matter. It fixes the
prompt format, not the scoring method: our generation-scored cells and the
log-likelihood cells are never subtracted from each other, because a model that
names no option scores zero on the first and cannot on the second. And it says
nothing about the two lanes' differing n: our checkpoint's best-supported figure
is at n=500 and LFM2's published-reproducing figure is quoted at both n=200 and
n=500, so a comparison should name which pair it is using.

The calibration is also the fault most likely to be re-introduced, because the
generated summary that many readers would reach for holds only the two
uncalibrated rows. See fault 3.

### Claim T1. Given the same pages, a matched-size general model converts them into accuracy and ours does not

Confirmed, with the effect smaller and less certain than the four-cell table
first read.

MMLU, log-likelihood scored, n=200, floor 0.2500, from `src/extern/FOURCELL.md`
and the record files under `results/extern/`.

| model | closed book | same pages in context | difference |
|---|---:|---:|---:|
| LFM2-350M | 0.4300 [0.363, 0.499] | 0.4500 [0.383, 0.519] | +0.020 |
| LFM2-350M, better retrieval | 0.4300 | 0.4850 [0.417, 0.554] | +0.055 |
| ours corpus-v1-8k, 375M | 0.2750 [0.218, 0.341] | see T3 | - |

Pages are worth about two points as the cell was originally configured. The
retrieval configuration was then swept and rerun on the same items with the
question and its options as the query, neural search and 20 results: 0.4850,
which is 5.5 points. Paired against closed book on the same 200 items that is 20
items retrieval-only against 9 closed-only, McNemar exact two sided p = 0.061.
So the best-configured arm does not clear significance at n=200, and the
two-point figure should not be quoted as though the ceiling were known.

At n=500 in a separate lane LFM2-350M reads 0.4360 [0.3932, 0.4798] closed book,
reproducing its published 43.43, which is the calibration for this whole battery
(`s3://decoupled-reasoner-009398924577/runs/real-v1-8k/results/mmlu_closed_lfm2-350m_n500_bos.json`,
`acc: 0.436`, `params_total: 354483968`).

### Claim T2, superseded. Retrieved pages carrying the answer lift LFM2 from 0.4300 to 0.7500

Dead. It was item selection, not treatment.

The contamination split put LFM2 at 0.7500 on the 20 items whose served pages
carried the gold answer string, against 0.4226 on the 168 where they did not.
Read as a treatment effect that is a 0.33-point lift from retrieval.

Killed by running the same 20 items closed book, with no pages at all. They
score 0.7000. McNemar exact p = 1.000, with one item retrieval-only and none
closed-only.

| arm | answer cell n | with pages | closed book, same items | McNemar p |
|---|---:|---:|---:|---:|
| published | 20 | 0.7500 | 0.7000 | 1.000 |
| control | 21 | 0.6667 | 0.6667 | 1.000 |
| new | 42 | 0.6429 | 0.6190 | 1.000 |

An item whose answer is findable on the web is an item this model already knows.
The `neither` cell has now been measured under three retrieval configurations
and has not moved off the closed-book 0.4300 [0.363, 0.499]. The split still has
to be kept, because it stops a lookup result being reported as a reasoning
result, but the effect of retrieval has to be read off the paired columns.

### Claim T3, corrected twice. Our checkpoint asks for pages on 0.2550 of MMLU items, and retrieval is not what stands between it and an answer

Confirmed at 102 of 400, and this supersedes two earlier readings.

The first reading was that the reader asks on about one item in twenty. That
number was never a rate at which the model asked for anything: it was the live
Exa search count off one log line of a run that was killed at 10 items, read as
a policy rate. Cache hits are invisible to a spend counter by construction. The
record file for that run is gone; the only surviving evidence is a single line
of `logs/extern/cell2.log`.

The second reading came from `src/extern/retrieval_ours.py`, which scored the
event as `n_rounds > 0 or stop_reason == "max_rounds"`. That condition means
different things with and without an index: with no index `<|retrieve|>` hits
the index-is-None guard and ends the trajectory, so every emission is counted;
with a web index the loop keeps decoding to collect query text and an emission
whose query runs past the token budget records no round. The legacy counter
therefore loses 0.0300 at a 256-token budget and 0.0425 at 64 tokens, and reads
lower in exactly the arm that matters.

Counting the `<|retrieve|>` token itself, which is the same event in every arm:

| arm | emitted / n | rate [95% CI] | legacy counter |
|---|---|---|---:|
| web index, greedy, 256 tokens | 102/400 | 0.2550 [0.215, 0.300] | 0.2250 |
| no index, greedy, 256 tokens | 102/400 | 0.2550 [0.215, 0.300] | 0.2550 |
| no index, sampled T=1.0 | 104/400 | 0.2600 [0.219, 0.305] | 0.2600 |
| no index, sampled T=0.8 p=0.95 | 98/400 | 0.2450 [0.205, 0.289] | 0.2450 |

The web and no-index arms agree item by item on 400 of 400, which they must,
since greedy decoding is deterministic and nothing before the first
`<|retrieve|>` depends on a serving surface. Sampling puts the rate in the same
place, so it is not a greedy artifact. On the 200-item subset the closed-book
lane scored, the rate reproduces at 0.2550 [0.200, 0.320].

What the corrected counter kills is the reading it was used for. "The reader
never requests retrieved text, so this is a policy failure rather than a
comprehension failure" rested on the undercount. The reader does request, on one
item in four, and chunks reach its trace on 88 of 400. Nothing follows.

The paired control, item by item against the same model with retrieval
unavailable:

| comparison | n | web only | no index only | both | neither | McNemar p |
|---|---:|---:|---:|---:|---:|---:|
| all items, strict | 400 | 0 | 0 | 4 | 396 | 1.000 |
| items that asked | 102 | 0 | 0 | 0 | 102 | 1.000 |
| chunks reached the context | 88 | 0 | 0 | 0 | 88 | 1.000 |

The informative denominator is 102, not 400. On the 298 items where the policy
never asks, the two arms are the same trajectory and agree token for token on
answer text, generated length and stop reason on 298 of 298, so those items
cannot disagree and counting them only dilutes the test. On the 102 that did ask
there is not one discordant pair, and on the 88 where a chunk entered the trace
the reader named an option zero times, with pages and without.

Every item this cell scores correctly is an item where retrieval served nothing
at all.

### Claim T4. Retrieval training on real documents teaches the policy to ask and to read, and buys nothing on MMLU

Confirmed. `real-v1-8k`, the same 8,000-step budget as `corpus-v1-8k` with a
mixture that is 0.5029 real by example count, from `src/realret/REALRET.md`.
Archived under `s3://decoupled-reasoner-009398924577/runs/real-v1-8k/`.

Asking. On MMLU with the live web tier, n=200 seed 1234, the query rate goes
from 0.325 (65 of 200) to 0.710 (142 of 200), and pages enter the context on
exactly those rollouts in both cases. Verified in
`runs/real-v1-8k/results/mmlu_agentic_{corpus,real}-v1-8k_n200.json`
(`issued_query` 0.325 and 0.71). The queries change from prompt fragments to
question-derived terms.

Reading. On held-out real-document episodes, greedy, free-text answers so the
floor is 0.000. Recounted from
`s3://.../runs/real-v1-8k/results/real_scores_{corpus,real}-v1-8k.json`:

| source | n | shipped before | shipped after | strict after | given gold page served |
|---|---:|---:|---:|---:|---:|
| hotpot_qa open | 568 | 0.0035 | 0.2782 [0.2429, 0.3164] | 0.2500 | 0.4051 |
| natural_questions open | 599 | 0.0033 | 0.2788 [0.2444, 0.3160] | 0.2354 | 0.4514 |
| trivia_qa open | 600 | 0.020 | 0.417 | 0.398 | 0.561 |

The lenient and strict columns are within 0.045 of each other, so this is not a
grader effect. Mean rounds on the multi-hop source go 1.40 to 2.11, so the
policy takes its second hop. The HotpotQA yes/no sub-cell, n=32, is reported
separately at 0.5625 against a 0.5 floor and carries nothing; pooling it into
the open cell would have inflated the headline, and the lane does not.

MMLU. Closed book, n=500, floor 0.250: 0.2640 to 0.2820. Both intervals contain
chance. Verified at `acc: 0.264` and `acc: 0.282` in
`runs/real-v1-8k/results/mmlu_closed_{corpus,real}-v1-8k_n500.json`. With the
same web pages both checkpoints stay flat, 0.2600 matched format and 0.2340
native for the older one, 0.2700 and 0.2620 for the newer. Naming a letter at
all goes from 0.02 to 0.045.

This lane is also the counterexample to the archiving hazard. Its report cites
every record under `/mnt/nvme/realret/...`, which no longer exists, but all 57
objects including the per-rollout jsonl files were separately archived to
`s3://decoupled-reasoner-009398924577/runs/real-v1-8k/`, so every number above
was recomputable after the box was terminated.

Contamination was checked rather than assumed: 16,630 benchmark stems of eight
words or more scanned against 2.03 million documents, 37 exact matches in the
raw build and 0 in what was trained, after `src/realret/decontam.py` removed 41
episodes of 182,556.

### Claim T5. Learning to chain two hops over real Wikipedia does not transfer to chaining over an invented relation system

Confirmed, and this is the most useful negative in the lane.

`chain_rule` forced choice, held-out band, n=1,536, floor 0.250: 0.2520 before,
0.2441 after. Chance corrected that is 0.003 to -0.008, at the floor on both
sides. `weighted_chain` generation, n=1,536: 0.2051 to 0.1849.

The same checkpoint that moved HotpotQA from 0.004 to 0.278 and started taking
its second hop did not move this cell at all. Whatever `chain_rule` requires, it
is not the retrieval habit and not multi-hop practice on real text.

Caveat carried in the source: these cells were measured on the held-out band of
the diversity corpus rather than on the exact item selection `RETRAIN.md` used,
so the before column is this lane's own measurement of the control checkpoint
and not a quote of that document's number.

### Claim T6. The BM25 gate broke ties toward the lowest document index, and that moved recorded numbers in both directions

Confirmed. `BM25Index.top` in `src/train/retrieval.py` keeps the best score under
a strict `>`, so every exact tie goes to the earliest document, and
`minimal_pages` orders its tables so the table needed at step i sits behind the
table needed at step 0 in every episode.

Re-running the same rungs under a position-blind tie break, same questions,
seeds and graders, 400 chains per cell:

| recorded | was | is | denominator |
|---|---:|---:|---|
| R1w chain pass@1, depth two | 0.0025 | 0.0925 | 400 chains |
| R1w step one, depth two | 0.0050 | 0.2000 | 400 rollouts |
| R1w step one, depth three | 0.0050 | 0.1725 | 400 rollouts |
| R1o chain pass@1, depth two | 0.1875 | 0.0550 | 400 chains |
| R1 chain pass@1, depth two, control | 0.2050 | 0.2075 | 400 chains |

R1w rising proves little on its own. R1o falling is the half that is hard to get
by accident: it read 0.1875 because its needed page won every tie for sitting
early, exactly as R1w read 0.0025 for losing every one. The 75x gap between the
two rungs was page order and nothing else. The BM25 ranking columns barely move
between the halves, 0.437 tie misses before and 0.424 after, which is the check
that the fix changed the serving and not the ranking. Accuracy given the needed
page stays between 0.90 and 0.95 throughout, so none of this is the model
getting better at the lookup.

Chance floors are stated per cell and never merged: six desks gives 0.1667 on a
step and 0.0278 at depth two, 0.0046 at depth three.

R2w was not re-run. Its number in that table is inferred and labelled as such.

### Claim T7. Page order does not explain the composition wall

Confirmed and it is the counterweight to T6. R0 sits at 0.0000 lenient and
0.0000 forced at depths two and three under six different page orders, 400
rollouts each, while the table holding the answer goes from served 1 time in 400
to 33 times in 400. The needed page was made 33 times more reachable and the
accuracy did not move. R0 was then re-run under the tie-break fix itself, so the
new gate cannot be said to have moved the baseline: depth two reads 0.0025
against 0.0000 and depth three 0.0000 against 0.0000.

Artifacts `results/retrieval/r0_order.json`, `r0_order_rows.jsonl.gz`,
`r0_content.json`.

The change not made, and stated in the source rather than fixed: between 0.55
and 0.82 of misses in every cell are score losses rather than tie losses, mostly
to the preamble, which wins 0.40 of all rounds. On a two-page set the preamble
scores 3.06674 against the routing table's 3.036587, a one percent margin. That
is a ranking-function problem, it is proposed, and it is not done.

## What is dead, with the number that killed it

Including four I propagated myself.

### The composition wall as a capacity limit

The wall near three or four sequential steps was read as a property of the
substrate, and H10 attributed it to irreversible autoregressive commitment.

Killed by the training-ceiling arms. Eight arms from the same base varying only
the maximum plan depth in training: the depth-eight arm scores 0.99 on
depth-eight chains where the published arm scores 0.02, and emitted length
follows the diagonal to each arm's own ceiling and then flattens on it exactly.
The extrapolation constant is zero, not small. There was no three-step horizon;
there was a three-step training set.

Every conclusion that treated a wall near three as evidence about a mechanism
was reading the training distribution, and that includes the plan-head
comparison, the vocabulary ladder and the latent-recurrence sweep, all of which
train through depth three and evaluate past it.

With one caveat that has to travel with this entry: no artifact for those eight
arms could be located anywhere. See the unverifiable section. The capacity
reading stays dead, because it never had positive evidence, but the
distributional reading that replaced it currently rests on a prose table, and
the evidence to cite for it is the corpus retrain's plan-length result instead.

### The positional collapse as a substrate result

I argued this from three flips: the 93M rung reverses against the 45M rung, arm
D reverses against its own baseline, and four training-signal interventions
moved which convention was chosen without removing the choice. A property that
reverses under scale and under training changes while never disappearing looked
like a property of the substrate.

Killed by the 167M rung, at 0.6341 key-first against 0.6063 value-first, gap
0.028 against the 45M rung's 0.413, recounted from
`results/system/eval/xxl167/records_mode_greedy.jsonl.gz`. It disappears. We had
not looked above 93M.

The correction needs its own correction, and it is in claim R4 above: on the
eight shapes where the axis actually reaches the page, the 167M rung reaches
symmetry at 0.3938 and 0.3392, where the 45M rung was at 0.7450 on the order it
could do. The asymmetry goes; the competence does not arrive.

### The retrieval failure as purely a policy failure

`src/extern/fourcell.py` emitted a section concluding that the reader never
requests retrieved text, so the failure is a policy failure rather than a
comprehension failure. I repeated it.

Killed by the corrected emission counter. The reader emits `<|retrieve|>` on 102
of 400 passes, 0.2550 [0.215, 0.300], and chunks reach its trace on 88. It asks
on one item in four. On those 88 it names an option zero times, with pages and
without. The premise the claim rested on is gone, and what the run supports is
narrower: this checkpoint cannot produce an MMLU answer, and its retrieval
behaviour is not what stands between it and one.

### The query rate of one in twenty

I propagated 0.05. It was the live Exa search count off one log line of a run
killed at 10 items, read as a policy rate, with cache hits invisible to it by
construction. The measured rate is 0.2550 on 400 items, reproducing at 0.2550
[0.200, 0.320] on the 200-item subset the closed-book lane scored, and stable
across greedy and two sampling temperatures. No counter over those 10 items
gives 0.05; one over twenty does, and one is the live search count on that line.

### That retrieved pages carrying the answer lift LFM2 to 0.7500

Killed by the paired closed-book run on the same 20 items: 0.7000 without any
pages, McNemar p = 1.000. Item selection, not treatment.

### That the model induces operators from an unseen page

Killed by the transposition audit: on pages whose operand roles were transposed
after training, the model followed the training identity on 678 of 678 items and
the page on 0 of 678.

With it went three dependent claims: that induction works and only planning
fails; that gold operators change nothing, since plan_execute and oracle_ops
differ in 5 of 26 cells by up to 0.420; and that depth costs nothing once a
correct plan exists, which holds only under the one trained page wording and
reads 0.087 to 0.207 under three others.

### That the depth-two and depth-three composition cells were partial successes

Killed by the pairing. The checkpoint writes a byte-identical plan for a page
stating left to right and a page stating right to left in 750 of 750 pairs, and
the two arms sum to 0.480 + 0.533 = 1.013. That is chance across the pair. Any
reading of 0.480 as half the compositions succeeding is wrong.

### That the design fails safe by refusing malformed structures

Killed by the refusal census. On trained frames the refusal rate is 0.0000 and
the malformed rate is 0.0000 against a wrong-structure rate of 0.0791 at 45M and
0.1093 at 93M. Every failure on surface the reader was trained on is a structure
the interpreter accepts and executes to a wrong answer. Refusals appear only as
the surface moves away from training, and even there the safe-to-unsafe ratio
never reaches one in fifteen cells.

### That frame boundedness is a property of this architecture

Killed by the corpus retrain, which moved macro chance-corrected accuracy on
`substitution_rule` from -0.120 to 0.943 by widening the training distribution.
Three of four never-trained sentence shapes read at ceiling afterwards. It was a
corpus property.

### That milestone A is met

Withdrawn. Correction 1 removed one family of three as a grading artifact and
showed the near-zero controls are consistent with copying. Correction 2 showed
that under matched presentation the effect is frame matching: `processing`,
which shares no content word with the trained idiom, scores 0.840, while
`routing_frameb`, which keeps every content word and changes only the sentence
frame, scores 0.030. Nouns cost 0.13; sentence shape costs 0.94. And a
fifty-line regex outscores the model on the identical items, 1.000 against
0.968, and beats it on every untrained family.

## Claims whose supporting artifact could not be located

These are not disputed. They are unsupported until an artifact turns up, and
they should be quoted with that attached or not quoted.

### The MMLU re-measurement at n=1000, reading 0.2450

`src/e3/E3.md` re-measures the 375M corpus checkpoint at three sample sizes and
records 0.2750 at n=200, 0.2640 at n=500 and 0.2450 at n=1000, citing
`/mnt/nvme/e3eval/mmlu_ref_n{200,500,1000}.json`. `/mnt/nvme` is instance store
on worker 2, which has been terminated, and there is no mirror anywhere under
`s3://decoupled-reasoner-009398924577/`. The n=1000 row cannot be checked.

What does survive, read directly:

| n | accuracy | floor | artifact | status |
|---:|---:|---:|---|---|
| 200 | 0.2750 | 0.2500 | `results/extern/bench/ours_corpus-v1-8k_mmlu.json`, `acc: 0.275` | confirmed, in the checkout |
| 500 | 0.2640 | 0.2500 | `s3://.../runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json`, `acc: 0.264` | confirmed, durable |
| 1000 | 0.2450 | 0.2500 | `/mnt/nvme/e3eval/mmlu_ref_n1000.json` | gone |

So the best-supported figure is 0.2640 at n=500, and 0.2750 at n=200 is the one
the repository can produce on its own. 0.2450 should be recorded as
unverifiable rather than quoted, and I had been propagating it as the headline.

The reading it was used for survives without it. The point of the n=1000 row was
that the checkpoint's apparent score is a positional prior rather than reading,
and that is established at n=200 from a surviving artifact: predictions split
A/B/C/D as 146/7/35/12, 0.730 of the mass on the first option, against a gold-A
share of 0.300 in the drawn sample. Every interval at every n contains chance.

### The training-ceiling arms, which are what killed H10

This is the most consequential entry here and it was found while writing this
document.

`PREREGISTERED.md` records "H12 result, 2026-08-29: the composition wall was the
training ceiling": eight arms from the same 350M base, same worlds, same seeds,
8000 steps at batch 32, varying only the maximum plan depth in training, with a
table of mean emitted plan steps and accuracy for arms `d1s1`, `d3s1`, `d6s1`
and `d8s1` at evaluation depths 3 to 32. It is the result that declares H10 dead
and reframes the composition wall as distributional, and `THESIS.md` and the
rest of the programme are written on top of it.

No artifact for it could be found. Searched, all negative:

- no record file under `results/` matching the arm names; `results/opgraph/`
  holds the earlier direct / trace / plan_execute / oracle_plan experiment,
  which is the one correction 3 audited, and not these arms
- no object anywhere under `s3://decoupled-reasoner-009398924577/`
- no script or config in `src/` or `scripts/` referencing `d1s1`, `d3s1`,
  `d6s1` or `d8s1`
- nothing in `logs/` or `~/logs`
- `git log --all --diff-filter=A --name-only` shows no file ever added to the
  repository whose name contains `ceiling`, `d8s1` or `h12`
- the working directories that hold other sweeps, `~/sweep`, `~/opg`, `~/runs`,
  hold different experiments

The only occurrence of the arm names anywhere on the box is the table in
`PREREGISTERED.md` itself.

What follows. The claim that the composition wall was a capacity limit is still
dead, because a claim of a capacity limit needs positive evidence and never had
it. But the distributional reading that replaced it is not currently supported
by a locatable artifact either, and the confident statements built on it
("H10 is dead", "the extrapolation constant is zero rather than small", "any
depth curve that stops near three is measuring the training distribution")
should be read as resting on an unlocatable table until the arms are found or
re-run.

Partial independent corroboration does exist and should be weighed. The corpus
retrain, a separate experiment with artifacts, reports emitted plan steps
tracking required steps at all 18 trained lengths and extrapolating past the 48
training maximum, with accuracy past 48 at 0.000. That supports the general
shape of the distributional reading, on different arms, and it is the evidence
to cite instead. It does not reproduce the H12 table.

### The one-shot figure of 0.9644

Checked twice, independently, and it is in nothing. Not in any markdown file,
not in `results/norm/**`, not in any template, and `git log --all -S"0.9644"`
returns no commit. The digit string `9644` occurs under `results/` only as a
substring of longer floats in unrelated lanes.

The one-shot lane's own headline is 1.0000 forced-choice strict on each of four
operation families, which is a different and stronger number attached to a much
narrower claim, and it is set out in claim N2 with its five caveats. Anyone
holding 0.9644 should replace it with 1.0000 on 850 items over 170 operations,
and read the caveats before quoting either.

### The 0.680 rule-application headline

Recorded in `THESIS.md` and propagated for days. A falsification lane re-ran the
shipped script against the shipped checkpoint and could not find any artifact
producing 0.680; the same script gives 0.958 at n=500. This was reported as
stale with no provenance before this document, and it is repeated here because
it is the origin case for the rule that every number must have a persisted
artifact and the path must be named.

### The 4B against 27B comparison

`THESIS.md` twice states that a controlled comparison of a 4B against a 27B of
the same generation shows factual knowledge retaining 92 percent under a 6.75x
parameter cut while search depth retains 30 to 69 percent, and `PREREGISTERED.md`
gives it as one of three bases for P1, the composition-first prediction.

No artifact for it could be found: nothing in `results/`, nothing anywhere under
`s3://decoupled-reasoner-009398924577/`, no script that would produce it. The
only hits when grepping `results/` for the model name are inside a checkpoint
zip and a gzipped rollout dump, which is binary noise rather than a record.

It is quoted as a measurement made here. It should either be re-sourced as a
citation to somebody else's published numbers, with the reference, or dropped.
As it stands it is the second of the two foundations of P1 that cannot be
checked.

### The six objectives that failed at zero

Stated in `THESIS.md`, in `PREREGISTERED.md` as the first basis for P1, and in
`src/opgraph/README.md`. This one is partially locatable and the distinction
matters: RL run artifacts do exist, locally under `~/runs/rl-350m-{a,b}` and
`~/runs/rl-probe` and in S3 under `runs/rlskill/`, `rlskill2/`, `rlvr/`,
`rlweb/` and `rule-test/`, so the underlying runs are real. What does not exist
is any record enumerating the six objectives and their scores together. Only one
of the six is named anywhere, in `src/disc/SLATE.md`: multi-attempt revision
against a programmatic verifier.

So "six objectives ended at 0.000" cannot be checked as stated. It should be
replaced by a table naming each objective, its run and its number, which the
runs appear to support.

### Cell 2's original finding

The pass behind the published cell 2 was killed at 10 items and its conclusion
was read off 20 passes. Its record file is gone. The only surviving evidence is
one line of `logs/extern/cell2.log`. The n=400 rerun supersedes it entirely.

### R2w under the corrected tie break

`src/retrieval/RANKING.md` gives R2w's depth-two value as 0.03 to 0.06 and
labels it inferred rather than measured. The rung was not re-run. That is
correctly marked in the source and is repeated here so the number is not lifted
out of it.

## The measurement faults

Numbered, with what each would have done to a reported number if it had not been
caught. Several flattered us. All were found internally, which is the only
reason any surviving number here is worth anything.

1. Reading the first N rows of an ordered file as though it were a sample.
   The frame-group evaluation files carry 7,000 items; an earlier pass read the
   first 2,800. The `qframe` file lists its 35 key-first frames before its 35
   value-first ones, so 2,800 of 7,000 was every key-first item and no
   value-first one. Effect: the `qframe` column was a key-first-only score
   standing beside mixed-position scores from four other groups, in a lane whose
   entire finding is a key-position split. All groups are now read whole.
   (`src/system/THRESHOLD.md` section 2.)

2. The same shape again, on a rate rather than an item set. The e3 pretrain ETA
   was taken from the quietest 200-step window, 5.47 s/step, and reported as the
   run rate. End to end the run does 6.22 s/step, 13.7 percent overhead. Effect:
   40.2 hours reported against 46.1 actual, a six-hour understatement, and a
   schedule built on a number chosen where it looked best.

3. A generated report that stopped regenerating and went unnoticed for 152
   commits. `results/extern/bench_summary.md` holds only the two UNCALIBRATED
   LFM2 configurations, 0.3950 chat zero-shot and 0.3550 completion without the
   bos token, and not the calibrated 0.4300. Effect: quoting it puts LFM2's MMLU
   3.5 to 7.5 points below its calibrated value, narrowing the gap in our
   favour, on the one comparison the thesis turns on. Verified against the
   record files: `results/extern/bench/lfm2_350m_mmlu_chat.json` acc 0.395,
   `lfm2_350m_mmlu_completion.json` acc 0.355,
   `lfm2_350m_mmlu_completion_bos.json` acc 0.430, all n=200 seed 1234. Its
   generator would now crash on 11 of 12 record files before writing a row.

4. A generator that rewrote its own report on every run. `src/extern/fourcell.py`
   wrote the whole of `FOURCELL.md` each time it ran. Effect: it would have
   silently deleted the cell 4 rerun and the cell 2 n=400 sections, for which it
   has no record files, restoring the retracted "policy failure" reading and the
   withdrawn 0.7500 answer cell into the published table. It now splices at a
   sentinel. Restoring that loss is how the bug was found. (Commit `daadcc5`.)

5. Hand-written prose pasted verbatim into a generated report by that same class
   of generator. `results/extern/verdict.md` asserts the reader "almost never
   emits a retrieval request", with near-zero Exa spend as the evidence, and is
   copied into `LIQUID.md` on every run. The n=400 record shows 0.2550 emission,
   73 live searches and 255 cache hits. Effect: a retracted claim that
   re-propagates on every regeneration rather than decaying.

6. A spend counter read as a policy rate. The claim that the reader asks on about
   one item in twenty came from the live Exa search count on one log line of a
   run killed at 10 items. Cache hits are invisible to a spend counter by
   construction. Effect: understated the retrieval policy by a factor of five,
   0.05 against the measured 0.2550, and the record file for that run no longer
   exists.

7. An event counter whose definition changed with the condition it measured.
   `src/extern/retrieval_ours.py` scored a query as `n_rounds > 0 or stop_reason
   == "max_rounds"`. Without an index, `<|retrieve|>` hits the index-is-None
   guard and every emission counts; with a web index, an emission whose query
   runs past the token budget records no round. Effect: undercounts by 0.0300 at
   a 256-token budget and 0.0425 at 64 tokens, and only in the arm that has
   retrieval attached, which is the arm the comparison is about.

8. A paired control whose denominator was mostly items that could not disagree.
   The cell 2 McNemar test was run over all 400 items. On the 298 where the
   policy never asks, the two arms are the same trajectory and agree token for
   token on answer text, generated length and stop reason on 298 of 298. Effect:
   dilutes the test with items retrieval never touched. The informative
   denominator is 102, and on those there is not one discordant pair.

9. Item selection reported as a treatment effect. The contamination split put
   LFM2 at 0.7500 on the 20 items whose served pages carried the gold answer,
   against 0.4226 where they did not. Those same 20 items score 0.7000 with no
   pages at all, McNemar p = 1.000. Effect: a 0.33-point retrieval lift that is
   item difficulty. An item whose answer is findable on the web is an item this
   model already knows.

10. A rescore that mixed two differently graded runs. A contamination-label
    rescore compares a published arm labelled by a character detector against a
    control and a new arm labelled by whole-token matching, all three in one
    table; the claimed reproduction of "0.105 against 0.100" is 21/200
    token-labelled against 20/200 char-labelled. The general form of this fault
    has happened here before, and both report builders now refuse to run:
    `src/norm/opdoc.py:check_fresh` and `src/system/threport.py` raise, rather
    than warn, when a records file is newer than the report quoting it.

11. A containment grader, and the grader check that did not cover it. The
    environment grader accepts any prediction containing the gold string within
    six tokens of slack, so naming both candidates scores correct whichever is
    right. `threshold_rule` hedges on 94.3 percent of its answers and moves from
    0.985 to 0.009 once hedging is disallowed. Effect: one family of three
    carried a three-family macro headline by a third. The grader check that
    cleared this harness quoted seven of eight tested answer shapes; the omitted
    one is the only shape with a nonzero false-positive rate, where handed the
    text of a wrong option the grader calls it correct on 5 of 400.

12. A retrieval gate whose tie break was page order. `BM25Index.top`
    (`src/train/retrieval.py`) keeps the best score under a strict `>`, giving
    every exact tie to the earliest document, and `minimal_pages` orders its
    tables so the page needed at step i sits behind the page needed at step 0.
    Effect in both directions: R1w's depth-two chain pass@1 was understated
    0.0025 against 0.0925 and R1o's was overstated 0.1875 against 0.0550, both
    on 400 chains. The 75x gap between those two rungs was page order and
    nothing else.

13. Two different chance floors for the same cells, one in the report and one in
    the record files. `src/retrieval/ordercurve.py:165` and
    `rungeval.py:170` compute `chance_per_step = 1/alpha` and `chance_per_chain
    = (1/alpha)**depth` with `alpha = len(episode["alphabet"])`, which is the
    union over all levels and is 36, while the answer at any one step is one of
    6. `src/retrieval/RANKING.md` states the correct floors, 0.1667 per step and
    0.0278 at depth two. The two collide at depth two, since 1/36 = (1/6)^2,
    which is why it is easy to miss, and diverge by a factor of 214 at depth
    three. Effect: no published number is wrong, because the report uses the
    correct floor and every swept cell reads 0.0000 anyway. The hazard is live
    for anyone rescoring from the record file: RANKING's own depth-three caveat
    reads 0.0100 as sitting just above a 0.0046 floor, and against the record
    file's 2.1e-5 the same number would read as 470 times chance.

14. A comparison whose losing arm was mostly items that never ran. The
    general-knowledge cell reports LFM2 0.5769 against ours 0.0000 at n=26. Only
    7 of the 26 items actually ran; 17 failed with "slot W8 is not in the text".
    Effect: reads as "answered 26, got 26 wrong" when it is "could not be
    prompted on 17 of 26", and it was reported upward as a decisive loss on that
    axis. It does not carry that weight.

15. A generator defect that made a wrong answer land on the right value.
    `src/corpus/plans.py:render_tree` writes binary infix for any node with more
    than two children, so a four-operand item prints two of its operands.
    11,887 of 32,000 training and 1,196 of 3,199 held-out whole-plan items are
    underdetermined, and on those a wrong plan reaches the right value 0.642 of
    the time. Effect: every plan table now reports the determinate subset only.

16. Benchmark items sitting verbatim in the training corpus. The real-document
    build scanned 16,630 benchmark stems of eight words or more against 2.03
    million documents and found 37 genuine matches, MMLU items such as the
    number of books in the new testament appearing as TriviaQA training
    questions or inside their pages. Effect if uncaught: MMLU scored partly on
    memorised training items. `src/realret/decontam.py` removed 41 episodes of
    182,556 and the trained pack scans clean at 0.

17. A report generator that splices the wrong table under five headings.
    `scripts/norm_compare_md.py` substitutes markers by plain `str.replace` over
    a sorted set, and `str.replace` has no word boundary, so `TABLE_MAIN` is
    substituted inside `TABLE_MAIN_EXACT` and `TABLE_MAIN_HEDGE`, `TABLE_HOME`
    inside `TABLE_HOME_NONE` and `TABLE_HOME_RANGE`, and `TABLE_TRANSPOSE`
    inside `TABLE_TRANSPOSE_SPLIT`, leaving the residue `_EXACT`, `_HEDGE`,
    `_SPLIT`, `_RANGE`, `_NONE` glued to the wrong table. The generator's own
    guard passes because the residue no longer begins with `TABLE_`. Visible in
    the committed `src/norm/COMPARE.md` at lines 311, 407, 475, 745 and 773.
    Effect, and it is the worst in this list because it inverts a meaning rather
    than shifting a value: under the heading "the rate at which each system names
    nothing" the document displays the forced-choice accuracy table, so a reader
    sees the 45M reader "naming nothing" at 1.0000 on training frames when the
    true none rate is 0.0000 and 1.0000 is its accuracy. Four other sections
    likewise display a table that does not support the sentence above it. And
    the file named `t_main_hedge.md` in fact holds the none rate, so no table
    anywhere in `COMPARE.md` reports the hedge field at all, despite the
    document's own section 1 promising that the hedge rate travels with every
    cell.

18. A chance floor taken from the item's option count where the correct null is
    the majority class. `~/oneshot_floor_check.json` records the four one-shot
    ladder pools with stated floors of 0.5000, 0.3333, 0.2500 and 0.3333 against
    majority-class baselines of 0.80, 0.80, 0.60 and 0.60, because each pool has
    only five distinct question keys. Effect: `ONESHOT.md` says the network
    "clears the floor" at k=256 on one operation, 0.5500 against 0.5000, and at
    k=1024 on a second, 0.3800 against 0.3333. Against the correct null those are
    0.5500 against 0.80 and 0.3800 against 0.80, and `beats_majority` is false in
    all 26 recorded rungs. The network clears nothing at any rung. The library's
    1.0000 survives either null. The floor check exists and says this; the
    document predates it and was never updated. Compounding it, the 100 rows per
    pool are 5 keys by 20 wording draws, and the standard error in the same file
    is computed as though they were 100 independent items; the script computes a
    per-key breakdown and then discards it without writing it out.

19. A training-set-overlap audit that exists on disk and is in no document.
    `results/norm/verify/fresh.json` gives the rate at which a freshly drawn
    evaluation structure is already in the 1.2M-item training file: 1.0000 for
    `lookup_general` and `precedence`, 0.9807 to 0.9993 for four more.
    `results/norm/verify/novel.json` splits the headline into 0.9997 on 3,674
    seen structures and 0.7859 on 3,326 unseen ones. The seven shapes `TRAIN.md`
    reports at 1.000 are the same seven that are 74 to 100 percent memorisable.
    Effect: the reported 0.8982 is a pool over an item set that is 52.5 percent
    memorisation-eligible, and the honest decomposition was measured, persisted,
    and never written down. The words leak, novel and seen-in-training appear in
    none of the three lane documents.

20. A freshness guard with a non-recursive glob, hiding a control that qualifies
    the headline. `src/norm/opdoc.py:check_fresh` globs `oneshot/*.jsonl.gz` and
    cannot see `results/norm/oneshot/verify/`, which holds five newer record
    files written two hours after the report. Those files are the frame-novelty
    control for the one-shot ladder: the same fine tune at the same k reads
    0.5200 on held-out frames and 0.7200 on trained frames. Effect: `ONESHOT.md`
    states the ladder items come from frames the normalizer never trained on and
    then compares library against network on them, and about a third of the gap
    is frame novelty rather than operation novelty. The control was run, it is
    persisted, and it is in no document.

21. Twelve of twenty-eight generated tables never reach their document. Five are
    swallowed by fault 17; seven more are written on every build with no marker
    referencing them at all, including the whole composition-depth-by-frame-group
    measurement, which exists only as five files on disk. Effect: no number is
    wrong, but a measurement that was made and paid for is invisible, and the
    fact that the files regenerate every run is why nobody noticed.

22. A failure dump that a passing run does not clear.
    `src/norm/roundtrip.py` writes `failures.json` only when there are failures,
    so a clean run leaves the previous run's file in place. The directory
    currently presents a 1.0000 summary written at 05:59 beside a 134 KB
    failures file written at 05:39. No reported number is affected; it is a trap
    laid for the next reader.

Fault 1 has now appeared three times in three lanes, which is why it is first.
Its third instance is `~/verify_oneshot_circularity.py`, which reads the first
200 rows of an ordered 800-row file and so covers two of eight operations from
one of four families, while its conclusion is generalised to the whole set.

Faults 3 through 9, 11 and 14 were found by an adversarial verification pass over
the external-comparison lane; 1, 12 and 13 in the system and retrieval lanes; 2,
15 and 16 in the e3, corpus and real-document lanes; 17 through 22 in the
normalisation lane. Faults 17 to 22 are concentrated in the plumbing between
artifact and document rather than in the measurement code, which is the pattern
worth noticing: the graders in that lane are the best on the project and the
documents built from them are the least reliable.

### Two standing hazards that are not yet faults

Neither has corrupted a number, and both are the conditions under which the
faults above happened.

Artifacts that live in one place. The four role-intervention arms are complete
with per-item records, and they exist only under
`s3://decoupled-reasoner-009398924577/role-back/`, not in the checkout, so a
reader of the repository cannot reach them from the repository.

Record paths on instance store. `src/realret/tables.md` cites every one of its
record files under `/mnt/nvme/realret/...`, which was worker 2 and is now
terminated. That lane survives only because it was separately archived to
`s3://.../runs/real-v1-8k/`. The e3 lane was not so lucky; see the unverifiable
section.

## What is open

### The pre-registered hypotheses, and which of them still have a test

`PREREGISTERED.md` carries P1 to P3 and H7 to H12. Their current status, with
the caveat that two of them turn on artifacts recorded above as unlocatable.

| id | claim | status |
|---|---|---|
| P1 | composition degrades earliest and steepest as substrate shrinks | untested as stated; two of its three stated bases cannot be checked |
| P2 | recurrence selectively raises composition depth | not run |
| P3 | capacity versus trainability, via oracle-isolated curves | partially run; the ladder gives a capacity reading on one axis only |
| H7 | the failure is the continuation decision, not computation | supported by the minimal repro, superseded in scope by H12's reading |
| H8 | stated-in-a-chapter near 0.514, derived-by-computation near 0.000 | refuted; both families sit below their own guessing floors |
| H9 | plan representation is the binding constraint | its motivating result was withdrawn by correction 3 |
| H10 | a three-step autoregressive planning horizon | declared dead by H12, whose arms cannot be located |
| H11 | the vocabulary bottleneck between reasoning steps | not run |
| H12 | the wall is a plan-length and symbol-count generalisation failure | the arms cannot be located; corroborated in shape by the corpus retrain |

P1 deserves naming because it is the project's first prediction and the one the
programme was built around. Its three stated bases are the six objectives at
zero, which is partially locatable but never enumerated; the pointer head, whose
artifacts exist; and the 4B against 27B comparison, which has no artifact at
all. A prediction can still be true with weak stated bases, but P1 has not been
tested by the substrate sweep it was written for, because that sweep stops at
167M.

H8 is worth separating because it is the one pre-registered prediction run to
completion on an independently built instrument, with its gate run first, that
returned a clean negative against itself. It predicted `stated_in_a_chapter`
near 0.514 and `derived_by_computation` near 0.000. On the universe's own pages,
greedy, from `src/mathgen/EVAL.md`:

| family | n | floor | accuracy | chance corrected |
|---|---:|---:|---:|---:|
| stated_in_a_chapter | 593 | 0.141 | 0.000 | -0.164 |
| derived_by_computation | 518 | 0.154 | 0.004 | -0.178 |

Both families sit below their own guessing floors, so the split the instrument
was built to measure carries no signal at all. Under the pre-registration that
is the third outcome: not that answer source does not matter, but that this
instrument is harder than the skillacq families for a reason that is not answer
source. The prediction was wrong and the pre-registration says what to conclude,
which is the point of writing it down.

### The measurements that would move things

The 355M rung of the ladder, which would bracket the perception threshold from
above rather than only from below. It needs about 234,000 steps, some 64 hours
on one L40S, and was dropped as unaffordable rather than measured. Everything
said about a threshold here is bracketed on one side only.

An architecture in which role is a structural field the decoder must fill,
rather than a label an auxiliary head guesses. The four role arms tested four
specific interventions on the training signal, and correction 4 shows capacity
does the job at 167M, but nothing has tested making role a typed channel at a
size where the positional habit still appears.

The chaining failure, which is the one negative that has survived four
independent interventions and is where the project's remaining value sits. What
has not been tried is the obvious next thing: whether an external structure that
holds the intermediate result, rather than a token stream that must carry it,
moves the two-hop cell off its floor.

Re-running or locating the training-ceiling arms, since a claim that reframed
the whole composition question should not rest on a table.

The e3 pretrain reaching its budget, which is the only thing that would tell us
whether a from-scratch 375M can read at all. It is a third of the way there.

## The state of the thesis

The falsifiable target in `THESIS.md` is a from-scratch sub-1B system
competitive with Qwen3.8-27B, with milestones A through F.

There is no 1B model. There is no benchmark win. There is no benchmark result
above chance.

The largest from-scratch checkpoint is `corpus-v1-8k` at 375,440,384 parameters
(`params_total`, read from the record file). On MMLU, five-shot completion,
floor 0.2500:

| model | n | accuracy | 95% Wilson | artifact |
|---|---:|---:|---|---|
| ours corpus-v1-8k, 375M | 200 | 0.2750 | [0.2178, 0.3407] | `results/extern/bench/ours_corpus-v1-8k_mmlu.json` |
| ours corpus-v1-8k, 375M | 500 | 0.2640 | [0.2273, 0.3043] | `s3://.../runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json` |
| ours real-v1-8k, 375M | 500 | 0.2820 | [0.2443, 0.3230] | `s3://.../runs/real-v1-8k/results/mmlu_closed_real-v1-8k_n500.json` |
| LFM2-350M, calibrated | 200 | 0.4300 | [0.363, 0.499] | `results/extern/bench/lfm2_350m_mmlu_completion_bos.json` |
| LFM2-350M, calibrated | 500 | 0.4360 | [0.3932, 0.4798] | `s3://.../runs/real-v1-8k/results/mmlu_closed_lfm2-350m_n500_bos.json` |

Every one of our intervals contains chance. LFM2-350M reproduces its published
43.43 at 0.4360, which is the calibration for the whole battery, and it has
21M fewer parameters than our checkpoint.

A fourth number, 0.2450 at n=1000, has been quoted on this project including by
me. Its record file was on worker 2's instance store and is gone. It is in the
unverifiable section and should not be used.

The reason for the flatness is worse than noise, and this part is supported by a
surviving artifact. The checkpoint puts 0.730 of its answer mass on option A at
n=200, splitting A/B/C/D as 146/7/35/12, against a gold-A share of 0.300 in the
drawn sample. It is not guessing uniformly and it is not reading. The answer
policy is degenerate in a specific, measurable way.

Asked to answer by free generation rather than by log likelihood, it names one
of A to D on 18 of 400 items, and on those 18 it is at chance: 0.2222 [0.090,
0.452] against 0.2500. The flat 0.0100 it scores is a formatting failure
stacked on a chance-level reader, and the two have to be reported apart. The
grader was exercised on synthetic answer shapes before that number was
believed, and one of those checks has a hole (fault 11).

The strict form of the thesis was already dead before most of this work. The
pre-registered kill test of 2026-08-26 put a substrate trained with no natural
language at 0.0000 against 0.2053 for the same size trained on ordinary text,
and `SPEC.md` section 7 says what that means. Every checkpoint measured since is
the weakened form: a model that has read ordinary text. Descriptions of a
"fact-free" model elsewhere in `THESIS.md` do not describe anything currently in
use.

Milestone A, genuine acquisition of an unseen skill with controls ruling out
memorisation, was declared provisionally met and is withdrawn. Milestones B
through F have not been attempted.

The 375M from-scratch pretrain on `regime_e3` is the current attempt to move the
first number. It is at step 9,060 of a planned 26,700, about 34 percent, loss
2.677, 15.6 hours in against an end-to-end estimate of 46.1. At step 2,000 it
read MMLU 0.2250 [0.2002, 0.2519] and its modal share had gone from 0.464 at
step 1,000 to 0.589, walking toward the old checkpoint's 0.695 rather than away
from it. No claim rests on either accuracy at that budget and the lane says so.
The one axis moving the right way is retrieval, which the model is picking up
out of the pretraining mixture with no fine-tuning teaching it: 0.000 at step
1,000, 0.070 at step 2,000.

### What remains standing

Something does, and it is not the headline.

The measurement apparatus, which is the most transferable thing here. Reports
refuse to build from records newer than themselves, in two independent
builders. Every accuracy carries a denominator, a per-item chance floor, a hedge
rate and a forced-choice score beside any lenient one. Nothing is pooled across
families. A hand-written parser runs beside the model on the same items wherever
one can be written, and it usually wins, which is itself reported. Instruments
are required to reproduce a prior run cell for cell before their new numbers are
read. Sixteen measurement faults have been found and named, several of which
flattered us, and they were found here rather than by anyone else.

Three positive results at full strength, and the strongest of them is not
neural. A symbolic library reads an operation off one page of prose and applies
it at 1.0000 forced choice on 850 items over 170 operations, against floors of
0.29 to 0.37, where the network on the same items is at 0.00 to 0.12 and emits
the right structure zero times in 6,736 attempts. That is the acquisition the
thesis is about, performed by the part of the system that has no weights. Value
reading: a page with identical wording and permuted values moves the answer with
the page. And role binding from syntax is learned from this task rather than
supplied by English pretraining, carried by a 354M model failing where a 167M
model passes.

The uncomfortable reading of the first of those, which should be stated rather
than left implicit: on the one axis where this project has a clean acquisition
result, the neural substrate contributes nothing and a symbolic reader does all
of it. That is evidence for the decoupling thesis in a form the thesis did not
ask for, and it is not evidence that a small network can acquire anything.

One clean negative that cost real compute and is worth more than a weak
positive: chaining a step's input from a previous step's retrieved result does
not come from a wider training distribution, does not come from real multi-hop
practice on Wikipedia, and is not a page-order artifact. Each of those
interventions is recorded with the number showing it worked at what it was for.

And one capability boundary with a parameter count on either side of it: below
about 167M this reader commits to a positional convention on unseen sentence
forms, above it it does not. That is the only threshold this project has
located, it is bracketed from below only, and the 355M rung that would
characterise it above was dropped as unaffordable rather than measured.

## Lanes not yet re-verified in this document

Verification of `src/disc/` with `src/falsify/`, and `src/corpus/` with
`src/e3/`, is still in progress. Claims drawn from those two lanes and not
recounted here are marked in place; everything else in this document was read
out of the artifact it names.
