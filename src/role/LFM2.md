# LFM2-350M has the same collapse, and English is not what fixes it

The 45M normalizer binds role to position on a held-out sentence mode, and
four interventions moved which convention it picked without moving whether it
picked one (`src/role/ROLE.md`). That result had a confound. Our checkpoints
are trained at about 5.24 target tokens per parameter against a compute
optimal 20, and the 375M corpus model reads MMLU at 0.2750 against LFM2-350M's
0.4300, so "a transformer reader cannot represent role independently of
position" and "our reader never saw enough English to generalise role marking
syntax" predicted the same table.

LFM2-350M kills the second one. It has 354,483,968 parameters, essentially the
size of our largest checkpoint, it is trained to convergence by someone else,
and it has never seen this corpus. Put on the same items it writes the roles
of a key-first rule sentence the right way round on 0.8805 of the pairs it
reproduces and a value-first one on 0.3479, against a 0.5 floor and a parser
that reads every cell at 1.0000. Four splits, six statement modes, five
shapes, greedy and sampled, two parsers, all the same direction. Ample English
does not buy a reader the ability to take role from what a rule sentence says
rather than from where the words sit in it.

That is the whole of what this measurement shows, and it is smaller than it
looks. `THESIS.md` correction 4 landed today, from the ladder rung running
next to this: at 167,376,384 parameters on a matched token budget our own
reader reads 0.6341 key first and 0.6063 value first on this split, verified
here from `results/system/eval/xxl167/records_mode_greedy.jsonl.gz`, and the
asymmetry is gone. So the collapse is not a fixed property of a transformer
reader at this size. It goes away with capacity, given training on the task.
LFM2 is 354M and collapses because it has no training on the task; xxl167 is
167M and does not because it has. The two results are consistent and together
they say something narrower than either alone: reading role off the syntax of
an unfamiliar rule sentence is learned from this task, it is not inherited
from English pretraining, and below about 167M our reader does not learn it.

## What the model is and how it was prompted

`LiquidAI/LFM2-350M`, the checkpoint this project already calibrated its
harness against. Parameters are summed over the loaded tensors rather than
quoted from the card: 354,483,968 total, 287,375,104 outside the embedding,
`Lfm2ForCausalLM`, bfloat16, no quantisation.

Every prompt goes through `tokenizer.apply_chat_template` with
`add_generation_prompt=True`, and the rendered string is tokenized with
`add_special_tokens=False`. That combination is the one the bos correction in
`src/extern/LIQUID.md` established, and it is checked rather than assumed:
`src/role/lfm2_run.py` asserts that the first token id of the first rendered
prompt is the tokenizer's bos id before it scores anything. The rendered form
is

    <|startoftext|><|im_start|>user\n ... <|im_end|>\n<|im_start|>assistant\n

whose first three ids decode to `<|startoftext|>`, `<|im_start|>`, `user`.
Tokenizing the same string with `add_special_tokens=True` would give ids
`[1, 1, 6, 6423]`, two bos tokens, which is why the flag is off.

`src/role/lfm2_control.py` runs five control questions through that template
and again with the bos token stripped, and writes both to
`results/role/lfm2/control.json`. With the token the model answers
"The capital of France is Paris", "The answer is 42", "Jupiter", "William
Shakespeare". Without it the same five questions return "is of France?",
"What is 30?" repeated forty times, "Name the largest planet in our solar
system." repeated, and a run of the digit 1. The template is doing its job and
the bos token is present.

## The items are the arms' items

`src/role/lfm2_items.py` reads `data/norm/<split>.meta.jsonl.gz`, which
`src/norm/ndata.py` wrote, and takes each row's `fid`, `shape`, `slots`,
`prog` and `text` unchanged. The key position label is `fid.split(".")[2]`,
the field `src/role/rsplit.py` splits on, so `key_first` here holds the same
items as `key_first` in the arm tables. The held-out sentence mode split is
7,000 items, 3,528 key first and 3,472 value first, which is the n of the
0.7302 and 0.3177 cells.

Rows are shuffled under seed 20260901 before they are written, so any prefix
of the file is a sample of the split. Two bugs on this project came from
reading the first N rows of an ordered file and every run here draws from the
shuffled file.

