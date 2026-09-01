# Does giving role an explicit representation fix the positional collapse

Status: the four arms are queued behind the 167M ladder rung on the one card.
This document holds the method, the verification of the two new training draws,
and the reference numbers the arms are measured against. Results per arm land in
the results section as each arm finishes.

## What is being attacked

The normalizer reads prose into a typed structure. On a held-out sentence mode
it binds which invented word is the key and which is the value to where the word
sits in the sentence rather than to what the sentence says about it, and it does
so with a convention that is a property of the run:

| rung | key first | value first |
|---|---:|---:|
| l45, 45,483,008 params | 0.7302 (n=3528) | 0.3177 (n=3472) |
| xl93match, 93,579,520 params | 0.3243 | 0.7252 |

Pooled the two rungs read 0.5256 and 0.5231 and look identical. On trained
frames both positions are fine, 0.9206 against 0.9211 at l45. The floor for
these cells is `src/norm/neval.py`'s modal-by-shape baseline, 0.1026 key first
and 0.0864 value first on the held-out mode, and the ceiling is
`src/norm/parse.py` at 1.0000 on every cell of every split, so the binding is in
the text and unambiguous there.

The hypothesis this experiment tests is that role order has no representation of
its own, and is inferred from a surface template keyed on the pair (statement
mode, key position). When that template is unseen there is no other channel
stating the roles, and one positional convention takes over.

Two things already argue against the nearest competing account. Nearest-template
transfer would carry the binding over from whichever trained sentence the new one
most resembles, and it predicts the opposite of what happens.
`src/role/rtmpl.py` measures the resemblance over the English words with both
blanks removed:

| held-out sentence | nearest trained sentence | similarity | same key position | l45 reads it |
|---|---|---:|---|---:|
| `The {v} {target} is the one that {vact} a {k} {item}.` | `passive_decl.value_first` `The {v} {target} is what {vact} a {k} {item}.` | 0.7778 | yes | 0.3177 |
| `The {target} that {vact} a {k} {item} is the {v} {target}.` | `passive_decl.value_first` | 0.6667 | no | 0.7302 |

The half whose nearest trained neighbour agrees with it, and agrees closely, is
the half that fails. The half whose nearest neighbour disagrees is the half that
succeeds. Written into `results/role/template_distance.json`.

And the slot numbering does carry a positional cue, but not a sufficient one.
Copy slots are numbered by order of first appearance, so on a page whose rule
lines each name one new key and one new value the two roles land on opposite
parities of slot index. `src/role/rparity.py` fits that rule per key position on
trained frames and applies it unchanged: it reads role at 0.6793 key first and
0.8024 value first on the held-out mode, over 22,835 and 22,464 slots that the
structure gives exactly one role, against a majority-class rate of 0.56. A
shortcut, not a sufficient one, which is what makes the auxiliary arm a fair
test rather than a free pass. In `results/role/parity_shortcut.json`.

## The arms

Every arm is the 45M rung: the same model class from `src/norm/nmodel.py` built
through `src/system/sizes.py`, the same 490 training frames from
`src/norm/ndata.py:split_frames`, the same 1,200,000 training items, the same
30,000 steps at a 32,768 padded-source-token budget, the same seed 1, the same
cosine schedule and peak rate. One thing changes per arm.

    A  baseline          data/norm/train unchanged, no auxiliary loss
    B  minimal pairs     data/role/paired_train, pair-aware batching
    C  auxiliary role    data/norm/train unchanged, a role head on the encoder
    D  both

`src/role/rtrain.py` is `src/system/strain.py` with two switches added. With
neither switch on it calls the same `src/norm/ntrain.py:batches`, the same
`make_batch`, the same loss and the same schedule, and it reaches the encoder
and decoder through `model.encode` and `model.decode`, which is what
`Normalizer.forward` does, so arm A is a reproduction and not a near miss.

Scoring is `src/system/sreport.py` unchanged, which decodes greedy and sampled,
counts exact, malformed, refused and wrong per shape through
`src/norm/neval.py:score`, carries the parser and modal baselines, and writes one
record per item. `src/role/rsplit.py` recounts those records by key position and
never pools across it.

## The minimal pair draw

The corpus already balances key position: 49.78 to 50.06 percent value first for
every shape, and 8,362 to 8,910 value-first items inside every one of the five
trained sentence modes. Balance is not the same as contrast. Every item is a
fresh structure in one frame, so nothing in the file contradicts a rule that
reads the frame's own template and takes the key from a fixed position in it.
That rule fits the whole draw.

`src/role/rdata.py` removes that. One structure is drawn once and rendered
twice, in two frames that agree on lexicon, statement mode, question form and
scope position and differ only in key position, and the two renderings sit next
to each other in the same batch. Slots are numbered by order of first
appearance, so the two gold targets are correspondingly different: the same
table is written `W1 W2` in one member and `W2 W1` in the other. A reader that
takes role from position emits one of those for both and is right about at most
one.

