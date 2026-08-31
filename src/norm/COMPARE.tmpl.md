# Three readers, one item set

Whether the network should do the reasoning or only the reading is an empirical
question with three answers on the table, and this document runs all three over
the same items with the same grader.

    A   the RL checkpoint at runs/final/rlsimple-503-921, which reads, reasons
        and answers, driven through the world header and the retrieval loop it
        was trained in
    B   the hand written frame aware parser of src/norm/parse.py feeding
        src/norm/interp.py, in two conditions: handed the item's own frame,
        and restricted to the 490 frames it was written for
    C   the normalizer of src/norm/TRAIN.md feeding the same interpreter, at
        404,608 and at 45,483,008 parameters

The claim under test is that C holds on frames it never trained on, where B
cannot generalise and A collapses. Two thirds of that is what the numbers say.
The third is not, and the way it fails is the more useful half of the document.

## 1. The item set

One structure per item, drawn by `src/norm/gen.py`, written into one corpus
frame by `src/norm/render.py`, executed by `src/norm/interp.py` for the gold
answer. Frames come from `src/norm/ndata.py:split_frames`, the partition the
normalizer trained under, so a held out frame here is held out there. 50 items
in each of 5 frame groups by 12 structure shapes, 3,000 items.

Two of the fourteen renderable shapes are not here. `apply_n` and `sum_chain`
answer with an integer the page never states, so they have no option set and no
chance floor that is not invented. Every item that is here passed one gate: the
option set is `src/norm/neval.py:candidates`, the values the plan's last step
could have returned, it holds the gold answer, and it has at least two members.
The floor is the mean of one over the option count and runs from 0.100 to 0.500
by shape.

Grading is one function, `src/norm/cmpwork/grade.py`, for all three systems. It
matches word tokens, not substrings, because an invented word can be a prefix of
another invented word on the same page and asking whether the answer contains
`emb` would score a page whose answer is `embqen`. Forced choice is the
headline: exactly one option named and it is the gold one. Naming two is wrong
however the first one falls. The lenient companion takes the first option named,
and the hedge rate and the rate of naming nothing travel with every cell.

A note on reading a score below its floor. The floor is what a guesser gets.
A system that names nothing gets zero, which is below it, and both of the
networks here spend most of their errors naming nothing rather than guessing.

## 2. How far the held out frames are

`src/frames/distance.py` splits frame distance in two and refuses to average
them: `shape_distance` is Levenshtein over a delexicalised token sequence
divided by the longer length, and `lex_distance` is one minus the Jaccard
overlap of the open class words delexicalisation removed. Those functions and
`delexicalise` are imported unchanged.

What that module cannot supply here is the surface. Its own `surface` renders
the 156 frame bank of `src/frames/generate.py`, and these are the 768 corpus
frames, so `src/norm/cmpwork/dist.py` renders one fixed structure into each
frame and reads the nonce map off that structure. Distance is then measured
from each frame to the nearest of the 490 training frames.

TABLE_DISTANCE

The two axes come apart the way that module was built to show. The held out
lexicon sits at shape distance 0.0000: its sentence geometry is a training
frame's geometry token for token and only the words differ. The held out
sentence mode is the reverse, a fifth of the geometry away with ordinary words.
`mixed` is far on both.

## 3. Reading the checkpoint's number honestly

A is driven exactly as `src/primitives/framecheck.py:make_trained_answer_fn`
drives it, which is `src/rl/env.py:build_prompt` with no in context documents:
the world header, then the question, with the pages reaching the model only
through `src/evals/interactive.py:generate_with_retrieval`. That loop decodes
greedily and nothing in it is configurable, so the sampled companion leaves the
loop alone and sharpens the step function instead, returning a vector whose
argmax is a token sampled from the real logits at temperature 0.7 and top k 50.

Two things were checked before any number was kept. The header's domain string
is not specified by the gate, and this checkpoint trained one family per
domain, so five domain strings and an empty world dict were run over the same
32 items:

TABLE_AHEADER

Nothing separates them, and `skill_exception_rule`, which drew the most
retrieval rounds, is the one used throughout. The second check found what does
separate them, which is the question form:

TABLE_AFORM

On `wh`, the form its own rollouts are written in, the checkpoint retrieves once
per item and answers 0.3125 of them. On `cloze` and `imperative` it issues no
retrieval at all and answers nothing. The zero is the checkpoint's behaviour and
not the harness: the same code, the same header and the same generator produce a
non zero score as soon as the question is phrased the way it was trained. Adding
the pages to the prompt as documents instead does not help it, and neither does
forcing the answer marker.

The loop itself ran clean. Retrieval rounds, stop reasons and denominators for
every pass the checkpoint made in this document:

TABLE_AHARNESS

