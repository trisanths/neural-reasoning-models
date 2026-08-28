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
    """One invented notation: a pipeline of maps, plus one unused distractor.

    typed is the variant that matters. Level i has its own alphabet and map i
    runs level i-1 to level i, so a token is a source on exactly one page and a
    target on at most one other. Every lookup is then as unambiguous as the
    substitution_rule family this checkpoint answers at 0.969, and the only
    thing depth adds is that the key to lookup i comes from lookup i-1 rather
    than from the question.

    typed False is the closed-alphabet variant: one alphabet, every map a
    derangement of it, so each token appears as a source and as a target on
    every page. Keeping it here is deliberate. It separates referent ambiguity
    from depth, and it is the version the calibration run showed already fails
    at depth one, which is a different failure from the one under study.
    """

    def __init__(self, rng: random.Random, alphabet_size: int = ALPHABET_SIZE,
                 max_depth: int = N_MAPS, typed: bool = True):
        self.alphabet_size = alphabet_size
        self.max_depth = max_depth
        self.typed = typed
        taken: set[str] = set()
        if typed:
            self.levels = [_distinct_words(rng, alphabet_size, taken)
                           for _ in range(max_depth + 1)]
        else:
            shared = _distinct_words(rng, alphabet_size, taken)
            self.levels = [shared for _ in range(max_depth + 1)]
        self.name = _distinct_words(rng, 1, taken)[0].capitalize()
        names = _distinct_words(rng, max_depth + 1, taken)
        self.map_names = [n.capitalize() for n in names[:max_depth]]
        self.distractor_name = names[max_depth].capitalize()
        self.maps: list[dict[str, str]] = []
        for i in range(max_depth):
            src, dst = self.levels[i], self.levels[i + 1]
            if typed:
                perm = list(dst)
                rng.shuffle(perm)
                self.maps.append(dict(zip(src, perm)))
            else:
                self.maps.append(_derangement(rng, src))
        if typed:
            self.distractor_targets = _distinct_words(rng, alphabet_size, taken)
            dperm = list(self.distractor_targets)
            rng.shuffle(dperm)
            self.distractor = dict(zip(self.levels[0], dperm))
        else:
            self.distractor_targets = []
            self.distractor = _derangement(rng, self.levels[0])
        # One level-zero token is reserved for the worked example, so no
        # question ever starts where the example started.
        self.example_start = self.levels[0][0]
        self.starts = self.levels[0][1:]
        self.universe = sorted({w for lv in self.levels for w in lv}
                               | set(self.distractor_targets))

    # ------------------------------------------------------------- execution

    def chain(self, depth: int) -> list[str]:
        """Depth d always applies the first d maps in order. The pipeline is
        fixed so that parsing which maps to use is never part of the task."""
        return self.map_names[:depth]

    def run(self, start: str, depth: int) -> list[str]:
        """Every stage, stage 0 being the starting token."""
        stages = [start]
        cur = start
        for i in range(depth):
            cur = self.maps[i][cur]
            stages.append(cur)
        return stages

    # ----------------------------------------------------------------- pages

    def _table(self, name: str, table: dict[str, str], sources) -> str:
        lines = "\n".join(f"A {k} is handled by the {table[k]} desk."
                          for k in sources)
        return (f"The {name} routing table.\n\n"
                f"Requests in the {name} office are routed by their type.\n\n"
                f"{lines}")

    def _preamble(self) -> str:
        return (f"The {self.name} referral system.\n\n"
                f"Every office in the {self.name} system routes a request to a "
                f"desk according to the request's type. When a request is "
                f"referred on to the next office, the name of the desk that "
                f"handled it becomes its type at that next office.")

    def _worked(self) -> str:
        a, b = self.map_names[0], self.map_names[1]
        s = self.run(self.example_start, 2)
        return (f"A worked referral.\n\n"
                f"A {s[0]} request arrives at the {a} office. A {s[0]} is "
                f"handled by the {s[1]} desk. The request is referred to the "
                f"{b} office, where its type is now {s[1]}. A {s[1]} is handled "
                f"by the {s[2]} desk. The desk that handles it at the {b} "
                f"office is the {s[2]} desk.")

    def pages(self, rng: random.Random) -> list[str]:
        pages = [self._preamble(),
                 self._table(self.distractor_name, self.distractor,
                             self.levels[0])]
        if self.max_depth >= 2:
            pages.append(self._worked())
        for i, m in enumerate(self.map_names):
            pages.append(self._table(m, self.maps[i], self.levels[i]))
        rng.shuffle(pages)
        return pages

    def minimal_pages(self, depth: int) -> list[str]:
        """Only what the chain needs, in chain order: the gold source chapter
        of the rescue matrix. No distractor, no worked example, no unused map.
        This is the most favourable evidence condition the task admits, and it
        keeps the prompt inside the length the checkpoint was trained on."""
        return [self._preamble()] + [
            self._table(self.map_names[i], self.maps[i], self.levels[i])
            for i in range(depth)
        ]

    # ------------------------------------------------------------- questions

    def question_text(self, start: str, depth: int) -> str:
        """Depth one is the substitution_rule question verbatim in shape. Each
        extra step adds one referral clause and moves the office named in the
        wh-question one office further along."""
        chain = self.chain(depth)
        head = f"A {start} request arrives at the {chain[0]} office."
        if depth == 1:
            return head + " Which desk handles it?"
        hops = ", then to the ".join(chain[1:])
        return (f"{head} It is then referred to the {hops} office. "
                f"Which desk handles it at the {chain[-1]} office?")

    def problems(self, rng: random.Random, depth: int, n: int) -> list[dict]:
        """Sample n depth-d problems that survive every exclusion."""
        out: list[dict] = []
        starts = list(self.starts)
        rng.shuffle(starts)
        for start in starts:
            if len(out) >= n:
                break
            stages = self.run(start, depth)
            gold = stages[-1]
            if len(set(stages)) != len(stages):
                # Distinct stages keep the stopped-early diagnostic unambiguous.
                continue
            if depth > 1 and gold == self.maps[depth - 1].get(start):
                # The last map applied straight to the starting token must not
                # coincide with the answer.
                continue
            text = self.question_text(start, depth)
            if _mentions(gold, text):
                continue
            out.append({
                "qid": f"d{depth}_{len(out)}",
                "kind": f"chain{depth}",
                "depth": depth,
                "start": start,
                "chain": self.chain(depth),
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
                     alphabet_size: int = ALPHABET_SIZE,
                     max_depth: int = N_MAPS, typed: bool = True) -> dict:
    """One RL-shaped episode at a fixed composition depth.

    pages selects the evidence condition. "correct" gives the system's own
    pages. "wrong" gives the pages of a different system over a different
    alphabet, so the question is unanswerable but the prompt is the same
    shape. "blank" gives a single empty placeholder page.
    """
    # The system depends on the seed only, never on the depth, so the very
    # same notation and the very same page set are used at every depth. Only
    # the question changes down the curve.
    rng = random.Random(seed * 7919)
    system = MinSystem(rng, alphabet_size=alphabet_size, max_depth=max_depth,
                       typed=typed)
    problems = system.problems(rng, depth, n_problems)
    if pages == "correct":
        docs = system.pages(rng)
    elif pages == "minimal":
        docs = system.minimal_pages(depth)
    elif pages == "wrong":
        other = MinSystem(random.Random((seed * 7919) ^ 0x5EED),
                          alphabet_size=alphabet_size, max_depth=max_depth,
                          typed=typed)
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
        "max_depth": max_depth,
        "typed": typed,
        "pages_condition": pages,
        "world": {"domain": "skill_minrepro"},
        "n_context": 0,
        "documents": [{"text": p} for p in docs],
        "alphabet": system.universe,
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
                alphabet_size: int = ALPHABET_SIZE,
                max_depth: int = N_MAPS, typed: bool = True) -> dict:
    n_eps = n_q = 0
    with open(path, "w") as fh:
        for s in seeds:
            ep = generate_episode(s, depth, n_problems=n_problems, pages=pages,
                                  alphabet_size=alphabet_size,
                                  max_depth=max_depth, typed=typed)
            if in_context:
                ep["n_context"] = len(ep["documents"])
            fh.write(json.dumps(ep) + "\n")
            n_eps += 1
            n_q += len(ep["questions"])
    return {"path": path, "episodes": n_eps, "questions": n_q, "depth": depth,
            "pages": pages, "in_context": in_context,
            "alphabet_size": alphabet_size, "typed": typed}


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
            m = re.search(rf"A {re.escape(stages[0])} is handled by the (\w+) desk",
                          page)
            if m and m.group(1) == gold:
                hits["keyword_nearest"] += 1
            # A reader that ignores the referral chain and looks the starting
            # type up in the table of the office the question asks about.
            last = q["chain"][-1]
            m2 = re.search(
                rf"{re.escape(last)} office are routed by their type\.(.*?)(?:\n\n|$)",
                blob, re.S)
            if m2:
                m3 = re.search(
                    rf"A {re.escape(stages[0])} is handled by the (\w+) desk",
                    m2.group(1))
                if m3 and m3.group(1) == gold:
                    hits["last_office_on_start"] += 1
    return {
        "n_questions": n,
        # Chance is one over the alphabet of a single level, because the type
        # of the answer is fixed once the last map is named.
        "chance": 1.0 / episodes[0]["alphabet_size"] if episodes else 0.0,
        "violations": dict(viol),
        "baselines": {k: v / n for k, v in hits.items()},
        "max_symbol_frequency_spread": max(freq_spread) if freq_spread else 0,
    }


