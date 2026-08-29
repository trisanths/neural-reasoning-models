# Pre-registered predictions

Recorded before the primitive suite, the eight-level benchmark, or the substrate
sweep returned any result. Written down so they can be wrong on the record.

## P1, composition-first

As substrate size decreases, the earliest and largest degradation will occur in
novel multi-step composition of acquired procedures, before intent parsing, gap
detection, retrieval selection, individual abstraction induction, or
verification. The composition deficit will persist under oracle retrieval and
oracle skill extraction, indicating it is not primarily an information-access
failure.

Basis: six independent objectives failed to teach computation over an acquired
rule at 350M, each ending at 0.000 after one to three thousand steps with healthy
reward variance; a pointer head lifted copy-heavy accuracy from 0.021 to 0.514
while being slightly worse where arithmetic was required; and a controlled 4B
versus 27B comparison of the same generation shows factual knowledge retaining 92
percent under a 6.75x parameter cut against 30 to 69 percent for search depth.

Falsified if any other primitive degrades earlier or more steeply, or if oracle
retrieval or oracle abstractions rescue composition.

## P2, recurrence rescue

Increasing recurrent latent computation at fixed parameter count will selectively
raise maximum compositional depth substantially more than it improves retrieval
selection or intent understanding.

Basis: the Huginn recurrent-depth result saturates near eight iterations on
knowledge and commonsense tasks while continuing to gain on math, code and
multi-step reasoning, which is the same split our own measurements show.

Falsified if extra recurrence lifts all primitives roughly equally, or lifts
retrieval and intent more than composition, or lifts nothing.

## P3, capacity versus trainability

If direct isolated composition training largely rescues small models while
integrated acquisition does not, then parameter count is not the dominant
bottleneck and the work should redirect toward the learned-skill representation
and the interface between acquisition and use.

This is the most decision-relevant of the three. Every primitive is therefore
measured twice: integrated capability as a function of substrate size, and
oracle-isolated capability as a function of substrate size. The distance between
the curves is the architecture and training gap. The point where even the
oracle-isolated version fails is evidence of a capacity gap.

## The rescue matrix

For every faculty, intervene by replacing it with an oracle and observe whether
the episode is rescued. A failed integrated episode otherwise smears its failure
downstream and cannot be localised.

| Faculty | Normal condition | Rescue intervention |
|---|---|---|
| Intent understanding | raw problem | supply the canonical structured goal |
| Gap recognition | model identifies what it lacks | supply the gold capability gap |
| Acquisition and search | model searches | supply the gold source chapter |
| Abstraction construction | model reads the lesson | supply the gold structured skill |
| Composition | model combines learned operations | supply intermediate results, not the answer |
| Verification | model checks itself | supply a perfect verifier signal |
| Memory and use | model preserves the acquired skill | re-inject the gold acquired state |

The target output is not "composition scores 21 percent" but a located failure:
which faculties succeed, at what depth the integrated system collapses, and which
oracle interventions rescue it.

## Three kinds of composition, measured separately

They may have entirely different scaling laws, so they are never pooled.

Sequential depth: carrying a computation through many chained transformations.

Relational breadth: integrating many simultaneously relevant constraints to reach
one conclusion.

Novel composition: forming a program from procedures each learned independently
and never seen combined. This is the acquisition test proper, since a model can
memorise the parts and still fail to build the whole.

## The experimental triangle

What breaks, from the primitive suite. How hard learning can get, from the
eight-level benchmark. How small the learner can get, from the substrate sweep.

Every failure yields the next architectural question, so the programme produces
knowledge whether or not the sub-billion-parameter outcome holds.

## H7, registered 2026-08-28, before the rescue ladder was run

The minimal repro (`src/disc/minrepro.py`) puts a wall between depth one and
depth two that is total, and locates it in the control signal rather than in
any computation.

Depth one scores 0.5375 pass@1 and 0.950 pass@4. Depths two, three and four
score 0.0000 on both, over 1200 rollouts, on a task whose depth-one form the
same checkpoint answers at 0.969 greedy.

Two facts move the reading away from capacity.

Error compounding is dead. Independent lookups at the measured depth-one rate
predict 0.289 at depth two. Observed is zero in 400, and pass@4 is also zero.
Under a compounding model the chance of that is around 10^-59. Depth two is not
two copies of depth one.

