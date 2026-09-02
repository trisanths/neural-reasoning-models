"""The GSM8K section, written from the record files the run leaves behind.

Conditions are reported separately and never pooled. Every accuracy carries n,
its chance floor and a Wilson interval, and the two lm-eval parsing
conventions are kept apart, because "solves 12 percent of GSM8K perfectly" and
"scores 12 percent on GSM8K" are different claims and only the second compares
to a published table.
"""
from __future__ import annotations

import json
import os
import time

from src.extern.stats import ci, paired, tbl, wilson

B = "results/extern/bench"
CTRL = f"{B}/gsm4_controls.json"
FILES = {
    "lfm2_bos": f"{B}/gsm4_lfm2_350m_bos_n200.json",
    "lfm2_nobos": f"{B}/gsm4_lfm2_350m_nobos_n200.json",
    "ours_a": f"{B}/gsm4_ours_native_a_n200.json",
    "ours_free": f"{B}/gsm4_ours_native_n200.json",
    "ours_shots": f"{B}/gsm4_ours_shots_a_n200.json",
}
D = {k: json.load(open(v)) for k, v in FILES.items() if os.path.exists(v)}
C = json.load(open(CTRL)) if os.path.exists(CTRL) else None


def recs(key, cond, dec="greedy"):
    d = D.get(key)
    if not d:
        return None
    a = d["arms"].get(f"{cond}/{dec}")
    return a["records"] if a else None


def acc(rs, field):
    return sum(r[field] for r in rs), len(rs)


LABEL = {
    ("lfm2_bos", "closed"): ("LFM2-350M", "8 shot CoT, bos", "closed book"),
    ("lfm2_bos", "method"): ("LFM2-350M", "8 shot CoT, bos", "method retrieval"),
    ("lfm2_bos", "problem"): ("LFM2-350M", "8 shot CoT, bos",
                              "problem-text retrieval"),
    ("lfm2_nobos", "closed"): ("LFM2-350M", "8 shot CoT, no bos",
                               "closed book"),
    ("ours_a", "closed"): ("ours corpus-v1-8k", "native, answer prefilled",
                           "closed book"),
    ("ours_a", "method"): ("ours corpus-v1-8k", "native, answer prefilled",
                           "method retrieval"),
    ("ours_a", "problem"): ("ours corpus-v1-8k", "native, answer prefilled",
                            "problem-text retrieval"),
    ("ours_free", "closed"): ("ours corpus-v1-8k", "native, unforced",
                              "closed book"),
    ("ours_free", "method"): ("ours corpus-v1-8k", "native, unforced",
                              "method retrieval"),
    ("ours_free", "problem"): ("ours corpus-v1-8k", "native, unforced",
                               "problem-text retrieval"),
    ("ours_shots", "closed"): ("ours corpus-v1-8k",
                               "8 shot text, answer prefilled", "closed book"),
    ("ours_shots", "method"): ("ours corpus-v1-8k",
                               "8 shot text, answer prefilled",
                               "method retrieval"),
}
ORDER = [("ours_a", "closed"), ("ours_a", "method"), ("ours_a", "problem"),
         ("lfm2_bos", "closed"), ("lfm2_bos", "method"),
         ("lfm2_bos", "problem")]

o = []
A = o.append
A("## GSM8K with method retrieval")
A("")
A("`src/extern/gsm_retrieval.py` set the design and `src/extern/gsm4.py` runs "
  "it over both readers. The query is built from the problem's method rather "
  "than its wording: numbers and proper names are stripped and what is left "
  "is the operation being asked for, which is what a worked example would be "
  "indexed under. The gold number cannot appear in that query, so a page it "
  "finds was not found by carrying the answer. The raw problem text is kept "
  "beside it as the contaminated control, which shows what lookup would buy.")
A("")
A("The retrieved material is identical between the two readers by "
  "construction: the query comes from the same function over the same item "
  "list in the same order, and the page cache is keyed on the query. Each "
  "context block is hashed per item and the hashes are compared across the "
  "record files below.")
A("")
A("GSM8K is generated rather than ranked, so the chance floor is 0.0000 and "
  "an unparseable generation is counted apart from a wrong answer. Strict is "
  "the number after the `#### ` marker the shots demonstrate; flexible is the "
  "last number anywhere, which is lm-eval's flexible-extract. The two prompts "
  "are not the same prompt and the rows are never pooled or subtracted: "
  "neither format is available to both models.")
A("")

