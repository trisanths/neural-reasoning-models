# How this project does research

## The governing question

What representation of newly acquired knowledge makes it behave like computation
rather than context?

If acquired procedures remain declarative tokens that the model re-reads on every
step, then deepening the engine only buys more time to stare at text it cannot
execute. Solve the representation and recurrence becomes the engine that runs the
acquired computation. Fail to solve it and depth is wasted.

## What the literature is for

Boundary conditions, not an implementation backlog. From each paper extract
exactly four things and move on: the phenomenon it demonstrated, the mechanism
that produced it, where that mechanism stopped working, and the assumption it
never challenged.

A paper may justify an experiment. A paper may never be the reason for one.

  Wrong: text-to-weights was shown to work, so test text-to-weights.
  Right: our failure appears to arise because acquired procedures remain
  declarative tokens rather than modifying the model's computation. One
  intervention is compiling procedural descriptions into ephemeral weights. Prior
  work establishes that text-to-weights is technically feasible but does not test
  our phenomenon. We therefore test whether compiling text into temporary
  operator weights causally increases novel composition depth.

## The direction of reasoning

Desired phenomenon, then necessary properties, then known failures, then
unexplored mechanism. Never the reverse. Combining every mechanism the literature
offers produces a collage, not an architecture.

The desired phenomenon here: a very small permanent substrate receives
information it did not previously hold, converts it into usable capability,
composes those capabilities, reasons as long as necessary, and approaches the
usefulness of far larger models.

## The loop, run per failure

1. Observe. Exactly what computation failed.
2. Minimise. The smallest example that still exhibits it.
3. Causally localise. Oracle-rescue the surrounding faculties one at a time.
4. Survey. Mechanisms addressing analogous computation, in any field.
5. Extract constraints. What worked, what failed, what assumption was retained.
6. Map the empty space. Which representations, objectives and combinations remain
   untested.
7. Invent at least five mechanisms, including at minimum one architectural, one
   objective or training, one representation, one memory or learning-rule, and
   one genuinely strange.
8. Rank by information gain, not by probability of success. An experiment with a
   one-in-five chance of moving composition depth from three to twelve because it
   changes the representation of computation is worth more than a reliable move
   from three to three point four.
9. Test.
10. Update beliefs. Name the assumption that died.
11. Go more extreme.

## The empty region this project targets

No system demonstrated, at small fixed parameter count, this full path: arbitrary
raw information, to inferred semantics and procedures, to newly constructed
executable primitives, to installation in ephemeral computational state, to
composition into programs never demonstrated in training, to recurrent execution
and revision, to testing the acquired capability, to repairing the temporary
machinery from its failures.

The distinction from adjacent work is the first arrow. Skill-to-weights methods
map a known-form description to a delta. Fast-weight methods compile associations.
Program-induction methods compose a vocabulary of primitives learned during
training. The hypothesis here is stronger: the primitive itself may not exist
before reading.

## Candidate empty spaces, none yet tested

Runtime creation of primitives: allocate a new operator at inference whose
semantics are induced from text and examples, rather than composing operators
learned in training.

Executable epistemic memory: memory entries holding an operator with its
preconditions, postconditions, invariants, type signature, failure cases and
verification procedure, so a textbook compiles into a library rather than a
summary.

Temporary architecture mutation: acquired knowledge alters the computational
graph. A recursive algorithm instantiates recurrence; a branching procedure
instantiates control flow; a theorem becomes a guarded callable transformation.
The fixed substrate becomes an interpreter that builds its own temporary machine.

Acquisition by experimentation: read, hypothesise an operator, synthesise a test,
execute, find the contradiction, revise, synthesise an adversarial case, revise
again. Closer to system identification than to retrieval.

Separating meaning from execution: one temporary structure for what a concept
means, another for how to use it, with practice and self-testing compiling the
first into the second. That transition may itself be the missing architecture.

Composition outside the language model: rather than requiring a small transformer
to simulate a lengthening implicit program inside its activations, make the
operator graph explicit, with a learned scheduler and a recurrent executor. Depth
then stops being something the backbone must simulate.

An inference-time internal instruction set: the episode allocates opcode slots
and induces their implementations, so each episode carries its own temporary
vocabulary of operations.

## One thing not to assume

That a neural network is the right representation for the temporary capability.
The permanent substrate is neural. The acquired capability could be fast weights,
a discrete program, a graph, a differentiable program, a tensor operator, a
symbolic rule, a latent vector, a state machine, or a combination. Which one it
should be is a discovery variable, not a design decision. Do not constrain this
system to look like a conventional model internally merely because conventional
models do.
