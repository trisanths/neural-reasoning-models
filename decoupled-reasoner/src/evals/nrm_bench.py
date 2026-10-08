"""NRM task benchmark: answer a question given ACCESS to a knowledge source.

This is the project's primary metric. An item is a question, a set of
accepted gold answer forms, and a binding to a knowledge source that is
NOT in the model's context. The model must drive the emit-query-read loop
of src/evals/interactive.py to reach the evidence, then answer. Scoring is
mechanical: normalized exact match with a contains fallback, plus evidence
grounding, retrieval efficiency, abstention quality, and cost.

Why this replaces the naturalized reading gate
----------------------------------------------
The old gate (src/evals/naturalized.py) put a passage in the context
window, let the model free-run a continuation, and scored contains-answer
against a conventional autoregressive LM of similar size. Three things are
wrong with that as this project's headline number.

First, it measures reading with the evidence already selected. Nothing in
it exercises query formulation, retrieval, or evidence selection, which is
where a Neural Reasoning Model does its work: the entire world's knowledge
sits behind an interface, not in the weights and not in the prompt.

Second, scoring free-running prose against a conventional LM measures
LLM-likeness. A model that produces fluent continuations scores well; a
model that emits a query, reads a result, and returns a bare answer string
scores badly on the same evidence. That is the wrong direction of pressure
for a system whose output should be a short verified answer with a
citation.

Third, it cannot distinguish knowing from looking up. With the passage in
context, a memorized fact and a retrieved fact produce the same score. The
controls here separate them: the oracle-context control puts the gold
document in the context and upper-bounds what the reading ability allows;
the retrieval-free control removes the knowledge source entirely and
measures what the weights alone hold. The gap between oracle-context and
full-retrieval isolates query formulation from extraction. The gap between
oracle-context and retrieval-free isolates extraction from memory.

The naturalized suite stays useful as a reading probe. It is no longer the
gate.

Suites
------
synthetic_world  Held-out worldgen episodes (src/worldgen). Tasks are
                 single-hop, multi-hop over 2 to 4 derivation hops,
                 temporal ordering, counting, source arbitration where a
                 low-reliability document contradicts a reliable one, and
                 unanswerable items whose supporting documents have been
                 removed from the binding. The knowledge source is the
                 episode's document set behind the training BM25 oracle,
                 never in context.
scrubbed_web     Held-out scrubbed-web bundles (src/scrub/web_retrieval)
                 over real-register prose with fact-scrubbed entities.
                 Same structure, answers are verbatim spans.
real_web         Authored questions over stable public facts, bound to the
                 live Exa tier (src/retrieval_web). Answerable only through
                 retrieval by construction: the checkpoints train on
                 fact-scrubbed text where entity names are reassigned per
                 document, so name-to-fact associations are destroyed
                 before training sees them. The retrieval-free control
                 measures that claim on every run rather than assuming it.

Conditions
----------
All three run through one interface, run_item(item, runner_ctx, condition):

retrieval       the knowledge source is reachable only through the loop
no_retrieval    same prompt, no knowledge source; a query is answered with
                an explicit miss, so the answer comes from the weights
oracle_context  the gold documents are pasted into the context before the
                question, and queries again come back empty

The controls answer a query rather than refusing it because the decode
loop ends the moment a <|retrieve|> arrives with nothing behind it, and
these checkpoints are trained to retrieve before answering. An unserved
control would therefore score zero for every model whatever it knows, and
both diagnostic gaps would collapse. See EmptyResultIndex.

Determinism: decoding is greedy, suite construction is seeded, and the web
tier is disk-cached and budget-capped, so a rerun over a warm cache issues
no live searches and reproduces the previous numbers exactly.
"""

import json
import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path

from src.evals.interactive import generate_with_retrieval
from src.evals.naturalized import contains_answer, exact_match, normalize
from src.train.data import render_world_preamble

SUITES = ("synthetic_world", "scrubbed_web", "real_web")

TASKS = ("single_hop", "multi_hop", "temporal", "counting", "arbitration",
         "span", "unanswerable")

CONDITIONS = ("retrieval", "no_retrieval", "oracle_context")

# The real-web prompt uses a training domain name on purpose:
# scripts/diag_webdemo.py showed an out-of-vocabulary preamble suppresses
# query emission entirely, so the header stays inside the training
# distribution and the retrieve habit can fire.
REAL_WEB_PREAMBLE = "domain: corporate"
SCRUBBED_WEB_PREAMBLE = "domain: scrubbed_web"

# An answer counts as an abstention when it normalizes to one of these, or
# begins with one of them. Short list on purpose: a model that hedges in
# prose is confabulating, not abstaining.
ABSTENTION_FORMS = (
    "unknown", "unsure", "not known", "not stated", "not in the documents",
    "no answer", "cannot answer", "can not answer", "i do not know",
    "i don t know", "insufficient evidence", "no evidence",
)

NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six",
                "seven", "eight", "nine", "ten", "eleven", "twelve"]

DEFAULT_MAX_ROUNDS = 3
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_CHUNK_TOKENS = 256
DEFAULT_NUM_RESULTS = 5
CHUNK_PREVIEW_CHARS = 200


# ---------------------------------------------------------------- items


@dataclass
class BenchItem:
    """One benchmark item: a question, its gold forms, and a source binding.

    documents are the knowledge source for episode-bound items, in the
    worldgen document dict shape ({"text", "reliability", ...}); web-bound
    items carry none and take their source from the run context's web index
    factory. oracle_docs are the documents the oracle-context control
    pastes into the prompt. evidence_strings are the strings that must show
    up in served evidence for the item to count as grounded, which for a
    counting item is the things counted rather than the number.
    """

    item_id: str
    suite: str
    task: str
    question: str
    golds: list
    preamble: str = ""
    documents: list = field(default_factory=list)
    oracle_docs: list = field(default_factory=list)
    evidence_strings: list = field(default_factory=list)
    distractor_strings: list = field(default_factory=list)
    trap_strings: list = field(default_factory=list)
    unanswerable: bool = False
    web: bool = False
    n_hops: int = 1
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.suite not in SUITES:
            raise ValueError(f"unknown suite {self.suite!r}")
        if self.task not in TASKS:
            raise ValueError(f"unknown task {self.task!r}")
        if not self.golds:
            raise ValueError(f"item {self.item_id} has no gold answer forms")
        if not self.evidence_strings:
            self.evidence_strings = [self.golds[0]]

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id, "suite": self.suite, "task": self.task,
            "question": self.question, "golds": list(self.golds),
            "unanswerable": bool(self.unanswerable), "web": bool(self.web),
            "n_hops": int(self.n_hops),
            "n_documents": len(self.documents),
            "evidence_strings": list(self.evidence_strings),
            "distractor_strings": list(self.distractor_strings),
            "trap_strings": list(self.trap_strings),
            "meta": dict(self.meta),
        }


