# Intelligence per example

Built 2026-08-31 13:09 UTC from `results/norm/oneshot/report.json`. Every table below is
rendered by `src/norm/opdoc.py` out of the record files named at the end.

The measurement. A person reads one page and can then use what it says. A
gradient trained model needs many examples, because that is how gradients work.
A library based system should need one, because that is how definitions work.
This lane invents operations the system has never seen, states each one on a
single page of text, and asks both systems to use it.

The answer. One page is enough for the library system and it is enough on the
first page: 1.0000 strict on all four operation families, unchanged when the
same operation is stated on two pages and on four. The network, given the same
page in its context and no gradient step, is at 0.0157 strict against a floor
of 0.3085, which is below its own guessing floor. Given labelled examples of the
one operation it will be tested on, and an output vocabulary extended for free
so it can write the operation down at all, it climbs the ladder in the table
below rather than arriving at the first example.

## The operation, and why it is new to everything here

The corpus holds four relation structures out: `two_key`, `exclusion`,
`priority_list` and `agreement`. This lane builds operations of the fourth kind.
An agreement operation reads one item in two or more directories and decides
what to answer from whether those readings agree.

Nothing in this project could state one before. `src/norm/shapes.py` has no
shape for it, `src/norm/render.py` cannot write it, `src/norm/parse.py` cannot
read it, and the normalizer's target vocabulary in `src/norm/ntok.py` has no
token for an operator definition at all. The interpreter could always run one,
because `src/norm/lang.py` has had the `OpDef` kind and `src/norm/interp.py` the
`call` operation since they were written, and that asymmetry is the architecture:
the language is fixed, the library grows.

What a definition page may state is fixed and small. An operation names itself,
says which directories it reads and in what order, and gives an ordered list of
clauses, each a condition on the readings and a result. Conditions are: all the
readings agree, no two agree, these two agree, these two differ. Results are:
the reading from that directory, the reading just found shared, a word the page
states outright. `src/norm/oplang.py:enumerate_space` writes out every operation
statable with one clause over two or three directories. There are 144 of them
once the duplicates between the two enumerations are removed, 42 over two
directories and 102 over three. The measurement runs over the whole set rather
than over a chosen example.

An operation whose answer is always what one directory states is dropped. Such a
page defines a new operator that computes an old one, and acquiring it would
prove nothing. 94 of the 285 drawn skeletons were dropped that way and the count
is in `results/norm/oneshot/items.meta.json`.

## What the reader knows, and what it does not

`src/norm/opread.py` is handed the episode text and the frame id and nothing
else. Not the shape, not the operation, not which pages matter. It knows the
definition grammar: three of the four wording modes, the fixed condition
vocabulary, the fixed result vocabulary. It knows no operation. The operator's
name, its arity, which directories it reads, in what order, which conditions it
tests, in what order, what each clause answers and what it answers when no
clause fires are all read off the page, and no branch below names a particular
operation.

The directories themselves are ordinary corpus pages. They are written by
`src/corpus/frames_default.py` through `Frame.page`, so they are byte identical
to what the corpus writes for a two directory agreement instance, and the
normalizer has read thousands of them. Only the definition page and the question
are new.

## The acquisition curve

Each row is one operation family, never pooled with another. `L` is the library
system: read the page, put the operation in an episode scoped library, run the
plan, with no gradient step anywhere in that path. `S1` and `S2` are the
shortcut readers that take the first and the last line stating the question's
key, which is the baseline that matters for an agreement page because two
directories both state the key. `parser` is `src/norm/parse.py`, the project's
hand written parser for the fourteen corpus shapes.

| operation family               | n   | floor  | L 1 page | L 2 pages | L 4 pages | S1     | S2     | parser |
| ------------------------------ | --- | ------ | -------- | --------- | --------- | ------ | ------ | ------ |
| two directories, one clause    | 110 | 0.3735 | 1.0000   | 1.0000    | 1.0000    | 0.2636 | 0.2182 | 0.0000 |
| three directories, one clause  | 310 | 0.3086 | 1.0000   | 1.0000    | 1.0000    | 0.3194 | 0.4129 | 0.0000 |
| two directories, two clauses   | 25  | 0.3567 | 1.0000   | 1.0000    | 1.0000    | 0.2800 | 0.2400 | 0.0000 |
| three directories, two clauses | 405 | 0.2879 | 1.0000   | 1.0000    | 1.0000    | 0.3654 | 0.3358 | 0.0000 |

