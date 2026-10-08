# Findings

The full research record, organised by theme. Every entry gives the claim, its
numbers, its status, and the file it came from. Paths are within the combined
repository: `decoupled-reasoner/` for the main program, `latent-transfer/` and
`latent-translation/` for the two earlier projects.

Status words are used consistently. Confirmed means the artifact supports the
claim at the strength stated. Corrected means an earlier reading of the same
measurement was replaced. Refuted means the claim was tested and failed.
Withdrawn means the claim was taken back without a replacement measurement.
Open means measured but unresolved. Registered means written down with a
falsification condition and not yet run.

Where a number is reported as uncertain, the reason is stated. Two claims that
appear in the governing documents have no locatable artifact and are marked as
such rather than repeated as results.

---

## 1. The governing hypothesis and the target

### The two objects

The program is framed as a comparison between two computational objects rather
than two model sizes. X is one large static network whose capability is a
function of parameter count. Y is a small permanent engine plus external
knowledge, autonomous acquisition, temporary skill formation and adaptive
test-time computation, with the actual learning happening at inference.
Comparing X and Y by parameter count is close to the wrong abstraction.

Status: confirmed. Source: `decoupled-reasoner/THESIS.md`

### The capability function is asymmetric

For X, capability is approximately a function of parameters alone. For Y it is a
function of permanent parameters, accessible external knowledge, retrieval and
search quality, available test-time compute, temporary learned state, and the
ability to acquire new abstractions. The last term is the one ordinary
retrieval augmentation does not have.

Status: confirmed. Source: `decoupled-reasoner/THESIS.md`

### The falsifiable target

Stated as a target rather than a prediction, against Qwen3.8-27B as the
reference point: a 7B system at parity is a 4x parameter-efficiency result, 4B
is nearly 7x, and under 1B is more than 27x. Books, indices, the web and any
other environmental information are excluded from the denominator, because a
person is not credited with the parameters of a library. Nothing in the
repository reports a measurement against this target.

Status: open. Source: `decoupled-reasoner/THESIS.md`

### The design the target implies

NRM-1B is specified as roughly a 1B decoder plus a 0.15B evidence encoder, with
four departures from a plain decoder: a partitioned context, evidence
cross-attention, a recurrent core with static depth, and a pointer head, plus
answer-block refinement, three-stage training and three falsification
conditions. The hardware contract comes from an external H200 lab and fixes
kernel shapes, a 9.4 MB launch floor, static shapes, batch amortisation and no
custom kernels.

Status: confirmed as a specification. No model at this size was trained.
Source: `decoupled-reasoner/ARCH.md`

### The named wall

`THESIS.md` names composition as the current wall: what is not established is
composing or computing over an acquired rule.

Status: confirmed. Source: `decoupled-reasoner/THESIS.md`

### Two supporting numbers behind that framing that have no artifact

The same section cites a controlled 4B-against-27B comparison of one model
generation showing factual knowledge retaining 92 percent under a 6.75x
parameter cut while search depth retains 30 to 69 percent, and states that six
independent objectives have failed at zero to teach computation over an acquired
rule. Both appear in `THESIS.md` as written. The audit records that the
4B-against-27B comparison has no artifact anywhere and should be re-sourced as
somebody else's published numbers or dropped, and that the six-objective claim
cannot be checked as stated, because the runs exist in S3 but no record
enumerates the six objectives and their scores together and only one of the six
is named anywhere.

Status: uncertain, pending re-sourcing. Sources: `decoupled-reasoner/THESIS.md`
and `decoupled-reasoner/src/STATE.md`

---

## 2. The pre-registered kill test

### The decision rule, fixed before the test

If regime C reaches at least 90 percent of regime A's score, the strict form
survives and Phase 2 tests it. Between 60 and 90 percent it is weakened to a
frequency-ordered resident knowledge diet plus teacher distillation. Below 60
percent the strict form is dead and the writeup says so plainly.

Status: confirmed. Source: `decoupled-reasoner/SPEC.md` section 7

### The verdict

Regime C, trained with no natural language at all, scored 0.0000 contains-answer
on all 250 naturalized items on every seed. Regime A at the same 350M class
scored a mean of 0.2053 across three seeds (0.228, 0.196, 0.192). The C-to-A
ratio of means is 0.0000 with a bootstrap 95 percent interval over items and
seeds of [0.0000, 0.0000] on 10,000 replicates, below the 0.6 threshold. The C
checkpoints score 0.66 to 0.72 on their own-format held-out worlds, so the
failure is reading the knowledge stated in prose rather than learning nothing.
Dated 2026-08-26.

Status: refuted (the strict form of the thesis). Sources:
`decoupled-reasoner/src/STATE.md` claim K1, `decoupled-reasoner/PLAN.md`,
`decoupled-reasoner/PREP.md`

### Phase 2 scope after the verdict

Phase 1 is recorded as complete and Phase 2 re-scoped to the weakened form with
regime D, with verified RunPod prices, three owner-side blockers and a five-item
risk register from a nine-agent literature verification.

Status: confirmed. Source: `decoupled-reasoner/PLAN.md`

---

## 3. Reading a page: values, frames and rules

### Value reading survives attack