def is_abstention(answer: str) -> bool:
    """True when the answer declines rather than asserting something.

    An empty answer counts: producing nothing is not producing a claim.
    Otherwise the whole normalized answer must be a decline form, or a
    short phrase ending in one ("the acquirer is unknown"). A decline word
    that merely opens a longer assertion ("unknown company acquired
    Reyner") is an assertion.
    """
    norm = normalize(answer)
    if not norm:
        return True
    if norm in ABSTENTION_FORMS:
        return True
    if len(norm.split()) <= 6:
        return any(norm.endswith(" " + form) for form in ABSTENTION_FORMS)
    return False


def number_forms(n: int) -> list:
    """Accepted surface forms of a count."""
    forms = [str(n)]
    if 0 <= n < len(NUMBER_WORDS):
        forms.append(NUMBER_WORDS[n])
    return forms


def stratum_key(item: BenchItem) -> tuple:
    """The split a subsample has to keep proportional: suite and task.

    These are the buckets the metric tables report, so a slice that
    distorts them reports numbers that do not stand for the full suite.
    """
    return (item.suite, item.task)


def facet_key(item: BenchItem) -> str:
    """The generator's own label for what an item is about.

    A category for the authored real-web questions, a world domain for the
    episode suites. Subject spread inside a task, not a reported split.
    """
    return item.meta.get("category") or item.meta.get("domain") or ""


def _allocate(sizes: dict, n: int) -> dict:
    """Largest-remainder split of n slots over strata, floored at one each.

    Every stratum that fits gets a slot before proportionality is served,
    so a small slice still covers every task. With more strata than slots
    the largest strata take them.
    """
    names = sorted(sizes)
    if len(names) >= n:
        return {s: 1 for s in sorted(names, key=lambda s: (-sizes[s], s))[:n]}
    total = sum(sizes.values())
    exact = {s: sizes[s] * n / total for s in names}
    alloc = {s: min(sizes[s], max(1, int(exact[s]))) for s in names}
    while sum(alloc.values()) < n:
        room = [s for s in names if alloc[s] < sizes[s]]
        if not room:
            break
        alloc[max(room, key=lambda s: (exact[s] - alloc[s], s))] += 1
    while sum(alloc.values()) > n:
        room = [s for s in names if alloc[s] > 1]
        if not room:
            break
        alloc[min(room, key=lambda s: (exact[s] - alloc[s], s))] -= 1
    return alloc


def subsample(items, n: int, seed: int = 0, key=stratum_key,
              facet=facet_key) -> list:
    """At most n items, cut so the slice still stands for the full suite.

    A head slice is the wrong way to shrink a suite. Items arrive grouped
    by generator, so the first n of them cover a few domains and drop whole
    task families. The authored real-web file keeps its unanswerable
    questions last, so any head slice shorter than the file scores
    abstention on nothing at all.

    Two levels. Slots go to (suite, task) strata by largest remainder with
    one slot floored per stratum, which holds the reported splits near
    their true proportions and still covers every task. Inside a stratum
    the quota is dealt round-robin across facets, so categories and world
    domains spread as evenly as the quota allows instead of clumping.
    Selection is a seeded shuffle and the result keeps the input order, so
    a slice is reproducible and reads in suite order.
    """
    items = list(items)
    if not n or n >= len(items):
        return items

    groups: dict = {}
    for index, item in enumerate(items):
        groups.setdefault(key(item), []).append(index)
    alloc = _allocate({s: len(v) for s, v in groups.items()}, n)

    rng = random.Random(seed)
    chosen: set = set()
    for name in sorted(alloc):
        by_facet: dict = {}
        for index in groups[name]:
            by_facet.setdefault(facet(items[index]), []).append(index)
        queues = []
        for label in sorted(by_facet):
            queue = list(by_facet[label])
            rng.shuffle(queue)
            queues.append(queue)
        rng.shuffle(queues)
        taken = 0
        while taken < alloc[name]:
            progressed = False
            for queue in queues:
                if not queue:
                    continue
                chosen.add(queue.pop())
                taken += 1
                progressed = True
                if taken == alloc[name]:
                    break
            if not progressed:
                break
    return [item for i, item in enumerate(items) if i in chosen]


# ------------------------------------------------- synthetic world suite


def _docs_touching(episode: dict, fact_ids: set) -> list:
    """Positions of documents supporting or contradicting any of the facts."""
    out = []
    for i, doc in enumerate(episode.get("documents", [])):
        touched = set(doc.get("supports", [])) | set(doc.get("contradicts", []))
        if touched & fact_ids:
            out.append(i)
    return out


def _supporting_docs(episode: dict, fact_ids) -> list:
    """Document dicts supporting the given facts, in episode order."""
    wanted = set(fact_ids)
    return [doc for doc in episode.get("documents", [])
            if wanted & set(doc.get("supports", []))]


def _name_map(episode: dict) -> dict:
    return {e["id"]: e["name"] for e in episode["world"].get("entities", [])}


def _facts_by_predicate(episode: dict, predicate: str) -> list:
    return [f for f in episode["world"].get("facts", [])
            if f["p"] == predicate]


def _contradicted_facts(episode: dict) -> set:
    out = set()
    for doc in episode.get("documents", []):
        out.update(doc.get("contradicts", []))
    return out