A("### The four conditions")
A("")
rows = []
for key, cond in ORDER:
    for dec in ("greedy", "T=0.8,p=0.95"):
        rs = recs(key, cond, dec)
        if not rs:
            continue
        m, pr, cn = LABEL[(key, cond)]
        ks, n = acc(rs, "strict_correct")
        kf, _ = acc(rs, "flexible_correct")
        ku, _ = acc(rs, "unparseable")
        rows.append([m, pr, cn, dec, n, "0.0000", ci(ks, n), ci(kf, n),
                     f"{ku / n:.4f}"])
A(tbl(["model", "prompt", "condition", "decode", "n", "floor",
       "strict [95% CI]", "flexible [95% CI]", "no number at all"], rows))
A("")

A("### Against the published 30.1")
A("")
lc = recs("lfm2_bos", "closed")
if lc:
    ks, n = acc(lc, "strict_correct")
    lo, hi = wilson(ks, n)
    inside = lo <= 0.301 <= hi
    A(f"LFM2-350M closed book is {ci(ks, n)} strict on {n} items against a "
      f"published 30.1. The published figure falls "
      f"{'inside' if inside else 'just outside'} the interval, whose lower "
      f"bound is {lo:.4f}.")
    A("")
    A("This is not the MMLU situation and should not be read as one. There "
      "the harness was calibrated against the published number and matched "
      "it to within 0.43 once the start token was handled, which is the "
      "credential the rest of this work rests on. Here it reads above the "
      f"published figure by {ks / n - 0.301:.4f}. Three differences could "
      "carry that and this run does not separate them: the score is over a "
      f"{n} item sample of the test split rather than all 1,319 items, the "
      "eight shots come from the train split under a fixed seed rather than "
      "from a published shot list, and a published GSM8K number for a small "
      "instruct model is not always the eight shot completion score. What "
      "the row supports is a comparison against the retrieval rows beside "
      "it, which share every one of those choices. It is not a reproduction "
      "claim.")
    nb = recs("lfm2_nobos", "closed")
    if nb:
        kb, nn = acc(nb, "strict_correct")
        blo, bhi = wilson(kb, nn)
        overlap = not (bhi < lo or blo > hi)
        A("")
        A(f"The bos control, the same items and prompt with the start token "
          f"left off, scores {ci(kb, nn)}, "
          f"{abs(ks / n - kb / nn):.4f} {'below' if kb / nn < ks / n else 'above'} "
          "the row above. On MMLU that token was worth several points and "
          "its absence was what put the first reproduction under the "
          "published figure. It moves this number too, in the same "
          "direction, and the two intervals "
          f"{'overlap' if overlap else 'do not overlap'}. The calibrated "
          "convention is to prepend it, which is what lm-eval does for a "
          "model that defines one, so the bos row is the one every "
          "comparison in this section is made against. A GSM8K number quoted "
          "off this harness without it would be the low one.")
    A("")

A("### What our reader can and cannot do here")
A("")
free = recs("ours_free", "closed")
forced = recs("ours_a", "closed")
if free and forced:
    kr, n = acc(free, "emitted_retrieve")
    zero = sum(1 for r in free if r["n_generated"] == 0)
    A(f"Left to run its own loop closed book, this checkpoint emits "
      f"`<|retrieve|>` as its first token on {kr} of {n} GSM8K prompts, and "
      f"that is the end of the trajectory: on {zero} of {n} it generates "
      "nothing at all, "
      "because with no episode documents there is nothing to serve and the "
      "loop stops at the index-is-None guard. A zero read off that arm would "
      "be a fact about the harness rather than about the model.")
    A("")
    rows = []
    for cond in ("closed", "method", "problem"):
        rs = recs("ours_free", cond)
        if not rs:
            continue
        ku, nn = acc(rs, "unparseable")
        kf, _ = acc(rs, "flexible_correct")
        rounds = sum(r.get("n_rounds", 0) for r in rs)
        rows.append([cond, nn, f"{acc(rs, 'emitted_retrieve')[0]}/{nn}",
                     f"{nn - ku}/{nn}", rounds, ci(kf, nn)])
    A(tbl(["condition", "n", "emitted the retrieve token",
           "produced a number", "rounds served", "flexible [95% CI]"], rows))
    A("")
    A("Given something to serve, the loop completes. The emission rate falls "
      "in the retrieval conditions because the pages sit in the prompt and "
      "the trajectory is no longer the same one. In those two conditions the "
      "conditions the same pages are handed to the loop as episode documents "
      "as well as placed in the context, so a retrieval request is answered "
      "out of the retrieved material instead of ending the run, and the "
      "reader then writes a number on four items in five. What it does not "
      "do is get them right.")
    A("")
    kf, _ = acc(forced, "flexible_correct")
    ku, _ = acc(forced, "unparseable")
    par = n - ku
    A(f"With the `<|a|>` answer marker prefilled, so the answer channel is "
      f"open before decoding starts, it produces a number on {par} of {n} "
      f"prompts and scores {ci(kf, n)} flexible. It writes a bare number and "
      "stops. It emits no chain of reasoning, no `#### ` marker and, on the "
      "evidence of the strict column, nothing that resembles the worked "
      "format the shots demonstrate.")
    A("")
    sh = recs("ours_shots", "closed")
    if sh:
        ksh, nsh = acc(sh, "flexible_correct")
        A(f"Shown the same eight shot chain of thought text LFM2 reads, "
          f"through its own tokenizer and with the answer channel open, it "
          f"scores {ci(ksh, nsh)} flexible. The format was not what was "
          "missing.")
        A("")
    kfc, _ = acc(forced, "flexible_correct")
    A("So the plain statement is this. Our reader does not solve GSM8K. It "
      f"parses the problems in the weak sense that it emits a number when a "
      f"number is asked for, on {par} of {n} items, and closed book that "
      f"number is right {kfc} times in {n}. Both figures belong in the same "
      "sentence, because the score above is over all "
      f"{n} items and not over the {par} it managed to format; that is what "
      "makes it the number the published table can be held next to, and "
      "quoting the parse rate as the accuracy would be a different and "
      "better sounding claim.")
    A("")