With page wording byte-identical and only the value set cyclically permuted, the
answer follows the page: 0.9380 against 0.0078 on `substitution_rule` (n=258,
floor 0.2012) and 0.9608 against 0.0120 on `exception_rule` (n=332, floor
0.5030). A position-based copier lands on the pre-permutation answer 71 percent
of the time; the model lands there 0.8 percent of the time. Three attacks were
run against this and all three failed. The audit attaches the ceiling: what is
established is value-sensitivity within a trained sentence frame, not rule
execution.

Status: confirmed. Sources: `decoupled-reasoner/src/STATE.md` claim D3,
`decoupled-reasoner/THESIS.md` Correction 1

### The acquisition claim does not survive a change of surface form

On `substitution_rule`, forced-choice accuracy is 0.970 in the native wording,
the surface the RL stage trained on, and 0.045, 0.045 and 0.015 in three other
ordinary English idioms, against a 0.200 chance floor and a 0.111 page-word
floor. Claims of inference-time skill acquisition are not supported. What is
supported is frame-conditioned value binding.

Status: refuted. Sources: `decoupled-reasoner/src/disc/TEMPLATE.md`,
`decoupled-reasoner/THESIS.md` Correction 2

### Frame, not vocabulary, carries the result

With retrieval removed and one document in the store, `processing` shares no
content word with `routing` and scores 0.840 against `routing`'s 0.970, while
`routing_frameb` keeps every content word and moves them into `abstract`'s frame
and scores 0.030. Swapping the nouns costs 0.13; keeping the nouns and swapping
the sentence shape costs 0.94.

Status: confirmed. Source: `decoupled-reasoner/src/disc/TEMPLATE.md`

### One rule family was a pure grading artifact

The native renderer on `threshold_rule` names both candidate labels in 100
percent of greedy answers, and 1.000 under the shipped containment grader
becomes 0.000 under forced choice. At temperature 0.7 the same cells read 0.964
hedge, 0.988 shipped and 0.024 forced. Counted across the three-family macro
average, `threshold_rule` names both candidate words in 94.3 percent of its
answers, fifteen pairs of items with byte-identical output and opposite gold
answers were all thirty graded correct, and disallowing hedging moves it from
0.985 to 0.009. After forced choice and against a chance floor of 0.401, only
0.292 of the headroom above guessing is real rule application.

Status: refuted. Sources: `decoupled-reasoner/src/disc/TEMPLATE.md`,
`decoupled-reasoner/THESIS.md` Correction 1,
`decoupled-reasoner/PRIMITIVES.md`

### The 0.680 headline, in three stages

Stage one: the recorded 0.680 rule-application figure is stale and its
provenance could not be found. Re-running the shipped script on the shipped
checkpoint gives textbook 0.958, wrong textbook 0.002 and blank 0.000 at n=500,
and 0.968 / 0.001 / 0.000 at n=1000. The chance floor for the task is 0.401, not
0.000. An independently built native renderer gives 0.966 pooled at the same
temperature on textbook evidence.

Stage two: the artifact does exist. Its checkpoint field reads `rl-000250.pt`,
RL step 250, where the shipped model is `final.pt` at step 3000. So 0.680
against 0.958 is a step gap rather than a fabrication. The step-250 checkpoint
has since been deleted, and the 0.4018 chance floor for that item set was never
stated beside 0.680 in any document.

Stage three: `ARCH.md` section 1 still justifies the whole design with the
retracted form, citing a 350M model reading stated rules at 0.680 with the
correct page against 0.002 with a different system's page and 0.000 with a
blank page. The governing architecture document is out of sync with `THESIS.md`.

Status: corrected, twice. Sources: `decoupled-reasoner/THESIS.md` Correction 1,
`decoupled-reasoner/src/disc/TEMPLATE.md`, `decoupled-reasoner/src/STATE.md`
claims D1 and D2, `decoupled-reasoner/ARCH.md`

### The "correct page retrievable" framing does not survive

Placing a twin system of the same family in the store drops accuracy to 0.463,
with the model naming the twin's candidate words 48.8 percent of the time
against its own 47.5 percent. A roughly fifty-line regex over the top-ranked
pages scores 1.000 against the model's 0.968 on identical items, while generic
value-blind heuristics reach only 0.387, the nearest invented word to a question
keyword. Claims of the form "with the correct page retrievable" describe work
the model does not do.

Status: refuted. Source: `decoupled-reasoner/THESIS.md` Correction 1

### Three ceilings were corpus properties

A retrain on the diversity corpus moved three of four measured failures. On
`substitution_rule` forced choice, frames at shape distance 0.30 and above go
from 0.009 to 0.997. Macro chance-corrected score moves from -0.120 to 0.943 on
`substitution_rule` and from -0.208 to 0.691 on `exception_rule`. Emitted plan
steps where 48 are required go from 2.65 to 47.69, and emitted distinct symbols
where 5 are needed from 1.06 to 4.98. `threshold_rule` forced choice goes from
0.008 to 0.990. The extrapolation constant is no longer zero, with the caveat
that accuracy past 48 steps is 0.000 even where the emitted length is right.

Status: corrected. Sources: `decoupled-reasoner/THESIS.md` 2026-08-30,
`decoupled-reasoner/src/corpus/RETRAIN.md`

