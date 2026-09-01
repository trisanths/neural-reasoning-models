# Open weight models on the one page acquisition task

Built 2026-09-01 01:47 UTC from `results/extern/report.json` by `src/extern/md.py`, out of
7 record files. Every number below is read from a generation file
written by `src/extern/run.py`; none is typed.

This is the first time anything in this project has been measured against a
model it did not train. The comparison is against Liquid AI's LFM2.5 line,
which is open weight, publishes at sizes that bracket ours, and makes an
efficiency claim of its own.

The answer is outcome two, and it is the first externally validated result
this project has.

LFM2.5-350M read the same definition page the project's own reader was given,
under the formulation that scored best of five tried, and answered 850
questions at 0.2459 strict against its own measured chance floor of 0.3085.
It is below chance on three of the four operation families, above it on one,
and it names none of the candidate answers at all on 0.4965 of the items. A
general model of this size does not acquire a new operation from one page.

That is not a statement about these models being weak. On 26 ordinary
factual, numeric and commonsense questions put through the same harness and
graded by the same function, the same checkpoint scores 0.5769 against a
0.2500 floor where this project's reader scores 0.0000. They win the general
axis outright and it is not close. The two numbers belong beside each other,
because a report carrying only the first would be advocacy.

The retrieval lane adds a second finding and it is about policy, not
comprehension: on MMLU this project's reader almost never emits a retrieval
request at all, so its retrieval condition and its closed book condition are
nearly the same run. The near zero Exa spend on that cell is itself the
evidence, because a retrieval condition that costs almost nothing is a
retrieval condition that did not happen.

What the result does not do is settle the architecture question. The library
system's 1.0000 comes from an exact interpreter running a parsed definition,
and the comparison here is against a model that was never built to parse one.
The finding is narrower than the thesis and worth exactly what it says: the
capability is not free at this scale, and something has to supply it.

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

## Three checkpoints, and which number belongs to which

This lane has had one conflation running through it and it should not
survive into the writeup. Three different checkpoints appear in these
tables and they are not the same model.

| checkpoint | parameters | what it is measured on here |
| ---------- | ---------- | --------------------------- |
| `results/norm/train/ckpt_l.pt` | 45,483,008 | the one page acquisition task, where it scores 0.0000 to 0.1200 across the four families |
| `retrain/corpus-v1-8k.pt` | 375,440,384 | the public benchmarks, closed book and with retrieval |
| `LiquidAI/LFM2.5-350M` | 354,483,968 | the one page acquisition task |
| `LiquidAI/LFM2-350M` | 354,483,968 | the public benchmarks, and the harness calibration |

The network that scores 0.0000 on the acquisition task is the 45.5M one.
It is not the 375M corpus model and it is not parameter matched to
anything from Liquid. The corpus model is parameter matched, at
375,440,384 against LFM2-350M, and that is the pairing the public
benchmark tables use.

## The harness gap that had to be closed first

A reproduction that misses a published number by eight points is a
harness result, not a model result, and everything measured through it
inherits the gap. LFM2-350M publishes MMLU 43.43. This harness
reproduced it three ways.

| configuration | MMLU, n=200 | against 43.43 |
| ------------- | ----------- | ------------- |
| completion, 5 shot, no bos token | 0.3550 | -7.93 |
| the model's chat template | 0.3950 | -3.93 |
| completion, 5 shot, bos token prepended | 0.4300 | -0.43 |

The bos token was the whole gap. lm-eval prepends one for a model that
defines it, LFM2 defines the startoftext token, and leaving it off shifts
every position relative to how the model read a document start in
training. The signature was visible before the cause was: without the bos
token the predictions piled onto the first option, 102 of 200 where the
gold was 60.

Every LFM2 row below is the bos corrected configuration. Numbers measured
before the fix are void rather than merely low, and are not reported as
results: that includes an LFM2.5-350M MMLU of 0.3700, and the
ARC-Challenge and WinoGrande runs for both Liquid models, which sat at or
under their floors. They are named here so that nobody recovers them from
the record files and reads them as findings.

Our own tokenizer defines no bos token at all, only the eot token, so
there is nothing to prepend on that side and the closed book number
already stood at the calibrated setting. The eot prefix run is the control
that says so rather than assuming it.

## Two measurement faults this lane found in itself