The chain runs exactly one step and halts. A quarter of depth-two rollouts emit
the correct answer to the depth-one question embedded inside the depth-two
question, and the classes for later intermediates never appear once in 800
rollouts. Mean retrieval rounds falls as the problem deepens: 0.99, 0.73, 0.56,
0.54. The policy issues fewer queries exactly when more evidence is needed, so
the second table is never fetched at all.

H7 states the failure is the continuation decision: the substrate has no
representation of being unfinished, and the halting choice sits on a token
policy that makes it wrongly.

Two supporting boundaries. Referent ambiguity is not the cause; the closed
alphabet variant, where every token is both a key and a value, leaves depth one
at 0.545 and depth two at 0.000 with the same stop-after-one signature. Page
clutter is separable and expensive but is not the cause either; going from two
gold pages to six costs depth one 0.5375 to 0.125 without touching depth two.

With both tables already in the prompt there is no cliff: 0.070, 0.0175, 0.0150
at depths one to three. Depth two yields 7 correct in 400 where retrieval yields
0 in 400, from a depth-one rate 7.7 times higher. Removing the halting problem
moves depth two off zero, and does not by itself produce composition.

### E0, the re-keying rescue ladder, predictions on record

R0 is depth d as generated. R1 splices the gold intermediate back in after each
round, making a depth-d problem into d depth-one problems. R2 splices the
model's own previous answer instead. R3 asks the model to write the intermediate
unaided.

Predicted: R1 recovers to about p1^d, near 0.29 at depth two and 0.16 at depth
three from the sampled rate, or 0.71 and 0.59 from the greedy rate. R2 recovers
less. R3 recovers nothing.

If R1 rescues, the substrate executes a lookup keyed by a value it was handed
but cannot route its own output back in as a key. The failure is control, H2 and
H3 die, and the work goes to where the continuation decision lives.

If R1 does not rescue, the substrate cannot execute a lookup keyed by anything
it was not handed in the question, H7 is downstream of a representation failure
rather than its cause, and the work goes to making the acquired rule executable.

Either outcome eliminates about half the mechanism slate in `src/disc/SLATE.md`
for a day of work and no training.

### A caveat that bounds the headline result

The repro's first notation scored at or below 0.19 at depth one where the
routing idiom reaches 0.84, and the two were never measured under one matched
condition because presentation moved as well. If surface form accounts for most
of that gap, the 0.680 rule-application result generalises across invented
systems within a template and not across templates. The renderer swap that
settles this is running; until it reports, the headline is stated with this
bound attached.

## H8, registered 2026-08-28, before the mathgen evaluation was run

The invented-mathematics generator in `src/mathgen/` measures a property of its
own exercises that this project had not been separating, and the separation is a
direct test of the headline result.

An exercise is labelled `stated_in_a_chapter` when the textbook prints its answer
somewhere, and `derived_by_computation` when it does not. The label is measured
rather than asserted: the generator renders the string the textbook would print
if it stated this answer, and searches the prose for it. Over 100 universes the
split is 2329 stated against 2061 derived. Both families pass an identical
necessity check, because asking for the extension of a definition is retrieval
while asking for the value of a nested expression is not.

On this project those two families have already been measured far apart. The
pointer head reached 0.514 on copy-heavy items against 0.021 for generation, and
computing over an acquired rule scored 0.000 under six separate objectives.

H8 predicts `stated_in_a_chapter` lands near 0.514 and `derived_by_computation`
lands near 0.000.

If instead the two families score close together and high, the 0.680
rule-application result was measuring retrieval rather than rule application, and
the project's headline claim is much weaker than it has been stated. If they
score close together and low, the instrument is harder than the skillacq families
in some way that is not the answer source, and the harness gate on
`substitution_rule` and `threshold_rule` is what distinguishes those two cases.

The evaluation is required to report the gate first, to split every figure by
answer source, and never to report a number pooled across it. Pooling is the
error the instrument exists to expose.

### The dependency axis

Each universe carries a theory graph whose longest path is six edges, and every
exercise carries the chapters it requires. Serving only chapters 1..k and scoring
exercises that need more than k measures whether a result can be carried across a
dependency edge that cannot be looked up.

If that curve shows the same total wall between one and two that the minimal
composition repro found, the wall has appeared in a second, independently built
instrument, which is much stronger than one repro. If it decays gradually
instead, the two instruments disagree, and the disagreement is the finding.

## H9, the representation-horizon hypothesis, registered 2026-08-28 before running