### Template sensitivity, measured under matched presentation

An earlier reading recorded a confounded swing from at most 0.19 to 0.84 at
depth one between an abstract notation and the routing idiom, with presentation
moving at the same time. Under matched presentation the gap is 0.960 forced
(`routing` 0.970 against `abstract` 0.010) in the retrieval-free condition, so
template accounts for the entire recorded gap and then some.

Status: corrected. Sources: `decoupled-reasoner/src/disc/TEMPLATE.md`,
`decoupled-reasoner/src/disc/SLATE.md`

### One sentence shape resists everything

After retraining, `archive__tablepipe` reads 0.375 and `abstract__tablepipe`
0.260 in their two frames, while the other three never-trained sentence shapes
read 0.985 to 1.000. `archive__tablepipe` has lexical distance 0.000 from
`archive__tablecolon`, a frame the corpus trained 17,000 times, so what defeats
it is a colon becoming a pipe.

Status: an unresolved residual. Source:
`decoupled-reasoner/src/corpus/RETRAIN.md`

### The rule-family negative the primitive suite is built against

Three relation types never seen in training scored at or below chance under
balanced scoring, while a fifty-line regex parser scored above 0.98 on identical
items.

Status: confirmed. Source: `decoupled-reasoner/PRIMITIVES.md`

### The one axis pointing the other way

Under paraphrase, direct answering falls from 0.480 to 0.187 while `oracle_plan`
holds flat near 0.59 across all eight depths, which Correction 2 calls the
single place the architecture direction currently earns its keep. This sits in
tension with Correction 3 one day later, which reports a different
`oracle_plan` arm reading 0.087 to 0.207 under three untrained wordings, so it
should not be read as general frame robustness.

Status: confirmed as measured, with that tension recorded. Source:
`decoupled-reasoner/THESIS.md` Corrections 2 and 3

### Two positive levers

A pointer head selecting spans from evidence lifts copy-heavy accuracy from
0.021 to 0.514, while being slightly worse where arithmetic is needed. RL
against programmatic verifiers moved held-out accuracy from 0.448 to 0.854 in
nine minutes on one GPU, and from 0.000 to 0.812 on rule application in 216
steps.

Status: confirmed. Sources: the pointer-head figures are in
`decoupled-reasoner/THESIS.md`; the RL figures are in
`decoupled-reasoner/ARCH.md`. `ARCH.md` describes the pointer head in section
4.4 but attaches no accuracy figures to it, so the pointer-head numbers should
be cited to `THESIS.md`.

---

## 4. The symbolic reader against the neural reader

### The clean acquisition result is symbolic

A library with no gradient step in its path reads an operation off one page of
prose and applies it at 1.0000 forced choice on 850 items over 170 distinct
operations, against per-family chance floors of 0.29 to 0.37. On the same items
the neural reader is at 0.00 to 0.12 and never once emits the right structure in
6,736 attempts, greedy or sampled. The audit attaches two limits: the effective
denominator is 170 rather than 850, since the 850 items cover 170 distinct
operations, and the parser baseline beside it is vacuous rather than passed.

Status: confirmed. Source: `decoupled-reasoner/src/STATE.md` claim N2

### The reading of that result

On the one axis where this project has a clean acquisition result, the neural
substrate contributes nothing and a symbolic reader does all of it. That is
evidence for the decoupling thesis in a form the thesis did not ask for, and it
is not evidence that a small network can acquire anything.

Status: confirmed, and stated explicitly in the source rather than left
implicit. Source: `decoupled-reasoner/src/STATE.md`

### The one-shot figure of 0.9644 does not exist

The number 0.9644 appears in no document in the repository, in no record file,
and in no commit, checked twice independently. The lane's actual headline is
1.0000 on a much narrower claim.

Status: withdrawn. Source: `decoupled-reasoner/src/STATE.md` claim N1

### A training-set-overlap audit that existed on disk and in no document

`novel.json` splits the reported 0.8982 reader headline into 3,674 seen
structures at 0.9997 exact and 3,326 unseen at 0.7859, pooling to 0.8982. The
pooled figure is therefore over an item set that is 52.5 percent
memorisation-eligible. The words leak, novel and seen-in-training appear in none
of the three lane documents.

Status: corrected. Source: `decoupled-reasoner/src/STATE.md` claim N5 and fault
19

### Milestone A

Milestone A, genuine acquisition of an unseen skill with controls ruling out
memorisation, was declared provisionally met and is withdrawn. Milestones B
through F have not been attempted. Under matched presentation the effect is
frame matching, with nouns costing 0.13 and sentence shape costing 0.94.

Status: withdrawn. Source: `decoupled-reasoner/src/STATE.md`

---

## 5. Composition and serial depth

### The minimal repro and its wall

On the minimal invented-referral repro, depth d is d chained table lookups.
Sampled at temperature 1.0 with 4 samples per question and 100 questions per
depth, depth one scores 0.5375 pass@1 and 0.950 pass@4, with 0.99 mean retrieval
rounds and 0.905 well formed. Depths two, three and four score 0.0000 on both,
zero correct answers in 1200 rollouts. Greedy on the same files reads 0.84 at
depth one and 0.00 at depths two, three and four. The wall sits between depth
one and depth two and is total.

