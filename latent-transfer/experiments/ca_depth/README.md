# Where does serial-depth state have to live?

A controlled test of one question: when a small transformer must carry state through
k steps of a novel rule, does it matter whether the intermediate states sit in the KV
cache as explicit tokens or as learned latent vectors, given an identical readout?

## Setup

Replicates Beyond Memorization (Rodkin et al., ACL Findings 2026, arXiv 2508.16745):
radius-2 one-dimensional cellular automata, width 20, ten prior states shown, predict
the state k steps ahead, train and test rule sets disjoint (2^31 rules each side).
Backbone 4 layers, d=128, 4 heads, rotary positions, batch 256, 40k steps, Adam 3e-4.
Exact-match on 2000 held-out-rule examples. Three seeds on the decisive cells.
`ca_arms.py` is the whole experiment; `results/TABLE.txt` is the current rendering.

Arms differ only in what crosses the step boundary and how the answer is read out:

| arm | intermediate states | readout |
|---|---|---|
| `os_tok` | none (the paper's O-S) | main model emits 20 bit tokens |
| `oo_tok` | every state as bit tokens (the paper's O-O) | same |
| `oo_pause_a` | one learned slot vector per step, in the KV | same, attending over prefix and slots; emitted bits never carried |
| `oo_lat_a` | hidden state fed back as next input, in the KV | same |
| `oo_pause_s` | `oo_pause_a` plus a probe loss pinning each slot to its state | same |

## Result

Exact match, mean over seeds [min to max], paper recipe:

| arm | k=1 | k=2 | k=4 |
|---|---|---|---|
| paper O-S | 0.95 | 0.40 | <0.25 |
| `os_tok` | 0.840 [0.75-0.89] | 0.518 [0.39-0.67] | 0.280 [0.26-0.30] |
| paper O-O | >0.9 | >0.9 | >0.9 |
| `oo_tok` | 0.752 [0.64-0.94] | 0.794 [0.65-0.93] | 0.718 [0.50-0.89] |
| `oo_pause_a` | 0.609 [0.10-0.93] (4 seeds) | 0.011 [0.01-0.01] | 0.021 [0.01-0.03] |
| `oo_lat_a` | 0.393 [0.01-0.77] | 0.044 [0.03-0.06] | 0.031 [0.03-0.03] |
| `oo_pause_s` | 0.034 | | 0.031 |

Trained on k<=4 and evaluated deeper, `oo_tok` reaches 0.395 [0.12-0.56] at k=8 and
is at chance by k=16. Every latent arm is at 0.003 to 0.041 at every k.

1. Both of the paper's curves reproduce within seed spread once the backbone matches
   theirs. Rotary positions were most of the gap (0.40 to 0.75 at k=1 on one seed);
   the parallel block added 0.03; the rest was seed variance, which is large (0.3 at
   k=1 on identical configs).
2. Explicit intermediate tokens beat no intermediates by 0.44 exact at k=4.
3. Latent intermediates in the same KV, read out by the same mechanism, do worse than
   no intermediates at all. They fit the training rules (loss 0.04 or lower) and
   transfer nothing to held-out rules.
4. At k=1 the latent slot is a lottery over initialisation: 0.10, 0.93, 0.92, 0.48 on
   four seeds. At k>=2 it is dead on every seed, including the ones that won at k=1.
   The slot can hold one step's state well enough for the readout; what never works is
   the next slot reading the previous one. Composition through the latent fails, not
   encoding into it.
5. Forcing the slot to be a decodable copy of its state destroys the k=1 case that
   worked (0.616 to 0.034). What the slot holds when it works is readable by attention
   and not by a decoder, so it is not the state.

The mechanism this supports: a bit token is the CA state and carries no rule, so a
model that writes it can read it under any rule. A learned slot encoding entangles
the training rules, and nothing in the training signal forces it not to. KV memory is
necessary for depth; a fixed, rule-independent interface is what makes it transfer.

## Sequential cost of the token arm (speculative cognition)

The objection to explicit tokens as working memory is that they are serial: k states x
21 tokens, one forward per token. `jacobi_eval.py` initialises the whole k-step trace,
runs the model over it in one parallel pass, replaces every position with its
type-constrained argmax, and repeats to a fixed point. For a causal model the fixed point
is the greedy trajectory, so the output is unchanged and the only question is the number
of passes.

`oo_tok` rope 256x40k trained on k<=4, seeds 0 and 2, 2000 held-out examples per k:

| k | serial tokens | Jacobi passes | final state settles at pass | identical to serial | sequential reduction |
|---|---|---|---|---|---|
| 1 | 21 | 1.0 - 1.1 | 1.1 | 1.000 | ~20x |
| 2 | 42 | 2.1 | 2.1 | 1.000 | ~20x |
| 4 | 84 | 4.1 - 4.2 | 4.1 - 4.2 | 1.000 | ~20x |
| 8 | 168 | 8.4 - 8.6 | 8.4 - 8.6 | 1.000 | ~20x |

Exactly one parallel pass per reasoning step, at every depth. The 21 tokens inside a
state are conditionally independent given the previous state, so the model's
serialization was 21x deeper than the problem's. The token arm therefore has the
sequential cost of a recurrent loop (k passes) together with the accuracy and
extrapolation the latent arms lack.

Draft-and-verify (weak seed-1 checkpoint drafts, strong seed-0/2 checkpoint verifies in
one pass) accepts 0.6 / 1.2 / 2.1 / 2.9-3.3 states per verify at k=1/2/4/8. Both models
are the same size here so there is no wall-clock win; that is the acceptance rate a
cheaper drafter would be measured against. Results in `results/jacobi/`.

## What was wrong along the way, kept as negatives

`results/sweep_v1_linear_readout/` and `sweep_v2/`: a single linear map from one
vector to 20 bits saturates at 0.5 loss on training data and caps every arm at ~0.1;
a 2-layer autoregressive decoder reading from one vector does the same. Absolute
learned positions cap the token arm at 0.40 where rotary reaches 0.75 to 0.94. The
paper's 256x40k recipe overfits training rules under absolute positions and is the
better recipe under rotary. A 1024-way discrete write (`oo_split`) never learns.
`oo_tok`'s first eval argmaxed over the full vocabulary and reshaped; one stray SEP
misaligns every later bit, and that was most of an apparent extrapolation cliff.

`coverage.py`: on this data 7.5% of test examples at k=1 need a neighbourhood that
never appeared in the ten prior states, so the ceiling is 0.925, below the paper's
0.95; their orbits expose slightly more transitions than these.

## Reading number on the 350M (a separate experiment, `reading_number.py`)

Teacher-forced single-step rule application on the decoupled-reasoner 350M, page in
context, 160 questions per condition. Simple families: page under `<|doc|>` 0.138,
under `<|retrieve|><|result|>` 0.444, wrong page 0.000, no page 0.000. Free-running
the policy never emits `<|a|>` under `<|doc|>` and always does under `<|result|>`.
The in-context anomaly was a channel RL never trained. Arithmetic families: 0.000 in
every channel on every checkpoint including the arithmetic-trained ones, which
score the same on the right page and the wrong one. That wall is real.
