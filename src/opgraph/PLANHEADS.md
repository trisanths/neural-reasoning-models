# Plan heads

## What this varies

`oracle_plan` is flat at 1.000 through depth eight while `plan_execute` collapses
after depth three, and `plan_execute` equals `oracle_ops` to three decimals at
every depth. Conditional on a correct plan, the 350M substrate induces and
executes operators with no depth degradation that this grid can see, and gold
operators change nothing. The remaining failure is in plan construction.

These heads change how a plan is constructed and nothing else. Same base
checkpoint, same reader, same operator objects, same worlds and seeds, same
questions, same executor, same optimizer steps, same sequences per step, same
held-out sets.

| head | plan representation | how a plan is produced |
|---|---|---|
| P1 | plan text in the page's own operator symbols | one causal decode, pretrained `lm_head` |
| P2 | plan text in dedicated opcode tokens | one causal decode, pretrained `lm_head` |
| P2s | the fixed length slot array | committed left to right under a causal mask |
| P3 | the fixed length slot array | all MASK, then several bidirectional refinement passes |
| P4 | the graph slot array, with dependency edges | the same refinement, executed in topological order |

P1 is the existing `plan_execute` head and is the baseline. P2s is not in the
brief; it is here because P2 to P3 otherwise changes two things at once, the
alphabet and the generation geometry. P2s holds the alphabet at P3's and moves
only the geometry, so the difference between P2s and P3 is the refinement and
nothing else.

Everything is discrete. A slot holds one symbol from a small fixed set, so
accuracy is exact, an oracle can overwrite any slot, a counterfactual is one
substitution, and there is no continuous space large enough to hide an answer
in.

## The slot alphabet

Six field kinds. The kind of a slot fixes which symbols it may hold, and the
logits of a slot are restricted to its own field's window before every softmax
at training and at inference, so an out of field symbol is structurally
unreachable rather than merely unlikely.

| field | size | values |
|---|---|---|
| `active` | 3 | NO, YES, MASK |
| `opcode` | 13 | EMPTY, MASK, OP_1..OP_8, add, sub, mul |
| `register` | 14 | EMPTY, MASK, R_1..R_12 |
| `argument` | 272 | EMPTY, MASK, FALSE, TRUE, T_1..T_12, integers 0..255 |
| `dependency` | 14 | NONE, MASK, NODE_1..NODE_12 |
| `answer` | 272 | the argument alphabet |

Constants: 12 plan nodes, widest arity 7 (the `score` procedure takes a value
plus six flags), 8 induced operator symbols per world, integer literals below
256. The worlds define six operators and gold plans never pass 80, so the caps
are slack, and `scripts/planheads_codec_check.py` shows they are: 7800 of 7800
gold plans over the whole evaluation grid, both page wordings, survive a round
trip through every head's representation.

One global symbol id space of 588 symbols runs across all six fields, so the
head is one embedding table and one projection.

`OP_k` is the k-th operator of the world in the sorted order the signature line
already prints. It carries no semantics of its own; the binding from `OP_k` to
the page's written symbol is stated in the prompt.

## The two layouts

Flat, used by P2s and P3, is 12 nodes of `[opcode, arg_1..arg_7]` and then one
answer slot: 97 slots. Node *i* writes temporary `t(i+1)`, and an active node
may not follow an empty one, so the program is a prefix of the array and
execution order is array order.

Graph, used by P4, is 12 nodes of `[active, opcode, register, arg_1..arg_7,
dep_1, dep_2]` and then one answer slot: 145 slots. Active nodes may sit
anywhere in the array. Each carries its own output register and up to two
dependency edges, and the decoder runs them in topological order of those
edges.

The tie in the topological sort goes to the smallest ready node. Taking the
whole ready frontier at once would reorder an array that is already
topological, which would make an exactly correct P4 program serialise
differently from the identical P1 program and cost it the exact-gold-plan
diagnostic for nothing.

Nothing in the decoder repairs anything. A masked slot, an opcode past the end
of the operator table, a missing argument, an argument past the arity, a
dependency on an inactive node, two active nodes writing one register, and a
cycle in the edges all raise, and the caller records the failure instead of a
wrong answer. The dependency edges are not checked against the arguments: a
program whose edges disagree with its arguments serialises to a plan that reads
a temporary before it is written, and the strict plan parser every head meets
rejects it there.

## Prompts

P1 keeps exactly the prompt it was trained on:

```
<|world|> opgraph <|doc|> ops @/2/left #/2 <|q|> plan QUESTION <|a|>
```

The other four state the opcode binding, because they write a plan in opcodes
rather than in the page's written symbol:

```
<|world|> opgraph <|doc|> ops @=<|pg207|>/2/left #=<|pg208|>/2 ... <|q|> plan QUESTION <|a|>
```

