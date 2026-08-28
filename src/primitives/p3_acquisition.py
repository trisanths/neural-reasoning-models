"""Primitive 3: information acquisition.

Formulate queries, choose sources, recurse into prerequisites. The model
never reads a retrieved page for credit. It writes a source name and a
query string, and the oracle retriever decides whether that query would
have surfaced the page the task needs. Reading ability therefore cannot
inflate the score, and a model that cannot answer a single question about
a page can still score one here.

The oracle is the training retriever, src.train.retrieval.BM25Index, over
the same corpus, so what counts as retrievable is the project's own
definition and not a second one invented for this suite.

Why echoing the request fails. The catalogue is indexed by handling code,
never by common name. The need statement uses the common name; the page
that answers it names only the code; and a decoy page repeats the common
name at length while carrying nothing the need asks for. Issuing the
request verbatim ranks the decoy first. The mapping from name to code is
in the prompt, among three distractor mappings, so forming the right
query means selecting the right key rather than copying the question.
Generation measures the verbatim-copy heuristic on every item and rejects
any item that heuristic solves, and the report carries the surviving copy
baseline next to the model's score.

Two hops. The direct variant needs one query. The recursive variant hides
the answer behind a prerequisite: the code page names a protocol, and the
protocol page holds what was asked. The runner serves the first retrieved
page and calls the model a second time. Recursion is scored separately
and flagged, because noticing the protocol name in a served page is
reading, and reading is the one thing the direct score is built to
exclude.

CONTAMINATION CONTROL, faculty by faculty.

Reading and abstraction: the score reads the query, not an answer. The
gold page's content never has to be understood, applied or transferred.

Composition depth: the headline variant is one hop. The two-hop variant
is reported on its own line and never pooled into the headline.

Intent understanding: the isolated form states the need in one literal
sentence. The integrated form buries the same need in a request that must
first be parsed, which is what separates the two modes.

Missing-capability recognition: nothing is absent. Every item has a page
that answers it, and generation proves it by checking that the oracle
query retrieves it at rank one.

Temporary knowledge: single turn in the direct variant, two turns in the
recursive one, with the served page supplied verbatim.

Verification and action: no computation and no trap.

Chance control: source selection is one of four tiers, so chance is a
quarter and a constant reply is visible. Retrieval chance is measured
rather than assumed, by scoring a query drawn at random from the prompt's
own vocabulary over the same index.
"""

from __future__ import annotations

import random

from src.primitives.common import Item, invented_words, parse_fields, proportion
from src.train.retrieval import BM25Index

PRIMITIVE = "acquisition"

TIERS = [
    ("GLOSSARY", "definitions of terms used across the depot"),
    ("MANUAL", "step by step handling procedures, filed by protocol"),
    ("LEDGER", "one record per consignment, filed by handling code"),
    ("BULLETIN", "dated announcements and schedule changes"),
]
TIER_NAMES = [t[0] for t in TIERS]

INSTRUCTIONS = """You cannot see the archive. You may issue one search.
Name the tier you want searched and the exact search string to run.
Do not answer the question itself; the search is all that is asked for.
Answer with exactly these two lines:
SOURCE: one of {tiers}
QUERY: the search string"""

FOLLOWUP = """The search returned the page below. It does not answer the
question on its own. Issue one more search that will reach the page that does.
Answer with exactly these two lines:
SOURCE: one of {tiers}
QUERY: the search string"""


