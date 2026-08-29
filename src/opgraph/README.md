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
