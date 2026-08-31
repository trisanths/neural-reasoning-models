# Open weight models on the one page acquisition task

Built {built} from `results/extern/report.json` by `src/extern/md.py`, out of
{n_records} record files. Every number below is read from a generation file
written by `src/extern/run.py`; none is typed.

This is the first time anything in this project has been measured against a
model it did not train. The comparison is against Liquid AI's LFM2.5 line,
which is open weight, publishes at sizes that bracket ours, and makes an
efficiency claim of its own.

{verdict}

## What was asked of them

The items are `results/norm/oneshot/items.jsonl.gz`, unchanged: the same 850
one page questions per rung that `src/norm/ONESHOT.md` reports the library
system and the project's reader on. An item is a definition page for an
operation invented after any of these models was trained, the directory pages
it reads, and one question. The condition is the one the project's own reader
was put in: the page is in the context window, no gradient step is taken, and
nothing is fine tuned.

Grading is `src/norm/cmpwork/grade.py`, imported rather than reimplemented, so
the strict rule is the same function on both sides of every row. Strict is
exactly one candidate named and it is the gold one; naming two is wrong
however the first one falls. Lenient is the first candidate named. Both are
reported, with the hedge rate and the rate at which no candidate was named at
all.

Chance floors are the item's own option set, averaged over the items in the
cell, and no cell pools two operation families.

## A correction to the brief this lane was given

The brief described the network that scores 0.0000, 0.0194, 0.1200 and 0.0173
on the four families as a 350M network, which would have made LFM2.5-350M a
parameter matched comparison. It is not. Those numbers come from
`results/norm/train/ckpt_l.pt`, whose own checkpoint reports 45,483,008
parameters, 44,103,680 of them outside the embedding. The project does have a
350M class elsewhere, in `SPEC.md` and the `src/opgraph` and `src/disc` lanes,
but it is not the network in `ONESHOT.md`.

So LFM2.5-350M is not matched to the reader it is being compared with. It has
about 7.8 times the parameters. Every comparison below is therefore generous
to Liquid, which is the direction an external baseline should err in, and the
row labels say which number belongs to which parameter count rather than
implying a match that is not there.

## The models, counted rather than quoted

Parameter counts are summed over the loaded checkpoint's tensors, not taken
from the model card.

{t_models}

## The fairness gates

Two things had to pass before any benchmark number was kept.

Each model is prompted through its own `tokenizer.apply_chat_template`, so the
header is the model card's own jinja rather than anything written here, and
the rendered string of the first item is stored in each run's meta file. The
control check asks trivial questions through that same path and prints what
comes back, so a dropped header shows up as nonsense before the benchmark
rather than after.

The padding check matters more than it looks. LFM2 interleaves short
convolutions with attention, and a convolution reads its own left context, so
a left padded batch is exactly where this family could quietly differ from an
unpadded single. The same prompts were run both ways under greedy decoding and
compared.

{t_verify}

Generation budgets are generous on purpose, because a cap that truncates a
reasoning trace before its answer measures the cap. The reasoning variant gets
4,096 new tokens and the instruct models 512, against a task whose answer is
one word. Decoding follows each model card's recommended sampling settings,
recorded per run in the meta file.

## Every prompt formulation tried, not just the one reported

Four formulations were run over the same 213 item stride sample of the one
page set, and the full run uses the best of the three that hand the model no
more than the library system gets. The fourth prints the candidate list, which
is more than our own system is given, so it is kept apart as an advantaged
cell and never used for a matched row.

{t_selection}

## One page, by operation family

{t_oneshot}

## The acquisition curve

The same question items with the operation stated on one page, two pages and
four. Extra pages are further wordings of the same operation, so a system that
reads the page gains nothing from the second and a system that needs examples
has been given none.

{t_curve}

## The check they win

A comparison that reported only the axis this project is built for would be
advocacy. These are 26 ordinary factual, numeric and commonsense questions,
forced choice over four candidates so the same grader scores them and the
floor is 0.2500 by construction. The project's own reader is in the table on
the same questions, through the same path `src/norm/opneural.py` uses.

{t_general}

## What the outputs look like

An accuracy says a model was wrong. These say what it wrote instead.

{t_samples}

## What is not here

The 8B-A1B mixture of experts rung and a dense anchor near 8B are not in this
report. Both were deferred: the box's disk had fallen to 24GB free with a
parameter ladder writing checkpoints to the same volume, and a disk full crash
on this box has already cost four training lanes. The 8B-A1B weights were
pulled, then removed again without being run, which took the volume back to
39GB free. Those two rungs need a clear box and are worth running on one.

No quantisation was used anywhere in this report. Every model ran in bfloat16
at full width, so no row here is handicapped by a lossy load.