The composition cliff is partly a representation-horizon failure. Ordinary
text-token autoregression turns a short computational decision into many poorly
aligned stochastic decisions. Reparameterizing planning into a compact
executable vocabulary should increase composition depth disproportionately at a
fixed substrate size.

### Why this is now the leading reading

The operator-graph experiment separates induction, composition and execution.
With the plan supplied and operator induction still the model's own job,
sequential accuracy is flat at 1.000 from depth one through depth eight, and
flat at 0.573 to 0.640 on page wordings never seen in training. With the model
writing the plan, the same quantity falls from 1.000 to 0.013. Handing the model
gold operators instead changes nothing: plan_execute and oracle_ops agree to
three decimals at every depth.

So the substrate reads the page, induces the operator, and an executor chains it
to depth eight without loss. The loss is concentrated in emitting the plan.

The halting evidence points the same way. In the retrieval repro mean retrieval
rounds fall as depth rises, 0.99, 0.73, 0.56, 0.54, so the policy issues fewer
queries exactly when more evidence is required. Termination is being predicted as
a linguistic event rather than derived from an unmet obligation.

### The measured ceiling, which bounds every claim below

At depth eight, plan_execute is 0.013 and oracle_plan is 1.000. The 0.987 between
them is the representation gap on this task. Every condition is scored as the
fraction of that gap it recovers, at each depth, rather than as a raw accuracy.

### The ladder, and predictions on record

Same 350M checkpoint, same operators, same worlds, same seeds, same optimizer
steps. Only the plan representation changes.

A, an English plan. B, a symbolic plan in existing tokens. C, dedicated static
opcode tokens. D, typed opcode tokens with registers. E, D plus an externally
enforced goal stack that cannot terminate while an obligation is unresolved.
F, a non-autoregressive plan over graph slots.

Predicted ordering: A at the plan_execute baseline, B a modest gain, C a
substantial gain, D above C, E the largest on sequential depth because it is the
only condition addressing the measured halting failure, F the highest variance
and least predictable.

The quantity that matters is the shape in depth, not the value at any one depth.
A condition that lifts depth two but still collapses by depth eight has not
addressed the horizon; a condition that is flatter in depth has, even at a lower
absolute level.

### What would falsify it

If C through F all land at the plan_execute baseline, the plan vocabulary is not
the binding constraint and the planning failure is intrinsic to the substrate.
That would move the weight onto capacity readings this result currently argues
against.

If E does not beat D on sequential depth, then the halting failure is not
separable from the plan representation, and the goal stack is unnecessary
machinery.

### A bound this hypothesis must respect

Relational breadth has the opposite bottleneck. There oracle_plan collapses to
0.000 at breadth four and above while oracle_both stays at 1.000, so what fails
is the model's induction of a wide operator, not the plan. A plan vocabulary
cannot repair an operator induced wrongly. H9 therefore predicts movement on
sequential depth and novel composition and no movement on breadth. If breadth
moves as well, the localisation above is wrong and should be re-derived.

### The version that is not in the literature

Static opcodes still assume the operation existed during training. The test that
matters for this project is dynamic opcode induction: generate a universe after
training, give the model prose defining an unseen operation, have a compiler head
emit an episode-scoped symbol with its arity, types and latent implementation
state, insert that symbol into a temporary vocabulary, and let the planner emit
only the symbol while the executor interprets its episode-specific state. Text
becomes a new vocabulary item, which becomes new computation, at inference time.

## H10, the autoregressive planning horizon, registered 2026-08-28 before running

The trace control removes the convenient explanation. Trace writes the same
decomposition in tokens, computes every step itself and has explicit
intermediate supervision, and it still dies where everything else dies.

Sequential depth, original wording, n=150 per cell:

| depth | direct | trace | plan_execute | oracle_plan |
|---|---|---|---|---|
| 1 | 0.480 | 0.827 | 1.000 | 1.000 |
| 2 | 0.227 | 0.493 | 0.480 | 1.000 |
| 3 | 0.127 | 0.260 | 0.500 | 1.000 |
| 4 | 0.020 | 0.007 | 0.020 | 1.000 |
| 5 | 0.020 | 0.000 | 0.033 | 1.000 |
| 8 | 0.013 | 0.000 | 0.013 | 1.000 |

The recorded statement: sequential composition through the autoregressive token
channel has a hard horizon near three steps in this substrate, and increasing
supervision inside that channel improves the constant factor without extending
the horizon.

