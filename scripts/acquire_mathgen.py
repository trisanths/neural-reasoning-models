"""Run the acquisition loop against a universe built to src/mathgen/interface.

This is the generalization check. The loop was written against the prose of
src/acquire/universe.py, and a benchmark it cannot read is a benchmark it
cannot be measured on. What survives the change of generator, and what does
not, is written down in src/acquire/mathgen_adapter.py and reproduced by this
script's output.

The reasoner defaults to constant, because the point here is the search and
the graph reconstruction, and both are model-free: gap.py builds the query,
lesson.py ranks, curriculum.py recurses, and the score is against the
generator's own item dependencies. Pass --reasoner policy to see what the
gate does on top.
"""

from __future__ import annotations

import argparse
import json

from src.acquire.loop import LoopConfig, report, run_problem
from src.acquire.mathgen_adapter import adapt
from src.acquire.reasoner import ConstantReasoner
from src.mathgen.interface import load_universe


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="3,4,5")
    ap.add_argument("--universe-module", default=None)
    ap.add_argument("--levels", default="1,2,3,5")
    ap.add_argument("--per-level", type=int, default=3)
    args = ap.parse_args()

    levels = tuple(int(x) for x in args.levels.split(","))
    reasoner = ConstantReasoner("unknown")
    traces = []
    per_seed = {}
    for seed in [int(s) for s in args.seeds.split(",")]:
        universe = load_universe(seed, module=args.universe_module)
        documents, problems, meta = adapt(universe, levels=levels,
                                          n_per_level=args.per_level,
                                          seed=seed)
        lexicon = meta["lexicon"]
        chapters = meta["chapters"]
        print(f"seed {seed}: universe {universe.universe_id} "
              f"{len(documents)} pages {len(problems)} problems", flush=True)

        def query_for(term: str) -> str:
            return term

        seed_traces = []
        for p in problems:
            t = run_problem(p, chapters[p.chapter], documents, reasoner,
                            LoopConfig(max_nodes=12, max_search_rounds=16),
                            lexicon=lexicon, query_for=query_for)
            seed_traces.append(t)
        traces.extend(seed_traces)
        per_seed[str(seed)] = report(seed_traces)

    out = {"universe": "mathgen", "seeds": args.seeds,
           "per_seed": per_seed, "pooled_across_seeds_only": report(traces)}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    rep = out["pooled_across_seeds_only"]
    for name, cell in rep["by_level"].items():
        c = cell["curriculum"]
        print(f"L{name} n={cell['n']} "
              f"gap_fire={cell['gap_fire_rate']:.2f} "
              f"node_recall={c.get('node_recall', 0):.2f} "
              f"node_prec={c.get('node_precision', 0):.2f} "
              f"edge_recall={c.get('edge_recall', 0):.2f} "
              f"edge_prec={c.get('edge_precision', 0):.2f} "
              f"order={c.get('order_valid', 0):.2f} "
              f"abstain={cell['abstain_rate']:.2f}", flush=True)
    print("blockages:", json.dumps(rep["blockage_counts"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
