# The capability primitive suite

The central experiment trains the same acquisition machinery at descending
sizes and asks, at each size, which capability fails first. One pass rate per
size cannot answer that. This suite is the instrument that can: seven
faculties, each with its own generator, its own scorer and its own argument
for why the other six are not needed to pass it, so a result reads "at 500M,
abstraction construction breaks while retrieval planning and verification
survive" rather than "at 500M, 0.21".

Code lives in `src/primitives/`. Every item is generated procedurally from a
seed, every answer is checked mechanically, and no model judges anything.

## The seven

| faculty | module | what the model is asked for | what is scored |
|---|---|---|---|
| intent understanding | `p1_intent.py` | the structure of a messy request, never its execution | five extracted fields against a generated ground truth |
| missing-capability recognition | `p2_gap.py` | whether the manual is complete, and structurally what is absent | detection, gap type, and which plan step fails, apart |
| information acquisition | `p3_acquisition.py` | a source tier and a search string | whether that query retrieves the needed page under the training retriever |
| abstraction construction | `p4_abstraction.py` | a rule induced from cases, applied under a renamed surface | accuracy against a copy baseline on the same items |
| composition depth | `p5_composition.py` | a chain, a conjunction, and a program of separately taught parts | three curves over k, raw and step-conditioned |
| temporary knowledge | `p6_memory.py` | a fact carried across a long episode, and not carried past its end | retention by distance, intrusion, and leak, apart |
| verification and action | `p7_verification.py` | a verdict on a supplied candidate, then a final answer | detection and correction, apart |

## Independence, faculty by faculty

Each test has to be passable when the other six are weak, or a failure cannot
be located. Each module's docstring carries its own argument in full; this is
the summary of how each one is kept clean.

| test | how the other faculties are kept out |
|---|---|
| intent | every field is a one-step restatement of one span; the menu is supplied, so nothing is induced; the chunk list is empty, so nothing is retrieved; contradictions are textual with both sides present, which is a different object from a gap in the model's own procedure; the two conflict arms are balanced exactly, so always reporting no contradiction scores the option count and not the arm split |
| gap | the plan is supplied and numbered; nothing is applied or computed; every page is in context; the problem stem is byte-identical between the blocked and unblocked version of a seed; page count is held at six in both arms |
| acquisition | the score reads the query, not an answer, so reading cannot inflate it; the headline variant is one hop; the two-hop variant is reported apart and flagged as contaminated by reading; which tier holds the answer rotates over three of the four, so a constant reply wins a third of the items at most |
| abstraction | one comparison and one label, never arithmetic; the transfer condition adds exactly one renaming through an explicit legend, and the same-surface condition is printed beside it so that step's cost is visible |
| composition | every constituent step is probed on its own over the same tables, and the curve is reported both raw and restricted to items whose every step that model answered correctly alone |
| memory | one stated value retrieved by one lookup; filler segments carry the decoy options so the answer is never the only number present; all five answer options appear in every arm |
| verification | the candidate is handed over, so the model never has to solve the problem to check it; the check is one clause read against one stated property |

## The no-shortcut guard

Three heuristics stand in for the ways an item can be answerable without the
faculty it claims to test, and a generator rejects any item they solve:
answering from the question stem alone, answering with the most frequent
candidate in the prompt, and answering with the candidate that shares the
most words with the stem. `common.guard_report` runs all three.

The acquisition primitive runs the strongest version of this. The catalogue
is indexed by handling code and never by common name; the page that answers
carries only the code; a decoy page repeats the common name at length.
Issuing the request verbatim ranks the decoy first, which generation checks
on every item, and the surviving copy baseline is printed next to the model's
score.

## Two channels, and why both are needed

Producing an answer and preferring the right one are different abilities, and
a small checkpoint can lose the first while keeping some of the second. The
suite scores both and never merges them.

The generation channel reads what the model writes. Graders fall back to
reading the whole reply when no field headers appear, and binary verdicts go
through a synonym list, so a model trained to emit a bare answer after the
answer marker is not scored zero for format. Strict field presence is still
counted and printed as the parse rate.

The forced-choice channel scores each item's single-choice fields by
likelihood over the option texts, the way the held-out suite already scores
multiple choice. Picks use the summed negative log likelihood divided by the
option's token count. Without that division several fields here have a
correct option that is systematically the longest, and the pick goes to the
shortest option almost every time: the first run put two fields at exactly
zero out of forty for that reason alone. The unnormalised picks come from the
same forward pass and are kept in the JSON under
`forced_choice._unnormalised`, so a reader can see where length is doing the
work.

The query half of information acquisition stays generation only. Writing a
search string is production and cannot be posed as a pick.

## Two modes at every size

Every primitive is measured twice. In `isolated` mode the other six faculties
are supplied by oracle around the one under test. In `integrated` mode those
oracles are withdrawn and the model produces its own upstream inputs. The
distance between the two curves is the architecture and training gap. The
point where even the isolated curve fails is evidence of a capacity gap.

## Three kinds of composition

They may have different scaling laws, so they are never pooled.

