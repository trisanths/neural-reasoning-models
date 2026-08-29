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

## Prior evidence, checked, and what it actually supports

Four results are commonly cited in support of this direction. All four were
verified, and they support something weaker than they are usually taken to mean.

RETRO reported a 7.5B retrieval-native model matching models 25x larger on the
Pile. Norlund et al. (EACL 2023 Findings) reproduced it at 425M and bucketed the
loss by token overlap: the gains come almost entirely from tokens overlapping
retrieved text, with a small net negative effect on non-overlapping tokens. Their
conclusion is that the improvement is verbatim copying. This is the only careful
separation anyone has published between "retrieved the answer and copied it" and
"integrated retrieved content into a computation", and it came out on the wrong
side for us. RETRO's own downstream numbers agree: 45.5 exact match on Natural
Questions against FiD's 51.4 from a far smaller model.

Atlas reported an 11B model beating PaLM-540B on Natural Questions 64-shot. Atlas
was gradient fine-tuned on those 64 examples, reader and retriever both, with a
387M-passage index of the exact domain the questions came from. PaLM was prompted,
with no gradients and no retrieval. The authors footnote this. It is not evidence
about the parameter-capability curve.

Co-LMLM externalises facts through dense queries at 360M and scores 21.7 on
SimpleQA Verified. That benchmark is explicitly designed to measure parametric
knowledge, and its own paper notes that enabling tools yields near-perfect scores.
The comparison models had no retrieval; Co-LMLM had a 240M-entry index of
Wikipedia fact spans. It evaluates no mathematical, procedural or multi-hop task,
and retrieves single atomic facts top-1.

Recurrent-depth work (Huginn, 3.5B) showed continued improvement with more
iterations up to the FLOP load of a 50B model. The authors are explicit that this
is compute equivalence, not capability equivalence, and their tables show it does
not reach a 50B model's scores. Usefully for us, gains saturate near eight
iterations on knowledge and commonsense tasks and keep accruing on math, code and
multi-step reasoning. Recurrence deepens computation in a model that already has
the machinery; it does not add machinery.

What this set actually establishes: factual capacity can be decoupled from
parameter count, and computational depth can be decoupled from parameter count.
What it leaves untouched, and in RETRO's case actively discourages, is whether
PROCEDURAL capability can be externalised. Three of the four compare a
retrieval-equipped model against models denied retrieval, so the counterargument
writes itself: give the large model the index and the comparison reverses.

One paper comes closer than the rest and the claim must be precise about it.
Yang et al. (Findings of EMNLP 2025) retrieve proofs and proof techniques from
raw textbooks and papers and show models transferring a retrieved technique to a
novel theorem. So it is wrong to say nobody has tested retrieving a procedure.
Their own limitation section draws the sharper boundary: no significant gain when
the needed proof strategy is fundamentally novel and encoded neither in the model
nor in the retrieved context. That boundary, not the absence of prior work, is
what this project targets.

The precise claim is therefore: existing retrieval systems can expose a model to
facts and to reusable solution patterns. The open question is whether a
deliberately knowledge-limited substrate can convert external instruction into
new executable abstractions, compose those abstractions beyond the demonstrated
patterns, and thereby acquire capabilities absent from its weights.

That is where this project sits, and it is why the invented-mathematics
benchmark matters more than another factual evaluation. Our own strongest result
is a procedure-retrieval result: a model reads a page stating a rule it has never
seen and applies it, 0.680 against 0.002 with a different page. And our pointer
head independently reproduced the Norlund split without knowing it, lifting
copy-heavy accuracy from 0.021 to 0.514 while being slightly worse where
arithmetic was required. The literature and our own measurements agree on where
the line falls. The open question is whether anything crosses it.

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

## The falsifiable target

Build the highest-intelligence-per-permanent-parameter general-purpose model,
while remaining competitive with substantially larger frontier systems at the
system level.

Stated as a target rather than a prediction. The denominator is permanent neural
parameters. Books, indices, the web and any other environmental information are
excluded from it, because they are information the world already contains rather
than learned computation. A person is not credited with the parameters of a
library.

The reference point is Qwen3.8-27B: a dense 27B with a hybrid Gated DeltaNet and
attention design, 64 layers, multi-token prediction, 262K native context
extensible to a million, positioned by its authors around intelligence density.
It is not a strawman. Note that "Max" in its family is a reasoning-effort setting
rather than a model name.

