# Three readers, one item set

The architecture question this project has been circling is whether the network
should do the reasoning or only the reading. That is an empirical question with
three answers on the table, and this document runs all three over the same
items with the same grader.

    A   the RL checkpoint at runs/final/rlsimple-503-921, which reads,
        reasons and answers, through the world header and the retrieval loop
        it was trained in
    B   the hand written frame aware parser of src/norm/parse.py feeding
        src/norm/interp.py, in two conditions: handed the item's own frame,
        and restricted to the 490 frames it was written for
    C   the normalizer of src/norm/TRAIN.md feeding the same interpreter, at
        0.40M and at 45.5M parameters

The claim under test is that C holds on frames it never trained on where B
cannot generalise and A collapses. Part of that is true and part of it is not,
and the part that is not is the more useful half.

## 1. The item set

One structure per item, drawn by `src/norm/gen.py`, written into one corpus
frame by `src/norm/render.py`, and executed by `src/norm/interp.py` for the
gold answer. Frames come from `src/norm/ndata.py:split_frames`, which is the
partition the normalizer trained under, so a held out frame here is held out
there. 50 items in each of 5 frame groups by 12 structure shapes, 3,000 items.

Two of the fourteen renderable shapes are not here. `apply_n` and `sum_chain`
answer with an integer the page never states, so there is no option set for
them and no chance floor that is not invented. Every item that is here passed
the same gate: the option set is `src/norm/neval.py:candidates`, the values the
plan's last step could have returned, it holds the gold answer, and it has at
least two members. The floor is the mean of one over the option count and runs
from 0.100 to 0.500 depending on the shape.

Grading is one function, `src/norm/cmpwork/grade.py`, over all three systems.
It matches on word tokens rather than substrings, because an invented word can
be a prefix of another invented word on the same page and `answer.contains(x)`
would score `emb` correct where the answer is `embqen`. Forced choice is the
headline: exactly one option named, and it is the gold one. Naming two is
wrong however the first one falls. The lenient companion, which takes the first
option named, is recorded beside it, and so are the hedge rate and the rate at
which a system names nothing.

## 2. How far the held out frames are

`src/frames/distance.py` splits frame distance in two and refuses to average
them: `shape_distance` is Levenshtein over a delexicalised token sequence
divided by the longer length, and `lex_distance` is one minus the Jaccard
overlap of the open class words delexicalisation removed. Both functions are
imported unchanged, and so is `delexicalise`.

What that module cannot supply is the surface. Its own `surface` renders the
156 frame bank of `src/frames/generate.py`; the frames here are the 768 corpus
frames, so `src/norm/cmpwork/dist.py` renders one fixed structure into each of
them and reads the nonce map off that structure. Distance is then measured from
each frame to the nearest of the 490 training frames.

TABLE_DISTANCE

The two axes come apart exactly as that module was built to show. The held out
lexicon is at shape distance 0.0000: its sentence geometry is a training frame's
geometry, token for token, and only the words differ. The held out sentence mode
is the reverse, 0.2335 of geometry away with ordinary words. `mixed` is far on
both.

## 3. The comparison

Forced choice, per frame group and per shape, never pooled. n and the floor are
that cell's own.

TABLE_MAIN

Read by frame group, with the spread across the twelve shapes as min / median /
max:

TABLE_RANGE

## 4. What the parser does off its own frames

B in the restricted condition is not told which frame the text is in. It tries
each training frame's pattern set in sorted order and takes the first that
reads the whole item, which is what a parser written for a fixed frame set does
when text arrives from outside it.

TABLE_BCOVERAGE

The restricted parser never reads an item wrong. Where it reads, it is right,
in every group. Its accuracy is its coverage and nothing else, and its failure
is a refusal with a reason attached rather than a guess. On the training frames
it read 320 of 600 items through some frame other than the one they were
written in, so the templates it holds already cover more than the frames they
came from. On the held out question form it covers 542 of 600. On a held out
lexicon, a held out sentence mode, or both, it covers none.

Handed the frame, the same parser is 1.0000 in all sixty cells, 3,000 of 3,000.
That number is the one to keep in view for the rest of this document.

## 5. Structure exactness under C

The answer is a weaker reading than the structure. A structure can be wrong in a
row the question does not touch and still answer correctly, and on some shapes
that gap is wide.

TABLE_MAIN_EXACT

## 6. The transposed operand test

The sharpest result on record in this project is `src/audit/VERDICT.md` check 8:
pages whose operand roles were swapped after training, same glyph, same
constants, same associativity sentence, and the worked examples recomputed so
the page states the swapped rule twice. The checkpoint followed the identity it
had learned on 678 of 678 items and the page on 0 of 678.

The structure language's analogue of a non-commutative binary operation is a
`Table` whose key pairs are drawn from one symbol set, which the frame grammar
writes as the `pair` question shape, one line per ordered pair. Transposing the
operand roles swaps the two operands on every line and leaves the values where
they are. The question is byte identical in the two versions. Items are kept
only where the two versions give different answers and where the answer cannot
be echoed out of the question, which are the filters the original test applied.
750 pairs of pages, 1,500 items.

