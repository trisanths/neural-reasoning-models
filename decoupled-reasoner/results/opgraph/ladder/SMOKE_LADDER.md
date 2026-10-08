# The plan-representation ladder, smoke run

## What this run is and is not

Six rungs, each fine tuned from `ckpt/base350.pt` for 1500 optimizer steps at
batch size 16 over the same 8000 world seeds in the same shuffled order, then
scored on 8 items per cell at both decoding temperatures. The full sweep is 8000
steps at batch size 32 over 40000 worlds with 150 items per cell, and none of
the accuracies below should be read as the ladder's answer. What this run is for
is the three things that have to be true before the sweep is worth the compute:
every rung trains, every rung writes a plan the executor accepts, and every rung
returns `oracle_both` at 1.000.

All three hold for all six rungs.

## Harness check

`oracle_both` is 1.000 in every one of the 20 cells, for all six rungs, at both
temperatures. 240 cells, no exceptions. The gold plan is put through each
representation and read back before it is executed, so a lossy encoding would
show up here rather than as a quiet loss elsewhere.

`oracle_plan` is 1.000 at every sequential depth and every novel depth for all
six rungs, and 1.000, 1.000, 1.000, 0.000, 0.000, 0.000 across breadth one to
six for all six. That reproduces the recorded shape exactly: flat in depth,
collapsing at breadth four while `oracle_both` holds, which is what says the
breadth failure is induction and not composition.

Induction on the original wording is identical across the six rungs: 288 of 288
pages parsed, 432 of 432 operators induced, 408 exact, in every rung.

## Sequential depth, greedy, n=8 per cell

| rung | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| english | 1.00 | 1.00 | 0.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| symbolic | 1.00 | 0.62 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| opcode | 1.00 | 1.00 | 0.88 | 0.00 | 0.00 | 0.00 | 0.12 | 0.00 |
| typed | 1.00 | 1.00 | 0.88 | 0.12 | 0.12 | 0.00 | 0.00 | 0.00 |
| goalstack | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| slots | 1.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 |
| oracle_plan, all six | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

Sampled decoding agrees to within one item everywhere, so nothing here is a
greedy artifact. `oracle_ops` equals `plan_execute` to the last digit in every
cell of every rung, the same identity the original arms showed, so gold
operators change nothing about writing the plan.

At 1500 steps every rung is at chance from depth four on. No rung recovers a
measurable part of the gap at this scale, and no rung should be expected to: the
recorded `plan_execute` at depth four is 0.020 after 8000 steps. The number that
matters here is that the shape is the recorded shape and the ceiling is intact.

Slots is the one rung that is visibly behind inside the trained range, at 0.12
at depth two against 0.88 to 1.00 for the rest. It sees roughly two and a half
times the tokens per example and is trained on a masked objective rather than a
left to right one, so at matched optimizer steps it is further from convergence.
Whether that is a scale artifact or the representation is the first thing the
full sweep settles.

## Relational breadth, greedy, n=8 per cell

| rung | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| english | 1.00 | 1.00 | 1.00 | 0.25 | 0.38 | 0.25 |
| symbolic | 1.00 | 1.00 | 1.00 | 0.50 | 0.38 | 0.38 |
| opcode | 1.00 | 1.00 | 1.00 | 0.12 | 0.50 | 0.38 |
| typed | 1.00 | 1.00 | 1.00 | 0.25 | 0.12 | 0.12 |
| goalstack | 1.00 | 1.00 | 1.00 | 0.25 | 0.12 | 0.12 |
| slots | 0.50 | 0.75 | 0.50 | 0.00 | 0.12 | 0.25 |
| oracle_plan, all six | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| oracle_both, all six | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

The registered prediction is that the ladder does not move breadth, and nothing
here contradicts it. `plan_execute` beats `oracle_plan` at breadth four and above
in every rung, which is the same inversion the original experiment recorded: a
gold plan over a wrongly induced wide operator is worse than the model's own
plan, because no plan vocabulary can repair an operator that was induced wrongly.

## Novel composition

`plan_execute` is 0.000 at every depth for all six rungs. `oracle_plan` is 1.000
at every depth for all six. That is the recorded result at smoke scale.

## Rung E, whether the constraint binds

The point of the goal stack is that termination is not a token the model may
choose while an obligation is open. It binds, and the measurement says how hard.

Sequential, greedy, plan_execute:

| depth | bind events, ret | bind events, eot | returned | budget exhausted | accuracy |
|---|---|---|---|---|---|
| 1 | 0 | 8 | 1.00 | 0.00 | 1.00 |
| 2 | 0 | 15 | 1.00 | 0.00 | 1.00 |
| 3 | 0 | 22 | 1.00 | 0.00 | 1.00 |
| 4 | 42 | 55 | 0.62 | 0.38 | 0.00 |
| 5 | 49 | 76 | 0.25 | 0.75 | 0.00 |
| 6 | 46 | 72 | 0.38 | 0.62 | 0.00 |
| 7 | 42 | 75 | 0.25 | 0.62 | 0.00 |
| 8 | 51 | 86 | 0.00 | 1.00 | 0.00 |

