# Audit, checks 7 and 8: surface form and permuted operator semantics

Target: the sequential depth curve from the operator-graph experiment, n=150 per
cell, and the reading placed on it, that "the model induces operators from pages
and an executor chains them to depth eight with no loss, so the entire failure is
in emitting the plan".

Verdict up front. Check 7 fails and check 8 fails.

Check 7. The flat `oracle_plan` row at 1.000 to depth eight exists only under the
one page wording every arm trained on. Re-render the same pages, same seeds, same
operators, same questions, same gold plans and same page count in three other
wordings and the row falls to 0.087 to 0.207. The flatness survives, because a
flat row is what `oracle_plan` has to produce whatever happens: it is the
per-world induction rate multiplied by a Python function that does not degrade
with repetition. The level does not survive.

Check 8. Transposing the two operand roles inside each binary operator's rule,
while keeping the glyph, the sentence skeleton, the page's own worked examples
and every constant intact, gives a forced choice between the answer the page
implies and the answer the operator's training identity implies. Over 678 items
the model chose the training answer 678 times and the page answer 0 times. At the
level of the operator object, 290 of 290 distinguishable binary operators were
induced with the training identity and 0 with the page's. The claim that the model
induces operators from pages is dead. What it does is fill numerals into a
memorised template, and it does not read the page well enough to notice when the
template is wrong.

A hand written parser reading only the pages scores 1.000 at every depth from 1 to
8, on all four wordings and on the transposed pages, 150 items per cell.

Everything below runs the shipped checkpoints `runs/direct.pt`, `runs/trace.pt`
and `runs/opgraph.pt` through the shipped code path in `src/opgraph/run.py`. Code
is in `src/audit/surfaces.py`, `src/audit/pageparser.py`, `src/audit/run78.py`,
`src/audit/run78b.py`, `src/audit/analyze78.py` and `src/audit/parsercheck.py`.
Raw results are `results/audit_c78.json`, `results/audit_c78b.json`,
`results/audit_c78b_ops.json`, `results/audit_c78_ident.json` and
`results/audit_parser.json`.

## What is held fixed

`src/audit/surfaces.py` takes a world apart and puts it back together. It reads
the generator's parameters back out of the gold operator body, so it can re-render
a page without touching `src/opgraph/invent.py`. Its self test is that re-rendering
in style 0 reproduces `invent.py` byte for byte on 180 worlds, 720 pages, zero
mismatches.

Across every wording the run asserts, and finds, that the question strings, the
gold answers and the gold plans are identical to the trained-wording set at every
depth. The seed, the operator, the four pages, the retrieval order and the
question do not move. Only the prose does.

## Check 7, exact template swap: FAILED

### The three wordings

Style 0 is what every arm trained on. Style 1 is the paraphrase already shipped in
the results file, described in the package's own README as a weak one: different
prose, same underlying grammar. The three new ones change more.

* Style 2, a spec sheet. Field labels rather than sentences, the operands named
  explicitly, worked examples written `check: x=7, y=4 gives 7`.
* Style 3, a letter. No `x` and no `y` anywhere; the rule is stated over "the
  first number" and "the second number", and the examples are written out in
  words, "Seven / four came out 7".
* Style 4, examples first. The two worked examples open the page and the rule
  follows them, reversing the order of the page.

All three state the same rule, carry the same modulus sentence, the same
associativity sentence and the same two worked example pairs as style 0. The
parser below reads all of them at 1.000, which is the evidence that nothing was
lost or made ambiguous in the rewriting.

### The sequential row, every condition, 150 items per cell

| condition | depth | style 0 | style 2 | style 3 | style 4 | style 1 (shipped) |
|---|---|---|---|---|---|---|
| `direct_all` | 1 | 0.480 | 0.127 | 0.087 | 0.193 | 0.187 |
| `direct_all` | 8 | 0.013 | 0.013 | 0.013 | 0.013 | 0.000 |
| `trace_all` | 1 | 0.860 | 0.067 | 0.047 | 0.187 | 0.187 |
| `trace_all` | 8 | 0.000 | 0.000 | 0.013 | 0.007 | 0.013 |
| `plan_execute` | 1 | 1.000 | 0.187 | 0.207 | 0.087 | 0.600 |
| `plan_execute` | 8 | 0.013 | 0.000 | 0.000 | 0.000 | 0.007 |
| `oracle_plan` | 1 | 1.000 | 0.187 | 0.207 | 0.087 | 0.600 |
| `oracle_plan` | 2 | 1.000 | 0.153 | 0.160 | 0.093 | 0.640 |
| `oracle_plan` | 3 | 1.000 | 0.127 | 0.153 | 0.073 | 0.580 |
| `oracle_plan` | 4 | 1.000 | 0.187 | 0.187 | 0.153 | 0.587 |
| `oracle_plan` | 8 | 1.000 | 0.133 | 0.167 | 0.107 | 0.580 |