def _corpus(v: dict, rng: random.Random) -> tuple[list[dict], int, int]:
    """The archive, the index of the direct answer, the index of the hop page."""
    docs = [
        {"tier": "LEDGER",
         "text": f"LEDGER. Consignment {v['code']}. Handling code {v['code']} "
                 f"is recorded at bay {v['bay']}. Its {v['attr']} is "
                 f"{v['value']}. Consignment {v['code']} was accepted under "
                 f"protocol {v['proto']}."},
        {"tier": "BULLETIN",
         "text": f"BULLETIN. The {v['common']} consignments. A note on the "
                 f"{v['common']} consignments: the {v['common']} line will be "
                 f"reorganised next quarter. Nothing about the {v['common']} "
                 f"consignments changes before then. Queries about the "
                 f"{v['common']} consignments go to the depot office."},
        {"tier": "MANUAL",
         "text": f"MANUAL. Protocol {v['proto']}. A consignment handled under "
                 f"protocol {v['proto']} is inspected in {v['steps']} stages. "
                 f"Protocol {v['proto']} supersedes the older handling note."},
        {"tier": "GLOSSARY",
         "text": f"GLOSSARY. {v['attr']}. The {v['attr']} of a consignment is "
                 f"the figure entered in its ledger record. It is not the same "
                 f"as the bay number."},
    ]
    for i in range(6):
        w = invented_words(rng, 4)
        tier = TIER_NAMES[i % 4]
        docs.append({"tier": tier,
                     "text": f"{tier}. {w[0].capitalize()}. Handling code "
                             f"{w[1][:4].upper()}{rng.randrange(100, 999)} is "
                             f"recorded at bay {rng.randrange(2, 60)}. Its "
                             f"{w[2]} is {rng.randrange(10, 99)}. Filed under "
                             f"protocol {w[3][:3].upper()}-{rng.randrange(10, 99)}."})
    rng.shuffle(docs)
    direct = next(i for i, d in enumerate(docs) if d["text"].startswith("LEDGER. Consignment " + v["code"]))
    hop = next(i for i, d in enumerate(docs) if d["text"].startswith("MANUAL. Protocol " + v["proto"]))
    return docs, direct, hop


def _rank(index: BM25Index, query: str, k: int) -> list[int]:
    scored = sorted(range(index.n_docs),
                    key=lambda i: (-index.score(query, i), i))
    return scored[:k]


def generate(seed: int, mode: str = "isolated", variant: str = "direct") -> Item:
    rng = random.Random(seed * 104729 + 7)
    w = invented_words(rng, 6)
    v = {"common": w[0], "attr": w[1], "bay": rng.randrange(2, 60),
         "value": rng.randrange(100, 999),
         "code": f"{w[2][:4].upper()}{rng.randrange(100, 999)}",
         "proto": f"{w[3][:3].upper()}-{rng.randrange(10, 99)}",
         "steps": rng.randrange(3, 9)}
    docs, direct, hop = _corpus(v, rng)

    others = invented_words(rng, 6)
    mappings = [(v["common"], v["code"])]
    for i in range(3):
        mappings.append((others[i],
                         f"{others[i + 3][:4].upper()}{rng.randrange(100, 999)}"))
    rng.shuffle(mappings)
    note = ("The archive indexes consignments by handling code, never by "
            "common name. The handling codes on file are: "
            + "; ".join(f"{n} is {c}" for n, c in mappings) + ".")

    catalogue = "\n".join(f"  {name}: {desc}" for name, desc in TIERS)
    if variant == "direct":
        need = (f"Find the page that gives the {v['attr']} of the "
                f"{v['common']} consignment.")
        gold_doc, gold_tier = direct, docs[direct]["tier"]
    else:
        need = (f"Find the page that gives the number of inspection stages "
                f"used for the {v['common']} consignment.")
        gold_doc, gold_tier = hop, docs[hop]["tier"]

    if mode == "integrated":
        need = (f"Someone in the office wants to know about the {v['common']} "
                f"consignment. They were vague. What they need in the end is "
                + need[len("Find the page that gives "):].rstrip(".")
                + ", and they do not know where it is filed.")

    question = (INSTRUCTIONS.format(tiers=", ".join(TIER_NAMES))
                + "\n\nArchive tiers.\n" + catalogue
                + "\n\nIndexing note.\n" + note
                + "\n\nWhat is needed.\n" + need)

    # The first turn is always scored against the ledger page, which the
    # handling code reaches. The recursive variant's answer lives one page
    # further on, behind the protocol name only that ledger page carries,
    # so its oracle first query is the same code and its hop query is the
    # protocol. Both are checked below.
    texts = [d["text"] for d in docs]
    index = BM25Index(texts)
    copy_rank = _rank(index, need, 3)
    first_query = v["code"]
    first_rank = _rank(index, first_query, 1)
    hop_rank = _rank(index, v["proto"], 1)

    return Item(
        item_id=f"p3-{mode}-{variant}-{seed:07d}",
        primitive=PRIMITIVE, variant=variant, mode=mode,
        question=question, chunks=[],
        gold={"doc": gold_doc, "tier": gold_tier,
              "first_doc": direct, "first_tier": docs[direct]["tier"],
              "first_query": first_query, "oracle_query": first_query,
              "hop_query": v["proto"], "hop_doc": hop,
              "hop_tier": docs[hop]["tier"]},
        meta={"seed": seed, "docs": texts,
              "followup": FOLLOWUP.format(tiers=", ".join(TIER_NAMES)),
              "served_text": texts[direct],
              "copy_hits": copy_rank[0] == direct,
              "copy_top3": direct in copy_rank,
              "oracle_hits": (first_rank[0] == direct
                              and hop_rank[0] == hop)},
    )