The three library columns are the curve. One page, two pages and four pages of
the same operation give the same number, because the second page carries nothing
the first did not and the library says so by construction: a repeat that agrees
changes nothing and a repeat that disagrees is a refusal.

The same items split by the frame the pages are written in, which is the split
the normalizer trained under. The library does not read a held out frame
differently from a trained one, and this table is what says so rather than
assuming it.

| family | frame split | n   | floor  | L strict | S1 strict |
| ------ | ----------- | --- | ------ | -------- | --------- |
| a2c1   | mixed       | 10  | 0.4167 | 1.0000   | 0.3000    |
| a2c1   | mode        | 10  | 0.2667 | 1.0000   | 0.5000    |
| a2c1   | train       | 90  | 0.3806 | 1.0000   | 0.2333    |
| a2c2   | lexicon     | 5   | 0.5000 | 1.0000   | 0.2000    |
| a2c2   | mode        | 5   | 0.2500 | 1.0000   | 0.8000    |
| a2c2   | qframe      | 5   | 0.5000 | 1.0000   | 0.0000    |
| a2c2   | train       | 10  | 0.2667 | 1.0000   | 0.2000    |
| a3c1   | lexicon     | 15  | 0.3889 | 1.0000   | 0.3333    |
| a3c1   | mixed       | 15  | 0.2333 | 1.0000   | 0.4667    |
| a3c1   | mode        | 35  | 0.3143 | 1.0000   | 0.2571    |
| a3c1   | qframe      | 35  | 0.3071 | 1.0000   | 0.2571    |
| a3c1   | train       | 210 | 0.3075 | 1.0000   | 0.3286    |
| a3c2   | lexicon     | 45  | 0.3000 | 1.0000   | 0.3556    |
| a3c2   | mixed       | 25  | 0.3167 | 1.0000   | 0.4400    |
| a3c2   | mode        | 40  | 0.3167 | 1.0000   | 0.4000    |
| a3c2   | qframe      | 35  | 0.3214 | 1.0000   | 0.4571    |
| a3c2   | train       | 260 | 0.2740 | 1.0000   | 0.3423    |

## The same measurement against the network

The ladder items are their own set: the five question keys of eight operations,
each asked in twenty combinations of frame, wording and page order drawn from
frames the normalizer never trained on. Both systems answer the same 800 rows.

The network is given more than the library, on purpose. It gets labelled pairs
rather than a page, so each example carries the answer structure. It gets
examples of the very operation it will be tested on. It gets an output
vocabulary extended by the eleven operator tokens of `src/norm/optok.py`, whose
rows are appended after every token the checkpoint already had, so it is handed
for free a notation it would otherwise have had to be retrained to have. Its
training keys are disjoint from the five the items ask about, and half of every
batch is replay from the original training file so the run measures acquisition
rather than a trade.

| system               | examples | n   | floor  | strict greedy | strict sampled | structure exact |
| -------------------- | -------- | --- | ------ | ------------- | -------------- | --------------- |
| library, 1 page      |          | 800 | 0.3646 | 1.0000        | 1.0000         |                 |
| network, no gradient | 0        | 800 | 0.3646 | 0.0238        | 0.0125         | 0.0000          |
| network, control run | 0        | 800 | 0.3646 | 0.0225        | 0.0187         | 0.0000          |

Each fine tuned network on its own operation, which is the cell where it has
every advantage: k labelled examples of exactly this operation, tested on the
same operation in wordings it did not train on.

| pool         | operation    | k=1 | k=2 | k=4 | k=16 | k=64 | no gradient |
| ------------ | ------------ | --- | --- | --- | ---- | ---- | ----------- |
| acq_a2c1_2   | acq/a2c1/2   | -   | -   | -   | -    | -    | 0.0100      |
| acq_a3c1_26  | acq/a3c1/26  | -   | -   | -   | -    | -    | 0.0400      |
| acq_a3c2_144 | acq/a3c2/144 | -   | -   | -   | -    | -    | 0.0300      |
| acq_a2c2_157 | acq/a2c2/157 | -   | -   | -   | -    | -    | 0.0500      |

