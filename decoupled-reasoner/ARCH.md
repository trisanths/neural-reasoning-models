# NRM-1B architecture specification

A Neural Reasoning Model of roughly one billion parameters, trained from scratch,
whose weights hold language, reasoning machinery, and the retrieve-read-apply
loop, and whose knowledge lives outside in an evidence fabric.

Every choice below is justified by a measurement. Measurements marked OURS come
from this project's runs; measurements marked LAB come from the H200 optimization
lab at `~/Desktop/Overshoot/gpuoptimize`, whose numbers are cited with the effect
they produced. Where neither has evidence, the line says so and names the
experiment that would settle it.

## 1. What the model must do

Answer a question by fetching material it has never seen, reading it, and acting
on it, including material describing a system that did not exist when training
ended. OURS: a 350M model does this for stated rules at 0.680 accuracy with the
correct page against 0.002 with a different system's page and 0.000 with a blank
page, retrieving and answering well-formed in all three conditions, so the
dependence on the fetched material is real.

What it must stop doing: composing multi-token answers by generation when the
answer is present verbatim in the evidence. OURS: the same model reads a routing
table whose answer is "tutez" and emits "wrenbra desk"; on web questions the gold
answer reached its context 12 times in 60 and was never extracted; on arithmetic
families it scores 0.104 with the correct page and 0.098 with the wrong one,
which is no dependence at all.

## 2. The hardware contract

These are constraints, not preferences. A design that violates them wastes the
compute budget regardless of its elegance.

Distinct kernel shapes govern utilization, not parameter count. LAB: a 428M tower
with 13 distinct kernels at 8.38us mean is 51% device-busy at batch 1 and 92.9%
at batch 8; a 13M tower with 31 distinct kernels at 2.63us is 19.2% and 38.0%.
The smaller model uses the machine worse. Target a single repeated block shape.

A launch must move at least 9.4 MB to sustain the memory system. LAB: at 2.21us
mean kernel duration that is the break-even; an eager tower's 739 launches at
2.88us sit one to four orders of magnitude beneath it.

Static shapes are a contract. LAB: capture plus static shapes is worth 3.5x at
batch 1 (10.0% utilization eager, 34.8% graphed, 53.8% at batch 16); a dynamic
batch dimension costs 45% at batch 1. Data-dependent shapes cannot be captured at
all, and a single pageable host copy inside a forward cost 1.153 ms.

Batch is the amortization lever, not width. LAB: decode reaches 49.6% of the
bandwidth roofline at batch 1 and 84.2% at batch 8; a small encoder at batch 1
sits at 6.23% SM occupancy while costing the same as four times the work.

Sequential depth is the batch-1 latency floor; width is nearly free. LAB, stated
directly. This is in tension with recurrence and the tension is budgeted in 4.3.

Do not write custom kernels. LAB: the best hand-written Hopper QKV was 21.20%
slower than cuBLAS in an interleaved control, CUTLASS tuning was a wash, 2:4
sparsity was slower than dense, and 0 of 36 decode submissions were true
single-launch megakernels.

## 3. Shape of the model

One block type, repeated. Width 1536, head dimension 64 (LAB: cuDNN measured 389
TFLOP/s at 64 against 314 at 72, and padding 72 to 80 was slower), 24 heads,
SwiGLU feedforward at 4x, RMSNorm, rotary embeddings. Roughly 1.0B parameters in
the decoder plus 0.15B in the evidence encoder.

Norm sites are minimized. LAB: the elementwise tail is about 40% of batch-1
kernel time after all fusion, and Gemma places 7 norm sites per layer, 189 per
forward, running at 12 to 24% of peak bandwidth. Two per block, activations fused
into GEMM epilogues.

## 4. The four departures from a plain decoder

### 4.1 Partitioned context

Two regions with different roles. The authored stream (question, reasoning,
queries, answer) is predicted and scored. The evidence bank is read and never
predicted. Predicting the next token of a retrieved document spends capacity on
memorization, which is the one thing this project exists to avoid.

The partition is enforced in the loss, not by convention: evidence positions
receive zero gradient.

### 4.2 Evidence cross-attention

Chunks are encoded once by a small bidirectional encoder and consumed by the
decoder through cross-attention, so evidence tokens are keys and values only and
cost is linear in evidence rather than quadratic.

Chunks are never encoded one at a time. All chunks for all queries in a step are
packed into one call with a block-diagonal mask, padded to the batch maximum.
LAB: pad-to-max reached 116.9 img/s against 51.0 for the naive path and 122.3 for
an ideal bucketing scheduler, with 1.75% wasted work and no queueing, while the
bucketing scheduler's p99 was 831.6 ms against padding's 185.6 ms.

