# The typed core

A structure language, an exact interpreter over it, a renderer that writes a
structure into English through the corpus frame grammar, and a reference parser
that reads the English back. Structure and text are two views of one object,
and the round trip between them is the gate on the whole idea.

Nothing here is learned and nothing here samples. This lane never loaded a
checkpoint, so the world header gate on checkpoint evaluation does not apply to
any number below.

## 1. What the language has to say

The definition kinds were chosen by reading what the existing families express.
Each one is here because something in the repo already says it.

| kind | what it says | where it already appears |
|---|---|---|
| `Table` | key to value, in stated order, optionally with a default, optionally ordered so the first matching row wins, keys optionally pairs | `relations.py` substitution, inverse_table, chain_rule, transitive, two_key, priority_list, exclusion, agreement |
| `Bands` | n labels over n-1 ascending cut points on one named attribute | `relations.py` threshold, band_rule; `skillacq/simple.py` ThresholdRule |
| `Rule` | one general value with stated exceptions | `relations.py` exception_rule; `skillacq/simple.py` ExceptionRule |
| `Weights` | key to integer | `relations.py` lookup_then_band, weighted_chain |
| `Affine` | x becomes (a x + b) mod m | `relations.py` modular_apply |
| `OpDef` | a typed operator over parameters with preconditions and postconditions | `skillacq/systems.py` BinaryOpSystem, UnitSystem, ProcedureSystem |

The six task requirements land as follows. A keyed lookup is `Table`. A
conditional rule with an exception is `Rule`. A threshold test is `Bands`. A
chained composition of arbitrary depth is a plan of `lookup` steps, with no
bound on how many. An operator with several simultaneous conditions is an
`OpDef` whose body applies every condition at once, which is the `procedure`
family. A plan calling more than one distinct operator is any plan whose steps
name two different definitions, which is what `lookup_then_band`,
`band_then_lookup`, `sum_chain` and the `units` sum question all are.

## 2. The language

### Values

Four types. `int`, `sym` (an invented word, written as a Python string),
`bool`, and `set` (a tuple of syms, used for the groups a priority question
names). Booleans are checked before integers, so `True` is a `bool` and not
the integer 1.

### Definitions

```
Table(name, entries, default=None, ordered=False)
    entries   ((key, value), ...) in the order the page states them
    key       a sym, or a tuple of syms for a grid
    default   the value for a key that is not listed, or None if the page
              states no default
    ordered   when true, a lookup takes a set of keys and the first listed
              entry whose key is in that set wins

Bands(name, attr, cuts, labels)
    cuts      k ascending integers
    labels    k+1 syms. Band i covers cuts[i-1] <= x < cuts[i], with the
              first band open below and the last open above

Rule(name, general, exceptions)
    exceptions ((key, value), ...); the first matching exception wins,
              otherwise the general value

Weights(name, entries)      entries ((key, int), ...)

Affine(name, a, b, m)       x becomes (a x + b) mod m, or a x + b when m is 0

OpDef(name, params, body, pre=(), post=())
    body      an expression of src/opgraph/opdef.py: integers, string
              literals written 'like-this, booleans, variables, n-ary + and
              *, binary - // % >= <= > < = != min max, unary neg and not,
              n-ary and and or, and a three armed if
    pre       conditions over the parameters, all of which must hold
    post      conditions over the parameters and `r`, the result
```

Definitions are addressed by the pair (kind, name), so a `Table` and a
`Weights` written on the same page may share that page's name. `weighted_chain`
does exactly that and the addressing is what lets it.

### Plans and programs

```
Ref(name)        read a temporary or a named input
Lit(value)       a literal written into the plan
Step(out, op, args)
    args         leading definition names as plain strings, then values
Program(defs, inputs, steps, answer)
    inputs       ((name, value), ...); the first is the question's start
    answer       the name of the temporary or input that holds the answer
```

A plan does not branch and does not loop. All of the control flow a question
needs is the order of the steps and which temporary each one reads. That is the
point: composition depth becomes the length of a list.

### Operations