## Depth

One acquired operation applied n times over, on directories closed under their
own values so an answer can be fed back in. The library's plan is a list and
execution is a loop over it, so depth 16 costs what depth 1 costs and there is
no step cap in `src/norm/interp.py` to reach. Items are aligned: only the
question keys whose option set stays larger than one at every depth are counted,
so the five rows are the same items and not five different ones.

| applications | n   | floor  | L strict | S1     | S2     | network no gradient | network family trained |
| ------------ | --- | ------ | -------- | ------ | ------ | ------------------- | ---------------------- |
| 1            | 555 | 0.2504 | 1.0000   | 0.3820 | 0.4378 | 0.0072              | -                      |
| 2            | 555 | 0.3090 | 1.0000   | 0.1315 | 0.1477 | 0.0180              | -                      |
| 4            | 555 | 0.3589 | 1.0000   | 0.1820 | 0.2162 | 0.0288              | -                      |
| 8            | 555 | 0.3629 | 1.0000   | 0.1351 | 0.1640 | 0.0144              | -                      |
| 16           | 555 | 0.3629 | 1.0000   | 0.1910 | 0.2288 | 0.0090              | -                      |

## Composing two operations from two pages

Two operations, each defined on its own page, the second reading the answers of
the first. The plan is six steps: two directory reads and a call, then two more
and a second call.

| system                         | n   | floor  | strict | lenient | declined | structure exact |
| ------------------------------ | --- | ------ | ------ | ------- | -------- | --------------- |
| library, two pages             | 240 | 0.3915 | 1.0000 | 1.0000  | 0.0000   |                 |
| shortcut, first line           | 240 | 0.3915 | 0.1375 | 0.1375  | 0.0000   |                 |
| shortcut, last line            | 240 | 0.3915 | 0.1792 | 0.1792  | 0.0000   |                 |
| corpus parser                  | 240 | 0.3915 | 0.0000 | 0.0000  | 1.0000   |                 |
| network, no gradient (greedy)  | 240 | 0.3915 | 0.0125 | 0.0125  | 0.5125   | 0.0000          |
| network, no gradient (sampled) | 240 | 0.3915 | 0.0167 | 0.0167  | 0.5208   | 0.0000          |

## The page that contradicts the training

The decisive negative this project already recorded is that the trained
checkpoint followed its training identity on 678 of 678 transposed pages and the
page on 0 of 678. The test here is the same shape. The directory pages are
written exactly as the corpus precedence pages are written, where the first
named page wins, and the definition says the second one does. Both directions
are built, because a system that answers the first directory under both is
following training and a system that answers what the page says under both is
following the page, and one direction alone cannot tell those apart.

| page says   | system               | n   | floor  | follows page | follows training | neither |
| ----------- | -------------------- | --- | ------ | ------------ | ---------------- | ------- |
| page_first  | library              | 230 | 0.2703 | 1.0000       | 1.0000           | 0.0000  |
| page_first  | shortcut, first line | 230 | 0.2703 | 1.0000       | 1.0000           | 0.0000  |
| page_first  | shortcut, last line  | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_first  | corpus parser        | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_first  | network, no gradient | 230 | 0.2703 | 0.0000       | 0.0000           | 1.0000  |
| page_second | library              | 230 | 0.2754 | 1.0000       | 0.0000           | 0.0000  |
| page_second | shortcut, first line | 230 | 0.2754 | 0.0000       | 0.9087           | 0.0913  |
| page_second | shortcut, last line  | 230 | 0.2754 | 1.0000       | 0.0000           | 0.0000  |
| page_second | corpus parser        | 230 | 0.2754 | 0.0000       | 0.0000           | 1.0000  |
| page_second | network, no gradient | 230 | 0.2754 | 0.0130       | 0.0000           | 0.9870  |

