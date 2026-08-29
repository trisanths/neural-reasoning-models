# Audit, checks 5 and 6: plan leakage and executor independence

Target: the sequential depth curve from the operator-graph experiment, n=150 per
cell, and the reading placed on it, that "the model induces operators from pages
and an executor chains them to depth eight with no loss, so the entire failure
is in emitting the plan".

Verdict up front. Check 6 passes. The executor is clean: under `oracle_plan` it
runs the model's own induced operator object and nothing else, the gold plan
carries no operand values that make induction unnecessary, no intermediate value
reaches the model, and corrupting the induced operator drives accuracy to zero.
Check 5 passes on the channels it names: no packaging feature predicts the plan.

Both checks pass, and one of the three supporting internal claims dies with them.
`plan_execute` does not equal `oracle_ops` to three decimals; it differs in 5 of
26 cells and by as much as 0.420, in the direction where induced operators beat
gold ones. Two further things turned up that change what the headline row means
rather than what it measures: the plan target is a syntactic transduction that a
60-line parser solves exactly at every depth, and the induction step deletes the
associativity annotation on 300 of 300 binary operators, so the two conditions
whose agreement was offered as evidence differ only by a field the scheduler does
not read.

Everything below is measured on the shipped checkpoint `runs/opgraph.pt` with the
shipped tokenizer, through the shipped code path in `src/opgraph/run.py`, with a
recording proxy in front of the operator table. Code is in `src/audit/`.

## Check 5, plan leakage: PASSED

### The packaging channel is empty

A decision tree of depth four was fit on twelve surface features of a world and
nothing else: page character length, word count, line count, the position of the
operator page inside the shuffled retrieved set, the number of pages, the glyph
code point, the title length, the total length of all four pages, and two length
parities. The sentence that states associativity was deleted from every page
before any feature was computed, so the tree cannot read the answer off the text
it is measuring. It was fit on 4000 worlds from the training seed range and
tested on the 150 evaluation worlds.

| set | tree accuracy | majority baseline | n |
|---|---|---|---|
| train (seeds 0-3999) | 0.5212 | 0.5050 | 4000 |
| eval, style 0 | 0.4733 | 0.5267 | 150 |
| eval, style 1 | 0.5267 | 0.5267 | 150 |

The tree lands below the majority baseline out of sample. Page length parity, the
one channel that looked plausible because the two associativity sentences differ
in wording, splits 926/1054 for left and 925/1095 for right over 4000 worlds,
which is nothing. Page order, rule names, page lengths and token counts do not
encode the plan.

### But the plan target carries no semantic content at all

