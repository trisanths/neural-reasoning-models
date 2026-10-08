# Reasoning that never passes through the vocabulary

## What is being tested

Every condition in the composition experiment that dies near depth four passes
its reasoning state through the vocabulary between steps: hidden state,
projection to logits, selection of one symbol, re-embedding. The only condition
that runs flat to depth eight, oracle_plan, never constructs the composition
through that channel, and it is handed a gold plan.

These two conditions remove the symbol from between the steps while leaving
everything else where it was. A step's output hidden state becomes the next
step's input embedding. Nothing is projected, nothing is selected, nothing is
re-embedded.

* **Condition D, `latent_answer`.** R latent steps, then the answer. Nothing
  external runs. Whatever answers has to come out of the continuous state.
* **Condition E, `latent_plan`.** The same latent core, but the state emits an
  opcode plan and the existing executor runs it. This separates "latent
  computation produces the answer" from "latent computation produces a plan
  that something else executes".

R is a runtime parameter in both. The same weights answer at R = 0 and at
R = 64 with nothing rebuilt, which is what makes R a compute axis rather than
an architecture choice.

## The sequence

Condition D's prompt is the `direct` arm's prompt with its closing `<|a|>`
replaced by `<|result|>`. Condition E's is the `opgraph` arm's plan prompt with
the same substitution. Then the latent segment, then `<|a|>`, then the target.

```
<|world|> opgraph <|doc|> page ... <|q|> question <|result|> [L1 L2 ... LR] <|a|> ans 51 <|eot|>
<|world|> opgraph <|doc|> ops @/2/left #/2 <|q|> plan question <|result|> [L1 ... LR] <|a|> t1 = @ 7 4 ; ans t1 <|eot|>
```

`L1..LR` are positions whose input embedding is a vector, not a token. The id
tensor holds `<|pg0|>`, a reserved procgen slot, so the tensor has a shape; that
embedding is never read. A slot that is not yet filled is dropped from the
sequence entirely, and a slot that is filled has its embedding overwritten.

The `<|a|>` that closes the latent segment is written by the scaffold at
inference rather than predicted, so nothing is ever trained to predict it.

## Where the vector comes from

`src/latent/core.py`.

`trunk_from_embeds(model, x, loops)` is `model.trunk` entered at the embeddings
instead of at the token ids. It runs the model's own blocks, and under a
recurrent config it calls the model's weight tied core, so the per iteration
FiLM conditioning and the loop count override belong to `src/train/model.py`
and are not copies. A test pins `trunk_from_embeds(m, m.tok_emb(ids))` to
`m.trunk(ids)` by exact equality, with and without recurrence.

`LatentHead(d_model, slots, proj, scale)` turns a hidden state into the next
input embedding:

```
z = h                       (proj="none")  or  W z  (proj="linear", identity init)
z = z * scale
z = z * (1 + film_scale[r]) + film_shift[r]
```

`scale` is measured once from the checkpoint as the ratio between the embedding
table's RMS and the trunk output's RMS, on a batch of real prompts. On
`ckpt/base350.pt` it comes out at 0.0123: a trunk output injected at its own
magnitude sits eighty times away from any embedding the backbone has ever read,
and the first part of training would go on undoing that.

`film` is one zero initialised scale and shift per latent step, the same
conditioning the looped core applies per iteration. Zero means an untrained
head is the identity, so step one is exactly the state the trunk produced.
Steps past the last slot reuse the last row, the same convention as
`loop_slots`. With `proj="none"` the head adds `2 * slots * d_model` parameters
and nothing else: 8192 at slots=4 on a 375M backbone, 0.002 percent.

`with_depth_recurrence(model, prelude, core, coda, loops)` reinterprets the
plain 24 layer checkpoint as a prelude, a weight tied core and a coda, which is
how a latent step is given extra depth through `src/train/model.py`'s own loop
rather than through a second recurrent core written here. It is off by default,
because it changes what the base network computes and the run would then be
matched to the token channel arms on the checkpoint file and nothing else. The
cached decoder raises `NotImplementedError` on a recurrent model rather than
running `model.blocks` once and returning a quietly wrong number.

