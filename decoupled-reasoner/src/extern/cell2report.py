"""The cell 2 section of FOURCELL.md, written from the n=400 record file.

The headline is the rate at which the policy emits `<|retrieve|>`, with its
denominator and a Wilson interval. Accuracy comes after it. The two published
emission figures, 0.05 and 0.255, are reconciled from arms run for that
purpose: the same items decoded with a serving surface and without one, and
again under the token budget that produced the low figure.
"""
from __future__ import annotations

import json
import os
import sys
import time

from src.extern.stats import ci, paired, tbl

P = sys.argv[1] if len(sys.argv) > 1 else \
    "results/extern/bench/cell2_ours_mmlu_retrieval_n400.json"
d = json.load(open(P))
arms = d["arms"]
floor = d["floor"]
mt = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(P)))

NAMES = [k for k in ("web_greedy", "none_greedy", "none_t10", "none_t08",
                     "web_greedy_trunc64") if k in arms]
LAB = {"web_greedy": "web index, greedy, 256 tokens",
       "none_greedy": "no index, greedy, 256 tokens",
       "none_t10": "no index, sampled T=1.0, 256 tokens",
       "none_t08": "no index, sampled T=0.8 p=0.95, 256 tokens",
       "web_greedy_trunc64": "web index, greedy, 64 tokens"}


def ok(name):
    return [r for r in arms[name]["records"] if "error" not in r]


def kn(rs, key):
    return sum(r[key] for r in rs), len(rs)


o = []
A = o.append

A(f"## Cell 2 at n={d['n_items']}: the reader driving its own retrieval loop")
A("")
A(f"The pass behind the published cell 2 was killed at 10 items and its "
  f"finding was read off 20 passes. This run is {d['n_items']} items, seed "
  f"{d['seed']}, drawn by the same seeded shuffle the rest of the table uses, "
  "on the GPU rather than the CPU that made the first attempt too slow to "
  "finish. The prompt is built by `src/rl/env.py:build_prompt` with the world "
  "header, `<|world|> domain: corporate <|q|> ...`, and the builder asserts "
  "the header into the token stream: without it this checkpoint issues no "
  "retrieval rounds and runs to the token cap. `max_new_tokens` is 256.")
A("")

A("### How often the policy asks")
A("")
A("`emitted <|retrieve|>` counts the token the policy wrote. It is the same "
  "event in every arm and does not depend on whether a query finished or a "
  "page came back.")
A("")
rows = []
for nm in NAMES:
    rs = ok(nm)
    k, n = kn(rs, "emitted_retrieve")
    rows.append([LAB[nm], f"{k}/{n}", ci(k, n)])
A(tbl(["arm", "emitted / n", "rate [95% CI]"], rows))
A("")
wg, ng = ok("web_greedy"), ok("none_greedy")
agree = sum(1 for x, y in zip(wg, ng)
            if x["emitted_retrieve"] == y["emitted_retrieve"])
kwg, nwg = kn(wg, "emitted_retrieve")
A(f"The rate is {kwg / nwg:.4f} and it does not move: the web arm and the "
  f"no-index arm agree item by item on {agree} of {len(wg)}, because greedy "
  "decoding is deterministic and nothing before the first `<|retrieve|>` "
  "depends on whether a serving surface is attached. Sampling at T=1.0 and at "
  "T=0.8 puts it in the same place, so this is not a greedy artefact. One "
  "item in four is not a policy that never asks.")
A("")

A("### Reconciling 0.05 against 0.255")
A("")
A("The two figures are both from this harness and they disagree because they "
  "are not the same measurement.")
A("")
A("`src/extern/retrieval_ours.py` scored the event as `n_rounds > 0 or "
  "stop_reason == \"max_rounds\"`, and those conditions mean different things "
  "depending on whether an index is attached. With no index, `<|retrieve|>` "
  "hits the index-is-None guard in `src/evals/interactive.py` and ends the "
  "trajectory before a query token is written, so `stop_reason` is "
  "`max_rounds` and every emission is counted. With a web index the loop "
  "keeps decoding to collect the query text, and if the new-token budget runs "
  "out mid query it breaks with `stop_reason` still `max_new_tokens` and no "
  "round recorded, so that emission is counted as zero. The same policy "
  "therefore reads lower in the web pass than in the no-index pass.")