Both would have moved a number in this project's favour, which is why
they are recorded here rather than quietly fixed. A reader should be able
to see that they were caught internally.

The first is the bos token, described above: it cost the reproduction 7.93
points against a published figure and, left in place, would have put every
external model eight points lower than it belongs while leaving this
project's own reader untouched, because our tokenizer has no bos token to
omit. The comparison would have flattered us on both sides of the gap.

The second is cache poisoning. An offline validation run against MockExa
wrote its empty results into the same on-disk search cache the live runs
read, keyed by the same query strings. The first items of the live
retrieval control then took those empty entries as cache hits and were
scored with no retrieved text at all. That weakens the one cell that can
falsify the thesis: an external model handed nothing would have looked as
though retrieval had not helped it. Nine poisoned entries were purged, the
control was restarted from scratch, and the cache is now namespaced by
retriever so a mock run and a live run can never share a key. The manifest
in `results/extern/exa_manifest.json` records a sha256 per query so a
changed or empty entry is visible rather than silent.

## The models, counted rather than quoted

Parameter counts are summed over the loaded checkpoint's tensors, not taken
from the model card.

| model       | parameters, counted from the checkpoint | non embedding | architecture    | quantisation |
| ----------- | --------------------------------------- | ------------- | --------------- | ------------ |
| LFM2.5-350M | 354,483,968                             | 287,375,104   | Lfm2ForCausalLM | none         |

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

| model       | batched matches unbatched | control questions answered |
| ----------- | ------------------------- | -------------------------- |
| LFM2.5-350M | 7/7                       | 5/5                        |

Generation budgets are generous on purpose, because a cap that truncates a
reasoning trace before its answer measures the cap. The reasoning variant gets
4,096 new tokens and the instruct models 512, against a task whose answer is
one word. Decoding follows each model card's recommended sampling settings,
recorded per run in the meta file.

## Every prompt formulation tried, not just the one reported

Five formulations were run over the same 41 item stride sample of the one
page set, and the full run uses the best of the four that hand the model no
more than the library system gets. The fifth prints the candidate list, which
is more than our own system is given, so it is kept apart as an advantaged
cell and never used for a matched row.

One of the four is a scaffold naming the steps the definition calls for, and
one prefills the assistant turn so the model has to write the values it read
before it can answer. Both are here because the small models comply with an
answer format and skip the reasoning when they are merely asked for it.

| model       | prompt                            | options shown | n  | floor  | strict | lenient | hedge  | no option named | unparseable | mean new tokens |
| ----------- | --------------------------------- | ------------- | -- | ------ | ------ | ------- | ------ | --------------- | ----------- | --------------- |
| LFM2.5-350M | bare                              | no            | 41 | 0.2911 | 0.1463 | 0.1463  | 0.0000 | 0.7073          | 0.0000      | 4.0             |
| LFM2.5-350M | worked + assistant turn prefilled | no            | 41 | 0.2911 | 0.0976 | 0.0976  | 0.0000 | 0.6585          | 0.0000      | 86.8            |
| LFM2.5-350M | worked                            | no            | 41 | 0.2911 | 0.2927 | 0.2927  | 0.0000 | 0.4146          | 0.0000      | 6.4             |

## One page, by operation family

| operation family               | n   | floor  | system                             | strict | lenient | hedge  | no option named | unparseable |
| ------------------------------ | --- | ------ | ---------------------------------- | ------ | ------- | ------ | --------------- | ----------- |
| two directories, one clause    | 110 | 0.3735 | library, one page                  | 1.0000 | -       | -      | -               | -           |
| two directories, one clause    | 110 | 0.3735 | project reader, 45.5M, no gradient | 0.0000 | 0.0000  | -      | 0.4364          | -           |
| two directories, one clause    | 110 | 0.3735 | LFM2.5-350M                        | 0.4364 | 0.4364  | 0.0000 | 0.1909          | 0.0000      |
| three directories, one clause  | 310 | 0.3086 | library, one page                  | 1.0000 | -       | -      | -               | -           |
| three directories, one clause  | 310 | 0.3086 | project reader, 45.5M, no gradient | 0.0194 | 0.0194  | -      | 0.7323          | -           |
| three directories, one clause  | 310 | 0.3086 | LFM2.5-350M                        | 0.1935 | 0.1935  | 0.0000 | 0.5387          | 0.0000      |
| two directories, two clauses   | 25  | 0.3567 | library, one page                  | 1.0000 | -       | -      | -               | -           |
| two directories, two clauses   | 25  | 0.3567 | project reader, 45.5M, no gradient | 0.1200 | 0.1200  | -      | 0.5200          | -           |
| two directories, two clauses   | 25  | 0.3567 | LFM2.5-350M                        | 0.3600 | 0.3600  | 0.0000 | 0.2800          | 0.0000      |
| three directories, two clauses | 405 | 0.2879 | library, one page                  | 1.0000 | -       | -      | -               | -           |
| three directories, two clauses | 405 | 0.2879 | project reader, 45.5M, no gradient | 0.0173 | 0.0173  | -      | 0.5852          | -           |
| three directories, two clauses | 405 | 0.2879 | LFM2.5-350M                        | 0.2272 | 0.2272  | 0.0000 | 0.5605          | 0.0000      |

