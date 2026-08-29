# The diversity corpus

A training corpus built to remove four measured ceilings on the 350M
checkpoint. Every number below is read from
`s3://decoupled-reasoner-009398924577/data/corpus/v1/manifest.json`, which is
written by `python -m src.corpus.report` from the corpus files themselves.
Nothing is trained here.

## Why it exists

Three findings, all on `rlsimple-503-921`, say the checkpoint reproduces its
training distribution and does not generalise past it.

Sentence frame. A renderer ablation (`src/disc/TEMPLATE.md`, commits 7b94a2f
and fab864f) put forced-choice `substitution_rule` at 0.970 in the trained
idiom and 0.015 to 0.045 in three other ordinary English idioms, against a
0.200 chance floor. On a single-document chain task a renderer sharing no
content word with the trained idiom scored 0.840, and one keeping every
content word while changing only the sentence frame scored 0.030. Nouns cost
0.13, sentence shape costs 0.94.

Plan length and symbol count. Reading emitted plans (commit 20295e2) found step
count tracking the question to three and then saturating, so a depth-eight
question got a three-step plan, and novel composition failing by writing the
first operator symbol twice where gold named two. Operands, ordering and
register wiring were correct. `src/opgraph/data.py:training_examples` draws
depth from `rng.choice([1, 2, 3])` and `src/opgraph/invent.py:novel` is the
only generator that ever forces two symbols, so those are the training
distribution's edges and the model sits on them.

Relation type. Three relation types never seen in training scored at or below
chance on balanced scoring: `inverse_table` 0.107 against 0.251, `chain_rule`
0.008 against 0.334, `band_rule` 0.313 against 0.334, while a fifty line regex
scored 0.98 to 1.00 on identical items.

Each of those is an edge of the training distribution. This corpus moves the
edges.

## What is in it

Four components, in separate files, never pooled in any count.

`relation` is the main body: sixteen relation structures crossed with 768
sentence frames. A structure in `src/corpus/relations.py` emits facts and
questions as records with no prose in them, and a frame in
`src/corpus/frames_default.py` decides only how those records are spelled. The
separation is what makes the gold answer for a seed the same in every frame,
which the manifest checks rather than assumes.

`plan` is operator worlds from `src/opgraph/invent.py` with plans of 1 to 48
steps using 1 to 5 distinct operator symbols. Both the whole-plan target and
the stepwise target are written.

`mathgen` is invented formal systems from `src/mathgen/cli.py`, which runs its
own verification and returns the assertion counts with the universe.

`external_frames` is `src/frames/`, the frame generator that landed while this
was being built, over the three `src/skillacq/simple.py` families it covers.

## The four axes

### Sentence frame

A frame is a point in a product of shape choices crossed with a lexicon:

    statement_mode   passive_decl, conditional, mapping, table_row,
                     imperative, relative_clause
    key_position     key_first, value_first
    question_form    wh, imperative, cloze, inverted
    scope_position   scope_first, scope_last
    lexicon          routing, assembly, transit, ledger, signal, clinic,
                     depot, abstract

That is 6 x 2 x 4 x 2 x 8 = 768 frames. The first four axes move the shape of
the sentence; the lexicon moves its words. Both are varied so the two are not
confounded, which is the mistake the original ablation could not rule out
because its renderers were hand written and chosen to be lexically distant.

The same rule, in four of the modes:

    passive_decl      A kayvor request is handled by the milzel desk.
    conditional       If an incoming request is kayvor, then the milzel desk
                      takes it.
    table_row         kayvor    milzel
    relative_clause   The desk that handles a kayvor request is the milzel desk.

The same question, in four forms:

    wh          A kayvor request arrives at the Brasol office. Which desk
                handles it?
    imperative  Name the desk that handles a kayvor request at the Brasol
                office.
    cloze       At the Brasol office, a kayvor request is handled by the ____
                desk. Give the missing word.
    inverted    For a kayvor request at the Brasol office: which desk?

`src/frames/` supplies a second, independently designed bank of 12 shapes over
its own lexicons. It is not loaded through the seam in `src/corpus/frames.py`
because its `Frame` renders three families through `pages_<family>` methods
while the corpus renders sixteen structures from prose-free records, and the
two interfaces do not meet. It is used as its own component instead, so the
corpus carries both banks and the manifest reports them separately.

### Plan length

The `plan` component runs to 48 steps. The `transitive` and `modular_apply`
relation structures also run to 48, and they are the vehicle for long plans on
the relation side because their question names one scope however long the walk
is: plan length is varied without varying prompt length with it. The multi-page
chains (`chain_rule`, `inverse_chain`, `weighted_chain`) stop at 6, because
their question has to name every stage and a depth-48 chain question would be
longer than everything else in the corpus.