The scheduler's prompt is `<|world|> opgraph <|doc|> ops <signature line> <|q|>
plan <question> <|a|>`. It contains no page. The signature line is symbol, arity
and, where present, associativity. So the plan is a function of two short
strings, and a parser can be written for it.

`src/audit/check5.py` contains that parser: 60 lines, reads only the signature
line and the question, never a page, an operator body, or a gold answer. Its
plans were compared to the gold plans by exact string match, and were also
executed against gold operators to get an answer accuracy comparable to
`oracle_ops`.

| cell | surface parser, exact plan | same, associativity field deleted | surface parser answer accuracy | model `oracle_ops` |
|---|---|---|---|---|
| sequential d=1 | 1.000 | 1.000 | 1.000 | 1.000 |
| sequential d=2 | 1.000 | 0.447 | 1.000 | 0.480 |
| sequential d=3 | 1.000 | 0.493 | 1.000 | 0.507 |
| sequential d=4 | 1.000 | 0.493 | 1.000 | 0.020 |
| sequential d=5 | 1.000 | 0.493 | 1.000 | 0.033 |
| sequential d=6 | 1.000 | 0.487 | 1.000 | 0.020 |
| sequential d=7 | 1.000 | 0.513 | 1.000 | 0.007 |
| sequential d=8 | 1.000 | 0.487 | 1.000 | 0.013 |

150 items per cell. The same parser is exact on `sequential_paren` at depths 2 to
6, on `breadth` at 1 to 3 and on `units`, 2550 items in total, all at 1.000.

Two things follow. The first is that the plan-writing step involves no reading
and no semantics, so `plan_execute` at depth one being 1.000 is one template with
two operands copied out of the question, not composition. The second is a floor
for the plan task that the audited table does not have. A grammar-only policy
that always associates to the left, and therefore uses no information beyond the
operand order, answers correctly 0.460 to 0.520 of the time at every depth from 2
to 8. The trained scheduler is at 0.480 and 0.500 at depths 2 and 3, which is that
floor, and at 0.007 to 0.033 at depths 4 to 8, which is well below it.

Check 5 passes the test it was set: the packaging carries nothing. The finding
that matters more is the one it turned up on the way, which is that the target it
was checking for leaks is a syntactic transduction.

## Check 6, executor independence: PASSED

The whole of this section is instrumented rather than argued. `src/audit/leak_run.py`
replaces `src.opgraph.run.run_plan` with a wrapper that calls the real executor
in `src/opgraph/plan.py` through a dict subclass that logs every lookup and puts
a recording proxy in front of every operator, so each call is logged with the
`id()` of the `Operator` object that was actually invoked.

### 6a. The executor runs the induced operator, by object identity

150 sequential worlds hold 900 gold `Operator` objects and 900 induced ones, with
zero object ids in common, so identity separates them cleanly.

| condition | operator calls | resolved to an induced object | resolved to a gold object | executions where the table was 6 induced / 0 gold |
|---|---|---|---|---|
| `plan_execute` | 3132 | 3132 | 0 | 1200 / 1200 |
| `oracle_plan` | 5400 | 5400 | 0 | 1200 / 1200 |
| `oracle_ops` | 3140 | 0 | 3140 | 0 / 1200 |
| `oracle_both` | 5400 | 0 | 5400 | 0 / 1200 |

Under `oracle_plan` the executor invoked a model-induced operator 5400 times out
of 5400 and a gold operator zero times. The claim rested on an accuracy
difference; it is now a direct measurement.

### 6b. The gold plan carries no operand values that make induction unnecessary

Across 1200 gold plans at depths 1 to 8, holding 5400 steps:

- 5400 steps invoke an induced operator, 0 steps use a builtin (`add`, `sub`, `mul`)
- 1200 of 1200 plans end on a temporary; none ends on a literal
- 0 of 1200 plans contain an integer literal that does not appear in the question text
- at depth 8 a plan holds 9 literal arguments and 7 temporaries, which is exactly
  the 9 operands the question states and the 7 intermediates the executor must
  produce

The gold plan therefore supplies the tree shape and the operands the question
already gives in plain sight. It supplies no value the executor would otherwise
have to compute.

### 6c. No intermediate value reaches the model

Every prompt shown to the model was recorded and tagged with the condition that
showed it. Under `oracle_plan` and `oracle_both` the model is never called: zero
generate calls, zero prompts. The only prompts issued during the plan conditions
are 1200 under `plan_execute` and 1200 under `oracle_ops`, each of the form
`ops <signature line> <|q|> plan <question>`. Induction prompts carry one page and
no question. Nothing written back, because there is no loop to write back into.

### 6d. Corrupting the induced operator destroys `oracle_plan`

The gold plans were re-executed on CPU against the induced table with the body
replaced. Accuracy, 150 items per cell:

| depth | as induced | gold ops | body + 1 | identity | constant 0 | empty table |
|---|---|---|---|---|---|---|
| 1 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 3 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 4 | 1.000 | 1.000 | 0.013 | 0.000 | 0.013 | 0.000 |
| 5 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 6 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 7 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 8 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

There is no default operator, no silent identity, and an unknown symbol raises
rather than guessing. `run_plan` is honest.

### 6e. The reverse leak is real but tiny, and it is not structural

Two ways to reach a correct answer without the induced operator being right were
tested.

No-op paths, on the sequential grid, over 1200 `plan_execute` plans and 1200
`oracle_plan` plans: zero plans with no operator call, zero builtin calls, zero
zero-step plans. The escape hatch the grammar allows, a plan of the form
`ans <literal>` that returns a number without touching the operator table, is
never taken. Every non-zero cell of `plan_execute` at depths 4 to 8 (3, 5, 3, 1
and 2 items out of 150) is a three-step plan that lands on the gold value by
coincidence, 14 items out of 750, which is the whole of those five cells.

Wrong operators, on the paraphrase pass where induction actually fails, 1200
sequential items:

| induced operator for the symbol the question needs | items | correct under `oracle_plan` |
|---|---|---|
| body exactly gold | 712 | 712 |
| body present but wrong | 35 | 7 |
| symbol absent from the induced table | 453 | 0 |

A missing operator is a failure every time, so nothing is being filled in. A wrong
operator produces the gold answer 7 times in 35, which is numerical coincidence on
the particular arguments, and 7 items out of 1200 is 0.6 per cent of the
condition. The reported 0.599 for `oracle_plan@para` is (712 + 7) / 1200.

Check 6 passes on every part.

### 6f. There is a no-op family, and it is in `plan_execute` on breadth

The gold-plan path is clean. The model-plan path is not, on the one kind where
the operator's shape changes with the cell.

The procedure page defines `score` over one number and `b` flags, so gold arity is
`b + 1`. Training saw breadth 1 to 3 only. At breadth 4, 5 and 6, over 150 worlds
each:

| breadth | gold arity | induced arity | plan writes `score` with | plans that drop arguments | `plan_execute` correct | of those, every dropped flag was false | `oracle_ops` |
|---|---|---|---|---|---|---|---|
| 4 | 5 | 4 in 150/150 | 4 args in 150/150 | 150/150 | 63/150 = 0.420 | 47/63 | 0.000 |
| 5 | 6 | 4 in 150/150 | 4 args in 150/150 | 150/150 | 47/150 = 0.313 | 30/47 | 0.000 |
| 6 | 7 | 4 in 88, 3 in 26, 2 in 36 | 4 args in 150/150 | 150/150 | 17/150 = 0.113 | 4/17 | 0.000 |

Every correct item in those three cells, 127 of 127, comes from a plan that hands
the operator fewer arguments than the question has conditions, and 81 of those 127
are items where every dropped condition was a no-op, a flag that was not set and
therefore contributes zero. `oracle_ops` is 0.000 in the same cells because the
gold operator has the right arity and refuses a four-argument call.

So the 0.420, 0.313 and 0.113 in the breadth row of `plan_execute` are not partial
competence at breadth 4 to 6. They are a truncated plan meeting a truncated
operator on items where the truncation did not matter. This is the pattern the
falsification lane found before, an ablation reporting a real-looking number that
is carried by items where the missing work was zero.

One instrumentation caveat: the recording proxy logs a call after it returns, so
calls that raise are counted only through the per-execution marker. That is why
`oracle_plan` on breadth 6 shows 150 executions and zero completed operator calls,
which is the arity refusal, and it does not affect any accuracy number.

## What did not survive

### Dead: "plan_execute equals oracle_ops to three decimals at every depth"

It differs in 5 of the 26 cells of the grid, and the largest gap is 0.420.

| kind | depth | `plan_execute` | `oracle_ops` |
|---|---|---|---|
| sequential | 3 | 0.500 | 0.507 |
| novel | 3 | 0.013 | 0.027 |
| breadth | 4 | 0.420 | 0.000 |
| breadth | 5 | 0.313 | 0.000 |
| breadth | 6 | 0.113 | 0.000 |

The sign is the part that matters. On breadth the condition with model-induced
operators beats the condition with gold operators by up to 0.420. Gold operators
do not merely fail to help there, they hurt, and section 6f says why: the model's
plan is written for a four-argument operator, the induced operator happens to take
four arguments, and the gold operator does not.

The remaining claim, that `oracle_plan` and `oracle_both` diverge on relational
breadth at 0.000 against 1.000, is confirmed: the divergence is in the results
file and my rerun reproduces it. The inference drawn from it, that `oracle_plan`
therefore runs model-induced operators, is also correct, and section 6a now
establishes it directly rather than by inference.

### Dead: the reading of why the two conditions match on sequential

They match because the only difference between their prompts is a field the
scheduler does not read.

Induction drops the associativity clause on every single binary operator: 300 of
300 induced binary operators across the 150 sequential worlds carry no `(assoc ...)`,
while 300 of 300 gold ones do. The bodies are otherwise perfect, 900 of 900
induced operators exact in body and parameter list. So the operator table that
`plan_execute` hands the scheduler prints as `#/2 //2 score/4 ...` in 150 of 150
worlds, with no associativity field at all, while `oracle_ops` prints
`#/2/left //2/left ...` in 150 of 150.

