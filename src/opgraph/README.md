# Composition outside the language model

## What this tests

A 350M fact-free model reads a page defining a system invented after training
and applies it, but computing or composing over the acquired rule fails
completely. Six objectives ended at 0.000. The reading of that failure taken
here is that an acquired procedure stays a declarative token sequence the model
re-reads at every step, so a lengthening composition has to be simulated inside
activations that were never shaped to hold one.

This package makes the program explicit instead. A page becomes an operator
object with a symbol, an arity, an executable body, and the page's worked
examples as its verification procedure. A question becomes a straight line plan
over those operators. An executor runs the plan. Composition depth is then the
length of a list, and nothing about it has to be simulated.

## The pieces

| file | what it holds |
|---|---|
| `opdef.py` | the operator object, the prefix expression language, parsing, execution, verification against worked examples |
| `plan.py` | plans, the executor, and the written out trace form used by the control arm |
| `invent.py` | invented worlds: pages, gold operators, and questions of known depth with their gold plans |
| `data.py` | the three prompt formats, the training stream per arm, and the evaluation sets |
| `run.py` | greedy decoding, batched induction, and each scored condition |

Scripts: `scripts/opgraph_train.py` fine tunes one arm, `scripts/opgraph_eval.py`
scores every condition on both page wordings, `scripts/opgraph_report.py` turns
the raw JSON into the depth table and the stage attribution, and
`scripts/opgraph_launch.sh` and `scripts/opgraph_evaluate.sh` drive the boxes.

## The arms, and why the comparison is fair

Three arms start from the same 350M checkpoint, draw the same worlds from the
same seeds, and see the same four questions per world, for the same number of
optimizer steps at the same batch size in sequences.

* **direct** answers the question from the pages. Half its training prompts
  carry all four pages and half carry only the pages the question needs, so the
  gold source chapter rescue is in distribution for it.
* **trace** writes the same decomposition out in tokens and computes every step
  itself. This is the strong control: same structure, same intermediate
  supervision, no external executor.
* **opgraph** induces an operator from each page and writes a plan for the
  question. The executor runs the plan.

The direct arm sees roughly twice the question-answer supervision of the
opgraph arm, since the opgraph arm spends half its steps on induction. That
asymmetry favours the baseline and is left in.

## What is held out

Training never shows a plan that uses two distinct operator symbols, and never
goes past depth three. Every depth above three and every question needing two
operators is therefore an extrapolation, equally, for all three arms.

Every page also has a second wording that states the same rule and implies the
same operator. Training only ever sees the first. The paraphrase pass separates
reading a page from matching a template.

## The three kinds of composition, never pooled

* **sequential** one operator chained d times, written flat, with the page
  stating which way it associates
* **breadth** one procedure integrating b simultaneous conditions, answered with
  the adjusted number rather than the accept or refuse decision, so the curve
  has no chance floor
* **novel** a parenthesised expression needing both operators, each defined on
  its own page and shown there only alone

## The conditions that localise the failure

| condition | induction | composition | execution |
|---|---|---|---|
| direct_all, direct_oracle_page | implicit | implicit | implicit |
| trace_all, trace_oracle_page | implicit | model, in tokens | model, in tokens |
| plan_execute | model | model | executor |
| oracle_plan | model | gold | executor |
| oracle_ops | gold | model | executor |
| oracle_both | gold | gold | executor |

`oracle_both` must come out at 1.000 or the harness is broken.

## Design notes worth knowing before reading a number

Binary operators always reduce modulo a stated modulus. Without that, a depth
eight chain returns a thirty digit integer and the depth curve becomes a
measurement of digit length.

Questions are rejection sampled so the answer never stands alone inside the
question text, which removes echoing as a way to score.

The plan language has three fixed arithmetic builtins, `add`, `sub` and `mul`.
No gold plan uses them, so their contribution to any reported number is zero,
but they remain callable and their use is counted.

Pages are generated from templates, so the induction step is closer to a
structured translation than to open ended reading. The paraphrase pass is the
only evidence here about how far induction generalises, and it is a weak
paraphrase: different prose, same underlying grammar. Nothing in this package
supports a claim about inducing operators from arbitrary text.

## What the run found

Execution is free and induction is nearly free. The wall is the plan.

With the plan supplied, sequential accuracy is 1.000 at every depth from one to
eight, and novel composition is 1.000 at every depth. Supplying gold operators
instead changes nothing: `plan_execute` and `oracle_ops` agree to three decimals
in every cell. So the executor chains an induced operator to depth eight without
loss, and the model's own induced operators are good enough to do it with.

With the model writing the plan, sequential holds 1.000 through depth three and
falls to 0.020 at depth four. That is not a decay. It is a cliff at the exact
depth training stopped.

Reading the plans the model actually wrote says why, and it is narrower than a
failure to compose. The number of steps it emits tracks the question exactly to
three and then saturates: depth four, five, six, seven and eight all get three
step plans. Asking for the plan one step at a time does not change this, and
sometimes returns fewer steps rather than more.

Novel composition fails a second way, at a depth where length is not the issue.
Gold at depth two is `t1 = > 7 6 ; t2 = ^ 5 t1`. The model writes
`t1 = ^ 7 6 ; t2 = ^ 5 t1`. Operands, order, register wiring and answer line are
all correct; the second distinct operator symbol is replaced by the first.
Training never showed a plan using two distinct symbols, and the model never
writes one.

Both failures are the same shape. Every content-dependent slot is filled
correctly, and the two structural parameters of the plan, its length and how
many distinct symbols it names, are pinned to the largest values training
showed. The scheduler is not failing to reason about the question. It is failing
to emit a structure outside the support the training distribution gave it.

## What the ladder adds

Six spellings of the same plan, changing nothing else: english sentences,
registers in ordinary text, dedicated opcode tokens, a typed instruction stream,
a goal stack, and a slot graph. Every rung holds through depth three and every
rung is at or near zero by depth four. The horizon is not a property of the
notation.

These rungs are smoke sized, eight items a cell, so the only claim they carry is
the one they make unanimously. The slot rung also sees two and a half times the
supervised tokens per step at matched optimizer steps, so its lower numbers
could be budget rather than representation, and nothing here separates the two.

## Two things a reader will otherwise over-read

Breadth above three is not a clean composition test. Training draws the wide
procedure's condition count from one, two and three, and evaluation sets it to
the depth, so a breadth six page defines an arity seven operator the model has
never had to induce. Induction breaks there rather than planning: `oracle_plan`
is 0.000 at breadth four to six while `oracle_both` is 1.000, because the gold
plan calls an arity the induced operator does not have. Essentially all 453 of
the induction failures across the eval fall on those pages; the other half of
the grid induces 2700 of 2700 operators exactly. `plan_execute` scoring 0.380 at
breadth four is the model writing a plan that matches its own wrong-arity
operator and sometimes landing on the right number, not evidence of composition.

The gold plan is close to free information. A surface-only transducer that reads
the operator order off the question reproduces the gold plan exactly, 1.000 in
every kind and depth in both wordings. Strip the associativity bit and it drops
to about 0.49 on flat chains, a coin flip, and a decision tree over page surface
statistics predicts that bit at chance on held-out pages, so the bit has to be
read from the page's words. `oracle_plan` at 1.000 to depth eight therefore
proves the executor works; it does not prove the plan was hard to produce. What
it sharpens is the negative: the scheduler cannot produce a plan that a surface
transducer plus one bit produces perfectly.