Status: confirmed. Sources: `decoupled-reasoner/src/disc/SLATE.md`,
`decoupled-reasoner/PREREGISTERED.md` H7

### Error compounding is dead as an explanation

Independent lookups at the measured depth-one rate predict about 0.289 at depth
two. Observed is zero in 400, and pass@4 is also zero. In `SLATE.md`'s
hypothesis table this is H4, recorded as dead; H5, substrate capacity, is a
different hypothesis and is recorded as alive.

Status: refuted (error compounding). Sources:
`decoupled-reasoner/src/disc/SLATE.md`, `decoupled-reasoner/PREREGISTERED.md`

### The halting signature

Mean retrieval rounds fall as the problem deepens: 0.99, 0.73, 0.56, 0.54. The
policy issues fewer queries exactly when more evidence is needed.

Status: confirmed. Source: `decoupled-reasoner/PREREGISTERED.md` H7 and H9

### The re-keying rescue

Handing the gold intermediate back as the key to a fresh sub-question, on the
same questions, pages, retriever and grader, moves depth-two chains from 0.0000
to 0.2050 pass@1 and from 0.0000 to 0.5600 pass@4: 82 correct chains out of 400
against 0 out of 400, against a 0.0278 chain floor. The substrate executes a
lookup keyed by a handed value at 0.4575 against 0.4850 for one keyed by the
question, and 0.915 against 0.907 given the page. What it cannot do is write its
own previous answer back into its next query.

Status: confirmed. Sources: `decoupled-reasoner/src/disc/RESCUE.md`,
`decoupled-reasoner/src/STATE.md` claim D4

### Re-keying alone does not rescue, and why

With the gold key supplied but the whole depth-d page set left in place, depth
two scores 0.0025 and depths three and four 0.0000. This is not a halting
failure: the policy still retrieves on 0.98 of rollouts at every step. It is a
retrieval-selection failure.

Status: confirmed. Source: `decoupled-reasoner/src/disc/RESCUE.md`

### Document position under a near-tied BM25

Holding the page count fixed and moving only the needed table to position one
takes depth-two step one from 0.0050 to 0.3825 and chain pass@1 from 0.0025 to
0.1875. The gold page is served on 0.417 of those step-one rollouts against
0.007 before. The BM25 scores are a near-tie and the tie goes to the earlier
page.

Status: confirmed. Source: `decoupled-reasoner/src/disc/RESCUE.md`

### The depth curve measures two things at once

Because the page order in the baseline rung was never varied, the published
depth curve measures composition and retrieval position together, and how much
of the wall is retrieval position is not answerable from these runs.

Status: corrected. Source: `decoupled-reasoner/src/disc/RESCUE.md` correcting
`decoupled-reasoner/src/disc/SLATE.md`

### The wall is not a wording artifact

Depth two is 0.000 in every one of the nine renderers and in both the gold-pages
and retrieval-free page conditions.

Status: confirmed. Source: `decoupled-reasoner/src/disc/TEMPLATE.md`

### Asking for an intermediate measures nothing on this checkpoint

The rung that asks the model to name each intermediate and its length-matched
null control score identically, 0.0050 at depth one and 0.0000 below, and both
drop mean retrieval rounds from 0.98 to 0.01. Appending any sentence at all is
what breaks the policy, not the instruction the sentence carries. Any future
intervention phrased as extra words in the question is untestable on this
checkpoint.

Status: withdrawn. Source: `decoupled-reasoner/src/disc/RESCUE.md`

### The training ceiling

Eight arms from the same 350M base, same worlds, same seeds, 8000 steps at batch
32, varying only the maximum plan depth in training: the depth-eight arm scores
0.99 on depth-eight chains where the previously published arm scores 0.02. The
extrapolation constant is zero rather than small, since no arm generalises one
step past its training maximum. The published arm is reproduced by the
depth-three arm.

Status: confirmed as recorded, with the artifact caveat in section 17. Source:
`decoupled-reasoner/PREREGISTERED.md` H12 result, 2026-08-29

### H10 is dead

There is no three-step autoregressive horizon; there was a three-step training
set. Every conclusion that treated the wall near three or four as evidence about
a mechanism was reading the training distribution.

Status: refuted. Source: `decoupled-reasoner/PREREGISTERED.md`

### Three architecture comparisons invalidated in flight

The plan-head comparison, the vocabulary ladder and the latent-recurrence sweep
all train through depth three and evaluate past it, so each would produce a wall
at three regardless of its mechanism. They need rerunning with the training
ceiling raised, and every depth curve needs its training maximum reported beside
it.

Status: corrected. Source: `decoupled-reasoner/PREREGISTERED.md`

### Relational breadth did not move

Relational breadth is identical across all arms, 1.00 at breadth one to three
and 0.00 at four to six. The manipulation that moved sequential depth left
breadth untouched, which is the cleanest evidence that breadth is a different
failure.

Status: confirmed. Source: `decoupled-reasoner/PREREGISTERED.md`

### Novel composition did not move and is the remaining problem