Key position is not one of the three withheld axes and no held-out group is
defined by it, so every training frame's sibling is also a training frame: 490
training frames are 245 sibling pairs, and nothing held out is touched.

Key position reaches only some pages. It selects the `ASSOC` rule sentence and
the `table_row` column header and nothing else, so a `classify`, `apply_n`,
`lookup_general` or `pair` page comes out byte identical in the two frames.
Rendering those twice would put a literal duplicate in the batch and halve the
distinct content for no contrast, so a draw whose two renderings agree is thrown
away and replaced by two independent items of that same shape, drawn the way
`src/norm/ndata.py` draws them. The shape mix is unchanged and the file holds
1,200,000 items, the same as the baseline.

`src/role/rcheck_full.py` checks the invariant on every row of the file rather
than on a sample. The training file carries no text and no structure, only token
ids on both sides, but the target side is the structure written in slot indices
and each member has its own slot table, so deserialising both targets against
their own tables gives two structures in surface symbols that must be equal.
Over all 600,000 slots of two:

| check | count |
|---|---:|
| slots of two | 600,000 |
| minimal pairs | 394,367 |
| independent, the axis does not reach that shape | 205,633 |
| pairs whose frame ids differ in the key position field and no other | 394,367 |
| pairs ordered key first then value first | 394,367 |
| pairs with the same shape | 394,367 |
| pairs with the same structure | 394,367 |
| pairs with the same invented words | 394,367 |
| pairs whose gold targets differ | 342,796 |

The 51,571 pairs whose targets agree are `band_then_lookup` and
`lookup_then_band` in `table_row`, where the symbols of the rule lines have
already been given slot numbers by an earlier page, so flipping the sentence
changes the text without changing the numbering. Those pairs still contradict a
positional reader, which would emit two different targets for them. Written to
`results/role/pairs_paired_train.json`.

One pair, printed in full from a sample built with the text kept:

```
depot.imperative.key_first.wh.scope_last  lookup
    Send every lumxil crate to the wiskybor bay.
    Send every haldmi crate to the zuntcinq bay.
    ...
    Send any unlisted crate to the dricinq bay.
  slots  W0=Thoxmi W1=lumxil W2=wiskybor W3=haldmi W4=zuntcinq ...
  target table W0 a1 W1 W2 W3 W4 W5 W6 W7 W8 dflt W9 ; | in x W7 ; | ...

depot.imperative.value_first.wh.scope_last  lookup
    To the wiskybor bay, send every lumxil crate.
    To the zuntcinq bay, send every haldmi crate.
    ...
    Send any unlisted crate to the dricinq bay.
  slots  W0=Thoxmi W1=wiskybor W2=lumxil W3=zuntcinq W4=haldmi ...
  target table W0 a1 W2 W1 W4 W3 W6 W5 W8 W7 dflt W9 ; | in x W8 ; | ...
```

What it costs. Half as many distinct structures on the paired shapes, and a
step that is 6.3 percent smaller: bucketing by the longer member of a pair gives
150.64 rows and 7,445.5 target tokens per batch against the baseline's 160.84
and 7,949.0, at the same 32,768 budget and with 0 batches over it and 0 pairs
split across two steps. The step count is held at 30,000 as specified, so arm B
sees 6.3 percent fewer target tokens than arm A. That is far smaller than the
effect being measured and it is stated rather than corrected. In
`results/role/batches.json`.

## The auxiliary role head

`src/role/rtrain.py --aux W` puts a linear head over the encoder output that
predicts, at every input position holding a copy slot, whether that invented
word is used as a key and whether it is used as a value. Two independent bits,
because a compose chain's middle level is the value of one table and the key of
the next and a three-way choice would make that a collision. Linear on purpose:
the arm is asking whether role becomes linearly readable off the encoder at the
word's own position, which is what an explicit representation would mean here.

The head is not part of the model. It is not in the checkpoint's `state`, the
parameter count does not move, and the checkpoint loads through
`src/system/sreport.py` unchanged, so what is scored is the same 45,483,008
parameter normalizer as every other arm. The head shapes the encoder during
training and then goes away. `src/role/raux.py` reloads it separately to ask
whether the thing the arm was told to represent transferred.

The labels come from gold and not from a second pass over the text.
`src/role/rlabels.py` deserialises each training item's own target, which is the
structure in the closed output vocabulary, and walks it: table keys and tuple
key parts, weights keys and rule exception keys are keys; table values,
defaults, band labels, rule generals and rule exception values are values. The
surface spellings are not needed, so the slot table handed to `deserialize` is
the slot names themselves and the program comes back written in `W0..W63`, which
is already the index the input side uses.