The column adds no semantics. The symbol, the arity and the associativity are
the same facts P1 gets. It does cost tokens: 53 against 26 on a six operator
world, which is listed below under what is not matched.

The eleven opcode tokens come from the tokenizer's reserved block and are ids
207 to 217, verified single ids, so no embedding row is added and an operator
costs exactly one token. In the page's own symbols an operator costs one token
when it is a glyph and three when it is a word, which is the lexical difference
P2 isolates.

The slot region carries no token ids at all. Its inputs are the head's own
symbol, field and position embeddings, so nothing about the plan representation
leaks into the token vocabulary.

## The head module

The only new parameters in P2s, P3 and P4: a symbol embedding over the 588
symbol alphabet, a field kind embedding, a slot position embedding, and one
linear projection back to the alphabet. 1,359,872 parameters at `d_model` 1024,
against the backbone's 350M. P1 and P2 use the pretrained `lm_head` and add
nothing.

## Attention

The sequence is `[left padding][prompt][slots]`. The prompt region stays causal,
which is how the backbone was pretrained, and never reads a slot. The slot
region sees the whole prompt and, under P3 and P4, every slot including itself
and the ones after it. Under P2s the slot region stays causal, which is the
point of that arm.

`model.py` is not touched. `run_stack` inlines `Block.forward` and
`Attention.forward` with an explicit `attn_mask` in place of `is_causal`, which
is the same computation whenever the mask is the causal one.

The diagonal of the mask is forced open so a fully padded row still attends to
something. Without it such a row softmaxes to NaN and the NaN reaches every
later position through the key and value it writes.

## Training

One trainer, one schedule, five heads. Odd steps are an induction batch under
the text objective, identical for every head. Even steps are a plan batch. Both
pools are shuffled with the same seed for every head, so step *k* of one head
holds the same worlds and the same questions as step *k* of another.

P1 and P2 train the plan batch as text with the prompt masked out of the loss,
P2 on the opcode spelling of the same plan.

P2s trains the slot array teacher forced under the causal mask.

P3 and P4 train repair. A gold slot array is corrupted, the corrupted array is
the input, and the loss is cross entropy against the gold array over every
slot, including the slots that were not corrupted. The target is what
computation makes this partial program globally correct, not what symbol
follows this one.

### Corruption mixture

Uniform masking alone teaches what symbol goes in this hole. The other types
teach the question a refinement pass actually has to answer. The weights are a
design choice, so they are reported with every result and the counts actually
drawn are written into the run log beside the checkpoint.

| type | flat, P3 | graph, P4 | what it does |
|---|---|---|---|
| `all_mask` | 0.25 | 0.22 | the whole array to MASK, which is the inference time starting point |
| `random_mask` | 0.25 | 0.22 | a hole rate drawn per example in 0.10 to 1.0 |
| `transpose` | 0.10 | 0.09 | two active nodes swapped whole |
| `wrong_op` | 0.15 | 0.13 | one or two opcodes replaced by a different operator from the table |
| `truncate` | 0.15 | 0.13 | the tail of the program masked, answer slot masked |
| `sparse` | 0.10 | 0.08 | at most one node kept, the rest masked |
| `edge_noise` | n/a | 0.13 | a dependency edge dropped, misdirected, or masked |

On every type other than `all_mask`, an extra uniform hole rate drawn in 0.0 to
0.30 is applied on top, so the head meets mixtures rather than pure types.

`all_mask` is in the mixture because the inference time starting point has to be
a corruption the head was trained on.

### Holdout

Identical for all five heads, asserted over the whole plan pool before the first
optimizer step rather than described. No training plan is deeper than three
steps and no training plan uses two distinct induced operator symbols. The
depth histogram and the worst distinct symbol count are printed and written into
the run log. Everything past depth three, and all of novel composition, is
extrapolation equally for every head.

### Sequences that do not fit

A sequence over `max_len` is counted, not dropped in silence. The slot heads
raise on a prompt that does not fit; a text head that quietly dropped one would
take a smaller step on the same nominal batch size and the arms would stop being
matched on sequences per step without saying so. The counts go to stdout and
into the run log.

## Inference

P1 and P2 decode causally through the repo's key and value cached sampler until
the model writes end of text or hits the token cap of 160, then the text is
parsed by the strict plan parser. P2's opcodes are mapped back to the page's
symbols first; an opcode past the end of the table stays as its raw token and
the parser rejects it, which is the intended outcome and not a repair.

P2s starts from an all MASK array and commits slot *j* at pass *j* under the
causal mask, 97 or 145 passes for one plan.