def _evidence_chain(episode: dict, derivation) -> list:
    """Entity names named by the derivation's facts, in hop order.

    These are the strings retrieval has to deliver for a multi-hop item to
    be grounded, not just the final answer.
    """
    name_of = _name_map(episode)
    facts = {f["id"]: f for f in episode["world"].get("facts", [])}
    seen = []
    for fid in derivation:
        fact = facts.get(fid)
        if fact is None:
            continue
        for side in ("s", "o"):
            value = fact[side]
            name = name_of.get(value, str(value))
            if name not in seen:
                seen.append(name)
    return seen


def _temporal_items(episode: dict, prefix: str) -> list:
    """Ordering questions over two facts with distinct periods.

    Corporate episodes order two acquisitions, kinship episodes order two
    birth years, regulatory episodes order two restrictions inside one
    jurisdiction. Each item's answer is an entity name that both candidate
    documents make available, so scoring stays mechanical.
    """
    domain = episode["world"]["domain"]
    name_of = _name_map(episode)
    items = []

    def add(question, gold, derivation, evidence, options):
        items.append(BenchItem(
            item_id=f"{prefix}-temporal-{len(items) + 1}",
            suite="synthetic_world", task="temporal", question=question,
            golds=[gold], preamble=render_world_preamble(episode["world"]),
            documents=list(episode["documents"]),
            oracle_docs=[d["text"] for d in _supporting_docs(episode, derivation)],
            evidence_strings=evidence,
            distractor_strings=[o for o in options if o != gold],
            n_hops=len(derivation),
            meta={"derivation": list(derivation), "domain": domain}))

    if domain == "corporate":
        acqs = _facts_by_predicate(episode, "acquired")
        pairs = [(a, b) for i, a in enumerate(acqs) for b in acqs[i + 1:]
                 if a["t"] != b["t"]]
        for a, b in pairs[:1]:
            first, second = (a, b) if a["t"] < b["t"] else (b, a)
            add(f"Which company was acquired earlier, "
                f"{name_of[first['o']]} or {name_of[second['o']]}?",
                name_of[first["o"]], [first["id"], second["id"]],
                [name_of[first["o"]], name_of[second["o"]]],
                [name_of[first["o"]], name_of[second["o"]]])
    elif domain == "kinship_temporal":
        borns = _facts_by_predicate(episode, "born_in_year")
        pairs = [(a, b) for i, a in enumerate(borns) for b in borns[i + 1:]
                 if int(a["o"]) != int(b["o"])]
        for a, b in pairs[:1]:
            first, second = (a, b) if int(a["o"]) < int(b["o"]) else (b, a)
            add(f"Who was born earlier, {name_of[first['s']]} or "
                f"{name_of[second['s']]}?",
                name_of[first["s"]], [first["id"], second["id"]],
                [str(first["o"]), str(second["o"])],
                [name_of[first["s"]], name_of[second["s"]]])
    elif domain == "regulatory":
        restricts = _facts_by_predicate(episode, "restricts")
        by_jur: dict = {}
        for fact in restricts:
            by_jur.setdefault(fact["s"], []).append(fact)
        for jur, facts in sorted(by_jur.items()):
            pairs = [(a, b) for i, a in enumerate(facts) for b in facts[i + 1:]
                     if a["t"] != b["t"]]
            if not pairs:
                continue
            a, b = pairs[0]
            first, second = (a, b) if a["t"] < b["t"] else (b, a)
            add(f"Which substance did {name_of[jur]} restrict earlier, "
                f"{name_of[first['o']]} or {name_of[second['o']]}?",
                name_of[first["o"]], [first["id"], second["id"]],
                [name_of[first["o"]], name_of[second["o"]]],
                [name_of[first["o"]], name_of[second["o"]]])
            break
    return items


def _counting_items(episode: dict, prefix: str) -> list:
    """Counting questions over one subject's outgoing facts.

    Only built when no document in the episode contradicts any counted
    fact, so a counting item never doubles as an arbitration item.
    """
    domain = episode["world"]["domain"]
    name_of = _name_map(episode)
    contradicted = _contradicted_facts(episode)
    spec = {
        "corporate": ("acquired",
                      "How many companies did {name} acquire?"),
        "regulatory": ("restricts",
                       "How many substances does {name} restrict directly?"),
        "logistics": ("route_to",
                      "How many outbound routes does {name} have?"),
    }.get(domain)
    if spec is None:
        return []
    predicate, template = spec
    by_subject: dict = {}
    for fact in _facts_by_predicate(episode, predicate):
        by_subject.setdefault(fact["s"], []).append(fact)
    items = []
    for subject, facts in sorted(by_subject.items(), key=lambda kv: -len(kv[1])):
        if len(facts) < 2 or any(f["id"] in contradicted for f in facts):
            continue
        derivation = [f["id"] for f in facts]
        items.append(BenchItem(
            item_id=f"{prefix}-count-1",
            suite="synthetic_world", task="counting",
            question=template.format(name=name_of[subject]),
            golds=number_forms(len(facts)),
            preamble=render_world_preamble(episode["world"]),
            documents=list(episode["documents"]),
            oracle_docs=[d["text"] for d in _supporting_docs(episode, derivation)],
            evidence_strings=[name_of.get(f["o"], str(f["o"])) for f in facts],
            n_hops=len(facts),
            meta={"derivation": derivation, "domain": domain,
                  "count": len(facts)}))
        break
    return items