Against it: a 7B system at parity is a 4x parameter-efficiency result, 4B is
nearly 7x, and under 1B is more than 27x. If a sub-1B system approaches
frontier-class system capability, the conventional parameter-efficiency curve has
been broken rather than improved.

## Three efficiencies, reported separately

Intelligence per permanent parameter is the metric the thesis is about, and the
denominator counts only weights.

Intelligence per unit of inference compute prevents winning by running a small
model fifty thousand times. That may still be useful, but it is a different
result and must be reported as one.

Intelligence per dollar and per joule, counting inference, retrieval, search,
context processing, tool execution and temporary memory, is what decides whether
this replaces anything in practice.

Y does not have to win all three at once. A system with better capability, seven
times the parameter efficiency, lower cost and worse latency is already a
significant result, and latency then becomes an engineering problem.

## Two axes of intelligence

Static intelligence asks whether the model already knows something. Conventional
benchmarks measure this, and they structurally favour the conventional system,
because that is what its parameters were spent on.

Acquisitional intelligence asks whether the model can become competent at
something it did not know five minutes ago. That is this system's intended
advantage, and it is measured on unseen mathematical systems, newly released
interfaces, invented programming languages, synthetic scientific domains,
literature published after training, unfamiliar codebases, novel tools, and
problems requiring autonomous prerequisite learning.

Conventional benchmarks then become a second question rather than the primary
one: can the system recover a conventional model's capabilities through
acquisition rather than through memory?

The aggregate capability score weights novel reasoning, mathematics, coding,
agentic execution, learning and acquisition, tool use, and general problem
solving. Intelligence density is that aggregate over permanent parameters; system
efficiency is that aggregate over total serving cost.

## Milestones

A. A model between 350M and 1B demonstrates genuine acquisition of an unseen
   skill, with controls that rule out memorisation.
B. A model at or under 1B beats ordinary models of the same size by a wide margin
   under system evaluation.
C. A model at or under 1B becomes competitive with 4 to 8B frontier models.
D. A 4B system beats Qwen3.8-27B on intelligence per parameter and approaches it
   in absolute capability.
E. A 4 to 7B system beats it broadly at the system level.
F. Push the substrate down again until the smallest size preserving the behaviour
   is found.

Endgame: a sub-1B system that converts additional retrieval, learning and
reasoning compute into capability, climbing toward the contemporary frontier.

The real target is not parity at some parameter count. It is that capability
becomes weakly coupled to permanent parameter count, so knowledge scales by
adding information, reasoning scales by adding test-time computation, skill
scales through online acquisition, memory scales externally, and the neural core
only grows when a cognitive operation is discovered that the substrate cannot
perform.

## Where we stand

Milestone A is provisionally met and under active attack. A fact-free 350M model
reads a page defining a system invented after its training and applies it, at
0.680 against 0.002 with a different system's page and 0.000 with a blank page,
retrieving and answering well-formed in all three conditions. The falsification
lane is currently attempting to destroy this result with a heuristic baseline, a
shortcut audit, a same-family control and an unseen-family transfer test. Until
that returns, the milestone is provisional.

Nothing beyond A has been attempted. The known obstacle is composition: six
independent objectives have failed to teach computation over an acquired rule,
and a controlled comparison of a 4B against a 27B of the same generation shows
factual knowledge retaining 92 percent under a 6.75x parameter cut while search
depth retains 30 to 69 percent. Acquisition is demonstrated; composition is not.


## Capacity floor is not trainability floor

Every primitive is measured twice: integrated capability as a function of
substrate size, and oracle-isolated capability as a function of substrate size.
The distance between those curves is the architecture and training gap. The point
where even the oracle-isolated version fails is evidence of a capacity gap.

This distinction decides what to build next. If a 350M model scores 8 percent on
composition depth three inside an integrated acquisition episode but 91 percent
when trained directly on isolated composition, then the substrate has the
machinery and the failure lives in representation, skill compilation, credit
assignment, curriculum, state interface or orchestration. If instead the model is
given gold intent, gold gap, gold retrieval, gold abstractions, a structured
skill state and direct composition training, and still falls off a cliff at depth
five while a 1B survives to depth eleven, that is a substrate bottleneck.