Every arm emits about 1.0 distinct operator symbols where two are needed, at
chance, including the arms trained with more symbols. Those arms taught
cross-page chains rather than two interchangeable binary operators, so the
stronger form of the manipulation is untested.

Status: open. Source: `decoupled-reasoner/PREREGISTERED.md`

### A breadth curve that is not one

`plan_execute` reads 0.24 to 0.42 at breadth four to six, above both oracles,
because two matched errors cancel. It is not a breadth curve and must not be
read as one.

Status: recorded as a trap. Source: `decoupled-reasoner/PREREGISTERED.md`

### No composition horizon has a number

Nothing in range saturates. The largest plan ever written across arms is 1, 2,
3, 4, 10, 10, so locating a horizon needs arms deeper than eight. The corpus
carries plans to 48, and the plan parser caps at 32 steps and must be raised
first or long plans score as parse failures.

Status: open. Source: `decoupled-reasoner/PREREGISTERED.md`

### The first measured trade-off

The depth-eight arm has the worst paraphrase induction of any arm and about a
third of the shallower arms' paraphrase accuracy. Depth is bought against
induction robustness at a fixed step budget.

Status: confirmed. Source: `decoupled-reasoner/PREREGISTERED.md`

### The representation gap that bounds everything beneath it

At depth eight, `plan_execute` is 0.013 and `oracle_plan` is 1.000. The 0.987
between them is the representation gap on this task, and every condition is
scored as the fraction of that gap it recovers at each depth rather than as a
raw accuracy. Handing the model gold operators instead changes nothing:
`plan_execute` and `oracle_ops` agree to three decimals at every depth, so the
loss is concentrated in emitting the plan.

Status: confirmed. Source: `decoupled-reasoner/PREREGISTERED.md` H9

### Chaining fails inside the training distribution

After the corpus retrain, the consumed training pack holds 1,228 two-hop
`chain_rule` items and 1,232 two-hop `inverse_chain` items. Held-out accuracy is
`chain_rule` 1.000 at one hop and 0.220 at two against a 0.250 floor (n=50),
`inverse_chain` 0.760 and 0.180, `weighted_chain` 1.000 and 0.039, and
`modular_apply` 0.000 at every depth on both bands. Training on real multi-hop
retrieval moved HotpotQA from 0.004 to 0.278 and left `chain_rule` at its floor,
0.2520 to 0.2441. The same checkpoint writes a correct 48-step plan over an
expression printed in its prompt.

Status: confirmed as a failure inside the training distribution. Sources:
`decoupled-reasoner/src/corpus/RETRAIN.md`, `decoupled-reasoner/THESIS.md`
2026-08-30, `decoupled-reasoner/src/STATE.md` claims C2 and T5

### Intervals correct the reading of the hop curve

The E3 harness recovers every published hop figure exactly and adds intervals.
At n=50, `chain_rule` depth 2 is 0.220 with a 95 percent Wilson interval of
[0.1275, 0.3524], so depths 2, 3 and 4 are indistinguishable from chance rather
than below it.

Status: corrected. Source: `decoupled-reasoner/src/e3/E3.md`

### Operator induction from a page was not tested by the corpus

The operator-graph arm answers 0 of 689 items toward the page and 689 of 689
toward training, and 0 of 293 and 293 of 293 at the operator level, reproducing
the recorded 0 of 678 and 678 of 678 and 0 of 290 and 290 of 290. The result
stands unmoved because nothing aimed at it.

Status: confirmed, unmoved. Source: `decoupled-reasoner/src/corpus/RETRAIN.md`

### What killed the induction reading

On pages whose operand roles were transposed after training, the model followed
the training identity on 678 of 678 items and the page on 0 of 678. The
`oracle_plan` row that is 1.000 through depth eight holds only under the one
trained wording and reads 0.087 to 0.207 under three others. The depth-two and
depth-three arms sum to 0.480 + 0.533 = 1.013, which is chance across the pair
rather than partial composition.

Status: refuted. Source: `decoupled-reasoner/THESIS.md` Correction 3, 2026-08-29

---

## 6. Role binding and the parser gap

### Where the collapse lives

On the held-out sentence mode the 45M rung (`l45`, 45,483,008 parameters) reads
key-first items at 0.7302 of 3528 and value-first at 0.3177 of 3472 greedy,
0.7171 and 0.3131 sampled, while on trained frames both positions are fine at
0.9206 against 0.9211. The eight-shape new-keys group, where the rule line's
wording is the only channel naming the key, reads 0.7450 (n=2016) against 0.0000
(n=1984), a gap of +0.7450. The other three question groups are within about
0.10 of symmetric. Three shapes (`inverse`, `priority`, `precedence`) are exact
on 252 of 252 key-first items and 0 of 248 value-first ones.

Status: confirmed. Sources: `decoupled-reasoner/src/role/ROLE.md`,
`decoupled-reasoner/src/system/THRESHOLD.md`

### The target is unambiguous in the text

The hand-written parser reads the value-first half of the held-out sentence mode
exactly, 1302 of 1302, and 93 of 93 on each of the seven affected shapes
separately, and reads 1.0000 on every cell of every split. The modal-by-shape
floor is 0.1026 key-first and 0.0864 value-first. The binding is present and
unambiguous; what the network gets wrong there, it gets wrong on its own.

