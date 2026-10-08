# Neural reasoning models

One research program and two earlier projects that fed into it, with the
evaluation artifacts for all three. The program asks whether a small reasoning
engine with access to external knowledge can do the work a large
parameter-heavy model does.

Most of what is here is negative. Several of the positive results in this
repository were overturned by later measurements in this repository, and the
record of those reversals is the part worth reading. A document that reported
only the surviving positives would be advocacy.

## The hypothesis

`decoupled-reasoner/THESIS.md` frames the question as a comparison between two
computational objects rather than two model sizes. X is one large static
network. Y is a small permanent engine plus external knowledge, autonomous
acquisition, temporary skill formation and adaptive test-time computation, with
the learning happening at inference time. Comparing the two by parameter count
is close to the wrong abstraction, because the capability function is not the
same shape on both sides.

For X, capability is approximately a function of parameters alone. For Y it is
a function of permanent parameters, accessible external knowledge, retrieval
and search quality, available test-time compute, temporary learned state, and
the ability to acquire new abstractions. That last term is the one ordinary
retrieval augmentation does not have, and it is the term this program spent
most of its time trying to measure.

"From scratch" is literal. `decoupled-reasoner/SPEC.md` specifies a Llama-style
model table running from an 8M smoke model to 1.3B, trained on generated
corpora with a tokenizer trained in-repo.
`decoupled-reasoner/ARCH.md` specifies NRM-1B as roughly a 1B decoder plus a
0.15B evidence encoder, with four departures from a plain decoder: a
partitioned context, evidence cross-attention, a recurrent core with static
depth, and a pointer head.

Nothing at the 1B class was ever trained. The largest from-scratch checkpoint
in the program is 375,440,384 parameters, and the role-binding and composition
work runs on rungs at 45,483,008, 93,579,520 and 167,376,384 parameters. The
~1B figure is a design target, not a trained artifact.

The falsifiable target is stated as a target rather than a prediction, with
Qwen3.8-27B as the reference point: a 7B system at parity is a 4x
parameter-efficiency result, 4B is nearly 7x, and under 1B is more than 27x.
Books, indices and the web are excluded from the denominator, on the argument
that a person is not credited with the parameters of a library. No measurement
against that target exists anywhere in this repository.

## Layout

The default branch holds a monorepo, so the full commit history of every source
is reachable from `main`.

- `decoupled-reasoner/` is the main program: the from-scratch reasoner, the
  retrieval fabric, and every experiment around them, over 514 commits. The
  governing documents sit at its root (`THESIS.md`, `PLAN.md`, `SPEC.md`,
  `ARCH.md`, `PREREGISTERED.md`), the consolidated self-audit is at
  `src/STATE.md`, and the lane reports live under `src/` beside the code they
  describe. `src/pilot/` is the acquisition pilot, whose 8 commits had not been
  pushed anywhere before.
- `latent-transfer/` is the cross-model latent handoff work plus the 1d
  cellular-automaton serial-depth study.
- `latent-translation/` is the earlier Coconut-based reasoning-outsourcing
  precursor.
- `results/s3/` mirrors the project's S3 bucket with the key layout preserved,
  filtered to what belongs in git: no model weights, no tokenized shards, no
  generated item banks, no thinking traces. 3,333 objects, 502 MB. The Stage A
  and Stage B evaluation artifacts are under `results/s3/runs/e3-350m/eval/`
  and the acquisition pilot's run is under `results/s3/runs/pilot-acq/`. Most
  of this was written after the last commit of the original repository and
  existed nowhere in git.
- `results/STAGE-B.md` reads the Stage B comparison, which no document under
  `decoupled-reasoner/` could have seen.
- `MANIFEST-s3.md` accounts for everything left out, with sizes and URIs.

Unmodified source histories are preserved as branches, so nothing depends on
reading the subtree assembly correctly: `history/decoupled-reasoner`,
`history/pilot-acq-bench`, `history/latent-transfer`,
`history/latent-translation`.

Start with `decoupled-reasoner/src/STATE.md`. It is a claim ledger: every claim
restated at the strength its artifact supports, each marked confirmed,
superseded, withdrawn or unlocatable, followed by 41 numbered measurement faults
and a list of claims whose artifacts no longer exist. It is the only document
where the reversals carry the same weight as the positive results.
`FINDINGS.md` in this directory is the full record organised by theme.