One constraint is inherited, not chosen. `src/opgraph/plan.py` sets
`MAX_STEPS = 32` and `parse_plan` refuses anything longer;
`src/opgraph/run.py` sets `MAX_PLAN_STEPS = 24` for the stepwise scheduler.
Plans past 32 steps serialize and execute correctly and the shipped parser
rejects them. `src/corpus/plans.py:verify_roundtrip` reports this per length,
and the self-test confirms it: every length up to 32 parses and runs, and 40
and 48 do not. Raising `MAX_STEPS` is a one-line change in a file this corpus
does not own, and it has to happen before anything past 32 steps can be scored.

### Distinct symbols per plan

Plans use 1, 2, 3, 4 and 5 distinct operator symbols. A world holds two
invented binop glyphs, and `src/opgraph/plan.py:BUILTIN_STEPS` makes `add`,
`sub` and `mul` callable in every world, so five arity-two symbols are
available without inventing anything the executor does not already accept.
`src/corpus/plans.py:build_tree` forces each requested symbol to appear at
least once, and the realised count is checked on the built tree rather than
assumed from the request.

### Relation type

Sixteen structures. Twelve are trained on and four are held out.

    trained     substitution, threshold, exception_rule,
                inverse_table, chain_rule, band_rule,
                inverse_chain, transitive,
                lookup_then_band, band_then_lookup,
                weighted_chain, modular_apply

    held out    two_key, exclusion, priority_list, agreement

The first three trained ones are the families the checkpoint already saw. The
next three are the measured generalisation failures, and they are in training
because they are the named ceilings.

That has a consequence worth stating plainly. `src/falsify/probe.py` holds
`inverse_table`, `chain_rule` and `band_rule` outside `SIMPLE_FAMILIES`
deliberately, because they are the untrained-relation probe. Training on this
corpus retires that probe: those three become in-distribution and the falsify
lane's relation-type arm stops measuring generalisation. The four held-out
structures replace it, and they were chosen to be structurally new rather than
new in wording: a two-coordinate grid, a negation, an ordered first-match-wins
rule set, and a precedence conflict between two pages. None of the twelve
trained structures has any of those shapes.

## The checks

Every check is in `src/corpus/audit.py`, run by `src/corpus/selftest.py` before
generation and by `src/corpus/report.py` over the generated files.

Gold agreement across frames. `audit.gold_agreement` requires every frame to
give the same gold answer for the same seed, family and question id. This is
what says the frame bank varies the wording and nothing else; a mismatch would
mean a frame changed the task and any accuracy difference across frames would
be uninterpretable.

The mechanism that makes it hold is worth naming, because it is where the
earlier bug was. Two reserved word sets do two different jobs. Each frame's own
reserved set is read off that frame's own templates, filled with sentinels, and
is what the collision check tests against. The union over the whole bank is
what the invented-word draw avoids. Drawing against the union rather than the
per-frame set is deliberate: a rejection that fired in one frame and not
another would advance that frame's random stream by a different amount and the
two frames would then draw different invented words for the same seed. Drawing
against the union keeps the stream identical everywhere, so gold agreement
holds by construction, and the per-frame check still bites because each frame's
set is a subset of the union.

Necessity. The four exclusions are
`src/disc/renderers.py:chain_violations`'s, with the same predicate bodies:
`answer_in_question`, `answer_is_start`, `answer_is_intermediate`,
`stages_not_distinct`. They run in two stages, counted separately. The
structural stage runs on the records before a frame is chosen and drops
individual questions; running it on rendered text would leave each frame with a
different surviving question set, which is the move
`src/disc/renderers.py:chain_problems` makes and says why. The episode stage
runs on the rendered text and drops whole episodes.

Shortcuts. Six value-blind readers (`most_frequent_symbol`, `copy_start`,
`depth_one_stop`, `random_candidate`, `most_frequent_nonce`, `last_nonce`) and
one page reader (`keyword_nearest`). The blind ones must sit at or below
chance. They are scored over independent seeds, not over rendered episodes: a
blind reader does not look at the wording, so one seed rendered in eight frames
is one item and counting it eight times would shrink the interval eightfold and
turn ordinary sampling noise into a finding. A reader is called above chance
only when its Wilson lower bound clears the floor.

The page reader is expected to score, because the task is to read the page. It
is reported so that a frame cannot look safe merely because the attack was
written for a different wording, which is how `src/disc/minrepro.py`'s
`keyword_nearest` behaves outside the routing idiom. The pattern comes from the
frame itself through `frame.lookup_regex`, and the self-test checks that every
one of the 768 patterns matches its own frame's rule line.

Token length parity. Prompt and page token lengths are held approximately
constant across frames, per family. Parity is required across frames inside a
family and not across families: two families legitimately need different
amounts of page, and pooling them would hide the thing the check is for, which
is a frame running systematically longer than its siblings on the same task.
Two padding knobs do it, both drawing from banks shared by every frame: a
sentence-at-a-time note bank on the page side, and a neutral lead-in bank on
the question side. Without them a table-row frame and a relative-clause frame
differ in page length by about half again, and `src/rl/env.py:load_tasks` drops
any task over `max_prompt_tokens`, so a long frame would silently lose its
longest items and stop being comparable with the others.