def _arbitration_items(episode: dict, prefix: str) -> list:
    """Lookup questions whose supporting fact is contradicted in the corpus.

    The contradicting document is low reliability by construction, so the
    reliability-weighted oracle should rank the true document first; the
    item records the corrupted value as a distractor so the harness can
    tell an arbitration failure from an ordinary miss.
    """
    contradicted = _contradicted_facts(episode)
    if not contradicted:
        return []
    name_of = _name_map(episode)
    facts = {f["id"]: f for f in episode["world"].get("facts", [])}
    items = []
    for question in episode.get("questions", []):
        derivation = question.get("derivation") or []
        if len(derivation) != 1 or derivation[0] not in contradicted:
            continue
        fid = derivation[0]
        distractors = []
        for doc in episode["documents"]:
            if fid not in doc.get("contradicts", []):
                continue
            true_names = {name_of.get(facts[fid][s], str(facts[fid][s]))
                          for s in ("s", "o")}
            for name in name_of.values():
                if name in doc["text"] and name not in true_names:
                    distractors.append(name)
        items.append(BenchItem(
            item_id=f"{prefix}-arb-{question['qid']}",
            suite="synthetic_world", task="arbitration",
            question=question["text"], golds=[question["answer"]],
            preamble=render_world_preamble(episode["world"]),
            documents=list(episode["documents"]),
            oracle_docs=[d["text"] for d in _supporting_docs(episode, derivation)],
            evidence_strings=[question["answer"]],
            distractor_strings=sorted(set(distractors)),
            n_hops=1,
            meta={"derivation": derivation,
                  "domain": episode["world"]["domain"]}))
        break
    return [i for i in items if i.distractor_strings]


def _unanswerable_item(episode: dict, prefix: str):
    """A question whose evidence has been removed from the binding.

    Every document that supports or contradicts the question's derivation
    is dropped from the item's knowledge source, and so is any remaining
    document that happens to state the answer string, so the source
    genuinely cannot support an answer and the gold is "unknown". The true
    answer is recorded as a trap string: a model that produces it is
    answering from weights, not from evidence.
    """
    for question in episode.get("questions", []):
        derivation = question.get("derivation") or []
        if not derivation:
            continue
        drop = set(_docs_touching(episode, set(derivation)))
        drop |= {i for i, d in enumerate(episode["documents"])
                 if question["answer"] in d["text"]}
        kept = [d for i, d in enumerate(episode["documents"]) if i not in drop]
        if len(kept) < 3:
            continue
        return BenchItem(
            item_id=f"{prefix}-unans-{question['qid']}",
            suite="synthetic_world", task="unanswerable",
            question=question["text"], golds=["unknown"],
            preamble=render_world_preamble(episode["world"]),
            documents=kept, oracle_docs=[],
            evidence_strings=["unknown"],
            trap_strings=[question["answer"]],
            unanswerable=True, n_hops=0,
            meta={"removed_documents": len(drop),
                  "domain": episode["world"]["domain"],
                  "withheld_answer": question["answer"]})
    return None


def build_synthetic_suite(episodes, max_hops: int = 4,
                          unanswerable_every: int = 4) -> list:
    """Build the synthetic-world suite from held-out worldgen episodes.

    Every episode contributes its lookup and multi-hop questions (2 to
    max_hops derivation hops), plus whichever of the derived task families
    that episode's domain supports: temporal ordering, counting, and source
    arbitration. Every unanswerable_every-th episode also contributes one
    unanswerable item. Deterministic in the episode list.
    """
    items = []
    for ep_index, episode in enumerate(episodes):
        prefix = episode.get("episode_id", f"ep{ep_index}")
        preamble = render_world_preamble(episode["world"])
        documents = list(episode["documents"])
        for question in episode.get("questions", []):
            derivation = question.get("derivation") or []
            hops = len(derivation)
            if hops == 1:
                task = "single_hop"
            elif 2 <= hops <= max_hops:
                task = "multi_hop"
            else:
                continue
            items.append(BenchItem(
                item_id=f"{prefix}-{question['qid']}",
                suite="synthetic_world", task=task,
                question=question["text"], golds=[question["answer"]],
                preamble=preamble, documents=documents,
                oracle_docs=[d["text"]
                             for d in _supporting_docs(episode, derivation)],
                evidence_strings=(_evidence_chain(episode, derivation)
                                  if hops > 1 else [question["answer"]]),
                n_hops=hops,
                meta={"derivation": derivation,
                      "domain": episode["world"]["domain"],
                      "question_type": question.get("type", "")}))
        items.extend(_temporal_items(episode, prefix))
        items.extend(_counting_items(episode, prefix))
        items.extend(_arbitration_items(episode, prefix))
        if unanswerable_every and ep_index % unanswerable_every == 0:
            unans = _unanswerable_item(episode, prefix)
            if unans is not None:
                items.append(unans)
    return items


# -------------------------------------------------- scrubbed web suite


def build_scrubbed_web_suite(bundles, seed: int = 0, n_questions: int = 3,
                             two_hop_share: float = 0.35,
                             unanswerable_every: int = 5) -> list:
    """Build the scrubbed-web suite from held-out document bundles.

    bundles is an iterable of lists of scrubbed document texts, the same
    shape src/scrub/web_retrieval builds regime E3 episodes from. Each
    bundle becomes one episode through build_web_episode, which plans and
    verifies every hop against the BM25 index, so an item's evidence is
    reachable by construction. Held out means the bundle seeds are outside
    the training render's seed space; the underlying corpus is shared, and
    the entity scrub reassigns names per document anyway.

    Every unanswerable_every-th bundle also yields one unanswerable item,
    built by dropping the target document from the binding.
    """
    from src.scrub.web_retrieval import build_web_episode

    items = []
    state: dict = {}
    for b_index, doc_texts in enumerate(bundles):
        doc_texts = list(doc_texts)
        if len(doc_texts) < 3:
            continue
        episode = build_web_episode(
            doc_texts, (int(seed), b_index), n_questions=n_questions,
            two_hop_share=two_hop_share, query_first=True, state=state)
        prefix = f"web{b_index:04d}"
        for q_index, question in enumerate(episode["questions"]):
            plan = question["plan"]
            target = plan[-1][1]
            chain = [doc_texts[d] for _, d in plan]
            items.append(BenchItem(
                item_id=f"{prefix}-q{q_index + 1}",
                suite="scrubbed_web",
                task="span" if len(plan) == 1 else "multi_hop",
                question=question["text"], golds=[question["answer"]],
                preamble=SCRUBBED_WEB_PREAMBLE,
                documents=[{"text": t} for t in doc_texts],
                oracle_docs=chain,
                evidence_strings=[question["answer"]],
                n_hops=len(plan),
                meta={"span_kind": question.get("span_kind", ""),
                      "target_doc": target}))
        if (unanswerable_every and b_index % unanswerable_every == 0
                and episode["questions"]):
            question = episode["questions"][0]
            kept = [t for t in doc_texts if question["answer"] not in t]
            if len(kept) < 3:
                continue
            items.append(BenchItem(
                item_id=f"{prefix}-unans",
                suite="scrubbed_web", task="unanswerable",
                question=question["text"], golds=["unknown"],
                preamble=SCRUBBED_WEB_PREAMBLE,
                documents=[{"text": t} for t in kept], oracle_docs=[],
                evidence_strings=["unknown"],
                trap_strings=[question["answer"]],
                unanswerable=True, n_hops=0,
                meta={"removed_documents": len(doc_texts) - len(kept),
                      "withheld_answer": question["answer"]}))
    return items