## What was found

### The strict form of the thesis is dead, by its own rule

`decoupled-reasoner/SPEC.md` section 7 fixed the decision rule before the test
ran: if regime C reaches at least 90 percent of regime A's score the strict form
survives, 60 to 90 percent weakens it to a frequency-ordered resident knowledge
diet plus teacher distillation, and below 60 percent it is dead with the writeup
saying so plainly.

Regime C, trained with no natural language at all, scored 0.0000 on naturalized
reading of all 250 items on every seed. Regime A at the same 350M class scored a
mean of 0.2053 across three seeds (0.228, 0.196, 0.192). The ratio of means is
0.0000 with a bootstrap 95 percent interval of [0.0000, 0.0000]. The same C
checkpoints score 0.66 to 0.72 on their own-format held-out worlds, so they
learned something; what they cannot do is read it stated in prose.

### The clearest positive result is symbolic, and that is uncomfortable

A library with no gradient step anywhere in its path reads an operation off one
page of prose and applies it at 1.0000 forced choice on 850 items covering 170
distinct operations, against per-family chance floors of 0.29 to 0.37. On the
same items the neural reader scores 0.00 to 0.12 and emits the right structure
0 times in 6,736 attempts. The audit attaches its own ceiling to this: the
effective denominator is 170 rather than 850, and the parser baseline beside it
is vacuous rather than passed.

`src/STATE.md` states the reading rather than leaving it implicit. On the one
axis where this program has a clean acquisition result, the neural substrate
contributes nothing and a symbolic reader does all of it. That is evidence for
the decoupling thesis in a form the thesis did not ask for, and it is not
evidence that a small network can acquire anything.

### Reading a value off a page is real; applying a rule is frame-bound

The attack expected to be decisive failed to falsify. With page wording
byte-identical and only the values cyclically permuted, the answer follows the
page: 0.9380 against 0.0078 on substitution_rule (n=258, floor 0.2012) and
0.9608 against 0.0120 on exception_rule (n=332, floor 0.5030). A position-based
copier lands on the pre-permutation answer 71 percent of the time; the model
lands there 0.8 percent of the time. Value reading is real.

The acquisition claim built on top of it is not. An independently built
renderer swap puts substitution_rule at 0.970 in the native sentence frame and
at 0.045, 0.045 and 0.015 in three other ordinary English idioms, against a
0.200 chance floor. Isolating the mechanism shows swapping the nouns costs 0.13
while swapping the sentence shape costs 0.94. What the checkpoint does is
frame-conditioned value binding.

### Three headline numbers that did not survive

The 0.680 rule-application figure was the number the architecture was designed
around. `THESIS.md` Correction 1 recorded it as stale with no findable
provenance, and re-measurement on the shipped checkpoint gave textbook 0.958 /
wrong textbook 0.002 / blank 0.000 at n=500 and 0.968 / 0.001 / 0.000 at
n=1000, with the chance floor at 0.401 rather than 0.000. The audit then
corrected the correction: the artifact does exist, and its checkpoint field
reads `rl-000250.pt` where the shipped model is `final.pt` at step 3000, so
0.680 against 0.958 is a step gap and not a fabrication. The step-250
checkpoint has since been deleted and the 0.4018 floor was never printed beside
the number. `ARCH.md` section 1 still justifies the whole design with the
retracted form of it.

One rule family inside a three-family macro average was a pure grading
artifact. `threshold_rule` names both candidate words in 94.3 percent of its
answers; fifteen pairs of items with byte-identical output and opposite gold
answers were all thirty graded correct; disallowing hedging moves it from 0.985
to 0.009. After forced choice and against a 0.401 floor, only 0.292 of the
headroom above guessing is real rule application. A fifty-line regex over the
top-ranked pages scores 1.000 against the model's 0.968 on identical items.

The operator-graph result was read as induction from a page. On pages whose
operand roles were transposed after training, the model followed the training
identity on 678 of 678 items and the page on 0 of 678. The flat
oracle_plan-through-depth-eight row holds only under the one trained wording
and reads 0.087 to 0.207 under three others. The depth-two and depth-three arms
sum to 0.480 + 0.533 = 1.013, which is chance across the pair rather than
partial composition.

