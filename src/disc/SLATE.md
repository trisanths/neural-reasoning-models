# Composition: the minimal repro, the empty space, and a ranked slate

Discovery loop steps 1, 2, 6, 7 and 8 run against the composition failure.
Steps 4 and 5, the survey and the constraint extraction, were not run; the
boundary conditions used here are the ones already verified in THESIS.md plus
the ones stated in the brief. Claims in the empty-space map that go beyond
those are marked, and a survey pass should confirm them before any of them is
used to justify a build.

## 1. The instrument

`src/disc/minrepro.py`. One episode invents a referral system. Level 0 holds
request types, level i holds the desk names of office i, and office i has a
routing table sending every level i-1 name to one level i name. Depth d asks
for d lookups, each keyed by the output of the previous one.

Three properties make the depth curve mean something.

Depth one is the `substitution_rule` question in shape, down to the sentence
"A {k} is handled by the {v} desk" and the wh-question "Which desk handles
it?". That family is answered by this same checkpoint at 0.969 greedy and
0.828 at temperature one, measured here as a harness control. So the curve
starts from a task the substrate demonstrably performs, and depth is the only
thing that varies along it.

The page set does not change with depth. The system is built from the seed
alone, so the same tables serve every depth and the question grows by about
four words per step rather than by a page. In the retrieval presentation, the
one the RL stage trained on, the prompt is the question alone at 30 to 60
tokens whatever the depth, and the pages arrive through the retriever. The
in-context presentation is reported as a secondary condition; its prompts run
from 232 tokens at depth one to 672 at depth four, outside the 384-token
budget of the RL stage, and it is worse everywhere.

Levels are typed. A token is a source on exactly one page and a target on at
most one other, so each individual lookup is as unambiguous as the family the
model already answers. The closed-alphabet variant, where one alphabet is
shared and every map is a derangement of it, is kept behind `--untyped`
because it fails at depth one for a different reason. That measurement is
reported below, since separating referent ambiguity from depth turned out to
be necessary.

### What the audit checks

`audit_episodes` verifies the exclusions rather than assuming them. Over 400
generated questions at depths one to four there were no violations of any of:
the answer appearing anywhere in the question, the answer being the starting
token, the answer being an intermediate, or the stages failing to be distinct.

The shortcut baselines, all at or below chance of 0.167:

| Reader | Accuracy |
|---|---|
| Most frequent token on the pages | 0.000 |
| Keyword-nearest, best page then the row naming the start | 0.000 at depth >= 2 |
| Last named office's table applied to the starting type | 0.000 at depth >= 2 |
| Answer the depth-one question instead | 0.000 at depth >= 2, by construction |
| Chance | 0.167 |

Maximum token frequency spread across a page set is 4 occurrences, from the
preamble and the worked example. The worked example on the page set is itself
a depth-two referral on a reserved starting type that no question uses, so
failure cannot be explained by the composition format never having been shown.

## 2. The depth curve

Checkpoint `s3://decoupled-reasoner-009398924577/runs/final/rlsimple-503-921/final.pt`,
tokenizer_v2, minimal gold pages, retrieval presentation, scored by the
project's own rule from `src/rl/env.py` (normalized exact match, then a
bounded contains fallback).

Sampled decoding, temperature 1.0, 4 samples per question, 100 questions per
depth, 400 rollouts per row.

| Depth | pass@1 | pass@4 | Answers the depth-one question | No token named | Mean retrieval rounds | Well formed |
|---|---|---|---|---|---|---|
| 1 | 0.5375 | 0.950 | n/a | 0.430 | 0.99 | 0.905 |
| 2 | 0.0000 | 0.000 | 0.250 | 0.723 | 0.73 | 0.823 |
| 3 | 0.0000 | 0.000 | 0.183 | 0.775 | 0.56 | 0.828 |
| 4 | 0.0000 | 0.000 | 0.188 | 0.795 | 0.54 | 0.820 |