Sequential depth follows one stated relation k times through an eight-cycle,
so the k-step answer differs from every shorter answer and stopping early
lands on a wrong candidate rather than on nothing.

Relational breadth integrates k simultaneous clues. Generation checks that
all k together single out one entry and that dropping any one leaves at least
two, so partial integration scores at chance rather than nearly right.

Novel composition applies k procedures each taught in its own lesson and
never shown combined. A model can memorise every part and fail the whole,
which is why this is the acquisition test proper.

The depth a curve is credited with is the last k whose chance-adjusted
interval clears a margin fixed at 0.15 in `p5_composition.DEPTH_MARGIN`, not
merely the last k that clears chance. A ninety-five percent interval fires on
one cell in forty by luck, and across three kinds, five depths and eight
stand-ins that is a depth of one reported for a stand-in with no composition
at all.

## The causal rescue matrix

Independent tests are necessary and not sufficient. A failed integrated
episode smears its failure downstream, so the model that never parsed the
brief also never found the chapter and its retrieval looks broken too.
`episode.py` builds one episode that needs all seven faculties and replaces
each one in turn with an oracle that supplies what that faculty would have
produced and nothing further. The composition oracle hands over intermediate
results, and generation asserts that the final answer appears in no injected
block. Lifts are paired across identical items, and the matrix reports how
many episodes each oracle flipped in each direction rather than a difference
of means.

The matrix runs on both channels. A model that writes nothing produces an
all-zero generation matrix, which locates nothing, and that is exactly the
model the forced-choice matrix exists for.

## Calibration

A benchmark never shown to respond to the thing it measures is decoration.
`fakes.py` builds scripted stand-ins with exactly one faculty each, at chance
in the other six and well formed throughout, and `tests/test_calibration.py`
pins the square matrix they fill: every diagonal cell clears the blind
stand-in by more than 0.30 and every off-diagonal cell stays within 0.25 of
it. A stand-in whose composition ability is capped at depth d reports k* = d
on all three curves. A stand-in that copies the nearest lesson case earns
exactly no transfer margin. A stand-in missing only composition is rescued by
the composition oracle and by no other.

Three degenerate replies are pinned as well. Silence scores zero rather than
chance and drives the parse rate to zero. Answering no to everything sits at
exactly chance detection with a false-alarm rate of one. Listing every
candidate counts as no choice at all.

## Reading a formatless model

The graders fall back to reading the whole reply when a model writes no field
headers, and binary verdicts go through a synonym list, because a checkpoint
trained to emit a bare answer after the answer marker would otherwise score
zero for format rather than for faculty. Strict field presence is still
counted and printed as the parse rate, and the report opens with a format
warning when that rate is low, saying plainly that the profile is a floor
rather than an estimate.

## Known limits

Source selection on the recursive acquisition variant has a constant gold
tier, because a two-hop chase always starts at the ledger. Read that cell as
whether the model names the ledger, and take the direct variant, whose gold
tier rotates, as the source-selection measurement.

Second-hop retrieval requires reading the served page, so it is contaminated
by reading ability. It is reported on its own line and never folded into the
acquisition headline.

The intent free-form grader used in integrated mode checks for key tokens in
each field, which a model can satisfy by copying spans of the request. The
menu form used in isolated mode has no such hole. The two modes are therefore
not directly comparable on that primitive, and only the isolated column
should be read as a clean measurement of extraction.

Chance rates are analytic where the answer is a pick from an enumerated set.
Where a score is a set overlap or a query, there is no analytic chance, and
the reference printed beside it is a measured baseline instead: the copy
baseline for acquisition, and the copy and majority baselines for
abstraction.

## Running it

    uv run python -m src.primitives.cli --ckpt runs/x/latest.pt \
        --tokenizer data/tokenizer_v2.json --out results/x \
        --n 40 --mode isolated --ks 1,2,3,4,5 --rescue-n 20

    uv run python -m src.primitives.cli --calibrate --out results/x

Decoding is sampled by default at temperature 0.7 with top-k 50. Greedy
decoding has produced false zeros on this project, so `--temperature 0` has
to be asked for and is recorded in the report when it is.

The runner takes any `predict(question, chunks) -> str`, which is the
`answer_fn` shape `src/evals/interactive.make_retrieval_answer_fn` already
returns, so anything wired for the interactive loop drops in unchanged and
nothing in `runner.py` imports torch.

## What this reuses

`src/skillacq/systems.py` supplies the invented vocabulary generator and the
rule-family shapes that every generator here builds on, and its
computation-free families in `simple.py` are the model for the threshold,
substitution and exception structures used in abstraction and verification.
`src/skillacq/procedures.py` is the model for the format-convention items.
`src/train/retrieval.py` supplies `BM25Index`, which is the acquisition
oracle, so what counts as retrievable is the project's own definition.
`src/rl/sampler.py` supplies the cached sampled decoder. `src/evals/mc.py`
loads checkpoints and `src/train/data.py` renders the world preamble, so
prompts match the training layout. `src/mathgen/interface.py` was read for
its level and ablation contract; the composition curves follow its idea that
a problem which still answers with its target chapter removed is not testing
that chapter, applied here as the gap primitive's ablation guard.