Two derived handles per item. One stated pair, drawn per item with a seeded
generator from the item's own tables, together with the page line that names
both of its symbols. The line is found by searching the page text rather than
by re-rendering a template, so it is byte identical to what a reader sees, and
which symbol the line names first is read off the line. That surface order
agrees with the frame id's key position field on 2,268 of 2,268 key-first and
2,232 of 2,232 value-first items of the held-out mode split, and on every item
of the other three splits. And the whole table, for the five single table
shapes, 1,260 key-first and 1,240 value-first items.

The hand written parser is the ceiling on the same items. `src/norm/parse.py`,
given the text and the frame id, recovers the program exactly on 3,528 of
3,528 and 3,472 of 3,472 items of the held-out mode split, gets the executed
answer right on all of them, gets the direction of the sampled pair right on
all 2,268 and 2,232, and gets the whole table right on all 1,260 and 1,240.
Every cell of every split reads 1.0000. The items are answerable and any
collapse belongs to the reader.

## Seven formulations, and which of them the model can do

LFM2 cannot emit the typed structure language, so the measured thing is moved
rather than dropped: given a rule sentence, does the model put the two
invented words in the right roles, and does that depend on the order they
appear in. Seven formulations were run, all of them identically on key-first
and value-first items.

| formulation | what the model is asked | floor | does the model do it |
|---|---|---:|---|
| `table_emit_gen` | the whole page, then list every rule as `<item type> -> <target>` | 0.5 on direction | yes, 0.88 to 0.97 key first |
| `page_qa_gen` | the whole page and its own question, answer in one word | item's own candidate set | weakly, above floor on single hop shapes |
| `line_emit_gen` | one rule line, rewrite it as one arrow | 0.5 | rarely, 5 to 13 percent well formed |
| `role_open_gen` | one rule line, which word names the `<item type>` | 0.5 | it answers by recency, not by role |
| `role_letter_ll` | the same, forced choice A or B, log likelihood | 0.5 | no, at floor in three wordings and with four worked examples |
| `role_letter_gen` | the same, generated | 0.5 | no, below floor with a 0.29 to 0.37 refusal rate |
| `role_verify_ll` | is this symbol the `<item type>`, yes or no | 0.5 | no, at floor with a 0.79 to 0.95 yes rate |

`table_emit_gen` is the one to read, because it is the only one where the
model demonstrably does the task in at least one condition. A formulation
sitting at its floor in both cells cannot tell a balanced reader from a
collapsed one, and four of these do exactly that.

The prompt for it names the required direction. It says to list the rules in
the form `<item noun> -> <target noun>`, that is, key on the left, in both
cells and with only the page text differing. So the model is told which way
round to write the arrow, and on value-first pages it writes it the other way
anyway.

## The held-out sentence mode

Of the arrows the model emits, the ones naming both symbols of a stated pair
are counted, and the question is what share of those are written key on the
left. A reader that chooses at random reads 0.5. A reader that copies surface
order reads near 1.0 on key-first pages and near 0.0 on value-first pages.

| decode | key first | value first |
|---|---|---|
| greedy | 0.8805 [0.8610, 0.8975] over 1,213 pairs | 0.3479 [0.3219, 0.3750] over 1,233 pairs |
| sampled | 0.9135 [0.8958, 0.9284] over 1,144 pairs | 0.2865 [0.2620, 0.3124] over 1,232 pairs |

The whole table written exactly, entries and order, is 0.0667 of 1,260 key
first and 0.0081 of 1,240 value first, so the model rarely gets a whole page
right in either cell and the direction figure is the one carrying the signal.

Per shape, on the same items, greedy:

| shape | key first | value first |
|---|---|---|
| lookup | 0.8771 [0.8209, 0.9174] n=179 | 0.1950 [0.1409, 0.2634] n=159 |
| inverse | 0.9082 [0.8611, 0.9405] n=207 | 0.3128 [0.2560, 0.3758] n=227 |
| iterate | 0.8317 [0.7918, 0.8652] n=398 | 0.4658 [0.4152, 0.5170] n=365 |
| exclusion | 0.8877 [0.8450, 0.9197] n=276 | 0.3830 [0.3282, 0.4409] n=282 |
| priority | 0.9608 [0.9171, 0.9819] n=153 | 0.2450 [0.1906, 0.3090] n=200 |

Five shapes, five non-overlapping pairs of intervals, one direction.

One item printed in full, a `priority` page whose rule lines read

    The nidargo value is the one that receives a eskstiv token.
    The civnevi value is the one that receives a verxmuth token.
    The frikharv value is the one that receives a lorngivo token.
    The jarnvand value is the one that receives a mistiv token.