`gold` is what the page in front of the reader says. `alt` is what the other
version of that same page says, which on a transposed page is the reading it
had before the edit.

TABLE_TRANSPOSE

The interpreter is not what is failing, and neither is the language. On these
same shared domain grids `serialize` and `deserialize` round trip 20 of 20 at
every degree of overlap between the two key columns, and the reference parser
recovers the structure exactly 20 of 20. What fails is the reading.

The failure is specific and it is legible. Handed a grid whose two key columns
are disjoint, which is the only kind `src/norm/gen.py` draws, the 45.5M
normalizer is exact on 40 of 40. Move one symbol into both columns and it is
exact on 0 of 40, and it emits the same token stream it would have emitted for
a disjoint grid, naming copy slots `W12` through `W15` that the text does not
contain. It is writing the shape of a page it has seen rather than the page in
front of it.

Against the checkpoint's 0 of 678 toward the page and 678 of 678 toward
training, the normalizer is 0 of 750 toward the page and 0 of 750 toward the
other reading. It matches the checkpoint on the first number. On the second it
does something different, and the difference is the whole of what the
architecture buys here: the structure it writes is not a structure, the
interpreter is handed nothing it can run, and the system answers nothing rather
than answering confidently from a memory. That is a safe failure where the
checkpoint's was a dangerous one. It is not a solved test.

## 7. What one example of the missing page is worth

TABLE_LADDER_XS

TABLE_LADDER_XS_SPLIT

## 8. Composition depth

The interpreter is flat in depth by construction, and this is the measurement
rather than the construction. One ring walk per depth against a reference
computed by index arithmetic rather than by walking, so an error in the walk
cannot be reproduced by the reference.

TABLE_INTERP

Depth 48 costs 4.4 microseconds per step and depth 32768 costs 5.3. Every
answer is exact.

Getting a depth question to the interpreter is the part that is not flat, and
there are two separate ceilings before it.

The first is arithmetic on the ring. A ring of width w makes depth n and depth
n mod w the same answer, so a ladder whose ring is narrower than its deepest
question is not a depth ladder. The first version of this one used width 10 and
scored 1.000 at depth 12 with the structure wrong in every item, because the
network walked two steps and on a ring of ten, two steps is twelve steps. Every
number below comes from cells where the depth is less than the width.

The second is the token seam. `src/norm/ntok.py:TEMPS` holds sixteen `t`
temporaries, so a plan of seventeen steps cannot be written in the output
vocabulary at all. `serialize` refuses at depth 17 with "temporary 't17' is not
canonical" while the interpreter answers the same plan exactly. This is a
constant in the seam and not a property of either the language or the
interpreter, and no amount of training moves it.

Crossing the two axes on purpose, on training frames, forty items per cell:

TABLE_WDEPTH

The parser is 1.0000 in all forty six cells, at every width and every depth. The
normalizer is exact only at ring widths it has read before, and inside those it
is flat: at width 10 it is 1.0000 at depth 2 and 1.0000 at depth 8. At width 12
and above it is 0.0000 exact at every depth including depth 2, so what stops it
is the page and not the plan.

Two cells there are worth reading closely because the answer score flatters
them. At width 14 depth 12 the forced score is 0.4250 against a floor of 0.071
and the structure exactness is 0.0000: the network writes a seven step plan over
a table it got wrong, and lands on the right ring node seventeen times in forty.
At width 12 depth 2 the forced score is 0.6000 and the exactness is again
0.0000. On this shape the answer level number is not evidence of reading.

Held inside the widths the generator draws, which is width max(4, depth + 2),
the depth curve is flat and exact:

TABLE_DEPTH_NARROW_TRAIN

And on a held out lexicon, where the restricted parser refuses every item:

TABLE_DEPTH_NARROW_LEXICON

## 9. How to run it

    export AWS_PROFILE=chronos
    cd ~/decoupled-reasoner

    .venv/bin/python -m src.norm.cmpwork.items --n 50
    .venv/bin/python -m src.norm.cmpwork.xitems
    .venv/bin/python -m src.norm.cmpwork.ditems
    .venv/bin/python -m src.norm.cmpwork.ditems --width 0 --depths 2,3,4,5,6,7,8 \
        --out results/norm/compare/n_items.jsonl.gz
    .venv/bin/python -m src.norm.cmpwork.dist --procs 4

    .venv/bin/python -m src.norm.cmpwork.runa --mode greedy
    .venv/bin/python -m src.norm.cmpwork.runb --procs 4
    .venv/bin/python -m src.norm.cmpwork.runc --ckpt results/norm/train/ckpt_l.pt

    .venv/bin/python -m src.norm.cmpwork.wdepth
    bash src/norm/cmpwork/ladder_drive.sh

    .venv/bin/python -m src.norm.cmpwork.report --stem main
    .venv/bin/python -m src.norm.cmpwork.xreport
    .venv/bin/python -m src.norm.cmpwork.tables
    .venv/bin/python scripts/norm_compare_md.py