# ------------------------------------------------------ real web suite


def default_real_web_path() -> Path:
    return Path(__file__).parent / "data" / "nrm_bench" / "real_web.json"


def load_real_web_suite(path=None, limit: int | None = None) -> list:
    """Load the authored real-web questions as bench items.

    Each record carries id, category, question, golds, and an evidence
    sentence stating the fact in neutral prose. The evidence sentence is
    the oracle-context document: it upper-bounds extraction the same way a
    gold passage does in the episode suites, and it is authored rather than
    retrieved so the control does not depend on what search returns today.
    Records with "unanswerable": true name entities that do not exist, so
    no knowledge source can support them; their gold is "unknown".
    """
    path = Path(path) if path else default_real_web_path()
    with open(path) as fh:
        records = json.load(fh)
    items = []
    for record in records[:limit] if limit else records:
        unanswerable = bool(record.get("unanswerable"))
        golds = ["unknown"] if unanswerable else list(record["golds"])
        evidence = record.get("evidence", "")
        items.append(BenchItem(
            item_id=record["id"], suite="real_web",
            task="unanswerable" if unanswerable else "single_hop",
            question=record["question"], golds=golds,
            preamble=REAL_WEB_PREAMBLE, documents=[],
            oracle_docs=[evidence] if evidence else [],
            evidence_strings=(["unknown"] if unanswerable
                              else list(record["golds"])),
            trap_strings=list(record.get("traps", [])),
            unanswerable=unanswerable, web=True, n_hops=1,
            meta={"category": record.get("category", "")}))
    return items


# ------------------------------------------------------- web plumbing


NO_RESULTS_TEXT = "no results"


class EmptyResultIndex:
    """Serving surface for the controls: every query comes back empty.

    The controls have no knowledge source, but they still have to let the
    model finish. src/evals/interactive.py ends the decode the moment a
    <|retrieve|> arrives with nothing behind it, and these checkpoints are
    trained to retrieve before answering, so an unserved control scores
    zero for every model whatever it knows: the answer slot is never
    reached. That measures the retrieve habit, not extraction or memory,
    and it would flatten both diagnostic gaps to nothing.

    Answering the query with an explicit miss is the honest version of no
    knowledge source. The model asks, is told there is nothing, and then
    has to answer or decline from what it already holds, which under
    oracle_context is the gold document sitting in its context. The miss
    text is never counted as evidence, so grounding for a control stays
    zero by construction rather than by accident.
    """

    def __init__(self, text: str = NO_RESULTS_TEXT):
        self.doc_texts = [text]

    def top(self, query: str, exclude=()) -> int:
        # exclude is ignored on purpose: the miss is the answer to every
        # query, and max_rounds is what bounds the loop.
        return 0


class ExaBudgetExhausted(RuntimeError):
    """Raised before a live search would exceed the run's budget."""


class BudgetedSearchClient:
    """Disk-cached, budget-capped wrapper around an Exa-shaped client.

    Cache entries key on (num_results, query) and persist across runs, so
    the second pass over a suite issues no live calls and reproduces the
    first pass exactly. live_calls counts only calls that reached the
    network; the budget is enforced against live_calls plus prior_calls,
    the total recorded by earlier runs against the same cache file.
    """

    def __init__(self, client, cache_path, budget: int, prior_calls: int = 0):
        self.client = client
        self.cache_path = Path(cache_path)
        self.budget = int(budget)
        self.prior_calls = int(prior_calls)
        self.live_calls = 0
        self.cache_hits = 0
        self.cache: dict = {}
        if self.cache_path.exists():
            with open(self.cache_path) as fh:
                self.cache = json.load(fh)

    def _save(self) -> None:
        tmp = self.cache_path.with_suffix(".tmp")
        with open(tmp, "w") as fh:
            json.dump(self.cache, fh)
        os.replace(tmp, self.cache_path)

    def search(self, query: str, num_results: int = 10,
               text: bool = True) -> list:
        key = f"{num_results}|{query}"
        if key in self.cache:
            self.cache_hits += 1
            return json.loads(json.dumps(self.cache[key]))
        if self.prior_calls + self.live_calls >= self.budget:
            raise ExaBudgetExhausted(
                f"live search budget ({self.budget}) exhausted")
        results = self.client.search(query, num_results=num_results, text=text)
        self.live_calls += 1
        self.cache[key] = results
        self._save()
        return json.loads(json.dumps(results))

    def usage(self) -> dict:
        return {"live_calls": self.live_calls, "cache_hits": self.cache_hits,
                "prior_calls": self.prior_calls, "budget": self.budget}


def make_web_index_factory(client, tokenizer,
                           chunk_tokens: int = DEFAULT_CHUNK_TOKENS,
                           num_results: int = DEFAULT_NUM_RESULTS):
    """Factory returning a fresh WebTierIndex per item.

    Fresh per item so one item's served chunks never leak into another
    item's without-replacement exclusions or its provenance check.
    """
    from src.retrieval_web.tier import WebRetrievalTier, WebTierIndex

    def factory():
        tier = WebRetrievalTier(client, tokenizer,
                                max_chunk_tokens=chunk_tokens,
                                num_results=num_results)
        return WebTierIndex(tier)

    return factory


# ----------------------------------------------------------- execution