## The training chain

`src/latent/chain.py`. One optimizer step is R + 1 forward passes. Pass r
carries r filled latent positions and no placeholders. It does two things: it
produces the vector pass r + 1 injects, and it gives the loss of answering
after exactly r latent steps.

Each pass is built at its own length rather than by masking a fixed length. If
the unfilled slots stayed in the sequence the answer positions would attend to
placeholder tokens, and the loss at pass r would be the loss of answering after
r latent steps with R - r blanks in the way. Dropping the tail slots shifts
everything after them down by R - r; rotary position embeddings are relative,
so that shift is correct rather than a compromise, and it puts the answer where
it sits at inference. Every row loses the same number of positions, so the
compressed batch stays rectangular even though the prompt length differs per
row. `compress_index` does this and is tested at both endpoints and in the
middle.

Only the target span is projected to the vocabulary. The arms project every
position and let IGNORE mask it; running R + 1 passes that way would spend most
of the step on states nothing reads. A test pins the R=0 chain loss to the
arms' own `model(ids[:, :-1], labels[:, 1:])` loss.

`--backprop-last-k k` runs all but the last k passes under `no_grad`, the same
truncation `model.recurrent.backprop_last_k` applies to loop iterations. The
head still gets gradients at every step index, because the head is applied
outside the `no_grad` block; what is lost is the gradient through the trunk of
the earlier passes.

## What the loss asks, and what it does not

Labels are IGNORE at every latent position and at the `<|a|>` that closes the
segment. No loss anywhere asks the continuous state to reconstruct a deleted
written step. The state only has to support the reasoning that follows, which
is the point: it is free to hold something the vocabulary cannot express
compactly, several live alternatives included.

`collate` refuses a batch whose supervised positions fall inside the latent
segment, so a future change that quietly starts supervising a latent position
fails loudly instead of turning the condition into a reconstruction task.

## Curricula

Both are off by default. The registered order is to try without one first,
because "latent recurrence does not work" and "latent recurrence did not train"
are different findings.

**`stage`**, condition D only. The Coconut style replacement schedule. At stage
k the first k written trace chunks are gone from the target and
`k * latents_per_step` latent positions stand in their place. Stage 0 is the
`trace` arm exactly. The chunks that remain are still written out, so what
moves across the schedule is how much of the reasoning has left the token
channel, not what the loss asks of the latent state. `--stage-mix p` draws a
uniformly earlier stage for a batch with probability p, so the earlier stages
are not forgotten. The stage is drawn per batch, not per example, because a
batch has to be homogeneous in the number of latent positions.

**`ramp`**, either condition. The latent segment grows from zero to R and the
target never changes. Condition E uses this rather than `stage`: its prompt
carries an operator signature line and no pages, so between reading the
question and writing the plan there is no written intermediate content for a
replacement schedule to replace.

`--r-sampling lo,hi` draws R per optimizer step, which is the same idea as
`model.recurrent.train_loop_sampling`: train the model to be correct at any
depth so the runtime dial has something to dial.

## Halting

`--halting ponder` puts `src/latentret/gate.py`'s `RetrievalGate` on the state
each pass produces, reads the halt logit, and builds the halting distribution
with `halting_distribution`. The objective becomes PonderNet's: the expectation
of the per pass losses under that distribution, plus `ponder_kl` against a
truncated geometric prior so the gate cannot halt at pass zero before anything
downstream has trained. Because every pass already computes states at every
position, the per step losses cost one extra projection over the supervised
span and no extra forward pass. Default off, and R fixed.

## Compute accounting

Nothing here is reported without it.

At inference, `DecodeCost` splits forward passes and wall clock into prompt,
reasoning and decode. A latent step is one forward pass at one new position
with the key value cache, which is the same shape as one decoded token, so R
latent steps cost about what R written tokens cost. `reason_layer_apps` is
positions times `cfg.effective_depth()`, so a looped core is priced at what it
runs rather than at the layers it stores.