def generate_many(n: int, seed: int = 0, mode: str = "isolated",
                  variant: str = "direct") -> list[Item]:
    """n items where the verbatim-copy heuristic fails and the oracle query wins."""
    out: list[Item] = []
    s = seed
    tried = 0
    while len(out) < n and tried < n * 60:
        tried += 1
        item = generate(s, mode=mode, variant=variant)
        s += 1
        if item.meta["copy_hits"] or not item.meta["oracle_hits"]:
            continue
        out.append(item)
    if len(out) < n:
        raise RuntimeError(f"only {len(out)} of {n} acquisition items passed the guard")
    return out


def _query_of(response: str) -> tuple[str | None, str]:
    f = parse_fields(response)
    src = None
    for name in TIER_NAMES:
        if name.lower() in f.get("SOURCE", "").lower():
            src = name
            break
    return src, f.get("QUERY", "").strip()


def grade(item: Item, response: str, followup: str | None = None) -> dict:
    """Score the query the model issued, never an answer it gave."""
    index = BM25Index(item.meta["docs"])
    src, query = _query_of(response)
    g = item.gold
    hop = item.variant == "recursive"
    want_first = g["first_doc"] if hop else g["doc"]
    want_tier = g["first_tier"] if hop else g["tier"]

    rank = _rank(index, query, 3) if query else []
    out = {
        "parsed": bool(query),
        "source": float(src == want_tier),
        "hit1": float(bool(rank) and rank[0] == want_first),
        "hit3": float(want_first in rank),
        "empty_query": float(not query),
        "echoed": float(bool(query) and query.strip() == item.question.strip()),
        "recursive": hop,
    }
    if hop:
        out["hop_source"] = 0.0
        out["hop_hit1"] = 0.0
        if followup is not None:
            src2, q2 = _query_of(followup)
            r2 = _rank(index, q2, 3) if q2 else []
            out["hop_source"] = float(src2 == g["hop_tier"])
            out["hop_hit1"] = float(bool(r2) and r2[0] == g["hop_doc"])
            out["hop_parsed"] = bool(q2)
    return out


def aggregate(items: list[Item], grades: list[dict]) -> dict:
    if not items:
        return {"primitive": PRIMITIVE, "n": 0}
    n = len(grades)
    copy1 = sum(int(i.meta["copy_hits"]) for i in items)
    copy3 = sum(int(i.meta["copy_top3"]) for i in items)
    out = {
        "primitive": PRIMITIVE, "mode": items[0].mode,
        "variant": items[0].variant, "n": n,
        "source_selection": proportion(sum(int(g["source"]) for g in grades), n,
                                       1.0 / len(TIER_NAMES), "source_selection"),
        "recall_at1": proportion(sum(int(g["hit1"]) for g in grades), n, 0.0,
                                 "recall@1"),
        "recall_at3": proportion(sum(int(g["hit3"]) for g in grades), n, 0.0,
                                 "recall@3"),
        "copy_baseline_at1": proportion(copy1, n, 0.0, "copy_baseline@1"),
        "copy_baseline_at3": proportion(copy3, n, 0.0, "copy_baseline@3"),
        "empty_query": proportion(sum(int(g["empty_query"]) for g in grades), n,
                                  0.0, "empty_query"),
        "parse_rate": proportion(sum(int(g["parsed"]) for g in grades), n, 0.0,
                                 "parse_rate"),
    }
    out["headline"] = out["recall_at1"]["acc"] - out["copy_baseline_at1"]["acc"]
    if items[0].variant == "recursive":
        out["hop_recall_at1"] = proportion(
            sum(int(g.get("hop_hit1", 0.0)) for g in grades), n, 0.0,
            "hop_recall@1")
        out["hop_source"] = proportion(
            sum(int(g.get("hop_source", 0.0)) for g in grades), n,
            1.0 / len(TIER_NAMES), "hop_source")
        out["note"] = ("hop scores require reading the served page and are "
                       "therefore contaminated by reading ability; they are "
                       "never folded into the headline")
    return out


CONTAMINATION = __doc__
