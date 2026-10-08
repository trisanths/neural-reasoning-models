# The training ceiling and the test ceiling

## The question

Reading the plans the opgraph arm actually emitted, rather than only scoring
its answers, turned up two ceilings. Step count tracks the question up to
three and then stops, so a depth eight question gets a three step plan. Novel
composition fails at depth two by writing the first operator symbol twice
where the gold plan names two distinct symbols, with operands, ordering and
register wiring correct in both cases.

Training contained neither structure. No plan longer than three steps, no
plan naming two distinct operator symbols. Two registered hypotheses predict
the same wall on that checkpoint and cannot be told apart from it.

* H12, the training ceiling. The composition cliff is a plan length and
  symbol count generalisation failure. The model composes up to the largest
  structure its training distribution held and cannot emit one it never saw.
* H10, the autoregressive horizon. The wall near three comes from irreversible
  sequential discrete commitment, not from the training distribution.

Varying the training ceiling separates them. If the test ceiling moves with
the training ceiling, H12. If it sits near three whatever the training
ceiling, H10. If it moves and then stops, there is a real horizon and this
measures where it is.

## What varies and what is held

Arms are named `d<D>s<S>`: `D` is the largest number of steps a training plan
may have, `S` is the largest number of distinct operator symbols one training
plan may name. Every arm starts from the same 350M base checkpoint, draws the
same worlds from the same seeds, sees four questions per world, and trains for
the same optimizer steps at the same batch size in sequences with the same
learning rate and schedule. The induction half of the stream is identical text
for every arm.

`src/ceiling/stream.py` is the only thing that changes. It asserts that at
`D=3, S=1` it rebuilds the original stream byte for byte before training
starts, so the `d3s1` arm is a replication of the published opgraph arm rather
than a near neighbour of it.

The depth ladder draws the flat chain from depths 1 to D and the parenthesised
form from 2 to D, which at D=3 is exactly the original's 1-to-3 and 2-to-3.

The symbol ladder replaces the unit conversion question with a chain across
two pages: a unit conversion feeding the assessment procedure at S=2, and the
procedure's decision on top of that at S=3. Two binary operators are never
combined in training at any setting, so the `novel` evaluation kind stays held
out throughout. What the S arms are shown is that a plan may name more than
one symbol, not which pair to combine.

One asymmetry is left in and reported rather than corrected: a higher depth
ceiling means longer targets, so the high D arms see more supervised tokens
over the same number of optimizer steps. The token counts are in each arm's
training log.

## What is measured

Accuracy is not the headline. The ceiling is visible in the plan the model
wrote, so every item's emitted plan is persisted to JSONL and compared to gold
structurally.

* emitted step count against required step count, as a distribution
* distinct operator symbols emitted against required
* plan parse rate, well typed rate, exact gold plan rate
* `shape_match`: the emitted plan inlined into an expression tree, operator
  symbols erased, compared to gold. A plan that is shape correct and symbol
  wrong has right operands, right ordering and right register wiring, which is
  what the observed novel failure looked like
* `operands_match`: the multiset of literals, so operand reading can fail
  separately from structure
* `hit_cap`: whether decoding stopped on the budget rather than on an end
  token. A plan cut off by the cap would read as a short plan, and short plans
  are the thing being counted, so the cap is recorded on every item

All four oracle conditions run per arm, so the induction, composition and
execution split is available at every training ceiling. `oracle_both` must
come out at 1.000 or the harness is broken.

Both page wordings run. Gold operators do not depend on the wording, so the
two ops-oracle conditions run on style 0 only. Greedy and sampled decoding
both run for the conditions where the model writes the plan; the gold plan
conditions ask nothing of the decoder beyond induction and run greedy only.

Relational breadth 1 to 6 runs for every arm. Breadth fails at induction,
with `oracle_plan` at 0.000 at breadth four while `oracle_both` holds 1.000,
so a plan length ceiling should not move it. If it moves, the induction
reading is wrong.

## Files

| path | what it holds |
|---|---|
| `src/ceiling/stream.py` | the ceiling-aware training stream and the parity assertion |
| `src/ceiling/planmetrics.py` | structural comparison of an emitted plan against gold |
| `src/ceiling/gen.py` | decoding at a temperature that reports its own truncation |
| `scripts/ceiling_train.py` | the opgraph trainer with the stream swapped and nothing else |
| `scripts/ceiling_eval.py` | four conditions, both wordings, both temperatures, per item records |
| `scripts/ceiling_report.py` | the ceiling tables |
| `scripts/ceiling_launch.sh` | training lanes |
| `scripts/ceiling_evaluate.sh` | evaluation lanes |