Two further facts constrain the reading. Under paraphrased wordings trace scores
0.187 at depth one, identical to direct at 0.187, so the whole trace advantage is
template bound, while oracle_plan stays flat near 0.59 across all eight depths.
And the shapes differ: trace decays smoothly before dying, while plan_execute
holds a plateau at 0.48 to 0.50 and then falls off a cliff. A plateau then cliff
is the signature of a fixed decision budget; a smooth decay is the signature of
accumulating per-step error.

What is licensed, stated exactly. Conditional on a correct externally supplied
plan, the model induces and executes individual operators with no observed
sequential-depth degradation through depth eight. When the model must express the
sequential composition itself through an autoregressive token stream, accuracy
collapses by about four steps even under explicit intermediate supervision. It is
NOT licensed to say that a 350M substrate composes to arbitrary depth.

### H10, stated so it can lose

The three-step wall belongs to the number of sequential discrete planning
decisions rather than to semantic composition depth.

Semantic depth and generation length are currently confounded, because a depth-d
plan is emitted in d decisions. The factorial separates them. Macro symbols let a
plan of semantic depth 8 be emitted in 8, 4, 2 or 1 decisions with identical
executor semantics, so accuracy can be plotted against autoregressive decision
depth rather than against composition depth.

H10a, the horizon reading: accuracy depends mostly on the number of plan
emissions. Semantic depth 8 emitted in one decision approaches oracle_plan.
H10b, the capacity reading: accuracy depends mostly on semantic depth, and macro
symbols do not help. This is the falsification of H10.
H10c: both axes carry independent slopes, and the surface separates them.

### Gold prefix and gold suffix

At semantic depth 8, supply the first k gold plan operations for k from 0 to 7
and require the model to finish. If the constraint is a fixed remaining planning
horizon, success should begin when about three decisions remain, near k=5, rather
than improving smoothly with k.

The gold suffix is the mirror: supply the last k operations and require the
beginning. If only remaining generation length matters, prefix and suffix should
behave differently in a predictable way. If uncertainty accumulates over semantic
state instead, the pattern differs.

### The plan probe, which separates cannot-plan from cannot-serialize

A remaining possibility is that the intended program is present in the latent
state before generation and is destroyed by serialization. Take the final prompt
hidden state and fit frozen probes to predict the operator at each plan position
one through eight, then repeat after each emitted token.

If positions four through eight read out above chance before generation while
behavior still dies at four, the substrate already holds a deeper plan than it
can serialize, and the work goes to a readout that does not pass through the
causal language channel. If future-position probes are at chance from the start,
long-range planning is genuinely absent and oracle_plan is bypassing a planner
the substrate does not have.

Both outcomes narrow the programme. The probe must be fitted on held-out worlds,
must report its chance level, and must report a control probe on shuffled labels,
because a probe with enough capacity will otherwise manufacture the result.

## H11, the vocabulary bottleneck between reasoning steps, registered 2026-08-28 before running

Every condition measured so far that dies near depth four passes its reasoning
state through the vocabulary between steps: hidden state, projection to logits,
selection of one symbol, re-embedding of that symbol. The one condition that runs
flat to depth eight, oracle_plan, does not construct the composition through that
channel at all.

H11 states the composition horizon is partly created by the projection into the
vocabulary between recurrent computations, and that removing it while holding the
substrate fixed extends the horizon.

The test is a latent recurrence in the style of Coconut: feed the hidden state
back rather than emitting and re-embedding a token. Its loss does not require the
continuous state to reconstruct a deleted linguistic step, only to support the
reasoning that follows, so the latent state is free to hold something the
vocabulary cannot express compactly, including several live alternatives rather
than one committed symbol.

### The conditions, with A, B, C and G already measured

A direct. B trace. C plan_execute. D latent recurrence. E latent recurrence
feeding an opcode plan. F masked iterative opcode planner, running separately.
G oracle_plan.

All non-oracle conditions train on plans through depth three only. Evaluation
runs to depth thirty two. Latent steps R sweep over 1, 2, 4, 8, 16, 32, 64.

### The prediction, which is about shape

What matters is not whether latent recurrence gains ten points at depth four. It
is whether the curve stops being a cliff. A condition that moves the cliff from
four to ten has found a second bottleneck underneath and is a different finding
from one that goes flat, and the report must distinguish them.

### The surface that matters most to the thesis

