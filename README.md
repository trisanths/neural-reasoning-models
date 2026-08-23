# decoupled-reasoner

An experimental test of knowledge-intelligence decoupling: train the smallest neural reasoner that holds language, logic, mathematics, and a general ontology in its weights, while specific world facts live in an external, retrievable address space.

The hypothesis in one line: capability is a function of reasoner quality, retrieval bandwidth, context utilization, tools, and test-time compute, rather than of parameter count.

## Documents

- [SPEC.md](SPEC.md): technical design. Training regimes, data formats, world generator, model architecture, evaluation suites.
- [PLAN.md](PLAN.md): phases, budgets, decision gates, and the risk register distilled from a verified literature review.

## Status

2026-08-23: repository created, design documents committed. Phase 0 (cloud scaffolding and smoke test) is next, pending compute credentials. All development and training runs on rented cloud GPUs; nothing runs on the owner's local machine.

## Provenance

The combined recipe tested here (fact-starved pretraining, per-episode-mutating synthetic worlds, retrieval-native training from scratch) appears unclaimed in the 2024-2026 literature. Nearest prior art: LMLM (arXiv:2505.15962), SILO (arXiv:2308.04430), Procedural Pretraining (ICML 2026, arXiv:2601.21725), Absolute Zero (arXiv:2505.03335), and Karpathy's cognitive core posts. PLAN.md carries the full citation list.