The programme therefore never asks whether a size works. It asks what breaks,
whether an oracle rescues it, whether recurrence rescues it, and whether the break
is capacity or trainability. That produces a map of the irreducible learner
rather than a leaderboard, and it produces knowledge whether or not the
sub-billion-parameter outcome holds.

## Correction, 2026-08-28: the rule-application headline is partly an artifact

A falsification lane re-ran the headline result against the shipped artifacts and
attacked it four ways. One third of it is a grading artifact, two thirds survive,
and the "correct page" framing collapses separately. Every number below replaces
what earlier sections of this document claim.

### The recorded number had no provenance

`scripts/skill_rule_test.py` on `s3://.../runs/final/rlsimple-503-921/` gives
textbook 0.958, wrong textbook 0.002, blank 0.000 at n=500, and 0.968 / 0.001 /
0.000 at n=1000. The controls reproduce to the digit. The headline does not: the
recorded 0.680 is stale and its provenance could not be found. Any statement
resting on 0.680 should be restated against the re-measured figure.

### The controls are weaker than they look

The invented answer words appear nowhere except the retrieved page, so a model
that copies any word off that page fails both controls without reading anything.
The chance floor is 0.401, not 0.000. The 0.958 / 0.002 / 0.000 pattern is
therefore consistent with copying, and on its own it does not establish reading.

### One family is a pure grading artifact

The environment grader accepts any prediction containing the gold answer within
six tokens of slack, so naming both candidate words scores correct whichever is
right. `threshold_rule` does that in 94.3% of its answers, and its first named
word is the same one 96.1% of the time regardless of the reading in the question,
which makes it a constant. Fifteen pairs of items were found with byte-identical
model output and opposite gold answers, and all thirty were graded correct. One
episode answered "wrenclo xilovi." to both reading 48, gold xilovi, and reading
12, gold wrenclo, and scored correct on both. Disallowing hedging moves
`threshold_rule` from 0.985 to 0.009.

`exception_rule` at 0.959 and `substitution_rule` at 0.951 are unaffected and are
real.

### What survives, with the floor stated

Textbook condition, n=1000, macro over three families:

| Scoring | Value |
|---|---|
| Published grader, contains with six token slack | 0.968 |
| Forced choice, first candidate word named | 0.795 |
| Naming more than one candidate counts wrong | 0.646 |
| Non-trivial items only, 416 of 1000 kept | 0.640 |
| Chance floor for that set | 0.401 |
| Chance corrected | 0.292 |

About two thirds of the raw score survives as raw score, and 0.292 of the
headroom above guessing is real rule application.

### The model reads values, and this part held under attack

A page with identical wording and permuted values moves the answer with the page:
0.938 forced choice toward the page-implied answer against 0.008 toward the
original for substitution, and 0.961 against 0.012 for exception. The attack
expected to be decisive failed to falsify and produced the strongest positive
evidence in the set. Value reading is real.

### The "correct page" framing does not survive

Placing a second system of the same family in the same store, differing only in
name and values, drops accuracy to 0.463. The model names the twin's candidate
words 48.8% of the time against its own 47.5%, which is a coin flip. Retitling
every page to name its own system does not help: 0.486, twin 47.7% against own
51.2%. A regex baseline reaches 0.993 on those same items.

So the model selects the right line off a rule page but cannot tell which
system's page it is reading. Claims of the form "with the correct page
retrievable" describe work the model does not do.

### Generalisation to new relation types fails at chance

Three relation types in the same style, never trained, on balanced scoring:
inverse_table 0.107 against a chance of 0.251, chain_rule 0.008 against 0.334,
band_rule 0.313 against 0.334. band_rule's apparent 0.671 under the shipped
grader is the same hedging artifact at a 94.2% hedge rate. A regex scored 0.993,
0.981 and 1.000 on the identical items. chain_rule is partly a retrieval failure,
since the two pages it needs were served together in only 3.6% of rollouts.

### The model loses to a parser

A roughly fifty line regex over the top ranked pages scores 1.000 against the
model's 0.968 on identical items, and beats it on every untrained family. Generic
value-blind heuristics are much weaker, the best being nearest invented word to a
question keyword at 0.387, so the task is not trivially guessable. It is trivially
programmable. The parser also degrades gracefully where the model collapses.

