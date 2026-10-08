"""Episode assembly: world generation, document rendering, noise injection,
and validation. Every episode is fully reproducible from its integer seed."""

import numpy as np

from src.worldgen.domains import DOMAIN_ORDER, DOMAINS

STYLES = ["report", "filing", "memo", "note", "bulletin"]

SEED_STRIDE = 1_000_003


def episode_seed(base_seed: int, index: int) -> int:
    """Derive the per episode seed recorded in the JSONL."""
    return (int(base_seed) * SEED_STRIDE + int(index)) % (1 << 63)


def make_episode(seed: int, episode_id: str, domain: str,
                 contradiction_rate: float = 0.15,
                 filler_rate: float = 0.25) -> dict:
    """Build one episode dict matching the SPEC.md schema."""
    if domain not in DOMAINS:
        raise ValueError(f"unknown domain {domain!r}, known: {sorted(DOMAINS)}")
    rng = np.random.default_rng(int(seed))
    dom = DOMAINS[domain]
    entities, rules, facts, questions = dom.generate(rng)
    name_of = {e["id"]: e["name"] for e in entities}

    raw_docs = []
    for fact in facts:
        raw_docs.append({
            "text": dom.sentence(fact, name_of, rng),
            "reliability": round(0.7 + 0.28 * float(rng.random()), 2),
            "style": STYLES[int(rng.integers(len(STYLES)))],
            "supports": [fact["id"]],
            "contradicts": [],
        })
    for fact in facts:
        if float(rng.random()) < contradiction_rate:
            wrong = dom.corrupt(fact, entities, rng)
            if wrong is None:
                continue
            raw_docs.append({
                "text": dom.sentence(wrong, name_of, rng),
                "reliability": round(0.1 + 0.3 * float(rng.random()), 2),
                "style": STYLES[int(rng.integers(len(STYLES)))],
                "supports": [],
                "contradicts": [fact["id"]],
            })
    for _ in range(int(round(filler_rate * len(facts)))):
        raw_docs.append({
            "text": dom.filler(entities, name_of, rng),
            "reliability": 0.5,
            "style": STYLES[int(rng.integers(len(STYLES)))],
            "supports": [],
            "contradicts": [],
        })

    order = [int(i) for i in rng.permutation(len(raw_docs))]
    documents = []
    for i in order:
        doc = dict(raw_docs[i])
        doc["doc_id"] = f"d{len(documents) + 1}"
        documents.append(doc)

    clean_facts = []
    for fact in facts:
        clean = {"id": fact["id"], "s": fact["s"], "p": fact["p"],
                 "o": fact["o"], "t": int(fact["t"])}
        if "cap" in fact:
            clean["cap"] = int(fact["cap"])
        clean_facts.append(clean)

    return {
        "episode_id": episode_id,
        "seed": int(seed),
        "world": {
            "domain": domain,
            "entities": entities,
            "rules": rules,
            "facts": clean_facts,
        },
        "documents": documents,
        "questions": questions,
    }


def generate_episodes(base_seed: int, count: int, domains=None,
                      contradiction_rate: float = 0.15,
                      filler_rate: float = 0.25, start_index: int = 0):
    """Yield episodes cycling through the domain list."""
    if domains is None:
        domains = DOMAIN_ORDER
    for i in range(start_index, start_index + count):
        yield make_episode(
            episode_seed(base_seed, i),
            f"ep-{i:06d}",
            domains[i % len(domains)],
            contradiction_rate=contradiction_rate,
            filler_rate=filler_rate,
        )


def validate_episode(episode: dict) -> list:
    """Return a list of problems; an empty list means the episode is sound."""
    problems = []
    world = episode.get("world", {})
    fact_ids = {f["id"] for f in world.get("facts", [])}
    entity_ids = {e["id"] for e in world.get("entities", [])}
    supported = set()
    for doc in episode.get("documents", []):
        for fid in doc.get("supports", []) + doc.get("contradicts", []):
            if fid not in fact_ids:
                problems.append(f"doc {doc['doc_id']} references unknown fact {fid}")
        supported.update(doc.get("supports", []))
    for fact in world.get("facts", []):
        if fact["s"] not in entity_ids:
            problems.append(f"fact {fact['id']} has unknown subject {fact['s']}")
        if fact["id"] not in supported:
            problems.append(f"fact {fact['id']} has no supporting document")
    for q in episode.get("questions", []):
        if not q.get("answer"):
            problems.append(f"question {q['qid']} has an empty answer")
        for fid in q.get("derivation", []):
            if fid not in fact_ids:
                problems.append(f"question {q['qid']} derives from unknown fact {fid}")
    if not episode.get("questions"):
        problems.append("episode has no questions")
    return problems