Given that difference in the prompt, 1170 of 1200 model plans, 97.5 per cent, are
byte identical between the two conditions. And the direction the scheduler picks
is independent of the truth in both:

| condition | depth | gold left / model left | gold left / model right | gold right / model left | gold right / model right | agreement | chi square | phi |
|---|---|---|---|---|---|---|---|---|
| `plan_execute` | 2 | 34 | 33 | 47 | 36 | 0.467 | 0.516 | -0.059 |
| `oracle_ops` | 2 | 34 | 33 | 47 | 36 | 0.467 | 0.516 | -0.059 |
| `plan_execute` | 3 | 41 | 33 | 43 | 33 | 0.493 | 0.021 | -0.012 |
| `oracle_ops` | 3 | 40 | 34 | 41 | 35 | 0.500 | 0.000 | 0.001 |

One degree of freedom, so a chi square of 0.52 and 0.00 is no association at all.
The 0.480 and 0.500 cells of the audited table are a coin flip, not partial
competence, and they stay a coin flip when the correct answer is written into the
prompt.

### Survives, but says less than it was read to say

`oracle_plan` at 1.000 across depths 1 to 8 is real, and my instrumented rerun
reproduces the whole sequential row of the audited table exactly, including
`plan_execute` at 1.000, 0.480, 0.500, 0.020, 0.033, 0.020, 0.007, 0.013. But once
6a to 6e are in hand, what the flat row measures is that a Python function whose
body is exactly correct returns the same value the eighth time it is called as the
first. The content sits in the induction rate, 900 of 900 bodies exact on the
wording the arm trained on and 712 of 1200 items with an exact body under
paraphrase, and in the plan rate, which is at chance at depths 2 and 3 and below a
grammar-only floor from depth 4.