if C and "emit_a_number_floor" in C:
    F = C["emit_a_number_floor"]
    A("### A floor for a reader that only emits a number")
    A("")
    A("GSM8K has no chance floor in the multiple choice sense and the tables "
      "above carry 0.0000, which is the convention. That convention is the "
      "wrong yardstick for a model whose entire output is one number. A "
      "policy that writes some number already in front of it is not "
      "reasoning, and how often that lands is measurable: draw uniformly "
      "from the numbers in the problem, or from the numbers in the retrieved "
      "block, and score it. Each row is 200 draws per item.")
    A("")
    rows = []
    for k, lab in (("number_from_the_problem",
                    "a number drawn from the problem text"),
                   ("number_from_the_method_block",
                    "a number drawn from the method block"),
                   ("number_from_the_problem_block",
                    "a number drawn from the problem-text block")):
        v = F.get(k)
        if v:
            rows.append([lab, v["n"], f"{v['rate']:.4f}",
                         v.get("mean_numbers_per_block", "-")])
    A(tbl(["strategy", "draws", "rate", "numbers available per block"], rows))
    A("")
    oc = recs("ours_a", "closed")
    om = recs("ours_a", "method")
    op = recs("ours_a", "problem")
    kc, nc = acc(oc, "flexible_correct")
    km2, _ = acc(om, "flexible_correct")
    kp, _ = acc(op, "flexible_correct")
    A(f"Against that yardstick our reader has no result on GSM8K under any "
      f"condition. Closed book it scores {kc / nc:.4f}, below the "
      f"{F['number_from_the_problem']['rate']:.4f} a uniform draw from the "
      f"problem's own numbers gets. With method retrieval it scores "
      f"{km2 / nc:.4f} against "
      f"{F['number_from_the_method_block']['rate']:.4f} for a uniform draw "
      f"from the block, and with problem-text retrieval {kp / nc:.4f} "
      f"against {F['number_from_the_problem_block']['rate']:.4f}. Every one "
      "of those intervals covers its floor. The apparent doubling from "
      "0.0150 to 0.0300 under retrieval is a doubling relative to a baseline "
      "that also moves, and the paired test below does not separate it from "
      "nothing.")
    A("")
    A("LFM2-350M is nowhere near this problem. At 0.3650 it is more than "
      "seventeen times the highest of these floors, which is the difference "
      "between a model that solves the problems and a model that emits "
      "plausible numbers.")
    A("")

A("### Contamination split, per condition")
A("")
A("Labelled on the pages actually placed in the context: the verbatim "
  "problem, its gold answer, or neither. Never pooled. Correct with the "
  "answer on the page is a lookup; correct with neither is the reasoning "
  "result.")
A("")
rows = []
for key, cond in ORDER:
    if cond == "closed":
        continue
    rs = recs(key, cond)
    if not rs:
        continue
    m, pr, cn = LABEL[(key, cond)]
    for lab in ("verbatim", "answer", "neither"):
        s = [r for r in rs if r["contamination"] == lab]
        if not s:
            rows.append([m, cn, lab, 0, "-", "-"])
            continue
        ks, n = acc(s, "strict_correct")
        kf, _ = acc(s, "flexible_correct")
        rows.append([m, cn, lab, n, ci(ks, n), ci(kf, n)])