`src/latent/bench.py` measures the per step cost directly, at batch one where
latency is the story and at a batch where throughput is. It needs no trained
checkpoint.

At training, every log line carries forward passes and token positions to date,
and the peak allocated memory. A step costs R + 1 passes rather than one. The
arms are matched on optimizer steps and batch size in sequences, not on
training FLOPs, and that asymmetry favours the latent conditions. It has to be
stated with any result, not derived from the logs later by someone else.

## What is matched to the arms, and what is not

Matched: base checkpoint (`ckpt/base350.pt`), worlds, seeds, the four questions
per world, the page subset draw per question, optimizer and schedule shape, and
the held out eval seed ranges, which come from `src.opgraph.data.eval_items`
untouched. A test asserts that `training_episodes(seed)` reproduces
`src.opgraph.data.training_examples(seed, "direct")` prompt for prompt and gold
for gold, so the stream cannot drift without failing.

Not matched, and to be reported with every number:

1. **Parameters.** The latent head adds `2 * slots * d_model`, and with
   `proj=linear` another `d_model^2`. Printed at startup, stored in the
   checkpoint, and carried into the eval JSON.
2. **Training compute.** R + 1 forward passes per optimizer step.
3. **Peak memory.** Condition D at batch 8, max_len 1024, R=4 peaks at 34 GiB,
   because the four page prompts are long and five passes of activations are
   live at once. The arms run at batch 32. Reaching batch 32 needs
   `--backprop-last-k` or a cached training pass, and the smoke below runs at
   batch 4 rather than pretending otherwise.

## Grading

Condition D's target is written `ans VALUE`, the same closing chunk the `trace`
arm writes, and it is read back by `src.opgraph.plan.trace_answer` and compared
with `src.opgraph.run._norm`, so D and `trace` are graded by the same code.
Condition E is parsed with `parse_plan` and run with `run_plan`, so a plan that
does not parse and a plan that runs to the wrong value are separated rather
than pooled; the per cell `reasons` tally carries that split.

`fit_decay` reports the log linear slope of the depth curve, the per depth
decay factor, the half life, and the first depth below each of 0.5, 0.25 and
0.1. The slope and the crossing depth are always emitted together, because a
cliff that moved and a curve that went flat are different claims about the
architecture and reporting one as the other would be the most damaging error
available here.

Relational breadth is scored for every condition at every R and printed in the
same table. The registered prediction is that breadth does not move.

## Attacking the number before reporting it

`src/latent/check.py` regenerates the same items three ways at each R: with the
trained head, with the injected vector replaced by zeros, and with each example
given another example's vector. If live and zeroed agree, nothing is being read
out of the state. If live and shuffled agree, what is read carries nothing
about this example. Either one makes an accuracy difference at larger R
impossible to attribute, and it is worth knowing before a sweep.

## Files

| file | what it holds |
|---|---|
| `core.py` | `trunk_from_embeds`, `LatentHead`, `measure_scale`, `with_depth_recurrence`, and the index and scatter helpers |
| `data.py` | prompts, the stream that mirrors the arms', the two curricula, encoding and collation |
| `chain.py` | the R + 1 pass chain, the span loss, the PonderNet objective, `ChainCost` |
| `infer.py` | `LatentPolicy`, the cached decoder that can advance on a vector, a full recompute reference, and `DecodeCost` |
| `train.py` | one arm, end to end |
| `eval.py` | the scored cells, the decay fit, the CLI |
| `bench.py` | what a latent step costs in milliseconds |
| `check.py` | zeroed and shuffled controls on the injected vector |
| `smoke.sh`, `smoke2.sh` | the smoke lanes |
| `tests/test_latent.py` | 28 tests, all CPU |

Nothing in `src/opgraph/` is modified. The worlds, operators, executor and
evaluation harness are imported.

## The smoke run

Tiny scale on purpose. 800 optimizer steps against the arms' 8000, batch 4 or 8
against the arms' 32, 4000 worlds against 40000. Nothing here is a result about
latent reasoning. It shows the code trains, the harness scores it, and the
counters are right.

