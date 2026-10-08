# Technical specification, v0

This document is the contract that Phase 0 implementation builds against. It will change as evidence arrives; changes get committed with reasons.

## 1. Training regimes

Three regimes, identical architecture and token budget, differing only in data.

Regime A, the baseline: natural language only (FineWeb-Edu sample, plus Wikipedia). This is what a conventional small model eats.

Regime B, the additive control: natural language plus synthetic reasoning data mixed in. Isolates the effect of reasoning data without fact starvation.

Regime C, the thesis: procedural warm-up (0.1 to 0.3 percent of tokens, front-loaded, following the ICML 2026 Procedural Pretraining recipe), then randomized synthetic worlds with within-episode retrieval. No natural corpus, no real-world entities. Facts mutate every episode so memorizing them has zero expected value.

## 2. Data formats

### Episode schema (JSONL, one object per episode)

```json
{
  "episode_id": "ep-000000",
  "seed": 12345,
  "world": {
    "domain": "corporate",
    "entities": [{"id": "e1", "type": "company", "name": "Lomera"}],
    "rules": ["acquisition transfers subsidiaries"],
    "facts": [{"id": "f1", "s": "e1", "p": "acquired", "o": "e2", "t": 3}]
  },
  "documents": [
    {"doc_id": "d1", "text": "...", "reliability": 0.9, "style": "filing",
     "supports": ["f1"], "contradicts": []}
  ],
  "questions": [
    {"qid": "q1", "text": "...", "answer": "...", "type": "multi_hop",
     "derivation": ["f1", "f7"], "hops": 2}
  ]
}
```

Entity names are sampled from a synthetic name grammar and never collide with real-world entities; a blocklist of frequent real names enforces this.

### Token stream

Token shards are uint16 arrays with an index file. Special tokens: `<|doc|>`, `<|q|>`, `<|a|>`, `<|retrieve|>`, `<|result|>`, `<|world|>`, `<|eot|>`. An episode renders as world preamble, a subset of documents, then question-answer pairs. Documents beyond the context budget are reachable only through retrieval.

### Retrieval protocol, v0

Within-episode oracle retrieval: when the model emits `<|retrieve|>` followed by query tokens, a BM25 index over the episode's documents returns the top chunk wrapped in `<|result|>`. Training teaches the emit-query-read loop; the retriever itself is deterministic. Learned retrievers and real-corpus indexes come later and are out of scope for the kill test.

## 3. World generator (worldgen)

Domains for v0: corporate (ownership, acquisitions, officers), regulatory (jurisdictions, restrictions, propagation), logistics (routes, capacities, schedules), kinship-temporal (people, relations, dates). Each domain is a rule module: entity type schema, generative rules for facts, and inference rules that define which questions have derivable answers.

Pipeline per episode: sample entity graph, roll facts forward through time steps, render documents (multiple surface styles per fact set, template banks with grammar-based variation), inject noise (contradictory documents at configurable rates, unreliable sources, irrelevant filler), compile questions with machine-checkable answers and stored derivations.

Determinism: every episode fully reproducible from its seed.

## 4. Procedural generators (procgen)

Following the verified recipe: k-Dyck and k-Shuffle Dyck (the hierarchy result says these carry the useful bias; the copy language ww is known harmful and is excluded), stack operation traces, sorting and set operations, elementary cellular automaton rule 110, graph reachability traces. Emitted as raw token streams for the warm-up phase.

## 5. Model

Llama-style decoder: RoPE, RMSNorm, SwiGLU, untied embeddings, 32k BPE tokenizer trained on a mixed sample of all regimes' data.

| class | params (approx) | d_model | layers | heads |
|---|---|---|---|---|
| smoke | 8M | 256 | 8 | 8 |
| 150M | 150M | 768 | 12 | 12 |
| 350M | 350M | 1024 | 24 | 16 |
| 700M | 700M | 1536 | 24 | 16 |
| 1.3B | 1.3B | 2048 | 24 | 32 |

Default token budget: 20 tokens per parameter. Context length 4096 for the kill test.

## 6. Evaluation suites

Held-out worlds: fresh episodes from held-out seeds and held-out domain mixes. Measures in-regime reasoning. Never the headline number, because it tests on the generator manifold.

Naturalized reading, the kill-test gate: question answering over real messy documents the model has never seen the likes of. Sources: public-domain and permissively licensed texts, OCR-noised, with injected contradictions and rhetorical framing. Questions authored with verifiable answers. This suite measures whether a fact-starved model can read reality at all.

Knowledge probes: cloze and QA probes for real-world facts. Regime C models must score at chance; anything above chance means leakage into the training data, and the run is investigated before its results count.

Retrieval-noise axis: corrupt the oracle retriever's results at 0, 10, 25, and 50 percent rates and measure the degradation slope by model size. The literature says small readers degrade fastest; this measures whether our training regime changes that.

## 7. Pre-registered kill-test decision rule

Compare regime C against regime A at the 350M class on the naturalized reading suite. If C reaches at least 90 percent of A's score, the strict form survives and Phase 2 tests it. Between 60 and 90 percent, the strict form is weakened: Phase 2 uses a frequency-ordered resident knowledge diet plus teacher distillation. Below 60 percent, the strict form is dead; Phase 2 tests only the weakened form and the writeup says so plainly.

## 8. Repository layout

```
src/worldgen/     episode and world generation
src/procgen/      procedural warm-up data
src/train/        model, tokenizer, dataloader, trainer
src/evals/        the four suites above
configs/          model and run configs (yaml)
scripts/          pod bootstrap, data generation, launch
```

Tests live inside each module directory. Nothing under data/ or checkpoints/ is ever committed.