`oracle_ops` and `oracle_both` are not in that table, and were run on style 0 and
on the transposed pages only. They cannot move with the wording, because the plan
prompt is `ops <signature line> <|q|> plan <question>` and contains no page at
all, and the shipped evaluation skips them on the paraphrase for the same reason.
On style 0 `oracle_ops` reproduces the shipped row exactly, 1.000, 0.480, 0.507,
0.020, 0.013, and `oracle_both` is 1.000 at every depth. On the transposed pages
`oracle_both` is 1.000 at every depth on all 678 items, so the harness computes
the transposed truth correctly.

Two things in that table are worth stating plainly.

The trained wording is worth about a factor of seven on `oracle_plan`, from 1.000 to
a mean of 0.145 over the three new wordings and the five depths. The shipped
paraphrase, at 0.599, sits between the two, which is what a weak paraphrase should
do.

The trace advantage does not merely vanish under a new wording, it inverts. At
depth one style 0 gives 0.860 for trace against 0.480 for direct. Style 2 gives
0.067 against 0.127 and style 3 gives 0.047 against 0.087, so the arm with the
written-out decomposition is now the worse of the two. Style 4 gives 0.187 against
0.193, a tie.

### The flatness is not evidence about depth

`oracle_plan` supplies the gold plan and asks nothing of the model but induction.
Its answer is therefore a function of one thing per world: whether the induced
operator for the glyph the question uses is right. If it is, every depth for that
world is right; if it is not, every depth is wrong. So the row is flat by
construction at whatever the induction rate is, and the flat 1.000 row measures a
Python function returning the same value on its eighth call as on its first. The
new wordings make the point visible by producing flat rows at 0.15 rather than at
1.000.

The one family in this audit where `oracle_plan` is not flat is the out-of-support
constants control below, and the reason is instructive.

### Where check 7 actually fails

Induction stops producing an operator at all. Over 600 pages per family:

| family | pages that parsed as a defop | binary operators induced, of 300 | body agrees with the page | associativity clause kept |
|---|---|---|---|---|
| style 0 | 600 / 600 | 300 | 300 | 0 / 300 |
| style 2 | 368 / 600 | 110 | 27 | 0 / 110 |
| style 3 | 362 / 600 | 64 | 47 | 0 / 64 |
| style 4 | 436 / 600 | 52 | 34 | 0 / 52 |

"Body agrees" is equality on eight probe pairs, associativity ignored. The
associativity column reproduces the earlier lane's finding: induction deletes the
clause on every binary operator it emits, under every wording.

At the item level the same thing shows up as an execution failure, because the
gold plan names a symbol the induced table does not hold. At depth one, out of 150
items: style 2 executed 53 and answered 28 correctly, style 3 executed 31 and
answered 31 correctly, style 4 executed 25 and answered 13 correctly. The gap
between the probe-level rate and the item-level rate is a wrong operator landing
on the right value for the particular operands, and it narrows as depth grows: at
depth eight style 2 executed 58 and answered 20 correctly.

## Check 8, permuted operator semantics: FAILED

### The transposition

The wording stays at style 0, the glyph stays, the constants stay, the modulus
stays, the associativity sentence stays, the worked example format stays, and the
two operand roles inside the rule swap. The page's worked examples are recomputed
so the page states the swapped rule twice, in prose and in numbers.

Trained page:

```
To evaluate x / y, subtract y from x, multiply that difference by 2, then add 1.
Every result in this system is reduced modulo 100. ...
Worked example: 7 / 4 = 7.
Worked example: 12 / 5 = 15.
```

Transposed page, same world, same seed, same glyph:

```
To evaluate x / y, subtract x from y, multiply that difference by 2, then add 1.
Every result in this system is reduced modulo 100. ...
Worked example: 7 / 4 = 95.
Worked example: 12 / 5 = 87.
```

Items are the style 0 items with the page-implied answer recomputed by running the
same gold plan against the transposed operator. An item is kept only when the two
answers differ, which is the forced choice, and only when the page answer cannot
be echoed out of the question text. Of 750 items across five depths, 51 were
dropped as indistinguishable and 21 as copyable, leaving 678.

