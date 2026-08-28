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
