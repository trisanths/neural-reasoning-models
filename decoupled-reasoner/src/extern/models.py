"""The models under test and the decode each publisher asks for.

`card` holds the sampling settings the model card recommends, so the primary
condition for every model is the one its own publisher specifies rather than
one chosen here. `greedy` is run beside it on the selection subsample, and
whichever of the two scores higher is the one taken to the full item set.

`max_new` is generous on purpose. A cap that truncates a reasoning trace
before its answer measures the cap, not the model, so the two reasoning
models get budgets several times the length of any answer the task needs.
"""
from __future__ import annotations

MODELS = {
    "lfm350m": {
        "repo": "LiquidAI/LFM2.5-350M",
        "card": dict(temperature=0.1, top_k=50, rep_penalty=1.05),
        "max_new": 512, "batch": 64, "reasoning": False,
    },
    "lfm1b2i": {
        "repo": "LiquidAI/LFM2.5-1.2B-Instruct",
        "card": dict(temperature=0.1, top_k=50, rep_penalty=1.05),
        "max_new": 512, "batch": 48, "reasoning": False,
    },
    "lfm1b2t": {
        "repo": "LiquidAI/LFM2.5-1.2B-Thinking",
        "card": dict(temperature=0.05, top_k=50, rep_penalty=1.05),
        "max_new": 4096, "batch": 48, "reasoning": True,
    },
    "lfm8ba1b": {
        "repo": "LiquidAI/LFM2.5-8B-A1B",
        "card": dict(temperature=0.2, top_k=80, rep_penalty=1.05),
        "max_new": 2048, "batch": 24, "reasoning": True,
    },
}


def flags(name, greedy=False):
    m = MODELS[name]
    if greedy:
        return "--greedy"
    c = m["card"]
    return (f"--temperature {c['temperature']} --top-k {c['top_k']} "
            f"--rep-penalty {c['rep_penalty']}")


if __name__ == "__main__":
    import sys
    n = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "repo":
        print(MODELS[n]["repo"])
    elif len(sys.argv) > 2 and sys.argv[2] == "greedy":
        print(flags(n, True))
    elif len(sys.argv) > 2 and sys.argv[2] == "maxnew":
        print(MODELS[n]["max_new"])
    elif len(sys.argv) > 2 and sys.argv[2] == "batch":
        print(MODELS[n]["batch"])
    else:
        print(flags(n))