### Unresolved

On the textbook condition a chunk naming two or more candidates reached the model
in only 65.6% of rollouts, yet accuracy when no such chunk was served was 0.930.
Either the retrieval detection heuristic is too strict, since chunking may split
a rule page, or the model is scoring without the defining page. Not resolved.

### Consequences for the rest of the programme

Every accuracy in this project must now be reported with its chance floor, its
hedge rate, and a forced-choice score alongside the grader score, and must never
be pooled across families. A single artifact family inside a three-family macro
average moved the headline by a third.

## Correction 2, 2026-08-28: the acquisition result is frame matching

An independently built renderer swap answers the confound flagged in
`src/disc/SLATE.md` section 3. The result does not survive.

The independent harness cross-checks the first one: its native renderer gives
0.966 pooled against the falsification lane's 0.958 at n=500 and 0.968 at n=1000,
and it reproduced the hedging artifact from scratch, with native
`threshold_rule` naming both labels in 100 percent of greedy answers and 1.000
shipped becoming 0.000 forced. `exception_rule` and `substitution_rule` never
hedge in any renderer, so they carry the conclusion.

### Forced choice, greedy, per family, n=66 to 68 per cell

| Family | native | personnel | abstract | inventory | chance |
|---|---|---|---|---|---|
| substitution_rule | 0.970 | 0.045 | 0.045 | 0.015 | 0.200 |
| exception_rule | 1.000 | 0.606 | 0.258 | 0.106 | 0.500 |
| threshold_rule, artifact | 0.000 | 0.191 | 0.191 | 0.132 | 0.500 |

Three of four renderers on substitution fall below chance. The failures are not
near misses: 0.53 to 0.94 of answers in the distant renderers name no candidate
at all. exception discriminates poorly against a 0.500 floor and a 0.750
page-word floor, so substitution carries the weight.

### The mechanism, isolated

The chain task with a single document in the store removes page identification
entirely. Forced choice, chance 0.028:

routing 0.970, processing 0.840, routing_postvalue 0.830, routing_keyphrase
0.820, reaction 0.090, routing_frameb 0.030, inventory and abstract 0.010,
personnel 0.000.

`processing` shares no content word with the native idiom and scores 0.840.
`routing_frameb` keeps every content word and changes only the sentence frame,
scoring 0.030. Nouns cost 0.13. Sentence shape costs 0.94.

The sentence frame carries the result. The vocabulary does not.

### The escape that was closed

Under the twin control, native `substitution_rule` holds at 0.939 with the twin's
words named in 4.5 percent of answers, while native `exception_rule` falls from
1.000 to 0.682 with 28.8 percent twin naming. The family carrying the renderer
conclusion is the one that does identify its page, so the template effect is not
a page-identification confound.

### What this replaces

Under matched presentation the routing-to-abstract gap is 0.960, wider than the
0.19 to 0.84 that SLATE section 3 recorded with presentation confounded.
Template accounts for the whole gap and nothing remains for presentation.

### The statement that survives

This checkpoint binds new values into a sentence frame it already knows, and does
essentially nothing with a frame it does not know. That is consistent with the
untrained relation types scoring at or below chance, with the twin-system coin
flip on source identity, and with a fifty line parser outscoring the model.

Claims of inference-time skill acquisition are not supported. What is supported is
frame-conditioned value binding.

### The one axis pointing the other way

Under paraphrase, direct answering falls from 0.480 to 0.187 while oracle_plan
holds flat near 0.59 across all eight depths. The operator and plan interface is
markedly more frame-robust than direct answering, which is the single place the
architecture direction currently earns its keep.

### What this implies for the programme

If the sentence frame is the unit of generalisation, the intervention is frame
diversity in training rather than a better plan head. That is a data decision.
Any architecture result measured only inside the native frame should be read as
within-frame until it is rerun across renderers.

### Caveats carried

One checkpoint, rlsimple-503-921. Renderers are hand written rather than sampled.
A temperature 0.7 run lost 150 of 250 episodes in one arm to the 384 token prompt
cap, so the greedy tables above, where all four renderers keep exactly 200
questions, are the unfiltered ones and should be preferred.