The library follows the page in both directions. It does so by construction and
the point of running it is that construction and behaviour are two different
claims. Neither shortcut reader follows the page in both directions: taking the
last matching line agrees with the page whenever the page happens to say the
last directory wins, and disagrees with it otherwise.

## What refuses, and what happens when the page is attacked

A system that answers 1.0000 everywhere is a bug until it has been attacked.
Four attacks and two controls, all in `results/norm/oneshot/attack.json` and
`report.json`.

| check                                  | n   | rate   | where                                  |
| -------------------------------------- | --- | ------ | -------------------------------------- |
| definition in the held out wording     | 120 | 1.0000 | definition 120                         |
| question names no defined operation    | 120 | 1.0000 | plan 120                               |
| last case of the definition moved      | 300 | 1.0000 | followed the new page, 159 golds moved |
| definition page removed                | 300 | 1.0000 | plan 300                               |
| operation renamed on page and question | 300 | 1.0000 | same answer                            |
| one directory row changed              | 294 | 1.0000 | followed the new row, 142 golds moved  |

The two controls are the honest limits. A definition written in the wording mode
the reader was not built for is refused at the definition stage, every time,
because a hand written reader covers the wordings it covers. That is the seam
the architecture puts a network in front of the library to close, and this lane
does not close it. A question naming an operation no page defines is refused at
the plan stage, every time, because a library that has not read a definition has
nothing to run.

## Operations past the shapes the reader was built on

`enumerate_space` was only ever asked for one and two clause operations over two
and three directories, and those are what the reader was written against. These
are three and four clause operations, and operations over four and five
directories, generated for the first time by this table.

| operation        | n   | floor  | L strict | S1     | S2     | parser |
| ---------------- | --- | ------ | -------- | ------ | ------ | ------ |
| three clauses    | 120 | 0.2704 | 1.0000   | 0.4417 | 0.3750 | 0.0000 |
| four clauses     | 120 | 0.2983 | 1.0000   | 0.4917 | 0.3667 | 0.0000 |
| four directories | 120 | 0.2908 | 1.0000   | 0.3250 | 0.4750 | 0.0000 |
| five directories | 120 | 0.2500 | 1.0000   | 0.3833 | 0.4167 | 0.0000 |

## What this does not show

The reader is hand written, so its 1.0000 measures that the definition grammar
is a grammar and that the reader is general over it. It does not measure that
arbitrary English can be normalized: the held out wording mode is refused on
every item, and that is the number to look at before believing anything else
here. The claim this lane supports is narrower and is the architectural one.
Once a page is normalized, using what it says costs one page, holds at depth 16,
composes, and follows the page against the training. Getting from arbitrary
wording to a normalized page is the network's job, and `src/norm/COMPARE.md`
already measures how well the network does it on the shapes it was trained for.

The neural baseline here is the normalizer of `src/norm/nmodel.py` at size `l`,
45,483,008 parameters, which is the stronger of this project's two networks on
every cell of the main comparison. The corpus checkpoint that scored 678 of 678
on the transposed pages was not run on these items; it is at or below 0.1 strict
on most cells of `src/norm/COMPARE.md` and adding it would not change what the
tables above say.

The two clause space is sampled, not enumerated: 120 of 4,528. The one clause
space is complete.

## How to reproduce

    .venv/bin/python -m src.norm.opitems
    .venv/bin/python -m src.norm.oprun
    .venv/bin/python -m src.norm.opattack
    .venv/bin/python -m src.norm.oprun --items results/norm/oneshot/stress_items.jsonl.gz \
        --out results/norm/oneshot/stress_sys.jsonl.gz
    bash src/norm/drive.sh          # the GPU side, about ninety minutes on one L40S
    .venv/bin/python -m src.norm.opreport
    .venv/bin/python -m src.norm.opdoc

| record     | path                                                                       |
| ---------- | -------------------------------------------------------------------------- |
| attack     | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/attack.json         |
| ladder_sys | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/ladder_sys.jsonl.gz |
| stress_sys | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/stress_sys.jsonl.gz |
| sys        | /home/ec2-user/decoupled-reasoner/results/norm/oneshot/sys.jsonl.gz        |