Artifacts, all on the training box under `/home/ec2-user/opg`:

| what | path |
|---|---|
| condition D, no curriculum | `runs/latent/answer_nocur.pt{,.log.json}`, `results/latent/answer_nocur.json` |
| condition D, stage curriculum | `runs/latent/answer_stage.pt{,.log.json}`, `results/latent/answer_stage.json` |
| condition E, no curriculum | `runs/latent/plan_nocur.pt{,.log.json}`, `results/latent/plan_nocur.json` |
| latent step cost | `results/latent/bench.json` |
| injection controls | `results/latent/check_answer.json`, `results/latent/check_plan.json` |
| memory probe | `logs/latent_mem.log` |

### Both conditions train without a curriculum

Training loss, first logged step to last:

| run | steps | batch | R | loss 1 | loss 800 |
|---|---|---|---|---|---|
| `answer_nocur` | 800 | 4 | 4 | 7.26 | 1.06 |
| `plan_nocur` | 800 | 8 | 4 | 4.00 | 0.00 to 0.02 |
| `answer_stage` | 800 | 4 | 0 to 6 | 5.08 | 0.50 at R=0, 1.27 at R=6 |

So the answer is that latent recurrence trains here with the loss on the answer
alone and no curriculum. A curriculum was still run, and its signature is
visible: the loss jumps at each stage boundary (0.55 at two latent positions,
0.75 at four, 2.41 at six) and comes back down inside the stage. At R=0 the
staged model still writes a full trace, `t1 = / 11 3 -> 16 ; ans 16`, and at
R=6 it writes `ans 9`, so the replacement schedule did move the reasoning out
of the token channel.

### The latent segment is not yet carrying anything

This is the finding that matters, and it is the reason `check.py` exists.

`results/latent/check_plan.json`, `results/latent/check_answer.json`, n=24,
fraction of items whose greedy text changes:

| run | R | vs R=0 | vs zeroed vector | vs another example's vector |
|---|---|---|---|---|
| `plan_nocur` | 2 | 0.042 | 0.000 | 0.000 |
| `plan_nocur` | 4 | 0.292 | 0.042 | 0.000 |
| `plan_nocur` | 8 | 0.083 | 0.000 | 0.000 |
| `answer_nocur` | 2 | 0.000 | 0.042 | 0.000 |
| `answer_nocur` | 4 | 0.042 | 0.042 | 0.042 |
| `answer_nocur` | 8 | 0.042 | 0.042 | 0.083 |

Replacing the injected vector with zeros changes at most one output in
twenty four. Giving an example another example's vector changes at most two.
After 800 steps neither condition reads anything out of the latent state, and
the greedy scores are consequently identical at R=0, 2, 4 and 8 for both
conditions. The sampled scores do move, so the injection reaches the logits; it
just never moves an argmax.

Condition E's depth curve at this scale, 1.000, 0.417, 0.458, 0.042, 0.000,
0.000 at depths 1, 2, 3, 4, 5, 8, sits close to the published `plan_execute`
arm's 1.000, 0.480, 0.500, 0.020, 0.033, 0.013. That similarity is not evidence
that latent reasoning works. Since R=0 scores the same, the whole curve is the
prompt, and the R latent steps are being paid for and not used.

### Relational breadth did not move

Registered prediction, confirmed, n=24 per cell.

| condition | b=1 | b=2 | b=3 | b=4 | b=5 |
|---|---|---|---|---|---|
| `plan_nocur`, every R in {0,2,4,8} | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 |
| `answer_nocur`, every R in {0,2,4,8} | 0.542 | 0.167 | 0.167 | 0.083 | 0.125 |
| `answer_stage`, every R in {0,2,4,6,8} | 0.583 | 0.167 | 0.125 to 0.167 | 0.042 to 0.083 | 0.125 |

Condition E is exactly the arms' breadth pattern: perfect through b=3, zero at
b>=4, and the `reasons` tally at b>=4 is `execute` for all 24, which is the
plan calling an operator at the arity training showed rather than the arity the
question needs. No R moves it.