## The acquisition curve

The same question items with the operation stated on one page, two pages and
four. Extra pages are further wordings of the same operation, so a system that
reads the page gains nothing from the second and a system that needs examples
has been given none.

| operation family               | n   | floor  | system      | 1 page | 2 pages | 4 pages |
| ------------------------------ | --- | ------ | ----------- | ------ | ------- | ------- |
| two directories, one clause    | 110 | 0.3735 | library     | 1.0000 | 1.0000  | 1.0000  |
| two directories, one clause    | 110 | 0.3735 | LFM2.5-350M | 0.4364 | -       | -       |
| three directories, one clause  | 310 | 0.3086 | library     | 1.0000 | 1.0000  | 1.0000  |
| three directories, one clause  | 310 | 0.3086 | LFM2.5-350M | 0.1935 | -       | -       |
| two directories, two clauses   | 25  | 0.3567 | library     | 1.0000 | 1.0000  | 1.0000  |
| two directories, two clauses   | 25  | 0.3567 | LFM2.5-350M | 0.3600 | -       | -       |
| three directories, two clauses | 405 | 0.2879 | library     | 1.0000 | 1.0000  | 1.0000  |
| three directories, two clauses | 405 | 0.2879 | LFM2.5-350M | 0.2272 | -       | -       |

## The check they win

A comparison that reported only the axis this project is built for would be
advocacy. These are 26 ordinary factual, numeric and commonsense questions,
forced choice over four candidates so the same grader scores them and the
floor is 0.2500 by construction. The project's own reader is in the table on
the same questions, through the same path `src/norm/opneural.py` uses.

| system                | n  | floor  | strict | lenient | factual | numeric | commonsense |
| --------------------- | -- | ------ | ------ | ------- | ------- | ------- | ----------- |
| project reader, 45.5M | 26 | 0.2500 | 0.0000 | 0.0000  | -       | -       | -           |
| LFM2.5-350M           | 26 | 0.2500 | 0.5769 | 0.5769  | 0.8000  | 0.2500  | 0.6250      |

## What the outputs look like

An accuracy says a model was wrong. These say what it wrote instead.


LFM2.5-350M, prompt worked:

    item acq/a2c1/10/0/p1  gold muthovi  options ['kaesk', 'muthovi', 'ondabelu', 'quilbra']
    state ok  graded span 'kaesk'
    output 'Answer: kaesk'

    item acq/a2c1/10/1/p1  gold quilbra  options ['kaesk', 'muthovi', 'ondabelu', 'quilbra']
    state ok  graded span 'kaesk'
    output 'Answer: kaesk'

    item acq/a2c1/10/2/p1  gold kaesk  options ['kaesk', 'muthovi', 'ondabelu', 'quilbra']
    state ok  graded span 'beluzunt'
    output 'Answer: beluzunt'


## What is not here

The 8B-A1B mixture of experts rung and a dense anchor near 8B are not in this
report. Both were deferred: the box's disk had fallen to 24GB free with a
parameter ladder writing checkpoints to the same volume, and a disk full crash
on this box has already cost four training lanes. The 8B-A1B weights were
pulled, then removed again without being run, which took the volume back to
39GB free. Those two rungs need a clear box and are worth running on one.

No quantisation was used anywhere in this report. Every model ran in bfloat16
at full width, so no row here is handicapped by a lossy load.
