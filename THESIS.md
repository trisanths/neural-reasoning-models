# The thesis

This project is not building a small language model. It is building a different
computational object and testing whether that object can do what a large one
does.

## Two systems

X, the conventional system. One large static network whose parameters
simultaneously store declarative facts, mathematical knowledge, programming
interfaces, linguistic competence, procedural patterns, and reasoning machinery.
Capability is a function of parameter count. Learning happens during training,
the weights freeze, and inference applies what was learned.

Y, the system under test. A small permanent computation engine, an external
knowledge substrate, autonomous acquisition, temporary skill formation, and
adaptive test-time computation. Learning how to learn happens during training,
and the actual learning happens at inference.

Comparing X and Y by parameter count is close to the wrong abstraction. A
frontier model carries an enormous amount of precomputed civilization in its
weights. The hypothesis is that most of that does not need to live in the
reasoning engine.

## The capability function

For X, capability is approximately a function of parameters alone. For Y it is a
function of permanent parameters, accessible external knowledge, retrieval and
search quality, available test-time compute, temporary learned state, and the
ability to acquire new abstractions. That last term is the one ordinary
retrieval augmentation does not have, and it is the one this project exists to
build.

## The research question

Not "can retrieval improve small models" and not "can a 4B compete with a 27B".
The question is:

  How small can the permanent neural substrate become, if declarative knowledge,
  task-specific knowledge, and mathematical skill can all be acquired externally
  at inference time?

The answer might be 7B. It might be 800M. It might be 200M. Nothing is served by
deciding in advance; the experiment should discover the lower bound. The
substrate sweep is therefore a primary experiment, not a footnote: train the same
acquisition machinery at several sizes and find where the capability breaks.

## What the weights should contain

If the thesis holds, the model should not know calculus the way a conventional
model knows calculus. It should hold primitives instead: enough language to parse
a definition it has never seen; primitive logic and inference; variable binding,
so symbols can carry local meaning; composition of transformations; analogy
across domains; induction of rules from examples; causal dependency; search
control, meaning the recognition that some machinery is missing;
reading-to-model conversion, turning prose definitions into executable
conceptual structure; verification of its own interpretation; and meta-learning,
changing behaviour in response to newly acquired rules.

If those fit in a few hundred million parameters, there is no law requiring tens
of billions of active parameters to reason.

## Why the small version is the clean test

A 7B result invites the objection that 7B models already know a great deal. A
model in the hundreds of millions that fails closed-book, recognises what it
lacks, retrieves a textbook it has never seen, learns the machinery, passes
hidden-source tests on the newly acquired concepts, and then solves the original
problem, cannot be explained by hidden memorisation. That is why the
invented-mathematics benchmark matters: a small model cannot have memorised the
axioms of a mathematical universe generated after its training ended.

## Evaluation must be resource-matched, not context-matched

Giving Y a searchable library and X only the problem sounds unfair, and is not.
X's external memory is its own weights; Y's is a corpus. The honest comparison
holds resources constant, not inputs: comparable wall-clock time, comparable
energy, comparable dollars, comparable latency budget. Report capability per
parameter, per joule, per second, per dollar, and per byte of resident weights,
alongside raw capability.

Frontier parity also need not happen in one forward pass. A system that spends
two minutes understanding, identifying its gap, searching, reading, compiling a
skill, self-testing, reasoning and verifying, and arrives at the same answer with
orders of magnitude less resident memory, has demonstrated the thing. Speed is an
optimisation problem after capability is proven: cache acquired skills,
parallelise search, speculate retrieval, compile a book once, run recurrence
efficiently.

## Prior evidence that the conventional curve is a property of X

Three independent results point the same way, and none of them is sufficient
alone. RETRO showed a 7B retrieval-native model reaching language-modelling
performance comparable to models an order of magnitude larger, though later
analysis attributed part of that to overlap between the retrieval set and the
test data. Atlas showed an 11B retrieval model beating a 540B model on Natural
Questions in its evaluated few-shot setting. Recurrent-depth work showed a 3.5B
model continuing to improve as its computation was increased toward the FLOP load
of a much larger fixed-depth model, reusing the same parameters rather than
adding any. Work on continuous-query knowledge externalisation reports a 360M
model scoring competitively on a factual benchmark against far larger models.

Taken together: scaling non-parametric memory substitutes for weights on some
capabilities, scaling computation substitutes for weights on others, and scaling
external knowledge access can produce capability disproportionate to resident
parameters. The conventional parameter-capability curve is therefore a property
of X, and should not be inherited as a law governing Y.

## What our own evidence says so far

Established, with controls: a fact-free 350M model reads a page defining a system
invented after training and applies it, at 0.680 against 0.002 with a different
system's page and 0.000 with a blank page. A pointer head that selects spans from
evidence lifts copy-heavy accuracy from 0.021 to 0.514 while being slightly worse
where arithmetic is needed. Reinforcement learning against programmatic verifiers
is three to five orders of magnitude cheaper per point of accuracy than
pretraining.

Not established, and the current wall: composing or computing over an acquired
rule. Six objectives have failed at zero, and a controlled comparison of a 4B
against a 27B of the same generation shows factual knowledge retaining 92 percent
under a 6.75x parameter cut while search depth retains 30 to 69 percent. The
cheap axis is the one we have been externalising. The expensive axis is depth,
and the only lever we hold for it is test-time computation.

## The claim to be proven or disproven

Given a searchable textbook for a mathematical system that did not exist when
training ended, and a problem requiring that system, can a model in the hundreds
of millions of parameters autonomously discover what it must learn, acquire the
prerequisite structure, demonstrate mastery on unseen exercises, and transfer the
acquired machinery to solve the target, with no weight update?

Closed-book at chance, high accuracy after autonomous study. That result would
show the intelligence was in the parameters and the mathematics was not.
