# The plan-representation ladder

## What this varies, and what it holds still

The operator-graph result localises the composition failure. With the plan
supplied and operator induction still the model's own job, sequential accuracy
is flat at 1.000 from depth one to depth eight. With the model writing the plan
it falls to 0.013. Gold operators change nothing: plan_execute and oracle_ops
agree to three decimals at every depth. So the executor chains an induced
operator to depth eight without loss, and the loss is in emitting the plan.

This ladder changes the plan and nothing else. The worlds, the seeds, the pages,
the questions, the operator objects, `run_plan`, the held-out sets and the
induction half of the training stream are the same objects the original arms
used, imported rather than rebuilt.

Every rung is a fine tune from `ckpt/base350.pt` for the same number of
optimizer steps at the same batch size in sequences, over the same world seeds
in the same shuffled order. Each rung's training stream is eight examples per
world: four induction examples, byte-identical across all six rungs and
identical to the opgraph arm's, and four plan examples in that rung's
representation.

Training never shows a plan past depth three and never shows a plan using two
distinct operator symbols. Depths four and beyond, and all of novel composition,
are extrapolation for every rung equally.

## Where the rungs are not matched, stated rather than buried

Three axes cannot be held equal, because they are the representation.

Tokens per example. A plan written as sentences is longer than the same plan
written as opcodes, and the slot graph is longer than either. Measured over the
whole stream at 60 worlds: english 138, symbolic 143, opcode 139, typed 164,
goalstack 177, slots 352 tokens per example. Supervised tokens per example:
english 41, symbolic 35, opcode 35, typed 45, goalstack 45, slots 156. What is
matched is optimizer steps and batch size in sequences, so the slot rung sees
roughly two and a half times the tokens per step. The asymmetry favours the
later rungs and is left in, the same way the original experiment left the direct
arm's token advantage in.

Embeddings. Rungs C to F put dedicated tokens in the model's mouth and re-draw
those rows of the input and output embeddings from N(0, 0.02), the model's own
initialisation, before fine tuning. Rungs A and B touch no reserved token. The
rows live in the tokenizer's existing 256 reserved `<|pgN|>` slots, so no rung
resizes anything and every rung has exactly the same parameter count. The rows
re-drawn are 12 for opcode, 44 for typed, 146 for goalstack and 151 for slots.

Information at decode time. Rung E receives an obligation count read off the
question's surface, which the other rungs do not get. This is set out in full
under rung E below, because it is the one place where a rung is handed something
the others are not, and a reader who misses it will over-read E's numbers.

## The reserved token block

167 logical tokens are mapped onto `<|pg0|>` through `<|pg166|>` in a fixed
order, so the mapping is stable across runs and checkpoints:

| block | count | names |
|---|---|---|
| operator slots | 12 | `op0` to `op11` |
| registers and slot references | 16 | `r0` to `r15` |
| small integer literals | 100 | `n0` to `n99` |
| arity | 7 | `a1` to `a7` |
| types | 3 | `tint`, `tbool`, `tstr` |
| instruction words | 6 | `apply`, `ret`, `to`, `end`, `goal`, `sep` |
| slot graph words | 5 | `nop`, `none`, `mask`, `row`, `retf` |
| booleans | 2 | `vtrue`, `vfalse` |
| slot identifiers | 16 | `s0` to `s15` |

Each is a single token that survives encode and decode exactly, including when
two of them abut with no space. `scripts/vocab_selftest.py` checks this.

An operator's slot is its index in `sorted(ops)`, the same order the signature
line is written in, so the prompt and the plan agree on what `op0` names without
either of them having to say so twice. The symbol is fixed across episodes and
its meaning is bound per episode by the page it was induced from.

## The six rungs

Throughout, `@` is an invented binary operator from a page, and the question is
`Evaluate 7 @ 4 @ 9.` with the page stating left association, whose gold plan is
`t1 = @ 7 4 ; t2 = @ t1 9 ; ans t2`.

### A, english

The plan prompt carries the original signature line, `@/2/left #/2/right ...`,
unchanged from the opgraph arm. Operators are named by the symbol the page uses.

```
first apply @ to 7 and 4, giving result one ;
then apply @ to result one and 9, giving result two ;
the answer is result two
```

Arguments are integers, `true`, `false`, or `result <ordinal>` for ordinals one
through thirty two. Several arguments are joined with commas and a final `and`,
so a breadth six question reads `apply score to 40, true, false, true, false,
true and false`. Results must be numbered in order, and the answer sentence must
come last. This is the rung the ladder is measured against: it is the closest to
prose the model already writes.

### B, symbolic in existing vocabulary