| op | definitions it names | values | result |
|---|---|---|---|
| `lookup` | one `table` | 1 or 2 | the stated value, else the default |
| `lookup_ordered` | one `table` | 1 set | the first listed entry whose key is in the set |
| `invert` | one `table` | 1 | the unique key mapping to the value |
| `odd_one_out` | one `table` | 1 | the unique key not mapping to the value |
| `prefer` | two `table` | 1 | the first table's value if it states one, else the second's |
| `band` | one `bands` | 1 int | the label whose band holds it |
| `weigh` | one `weights` | 1 | the stated integer |
| `rule` | one `rule` | 1 | the matching exception, else the general value |
| `step` | one `affine` | 1 int | one application |
| `call` | one `op` | as many as it has parameters | the body's value |
| `add`, `sub`, `mul` | none | 2 ints | arithmetic |

### Persistence

`program_json` and `program_load` are exact in both directions for every value
the language holds, and the round trip lane checks that on every item. Record
files hold the JSON form, so a persisted structure reloads to the one measured.
`pretty` writes the readable form used in this document.

## 3. The interpreter

`run(program)` returns a `Result` with `ok`, `value`, `reason` and a step
trace. There is no third outcome. Where it cannot compute an answer it says so
and returns no value, and `Result.text` is the empty string, which is what the
grader then scores as naming nothing.

It refuses on: a definition it was not given, two definitions of one kind under
one name, an operation it does not know, a step whose argument count is wrong,
a temporary read before it is written or written twice, a value of the wrong
type, a key the table does not state with no default stated either, a table
that states two different values for one key, an inversion that is not unique,
a band set whose labels and cuts do not line up, a precondition or
postcondition that does not hold, and division or modulo by zero.

Two of those are worth naming. A page that lists one key twice with two values
states two answers, and picking either one is a guess, so the interpreter
refuses. And a band set is checked for `len(labels) == len(cuts) + 1` before it
is used rather than indexed and hoped for.

Nothing in this module caps composition depth. `run` is a `for` over the step
list. Expression evaluation walks an explicit stack rather than recursing, so a
deeply nested operator body does not reach the Python recursion limit either.
`src/opgraph/plan.py` caps at `MAX_STEPS` 128 and `src/opgraph/opdef.py` caps
expression nesting at `MAX_DEPTH` 64; neither limit is inherited, and section 8
measures both.

## 4. The renderer

`render(program, fid, preamble_level)` writes nothing itself. It turns the
program into the `Fact` and `Question` records of `src/corpus/relations.py` and
hands them to a frame from the bank `src/corpus/frames.py:load_frames` returns,
which is the 768 frame product of 8 lexicons, 6 statement modes, 2 key
positions, 4 question forms and 2 scope positions. A rendered structure is byte
identical to what the corpus would have written for the same records.

`classify(program)` reads the plan and names which of the frame grammar's
question shapes it is. Fourteen shapes are renderable: `lookup`,
`lookup_general`, `classify`, `inverse`, `compose`, `iterate`, `pair`,
`priority`, `exclusion`, `lookup_then_band`, `band_then_lookup`, `sum_chain`,
`apply_n`, `precedence`. The fifteenth template the grammar has, `invert_chain`,
is not renderable and section 11 says why.

`text` is the strict serving form: every page and then the question, joined the
way blocks inside a page are joined, so nothing marks where a page ends except
the sentences themselves.

## 5. The reference parser

`parse(text, fid)` is handed the rendered text and the frame id and nothing
else. It is not handed the shape, the question's key, the scopes, or any part
of the structure. Every pattern it uses is built mechanically from the frame's
own templates in `src/corpus/frames_default.py` by `compile_template`, which
fills the lexicon slots with the words the frame writes and replaces the
structure slots with a capture group typed to what can appear there: a
capitalised scope name, a lowercase invented word, an integer, or one of the
three range spellings.

It finds page heads by the frame's own `PREAMBLE_HEAD`, drops the padding
notes, drops the table header line in `table_row` mode, reads each rule line by
trying the eight fact templates in an order that resolves the two shapes that
can collide, reads the question by trying all fourteen question templates and
refusing if more than one matches, and then keeps only the pages the question
names. A page that is served but not named is not part of the structure the
question asks about, which is how a store holding a distractor is read without
the distractor being folded in.

Where it cannot read something it refuses and says why. A refusal counts as a
round trip failure rather than being retried with a looser pattern.

## 6. The round trip