Status: confirmed. Sources: `decoupled-reasoner/src/system/THRESHOLD.md`,
`decoupled-reasoner/src/role/ROLE.md`

### The failure is representational, not distributional

Counted off the 1,200,000 items the network actually saw, the seven shapes
scoring exactly 0.0000 on value-first items each saw value-first order as 0.4978
to 0.5006 of their own draw, between 42,567 and 42,918 examples, spread over all
five trained sentence modes at 8,362 to 8,910 each. `THESIS.md` records the same
range as 42,567 to 42,917. This is the first failure in the program known to
survive the data fix that would be tried on it.

Status: confirmed. Sources: `decoupled-reasoner/src/system/THRESHOLD.md`,
`decoupled-reasoner/THESIS.md` 2026-08-31

### Nearest-template transfer predicts the opposite of what happens

The held-out sentence whose nearest trained neighbour agrees with it, at 0.7778
similarity and the same key position, is the half that fails at 0.3177. The half
whose nearest neighbour disagrees reads 0.7302.

Status: refuted (nearest-template transfer). Source:
`decoupled-reasoner/src/role/ROLE.md`

### The slot-parity shortcut is real but not sufficient

Fitted on trained frames and applied unchanged, slot-index parity reads role at
0.6793 key-first and 0.8024 value-first on the held-out mode, over 22,835 and
22,464 slots, against a majority-class rate of 0.56. A shortcut, not a
sufficient one, which is what makes the auxiliary-head arm a fair test.

Status: confirmed. Source: `decoupled-reasoner/src/role/ROLE.md`

### The minimal-pair draw, verified row by row

Over all 600,000 slots-of-two the file holds 394,367 minimal pairs that agree on
structure, shape and invented words and differ only in the key-position field,
of which 342,796 have differing gold targets. Pair-aware bucketing makes a step
6.3 percent smaller, 150.64 rows and 7,445.5 target tokens per batch against the
baseline's 160.84 and 7,949.0 at the same 32,768 budget, with the step count
held at 30,000. That cost is stated rather than corrected.

Status: confirmed. Source: `decoupled-reasoner/src/role/ROLE.md`

### The auxiliary head's labels

Labels are derived from gold targets and checked twice: they agree with the
held-out mode sidecar on 7,000 of 7,000 items, and over 1,200,000 training items
10,278,854 slot mentions are named by the structure, split 3,457,247 key only,
4,313,462 value only and 2,508,145 both.

Status: confirmed. Source: `decoupled-reasoner/src/role/ROLE.md`

### Four interventions, none of which closed the gap

All four arms ran at the 45M rung with the same 490 training frames, the same
1,200,000 training items, the same 30,000 steps and the same seed 1. Baseline
0.7302 / 0.3177 (gap 0.413), reproduction 0.7112 / 0.3119 (0.399), minimal pairs
0.7863 / 0.3787 (0.408), auxiliary role head 0.5519 / 0.2632 (0.289), pairs plus
head 0.2639 / 0.5942 (-0.330). Every intervention changed which convention was
chosen and none changed whether one was chosen. The arm specification is in
`ROLE.md`; the prose outcome is in `LFM2.md`, which carries no arm-spec numbers.

Status: refuted (the interventions). The substrate conclusion drawn from them is
withdrawn, below. Sources: `decoupled-reasoner/src/role/ROLE.md` for the arm
specification, `decoupled-reasoner/src/role/LFM2.md` and
`decoupled-reasoner/THESIS.md` 2026-09-02 for the outcome

### The substrate conclusion, withdrawn

The section concluding that the asymmetry is a property of the substrate rather
than of the data is withdrawn. The four arms still stand as measurements; the
conclusion drawn from them does not.

Status: withdrawn. Sources: `decoupled-reasoner/THESIS.md` 2026-09-02 and
Correction 4, `decoupled-reasoner/src/STATE.md` claim R3

### The collapse flips with scale, then disappears

Training both rungs on the same token budget had left the larger one
undertrained. The 93M rung had half the 45M rung's tokens per parameter, 10.38
against 21.36 counting source tokens and 2.55 against 5.24 counting only the
tokens the loss falls on, and fit its own training file worse, 0.01779 against
0.01320 over the last 5,000 steps, which is the signature of undertraining. The
claim that more parameters do not buy surface generalisation is therefore not
made from that pair.

At a matched budget the 93M rung gains on trained and held-out-question frames
and flips the positional collapse: `l45` reads 0.7302 key-first and 0.3177
value-first while `xl93match` reads 0.3243 and 0.7252 on the same data and axis.
Pooled, the two rungs read 0.5256 and 0.5231 and look identical, which hides the
collapse.

At a matched budget the 167M rung (`xxl167`, 167,376,384 parameters, 110,271
steps) reads 0.6341 key-first and 0.6063 value-first, a gap of 0.028 against
`l45`'s 0.413. The property does not survive scale, so it is not a property of
the substrate. The perception threshold sits between 93M and 167M. Nobody had
looked above 93M.

Status: corrected. Sources: `decoupled-reasoner/THESIS.md` 2026-09-01 and
Correction 4, `decoupled-reasoner/src/system/THRESHOLD.md`,
`decoupled-reasoner/src/role/LFM2.md`, `decoupled-reasoner/src/STATE.md` claim
R3