Sweep permanent parameters against latent recurrent steps and read composition
depth off the surface. The claim worth testing is that parameters mostly set the
computation available per iteration while recurrence sets the total attainable
reasoning depth. If that holds, a small substrate does not need a large parameter
count, it needs a transition function expressive enough to apply repeatedly,
which is much closer to this project's thesis than making a small transformer
unusually good.

### Boundary condition already measured, which cuts against the optimistic reading

Weight-tied recurrence does not automatically turn a memory-bound model into a
compute-bound one. The optimization lab measured a recurrent trunk running near
ten percent utilization, overhead-bound rather than compute-bound. So R=64 is not
free in wall clock, and the surface needs a measured time axis beside the
accuracy axis or it will recommend a configuration that does not deploy.

### Two ways this experiment produces a false negative

Latent recurrence is known to be hard to train without a curriculum that
progressively replaces written steps with latent ones. "Latent recurrence does
not work" and "latent recurrence did not train" are different findings and the
second is easy to mistake for the first. Whether a curriculum was needed must be
reported either way.

R latent steps cost R forward passes, so any gain must be checked against an
autoregressive arm given the same forward-pass budget. Without that arm the
result is test-time compute rather than the removal of the vocabulary bottleneck.

### The handoff, as a rescue instrument and not an architecture

Project the small model's hidden state into a larger frozen model's residual
space, run latent steps there, project back, and let the small model answer. If
the small model fails at a depth where the handoff succeeds, the information
needed was present in the small model's state and what is missing is machinery to
transform it. If the handoff also fails, the small model's state discarded
information that even a larger transformer cannot recover. These are different
architectural conclusions and no experiment in this project currently separates
them.

This is not a candidate architecture for Y. A 500M model paired with a 32B latent
reasoner is a 32.5B system, and intelligence per permanent parameter has to count
the whole thing. Its value is diagnostic.

The stronger use is computational distillation: rather than imitating the large
model's answer, train a tiny operator to imitate the transformation the large
model performs on a reasoning state, then shrink that operator until the
transformation stops being reproducible. The size at which it stops is a direct
measurement of the irreducible substrate this project is trying to find.

## H12, the training ceiling hypothesis, registered 2026-08-29 before running

Reading the emitted plans rather than only scoring answers moves the failure well
past composition.

Step count tracks the question up to three and then saturates, so a depth-eight
question receives a three-step plan. Novel composition fails at depth two, where
length is not the constraint, by writing the first operator symbol twice where the
gold plan names two distinct symbols. Operands, ordering and register wiring are
correct in both cases.

Training never showed a plan longer than three steps and never showed a plan using
two distinct operator symbols. Those are exactly the two observed ceilings.

H12 states the composition cliff is a plan-length and symbol-count generalisation
failure rather than a reasoning failure. The model composes correctly up to the
largest structure its training distribution contained, and cannot emit a structure
it never saw.

### Why this competes with H10 and is simpler

H10 attributed the roughly three-step wall to irreversible autoregressive
commitment. H12 attributes it to the training maximum being three. Both predict a
wall near three on the current checkpoint, so the existing data cannot separate
them.

H12 additionally explains, with no extra assumptions, why direct and trace die at
the same depth despite different channels, since both were trained on the same
plan lengths; why oracle_plan runs flat to depth eight, since a supplied plan
requires no length generalisation from the model; and why the minimal repro
succeeds only at depth one, since its RL stage trained on single-step tasks.

### The experiment that separates them

Vary the training ceiling and measure whether the test ceiling tracks it. Train
otherwise identical arms with maximum plan depth in 1, 2, 3, 4, 6 and 8, and with
maximum distinct operator symbols per plan in 1, 2 and 3. Evaluate every arm at
depths one to thirty two.

H12 predicts the achieved depth tracks the training maximum roughly one for one,
with a small constant of extrapolation, and that the novel-composition failure
disappears as soon as training contains plans using two distinct symbols.

H10 predicts the achieved depth saturates near three regardless of the training
maximum, because the constraint is the number of sequential discrete decisions
rather than the distribution.

A third outcome is available and would be the most useful: the test ceiling tracks
the training ceiling up to some point and then saturates. That would locate a real
horizon while showing that most of the observed wall was distributional, and it
would give the horizon a number rather than an argument.

### What each outcome implies for the programme

If H12 wins, the intervention is curriculum and data rather than a plan head, a
vocabulary, or latent recurrence, and the running architecture comparisons are
measuring a distributional artifact. They should be rerun with the training
ceiling raised past the evaluation range before their results mean anything.