against gold entries `eskstiv -> nidargo`, `verxmuth -> civnevi`,
`lorngivo -> frikharv`, `mistiv -> jarnvand`, and a default of `nidargo`.
LFM2 writes, in full,

    Nevihald -> eskstiv
    nidargo -> nidargo
    civnevi -> verxmuth
    frikharv -> lorngivo
    jarnvand -> mistiv

whose last three lines are the page in surface order with every pair reversed.
The first line names the page's scope and the second its default, and neither
matches a stated pair, so neither is counted in either direction.

## Every sentence mode, not the withheld one

The mode split is withheld from our reader's training and means nothing to
LFM2, which never trained on any of these frames. So the same measurement runs
on the other five statement modes, where our reader reads 0.9206 against
0.9211 and shows no gap at all.

| statement mode | key first | value first |
|---|---|---|
| `relative_clause`, withheld from our reader | 0.8805 [0.8610, 0.8975] n=1,213 | 0.3479 [0.3219, 0.3750] n=1,233 |
| `conditional` | 0.9146 [0.8850, 0.9372] n=445 | 0.5155 [0.4582, 0.5723] n=291 |
| `imperative` | 0.9245 [0.8809, 0.9530] n=212 | 0.6453 [0.5714, 0.7130] n=172 |
| `mapping` | 0.9777 [0.9594, 0.9878] n=448 | 0.0905 [0.0666, 0.1217] n=420 |
| `passive_decl` | 0.9641 [0.9432, 0.9774] n=473 | 0.2992 [0.2452, 0.3594] n=244 |
| `table_row` | 0.9380 [0.9016, 0.9615] n=258 | 0.1374 [0.0948, 0.1949] n=182 |

All six. The worst cell is `mapping`, whose value-first line is
`{v} is the image of {k}`, an explicit statement of the relation in ordinary
English, which LFM2 reverses on 91 percent of the pairs it reproduces. The
best value-first cell is `imperative`, `To the {v} {target}, send every {k}
{item}`, at 0.6453, where the fronted prepositional phrase is the one shape
that gets the model above chance.

The other two held-out splits agree, greedy:

| split | key first | value first |
|---|---|---|
| held-out sentence mode | 0.8805 [0.8610, 0.8975] n=1,213 | 0.3479 [0.3219, 0.3750] n=1,233 |
| trained frames | 0.9472 [0.9360, 0.9565] n=1,836 | 0.3033 [0.2790, 0.3287] n=1,309 |
| held-out question frame | 0.9616 [0.9517, 0.9695] n=1,796 | 0.2993 [0.2742, 0.3258] n=1,206 |
| held-out lexicon | 0.9713 [0.9646, 0.9767] n=2,925 | 0.3226 [0.3019, 0.3440] n=1,888 |

## The lookup question answered directly

The formulation the task named first is the page and its own question, one
word out, scored against the executed gold answer. The candidate set is the
item's slot table and the floor stated per cell is one over the number of
candidates, averaged over the cell's items.

| split | key first | value first |
|---|---|---|
| held-out sentence mode | 0.2029 [0.1900, 0.2165], floor 0.1788 | 0.1561 [0.1444, 0.1686], floor 0.1785 |
| trained frames | 0.1369 [0.1260, 0.1486], floor 0.1759 | 0.1224 [0.1119, 0.1337], floor 0.1760 |

Pooled over fourteen shapes this sits close to its floor, because two of them
are arithmetic and a 350M model does not do it: `sum_chain` reads 0.0079 key
first and `apply_n` 0.0079, and several more need a chain of hops. The floor
column is only meaningful where the answer is one of the item's invented
words, which is why `apply_n`, whose answer is a number and whose slot table
holds one name, is left out of the table below. Per shape on the held-out
mode, greedy:

| shape | key first | value first | floor |
|---|---|---|---|
| lookup | 0.3492 [0.2930, 0.4099] | 0.1734 [0.1313, 0.2254] | 0.0982 |
| priority | 0.5198 [0.4583, 0.5808] | 0.2903 [0.2374, 0.3497] | 0.1141 |
| band_then_lookup | 0.3492 [0.2930, 0.4099] | 0.0766 [0.0496, 0.1166] | 0.1213 |
| inverse | 0.2143 [0.1681, 0.2690] | 0.3952 [0.3364, 0.4572] | 0.1111 |