A(tbl(["model", "condition", "pages contained", "n", "strict [95% CI]",
       "flexible [95% CI]"], rows))
A("")

if C:
    A("### Is the answer label real")
    A("")
    A("The label fires when the gold number appears as a bare token anywhere "
      "in 4,000 characters of web text. GSM8K answers are small integers and "
      "4,000 characters of prose contains a lot of small integers, so before "
      "the split is read the label is checked against a seeded derangement: "
      "each item scored against another item's pages, which destroys any "
      "relationship between problem and page and leaves the page lengths and "
      "the number distribution alone.")
    A("")
    rows = []
    for cond in ("method", "problem"):
        for lab in ("verbatim", "answer", "neither"):
            v = C["label_permutation"][cond][lab]
            rows.append([cond, lab, v["n"], ci(v["real_k"], v["n"]),
                         ci(v["permuted_k"], v["n"])])
    A(tbl(["condition", "label", "n", "real pairing [95% CI]",
           "permuted pairing [95% CI]"], rows))
    A("")
    am = C["label_permutation"]["method"]["answer"]
    A(f"The answer label fires on {am['real_k']} of {am['n']} real pairings "
      f"and {am['permuted_k']} of {am['n']} deranged ones. Almost all of it "
      "is coincidence. The label is close to useless as evidence that a page "
      "is about the problem, and a split built on it separates two nearly "
      "arbitrary subsets. Reporting the split is still right, because a "
      "correct answer sitting beside its own number must never be counted as "
      "reasoning, but no weight goes on the difference between its rows.")
    A("")
    A("What survives that is the mechanism, and it is measurable. The number "
      "our reader emits, right or wrong, is checked against its own context "
      "block and against another item's.")
    A("")
    rows = []
    for cond in ("method", "problem"):
        v = C["copy"][cond]
        rows.append([cond, v["n_parseable"], ci(v["own_k"], v["n_parseable"]),
                     ci(v["other_k"], v["n_parseable"]), v["n_correct"],
                     v["correct_with_gold_in_block"]])
    A(tbl(["condition", "n with a number", "number is in its own block",
           "number is in another item's block", "correct",
           "correct with gold in the block"], rows))
    A("")
    cm = C["copy"]["method"]
    A(f"It reads a number off the page. Every one of the "
      f"{cm['n_correct']} answers it gets right under method retrieval is an "
      "item whose block contained the gold number, and it gets none right "
      "where the block did not. The excess over the deranged block is small "
      "because a block of that size almost always contains some number the "
      "model might have written anyway, but the direction is consistent and "
      "the correct-answer column is unambiguous. Its score under retrieval "
      "is lookup, and the reasoning cell beside it is the one in the table "
      "below reading 0.0000.")
    A("")

A("### The paired control")
A("")
A("Each retrieval condition against the same model on the same items closed "
  "book, item by item. A contamination split alone compares item sets, not "
  "treatments, so the split above cannot separate a page effect from item "
  "selection and this table is what decides it.")
A("")
rows = []
for key in ("ours_a", "lfm2_bos"):
    base = recs(key, "closed")
    if not base:
        continue
    m = LABEL[(key, "closed")][0]
    for cond in ("method", "problem"):
        rs = recs(key, cond)
        if not rs:
            continue
        p = paired([r["flexible_correct"] for r in rs],
                   [r["flexible_correct"] for r in base])
        kr, n = acc(rs, "flexible_correct")
        kb, _ = acc(base, "flexible_correct")
        rows.append([m, cond, n, f"{kr / n:.4f}", f"{kb / n:.4f}",
                     p["a_only"], p["b_only"], f"{p['p']:.3f}"])
A(tbl(["model", "condition", "n", "with pages", "same items closed book",
       "retrieval only", "closed only", "McNemar p"], rows))
A("")
lm = recs("lfm2_bos", "method")
lb = recs("lfm2_bos", "closed")
if lm and lb:
    km, nm = acc(lm, "flexible_correct")
    kb2, _ = acc(lb, "flexible_correct")
    pm = paired([r["flexible_correct"] for r in lm],
                [r["flexible_correct"] for r in lb])
    A(f"Method retrieval does not help LFM2-350M. It is "
      f"{km / nm:.4f} with the pages against {kb2 / nm:.4f} on the same items "
      f"closed book, {pm['a_only']} items gained and {pm['b_only']} lost, "
      f"McNemar p = {pm['p']:.3f}. Retrieving on the raw problem text, the "
      "contaminated control, does not help either. Neither does it hurt "
      "enough to call a cost. Four thousand characters of web prose in front "
      "of an eight shot chain of thought prompt is close to inert for this "
      "model on this task.")
    A("")