Greedy decoding, one sample per question, same files: 0.84, 0.00, 0.00, 0.00.

Harness control on the family the repro is built from, same checkpoint, same
code path: `substitution_rule` 0.969 greedy and 0.828 at temperature one;
`threshold_rule` 1.000 greedy and 0.922 at temperature one.

Zero correct answers in 1200 rollouts across depths two, three and four.

Evidence-ablation and referent-ambiguity controls: pending.

## 3. What the curve rules out

The wall sits between depth one and depth two, and it is total.

Error compounding is dead. If each step were an independent lookup succeeding
at the measured depth-one rate of 0.5375, depth two would score about 0.289.
Observed is 0.000 over 400 rollouts, and pass@4 is also 0.000, so no sample in
four ever landed. Under a compounding model the probability of seeing zero
successes in 400 draws is on the order of 10 to the minus 59. Whatever depth
two needs, it is not a second copy of what depth one does.

The chain does not run short. It runs exactly one step and halts. A quarter of
depth-two rollouts name the first office's desk, which is the correct answer to
the depth-one question embedded inside the depth-two question. At depths three
and four that same class stays near 0.19 while the classes for the second and
third intermediates never appear at all, not once in 800 rollouts. The model
executes the first lookup and then stops, at every depth.

Retrieval effort falls as the problem deepens. Mean rounds go 0.99, 0.73, 0.56,
0.54 from depth one to depth four. The policy issues fewer queries exactly when
more evidence is required, and it never issues the second query that a
depth-two answer needs. So this is not a case of fetching the second table and
misreading it. The second table is never fetched. The failure is visible in the
control signal, whether to keep going, before it is visible in any computation.

It is not degeneration. Well-formed trace rates stay between 0.82 and 0.91 at
every depth, and the answers remain fluent sentences in the family's idiom.

It is not a missing demonstration of the format. The page set carries a worked
depth-two referral, on a starting type reserved so that no question uses it.

It is not evidence length or prompt shape. The page set and the prompt are
constant along the curve except for one referral clause per step.