The claim "the entire failure is in emitting the plan" is true as bookkeeping and
misleading as a reading. Two separate things fail. At depths 2 and 3 the induction
step deletes the one notational fact the scheduler needs, and the scheduler
ignores that fact anyway when it is restored. From depth 4 the scheduler emits
exactly three steps whatever the question says: 150 of 150 plans at depths 4, 5,
7 and 8 have three steps, and 141 of 150 at depth 6. That is the training length
prior, not a composition limit, and a parser with no length prior scores 1.000 on
the same items.

## Reproduction

On the training box, `~/opg`, GPU chosen from `nvidia-smi` and pinned:

    PYTHONPATH=~/opg python src/audit/leak_run.py --kind sequential --style 0 \
        --out results/audit_leak_seq_s0.json
    PYTHONPATH=~/opg python src/audit/check5.py results/audit_check5.json
    PYTHONPATH=~/opg python src/audit/check6.py results/audit_leak_seq_s0.json
    PYTHONPATH=~/opg python src/audit/check6b.py results/audit_leak_seq_s0.json sequential
    PYTHONPATH=~/opg python src/audit/wrongop.py results/audit_leak_raw_s1.json out.json
    PYTHONPATH=~/opg python src/audit/gridcheck.py results/opgraph.json
    PYTHONPATH=~/opg python src/audit/planident.py results/audit_leak_seq_s0.json

The instrumented rerun of the sequential grid reproduces the audited numbers to
the digit, twice, on two different GPUs, at 21872 recorded executor events each
time.