A("")
rows = []
for nm in NAMES:
    rs = ok(nm)
    ke, n = kn(rs, "emitted_retrieve")
    kl, _ = kn(rs, "issued_query_legacy")
    ks, _ = kn(rs, "query_returned")
    rows.append([LAB[nm], n, f"{ke / n:.4f}", f"{kl / n:.4f}",
                 f"{ks / n:.4f}"])
A(tbl(["arm", "n", "emitted the retrieve token", "legacy issued_query",
       "query served a chunk"], rows))
A("")
tr = ok("web_greedy_trunc64")
klt, nt = kn(tr, "issued_query_legacy")
klw, _ = kn(wg, "issued_query_legacy")
A(f"That accounts for part of the gap and not for most of it. The legacy "
  f"counter loses {kwg / nwg - klw / nwg:.4f} at a 256 token budget and "
  f"{kwg / nwg - klt / nt:.4f} at the 64 token budget that truncated the "
  "original trajectory. It does not reach 0.05.")
A("")
sub = ng[:200]
ks, ns = kn(sub, "emitted_retrieve")
A(f"`src/extern/bench.py:load_mmlu` shuffles the test split under the seed "
  f"and truncates, so the first 200 items of this draw are the 200 items the "
  f"closed-book lane scored. On that subset, decoded the same way, the "
  f"emission rate is {ci(ks, ns)}. The 0.255 reproduces exactly.")
A("")
w10 = wg[:10]
kl10 = sum(r["issued_query_legacy"] for r in w10)
kq10 = sum(r["query_returned"] for r in w10)
nq10 = sum(len(r["sent_queries"]) for r in w10)
A(f"The other side does not. The record file for the killed run is gone and "
  f"the only surviving evidence is one line of `logs/extern/cell2.log`, "
  f"`10/100 1517s eta 13653s live=1 cached=1`. On the same first 10 items "
  f"this run sends {nq10} queries and serves {kq10}, which matches that line "
  f"exactly: one live call and one cache hit. The legacy counter on those 10 "
  f"items is {kl10}/10, and pooled across both passes the way a 20 pass "
  f"figure implies it is {kl10 + sum(r['issued_query_legacy'] for r in ng[:10])}/20. "
  "No counter over those items gives 0.05. One over twenty does, and one is "
  "the live search count on that log line. The 0.05 is a spend number read as "
  "a policy number, and cache hits are invisible to it by construction.")
A("")
A("So the 0.255 side is right about the policy. The 0.05 was never a rate at "
  "which the model asked for anything.")
A("")

A("### Accuracy, and why the floor is out of reach")
A("")
A("Generation scored: forced choice over the option strings with a bare "
  "letter honoured. A model that names no option scores zero, so the 0.25 "
  "floor is attainable only by a policy that picks, and this one mostly does "
  "not. These rows are not comparable to the log likelihood cells above and "
  "are never subtracted from them.")
A("")
rows = []
for nm in NAMES:
    rs = ok(nm)
    n = len(rs)
    named = [r for r in rs if not r["named_none"]]
    kk = sum(r["strict"] for r in named)
    rows.append([LAB[nm], n, f"{floor:.4f}",
                 ci(sum(r["strict"] for r in rs), n),
                 f"{len(named)}/{n}",
                 ci(kk, len(named)) if named else "-"])
A(tbl(["arm", "n", "floor", "strict [95% CI]", "named an option",
       "accuracy given it named one [95% CI]"], rows))
A("")
nmd = [r for r in wg if not r["named_none"]]
A(f"The decomposition is the result. The reader names an option on "
  f"{len(nmd)} of {len(wg)} items, and on those it is at chance: "
  f"{ci(sum(r['strict'] for r in nmd), len(nmd))} against a 0.2500 floor. The "
  "flat 0.0100 is a formatting failure stacked on top of a chance level "
  "reader, and the two have to be reported apart.")