`src/norm/roundtrip.py`. One structure per (frame, shape) cell over all 768
frames and all 14 shapes, with the preamble level drawn from 0 to 12 so the
padding varies. Four checks, all four required:

- `parsed`, the parser read the text at all
- `identical`, the recovered program equals the rendered one by structural
  equality of definitions, entries in order, inputs, plan and answer
- `rerender`, re-rendering the recovered program in the same frame gives back
  the same bytes. This check does not pass through anything the generator and
  the parser share, so a parser that guessed the plan from the shape alone
  would fail it
- `executes`, the interpreter returns the same answer for both

Result: **10752 of 10752, 1.000**, and 1.000 on each of the four checks
separately, in each of the 14 shapes separately at n = 768 per shape, and in
each frame axis separately. Nothing is pooled across shape.

Records `results/norm/roundtrip/records.jsonl.gz`, summary
`results/norm/roundtrip/summary.json`.

## 7. Reading structures the corpus built

The round trip measures whether the representation survives its own generator.
This lane measures whether it covers what the corpus writes.
`src/norm/corpuscheck.py` builds instances with `src/corpus/relations.py`
untouched, renders pages and questions with the corpus frames, serves a
distractor instance of another family alongside (before the answering pages on
half the items), hands the text to the parser, executes the recovered
structure, and scores against the gold the corpus recorded.

161,280 items, 768 frames, all 16 relation families, depths 1, 2, 3, 4, 6 and 8
for the five families that carry depth, 6 questions per instance. Per family
and depth, never pooled:

- every family and depth is **1.000** on the items whose store is unambiguous,
  except `inverse_chain` at depth 2 and deeper, which is **0.000**
- `inverse_chain` at depth 1 is 1.000
- 114 items of 161,280 are stores where the corpus's own distractor drew a page
  name an answering page already uses, which is 25 of the sweep's 31,488
  instances. The parser refuses those rather than guessing which page the
  question means

Records `results/norm/corpus/records.jsonl.gz`, summary
`results/norm/corpus/summary.json`.

## 8. Depth

`src/norm/depth.py`. One ring walk per depth against a reference computed by
index arithmetic rather than by walking, so an error in the walk cannot be
reproduced by the reference.

| plan depth | exact | microseconds per step |
|---|---|---|
| 2 | yes | 11.2 |
| 128 | yes | 4.2 |
| 512 | yes | 4.1 |
| 2048 | yes | 4.0 |
| 8192 | yes | 4.0 |
| 32768 | yes | 4.1 |

Cost per step is flat from depth 128 to depth 32768 and the depth 2 figure is
one timer reading over two steps. Depth 48 costs what depth 2 costs.

Measured beside it rather than quoted: `src/opgraph/plan.py:parse_plan` accepts
128 steps and refuses 129 with "plan too long". `src/opgraph/opdef.py:eval_expr`
evaluates an expression nested 64 deep and refuses at 65 with "expression too
deep"; `src/norm/interp.py:eval_expr` evaluates the same expression nested
100000 deep.

Summary `results/norm/depth/summary.json`.

## 9. Against the hand-written parsers on record

`src/norm/baselines.py`. The same episode files the published sweep used,
`/home/ec2-user/frames/eps`, 13 frames by 3 families by 100 episodes by 6
questions, 23,400 items. `src/frames/parsers.py` is re-run over them unchanged
and `src/frames/score.py` grades both, so this is the same items, the same
gold and the same grader.

The pipeline under test reads the text into a structure and then executes it.
It is handed less than the published parser in two ways, both harder: the
published frame-aware parser is handed the question's key, and this one parses
the key out of the question with the frame's own question template; the
published parser is handed the `src/skillacq/simple.py` system object, so it
knows the system's name and its fallback word before it reads, and this one is
handed only the frame and reads the name, the fallback, the table, the general
rule and the exception off the page. It also builds the whole structure rather
than the one row the question asks about.

Forced choice is the headline, `first` is beside it, hedge and none rates
travel with it, and both chance floors come from the published scorer.