### What a latent step costs

`results/latent/bench.json`, `ckpt/base350.pt`, prompt 600 tokens, 16 decoded
tokens, median of three.

| batch | ms per latent step | ms per decoded token | ms per example at R=0 | at R=64 |
|---|---|---|---|---|
| 1 | 24.8 | 24.8 | 407 | 2032 |
| 16 | 24.5 | 24.7 | 27.4 | 125 (extrapolated) |

Two numbers to keep. A latent step costs the same as a decoded token, because
it is the same shape of work: one forward pass at one new position. And the
per step cost is the same at batch 1 and batch 16, which is the optimization
lab's result restated: this is memory and overhead bound, sixteen times the
arithmetic for the same wall clock. R=64 is a 4x latency increase at batch 1
and a 4.6x increase in per example time at batch 16. A latent condition beats a
written trace on wall clock only when it needs fewer steps than the trace needs
tokens, and the smoke already shows that trade in miniature: `answer_stage`
spends 15 to 36 decode passes per example at R=0 writing the trace, against 4
to 5 decode passes plus 6 latent passes at R=6.

### Peak memory, which constrains the sweep

Condition D, max_len 1024, single H100, `logs/latent_mem.log`:

| batch | R | backprop_last_k | peak |
|---|---|---|---|
| 32 | 4 | none | out of memory above 79 GiB |
| 32 | 4 | 2 | 59.2 GiB |
| 32 | 4 | 1 | 32.9 GiB |
| 16 | 4 | none | 73.3 GiB |
| 8 | 8 | 2 | 19.4 GiB |

Condition D cannot be run at the arms' batch of 32 with full backpropagation
through the latent chain. The sweep has to choose `--backprop-last-k`, which is
a real difference from the token channel arms and belongs in the writeup rather
than in a footnote. Condition E is far cheaper, 12.1 GiB at batch 8 R=4, because
its prompt is an operator signature line rather than four pages.

## Running it

```
PYTHONPATH=$PWD uv run python -m pytest src/latent/tests -q

CUDA_VISIBLE_DEVICES=5 PYTHONPATH=$PWD uv run python -m src.latent.train \
  --base ckpt/base350.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --arm latent_answer --out runs/latent/answer_nocur.pt \
  --steps 800 --batch-size 4 --worlds 4000 --r 4

CUDA_VISIBLE_DEVICES=5 PYTHONPATH=$PWD uv run python -m src.latent.eval \
  --ckpt runs/latent/answer_nocur.pt --tokenizer /home/ec2-user/data/tokenizer_v2.json \
  --out results/latent/answer_nocur.json --r 0,2,4,8 \
  --depths 1,2,3,4,5,8 --breadths 1,2,3,4,5 --kinds sequential,breadth --n 24
```

`smoke.sh` and `smoke2.sh` drive the lanes. `bench.py` needs only the base
checkpoint. `check.py` needs a trained one.

## What the sweep has to settle first

1. **Make the latent segment load bearing.** At 800 steps it is inert. Options
   in rough order of cheapness: train long enough that it is not, `--r-sampling`
   so no single R is special, the `stage` curriculum at a slower schedule, and
   `proj=linear` so the head has capacity beyond a per step scale and shift.
   Until `check.py` shows a live and shuffled gap, an R sweep measures nothing.
2. **Pick the backprop truncation and say so.** Batch 32 needs
   `--backprop-last-k 1` or 2. Whatever is chosen applies to both latent
   conditions and to neither token channel arm.
3. **Put the token channel on the same compute axis.** `infer.token_generate`
   counts a `trace` or `direct` rollout with the same `DecodeCost`, so the
   comparison can be at matched forward passes rather than at matched accuracy.
4. **Report the shape, not the value.** `fit_decay` already emits the log
   slope and the crossing depth together. A latent condition that raises depth
   one and keeps the same slope has moved the cliff; one that flattens the slope
   has done something else, and only the second would say anything about the
   vocabulary bottleneck.