Template sensitivity is real and worth recording separately. The first version
of this task used a fresh notation ("the Fexharv map sends x to y", "Which
token results?") rather than the routing idiom, and scored 0.06 at depth one
under the most favourable condition available: typed levels, gold pages only,
232-token prompt, greedy decoding. Rewriting the same task into the
`substitution_rule` surface form moved depth one from 0.06 to 0.84 without
changing the underlying computation at all. The acquisition result generalises
across invented systems within a template and collapses across templates. That
bounds how much the 0.680 headline means, and it is the reason section 8
recommends repeating the curve on the pre-RL checkpoint.

## 4. Map of the empty space

For each region: what is demonstrated, what is not, and what this repro would
show that existing work does not.

### Runtime creation of primitives whose semantics are induced at inference

Demonstrated: a stated rule can be applied to a fresh input by a model that
never saw the rule in training. That is our own 0.680 result, and the depth
one number here is the same phenomenon in a second family. In-context learning
generally induces a mapping from examples and uses it inside the same forward
pass.

Not demonstrated: that the induced object is reusable, meaning its output can
be the input to another induced object. Every demonstration we have checked
applies the induced primitive exactly once. The word "primitive" is doing
unearned work in that literature; what is shown is a single conditional
response, not an operator.

What this repro adds: reuse is the only thing it varies. The primitive, the
page, and the prompt length are held fixed while the number of applications
moves, so a claim about primitive creation can be tested at its actual
definition rather than at one application.

### Executable epistemic memory

Demonstrated: structured storage of facts and of tool signatures. Retrieval of
proof techniques with transfer to a novel theorem (Yang et al., Findings of
EMNLP 2025), with the authors' own boundary that a fundamentally novel
strategy gains nothing.

Not demonstrated: that storing a precondition, an invariant or a type
signature changes what a model computes rather than what it says. No benchmark
we know of holds a rule's content fixed while varying whether its executable
annotations are present, so the two have never been separated.

What this repro adds: the typed variant has a real type discipline, since
office i accepts only level i-1 names. The type declaration can be added to or
removed from the preamble with one flag while the tables stay identical, which
turns "does a type signature help" into a measured difference rather than a
design argument.

### Temporary architecture mutation

Demonstrated: conditional computation, expert routing, per-task adapters, and
recurrent-depth models that vary iteration count at inference. Each of these
varies how much or which of a graph fixed at training time runs. Huginn's
authors are explicit that their result is compute equivalence rather than
capability equivalence.

Not demonstrated: an acquired description instantiating a control structure
the trained graph does not already contain.

What this repro adds: the smallest such control structure is a bounded loop of
length d, and d is the axis. A mechanism that genuinely mutates the graph
should put its cliff at the mutated bound, not at depth two. That is a
positional prediction no existing benchmark can check.

### Acquisition by experimentation

Demonstrated: verifier-guided revision improves answers. Our own multi-attempt
revision with a programmatic verifier was one of the six objectives that ended
at 0.000, so the negative result is ours as well.

Not demonstrated: a model synthesising a test for a hypothesised operator,
running it, and using the contradiction to revise the operator rather than the
answer. Published revision loops revise the answer.

What this repro adds: the operator is a finite table with ground truth, so a
revision that repairs one table entry is observable and separable from a
revision that changes the final token. That distinction cannot be made on a
natural-language task.

### Separating meaning from execution with a compilation step

Demonstrated: distilling explicit reasoning into direct answers works, and
practice converts explicit procedure into implicit competence.

Not demonstrated: any system where the compiled artefact is created at
inference from newly read text and can be inspected.

What this repro adds: the compiled artefact has a ground truth, the
permutation table. Compile accuracy can be scored against it directly and
separately from execution accuracy, which no natural-language benchmark
permits and which is the measurement that decides whether a compilation step
is worth building.

### Composition outside the language model

Demonstrated: neural module networks compose modules whose inventory is fixed
at training; tool-use agents compose tools whose implementations are given;
program-of-thought approaches emit code whose primitives are the interpreter's.

Not demonstrated: a scheduler over operators whose implementations were
induced in the same episode from prose. In every case we have checked the
primitive vocabulary is fixed before the episode starts.

What this repro adds: the operators exist only inside one episode and are
regenerated per seed, so memorising an operator has zero expected value across
episodes. That is what makes externalising composition a test of the thesis
rather than a test of tool use.

### An inference-time internal instruction set

Demonstrated: nothing we are aware of. Discrete latent codes, vector-quantised
bottlenecks and soft prompts allocate capacity, but a code's meaning is learned
across training rather than allocated and defined within an episode.

Not demonstrated: that a fixed substrate can hold an opcode whose
implementation was written into it minutes earlier and dispatch on it.

What this repro adds: the smallest instruction set that still requires
dispatch, K opcodes over one register, where the depth curve is the dispatch
count curve.

## 5. The hypothesis space

Everything below is ranked by how much of this table an experiment removes.

| | Hypothesis | Status after the curve |
|---|---|---|
| H1 | Credit assignment. Composition is representable; the objective never finds it. | Alive |
| H2 | Prompt-key locality. Evidence lookup can only be keyed by tokens literally in the context; a computed value cannot serve as a key. | Alive |
| H3 | No value register. The substrate cannot bind an intermediate symbol at all, even a literal one. | Alive |
| H4 | Error compounding. Each step is fine and accuracy is p^d, with no qualitative wall. | Dead. 0 of 400 at depth two against 0.289 expected |
| H5 | Substrate capacity. 350M lacks the serial depth. | Alive |
| H6 | Distribution. The failure is an artefact of prompt shape and RL overfitting. | Partly addressed; see section 3 |
| H7 | Halting. The policy has no representation of being partway through a chain, so it stops after one step and reduces its own retrieval effort. | Alive, and the curve's strongest positive evidence |

H7 was not on the list before the curve ran. The falling retrieval-round count
put it there, and it is the one hypothesis the measured trace shape actively
supports rather than merely permits.

## 6. Six invented mechanisms

### M1, representation. Compiled operator table with an APPLY primitive

Two additions to the 350M backbone. A compile head reads an evidence span and,
for each stated pair, writes one row into a slot: `K_m` holds the embeddings of
the stated sources, `V_m` the embeddings of the stated targets. Building the
slot requires only span selection, which the existing pointer head
(`src/train/pointer.py`) does at 0.514 on copy-heavy items. An apply primitive
is a single fixed learned operation, `u <- V_m^T softmax(K_m u / sqrt(d))`,
with the softmax temperature annealed toward argmax during training. The
backbone's job shrinks to emitting a slot sequence; a value register holds the
running `u`, initialised from the starting token's embedding and decoded at the
end through the tied unembedding.

Prediction on the repro: accuracy approximately flat in depth, at
`c * a^d` with compile accuracy `c` and per-apply accuracy `a` above 0.99.
Concretely, train on depths one and two only, then test three through twelve;
depth eight should land within a few points of depth two.

To be wrong: a verified-correct table plus a geometric decay in depth. That
would mean the value register itself is lossy and the representation of the
operator was never the binding constraint.

Cheapest distinguisher: the train-shallow, test-deep extrapolation. No other
mechanism here predicts flat extrapolation from a depth-two training set.

### M2, architectural. Value-keyed re-entrant retrieval inside the looped core

`src/train/model.py` already carries a weight-tied looped core and
`src/latentret` already has a gate that reads the recurrent state, a latent
query, and in-loop injection. The change is where the query comes from. Reserve
a fixed slice of the recurrent state as a value register. At each loop
iteration the latent query is produced from that slice alone, never from the
prompt token stream; the retrieved evidence line is injected; a learned write
gate overwrites the same slice with the retrieved target's representation. One
loop iteration is one composition step, and the loop count is a runtime knob.

Prediction: a plateau then a cliff, with the cliff located at the loop budget
rather than at depth two. For d at or below `n_loops`, accuracy within noise of
depth one; above it, chance.

To be wrong: accuracy decays with depth even below the loop budget, or the
value slice turns out to be ignored. The second is directly measurable by
zeroing the slice and checking whether depth one accuracy moves at all.

Cheapest distinguisher: sweep `n_loops` at fixed depth and depth at fixed
`n_loops`. This mechanism is the only one predicting the cliff tracks the knob.

### M3, memory and learning rule. Ephemeral association installation by a delta rule

One designated layer holds a fast-weight matrix `W`, zeroed at episode start.
While the evidence is read, each stated pair drives `W <- W + b (v - W k) k^T`,
the delta rule, with `k` and `v` the layer's existing key and value projections
of the source and target representations. At question time the layer computes
`u <- W u` once per composition step, iterated by the looped core. Nothing is
discrete, nothing is symbolic, and the only new trained parameters are the
write gate and `b`.

Prediction: flat in depth, but degrading in the number of installed
associations because of interference. Accuracy should fall as `--alphabet` and
the number of offices grow while staying flat as depth grows.

To be wrong: accuracy falls with depth at a fixed alphabet size, or six
associations already interfere.

Cheapest distinguisher: the alphabet-size sweep at fixed depth two, which
`minrepro.py` already supports. M1 predicts flat in both axes; this predicts
flat in one.

### M4, objective and training. Stage-supervised composition with a depth curriculum

Replace the final-answer reward with a per-stage reward. The environment knows
every stage, so the policy is required to emit them in order between markers
and is paid the fraction of stages correct, with the last weighted. The
revision loop already in `src/rl/env.py` is reused so that a wrong stage is
rejected and retried in place rather than the whole rollout being discarded.
Curriculum on depth, advancing when accuracy crosses a threshold.

Prediction: it lifts depth two well above zero, and the depth curve keeps a
geometric shape with per-step success `p`. The number that matters is `p`
against the measured depth-one accuracy. If they are close, credit assignment
was the whole problem and the six previous failures were an objective bug. If
`p` is far below depth-one accuracy, the second lookup is intrinsically harder
than the first, and that asymmetry is the fact every other mechanism has to
explain.

To be wrong: depth two stays at zero under per-stage reward and per-stage
retry. That kills H1 outright.

Cheapest distinguisher: it is the only mechanism predicting a geometric curve.
Everything that installs state predicts a flat one.

### M5, strange. Per-episode opcode allocation with external execution

The episode header declares K empty opcode slots. The policy fills a slot by
emitting input and output pairs copied out of the evidence, terminated by a
marker; the environment fits the smallest total function consistent with them,
rejects inconsistent sets, and installs the result as a callable named by the
slot. The policy then writes a program in a two-token syntax, `slot arg`, and
the environment executes it and returns the value through the existing
`<|result|>` channel. Composition leaves the network entirely. What the network
must do is copy and schedule, which is the operation the pointer head already
performs.

Prediction: near ceiling at every depth, with residual error confined to slot
filling and therefore independent of depth. This is the ceiling measurement for
externalised composition, and it converts the research question into "can the
model define the opcode", which is a selection problem the system already
solves.

To be wrong: slot filling fails, so accuracy is bounded by copy accuracy and
falls with depth anyway. That would mean even scheduling is beyond the
substrate and would make H5 much more likely.

Cheapest distinguisher: slot-fill accuracy and program accuracy are measured
separately. Nothing else on this slate decomposes that way.

### M6, strange. Rebound register tokens, or variable binding at inference

Reserve R vocabulary slots `r0..r7` carrying no pretrained meaning. When the
environment declares a binding, it writes a line naming it and simultaneously
sets the embedding row for that register to the bound token's embedding plus a
learned register tag, and the unembedding row to match. Nothing is trained and
no module is added; embedding rows are swapped per episode and restored after.
The policy writes `r0` where it means the current value and reads it back as a
key at the next office.

The question this answers is whether the failure is about the key being a
literal token in the stream or about the identity of the content the key
carries. THESIS.md assumes the weights hold variable binding, so symbols can
carry local meaning. Nobody has checked.

Prediction: if H2 is right, depth two under register binding rises to roughly
the square of depth-one accuracy, so near 0.7 from a depth-one figure around
0.84. If H3 is right, it stays at zero.

To be wrong: register tokens decode as noise and nothing moves, which rules out
the whole class of interventions that give the model a name for an
intermediate.

Cheapest distinguisher: it needs no training and no new module, so it is the
cheapest item here that can change a belief.

## 7. The ranked slate

Ranked by hypotheses eliminated per experiment, in either outcome, not by
probability of success.

### Rank 1. E0, the re-keying rescue ladder

Not a mechanism. A localiser, and the precondition for choosing among the
mechanisms. Four rungs on the repro, none of them requiring training.

R0, depth d as generated. R1, the environment splices the gold intermediate
back in as a fresh sub-question after each round, turning a depth-d problem
into d independent depth-one problems; this is the "supply intermediate
results, not the answer" row of the rescue matrix in PREREGISTERED.md, which
has never been run. R2, as R1 but splicing the model's own previous answer
instead of the gold one, so the chain is self-driven and only the re-keying is
done for it. R3, the model is asked to write the intermediate itself with no
help.

Prediction, on the record: R1 recovers to approximately `p1^d`, so about 0.29
at depth two and 0.16 at depth three from the sampled depth-one rate of 0.5375,
or about 0.71 and 0.59 from the greedy rate of 0.84. R2 recovers somewhat less.
R3 recovers nothing.

What it separates. If R1 rescues, then the substrate can execute a lookup keyed
by a value it was handed but cannot route its own output back in as a key. H2
and H3 die, H7 becomes the explanation, and compounding is restored as a
description of the rescued system rather than of the broken one. That promotes
M2, whose loop count is a runtime knob rather than something the policy must
decide, and demotes M1 and M6. If R1 does not rescue, the substrate cannot
execute a lookup keyed by anything it was not handed in the question, H7 is
downstream of a representation failure rather than the cause, and M1, M6 and M5
become the live options while M4 is close to pointless.

Roughly half the mechanism list is eliminated either way, for about a day of
work and no training. Nothing else on this slate has that ratio.

One rung is nearly free and should be run first: R1 at depth two with the gold
intermediate supplied, against R0 at depth two, both already generated. If the
gold intermediate alone moves depth two off 0.000, that single number decides
the shape of the whole programme.

### Rank 2. M1, compiled operator table with an APPLY primitive

The representation bet, and the one that can move depth from two to twelve
rather than from two to three. Its train-shallow test-deep protocol is a
falsifiable extrapolation claim rather than an accuracy claim.

If it works, the depth curve goes flat and the failure relocates entirely into
compilation, which is a selection problem this project already knows how to
attack. If it fails with a verified-correct table, it eliminates the entire
"make the acquired rule executable" family in one experiment, which is most of
the candidate empty space in DISCOVERY.md, and moves the weight onto H5.

Cost is the highest on the slate: two new heads and a training run. It is
ranked second rather than first only because E0 tells us whether to build the
compile side or the control side.

### Rank 3. M6, rebound register tokens

Cheapest belief-changer. It attacks H2 against H3 directly, needs no training,
and tests an assumption THESIS.md makes explicitly and has never verified. A
positive result would make M1 and M3 unnecessary, since the missing piece would
be binding rather than compilation. A negative result rules out every
intervention that works by giving the intermediate a name.

### Rank 4. M2, value-keyed re-entrant retrieval

Most of the parts exist in `src/latentret` and `src/train/model.py`, and it
turns P2, the recurrence-rescue prediction, into something positional and
therefore falsifiable: the cliff should track the loop budget. It separates
"recurrence buys more time to re-read" from "recurrence provides somewhere to
put the value", which is the distinction the governing question is about.
Ranked below M6 because it costs a training run to learn what M6 might reveal
for free.

### Rank 5. M5, per-episode opcode allocation

Establishes the ceiling for externalised composition and is the fallback if the
substrate genuinely cannot hold a value register. Lower information gain than
the ranks above because a positive result is close to expected and therefore
changes little; its value is almost entirely in the negative branch, where
failure would be strong evidence for H5.

### Rank 6. M3, ephemeral association installation

High variance and cleanly distinguishable from M1 by its interference
signature, which is why it is on the slate at all. It is below M5 because its
positive and negative branches both leave several hypotheses standing.

### Rank 7. M4, stage-supervised composition

Most likely to produce a number, least likely to change a belief. Demoted
deliberately, under the ranking rule. It earns its place only through its
negative branch: if per-stage reward with per-stage retry still yields zero at
depth two, H1 is dead and every remaining explanation is architectural. Run it
after E0, and only if E0's R1 rung rescues.

## 8. Caveats

The checkpoint is RL-overfit to three question templates. Rebuilding the repro
inside one of those templates was necessary to get a working depth one, and
the size of that effect is itself reported above. Every number here is
therefore about this checkpoint and not about 350M models in general. Before
any mechanism is built, the depth curve should be repeated on the pretrained
checkpoint without the RL stage, to confirm the cliff is not an artefact of the
RL run.

The repro measures sequential depth only. Relational breadth and novel
composition, the other two kinds in PREREGISTERED.md, are not pooled with it
and are not measured here.