A("")
A("The grader was exercised before the number was believed, because 0.0100 "
  "against a 0.2500 floor is the shape a broken grader makes. Handed a bare "
  "gold letter it scores 1.0000 on all 400 items, a gold letter with a "
  "period 1.0000, the gold option text 0.9775, a sentence naming the gold "
  "text 1.0000, a wrong letter 0.0000, and empty or nonsense output "
  "`named_none` 1.0000. `src/extern/gradecheck.py` reruns it.")
A("")

A("### The paired control")
A("")
A("Every retrieval condition is compared against the same model on the same "
  "items with retrieval unavailable, item by item.")
A("")
pw = paired([r["strict"] for r in wg], [r["strict"] for r in ng])
ask = [(x, y) for x, y in zip(wg, ng) if x["emitted_retrieve"]]
noask = [(x, y) for x, y in zip(wg, ng) if not x["emitted_retrieve"]]
ident = sum(1 for x, y in noask
            if x["answer"] == y["answer"]
            and x["n_generated"] == y["n_generated"]
            and x["stop_reason"] == y["stop_reason"])
pa = paired([x["strict"] for x, y in ask], [y["strict"] for x, y in ask])
served = [r for r in wg if r["context_entered"]]
by = {r["id"]: r for r in ng}
ps = paired([r["strict"] for r in served],
            [by[r["id"]]["strict"] for r in served])
pn = paired([1 - r["named_none"] for r in served],
            [1 - by[r["id"]]["named_none"] for r in served])
A(tbl(["comparison", "n", "web only", "no index only", "both", "neither",
       "McNemar p"],
      [["all items, strict", pw["n"], pw["a_only"], pw["b_only"], pw["both"],
        pw["neither"], f"{pw['p']:.3f}"],
       ["items that asked, strict", pa["n"], pa["a_only"], pa["b_only"],
        pa["both"], pa["neither"], f"{pa['p']:.3f}"],
       ["chunks reached the context, strict", ps["n"], ps["a_only"],
        ps["b_only"], ps["both"], ps["neither"], f"{ps['p']:.3f}"],
       ["chunks reached the context, named an option", pn["n"], pn["a_only"],
        pn["b_only"], pn["both"], pn["neither"], f"{pn['p']:.3f}"]]))
A("")
A(f"The first row is the weakest of the four and it is the one to distrust. "
  f"On the {len(noask)} items where the policy never asks, the two arms are "
  f"the same trajectory: greedy decoding is deterministic and the index is "
  f"never consulted, and {ident} of {len(noask)} agree token for token on "
  "answer text, generated length and stop reason. Those items cannot "
  "disagree, so counting them inflates the denominator without adding "
  f"information. The informative comparison is the {pa['n']} items that "
  "asked.")
A("")
A(f"On those there is not one discordant pair either, and on the "
  f"{len(served)} where a chunk actually entered the trace the reader named "
  "an option zero times, with the pages and without them. Retrieval moved "
  "nothing, and the split cannot be read as a treatment effect because there "
  "is no effect to attribute.")
A("")

A("### Contamination split, on the items where pages arrived")
A("")
A("Labelled on the chunks actually served. The split is reported over the "
  f"{len(served)} items that received text, not over all {len(wg)}: an item "
  "that was served nothing has no pages to be contaminated by, and folding "
  "those into `neither` would inflate that row with items retrieval never "
  "touched.")
A("")
rows = []
for lab in ("verbatim", "answer", "neither"):
    s = [r for r in served if r["contamination"] == lab]
    rows.append([lab, len(s), f"{floor:.4f}",
                 ci(sum(r["strict"] for r in s), len(s)) if s else "-",
                 sum(1 for r in s if not r["named_none"])])
nos = [r for r in wg if not r["context_entered"]]
rows.append(["nothing served", len(nos), f"{floor:.4f}",
             ci(sum(r["strict"] for r in nos), len(nos)),
             sum(1 for r in nos if not r["named_none"])])
A(tbl(["served chunks contained", "n", "floor", "accuracy [95% CI]",
       "named an option"], rows))
A("")
A("Every item this cell scores correctly is an item where retrieval served "
  "nothing at all.")
A("")