@dataclass
class RunnerContext:
    """Everything one condition needs to answer an item.

    step_fn is the model's next-token callable, exactly the interface
    src/evals/interactive.py drives, so a checkpoint, a scripted fake, and
    any future model all enter the harness the same way.
    """

    step_fn: object
    tokenizer: object
    max_rounds: int = DEFAULT_MAX_ROUNDS
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS
    seed: int = 0
    web_index_factory: object = None
    label: str = "model"


def build_prompt(item: BenchItem, tokenizer, condition: str) -> list:
    """Token prompt for one item under one condition.

    Every condition shares the world preamble and the question. Only
    oracle_context inserts documents, and it inserts exactly the item's
    gold documents, so the control measures extraction from correct
    evidence and nothing else.
    """
    sid = tokenizer.special_ids
    ids = [sid["<|world|>"], *tokenizer.encode(item.preamble)]
    if condition == "oracle_context":
        for text in item.oracle_docs:
            ids.append(sid["<|doc|>"])
            ids.extend(tokenizer.encode(text))
    ids.append(sid["<|q|>"])
    ids.extend(tokenizer.encode(item.question))
    return ids


def run_item(item: BenchItem, ctx: RunnerContext, condition: str) -> dict:
    """Answer one item under one condition and return the raw record.

    retrieval binds the knowledge source: the episode documents through the
    training BM25 oracle, or the web tier index for web items. The two
    controls bind an EmptyResultIndex instead, so a query is answered with
    an explicit miss and the model still reaches its answer; nothing that
    index serves counts as evidence.

    n_queries counts what the model asked for under any condition, which is
    the retrieve habit. n_rounds counts only the rounds that returned real
    evidence, so it is zero for a control by construction and the retrieval
    efficiency metrics stay about retrieval.
    """
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}")
    tokenizer = ctx.tokenizer
    prompt = build_prompt(item, tokenizer, condition)

    documents = []
    index = None
    serving = condition == "retrieval"
    if serving:
        if item.web:
            if ctx.web_index_factory is None:
                raise ValueError("web items need a web_index_factory")
            index = ctx.web_index_factory()
        else:
            documents = item.documents
    else:
        index = EmptyResultIndex()

    start = time.monotonic()
    out = generate_with_retrieval(
        ctx.step_fn, tokenizer, documents, prompt,
        max_rounds=ctx.max_rounds, max_new_tokens=ctx.max_new_tokens,
        seed=ctx.seed, index=index)
    seconds = time.monotonic() - start

    rounds = []
    for served in out["rounds"]:
        meta = {}
        if serving and index is not None:
            meta = index.doc_meta[served["doc_index"]]
        rounds.append({
            "query": served["query"],
            "n_query_tokens": len(tokenizer.encode(served["query"])),
            "doc_index": served["doc_index"],
            "n_chunk_tokens": served["n_chunk_tokens"],
            "url": meta.get("url", ""),
            "title": meta.get("title", ""),
            "served": bool(serving),
            "chunk": served["chunk"][:CHUNK_PREVIEW_CHARS],
            "chunk_full": served["chunk"],
        })

    if condition == "oracle_context":
        evidence_texts = list(item.oracle_docs)
        evidence_tokens = sum(len(tokenizer.encode(t))
                              for t in item.oracle_docs)
    elif serving:
        evidence_texts = [r["chunk_full"] for r in rounds]
        evidence_tokens = sum(r["n_chunk_tokens"] for r in rounds)
    else:
        # The miss text is not evidence and must never ground an answer.
        evidence_texts = []
        evidence_tokens = 0

    n_queries = out["n_rounds"] + int(out["stop_reason"] == "max_rounds")
    return {
        "item_id": item.item_id, "suite": item.suite, "task": item.task,
        "condition": condition, "question": item.question,
        "golds": list(item.golds), "answer": out["answer_text"],
        "stop_reason": out["stop_reason"],
        "n_rounds": out["n_rounds"] if serving else 0,
        "n_queries": n_queries,
        "n_empty_results": 0 if serving else out["n_rounds"],
        "unserved_retrieve": bool(out["stop_reason"] == "max_rounds"),
        "evidence_tokens": evidence_tokens,
        "evidence_texts": evidence_texts,
        "n_generated": out["n_generated"],
        "n_prompt_tokens": len(prompt),
        "n_total_tokens": len(out["tokens"]),
        "seconds": round(seconds, 3),
        "rounds": rounds,
    }


# ------------------------------------------------------------ scoring


def score_record(item: BenchItem, record: dict) -> dict:
    """Attach the per-item metric fields to a raw record.

    correct is exact match or the contains fallback for answerable items,
    and abstention for unanswerable ones. Grounding is string provenance:
    gold_in_evidence asks whether the served evidence actually carried the
    answer, answer_in_evidence asks whether the model's answer text appears
    in that evidence rather than being generated free.
    """
    answer = record["answer"]
    evidence = "\n".join(record.get("evidence_texts", []))
    abstained = is_abstention(answer)

    em = any(exact_match(answer, gold) for gold in item.golds)
    contains = any(contains_answer(answer, gold) for gold in item.golds)
    if item.unanswerable:
        em = contains = abstained

    gold_hit = any(contains_answer(evidence, s)
                   for s in item.evidence_strings) if evidence else False
    gold_complete = all(contains_answer(evidence, s)
                        for s in item.evidence_strings) if evidence else False
    answer_grounded = bool(answer.strip()) and contains_answer(evidence, answer)
    distractor_hit = any(contains_answer(answer, d)
                         for d in item.distractor_strings)
    trap_hit = any(contains_answer(answer, t) for t in item.trap_strings)

    scored = dict(record)
    scored.update({
        "unanswerable": bool(item.unanswerable),
        "n_hops": item.n_hops,
        "exact_match": bool(em),
        "contains": bool(contains),
        "correct": bool(em or contains),
        "abstained": bool(abstained),
        "answer_empty": not answer.strip(),
        "gold_in_evidence": bool(gold_hit),
        "evidence_complete": bool(gold_complete),
        "answer_in_evidence": bool(answer_grounded),
        "grounded_correct": bool((em or contains) and answer_grounded),
        "unsupported_correct": bool((em or contains) and not answer_grounded
                                    and not item.unanswerable),
        "answered_distractor": bool(distractor_hit and not (em or contains)),
        "answered_trap": bool(trap_hit),
    })
    scored.pop("evidence_texts", None)
    return scored