Two checks. On the 7,000 items of the held-out mode split, which carries the
structure in a sidecar written before either path existed, the labels agree with
that structure on 7,000 of 7,000 items and 0 items name a slot the sidecar does
not have. And over the 1,200,000 training items, 10,278,854 slot mentions are
named by the structure, split 3,457,247 key only, 4,313,462 value only and
2,508,145 both. In `data/norm/train.roles.npy.json`.

The main loss is unchanged: cross entropy over target tokens, summed and divided
by the number of target tokens in the batch. The auxiliary loss is a mean over
the slot positions of the batch, so the weight is a ratio between two per-token
means and does not drift with batch composition. The weight is chosen by a rule
fixed before the probes were run, in `src/role/rpick.py`: three probes at 3,000
steps against arm A's own quick eval at the same step, keep the weights whose
trained-frame score is no more than 0.01 below arm A's, take the largest of
those, and if none qualifies take the smallest probed. An auxiliary loss that
helps adds a signal, one that hurts takes gradient from the objective being
scored, and the second shows up first as the trained-frame score falling.

## What the exchanged structure test adds

The split says whether an arm is asymmetric. It does not say what the wrong
emissions are. `src/norm/neval.py` sorts a failure into wrong-but-executable,
which says the emission was a structure that ran and not what it said.

`src/role/rswap.py` asks the sharper question the positional account implies.
Since slots are numbered by order of first appearance, a reader that binds role
to that order emits, on a value-first page, exactly the gold structure with every
stated pair written the other way round and nothing else changed. That structure
is computable from gold, so the claim is checkable item by item.

This controls for something the minimal pair cannot. Arm B is an intervention on
what the network is trained on and its score says whether the intervention
worked. The exchange test is a measurement on what the network writes, and it
separates two failures that the split scores identically: a reader that has
inverted the binding, and a reader that has lost the page for some other reason.
An arm whose value-first score rises because its emissions stopped being
inverted has had the hypothesised defect repaired. An arm whose value-first score
rises while the inversion rate stays where it was has traded one error for
another, and the split alone would not tell them apart.

Because exact equality with the exchanged structure also demands the right entry
order and the right default, a looser figure runs beside it: over the symbols
gold uses as a key and not as a value, the share the emission uses as a value and
not as a key. That is the binding on its own. A calibration for the strict cell:
of the 1,736 value-first items of the seven shapes in the held-out mode, the
exchanged structure executes for only 496, so a reader that emitted it exactly
would refuse on 71.4 percent, and l45 refuses on 18.9 percent. The strict cell is
therefore expected to be small and the loose one is the number to read.

## Attacks planned against any arm that works

Seeing the same structure twice, adjacent, is a different training signal
whatever axis the two renderings differ on, so a gain from arm B could be a gain
from repetition. `data/role/qpaired_train` is the same draw against question form
instead of key position, pairing on exactly the shapes arm B pairs so the count
of distinct structures matches: 394,154 pairs against arm B's 394,367, every one
differing in the question form field of the frame id and no other, same
structure, same invented words. Question form does not change which symbol the
question names, so all 394,154 of its pairs have identical gold targets, against
342,796 of 394,367 in arm B. That is the difference the control isolates. It runs
only if arm B moves the split, and it takes the card for another three hours.

The other attacks are already in the measurement. Trained frames both positions
must not fall from about 0.92. The held-out question frame and the held-out
lexicon must not fall. Sampled decoding is reported beside greedy on every cell.
And an arm that lifts the pooled number while leaving the split asymmetric has
not fixed anything, which is why no table here carries a pooled headline.

## Results

Pending. Arm A is the gate: if it does not land near 0.7302 key first and 0.3177
value first on the held-out sentence mode, nothing downstream is worth reading
and this section will say so instead.

## Files

    src/role/rdata.py          the minimal pair draw
    src/role/rdata2.py         the same draw against question form, the control
    src/role/rlabels.py        role labels off the gold target
    src/role/rtrain.py         the arms
    src/role/rsplit.py         the key position split, never pooled
    src/role/rfloor.py         the floor and the parser ceiling per cell
    src/role/raux.py           the auxiliary head on held-out splits
    src/role/rswap.py          the exchanged structure test
    src/role/rtmpl.py          the held-out sentence against the trained ones
    src/role/rparity.py        the slot parity shortcut
    src/role/rcheck_full.py    the pair invariant over the whole file
    src/role/rcheck_pairs.py   the pair invariant on a sample that keeps text
    src/role/rcheck_labels.py  the labels against the sidecar structure
    src/role/rcheck_batches.py what a step costs under each batching
    src/role/rpick.py          the auxiliary weight rule
    src/role/rqueue.sh         the arms, one job at a time, behind the ladder
    src/role/rqueue2.sh        the exchanged structure test, after the arms

    data/role/paired_train.*   arm B and D training draw
    data/role/qpaired_train.*  the control draw
    data/norm/train.roles.npy  role labels for the baseline draw
    results/role/              every table above, as json