### Composition: a training ceiling, a retrieval artifact, and one real wall

Three different things were being called the composition wall.

The first was a training ceiling. Eight arms from the same 350M base, differing
only in the maximum plan depth seen in training, put the depth-eight arm at
0.99 on depth-eight chains where the previously published arm scores 0.02. H10,
the autoregressive planning-horizon hypothesis, is recorded as dead: there was
no three-step horizon, there was a three-step training set. The extrapolation
constant is zero rather than small, since no arm generalises one step past its
own maximum. The arms behind this result could not be located by the later
audit, so it rests on an unlocatable table, corroborated in shape by the corpus
retrain.

The second was retrieval position. The minimal repro measured a total wall
between depth one and depth two, zero correct answers in 1200 rollouts at
depths two, three and four against 0.5375 pass@1 at depth one. Error
compounding is dead as an explanation, because independent lookups at the
depth-one rate predict 0.289 at depth two and the observed count is zero in
400. But moving the needed table to position one, with the page count held
fixed, takes depth-two step one from 0.0050 to 0.3825 and the chain from 0.0025
to 0.1875: the gold page is served on 0.417 of those rollouts against 0.007
before. The rescue ladder therefore corrects its own parent document. The
published depth curve measures composition and retrieval position at once, and
how much of the wall is which is not answerable from the runs on record.

The third survived both. After a corpus built to widen the training
distribution, multi-hop chaining fails inside the training distribution:
`chain_rule` 1.000 at one hop and 0.220 at two against a 0.250 floor,
`inverse_chain` 0.760 and 0.180, `weighted_chain` 1.000 and 0.039, all trained
at those depths. Training on real multi-hop retrieval moved HotpotQA from 0.004
to 0.278 and left `chain_rule` at its floor, 0.2520 to 0.2441. Splicing the gold
intermediate back in as a fresh key rescues it, from 0.0000 to 0.2050 pass@1
and 0.000 to 0.560 pass@4 over 400 chains, which puts the failure in writing
the key rather than in using one.

### Role binding, and the only threshold this program located

A prose-to-structure reader binds which invented word is a key and which is a
value to where the word sits in the sentence. On a held-out sentence mode the
45M rung reads key-first items at 0.7302 and value-first at 0.3177, while on
trained frames both positions are fine at 0.9206 against 0.9211. Seven question
shapes score exactly 0.0000 on value-first items despite seeing between 42,567
and 42,918 value-first examples each. A hand-written parser reads the same
value-first half 1302 of 1302, so the binding is present and unambiguous in the
text.

This went through three readings. Four matched interventions at 45M all failed
to close the gap and each changed which convention was chosen without changing
whether one was chosen, which the program read as a property of the substrate.
That conclusion was wrong: at a matched tokens-per-parameter budget the
167,376,384-parameter rung reads 0.6341 key-first and 0.6063 value-first, a gap
of 0.028, so the collapse is capacity and the threshold sits between 93M and
167M. The audit then corrected that in turn. Key position only reaches eight of
the fourteen question shapes, and on those eight the 167M rung reaches symmetry
at 0.3938 against 0.3392 where the 45M rung was at 0.7450 against 0.0000: more
parameters cost 0.35 on key-first and bought 0.34 on value-first. The aggregate
improvement from 0.5256 to 0.6203 is carried almost entirely by the six shapes
the axis does not reach.

LFM2-350M, trained to convergence by someone else and never exposed to this
corpus, shows the same asymmetry at full strength (0.8805 against 0.3479 on a
0.5 floor), which kills the undertraining confound. What survives is narrower
than either result: reading role independently of position in an unfamiliar
rule sentence is taught by this task rather than supplied by English
pretraining.

### More tokens did not buy comprehension

The undertraining hypothesis was tested directly and died. A 350M model trained
from scratch on regime_e3 for 26,700 steps and 6,999,244,800 tokens, 18.64
tokens per parameter, cosine fully annealed, final loss 2.5409, zero restarts,
reads MMLU at chance across six checkpoints. Every 95 percent Wilson interval
contains the 0.2500 floor, and the highest point, 0.288, has a lower bound
sitting exactly on 0.2500.