# -------------------------------------------------------------------- eval

def hits_target(answer: str, target: str, slack: int = 6) -> bool:
    """The environment's own grading rule, reused so that the diagnostic
    classes and the reported accuracy agree. The model answers in the family's
    idiom ("the clomel desk"), which is a correct answer and which a bare
    exact match would throw away."""
    from src.evals.naturalized import contains_answer, exact_match, normalize

    if exact_match(answer, target):
        return True
    pred = normalize(answer).split()
    want = normalize(target).split()
    if not pred or len(pred) > len(want) + slack:
        return False
    return contains_answer(answer, target)


def classify(answer: str, q: dict, alphabet: list[str]) -> str:
    """Which token the answer actually names. correct is the final stage;
    stopped_at_k means the answer names the k-th intermediate, which is the
    signature of a chain that ran and then halted early."""
    stages = q["stages"]
    if hits_target(answer, stages[-1]):
        return "correct"
    for k, s in enumerate(stages[:-1]):
        if hits_target(answer, s):
            return "echoed_start" if k == 0 else f"stopped_at_{k}"
    for a in alphabet:
        if hits_target(answer, a):
            return "other_token"
    return "no_token"


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
        ok = cls == "correct"
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
        "accuracy": strict / max(1, len(rolls)),
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
    g.add_argument("--max-depth", type=int, default=N_MAPS)
    g.add_argument("--untyped", action="store_true",
                   help="one shared alphabet, so every token is both a key "
                        "and a value; the referent-ambiguity control")
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
        typed = not args.untyped
        kind = "t" if typed else "u"
        for d in depths:
            for pages in conds:
                for p in pres:
                    ctx = p == "ctx"
                    tag = f"{kind}a{args.alphabet}-d{d}-{pages}-{p}"
                    path = os.path.join(args.out_dir, f"{tag}.jsonl")
                    manifest.append(write_jsonl(
                        path, seeds, d, n_problems=args.problems, pages=pages,
                        in_context=ctx, alphabet_size=args.alphabet,
                        max_depth=args.max_depth, typed=typed))
        eps = [generate_episode(s, d, n_problems=args.problems,
                                alphabet_size=args.alphabet,
                                max_depth=args.max_depth, typed=typed)
               for d in depths for s in seeds]
        report = audit_episodes(eps)
        report["manifest"] = manifest
        with open(os.path.join(args.out_dir,
                               f"audit-{kind}a{args.alphabet}.json"), "w") as fh:
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