def _mean(values) -> float:
    values = list(values)
    return round(sum(values) / len(values), 4) if values else 0.0


def aggregate(records) -> dict:
    """Pool scored records into one metric block.

    Rates are over the population each metric is defined on: grounding over
    answerable items, abstention quality over the unanswerable and
    answerable splits separately, and evidence cost per correct answer over
    the correct ones.
    """
    records = list(records)
    n = len(records)
    if not n:
        return {"n_items": 0}
    answerable = [r for r in records if not r["unanswerable"]]
    unanswerable = [r for r in records if r["unanswerable"]]
    correct = [r for r in records if r["correct"]]
    total_evidence = sum(r["evidence_tokens"] for r in records)

    block = {
        "n_items": n,
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
        "accuracy": _mean(r["correct"] for r in records),
        "accuracy_em": _mean(r["exact_match"] for r in records),
        "accuracy_contains": _mean(r["contains"] for r in records),
        "accuracy_answerable": _mean(r["correct"] for r in answerable),
        "gold_in_evidence": _mean(r["gold_in_evidence"] for r in answerable),
        "evidence_complete": _mean(r["evidence_complete"] for r in answerable),
        "answer_in_evidence": _mean(r["answer_in_evidence"] for r in answerable),
        "grounded_accuracy": _mean(r["grounded_correct"] for r in answerable),
        "unsupported_correct": _mean(r["unsupported_correct"]
                                     for r in answerable),
        "mean_rounds": _mean(r["n_rounds"] for r in records),
        "mean_queries": _mean(r["n_queries"] for r in records),
        "mean_empty_results": _mean(r.get("n_empty_results", 0)
                                    for r in records),
        "share_any_round": _mean(bool(r["n_rounds"]) for r in records),
        "share_unserved_retrieve": _mean(r["unserved_retrieve"]
                                         for r in records),
        "mean_evidence_tokens": _mean(r["evidence_tokens"] for r in records),
        "evidence_tokens_per_correct": (round(total_evidence / len(correct), 2)
                                        if correct else None),
        "abstention_rate_unanswerable": _mean(r["abstained"]
                                              for r in unanswerable),
        "explicit_abstention_unanswerable": _mean(
            r["abstained"] and not r["answer_empty"] for r in unanswerable),
        "empty_answer_rate": _mean(r["answer_empty"] for r in records),
        "confabulation_rate": _mean(not r["abstained"] for r in unanswerable),
        "trap_rate_unanswerable": _mean(r["answered_trap"]
                                        for r in unanswerable),
        "over_abstention_answerable": _mean(r["abstained"] for r in answerable),
        "mean_seconds": _mean(r["seconds"] for r in records),
        "mean_generated_tokens": _mean(r["n_generated"] for r in records),
        "mean_total_tokens": _mean(r["n_total_tokens"] for r in records),
    }
    arbitration = [r for r in records if r["task"] == "arbitration"]
    if arbitration:
        block["arbitration_accuracy"] = _mean(r["correct"] for r in arbitration)
        block["arbitration_distractor_rate"] = _mean(
            r["answered_distractor"] for r in arbitration)
    return block


def by_key(records, key: str) -> dict:
    """Aggregate blocks split by one record field, sorted by key."""
    buckets: dict = {}
    for record in records:
        buckets.setdefault(record[key], []).append(record)
    return {k: aggregate(v) for k, v in sorted(buckets.items())}


def run_bench(items, ctx: RunnerContext, conditions=CONDITIONS,
              on_record=None) -> dict:
    """Run every item under every condition and return the full results.

    A web budget exhaustion stops that condition's remaining web items and
    is recorded rather than raised, so a partial run still reports honest
    numbers over what it managed to score.
    """
    items = list(items)
    records: list = []
    stopped: dict = {}
    for condition in conditions:
        budget_hit = False
        for item in items:
            if condition == "oracle_context" and not item.oracle_docs:
                # An unanswerable item has no gold document by
                # construction; the control is undefined for it.
                continue
            if budget_hit and item.web:
                stopped.setdefault(condition, 0)
                stopped[condition] += 1
                continue
            try:
                record = run_item(item, ctx, condition)
            except ExaBudgetExhausted:
                budget_hit = True
                stopped.setdefault(condition, 0)
                stopped[condition] += 1
                continue
            scored = score_record(item, record)
            records.append(scored)
            if on_record is not None:
                on_record(scored)

    results = {
        "model": ctx.label,
        "config": {
            "max_rounds": ctx.max_rounds,
            "max_new_tokens": ctx.max_new_tokens,
            "seed": ctx.seed,
            "conditions": list(conditions),
            "decode": "greedy",
            "scoring": "normalized exact match, contains fallback",
        },
        "n_items": len(items),
        "n_records": len(records),
        "skipped_for_budget": stopped,
        "by_condition": {},
        "records": records,
    }
    for condition in conditions:
        subset = [r for r in records if r["condition"] == condition]
        if not subset:
            continue
        results["by_condition"][condition] = {
            "pooled": aggregate(subset),
            "by_suite": by_key(subset, "suite"),
            "by_task": by_key(subset, "task"),
        }
    results["gaps"] = _condition_gaps(results)
    return results


# ------------------------------------------------------------- report


_REPORT_ROWS = [
    ("items", "n_items", "{:d}"),
    ("accuracy", "accuracy", "{:.3f}"),
    ("exact match", "accuracy_em", "{:.3f}"),
    ("gold in evidence", "gold_in_evidence", "{:.3f}"),
    ("evidence complete", "evidence_complete", "{:.3f}"),
    ("answer in evidence", "answer_in_evidence", "{:.3f}"),
    ("grounded accuracy", "grounded_accuracy", "{:.3f}"),
    ("unsupported correct", "unsupported_correct", "{:.3f}"),
    ("mean rounds served", "mean_rounds", "{:.2f}"),
    ("mean queries issued", "mean_queries", "{:.2f}"),
    ("empty results served", "mean_empty_results", "{:.2f}"),
    ("evidence tokens", "mean_evidence_tokens", "{:.1f}"),
    ("ev tokens per correct", "evidence_tokens_per_correct", "{:.1f}"),
    ("abstention (unans)", "abstention_rate_unanswerable", "{:.3f}"),
    ("explicit abstention", "explicit_abstention_unanswerable", "{:.3f}"),
    ("confabulation", "confabulation_rate", "{:.3f}"),
    ("withheld answer given", "trap_rate_unanswerable", "{:.3f}"),
    ("empty answers", "empty_answer_rate", "{:.3f}"),
    ("over-abstention", "over_abstention_answerable", "{:.3f}"),
    ("seconds per item", "mean_seconds", "{:.2f}"),
    ("generated tokens", "mean_generated_tokens", "{:.1f}"),
]


