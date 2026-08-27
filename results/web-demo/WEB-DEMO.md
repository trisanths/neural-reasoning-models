# Web demo: first real-web retrieval pass

2026-08-27, dev box i-00b1114be36214a6c, repo at 27dcf91 plus the
changes committed with this file. Exploratory, not a gate.

Search added nothing. Per-model contains-answer accuracy over 60 real
factual questions, with the live Exa tier serving against a no-serving
control on identical prompts:

| model | with search | without search | mean rounds | questions emitting any query |
| --- | --- | --- | --- | --- |
| curve-350me-501 | 0.017 (1/60) | 0.017 (1/60) | 0.20 | 12/60 |
| killtest-c-201 | 0.000 (0/60) | 0.000 (0/60) | 1.05 | 60/60 |
| curve-350md-401 | 0.000 (0/60) | 0.000 (0/60) | 1.00 | 60/60 |

The single scored point is not a retrieval success. On "How many moons
does the planet Mars have?" curve-350me-501 answered "2," in both
passes without retrieving, a confabulated numeral that happens to
match a short numeric gold. Contains-answer with one-digit golds
admits this kind of luck; the transcripts make it visible.

## Setup

Three final checkpoints (step 26700): curve-350me-501, the regime E
extreme fact-free model; killtest-c-201, pure synthetic regime C; and
curve-350md-401, the weakened form. 60 questions authored for this run
(scripts/web_qa_questions.json) in the naturalized register but about
the real world: 15 each on capitals and geography, people, years, and
quantities, every gold answer short and verifiable, with accepted
surface forms listed per question.

Per question the prompt is the training trace format with no documents
in context: <|world|>, the header "domain: corporate", <|q|>, the
question. Greedy decode. When the model emits <|retrieve|> its query
goes to Exa neural search, the top 5 pages are chunked to 512 tokens
with the project tokenizer, the pooled chunks are ranked by the same
Okapi BM25 the training oracle uses, and the top chunk is spliced
after <|result|>. At most 3 rounds, served without replacement, 160
new model tokens per question. The control pass runs the same prompts
with no serving surface, so a <|retrieve|> stops the loop unserved.
Scoring is the naturalized suite's normalized contains-answer against
any gold form.

The serving path is src/evals/interactive.py's generate_with_retrieval
with the new injected-index parameter, taking WebTierIndex from
src/retrieval_web. The built BM25 path is unchanged and the full suite
is green (262 passed, two new injected-index tests).
scripts/web_qa_demo.py drives the runs, caches searches on disk across
models, and enforces a live-call budget. The whole experiment used 90
live Exa searches plus 45 cache hits against the ~600 budget, with no
API errors and nonempty results for every query. Decode time: 64s,
163s, and 297s for the me, c, and md web passes; the control passes
are seconds, since two models stop at their first unserved retrieve.

## Does the trained loop fire on real questions

In distribution it works: on fresh worldgen heldout episodes both
probed checkpoints retrieve and answer correctly
(scripts/diag_webdemo.py). On real questions the retrieve habit fires
for killtest-c-201 and curve-350md-401 on every single question, in
both passes; the control pass for both is 60/60 attempted retrieves
that stop unserved with empty answers. curve-350me-501 mostly declines
to search: 48/60 questions get a direct confabulated answer in
worldgen morphology ("Troxti", "Vrivi", "Vrivi Vroldi") and 12/60 emit
a query.

Firing is sensitive to the preamble. With the out-of-vocabulary header
"domain: world", curve-350me-501 emitted zero queries in a three
question probe; with the training header "domain: corporate" it
retrieved on two of three. killtest-c-201 retrieved under every
variant. The main run uses "domain: corporate" and the probe is
recorded in the results json.

## What the queries look like