### The correction to that correction

The aggregate pools fourteen question shapes and key position only reaches eight
of them. On those eight, `xxl167` reaches symmetry at 0.3938 against 0.3392
where `l45` was at 0.7450 against 0.0000: more parameters cost 0.35 on key-first
and bought 0.34 on value-first. The aggregate improvement Correction 4 reports,
0.5256 to 0.6203, is carried almost entirely by the six shapes the axis does not
reach, which go from 0.7103 / 0.7413 to 0.9544 / 0.9624.

Status: corrected. Source: `decoupled-reasoner/src/STATE.md` claim R4

### An external 350M model shows the same asymmetry

LFM2-350M (354,483,968 parameters, trained to convergence by someone else, never
exposed to this corpus) writes a key-on-the-left pair on 0.8805 of the pairs it
reproduces on key-first pages and a value-first one on 0.3479 on value-first
pages, against a 0.5 floor and a parser that reads every cell at 1.0000. It
collapses on all six statement modes, not only the one withheld from the
program's own reader. Its worst cell is `mapping`, whose value-first line is an
explicit statement of the relation in ordinary English, at 0.9777 [0.9594,
0.9878] (n=448) against 0.0905 [0.0666, 0.1217] (n=420); its best value-first
cell is `imperative` at 0.6453.

Status: confirmed. Source: `decoupled-reasoner/src/role/LFM2.md`

### Which convention is chosen depends on the prompt; that one is chosen does not

Open generation of the role word, with no options, reads 0.2121 key-first and
0.8517 value-first, opposite in sign to the 0.8805 / 0.3479 arrow result, and
four of the seven formulations sit at their floor.

Status: confirmed. Source: `decoupled-reasoner/src/role/LFM2.md`

### The narrow claim that survives

Reading role independently of position in an unfamiliar rule sentence is taught
by this task rather than supplied by English pretraining. LFM2-350M fails it
with the English and without the task; `xxl167` passes it with the task at a
third of the parameters; the 45M and 93M rungs have the task and lack capacity.
There is no substrate result here.

Status: corrected to this narrower form. Source:
`decoupled-reasoner/src/role/LFM2.md`

### A symbol-level view of the same split

The 45M reader keeps the role of 0.9880 of key-first symbols (22,835) against
0.5128 of value-first ones (22,464), and flips 0.0119 against 0.3920.

Status: confirmed. Source: `decoupled-reasoner/src/role/LFM2.md`

### The pre-registered holdout dissociation

A prediction written into `src/system/THRESHOLD.md` before either arm ran held
on 2026-08-31. The split withholding a statement mode (`b45`) collapses on
value-first, 0.6165 key-first against 0.2471, while the split withholding a
whole question-form value (`c45`) stays balanced at 0.7440 against 0.7611, at
n about 3500 per cell. The held-out statement mode loses two thirds of its
accuracy when the value is named first.

Status: confirmed. Sources: `decoupled-reasoner/THESIS.md` 2026-08-31,
`decoupled-reasoner/src/system/THRESHOLD.md`

### The contrasting case that does have a data fix

Fine tuning on a draw carrying both operand orders takes reading of the
transposed page from 0 of 750 to 462 of 750 and the wrong untransposed key order
from 733 of 750 to 258 of 750, at the cost of the original page falling from 672
of 750 to 404 of 750. The fix is not free.

Status: confirmed. Source: `decoupled-reasoner/src/system/THRESHOLD.md`

### Decomposing the remaining distance to the parser

At 167M the gap is 0.6062 key-first and 0.6608 value-first: `xxl167` reads 0.3938
exact on 2,016 key-first items and 0.3392 on 1,984 value-first ones, where the
parser reads 2,016 of 2,016 and 1,984 of 1,984. The re-emission is gated on
reproducing the committed per-item records before any count is taken, and the
gate reads 7,000 of 7,000 agreeing for `xxl167` greedy and 7,000 of 7,000 for
sampled, with the same for `l45` and `xl93`.

The dominant failure mode is right kind with wrong binding, at 0.4804 of the
1,222 key-first failures and 0.4638 of the 1,311 value-first ones, the largest
category on both positions by a factor of about 1.5 over the next.

Whole-table transposition does not fall with capacity, it spreads: 0 of 514
key-first failures and 780 of 1,984 value-first ones (0.3931) at 45M, 3 of 607
and 758 of 1,963 (0.3861) at 93M, then 324 of 1,222 and 419 of 1,311 (0.2651 and
0.3196) at 167M.

Most of the wrong-kind category is a binding failure wearing a different plan
operation: 123 of the 128 key-first wrong-kind failures and 171 of 174
value-first ones are exact table transpositions that all execute to gold's
answer, so semantic rather than exact-match scoring would add 0.0610 key-first
and 0.0862 value-first.

Answer-level scoring understates the failure: answers land at 1,060 of 2,016
(0.5258) and 1,007 of 1,984 (0.5076) where structures land at 0.3938 and 0.3392.