The signature line becomes `op0=@/2/left op1=#/2/right ...`, so the slot binding
is declared in ordinary text.

```
A = op0 7 4 > B = op0 A 9 > ans B
```

Registers are single letters, `A` to `Z` then `a` to `f`. Operators are named by
slot rather than by glyph, so the invented character never appears in the plan.
No reserved token is used and no embedding is re-drawn.

### C, static opcode tokens

Grammatically identical to B. The signature line becomes `<op0> @/2/left <op1>
#/2/right ...` and the plan writes the slot as a dedicated token:

```
A = <op0> 7 4 > B = <op0> A 9 > ans B
```

B and C differ in exactly one thing, whether the operator slot is spelled in
ordinary vocabulary or as a fresh embedding, which is what separates compactness
from newness. Registers stay ordinary letters in both.

### D, typed opcodes with registers

The signature line carries the full type signature:
`<op0> @ <a2> <tint> <tint> <tint> left`, that is, slot, symbol, arity, one type
per parameter, result type, and the association the page states.

```
<apply> <op0> <a2> <tint> 7 4 <to> <r0> <end>
<apply> <op0> <a2> <tint> <r0> 9 <to> <r1> <end>
<ret> <tint> <r1> <end>
```

Each instruction declares its arity and its result type before its operands, so
a malformed plan is detectable before it is executed rather than by executing it
and seeing what happens. Types are `int`, `bool` and `str`, inferred from the
operator body: a parameter tested as a condition is boolean, a parameter
compared against a string literal is a string, everything else is an integer;
the result type follows the head of the body. That inference reproduces the
right signature for every operator these pages define, checked over the whole
grid, and it degrades to `int` on anything an induction invents that it does
not.

Two checks come out of the declarations. `well_typed` asks whether arities and
operand types agree with the operator table, and is computed identically for
every rung from the decoded plan, so the number means the same thing across the
ladder. `declarations_agree` asks whether the plan's own declared arities and
types match what the operator table says, and exists only for D and E because
only they declare anything.

### E, D plus an externally enforced goal stack

The surface form is D's. What differs is that an obligation state is maintained
outside the model, written into the sequence at every instruction boundary, and
enforced on the sampler.

The state is three obligations:

| obligation | closed when |
|---|---|
| applications | at least as many applies emitted as the question names operators |
| literals | every integer written in the question has been used as an operand |
| dangling | exactly one register is live, so no produced value is left unread |

Written into the sequence as `<goal> <n_pending> <n_unused> <n_live> <sep>`
before each instruction. Those tokens are never supervised: the decoder computes
and writes them, the model only reads them. Training and decoding therefore see
the same sequence.

Enforcement is a hard mask on the sampler. While any obligation is open, the
logits of `<ret>` and `<|eot|>` are set to negative infinity, so termination is
not a token the model may choose. How often that mask removed what would
otherwise have been the argmax is reported per cell as
`constraint_bound_rate` and `constraint_bind_events`.

The application count is read off the question by counting occurrences of the
single-character operator glyphs in the operator table the model is given, with
a floor of one. Only glyphs are counted. Worded operator symbols are not,
because a page's flag words and unit names are drawn from the same syllable pool
and can collide, and an over-count would make the obligation unsatisfiable and
stall the decoder against its step cap; under-counting only weakens the
constraint, so the rule errs that way deliberately. Measured over 50 items per
cell, the count equals the gold plan length exactly for sequential, parenthesised
sequential, novel, breadth and units, and under-counts for `same_page_pair`,
where the question names no glyph but needs two steps.

What E is handed, and what it is not. It is handed how many operators the
question mentions and which integers it mentions. For the sequential family that
count equals the depth, which is a real informational advantage over rungs A to
D and must be read that way. It is not handed the tree shape, the grouping of
operands, the order of steps, the association the page states, or the answer.
Its ceiling is still oracle_plan.

Because the count is read through the operator table, a failed induction leaves
the glyph unrecognised and the obligation collapses to its floor of one. That is
honest, since no gold information is available at that point, but it means E's
constraint is only as tight as its induction. `obligation_tight_rate`,
`mean_required` and `mean_gold_steps` are reported per cell so a weak constraint
is never mistaken for a strong one. When an instruction comes back unparseable
the state can no longer be tracked and the constraint is released for that item
rather than left to stall; `constraint_released_rate` reports how often.

### F, non-autoregressive plan over graph slots

Sixteen slots, each one opcode field and seven argument fields, then one return
field: 129 fields in all. Step k of the plan lands in slot k. An argument that
reads step j is written `<rj>`, which is the data-dependency edge. Unused slots
are `<nop>` with `<none>` arguments. Integer operands are the dedicated literal
tokens `<n0>` to `<n99>`, which is what makes the field width fixed; every
operand these worlds generate is under 100.