The flatness is worse than noise. The checkpoint puts 0.730 of its answer mass
on option A at n=200, splitting A/B/C/D as 146/7/35/12 against a gold-A share
of 0.300, and by free generation it names one of A to D on 18 of 400 items,
scoring 0.2222 [0.090, 0.452] on those. Over the earlier part of the same run
the modal-prediction share rises 0.464, 0.589, 0.600 toward the old
checkpoint's 0.695, so more tokens made the answer policy more degenerate.

### Nothing here beats a comparable off-the-shelf model

The 375,440,384-parameter checkpoint reads MMLU at 0.2750 (n=200), 0.2640
(n=500) and 0.2820 for the real-document variant, every interval containing the
0.2500 floor. LFM2-350M, calibrated against its published 43.43 to within 0.43,
reads 0.4300 at n=200 and 0.4360 at n=500 with 21M fewer parameters. On GSM8K,
scored against a floor built from drawing a number already in the prompt, the
program's reader has no result under any condition: 0.0150 against 0.0209
closed book, 0.0300 against 0.0182 with method retrieval, 0.0350 against 0.0153
with problem-text retrieval. All 6 answers it gets right under method retrieval
came from items whose context block contained the gold number.

The retrieval lane overturned its own headline. The 20 items whose pages carried
the gold answer scored 0.7500 with pages and 0.7000 on the same items closed
book, so the page changed one item out of twenty, and across three retrieval
runs the answer-bearing cell beat the same items closed book by one item, zero
items and one item. The cell that speaks to reasoning, where pages do not state
the answer, has not moved under three configurations: 0.4226, 0.4125, 0.4242
against 0.4300 closed book.

### Latent state does not travel, and discreteness is doing work

The cross-model handoff works on a toy and fails at scale. On a sequential
composition task with chance at 0.112, an adapted receiver reaches 1.000 against
a small-model latent floor of 0.684, with the random-big-model control at 0.736.
An earlier frozen-receiver version of the same pipeline scored 0.749 against a
control of 0.745, statistically the same, so the gain there was entirely the
adapter on the small model. At real scale on ProsQA the random-receiver control
scores highest of all arms (0.7600 against a pipeline at 0.7220 and 0.7300),
and on HotpotQA both pipeline and control land below the small model alone, so
the handoff is destructive rather than useless.

In the cellular-automaton study, latent intermediates in the same KV cache read
out by the same mechanism do worse than carrying no intermediates at all: at
k=4, tokens score 0.718, no intermediates 0.280, and the two latent arms 0.021
and 0.031. The latent arms fit their training rules at loss 0.04 or lower and
transfer nothing. At k=1 the learned slot is a lottery over initialisation
(0.10, 0.93, 0.92, 0.48 on four seeds) and at k>=2 it is dead on every seed,
including the ones that won at k=1, so what never works is the next slot
reading the previous one.

Jacobi decoding removes the token arm's serialisation penalty entirely: the
k-step trace settles in about one parallel pass per reasoning step at every
depth, with output identical to serial decoding at 1.000.

## The methodology that makes these numbers worth anything

Pre-registration with explicit falsification conditions.
`decoupled-reasoner/PREREGISTERED.md` holds predictions written down and dated
before the corresponding run existed, each with the condition that would kill
it. `SPEC.md` section 7 fixed the kill-test threshold before the kill test.
`src/system/THRESHOLD.md` carried a prediction about which training holdout
would collapse, written before either arm ran, and both halves held: the split
withholding a statement mode reads 0.6165 key-first against 0.2471, while the
split withholding a whole question form stays balanced at 0.7440 against
0.7611.

Four things beside every accuracy. After one day produced three containment
graders and a headline that changed meaning under attack, the standing rule
became that every accuracy carries its chance floor, its hedge rate, a
forced-choice score alongside the grader score, and its denominator. The
hedging reversal is why: a single artifact family inside a three-family macro
average moved the headline by a third.

Paired within-item controls rather than contamination splits. Every retrieval
effect in the external lane is read off the same items scored closed book, not
off a split between items where retrieval worked and items where it did not.
That is what killed the 0.7500 figure, and McNemar on the paired comparison is
reported even when it does not resolve: 0.4450 to 0.4850 on identical pages
sits at p = 0.115, and the lane says so rather than reporting the gain.