Inside the trained range the ban on the end of text removes what would otherwise
have been the argmax on every single item, and the ban on the return instruction
never fires. The model wants to stop, is not allowed to, and then gets the answer
right. That is a direct measurement of the halting failure this condition was
built for, at a depth where accuracy alone would have shown nothing.

Past the trained depth the constraint keeps working and the model still fails.
Both bans fire heavily, the fraction of decodes that end by returning falls from
0.62 to 0.00 as depth rises, and the rest run out of token budget still writing.
None of the depth four and beyond plans parse. Forbidding an early halt turns
halting too early into not halting at all: the failure moves but does not go
away. Whether 8000 steps changes that is exactly what the sweep asks.

`obligation_tight_rate` is 1.000 and `mean_required` equals `mean_gold_steps` at
every sequential depth, so the constraint was as tight as it can be, not a weak
one flattered by a floor.

## Rung F, whether refinement does anything

`refinement_passes` is 3 everywhere. `assignment_changed_rate` is 0.00 at
sequential depth one and units, and 0.75 to 1.00 from depth two on, so the
assignment moves between passes exactly where the problem is not trivial.

`free_argmax_in_domain_rate` is 1.000 in every cell. The unrestricted argmax
already falls inside each field's own domain, so restricting the argmax to the
domain is doing nothing at all. The slot form's plans always parse, and its
errors are wrong values rather than malformed graphs.

## Two harness defects found and fixed during this run

A decoding budget that clipped one rung. The shared budget was 192 new tokens.
`scripts/vocab_budget.py` measures the longest gold plan each rung has to write
over the whole grid: english 109, symbolic 60, opcode 60, typed 144, goalstack
234. Rung E could not have finished a depth eight plan whatever it wrote. Every
one of its depth four to eight decodes ended either mid instruction at the cap
or with no return instruction. The budget is now 320 for every rung, and the
first smoke is kept at `results/ladder/pass1_budget192/` so the difference is on
the record. This is the same shape as the max_prompt_tokens filter that produced
a wrong conclusion on this project once before.

A gold plan written in one operator table and read back in another. Rungs B to F
name an operator by its slot, which is its index in `sorted(ops)`. `oracle_plan`
wrote the gold plan from the gold table and read it back against the table the
model induced. `scripts/vocab_slotcheck.py` measures how often those two tables
agree over 500 evaluation items: on the original page wording, 500 of 500; on the
paraphrase, 145 of 500 on the whole symbol set and 263 of 500 on the operators an
item's own plan uses. Rung A names the operator by the symbol the page uses and
was immune, so the artifact hit five rungs out of six and looked like those
representations failing on paraphrase. Written in the table it is read back with,
the mean of paraphrased `oracle_plan` over the eight sequential depths went from
0.85 to 1.000 for rung B, 0.66 to 0.81 for rung C and 0.58 to 0.65 for rung D,
against rung A's 0.97 either way. Those three rungs write gold plans that fit
inside 192 tokens, so the budget change cannot account for their movement. A
symbol the induction never produced now fails at encode time under the
`gold_encode` counter instead of silently becoming a different operator, which
is where rung A had been counting the same failure under `execute` all along.

## What is still not matched, stated rather than buried

Induction diverges across the rungs on the paraphrased wording, even though the
induction half of the training stream is byte identical and the original wording
gives all six rungs the same 288 of 288 pages and 408 exact operators. On the
paraphrase, pages parsed runs english 278, goalstack 286, typed 252, symbolic
241, opcode 240, slots 209, and behaviourally correct operators run english 209,
goalstack 235, typed 169, symbolic 166, slots 166, opcode 131. Training the plan
half in a different representation moves the shared parameters and changes what
the model reads off an unseen page. So a difference between rungs in
`plan_execute@para` is partly a difference in induction and not only in the plan.
The original harness scores `oracle_ops` on the original wording only, which
leaves this uncontrolled on the paraphrase. Adding `oracle_ops@para` to the full
sweep would separate the two, at the cost of one more condition per cell.

Tokens per example still differ by representation, as set out in VOCAB.md, and
rung E still receives an obligation count read off the question that the other
rungs do not get. Both are properties of the representations rather than
accidents of the harness, and both are left in and reported.

## Reproducing this

```
# no GPU
PYTHONPATH=$PWD uv run python scripts/vocab_selftest.py --n 25 \
  --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/ladder/selftest.json
PYTHONPATH=$PWD uv run python scripts/vocab_budget.py \
  --tokenizer /home/ec2-user/data/tokenizer_v2.json --n 6 --budget 320

# one GPU, about ninety minutes for all six rungs
STEPS=1500 BS=16 WORLDS=8000 N=8 MAXNEW=320 bash scripts/vocab_smoke.sh 5

# rescore checkpoints already on disk without training again
TRAIN=0 N=8 MAXNEW=320 bash scripts/vocab_smoke.sh 5

PYTHONPATH=$PWD uv run python scripts/vocab_across.py --tag greedy \
  --out results/ladder/REPORT_across_greedy.txt
```