def _cell(block: dict, key: str, fmt: str) -> str:
    value = block.get(key)
    if value is None:
        return "-"
    if fmt == "{:d}":
        return str(int(value))
    return fmt.format(float(value))


def _table(title: str, columns: list, blocks: list) -> list:
    width = max(22, *(len(c) for c in columns)) if columns else 22
    lines = [title, "-" * len(title)]
    lines.append("metric".ljust(24) + "".join(c.rjust(width + 2)
                                              for c in columns))
    for label, key, fmt in _REPORT_ROWS:
        cells = [_cell(b, key, fmt) for b in blocks]
        if all(c == "-" for c in cells):
            continue
        lines.append(label.ljust(24) + "".join(c.rjust(width + 2)
                                               for c in cells))
    lines.append("")
    return lines


def format_report(results: dict) -> str:
    """Readable metric tables: conditions pooled, then per suite and task."""
    lines = [f"NRM bench: {results['model']}",
             f"items {results['n_items']}, records {results['n_records']}",
             f"config {json.dumps(results['config'], sort_keys=True)}", ""]
    if results.get("skipped_for_budget"):
        lines.append(f"skipped for search budget: "
                     f"{results['skipped_for_budget']}")
        lines.append("")
    if results.get("exa_usage"):
        lines.append(f"exa usage: {json.dumps(results['exa_usage'])}")
        lines.append("")

    conditions = [c for c in CONDITIONS if c in results["by_condition"]]
    lines.extend(_table(
        "pooled by condition", conditions,
        [results["by_condition"][c]["pooled"] for c in conditions]))

    suites = sorted({s for c in conditions
                     for s in results["by_condition"][c]["by_suite"]})
    for suite in suites:
        blocks = [results["by_condition"][c]["by_suite"].get(suite, {})
                  for c in conditions]
        lines.extend(_table(f"suite: {suite}", conditions, blocks))

    tasks = sorted({t for c in conditions
                    for t in results["by_condition"][c]["by_task"]})
    retrieval = "retrieval" if "retrieval" in conditions else conditions[0]
    blocks = [results["by_condition"][retrieval]["by_task"].get(t, {})
              for t in tasks]
    lines.extend(_table(f"tasks under {retrieval}", tasks, blocks))

    gaps = _condition_gaps(results)
    if gaps:
        lines.append("paired controls")
        lines.append("---------------")
        lines.append(f"{'paired answerable items'.ljust(44)}"
                     f"{int(gaps['paired_items'])}")
        for name in ("accuracy_retrieval", "accuracy_no_retrieval",
                     "accuracy_oracle_context"):
            lines.append(f"{name.ljust(44)}{gaps[name]:.3f}")
        lines.append(f"{'oracle - retrieval (query formulation)'.ljust(44)}"
                     f"{gaps['oracle_minus_retrieval']:+.3f}")
        lines.append(f"{'oracle - none (extraction over memory)'.ljust(44)}"
                     f"{gaps['oracle_minus_no_retrieval']:+.3f}")
        lines.append("")
    return "\n".join(lines)


def _condition_gaps(results: dict) -> dict:
    """The two diagnostic gaps, computed on the shared answerable items.

    oracle minus retrieval isolates query formulation from extraction;
    oracle minus retrieval-free isolates extraction from memory. Both are
    computed over items scored in all three conditions so the comparison is
    paired.
    """
    have = results["by_condition"]
    if not {"retrieval", "no_retrieval", "oracle_context"} <= set(have):
        return {}
    per_condition: dict = {}
    for record in results["records"]:
        per_condition.setdefault(record["condition"], {})[record["item_id"]] = \
            record["correct"]
    shared = set(per_condition["oracle_context"])
    for condition in ("retrieval", "no_retrieval"):
        shared &= set(per_condition[condition])
    if not shared:
        return {}
    acc = {c: _mean(per_condition[c][i] for i in sorted(shared))
           for c in ("retrieval", "no_retrieval", "oracle_context")}
    return {
        "paired_items": len(shared),
        "accuracy_retrieval": acc["retrieval"],
        "accuracy_no_retrieval": acc["no_retrieval"],
        "accuracy_oracle_context": acc["oracle_context"],
        "oracle_minus_retrieval":
            round(acc["oracle_context"] - acc["retrieval"], 4),
        "oracle_minus_no_retrieval":
            round(acc["oracle_context"] - acc["no_retrieval"], 4),
    }


def reaggregate(results: dict, conditions=CONDITIONS) -> dict:
    """Recompute every metric block from the records already in results.

    Aggregation is a pure function of the scored records, so a run's
    numbers can be rebuilt after a metric is added or a rate is redefined
    without paying for the decode again. Only the blocks are replaced; the
    records, items, and provenance fields are left alone.
    """
    out = dict(results)
    records = out.get("records", [])
    out["by_condition"] = {}
    for condition in conditions:
        subset = [r for r in records if r["condition"] == condition]
        if not subset:
            continue
        out["by_condition"][condition] = {
            "pooled": aggregate(subset),
            "by_suite": by_key(subset, "suite"),
            "by_task": by_key(subset, "task"),
        }
    out["gaps"] = _condition_gaps(out)
    return out


def strip_records(results: dict, keep: int = 0) -> dict:
    """Results with the per-item records trimmed, for a compact summary."""
    out = dict(results)
    out["records"] = results["records"][:keep]
    return out
