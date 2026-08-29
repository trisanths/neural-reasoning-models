# The retrieval gate's tie break

## What the gate is

One function decides which page the policy reads. `RetrievalService.top` in
`src/rl/env.py` calls `BM25Index.top` in `src/train/retrieval.py`, which walks
the episode's documents in order and keeps the best score under a strict
comparison:

```
for i in range(self.n_docs):
    if i in excluded: continue
    s = self.score(query, i)
    if s > best_score:
        best_score = s
        best_idx = i
```

Strict `>` means the lowest document index wins every exact tie. That is what
Lucene does with its internal ids and the docstring says so plainly: "Ties
break toward the earliest document, so retrieval is deterministic."

## What is not wrong

Reading the whole scoring path first, because three of the four candidate
faults in the brief are not present.

Okapi BM25 is implemented correctly. `term_score` at
`src/train/retrieval.py:137-147` computes
`idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))` with k1 1.5 and
b 0.75, which is the textbook formula with the textbook length normalization.
`_idf` at line 133 is the smoothed form `log(1 + (N - df + 0.5) / (df + 0.5))`,
positive for every term, larger for rarer terms.

Nothing is rounded or truncated anywhere between the score and the comparison.
`score` sums floats, `top` compares floats, and no format string, `round`, or
integer cast sits between them. The ties this gate produces are not
manufactured by precision loss.

There is no top-k and therefore no off-by-one in one. The gate returns exactly
one document per round and enforces without replacement across the rounds of a
rollout through the `served` set.

So the diagnosis is not an arithmetic bug. It is that a deterministic
order-dependent choice is being made in a place where BM25 has declined to
choose, over page sets whose order is not arbitrary.

## Why the ties are exact and universal on this family

`ta6-d*-minimal-ret.jsonl` writes every routing table from one template:

```
The Fexharv routing table.

Requests in the Fexharv office are routed by their type.

A harvka is handled by the zelmi desk.
... six rows
```

Two tables in the same episode differ only in the office name and the twelve
symbol tokens in the rows. Every other term, and the document length in
normalized terms, is identical. So for any query naming no term unique to one
of them, `score(query, table_i)` and `score(query, table_j)` are equal in IEEE
double, not merely close, and the earlier table wins.

`minimal_pages` emits the preamble and then one table per office in chain
order. The table a depth-d question needs at step i therefore sits behind the
table it needed at step 0 and loses every tie to it, in every rollout, for
every question in the file.

## The prediction, written before the paired runs

Recorded in this file before either run of `src/retrieval/rungeval.py` on
`ta6-d2-minimal-ret.jsonl`.

Under the "content" tie break a page tied k ways is served about one time in
k. On R1w depth two step one the tied group is the two tables, so the gold
page should be served on roughly half the rollouts on which the tie decides
the outcome. R1o's step one serves its gold page on 0.4175 of rollouts with
that page at position one, so R1w step one should land near 0.20 served, and
at the 0.916 accuracy given the page that R1o measures, near 0.18 step
accuracy against 0.0050 now.

Chain pass@1 pairs step zero with step one, so R1w depth two should land near
0.45 times 0.18, about 0.08.

It should not reach R1o's 0.1875 and it would be suspicious if it did. R1o
gives the needed page a deterministic advantage over its twin; a tie broken
without reference to position gives it a fair half share. The gap between
about 0.08 and 0.1875 is the part of R1o that is page order helping rather
than page order being neutral.

R1, whose page set holds the preamble and one table, has no tie to break and
should not move at all. That cell is the control on the change.