Query formation transfers by shape, weakly by content.
curve-350md-401 is the best of the three: 25 of its 60 queries carry a
content word from the question, and some are perfectly sensible
searches ("general relativity", "penicillin", "sistine", "first
modern Olympic games were"). The rest mutate question entities toward
worldgen morphology: "turkatron" for Turkey, "braza" for Brazil,
"canxdrus" for Canada. One query degenerates into "the continents"
followed by the word "continent" repeated to the 64-token query cap,
which reads as the oracle's minimax repeat-count query style firing
without its verification loop. killtest-c-201 writes mostly pure
worldgen pseudo-words ("nitrivi", "rerda", "vroplox") or function
words from the question ("in", "didin"); 3 of 63 queries carry a
content word. curve-350me-501's few queries are question fragments
("is", "is the", "mona"), 3 of 12 with content.

Exa's neural search does something with all of this: "turkatron"
finds a cartoon robot turkey, "didin" a LinkedIn profile, "mona" the
Mona Sans font. But content-bearing queries reach real evidence. The
gold answer appeared verbatim in a served chunk for 12/60 questions
for curve-350md-401 (Britannica, Wikipedia, NASA, olympics.com among
the sources), 2/60 for killtest-c-201, 0/60 for curve-350me-501.

## Why answers still fail

Reading is the binding failure, and it fails harder than the queries
do. curve-350md-401 produced an empty answer on all 60 web-pass
questions: every trace ends at the token budget without <|a|> ever
being emitted. A decode of its generated stream shows what it does
instead: after the served chunk it continues writing document-flavored
text, looping degenerately. Served a NAICS industries page, it
emits "Industries in the North American Industry Classification
System (NAICS) are: Agriculture, Forestry, Fisheries, Mining, Mining
and Metallurgy, Mining, Metallurgy, Mining, Metallurgy, ..." to the
budget. Served a Solar System page after querying "titan" for the
Titanic question, it emits "## Explore the Solar System" thirty times.
The model treats real web prose as document stream to continue, not as
evidence to answer from. killtest-c-201 sometimes closes the loop
formally, emitting <|a|> and a short answer, but the answer is
confabulated worldgen content ("Redresta", "Derves Industries", "88");
36/60 of its web answers are empty. curve-350me-501 rambles to the
budget on all 12 questions where it retrieved.

This is the same reading failure the E-501 verdict measured on the
naturalized suite (prose contains 0.168 against the regime A mean,
ratio 0.818, a gate fail): fluent continuation that fabricates
specifics instead of copying them. The web demo shows the failure
extends to retrieval-served real text, and that it, not query
formation, is what zeroes the pipeline: for curve-350md-401 the answer
was sitting in context 12 times and was never once copied out.

## Sample transcripts

Ten verbatim transcripts per model, with chunk previews and the
control answer for the same question, are in results-webdemo.json
under models.<name>.transcripts. Three condensed examples:

curve-350md-401, "Who developed the theory of general relativity?"
(gold Einstein). Query "general relativity". Served
wikipedia.com/wiki/General_Relativity, whose chunk contains Einstein.
Answer: empty, budget reached while continuing the article. Control:
empty.

killtest-c-201, "What is the capital city of Brazil?" (gold Brasilia).
Query 1 "brazil", served the Britannica Brazil page, gold in chunk.
Query 2 "of grandparent", served the Wikipedia Grandparent page.
Answer: empty. Control: empty.

curve-350me-501, "In what year did the Titanic sink?" (gold 1912). No
query. Answer "Vrivi" in both passes.

## Anomalies

The run itself was clean: no API errors, no crashes, resumable rows,
budget honored. Things to carry forward: the preamble sensitivity
above; contains-answer luck on short numeric golds (the one scored
point); single-word queries steer Exa neural search to arbitrary
same-named pages, so query specificity matters more here than against
the training oracle; and the repeat-count query degeneration, which
suggests the minimax-style traces teach a shape that needs its
verifier.

## Reading

The web tier, the chunker, the shared BM25 ranking, and the interactive
loop compose end to end against the live web on the first try, and the
trained emit-query-read reflex does fire out of distribution. What is
missing is transfer of content into queries for two of three models,
and extractive reading of real prose for all three. The weakened model
curve-350md-401, not the extreme one, has the most transferable query
habit, while the extreme model mostly refuses to search at all outside
its training distribution. Candidate next steps, in order of expected
information: rerun this demo on a checkpoint that passes the reading
gate once one exists, since reading is the binding constraint; add
real-prose styles to the retrieval-trace corpus so served text stops
reading as continuation material; and probe elicitation variants
(forced first retrieve, question-echo priming) cheaply through the
cache before spending new searches.