Almost every trajectory ends at `<|eot|>` of its own accord, so the 256 token
budget is not what is cutting the answers off, and on the wh corner of section
10 the checkpoint retrieves once per item, which is what its own rollout log
records.

That said, nine of the twelve shapes here and three of the four question forms
are outside anything this checkpoint was rewarded on. What follows is a
comparison of deployed systems on one corpus, and section 10 puts A back on its
own ground.

## 4. The comparison

Forced choice, per frame group and per shape, never pooled. n and the floor are
that cell's own.

TABLE_MAIN

By frame group, with the spread across the twelve shapes as min / median / max:

TABLE_RANGE

Three things fall straight out.

B handed the frame is 1.0000 in all sixty cells, 3,000 of 3,000, on every held
out frame group. A frame grammar plus a parser written against it does not
degrade with frame distance, because distance from the training frames is not a
quantity it has.

B restricted to the frames it was written for is 1.0000 where its templates
reach and 0.0000 where they do not, with nothing in between.

C is the only system whose score is a function of frame distance. It is not
1.0000 anywhere, including on the training frames, and it does not fall to zero
anywhere either.

The two distance axes cost it differently, and the ordering is the one
`src/frames/distance.py` was written to expose. The held out lexicon is far in
words and identical in geometry, and costs the 45.5M reader almost nothing: its
median cell is 0.990 against 1.000 on the training frames. The held out sentence
mode is the other way round, ordinary words in a geometry a fifth of the way
off, and it takes the median to 0.840. Moving the words is cheap and moving the
geometry is not, which is the direction the wording ablation that module cites
found for the checkpoint. At 404,608 parameters the two axes cost about the
same, 0.710 and 0.730, so the asymmetry is something the larger reader buys.

Distance columns in the group table are item weighted and the frame table in
section 2 is frame weighted, so the two differ slightly and neither is a
rounding of the other.

The rate at which each system names nothing, in the same cells:

TABLE_MAIN_HEDGE

## 5. What the parser does off its own frames

B in the restricted condition is not told which frame the text is in. It tries
each training frame's pattern set in sorted order and takes the first that reads
the whole item, which is what a parser written for a fixed frame set does when
text arrives from outside it.

TABLE_BCOVERAGE

The restricted parser never reads an item wrong. Where it reads, it is right, in
every group, so its accuracy is its coverage and nothing else and its failure is
a refusal with a reason attached. On training frames it read 320 of 600 items
through some frame other than the one they were written in, so its templates
already cover more than the frames they came from. On the held out question form
it covers 542 of 600. On a held out lexicon, a held out sentence mode, or both,
it covers none of 600, three times over.

This is the shape of the claim that C is supposed to beat, and on those three
groups C beats it in all thirty six cells. It is also the shape of the claim
that beats C: hand the same parser the frame and it is exact everywhere.

## 6. Structure exactness

The answer is a weaker reading than the structure. A structure can be wrong in a
row the question does not touch and still answer correctly, and on some shapes
that gap is wide enough to matter.

TABLE_MAIN_EXACT

## 7. The transposed operand test

The sharpest result on record in this project is `src/audit/VERDICT.md` check 8.
Pages whose operand roles were swapped after training, same glyph, same
constants, same associativity sentence, with the worked examples recomputed so
the page states the swapped rule twice. The checkpoint followed the identity it
had learned on 678 of 678 items and the page on 0 of 678.

The structure language's analogue of a non-commutative binary operation is a
`Table` whose key pairs are drawn from one symbol set, which the frame grammar
writes as the `pair` question shape, one line per ordered pair. Transposing the
operand roles swaps the two operands on every line and leaves the values where
they are, so the page states the swapped rule on all nine lines. The question is
byte identical in the two versions. Items are kept only where the two versions
answer differently and where the answer cannot be echoed out of the question,
which are the filters the original test applied. 750 pages in each version.

`gold` is what the page in front of the reader says. `alt` is what the other
version of the same page says, which on a transposed page is the reading it had
before the edit.

TABLE_TRANSPOSE

By frame group, which is where the restricted parser's 0.4000 comes from: two
of the five groups are frames it holds templates for and three are not.

TABLE_TRANSPOSE_SPLIT

Neither the language nor the interpreter is what fails. On these same shared
domain grids `serialize` and `deserialize` round trip 20 of 20 at every degree
of overlap between the two key columns, and the reference parser recovers the
structure exactly 20 of 20 and answers both versions 750 of 750. What fails is
the reading, and it fails before it reaches the interpreter.

The shipped normalizer does not read the page at all. `src/norm/gen.py` draws
the `pair` shape with two disjoint symbol sets, so no page it writes can state
an operation over one domain, and the network has never seen one. Handed a grid
whose key columns are disjoint it is exact on 40 of 40. Move a single symbol
into both columns and it is exact on 0 of 40 and emits the token stream a
disjoint grid would have produced, naming copy slots `W12` through `W15` that
the text does not contain.

