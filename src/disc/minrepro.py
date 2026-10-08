"""The smallest task that still exhibits the composition failure.

The invented-system families mix two abilities: reading a stated rule and
computing with it. The arithmetic families make that worse, because a wrong
answer can mean the model failed to read the rule, failed to chain, or failed
to multiply. This file removes arithmetic entirely and leaves only chaining.

One episode invents a notation: an alphabet of nonsense tokens, three maps
over that alphabet, and a fourth map that no question ever uses. Every map is
a derangement, so applying one always changes the token. A page per map states
the map as a table. A question names a starting token and a chain of maps, and
asks for the token that comes out. Depth d means d table lookups, each on the
output of the previous one.

The page set is identical at every depth. Only the question changes, and it
grows by four words per step. Prompt length is therefore not a confound in the
depth curve, which is the whole point of the instrument.

Shortcuts the registry has caught before are excluded by construction, and the
exclusions are checked rather than assumed (see audit_episodes):

  the answer never appears anywhere in the question;
  the answer is never the starting token or any intermediate token, so
    stopping early scores zero and is separately countable;
  the answer is never what the chain gives in the reverse order, nor what the
    first map alone gives, nor what the last map alone gives;
  every alphabet token appears the same number of times across the pages
    except for the single worked example, so frequency carries no signal;
  a keyword-nearest reader, which finds the best matching page and returns the
    token that page pairs with the starting token, is exactly the depth-one
    answer and therefore scores zero at depth two and beyond.

The worked example on the page set is itself a depth-two composition, on a
token reserved so that it never starts a question. A model that fails here
cannot be failing because the format was never demonstrated.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter

SYLLABLES = [
    "ka", "vor", "mi", "zel", "tu", "bra", "qen", "sol", "dri", "fex",
    "lum", "nak", "pyr", "tez", "ovi", "wren", "xil", "yuk", "zam", "clo",
    "nid", "harv", "esk", "plo", "tarn", "givo", "rusk", "mel", "onda", "verx",
]

ALPHABET_SIZE = 6
N_MAPS = 3

# Surface form is held as close as possible to skillacq's substitution_rule
# family, which this same checkpoint answers at 0.969 greedy and 0.828 at
# temperature one. Every table line names the map, its input and its output,
# so one line is self contained exactly as "A {k} is handled by the {v} desk"
# is. Where this task differs from that one is depth, and nothing else.


def _word(rng: random.Random, n: int = 2) -> str:
    return "".join(rng.choice(SYLLABLES) for _ in range(n))


def _distinct_words(rng: random.Random, count: int, taken: set[str],
                    n_syl: int = 2) -> list[str]:
    out: list[str] = []
    while len(out) < count:
        w = _word(rng, n_syl)
        if w in taken:
            continue
        taken.add(w)
        out.append(w)
    return out


def _derangement(rng: random.Random, items: list[str]) -> dict[str, str]:
    """A permutation with no fixed point, so every map moves every token."""
    n = len(items)
    while True:
        perm = list(items)
        rng.shuffle(perm)
        if all(a != b for a, b in zip(items, perm)):
            return dict(zip(items, perm))


class MinSystem:
    """One invented notation: an alphabet, three used maps, one distractor."""

    def __init__(self, rng: random.Random, alphabet_size: int = ALPHABET_SIZE,
                 n_maps: int = N_MAPS):
        self.alphabet_size = alphabet_size
        taken: set[str] = set()
        self.alphabet = _distinct_words(rng, alphabet_size, taken)
        self.name = _distinct_words(rng, 1, taken)[0].capitalize()
        names = _distinct_words(rng, n_maps + 1, taken)
        self.map_names = [n.capitalize() for n in names[:n_maps]]
        self.distractor_name = names[n_maps].capitalize()
        self.maps = {m: _derangement(rng, self.alphabet) for m in self.map_names}
        self.distractor = _derangement(rng, self.alphabet)
        # One token is reserved as the worked example's starting token so that
        # no question ever begins where the example began.
        self.example_start = self.alphabet[0]
        self.starts = self.alphabet[1:]
        self.example_chain = [self.map_names[0], self.map_names[1]]

    # ------------------------------------------------------------- execution

    def run(self, start: str, chain: list[str]) -> list[str]:
        """Every stage of the computation, stage 0 being the starting token."""
        stages = [start]
        cur = start
        for m in chain:
            cur = self.maps[m][cur]
            stages.append(cur)
        return stages

    # ----------------------------------------------------------------- pages

    def _table(self, name: str, table: dict[str, str]) -> str:
        lines = "\n".join(f"The {name} map sends {k} to {table[k]}."
                          for k in self.alphabet)
        return (f"The {name} map.\n\n"
                f"In the {self.name} notation the {name} map sends every token to "
                f"one token.\n\n{lines}")

    def _preamble(self) -> str:
        toks = ", ".join(self.alphabet)
        return (f"The {self.name} notation.\n\n"
                f"The {self.name} notation is written with these tokens: {toks}. "
                f"Each map of the notation sends every token to exactly one token. "
                f"When several maps are applied in turn, each one acts on the token "
                f"the previous map produced.")

    def _worked(self) -> str:
        a, b = self.example_chain
        stages = self.run(self.example_start, [a, b])
        return (f"A worked example in the {self.name} notation.\n\n"
                f"The {a} map is applied to {stages[0]}, then the {b} map is applied "
                f"to that result. The {a} map sends {stages[0]} to {stages[1]}. The "
                f"{b} map sends {stages[1]} to {stages[2]}. The token that results "
                f"is {stages[2]}.")

    def pages(self, rng: random.Random) -> list[str]:
        pages = [self._preamble(), self._worked(),
                 self._table(self.distractor_name, self.distractor)]
        pages.extend(self._table(m, self.maps[m]) for m in self.map_names)
        rng.shuffle(pages)
        return pages

    # ------------------------------------------------------------- questions

    def question_text(self, start: str, chain: list[str]) -> str:
        head = (f"In the {self.name} notation the {chain[0]} map is applied "
                f"to {start}")
        if len(chain) == 1:
            return head + ". Which token results?"
        rest = ", then ".join(f"the {c} map is applied to that result"
                              for c in chain[1:])
        return f"{head}, then {rest}. Which token results?"

    def sample_chain(self, rng: random.Random, depth: int) -> list[str]:
        chain: list[str] = []
        while len(chain) < depth:
            m = rng.choice(self.map_names)
            if chain and m == chain[-1]:
                continue
            chain.append(m)
        return chain

    def problems(self, rng: random.Random, depth: int, n: int) -> list[dict]:
        """Sample n depth-d problems that survive every exclusion."""
        out: list[dict] = []
        seen: set[tuple] = set()
        for _ in range(4000):
            if len(out) >= n:
                break
            start = rng.choice(self.starts)
            chain = self.sample_chain(rng, depth)
            key = (start, tuple(chain))
            if key in seen:
                continue
            seen.add(key)
            stages = self.run(start, chain)
            gold = stages[-1]
            if len(set(stages)) != len(stages):
                # Distinct stages keep the stopped-early diagnostic unambiguous.
                continue
            if depth > 1:
                if gold == self.run(start, list(reversed(chain)))[-1]:
                    continue
                if gold == self.maps[chain[0]][start]:
                    continue
                if gold == self.maps[chain[-1]][start]:
                    continue
            text = self.question_text(start, chain)
            if _mentions(gold, text):
                continue
            out.append({
                "qid": f"d{depth}_{len(out)}",
                "kind": f"chain{depth}",
                "depth": depth,
                "start": start,
                "chain": list(chain),
                "stages": stages,
                "text": text,
                "answer": gold,
            })
        return out


def _mentions(token: str, text: str) -> bool:
    return re.search(rf"(?<![\w]){re.escape(token)}(?![\w])", text) is not None


# --------------------------------------------------------------- episode I/O

def generate_episode(seed: int, depth: int, n_problems: int = 8,
                     pages: str = "correct",
                     alphabet_size: int = ALPHABET_SIZE) -> dict:
    """One RL-shaped episode at a fixed composition depth.

    pages selects the evidence condition. "correct" gives the system's own
    pages. "wrong" gives the pages of a different system over a different
    alphabet, so the question is unanswerable but the prompt is the same
    shape. "blank" gives a single empty placeholder page.
    """
    rng = random.Random(seed * 7919 + depth)
    system = MinSystem(rng, alphabet_size=alphabet_size)
    problems = system.problems(rng, depth, n_problems)
    if pages == "correct":
        docs = system.pages(rng)
    elif pages == "wrong":
        other = MinSystem(random.Random((seed * 7919 + depth) ^ 0x5EED),
                          alphabet_size=alphabet_size)
        docs = other.pages(rng)
    elif pages == "blank":
        docs = ["This page is intentionally blank."]
    else:
        raise ValueError(f"unknown pages condition {pages!r}")
    return {
        "episode_id": f"mr-{depth}-{seed:07d}",
        "seed": seed,
        "depth": depth,
        "alphabet_size": alphabet_size,
        "pages_condition": pages,
        "world": {"domain": f"minrepro_depth{depth}"},
        "n_context": 0,
        "documents": [{"text": p} for p in docs],
        "alphabet": system.alphabet,
        "questions": [
            {
                "qid": p["qid"],
                "text": p["text"],
                "answer": p["answer"],
                "plan": [f"s{i}" for i in range(p["depth"])],
                "type": p["kind"],
                "depth": p["depth"],
                "start": p["start"],
                "chain": p["chain"],
                "stages": p["stages"],
            }
            for p in problems
        ],
    }


def write_jsonl(path: str, seeds, depth: int, n_problems: int = 8,
                pages: str = "correct", in_context: bool = False,
                alphabet_size: int = ALPHABET_SIZE) -> dict:
    n_eps = n_q = 0
    with open(path, "w") as fh:
        for s in seeds:
            ep = generate_episode(s, depth, n_problems=n_problems, pages=pages,
                                  alphabet_size=alphabet_size)
            if in_context:
                ep["n_context"] = len(ep["documents"])
            fh.write(json.dumps(ep) + "\n")
            n_eps += 1
            n_q += len(ep["questions"])
    return {"path": path, "episodes": n_eps, "questions": n_q, "depth": depth,
            "pages": pages, "in_context": in_context,
            "alphabet_size": alphabet_size}


# ------------------------------------------------------------------- audit

def audit_episodes(episodes: list[dict]) -> dict:
    """Check the exclusions and score every shortcut we can think of.

    Returns counts that must be zero and baseline accuracies that must sit at
    or below chance for the instrument to mean anything.
    """
    from src.train.retrieval import BM25Index

    n = 0
    viol = Counter()
    hits = Counter()
    freq_spread: list[int] = []
    for ep in episodes:
        alpha = ep["alphabet"]
        texts = [d["text"] for d in ep["documents"]]
        blob = "\n".join(texts)
        counts = {a: len(re.findall(rf"(?<![\w]){re.escape(a)}(?![\w])", blob))
                  for a in alpha}
        top_symbol = max(counts, key=lambda a: counts[a])
        freq_spread.append(max(counts.values()) - min(counts.values()))
        index = BM25Index(texts, reliabilities=[1.0] * len(texts))
        for q in ep["questions"]:
            n += 1
            gold, stages = q["answer"], q["stages"]
            if _mentions(gold, q["text"]):
                viol["answer_in_question"] += 1
            if gold == stages[0]:
                viol["answer_is_start"] += 1
            if gold in stages[:-1]:
                viol["answer_is_intermediate"] += 1
            if len(set(stages)) != len(stages):
                viol["stages_not_distinct"] += 1
            # Shortcut baselines.
            if gold == top_symbol:
                hits["most_frequent_symbol"] += 1
            if gold == stages[0]:
                hits["copy_start"] += 1
            if len(stages) > 1 and gold == stages[1]:
                hits["depth_one_stop"] += 1
            try:
                best = index.top(q["text"], exclude=set())
                page = texts[best]
            except (ValueError, IndexError):
                page = ""
            m = re.search(rf"(?<![\w]){re.escape(stages[0])}(?![\w]) goes to (\w+)",
                          page)
            if m and m.group(1) == gold:
                hits["keyword_nearest"] += 1
    return {
        "n_questions": n,
        "chance": 1.0 / len(episodes[0]["alphabet"]) if episodes else 0.0,
        "violations": dict(viol),
        "baselines": {k: v / n for k, v in hits.items()},
        "max_symbol_frequency_spread": max(freq_spread) if freq_spread else 0,
    }


# -------------------------------------------------------------------- eval

def classify(answer: str, q: dict, alphabet: list[str]) -> str:
    from src.evals.naturalized import exact_match

    stages = q["stages"]
    if exact_match(answer, stages[-1]):
        return "correct"
    for k, s in enumerate(stages[:-1]):
        if exact_match(answer, s):
            return "start" if k == 0 else f"stopped_at_{k}"
    for a in alphabet:
        if exact_match(answer, a):
            return "other_token"
    return "off_alphabet"


def load_policy_parts(checkpoint: str, tokenizer_path: str):
    """Model, tokenizer and device, loaded once for a whole sweep."""
    import torch

    from src.evals.mc import load_checkpoint_model
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(tokenizer_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint_model(checkpoint, device)
    return model, tok, device


def evaluate(model, tok, device, episodes_path: str,
             samples: int, temperature: float, batch: int, max_len: int,
             max_prompt_tokens: int, max_rounds: int, max_new_tokens: int,
             seed: int) -> dict:
    """Roll the policy out over one episodes file and summarise the outcome."""
    from src.evals.naturalized import exact_match
    from src.rl.env import EnvConfig, EpisodeEnv, load_tasks, rollout_stats
    from src.rl.sampler import CachedPolicy

    lookup: dict[tuple[int, str], dict] = {}
    alphabets: dict[int, list[str]] = {}
    with open(episodes_path) as fh:
        for i, line in enumerate(fh):
            ep = json.loads(line)
            alphabets[i] = ep["alphabet"]
            for q in ep["questions"]:
                lookup[(i, q["qid"])] = q

    env_cfg = EnvConfig(max_rounds=max_rounds, max_new_tokens=max_new_tokens,
                        max_len=max_len)
    env = EpisodeEnv(tok, env_cfg)
    tasks = load_tasks(episodes_path, tok, questions_per_episode=10 ** 6,
                       min_hops=1, max_prompt_tokens=max_prompt_tokens,
                       limit_episodes=None, seed=0)
    if not tasks:
        raise SystemExit(f"no tasks survived load_tasks for {episodes_path}; "
                         f"raise max_prompt_tokens")
    wide = [t for t in tasks for _ in range(samples)]
    policy = CachedPolicy(model, device, max_len=max_len,
                          temperature=temperature, seed=seed)
    rolls = []
    for i in range(0, len(wide), batch):
        rolls.extend(env.rollout(policy, wide[i:i + batch]))

    per_question: dict[tuple[int, str], list[bool]] = {}
    kinds = Counter()
    strict = 0
    traces = []
    for r in rolls:
        key = (r.task.episode_index, r.task.qid)
        q = lookup[key]
        cls = classify(r.answer_text, q, alphabets[r.task.episode_index])
        kinds[cls] += 1
        ok = exact_match(r.answer_text, q["answer"])
        strict += int(ok)
        per_question.setdefault(key, []).append(ok)
        if len(traces) < 12:
            traces.append({"question": r.task.question, "gold": r.task.gold,
                           "answer": r.answer_text, "class": cls,
                           "rounds": [x["query"] for x in r.rounds],
                           "stop": r.stop_reason})
    stats = rollout_stats(rolls)
    n_q = len(per_question)
    return {
        "episodes_path": episodes_path,
        "n_questions": n_q,
        "n_rollouts": len(rolls),
        "samples_per_question": samples,
        "temperature": temperature,
        "accuracy_env": stats["accuracy"],
        "accuracy_exact": strict / max(1, len(rolls)),
        "pass_at_k": sum(any(v) for v in per_question.values()) / max(1, n_q),
        "classes": {k: v / max(1, len(rolls)) for k, v in kinds.items()},
        "mean_rounds": stats["mean_rounds"],
        "any_retrieval": stats["any_retrieval"],
        "well_formed": stats["well_formed"],
        "stop_reasons": stats["stop_reasons"],
        "traces": traces,
    }


# --------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen", help="write episode files and audit them")
    g.add_argument("--out-dir", required=True)
    g.add_argument("--depths", default="1,2,3,4,5,6")
    g.add_argument("--episodes", type=int, default=8)
    g.add_argument("--problems", type=int, default=8)
    g.add_argument("--seed0", type=int, default=1000)
    g.add_argument("--alphabet", type=int, default=ALPHABET_SIZE)
    g.add_argument("--conditions", default="correct,wrong,blank")
    g.add_argument("--presentations", default="ctx,ret")

    for name, helptext in (("eval", "score one episodes file"),
                           ("sweep", "score many episodes files, one model load")):
        e = sub.add_parser(name, help=helptext)
        e.add_argument("--checkpoint", required=True)
        e.add_argument("--tokenizer", required=True)
        e.add_argument("--out", default="")
        e.add_argument("--samples", type=int, default=4)
        e.add_argument("--temperature", type=float, default=1.0)
        e.add_argument("--batch", type=int, default=32)
        e.add_argument("--max-len", type=int, default=1536)
        e.add_argument("--max-prompt-tokens", type=int, default=1100)
        e.add_argument("--max-rounds", type=int, default=6)
        e.add_argument("--max-new-tokens", type=int, default=96)
        e.add_argument("--seed", type=int, default=99)
        if name == "eval":
            e.add_argument("--episodes", required=True)
        else:
            e.add_argument("--files", required=True,
                           help="comma separated episodes files, in order")

    args = ap.parse_args()

    if args.cmd == "gen":
        import os
        os.makedirs(args.out_dir, exist_ok=True)
        depths = [int(d) for d in args.depths.split(",")]
        seeds = list(range(args.seed0, args.seed0 + args.episodes))
        manifest = []
        conds = [c for c in args.conditions.split(",") if c]
        pres = [p for p in args.presentations.split(",") if p]
        for d in depths:
            for pages in conds:
                for p in pres:
                    ctx = p == "ctx"
                    tag = f"a{args.alphabet}-d{d}-{pages}-{p}"
                    path = os.path.join(args.out_dir, f"{tag}.jsonl")
                    manifest.append(write_jsonl(
                        path, seeds, d, n_problems=args.problems, pages=pages,
                        in_context=ctx, alphabet_size=args.alphabet))
        eps = [generate_episode(s, d, n_problems=args.problems,
                                alphabet_size=args.alphabet)
               for d in depths for s in seeds]
        report = audit_episodes(eps)
        report["manifest"] = manifest
        with open(os.path.join(args.out_dir,
                               f"audit-a{args.alphabet}.json"), "w") as fh:
            json.dump(report, fh, indent=2)
        print(json.dumps({k: v for k, v in report.items() if k != "manifest"},
                         indent=2))
        return 0

    model, tok, device = load_policy_parts(args.checkpoint, args.tokenizer)
    paths = ([args.episodes] if args.cmd == "eval"
             else [p for p in args.files.split(",") if p])
    out = []
    for path in paths:
        res = evaluate(model, tok, device, path, args.samples,
                       args.temperature, args.batch, args.max_len,
                       args.max_prompt_tokens, args.max_rounds,
                       args.max_new_tokens, args.seed)
        out.append(res)
        slim = {k: v for k, v in res.items() if k != "traces"}
        print(json.dumps(slim), flush=True)
        if args.out:
            with open(args.out, "w") as fh:
                json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