Padded evidence slots are masked by score poisoning, writing negative infinity
before the max rather than predicating loads. LAB: about 4% cheaper.

Queries batch against a shared bank, never banks against a query. LAB: the LM
head's latency is flat from batch 1 to 128 over a 1.476 GB read, which is the
same amortization.

GAP: the lab has no cross-attention measurement; all its attention numbers are
self-attention. First experiment on the new hardware is a cross-attention
occupancy and bandwidth profile at several bank sizes.

### 4.3 Recurrent core with static depth

A tied core of blocks applied a fixed number of times, so computational depth
exceeds parameter count.

Depth is a static per-request parameter drawn from a small enumerated set, chosen
before dispatch, with one captured graph per depth and same-depth requests
grouped into a step. It is never decided per token and never read back from the
device. LAB: every content-dependent compute mechanism tested was rejected, and
the one surviving routing decision was known before the request began.

The core is sized for L2 residency, so iterations re-read weights from cache
rather than DRAM. LAB: protecting an L2-resident weight pack by marking the
competing stream evict-first was worth +50% at context 2048 and +25% at 8192, and
the spill is a cliff rather than a slope, measured at -12% past the budget. The
evidence bank's loads are marked evict-first for exactly this reason.

OPEN AND DECIDING: the lab never states the H200 L2 size, and the tension between
"width is free, depth is the latency floor" and "keep the tied core resident"
resolves differently at different L2 budgets. Measure L2 on the target card, then
set core width and block count so the tied weights fit under it. This single
measurement fixes the width-versus-depth split.

### 4.4 Pointer head

The output distribution mixes vocabulary generation with selection over evidence
positions, so answering from retrieved material is a copy rather than a
reconstruction. This targets the measured failure in section 1.

The scoring projection is dense over a fixed-size padded evidence buffer and is
not chunked. LAB: the LM head runs at 4.27 TB/s, 100% of memcpy, with no residual
for a better kernel; chunking it measured 0.92x and 0.84x. The pointer head
writes one score per evidence position rather than per vocabulary entry, so it
sits further into the memory-bound region and batches at least as well.

Selection is an argmax on device, emitted as a tensor. LAB: argmax measured
12.67us against 88.81us for topk(1). Span materialization happens outside the
captured region, and no index is built from a runtime nonzero. LAB: runtime
compaction planning cost about 14 ms of non-kernel overhead, and a data-dependent
mask made capture impossible while inflating a stage 10.3x under contention.

## 5. Answer block refinement

The answer is a fixed-size block refined a fixed number of passes, which gives
joint structure for formatted outputs and a compute dial that batches well. OURS:
left-to-right sampling failed on invented format conventions, where producing the
first token requires knowing the whole shape.

Passes are fixed, never convergence-checked, for the reason in 4.3. LAB has no
measurement of iterative refinement; the transferable fact is that a decode step
ran 5,093 kernels at every batch size and went from 11.28 ms at batch 1 to 20.80
ms at batch 32, so 32x the work cost 1.84x the time. Target 128 to 192 token
positions in flight, which is where the LM head crosses from bandwidth-bound to
compute-bound.

## 6. Training

Objective in three stages. Language and procedure pretraining on a fact-scrubbed
corpus with retrieval traces, tool traces, and invented-system episodes. Then RL
against programmatic verifiers with retrieval inside the rollout, which OURS
shows is the highest-yield lever measured: 0.448 to 0.854 held-out accuracy in
nine minutes on one GPU, and 0.000 to 0.812 on rule application in 216 steps.
Then refinement of the answer block.

RL configuration inherits two hard-won defaults. Any new task family starts with
an exploration configuration, because a policy with no probability mass on
retrieving earns no reward, every rollout scores identically, and the run learns
nothing while looking healthy; this cost four restarts before it was written
down. Structured answers use token-overlap partial credit, because exact match is
a cliff a policy that has never produced the target shape cannot climb.

## 7. What would falsify this design

If cross-attention over a large bank profiles as badly as self-attention did,
the evidence bank is not worth its complexity and the design collapses back to
packed context with aggressive retrieval filtering.

If the tied core cannot be made L2-resident at a useful width, recurrence costs
sequential depth and buys nothing, and the compute dial should come from the
answer block alone.

If the pointer head does not beat generation on copy-heavy tasks in a matched
comparison, the failure in section 1 is not an output-space problem and the
budget should go to the training objective instead.
