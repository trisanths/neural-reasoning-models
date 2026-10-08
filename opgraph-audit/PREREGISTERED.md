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