### Forced choice at the answer

`oracle_plan`, gold plan, model-induced operators, executor:

| depth | n | toward the page | toward training |
|---|---|---|---|
| 1 | 131 | 0.000 | 1.000 |
| 2 | 136 | 0.000 | 1.000 |
| 3 | 140 | 0.000 | 1.000 |
| 4 | 135 | 0.000 | 1.000 |
| 8 | 136 | 0.000 | 1.000 |
| all | 678 | 0 / 678 | 678 / 678 |

`plan_execute`, which adds the model's own plan on top, tracks the training answer
at exactly the rate the trained-wording curve tracks the gold answer: 1.000, 0.493,
0.479, 0.022, 0.015 against 1.000, 0.480, 0.500, 0.020, 0.013. The whole shipped
sequential row reappears, pointed at the wrong answer.

`oracle_both` is 1.000 on all 678, so the transposed harness computes the
transposed truth correctly. `oracle_ops`, which never sees a page, is unchanged at
1.000, 0.493, 0.493, 0.000, 0.022.

The `direct` and `trace` arms lean the same way, 28 of 678 toward training against
12 of 678 toward the page for `direct_all`, and 270 of 678 against 15 of 678 for
`plan_execute`, but `direct` and `trace` are so near the floor on the
transposed pages that the comparison carries nothing. The plan path is where the
question can be answered, because there the induced operator is an object that can
be read.

### Forced choice at the operator

150 worlds hold 300 binary operator pages. On eight probe pairs, 290 of the 300
transposed operators are distinguishable from their training identity; 10 are not,
and are excluded.

| outcome | count |
|---|---|
| induced body follows the page | 0 / 290 |
| induced body follows the training identity | 290 / 290 |
| induced body follows neither | 0 / 290 |
| no operator induced for the symbol | 0 / 290 |

Every page produced a parseable operator, 600 of 600 pages, and every one of them
was the operator the page did not define.

### What the model reads off a page, and what it does not

Three slots, three different behaviours, all measured on the same 300 operators.

The coefficients are read. A control family renumbers `a`, `b` and `c` to 9, 11
and 13, values the generator can never draw during training, keeping the trained
wording and the trained roles. All 300 induced operators carry the page's
coefficients exactly.

The modulus is not read. The same control sets the modulus to 97, where training
only ever shows 100 or 1000. All 300 induced operators write 100. Not one carried
the 97 the page states, in the same sentence position, three lines above two
worked examples that only make sense modulo 97.

The operand order is not read. 290 of 290, as above.

The associativity clause is neither read nor written. Every induced binary
operator omits it, on every family: 300 of 300 on style 0, on the renumbered
pages and on the transposed pages, and 110 of 110, 64 of 64 and 52 of 52 on the
three new wordings.

This is what the numeral copying costs the depth curve. On the renumbered family
the induced operator is right except for the modulus, so it agrees with the page
whenever no intermediate value crosses 97, and `oracle_plan` is 0.473 at depth 1,
0.127 at depth 2, 0.080 at depth 3, 0.100 at depth 4 and 0.013 at depth 8, 150
items per cell. That is the only family in this audit where `oracle_plan` has a
depth curve, and it has one because the induced operator is nearly right rather
than exactly right or exactly wrong.

### The page's own verification procedure catches it, and nothing acts on it

`src/opgraph/opdef.py` treats the worked examples as the operator's verification
procedure, and `verify` is called on every induction. On the trained wording, 900
of 900 induced operators self-verify. On the transposed pages, 610 of 900 do, and
the 290 that fail are exactly the 290 transposed binary operators.

The induced text shows why. The model reproduces the page's worked example lines
into the operator it writes, then writes a body that cannot produce them:

```
page: (defop / (x y) (% (+ (* 2 (- y x)) 1) 100) (assoc left) (ex (7 4) 95) (ex (12 5) 87))
got : (defop / (x y) (% (+ (* 2 (- x y)) 1) 100)              (ex (7 4) 95) (ex (12 5) 88))
```

207 of 300 induced operators reproduce both of the page's worked example clauses
exactly, and on 197 of those 207 the body contradicts the clauses it just copied.
The signal that would have caught the failure is computed on every induction,
recorded in `induction.self_verified`, and consulted by no condition.

## The trivial program baseline