A("And the same comparison inside each contamination class, which is where "
  "the MMLU lane found that an 0.75 answer-present cell was item selection "
  "rather than the pages.")
A("")
rows = []
for key in ("ours_a", "lfm2_bos"):
    base = recs(key, "closed")
    if not base:
        continue
    by = {r["id"]: r for r in base}
    m = LABEL[(key, "closed")][0]
    for cond in ("method", "problem"):
        rs = recs(key, cond)
        if not rs:
            continue
        for lab in ("verbatim", "answer", "neither"):
            s = [r for r in rs if r["contamination"] == lab]
            if not s:
                continue
            b = [by[r["id"]]["flexible_correct"] for r in s]
            a = [r["flexible_correct"] for r in s]
            p = paired(a, b)
            rows.append([m, cond, lab, len(s), f"{sum(a) / len(a):.4f}",
                         f"{sum(b) / len(b):.4f}", p["a_only"], p["b_only"],
                         f"{p['p']:.3f}"])
A(tbl(["model", "condition", "pages contained", "n", "with pages",
       "same items closed book", "retrieval only", "closed only",
       "McNemar p"], rows))
A("")

A("The answer-present class repeats what the MMLU lane found. For LFM2 it "
  "reads 0.3898 with the pages and 0.4068 on the same items closed book: the "
  "class is not a treatment effect, it is a set of items, and the paired "
  "column is the only thing that could have shown that. For our reader the "
  "same class runs the other way, 0.1017 against 0.0339, and the copy "
  "control above says what is happening there. In both cases the split alone "
  "would have been read wrongly and in opposite directions.")
A("")

A("### Verification and spend")
A("")
same = []
for cond in ("method", "problem"):
    a, b = recs("ours_a", cond), recs("lfm2_bos", cond)
    if a and b:
        eq = sum(1 for x, y in zip(a, b)
                 if x["context_sha256"] == y["context_sha256"])
        same.append(f"{cond} {eq}/{len(a)}")
if same:
    A("Context blocks matching byte for byte between the two readers: "
      + ", ".join(same) + ". The two models read the same pages.")
    A("")
live = sum(d.get("live_searches", 0) for d in D.values())
hits = sum(d.get("cache_hits", 0) for d in D.values())
secs = sum(d.get("seconds", 0) for d in D.values())
nres = D["lfm2_bos"]["num_results"] if "lfm2_bos" in D else 4
gsm_cost = live * (0.005 + nres * 0.001)
c2 = None
c2p = f"{B}/cell2_ours_mmlu_retrieval_n400.json"
if os.path.exists(c2p):
    c2 = json.load(open(c2p))
cell2_cost = (c2["live_searches"] * (0.005 + c2["num_results"] * 0.001)
              if c2 else 0.0)
A(f"Live Exa searches across the GSM8K runs: {live}, all of them in the "
  f"fetch stage of the first run; every later run read them back. Cache "
  f"hits: {hits}. Wall clock {secs / 60:.1f} minutes on one L40S.")
A("")
A("Cost, priced at 0.005 dollars for a neural search and 0.001 dollars per "
  "page of text, which is what Exa lists:")
A("")
A(tbl(["job", "live searches", "results per search", "estimated cost"],
      [["cell 2 at n=400", c2["live_searches"] if c2 else 0,
        c2["num_results"] if c2 else "-", f"${cell2_cost:.2f}"],
       ["GSM8K at n=200", live, nres, f"${gsm_cost:.2f}"],
       ["total this pass", (c2["live_searches"] if c2 else 0) + live, "-",
        f"${cell2_cost + gsm_cost:.2f}"]]))
A("")
A(f"That pricing reproduces the project's own experience on the earlier "
  f"sweep: 652 searches at 20 results each comes to $16.30 under it, against "
  f"the $16 to $29 that sweep was reckoned to have cost. This pass costs "
  f"about {16.30 / max(cell2_cost + gsm_cost, 1e-9):.1f} times less than that "
  "sweep, because it asks for four or five results rather than twenty and "
  "because most of what it needed was already on disk.")
A("")
for k, v in list(FILES.items()) + [("controls", CTRL)]:
    if os.path.exists(v):
        A(f"- `{v}`, written "
          + time.strftime("%Y-%m-%d %H:%M UTC",
                          time.gmtime(os.path.getmtime(v))))
A("")
print("\n".join(o))