| family | n per frame | interpreter forced | frame-aware parser forced | chance | chncPg | hedge |
|---|---|---|---|---|---|---|
| `substitution_rule` | 600 | 0.988 | 0.992 | 0.200 | 0.073 | 0.000 |
| `exception_rule` | 600 | 1.000 | 1.000 | 0.500 | 0.102 | 0.000 |
| `threshold_rule` | 600 | 1.000 | not answered | 0.500 | 0.097 | 0.000 |

Identical in all 13 frames, including the four held out on both axes. The
hedging canary scores 0.000 forced on the same rows in every cell.

**On `substitution_rule` the interpreter does not beat the hand-written
parser.** 0.988 against 0.992. The reason is in the items, and the artifact
carries the classification:

- 23,309 of 23,400 items state one answer on the page and have a gold that
  agrees. On those the interpreter is **1.000** and the frame-aware parser is
  **1.000**, in every one of the 13 frames.
- 65 items are pages that state two different values for the key the question
  asks about. The interpreter declines all 65. The parser guesses and is right
  on 26 of them, which is where its extra 0.004 comes from.
- 26 items have a gold that contradicts the single value the page states. Both
  readers answer the page and both are scored wrong.

`threshold_rule` is reported for completeness only. The published parser
returns nothing on that family, and `src/frames/FRAMES.md` records that the
family is a grading artifact for the checkpoint, so it carries no headline.

Records `results/norm/baselines/records.jsonl`, summary
`results/norm/baselines/summary.json`.

## 10. The operator families

`src/norm/skillacq.py`. Episodes from `src/skillacq/systems.py:generate_episode`
unchanged, including its distractor page and its rejection of answers copyable
from the question. The reader is handed the textbook pages and the question
text; the glyph, the coefficients, the modulus, the associativity, the
conversion factors, the bonus, the penalty and the cutoff are all read off the
page. Gold is the generator's own reference implementation.

| cell | n | read | exact on read | distinct operators per plan |
|---|---|---|---|---|
| `binary_op/direct` | 1631 | 1631 | 1.000 | 1.0 |
| `binary_op/nested` | 806 | 806 | 1.000 | 1.0 |
| `units/convert` | 2137 | 2132 | 1.000 | 1.0 |
| `units/sum` | 1063 | 1052 | 1.000 | 3.0 |
| `procedure/score` | 3200 | 3200 | 1.000 | 1.0 |
| `procedure/decide` | 1582 | 1582 | 1.000 | 2.0 |

The 16 unread items are all pages that give two of the three units the same
name, which section 11 covers. `binary_op/solve_for`, 763 items, is out of
scope and counted rather than attempted: it asks for an inverse of the operator
over a domain the page does not state, which is a search and not a
composition, and this language does not express a search.

`procedure/decide` items never appear in a built episode, for the reason in
section 11, so they are run straight from `ProcedureSystem` against its own
`eligible`. They are the two operator plan for this family: one operator
carries both adjustments and applies them together, a second turns the score
into the stated verdict.

Records `results/norm/skillacq/records.jsonl`, summary
`results/norm/skillacq/summary.json`.

## 11. Attacks on the round trip number

A 1.000 is a bug until it has survived something. `src/norm/attack.py` runs five
attacks over 96 frames by 14 shapes. Each is a way the round trip could read
1.000 without the parser reading anything.

| attack | n | outcome |
|---|---|---|
| change one value word in the text | 1288 | 974 recovered a changed structure, 314 refused, **0 silently returned the original** |
| delete one rule line | 1208 | 950 changed, 238 refused, 20 dropped the table header which carries no structure, **0 silently returned the original** |
| read frame A's text with frame B's patterns | 1336 | 1323 refused, 13 returned the original and in every one of those both frames write byte identical text for that structure, **0 leaks** |
| cut the text off before the question | 1344 | **1344 refused** |
| does program equality see one changed entry | 192 | **192 distinguished** |

Summary `results/norm/attack/summary.json`.

## 12. What the language does not express

Stated so that its absence is not mistaken for coverage.

- A search. `binary_op/solve_for` asks which y gives a stated result, over a
  domain the page never states. `invert` and `odd_one_out` invert a table,
  which is a finite stated domain; inverting an operator is not.
- Branching or looping inside a plan. Everything conditional lives inside an
  `OpDef` body, where `if` is total and terminating.
- Anything the frame grammar has no sentence for. The renderer covers 14 of the
  15 question templates the grammar has, and refuses a plan of any other shape
  rather than inventing English for it.