If H10 wins, the architecture work stands and the training ceiling is incidental.

Either way the architecture experiments currently in flight need their training
maximum reported alongside every depth curve, since a curve that stops where its
training stopped says nothing about the mechanism under test.

### The bound this must respect

Relational breadth fails at induction, where oracle_plan collapses at breadth four
while oracle_both holds at 1.000. Raising a plan-length ceiling should not move
breadth. If it does, the induction reading of breadth is wrong.

## H12 result, 2026-08-29: the composition wall was the training ceiling

Eight arms from the same 350M base, same worlds, same seeds, 8000 steps at batch
32, varying only the maximum plan depth in training. The d3s1 arm reproduces the
published opgraph arm and its data stream is asserted byte-identical before
training starts.

Mean emitted plan steps and accuracy, sequential chains, gold operators, greedy,
n=100 per cell, chance floor 0.04 to 0.06:

| arm | 3 | 4 | 6 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| d1s1 | 1.0/0.00 | 1.0/0.01 | 1.0/0.01 | 1.0/0.02 | 1.0/0.00 | 1.0/0.00 |
| d3s1 | 3.0/1.00 | 3.0/0.01 | 2.7/0.03 | 3.0/0.02 | 3.0/0.02 | 3.0/0.02 |
| d6s1 | 3.0/1.00 | 4.0/1.00 | 6.0/1.00 | 6.0/0.04 | 6.0/0.03 | 6.0/0.01 |
| d8s1 | 3.0/1.00 | 4.0/1.00 | 6.0/1.00 | 8.0/0.99 | 8.4/0.04 | 8.6/0.01 |

Emitted length follows the diagonal to each arm's training ceiling and then
flattens on it exactly. Accuracy is a step function: 1.00 at and below the
ceiling, chance above. The depth-eight arm scores 0.99 on depth-eight chains
where the published arm scores 0.02.

The extrapolation constant is zero rather than small. No arm generalises one step
past its training maximum.

H10 is dead. There is no three-step autoregressive horizon; there was a
three-step training set. Every conclusion that treated the wall near three or
four as evidence about a mechanism was reading the training distribution.

### Checks

oracle_both 1.000 in all 272 cells. Truncation 0.000 and hedge 0.000 everywhere,
so no emitted length is a decoding artifact. Sampled decoding at 0.8 reproduces
greedy cell for cell. Under paraphrase the emitted length is unchanged, so the
ceiling is wording-independent, while accuracy falls purely through induction
(3077 to 4303 of 4400 pages parsed against 4400 of 4400 on the trained wording).

### No horizon located

Nothing in range saturates, so the true horizon has no number yet. Largest plan
ever written across arms: 1, 2, 3, 4, 10, 10. Locating a horizon needs arms
deeper than eight. The corpus at s3://decoupled-reasoner-009398924577/data/corpus/v1/
carries plans to 48, and src/opgraph/plan.py caps the parser at 32 steps, which
must be raised first or long plans score as parse failures.

### What did not move, and is now the real problem

Novel composition. Every arm emits about 1.0 distinct symbols where two are
needed, at chance, including the arms trained with more symbols. Caveat on the
record: those arms taught cross-page chains rather than two interchangeable
binary operators, so the stronger form of the manipulation is untested.

Relational breadth. Identical across all arms, 1.00 at breadth one to three and
0.00 at four to six. The induction reading survives the manipulation that moved
sequential depth, which is the cleanest evidence yet that breadth is a different
failure.

A trap worth recording: plan_execute reads 0.24 to 0.42 at breadth four to six,
above both oracles. It is two matched errors cancelling, since the model writes
three flags, the induced operator carries three flags, arities agree, and it is
correct whenever the dropped conditions did not matter. It is not a breadth curve
and must not be read as one.

### The first measured trade-off

The depth-eight arm has the worst paraphrase induction of any arm and about a
third of the shallower arms' paraphrase accuracy. Depth is bought against
induction robustness at a fixed step budget.

### Consequences

Any depth curve that stops near three is measuring the training distribution
rather than the mechanism under test. The plan-head comparison, the vocabulary
ladder and the latent-recurrence sweep all train through depth three and evaluate
past it, so each would produce a wall at three regardless of its mechanism.

Where an architecture claim still has something to measure: symbol selection, and
paraphrase induction robustness, especially the trade-off above.