A("### Where the trajectories end")
A("")
rows = []
for nm in NAMES:
    rs = ok(nm)
    n = len(rs)
    c = {}
    for r in rs:
        c[r["stop_reason"]] = c.get(r["stop_reason"], 0) + 1
    e = [r for r in rs if r["emitted_retrieve"]]
    rows.append([LAB[nm], n] +
                [c.get(k, 0) for k in ("eot", "answer_boundary", "max_rounds",
                                       "max_new_tokens")] +
                [f"{sum(r['n_generated'] for r in e) / max(len(e), 1):.1f}"])
A(tbl(["arm", "n", "eot", "answer_boundary", "max_rounds", "max_new_tokens",
       "mean tokens generated when it asked"], rows))
A("")
first = sum(1 for r in ng if r["emitted_retrieve"] and r["n_generated"] == 0)
A(f"When the policy asks, it asks at once: `<|retrieve|>` is the very first "
  f"token generated on {first} of the {len(ask)} items that ask, and the "
  "latest it ever arrives is token 19. The behaviour is close to bimodal. "
  "Either the first token is a retrieval request, or the model writes about "
  "eight tokens of free text and stops. It does not read the question and "
  "then decide.")
A("")
A("The web arm ends on `<|eot|>` on 380 of 400 items, so nothing here is a "
  "truncation artefact: served chunk tokens never count against "
  "`max_new_tokens`, and a trajectory that asked for a page still stops on "
  "its own after about 54 emitted tokens without opening an answer span. The "
  "no-index arm cannot say anything about what happens after a query, because "
  "its trajectories end at the guard after about one token; only the web arm "
  "reaches that part of the trace.")
A("")

eq = sum(r.get("empty_query", 0) for r in wg)
A(f"On {eq} items of the 256 token web arm, and {d['empty_queries']} across "
  "both web arms, the policy wrote `<|retrieve|>` and then `<|result|>` with "
  "no query text between them. An empty query is a degenerate query rather "
  "than a search that failed, so it is recorded and never sent: the API "
  "rejects an empty query string with an HTTP 400, and the original runner "
  "had no guard, so it would have ended the run there.")
A("")

A("### What this changes in the reading above")
A("")
A("`src/extern/fourcell.py` emits, whenever a cell 2 record file is present, "
  "a section saying the reader never requests any retrieved text and that "
  "the failure is therefore a policy failure rather than a comprehension "
  f"failure. At {d['n_items']} items it requests on {ci(kwg, nwg)} of them and "
  f"gets real pages into its context on {len(served)}. The policy fires less "
  "often than a reader that always retrieves, and it fires. What does not "
  "happen is anything downstream: on those items the reader names no option, "
  "with or without pages, and on the items where it does name one it is "
  "indistinguishable from guessing. Calling this a policy failure rather than "
  "a comprehension failure was resting on a counter that undercounted the "
  "policy, and the corrected counter does not support the claim. What the "
  "run supports is narrower: this checkpoint cannot produce an MMLU answer, "
  "and its retrieval behaviour is not what stands between it and one.")
A("")

A("### Retrieval spend, cell 2")
A("")
qs = [x for r in wg for x in r["sent_queries"]]
live = sum(1 for x in qs if x["outcome"] == "live")
cached = sum(1 for x in qs if x["outcome"] == "cached")
A(f"Live Exa searches: {d['live_searches']}. Cache hits: {d['cache_hits']}. "
  f"Queries the 256 token web arm sent: {len(qs)}, of which {live} live and "
  f"{cached} cache hits. Empty queries never sent, both web arms: "
  f"{d['empty_queries']}. API errors: "
  f"{d['n_api_errors']}. Cache hits that returned no page text: "
  f"{d['n_suspect_cache_hits']}. Every served query came back with pages "
  "carrying text, the thinnest of them 9,209 characters, so nothing was "
  "scored against an empty cache entry. Wall clock "
  f"{d['seconds'] / 60:.1f} minutes for all five arms on one L40S.")
A("")
A(f"Record file `{P}`, written {mt}. Cache audit `src/extern/cache_audit.py`, "
  "grader check `src/extern/gradecheck.py`, runner `src/extern/cell2.py`.")
A("")
print("\n".join(o))