Answer source. Every question carries `stated_in_a_chapter` or
`derived_by_computation`, labelled by reading the served pages rather than by
asking the generator: an answer that stands as a whole token somewhere in the
served prose is answerable by copying and one that does not is not. That is the
same rule `src/mathgen/exercises.py:answer_source` uses, and mathgen questions
carry both labels so the two can be compared. Pooling the two hid a result on
this project, so no count in the manifest crosses the split.

Two deliberate moves keep the split from collapsing to the generators'
defaults. `weighted_chain` and `modular_apply` are the only relation structures
whose answer is not written on a page, and they are given four times the seed
count of the other structures; without that they would be a sixth of the
component. Half the mathgen universes are generated with
`answer_source="derived"`, because mathgen's own mix is about four fifths
stated and inheriting it would mean reporting a stated number with a derived
tail.

Leakage. Two named checks.
`audit.seed_disjointness` is a reserved seed range interval test over the seeds
actually written, against every namespace another evaluation set owns
(`RESERVED_SEED_RANGES`).
`audit.hash_disjointness` is a sha256 intersection over question-and-answer
content hashes, between the training band, the held-out band, and the
evaluation sets regenerated from their own seeds by
`report.evaluation_set_hashes`.
The hash check exists because a seed split is not an item split: two seeds can
draw the same short question with the same answer, and when they land on
opposite sides the held-out item is leaked whatever its seed says. Both checks
found real defects on the first build, a held-out seed block that ran past the
end of its range and three items shared between the two bands, and both were
fixed rather than reported around. `python -m src.corpus.cli deleak` is the
pass that removes shared items from the held-out side.

## Seed layout

    train    [300_000_000, 340_000_000)
      relation  300_000_000    plan  315_000_000
      mathgen   320_000_000    external  330_000_000

    heldout  [350_000_000, 351_000_000)
      relation  350_000_000    plan  350_300_000
      mathgen   350_400_000    external  350_500_000

Reserved elsewhere and avoided: 900_000 to 1_000_000 (latentret eval),
1_000_000 upward (pointer copy bench), 2_900_000 to 3_150_000 (falsify
conditions) with its twin and wrong-textbook offsets, 4_100_000 (dependency
sweep), 5_000_000 and 5_500_000 (falsify template vocabulary), 700_000_000
(audit twin worlds), 900_000_000 to 906_100_000 (opgraph eval worlds), and
1_000_000_000 upward (worldgen held-out index).

## Held-out sets

Four, all disjoint from training by seed and by content hash:

  - the relation held-out band, spanning every eighth frame at all sixteen
    structures, which is the only place the four held-out structures appear
  - the plan held-out band, over the same step and symbol grid
  - the mathgen held-out band
  - the `src/frames/` test frames, which are its own `split_frames("both")`
    test side plus the bridge frames that are new on exactly one axis; the
    training band uses only its train side, so its lexicon and shape split
    survives

## What a training run should do with it

Read the files with `src/rl/env.py:load_tasks`, which is the shape they are
written in. `n_context` is 0 throughout, so pages arrive through retrieval;
set it higher to put them in the prompt instead.

Do not pool. Report every accuracy per family, per frame axis, and per
`answer_source`, and never as one number across components. The manifest is
laid out to make that the easy thing to do.

Train the plan arm on both targets. The whole-plan target is the one that
saturated at three steps; the stepwise target is the form
`src/opgraph/data.py:step_prompt` documents as removing the length prior. A
corpus meant to lift a length ceiling should carry the evidence for both, and
which one lifts it is the question.

Raise `src/opgraph/plan.py:MAX_STEPS` before scoring anything past 32 steps, or
those items will be counted as parse failures rather than as long plans.

Retire the relation-type arm of the falsify lane and point it at the four
held-out structures instead. After this corpus, `inverse_table`, `chain_rule`
and `band_rule` are in distribution and a score on them measures fit, not
generalisation.

The frame axis has a control built into it that is worth using. `src/frames/`'s
`split_frames` holds out whole lexicons and whole shapes, so its test side
asks a sharper question than the corpus's own held-out band does: whether a
sentence geometry never seen in training is answerable at all. Score that
separately from the corpus held-out band.

## Files

    src/corpus/relations.py       sixteen relation structures, prose free
    src/corpus/frames_default.py  the 768 frame bank
    src/corpus/frames.py          the seam that chooses a frame bank
    src/corpus/external_frames.py the src/frames component
    src/corpus/lexicon.py         per frame invented vocabulary
    src/corpus/plans.py           long and wide plans over operator worlds
    src/corpus/build.py           episode assembly
    src/corpus/audit.py           necessity, shortcuts, parity, leakage
    src/corpus/cli.py             generation and the de-leak pass
    src/corpus/report.py          the manifest
    src/corpus/selftest.py        the checks, before generation