Falsifying arms, run with the expectation that they win. The value-permutation
attack was expected to be decisive and failed, which is the strongest positive
evidence in its lane. The twin-system control and the regex baseline were run
and both cut against the project. Length-matched nulls are standard: the rung
that asks the model to name each intermediate scores identically to a null
control that appends any sentence at all, so it measures nothing about
intermediates.

No pooling across composition types. Sequential depth, relational breadth and
novel composition are never averaged together, because the manipulation that
moved sequential depth left breadth identical across all arms (1.00 at breadth
one to three, 0.00 at four to six) and left novel composition at chance.
Pooling hides results in both directions: `plan_execute` reads 0.24 to 0.42 at
breadth four to six, above both oracles, because two matched errors cancel, and
the registry records a run pooling to 0.156 that reads as partial success until
the split shows two of three domains at 0.000.

Faults named rather than quietly fixed. `src/STATE.md` enumerates 41 numbered
measurement faults, several of which flattered the program, all found
internally. Fault 1, reading the first N rows of an ordered file as a sample,
recurred four times in four lanes. Fault 2, reading a rate off the window where
it looks best, appeared three times, twice inside the document that had just
corrected it.

## What is still open

The composition horizon has no number. Nothing in range saturates, the largest
plan ever written across the depth arms is 1, 2, 3, 4, 10, 10, and locating a
horizon needs arms deeper than eight. Novel composition did not move under any
manipulation: every arm emits about 1.0 distinct operator symbols where two are
needed.

The capacity threshold for axis composition is bracketed from below, between
93M and 167M, and not characterised above 167M. A matched budget at the 355M
rung is 234,238 steps, about sixty-four hours on one L40S, and it was dropped as
unaffordable rather than measured.

Whether an architecture in which role is a structural field the decoder must
fill, rather than a label an auxiliary head guesses, closes the positional gap
is untested. `src/norm/GAP.md` pre-registers the prediction that separates a
data fix from a capacity fix, and concludes that a 7B-token 350M pretrain would
be testing the smaller half of the gap, since binding failures plus
transposition-driven wrong-kind items are about 0.58 and 0.59 of all failures.

Stage B of the 2026-09-04 pretrain is answered, and not by any document under
`decoupled-reasoner/`. The driver meant to record it died after launch, so
every lane report still calls it outstanding. The artifacts survived in S3 and
are read in `results/STAGE-B.md`: with the fine-tuning pack held identical, the
seven-billion-token pretrain is worth -0.0009 on the 71 shape-conditions where
both arms emit a parseable answer, and the correlation between its apparent
movements and its answer-emission rate is -0.9070. The registered prediction in
`src/norm/GAP.md` was built to separate a data fix from a capacity fix, and the
outcome is neither.

Page semantics induction is unmeasured rather than refuted. Neither checkpoint
emits an operator definition and parsed output is 0 of 298 for both, so the
0 of 689 toward the page stands unmoved because nothing aimed at it.

The acquisition pilot is registered and not run. Its instrument, models,
decoding and three decision rules are fixed, and amendment 1 of 2026-10-06
rebuilt both the instrument and the validity rule after two reviews found the
rule as registered could not pass. No verdict, no scored record and no chosen
treatment base exist.

Several surviving positive results rest on artifacts that exist on one live box
and in neither the repository nor S3, so they are one instance termination from
unverifiable. Others have no artifact at all, including the eight
training-ceiling arms. `src/STATE.md` lists both sets.

## Artifacts, checkpoints and S3

No model weights are in git. `MANIFEST-s3.md` lists every large artifact
deliberately left in S3 with its size and URI.

Two record files are permanently gone rather than merely absent. The MMLU
re-measurement at n=1000 reading 0.2450, which had been propagated as the
headline, was written to instance store on a worker that has since been
terminated, and a recursive listing of all 39,334 objects in the project bucket
returns no match. The best-supported figure is 0.2640 at n=500. Numbers measured
before the start-token fix in the external lane are void rather than merely low,
and are named in `src/extern/LIQUID.md` so nobody recovers them from the record
files and reads them as findings.

`results/s3/` holds the evaluation artifacts small enough to live in git, in
the bucket's own key layout so every path maps back to its S3 object.
`results/README.md` states the filter that produced it.