`inverse` is the check that the positional account predicts and passes. Its
question hands the model a value and asks for the key, so a reader that has
the table backwards answers it correctly, and it is the one shape whose gap
runs the other way. On a value-first page the model reads `inverse` at 0.3952
and `lookup` at 0.1734, out of the same table and the same page layout.

## The formulations that stayed at their floor

Reported because a null on one prompt is not a null, and because three of
these were run to try to make the model succeed.

Forced choice between the two symbols, scored by log likelihood so no answer
format can be failed, three wordings, both roles asked. On the held-out mode
with the middle wording the model reads 0.0705 when asked which symbol is the
key on a key-first line and 0.9246 when asked which is the value on the same
line, that is, it names the second symbol either way. Getting both questions
right on one item runs at 0.0132 key first and 0.1071 value first, against
0.25 for two independent coin flips, so the two answers are anticorrelated:
the model is answering the line and ignoring the question. Four worked
examples, drawn from two sentence shapes that are not `relative_clause` and
balanced across key positions, do not move it: 0.0384 and 0.5099 on the key
question.

The yes or no verification form reads 0.4277 and 0.4928 with a yes rate of
0.8307 and 0.9521, which is acquiescence rather than reading.

Open generation of the word, with no options, reads 0.2121 key first and
0.8517 value first, and names the sentence's second symbol on 0.7618 and
0.9664 of items. That is a clean recency rule and it is worth stating that it
runs opposite in sign to the arrow result. Which convention the model commits
to depends on the formulation. Whether it commits to one does not, which is
the same shape the four training arms produced.

`line_emit_gen`, one line rewritten as one arrow, is well formed on 0.0511 of
key-first and 0.1272 of value-first items, the model preferring to write a
paragraph. Among the well formed ones the direction reads 0.6379
[0.5473, 0.7197] and 0.3838 [0.3292, 0.4416], the same sign at much smaller n.

## Attacks on the arrow result

The parser. The first pass took the last word left of the arrow and the first
word right of it, which drops a line like `ledger muthxanth -> filing
muthnevi`. `src/role/lfm2_rescore.py` re-reads the same generations and looks
on each side for any symbol the page names, which counts those lines instead
of discarding them. Held-out mode, greedy: 0.8805 against 0.8814 key first and
0.3479 against 0.3514 value first, over 1,213 and 1,233 pairs against 1,155
and 1,178. The reading does not depend on the parser.

The generation budget. `max_new_tokens` is 512 against a mean of 61.2 and 53.1
new tokens, and the truncation rate is 0.0286 key first and 0.0210 value first
on the held-out mode, 0.0468 and 0.0508 on the trained frames. Balanced across
the cells and far too small to carry a 0.53 gap.

Selection. The direction is conditional on the model having reproduced the
pair, and it reproduces more pairs on key-first pages, 1,836 against 1,309 on
the trained frames. The denominators are stated in every cell and the held-out
mode's are near equal, 1,213 against 1,233, with the gap at its full size
there.

The decode. Sampled runs at temperature 0.1, top k 50 and repetition penalty
1.05, the settings `src/extern/models.py` carries for the Liquid 350M, and it
agrees with greedy in both cells of both splits: 0.9135 [0.8958, 0.9284]
against 0.2865 [0.2620, 0.3124] on the held-out mode, and 0.9284
[0.9161, 0.9390] against 0.3074 [0.2835, 0.3323] on the trained frames.

The prompt. It states the required direction, identically in both cells.

## Beside the 45M reader

The two measurements are not the same statistic and are set out that way. Ours
is exact equality with the gold structure and, beside it, the share of symbols
whose role the emission keeps, from `src/role/rswap.py`. LFM2's is the share
of reproduced pairs written in the gold direction. Both ask whether the reader
keeps the roles or swaps them, on the same items, on the same split.

| reader | measure | key first | value first |
|---|---|---|---|
| l45, 45,483,008 params, ours | structure exact | 0.7302 (n=3,528) | 0.3177 (n=3,472) |
| l45 | symbol role kept | 0.9880 (22,835 symbols) | 0.5128 (22,464 symbols) |
| l45 | symbol role flipped | 0.0119 | 0.3920 |
| xl93match, 93,579,520 params, ours | structure exact | 0.3243 (n=3,528) | 0.7252 (n=3,472) |
| xxl167, 167,376,384 params, ours | structure exact | 0.6341 (n=3,528) | 0.6063 (n=3,472) |
| LFM2-350M, 354,483,968 params | pair direction | 0.8805 (1,213 pairs) | 0.3479 (1,233 pairs) |