So the test as posed cannot be answered by a checkpoint that has never read the
page shape it needs. Section 8 gives it the page shape.

## 8. What examples of the missing page buy

Half of every fine tuning batch is drawn from the original training file, so
this measures acquisition rather than a trade, and the twelve shape set of
section 4 is re-scored at every rung as the regression check. The k = 0 rung is
the control: the same optimiser, the same 1,500 steps, no grids.

The 404,608 parameter reader:

TABLE_LADDER_XS

The 45,483,008 parameter reader:

TABLE_LADDER_L

On the smaller reader the transposed column peaks at 236 of 750 and then falls
back while the original column keeps rising to 420. On the larger one, at 1,024
grids, the original version of the page is answered 672 of 750 and the
transposed version 40 of 750, from pages that differ only in which of two
operands is named first on each line. The structure is exact on 0 of 750
transposed items at every rung of both ladders.

The structure level census says what it writes instead. Categories are disjoint;
`keys in the untransposed order` means the nine values are the page's nine
values in the page's order and the nine key pairs are the row major order of an
untransposed grid:

TABLE_XMODE

That is the whole finding. The reader transcribes the page's values in the
page's order onto the key layout it learned, and binds them wrong. It is the
failure `src/norm/TRAIN.md` section 9 reads out of `compose` in a case built to
isolate it: right keys, right values, wrong pairing.

Against the checkpoint's 0 of 678 toward the page and 678 of 678 toward its
training identity, the normalizer that has been shown the page shape 1,024 times
is 40 of 750 toward the page and 0 of 750 exact. Both readers follow a layout
they carry rather than the one in front of them. The architecture moved where
the failure lives, from the answer to the structure, and it did not remove it.

There is one real difference and it is not nothing. The checkpoint answered
confidently and wrongly. The shipped normalizer emits a stream that is not a
structure, the interpreter is handed nothing it can run, and the system declines
on 750 of 750 rather than naming a cell. That is a safe failure where the other
was a dangerous one. It is not a passed test.

## 9. Composition depth

The interpreter is flat in depth by construction, and this is the measurement
rather than the construction: one ring walk per depth against a reference
computed by index arithmetic rather than by walking, so an error in the walk
cannot be reproduced by the reference.

TABLE_INTERP

Depth 48 costs 4.4 microseconds per step and depth 32768 costs 5.3, and every
answer is exact.

Getting a depth question to the interpreter is the part that is not flat, and
two ceilings stand before it.

The first is arithmetic on the ring. A ring of width w makes depth n and depth
n mod w the same answer, so a ladder whose ring is narrower than its deepest
question is not a depth ladder. The first version of this one used width 10 and
scored 1.000 at depth 12 with the structure wrong in every item, because the
network walked two steps and on a ring of ten, two steps is twelve steps. Every
cell below has depth below width.

The second is the token seam. `src/norm/ntok.py:TEMPS` holds sixteen `t`
temporaries, so a plan of seventeen steps cannot be written in the output
vocabulary at all. `serialize` refuses at depth 17 with "temporary 't17' is not
canonical" on a plan the interpreter answers exactly. That is a constant in the
seam, not a property of the language or the interpreter, and no amount of
training moves it.

Crossing width against depth on purpose, on training frames, forty items a cell:

TABLE_WDEPTH

The parser is 1.0000 in all forty six cells at every width and every depth. The
normalizer is exact only at ring widths it has read before, and inside those it
is flat: width 10 is 1.0000 at depth 2 and 1.0000 at depth 8. At width 12 and
above it is 0.0000 exact at every depth including depth 2. What stops it is the
page, not the plan.

Two cells there are worth reading closely because the answer score flatters
them. At width 14 depth 12 the forced score is 0.4250 against a floor of 0.071
with structure exactness 0.0000: the network writes a seven step plan over a
table it got wrong and lands on the right ring node seventeen times in forty. At
width 12 depth 2 the forced score is 0.6000 and the exactness is again 0.0000.
On this shape the answer level number is not evidence of reading.

Held inside the widths the generator draws, which is max(4, depth + 2), the
depth curve is flat and exact, and A is at or below its floor at every depth:

TABLE_DEPTH_NARROW_TRAIN

And on a held out lexicon, where the restricted parser refuses every item:

TABLE_DEPTH_NARROW_LEXICON

So depth 48 is reachable by B and by the interpreter, at 1.0000 and at constant
cost per step, and is not reachable by C at all. It is thirty two steps past
what the output vocabulary can spell, and the ring that would make it an honest
question is nearly five times wider than the widest ring the generator draws.

## 10. The checkpoint on its own ground