Fixing only the three shapes where the failure is a clean transposition would
not close the gap: bringing `lookup`, `inverse` and `priority` to 1.0000
key-first recovers 319 items and moves 794/2016 = 0.3938 to 1113/2016 = 0.5521,
still 0.45 below the parser.

Status: confirmed. Source: `decoupled-reasoner/src/norm/GAP.md`

### What a further pretrain would be testing

Binding failures are 0.4804 and 0.4638 of failures, and counting the
transposition-driven wrong-kind items with them puts the figure at about 0.58 and
0.59. A 7B-token 350M pretrain would be testing the smaller half of the gap.

Status: confirmed. Source: `decoupled-reasoner/src/norm/GAP.md`

### The pre-registered prediction that separates data from capacity

If more tokens fix the binding, `lookup`, `inverse` and `priority` should move
first and their transposition share should collapse. If they fix capacity
instead, `sum_chain` and `compose` should move and the small shapes'
transposition share should stay put.

Status: resolved, and by neither branch. The run that would have tested it
finished on 2026-09-04 and was never written back into any lane report.
`results/STAGE-B.md` reads its artifacts; section 7 below states the outcome.
Sources: `decoupled-reasoner/src/norm/GAP.md`, `results/STAGE-B.md`

### A safety claim that was overstated

The interpreter refusing malformed structures was reported as a property of the
design. On trained frames the refusal ratio is 0.000: every failure there is a
wrong structure that executes silently. Over the seven failing shapes the
breakdown is exact 0 of 651, wrong but executable 531, refused 120, malformed 0.
Only on genuinely unfamiliar page shapes does roughly one failure in eight
become a refusal.

Status: withdrawn. Source: `decoupled-reasoner/THESIS.md` 2026-08-31

### The lane report that was never updated

`src/role/ROLE.md`'s results section still reads Pending with arm A as the gate,
while `THESIS.md` reports all four arms. The per-arm cells have to be read from
`src/STATE.md` or the records, not from the lane report.

Status: a documentation defect, recorded. Sources:
`decoupled-reasoner/src/role/ROLE.md`, `decoupled-reasoner/src/STATE.md`


---

## 7. Stage B, read from artifacts no document in this repository saw

Every document under `decoupled-reasoner/` was written before this result
existed. The last commit of the original repository is 2026-09-04T04:40Z, the
Stage B checkpoint was written at 2026-09-04T06:12Z, and the driver meant to
record it had already died. The artifacts survived in S3 and are committed here
at `results/s3/runs/e3-350m/eval/`.

### The pretrain is worth nothing on MMLU

Five-shot, completion format, seed 1234, 375,440,384 parameters, floor 0.2500.
Stage A, the pretrain alone, reads 0.2720 at n=500 and 0.2510 at n=1000. Stage
B, the same pretrain with the fine-tuning pack applied, reads 0.2700 and 0.2490.
Fine-tuning moves MMLU by 0.0020 at both sample sizes, toward the floor.

Status: confirmed. Source: `results/s3/runs/e3-350m/eval/mmlu_*.json`

### Against the reference pretrain, the shape-level comparison is a wash

With the fine-tuning pack held identical, the seven-billion-token pretrain
against the earlier corpus-v1-8k checkpoint reads: 40 rule shapes greedy, 0.8841
against 0.9000, with 33 of 40 inside 0.01; the same shapes at temperature 0.7,
0.8824 against 0.8850, with 27 of 40 inside 0.01; 28 held-out conditions, 0.6191
against 0.5748. The only mean that moves is the held-out one, and two shapes
carry almost all of it.

Status: confirmed. Sources: `results/s3/runs/e3-350m/eval/score_e3sft-*.json`,
`score_ref-*.json`, `score_*_heldout.json`

### Every movement is answer emission, not reasoning

Across all 108 shape-conditions the correlation between the accuracy delta and
the none-rate delta is -0.9070. Where the none rate moves by more than 0.05, in
13 conditions, the mean absolute accuracy delta is 0.2496; everywhere else it is
0.0073. Restricted to the 71 shape-conditions where both arms emit a parseable
answer on at least 98 percent of items, the mean delta is -0.0009, and exactly
two conditions move by more than 0.05, `lookup_then_band` and `transitive`, both
at -0.055 and both against the new pretrain.

The largest single movement, `priority_list` at +0.495, comes with its none rate
falling from 0.545 to 0.010. What improved is that the model answers on that
shape, not that it binds roles on it.

Status: confirmed. Source: `results/STAGE-B.md`

### The registered prediction gets a third answer

`src/norm/GAP.md` fixed two outcomes in advance: a data fix moves `lookup`,
`inverse` and `priority` first, a capacity fix moves `sum_chain` and `compose`.
Neither fired. `priority_list` moved for the reason above, `inverse_chain` went
0.275 to 0.265 with its none rate near 0.48, `transitive` went 0.270 to 0.215,
`chain_rule` went 0.420 to 0.440 against a 0.250 floor, and `exclusion` is 0.000
in both arms. The instrument was not built to see the outcome it got.

Status: confirmed, and it closes the last objection to the undertraining result.
That result rested on Stage A, which had no fine-tuning while the model it was
compared against had. With fine-tuning held identical the better pretrain is
worth -0.0009 on the shapes that can be read cleanly.

Source: `results/STAGE-B.md`