Our 45M reader keeps the role of 0.9880 of key-first symbols and 0.5128 of
value-first ones. LFM2 writes 0.8805 of key-first pairs the right way round
and 0.3479 of value-first ones. Same sign, same rough size, one model
undertrained by a factor of four and the other not. The rung that breaks the
pattern is ours: xxl167 reads 0.6341 against 0.6063, a gap of 0.028, at less
than half LFM2's parameter count. Capacity plus training on the task is doing
something that four times the parameters and a proper English budget do not.

The difference that remains is which sentences it happens on. Our reader is at
0.9206 against 0.9211 on the five trained sentence modes and collapses only on
the one it never read, which is what makes the collapse look like a failure of
generalisation. LFM2 collapses on all six, because none of them is a trained
mode for it. So the finding is not that a sentence mode has to be withheld for
this to happen. Role binding by surface order is what both readers do with a
rule sentence they have no template for, and training on a sentence shape is
what buys our reader its way out of it on that shape.

## Which outcome this is

Of the three the task set out, the second, on the measurement. LFM2-350M shows
the same asymmetry, at full strength, and the undertraining account of our own
45M collapse does not survive it: a model with four times the size and a
proper English budget does the same thing on the same items.

The inference the task attached to that outcome does not follow, and the
reason is our own ladder rather than anything LFM2 did. "A real property of
transformer readers rather than of our training budget" is refuted by
xxl167, which is a transformer reader of this family at 167M and reads
0.6341 against 0.6063. This is not the strongest substrate result on the
project. There is no substrate result here. The correct statement is the
narrow one:

    Role-independent-of-position reading of an unfamiliar rule sentence is
    something this task teaches, not something English pretraining supplies.
    LFM2-350M, with the English and without the task, fails it. xxl167, with
    the task and a third of the parameters, passes it. The 45M and 93M rungs
    have the task and fail it, so what they lack is capacity.

Three things this does not say. It does not say the two models fail for the
same mechanical reason, only that they fail the same way on the same items.
It does not compare like tasks: xxl167 emits a typed structure after 110,271
training steps on this corpus and LFM2 writes arrows zero shot, so the levels
are not comparable and only the shape of the split is. And it does not rescue
the four arms, which remain four interventions that changed a convention
without removing one, at a rung where correction 4 now says capacity was the
binding constraint.

What LFM2 is still good for. It is the only reading in this lane of what an
untrained-on-task reader does with these sentences, and it says the default is
surface order, strongly and consistently, at a size where our own trained
reader has already stopped doing it. Any claim that a retrieval-fed small
reasoner will pick up role marking from a general checkpoint has to answer
0.3479.

On the control the task asked for. LFM2 has no trained sentence forms here,
so a trained against held-out ratio would be a ratio of two things that mean
nothing for this model, and the per-mode table stands in its place. What that
table has to say is that LFM2 reads key-first sentences well in every one of
the six modes, 0.8805 to 0.9777, so its value-first cells are a collapse and
not a floor. The one place a floor does swallow the comparison is the four
forced choice and verification formulations, and those are reported as floors
rather than as results.

## Files

    src/role/lfm2_items.py     the probe items, off the same eval splits
    src/role/lfm2_control.py   the chat template and the bos token, checked
    src/role/lfm2_run.py       one formulation per invocation
    src/role/lfm2_report.py    cells by key position, with Wilson intervals
    src/role/lfm2_rescore.py   the generous arrow parser, on the same raw
    src/role/lfm2_qa.py        the lookup answers against the slot list
    src/role/lfm2_tables.py    every cell quoted above, as one json

    results/role/lfm2/control.json           the bos and template evidence
    results/role/lfm2/items/                 the probe items and their counts
    results/role/lfm2/runs/                  one record per item per run
    results/role/lfm2/tables.json            every cell above
    results/role/lfm2/rescore.json           the generous arrow parse
    results/role/lfm2/page_qa_rescore.json   the lookup answers and floors
    logs/lfm2/                               the run logs

    s3://decoupled-reasoner-009398924577/results/role/lfm2/