A field is a categorical variable over its own domain, and the argmax is taken
inside that domain. `free_argmax_in_domain_rate` reports how often the
unrestricted argmax already fell in the domain, so it is visible how much the
restriction is doing.

Refinement is done as repeated rows in one sequence rather than by changing the
attention mask. The sequence is the prompt followed by R rows, each
`<row> <s0> f f f f f f f f <s1> ... <retf> f`, 147 tokens. Row 1 is entirely
`<mask>`, so every field in it is predicted in parallel from the prompt alone
with no output feeding another output. Row r holds the fields committed so far
and `<mask>` elsewhere, and its predictions see all of row r-1, which is where
the bidirectional information comes from. In training, row r has a random
`(r-1)/R` of its fields filled with gold and loss is taken only on the masked
positions. At decode time, after each pass the most confident predictions are
committed until `r/R` of the fields are fixed, and the last pass commits
everything. R defaults to 3 and is reported as `refinement_passes`;
`assignment_changed_rate` reports whether the assignment moved between passes,
which is what says whether refining did anything.

The decoded assignment is read as a graph: active slots, edges from their
register references, a topological sort, then the existing executor. A reference
to an inactive slot, a gap in a slot's arguments, or a cycle is a parse failure,
not a guess.

## Reading a rung

Four conditions per rung, the same four the original experiment used.

| condition | induction | composition |
|---|---|---|
| plan_execute | model | model |
| oracle_plan | model | gold, written in this representation and read back |
| oracle_ops | gold | model |
| oracle_both | gold | gold, written in this representation and read back |

`oracle_both` must come out at 1.000. Because the gold plan is put through the
representation and read back before being executed, a lossy encoding shows up
there rather than as a quiet loss elsewhere. `oracle_plan` should be the same
number for every rung, since the plan is gold in all of them, and a rung where
it is not has a round-trip problem.

Per cell, alongside accuracy: `n`, `plan_parses`, `well_typed`,
`exact_gold_plan`, `parsed_but_wrong`, and the reason counter. The gap between
`plan_parses` and `acc` is where the remaining failure sits.

Both page wordings are run. Gold operators do not depend on the wording, so
oracle_ops and oracle_both are scored on the original wording only, exactly as
the original harness did. Greedy and sampled decoding are both available through
`--temperature` and both should be reported: a greedy decode has produced false
zeros on this project before, where the behaviour was present but not the
argmax.

The registered prediction is that this ladder moves sequential depth and novel
composition and does not move relational breadth, where the bottleneck is the
opposite one: oracle_plan collapses at breadth four and above while oracle_both
holds at 1.000, so what fails there is inducing a wide operator, which no plan
vocabulary can repair. Breadth is therefore reported for every rung so that stays
checkable.

## Files and commands

| file | what it holds |
|---|---|
| `src/opgraph/vocab.py` | the six representations, the type inference, the obligation state, the slot layout, the fresh-embedding draw |
| `src/opgraph/ladder_run.py` | the token-level generator, the goal-stack hook, the mask-predict slot decoder, the cell scorer |
| `scripts/vocab_selftest.py` | round trip, obligation satisfiability, typing and tokenizer checks over the whole grid, on CPU |
| `scripts/vocab_eval.py` | the four conditions for one rung, both wordings |
| `scripts/vocab_smoke.sh` | train and score every rung at tiny scale |
| `scripts/opgraph_train.py` | the shared trainer, with six arms added |

```
# checks that need no GPU and should pass before anything is trained
PYTHONPATH=$PWD uv run python scripts/vocab_selftest.py --n 25 \
  --tokenizer /home/ec2-user/data/tokenizer_v2.json --out results/ladder/selftest.json

# one rung
PYTHONPATH=$PWD CUDA_VISIBLE_DEVICES=5 uv run python scripts/opgraph_train.py \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --arm ladder_typed --out runs/ladder/ladder_typed.pt \
  --steps 8000 --batch-size 32 --lr 2e-5 --warmup 200 --worlds 40000

PYTHONPATH=$PWD CUDA_VISIBLE_DEVICES=5 uv run python scripts/vocab_eval.py \
  --ckpt runs/ladder/ladder_typed.pt \
  --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/ladder/typed_greedy.json --n 150 --temperature 0.0
```

The full sweep uses the original arms' settings, `--steps 8000 --batch-size 32
--lr 2e-5 --warmup 200 --worlds 40000`, so a rung is directly comparable to the
plan_execute and oracle_plan numbers already on record.