`src/audit/pageparser.py` is a hand written parser and executor, 198 lines, of
which sixteen are the rule regexes.
It is handed exactly what `direct_all` is handed, the four pages concatenated in
the retriever's order plus the question string, and nothing else: no gold operator,
no gold plan, no gold answer, no model. It finds the page that mentions the glyph,
reads the modulus, reads the associativity, reads the rule, and folds the operands
in the stated direction. The sixteen regexes cover four rule shapes across four wordings.

Accuracy, 150 items per cell:

| depth | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| style 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| style 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| style 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| style 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| transposed | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

On the transposed pages it is 1.000 toward the page and 0.000 toward the training
identity at every depth, on 1095 items, which is the mirror image of the model.

So the parser equals `oracle_plan` at depth eight on the trained wording, 1.000
against 1.000, and beats it everywhere else: at depth eight by 0.867 on style 2, by 0.833 on
style 3, by 0.893 on style 4, and by 1.000 on the transposed pages. It also beats `plan_execute` at every
depth on every family, and `oracle_ops` at every depth from 2 to 8.

One honest note in the parser's disfavour. With only the trained wording's four
regexes enabled it scores 1.000 on style 0 and 0.000 on styles 2, 3 and 4, because
it refuses rather than guessing. The parser is as surface-bound as the model, by
construction; the difference is that adding a wording costs it four regexes and
the model cannot add one at all. What the parser establishes is that the pages
contain everything the answer needs, mechanically, under every wording, so the
model's drop is not the task getting harder.

## What is dead

### Dead: "the model induces operators from pages"

It induces from a template. Coefficients are copied, including values outside the
training support. Operand order comes from the template and not the page, 290 of
290. The modulus comes from the template and not the page, 300 of 300. The
associativity clause is dropped, 300 of 300. When the page states a rule the
template does not cover, the model writes the template's rule and appends the
page's worked example as evidence for a body that contradicts it, 197 of 300.

### Dead: the depth reading of the flat `oracle_plan` row

The row is flat because `oracle_plan` is a per-world induction outcome multiplied
by an exact interpreter. Flat rows at 0.087 to 0.207 come out of the same code
under three other wordings, and a non-flat row comes out of it when induction is
nearly right rather than binary. The 1.000 is the induction rate on one wording,
not a statement about composition to depth eight.

### Dead: the trace arm's advantage as a property of writing the decomposition out

At depth one it is 0.860 against 0.480 for direct on the trained wording, 0.067
against 0.127 on style 2, and 0.047 against 0.087 on style 3. Two of the three new
wordings put the trace arm below the arm it was built to beat.

### Survives

The harness. `oracle_both` is 1.000 on all five families and both control
families, 150 or 678 items per cell, including on pages whose operators were
transposed after training. The executor computes what it is told to compute.

`oracle_ops` and `oracle_both` are wording independent, exactly as the design
says, because the plan prompt carries no page.

## What would change the reading

The result as stated is narrower than it reads: it is about one page template. To
be about induction it would need the induction arm trained across several wordings
and tested on a held-out one, and it would need a page whose stated rule
contradicts the template to be followed rather than overwritten. The transposition
in check 8 is the cheapest available test of that and it is a clean zero, so the
gap is not marginal.

## Reproduction

On the training box, `~/opg`, with a GPU picked off `nvidia-smi` and pinned:

```
uv run python -m src.audit.surfaces                       # byte-identical style 0
uv run python -m src.audit.parsercheck results/audit_parser.json
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=$PWD uv run python -m src.audit.run78 \
  --out results/audit_c78.json --n 150 --batch-size 32
CUDA_VISIBLE_DEVICES=5 PYTHONPATH=$PWD uv run python -m src.audit.run78b \
  --out results/audit_c78b.json --n 150 --batch-size 24
uv run python -m src.audit.analyze78 results/audit_c78b_ops.json \
  results/audit_c78_ident.json
uv run python -m src.audit.report78 results/audit_c78.json
```

Reproduction note. The style 0 rows of `direct_all`, `direct_oracle_page`,
`plan_execute`, `oracle_plan`, `oracle_ops` and `oracle_both` come back identical
to the shipped table at all five depths. The `trace` arm drifts by up to 0.033,
0.860 here against 0.827 shipped at depth one, which is the arm with 256 token
generations and the one most exposed to kernel nondeterminism across GPUs. No
conclusion here rests on the trace arm to better than 0.05, and every check 7
comparison is between wordings measured in the same process on the same card.