Section 3 showed that most of the item set is outside what A was rewarded on. So
here is the corner that is not: the three structure shapes its three training
families correspond to, asked as `wh` questions, which is the form its rollouts
use. 60 items per cell, same generator, same grader, same three systems.

TABLE_HOME

By frame group:

TABLE_HOME_RANGE

## 11. What this says

On held out frames the normalizer beats the restricted parser, decisively and in
every cell where the parser's templates do not reach. That is the claim, and it
holds: on the held out lexicon, the held out sentence mode and the two together,
B restricted answers none of 1,800 items and C answers most of them.

The claim does not survive contact with the unrestricted parser. Handed the
frame, `src/norm/parse.py` is 1.0000 on all 3,000 items of the twelve shape set,
1.0000 in all forty six cells of the width by depth grid, 1.0000 at depth 48,
and 750 of 750 on both versions of the transposed page. The normalizer is none
of those things at any size measured. On this corpus, where the frame grammar is
written down and a parser can be compiled from it mechanically, the hand written
parser plus the frame grammar is the better system, and saying otherwise would
require a wording the grammar does not contain.

What the normalizer buys is the case the grammar does not contain, and what it
costs is exactness. That trade is real and it is measurable here: 542 of 600 on
one held out axis for the parser against 0 of 600 on each of the other three,
versus a reader that answers everywhere and is exact nowhere.

The transposed operand test says the harder thing. The architecture was built so
that composition, depth, verification and termination stop being the network's
problem, and on those it delivers: the interpreter is exact and flat to depth
32768, refuses what it cannot compute, and never guesses. Reading was supposed
to be the easy half. On a page whose operand roles are swapped, the reader
follows the layout it learned and not the page in front of it, 0 of 750 exact
after 1,024 examples of that page shape, which is the same failure the language
model has at a different level of the stack. Moving the reasoning into a program
did not make the perception faithful. It made its failures loud instead of
confident, which is worth something, and it did not make them go away.

## 12. Every artifact

    results/norm/compare/items.jsonl.gz          the twelve shape set, 3,000
    results/norm/compare/h_items.jsonl.gz        the wh corner, 900
    results/norm/compare/x_items.jsonl.gz        the transposed grids, 1,500
    results/norm/compare/d_items.jsonl.gz        the fixed width depth ladder
    results/norm/compare/n_items.jsonl.gz        the generator width depth ladder
    results/norm/compare/frame_distance.json     768 frames to the nearest train frame
    results/norm/compare/a_*.jsonl.gz            A, per item, with rounds and stop reason
    results/norm/compare/b.jsonl.gz              B in both conditions, per item
    results/norm/compare/c_*.jsonl.gz            C, per item, greedy and sampled
    results/norm/compare/report_*.json           every cell of every table
    results/norm/compare/ladder_xs.json          the example ladder, 0.40M
    results/norm/compare/ladder_l.json           the example ladder, 45.5M
    results/norm/compare/xmode.json              the structure level census
    results/norm/compare/wdepth.json             width crossed with depth
    results/norm/compare/header_ablation.json    six world headers
    results/norm/compare/a_diagnostic.json       A by question form and condition
    results/norm/depth/summary.json              the interpreter to depth 32768
    results/norm/compare/tables/                 every table in this document

## 13. How to run it

    export AWS_PROFILE=chronos
    cd ~/decoupled-reasoner

    .venv/bin/python -m src.norm.cmpwork.items --n 50
    .venv/bin/python -m src.norm.cmpwork.homeitems
    .venv/bin/python -m src.norm.cmpwork.xitems
    .venv/bin/python -m src.norm.cmpwork.ditems
    .venv/bin/python -m src.norm.cmpwork.ditems --width 0 --depths 2,3,4,5,6,7,8 \
        --out results/norm/compare/n_items.jsonl.gz
    .venv/bin/python -m src.norm.cmpwork.dist --procs 4
    .venv/bin/python -m src.norm.cmpwork.xdata

    .venv/bin/python -m src.norm.cmpwork.hdr
    .venv/bin/python -m src.norm.cmpwork.diag
    .venv/bin/python -m src.norm.cmpwork.runa --mode greedy
    .venv/bin/python -m src.norm.cmpwork.runb --procs 4
    .venv/bin/python -m src.norm.cmpwork.runc --ckpt results/norm/train/ckpt_l.pt

    .venv/bin/python -m src.norm.cmpwork.wdepth
    bash src/norm/cmpwork/ladder_drive.sh
    .venv/bin/python -m src.norm.cmpwork.xmode --ckpts ...

    .venv/bin/python -m src.norm.cmpwork.report --stem main
    .venv/bin/python -m src.norm.cmpwork.xreport
    .venv/bin/python -m src.norm.cmpwork.tables
    .venv/bin/python scripts/norm_compare_md.py