## 13. Defects found in the corpus

Four, all measured, all pinned by a test in `src/norm/tests/test_norm.py` so
that a later corpus change cannot move them unnoticed.

`invert_chain` renders a question that does not ask for its own gold.
`QUESTION_TABLES` gives `invert_chain` the same `Q_INVERSE` template as
`inverse`, and that template names only `q.scopes[0]`. An inverse chain has its
scopes reversed, so `scopes[0]` is the last hop's page and the earlier hops are
never named. The question therefore asks which key the last page maps to the
given value, whose answer is the token one hop back, while the recorded gold is
the token at the start of the chain. `src/norm/witness.py` prints a witness: two
pages served, one named, the question's own answer `cinqciv`, the gold `zeltu`.
Measured at 1.000 for depth 1 and 0.000 at depths 2, 3, 4, 6 and 8, 15,360
items.

A distractor can take an answering page's name. `src/corpus/build.py:_instances`
draws the distractor's invented words from a second `Lexicon` that knows
nothing of the first, so the two can draw the same scope name. Calling
`_instances` directly over 30,000 draws spread across frames, families and
depths puts it at 25 draws, 0.00083. The sweep's own rate agrees: 25 of 31,488
instances, 0.00079, which is 114 items of 161,280. The served store then holds
two pages under one name and the question naming it does not say which one it
means.

`SubstitutionRule` states two answers on one page, and sometimes states one that
its gold contradicts. Its four keys are drawn independently and can repeat, so
a page lists one key twice with two values: 65 items of 23,400, 5 per
substitution cell, and `src/frames/FRAMES.md` already records this one. Not
already recorded: the 20 percent branch that draws an unlisted key draws a fresh
word without checking it against the listed keys, so the page can state a value
for a key whose gold is the fallback. That is 26 items of 23,400, 2 per cell,
and it caps every reader below 1.000 for a second reason.

Half of `ProcedureSystem`'s question space never reaches an episode. Every
`decide` item asks "Is it accepted or refused?" and its answer is one of those
two words, so `_answer_is_copyable` rejects all of them and
`generate_episode` emits only `score` items. `UnitSystem` has a smaller version
of the same class of problem: it draws its three unit names independently and
repeats one in 0.0072 of draws, after which the page reads "One A equals k B.
One B equals m A." and a question naming the repeated word does not say which
unit it means.

## 14. Files

```
src/norm/lang.py         the language, its JSON form and its readable form
src/norm/interp.py       the exact interpreter
src/norm/shapes.py       the canonical program for each renderable shape
src/norm/render.py       structure to text, through the corpus frames
src/norm/parse.py        the reference parser, text back to structure
src/norm/gen.py          random structures, sized like the corpus families
src/norm/roundtrip.py    the round trip gate
src/norm/corpuscheck.py  the interpreter against the corpus gold
src/norm/baselines.py    the interpreter against the parsers on record
src/norm/depth.py        composition depth, and the limits not inherited
src/norm/skillacq.py     the operator families
src/norm/attack.py       five attacks on the round trip number
src/norm/witness.py      the invert_chain witness
src/norm/tests/test_norm.py
```

Artifacts, all under `/home/ec2-user/decoupled-reasoner/results/norm/`:

```
roundtrip/records.jsonl.gz  roundtrip/summary.json
corpus/records.jsonl.gz     corpus/summary.json    corpus/failures.json
baselines/records.jsonl     baselines/summary.json
skillacq/records.jsonl      skillacq/summary.json
depth/summary.json
attack/summary.json
```

## 15. Running it

```
python3 -m src.norm.roundtrip   --out results/norm/roundtrip
python3 -m src.norm.corpuscheck --stride 1 --out results/norm/corpus
python3 -m src.norm.baselines   --out results/norm/baselines
python3 -m src.norm.skillacq    --out results/norm/skillacq
python3 -m src.norm.depth       --out results/norm/depth/summary.json
python3 -m src.norm.attack      --out results/norm/attack/summary.json
python3 -m src.norm.witness
python3 -m unittest discover -s src/norm/tests -t .
```

All of it is CPU only and the whole set runs in about six minutes, of which the
corpus sweep is nearly all.