P3 and P4 start from an all MASK array and run a fixed number of bidirectional
passes, 8 by default. Each pass re-predicts every slot from every other slot.
At pass *t* of *T* the `round(S(t+1)/T)` most confident predictions are kept and
every other slot is reset to MASK, so a slot committed early can be dropped and
rewritten later; the last pass commits what is left. The order of resolution is
free and is chosen by confidence, not by position.

Greedy and sampled decoding are both run, at temperature 0.0 and 0.8. Greedy has
produced false zeros on this project, so a greedy zero is never reported alone.

## Compute accounting

P3 and P4 spend several forward passes constructing one plan while P1 and P2
spend one per token. Without counting that, a win by P3 cannot be told apart
from a win by spending more compute, and the second is a much weaker claim.

Three numbers are reported with every cell.

`fwd_passes` is stack invocations. For P1 and P2 it is the prompt pass plus one
per token that item generated before its own end of text. For P2s it is the slot
count. For P3 and P4 it is the iteration count, independent of the plan's
length.

`slot_decisions` is discrete symbols committed, refinements included. For P1 and
P2 it is tokens generated. For P2s it is the slot count. For P3 and P4 it is
iterations times slots, because every pass re-predicts every slot.

`position_evals` is positions whose hidden states were newly computed. For P1
and P2 it is the prompt width plus the tokens generated, since the cached
decoder computes one new position per step. For the slot heads it is the prompt
width plus slots times passes: the prompt region is causal and never reads a
slot, so its states are identical on every pass and are charged once. This is
the inherent cost. The current slot implementation recomputes the prompt every
pass, so its wall clock is higher than the number.

`fwd_passes` is checked against the model rather than against the bookkeeping
that produced it. `ForwardCounter` hooks `model.tok_emb`, which every path
through the backbone touches exactly once per stack invocation, including the
cached decoder that inlines the blocks rather than calling them. The evaluation
runs one plan at batch one under the hook and reports reported against observed.

## What is reported

Accuracy, and the plan level diagnostics kept separate from it and never folded
into it: parse rate, well typed rate, exact gold plan rate, and the rate at
which a plan that parses still gives a wrong answer. Every cell reports its
denominator. Relational breadth is on the grid for every head; the registered
prediction is that breadth does not move, because it fails at induction, and a
moved breadth falsifies the current localisation and matters more than a
confirmed prediction.

`oracle_both` must be 1.000 under every head or the harness is broken.
`oracle_both_roundtrip` pushes the same gold plan through that head's own
representation and back before executing it, and must also be 1.000. It is the
stronger check: it fails if a head's codec cannot express a plan the executor
would have answered, which is a way an arm could be quietly capped.

## What is not matched

Both of these are real and neither is hidden.

The four opcode heads carry the binding column in the prompt, 53 tokens against
P1's 26 on a six operator world. P1 does not need it because it writes the
page's own symbol.

P2s, P3 and P4 carry a freshly initialised 1.36M parameter head where P1 and P2
reuse the pretrained `lm_head`. The slot alphabet has no pretrained embedding to
reuse, so this cannot be removed; it can only be stated.

Two further differences are the thing being varied rather than a confound, but
they are worth naming. P1 and P2 have to get the plan's length right and the
slot heads are handed a fixed length array. P2s trains teacher forced while P3
and P4 train on the corruption mixture.

## Files

| path | what it holds |
|---|---|
| `src/opgraph/planheads.py` | schema, codec, corruption, head module, masked trunk, forward counter, planners, diagnostics |
| `src/opgraph/tests/test_planheads.py` | codec round trip, field containment, rejection cases, mask geometry, corruption coverage |
| `scripts/planheads_train.py` | one trainer for all five heads |
| `scripts/planheads_eval.py` | every condition, kind and depth, both temperatures, with the compute |
| `scripts/planheads_codec_check.py` | can each head's representation hold every plan the sweep will ask for |
| `scripts/planheads_smoke.sh` | the tiny end to end run |
| `scripts/planheads_smoke_report.py` | the smoke condensed to what it is allowed to establish |
| `scripts/planheads_micro.sh` | a four step per head version of the smoke, for catching a broken path fast |

## Running one head

```
cd ~/opg && export PYTHONPATH=$PWD
CUDA_VISIBLE_DEVICES=7 uv run python scripts/planheads_train.py \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --head p3 --out runs/p3.pt --steps 8000 --batch-size 32 --worlds 40000
CUDA_VISIBLE_DEVICES=7 uv run python scripts/planheads_eval.py \
  --ckpt runs/p3.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/p3.json --n 150 --styles 0,1 --temperatures 0.0,0.8 \
  --iters 4,8,16 --verify-counter
```

`--iters` takes a list for P3 and P4 and is ignored elsewhere, which is how the
refinement budget is separated from the refinement.
