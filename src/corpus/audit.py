"""The checks a corpus has to pass before a training run is spent on it.

Four necessity exclusions and a set of shortcut readers, written to match the
ones the project already uses so a number here is comparable with one there:

  answer_in_question       `src/disc/renderers.py:chain_violations`
  answer_is_start          same
  answer_is_intermediate   same
  stages_not_distinct      same

  most_frequent_symbol     `src/disc/minrepro.py:audit_episodes`
  copy_start               same
  depth_one_stop           same
  keyword_nearest          same, but the pattern comes from the frame rather
                           than being written for the routing wording, so the
                           attack is as strong in every frame as it is in the
                           trained one
  random_candidate         `src/falsify/probe.py:h_random_nonce` in spirit
  most_frequent_nonce      `src/falsify/probe.py:h_freq_nonce`
  last_nonce               `src/falsify/probe.py:h_last_nonce`

The value blind readers are the ones that never look at the served pages for
the question's own key: `most_frequent_symbol`, `copy_start`,
`depth_one_stop`, `random_candidate`, `most_frequent_nonce` and `last_nonce`.
Those must sit at or below chance. `keyword_nearest` reads the page and is
expected to score, since the task is to read the page; it is reported so a
frame cannot look safe merely because the attack was written for a different
wording.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from collections import Counter

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def mentions(token: str, text: str) -> bool:
    """`src/disc/minrepro.py:_mentions`, verbatim."""
    return re.search(rf"(?<![\w]){re.escape(str(token))}(?![\w])",
                     text) is not None


# ------------------------------------------------------------- retrieval

class MiniBM25:
    """Okapi BM25 over the episode's own pages, in the standard library.

    `src/train/retrieval.py:BM25Index` needs numpy, and the corpus builder runs
    in forked worker processes where importing it per shard is wasteful. The
    ranking is the same formula with the same defaults.
    """

    def __init__(self, texts, k1: float = 1.5, b: float = 0.75):
        self.texts = list(texts)
        self.docs = [[w.lower() for w in WORD_RE.findall(t)] for t in self.texts]
        self.k1, self.b = k1, b
        self.n = len(self.docs)
        self.lens = [len(d) for d in self.docs]
        self.avg = sum(self.lens) / self.n if self.n else 0.0
        self.tf = [Counter(d) for d in self.docs]
        df: Counter = Counter()
        for d in self.docs:
            df.update(set(d))
        self.idf = {w: math.log(1 + (self.n - c + 0.5) / (c + 0.5))
                    for w, c in df.items()}

    def top(self, query: str) -> int:
        q = [w.lower() for w in WORD_RE.findall(query)]
        best, best_i = -1.0, 0
        for i, tf in enumerate(self.tf):
            s = 0.0
            for w in q:
                if w not in tf:
                    continue
                f = tf[w]
                denom = f + self.k1 * (1 - self.b + self.b *
                                       self.lens[i] / (self.avg or 1.0))
                s += self.idf.get(w, 0.0) * f * (self.k1 + 1) / denom
            if s > best:
                best, best_i = s, i
        return best_i


# -------------------------------------------------------------- necessity

VIOLATIONS = ("answer_in_question", "answer_is_start",
              "answer_is_intermediate", "stages_not_distinct")

BLIND_READERS = ("most_frequent_symbol", "copy_start", "depth_one_stop",
                 "random_candidate", "most_frequent_nonce", "last_nonce")

PAGE_READERS = ("keyword_nearest",)


def violations(question, page_text: str) -> dict:
    """The four exclusions, on the wording actually shown."""
    gold = str(question["answer"])
    stages = [str(s) for s in question["stages"]]
    out = dict.fromkeys(VIOLATIONS, 0)
    if mentions(gold, question["text"]):
        out["answer_in_question"] = 1
    if stages and gold == stages[0]:
        out["answer_is_start"] = 1
    if gold in stages[:-1]:
        out["answer_is_intermediate"] = 1
    if len(set(stages)) != len(stages):
        out["stages_not_distinct"] = 1
    return out


def nonce_words(texts, reserved) -> list:
    """Words on the served pages that are not the frame's own English."""
    out = []
    for t in texts:
        for w in WORD_RE.findall(t):
            lw = w.lower()
            if lw not in reserved:
                out.append(lw)
    return out


def shortcut_hits(episode, frame, reserved, rng) -> dict:
    """Score every shortcut reader on one episode. Counts, not rates."""
    texts = [d["text"] for d in episode["documents"]]
    blob = "\n".join(texts)
    index = MiniBM25(texts)
    nonces = nonce_words(texts, reserved)
    freq = Counter(nonces)
    top_nonce = freq.most_common(1)[0][0] if freq else ""
    last = nonces[-1] if nonces else ""
    hits = Counter()
    n = 0
    for q in episode["questions"]:
        n += 1
        gold = str(q["answer"]).lower()
        stages = [str(s).lower() for s in q["stages"]]
        cands = [str(c).lower() for c in q.get("candidates") or []]
        counts = {c: len(re.findall(rf"(?<![\w]){re.escape(c)}(?![\w])", blob))
                  for c in cands}
        if counts and gold == max(counts, key=lambda c: counts[c]):
            hits["most_frequent_symbol"] += 1
        if stages and gold == stages[0]:
            hits["copy_start"] += 1
        if len(stages) > 2 and gold == stages[1]:
            hits["depth_one_stop"] += 1
        if cands and rng.choice(cands) == gold:
            hits["random_candidate"] += 1
        if top_nonce == gold:
            hits["most_frequent_nonce"] += 1
        if last == gold:
            hits["last_nonce"] += 1
        key = q.get("lookup_key")
        if key is not None:
            page = texts[index.top(q["text"])]
            m = re.search(frame.lookup_regex(str(key)), page)
            if m and m.group(1).lower() == gold:
                hits["keyword_nearest"] += 1
    return {"n_questions": n, "hits": dict(hits)}


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    """A Wilson interval, as `src/primitives/common.py:wilson` computes it.

    A blind reader is called above chance only when the lower bound clears the
    floor. Reporting a point estimate against the floor would flag every reader
    that happened to land a fraction high, and with a few hundred items that is
    most of them.
    """
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centre - half), min(1.0, centre + half)


def chance_floor(question) -> float:
    cands = question.get("candidates") or []
    if cands:
        return 1.0 / len(set(cands))
    return 0.0


# ---------------------------------------------------------- answer source

STATED = "stated_in_a_chapter"
DERIVED = "derived_by_computation"


def answer_source(answer, page_texts) -> str:
    """Labelled by reading the served pages, not by asking the generator.

    `src/mathgen/exercises.py:answer_source` makes the same distinction the
    same way: an answer that stands as a whole token somewhere in the served
    prose is answerable by copying, and one that does not is not. Pooling the
    two hid a result on this project, so the label is carried per question and
    every count is reported split by it.
    """
    a = str(answer)
    for t in page_texts:
        if mentions(a, t):
            return STATED
    return DERIVED


# ------------------------------------------------------------- parity

def token_lengths(episodes, encode) -> dict:
    """Prompt token length statistics, per the template ablation's measure.

    `src/rl/env.py:load_tasks` drops any task whose prompt exceeds
    `max_prompt_tokens`, 384 by default. A frame that runs systematically long
    would therefore lose its longest items and its sample would differ from
    every other frame's, which is exactly the rival explanation the parity
    check exists to remove.
    """
    lens = []
    for ep in episodes:
        docs = sum(len(encode(d["text"])) for d in ep["documents"])
        for q in ep["questions"]:
            lens.append(docs + len(encode(q["text"])) + 8)
    lens.sort()
    if not lens:
        return {"n": 0}
    def pct(p):
        return lens[min(len(lens) - 1, int(p * len(lens)))]
    return {"n": len(lens), "min": lens[0], "p25": pct(0.25),
            "median": pct(0.5), "p75": pct(0.75), "p95": pct(0.95),
            "max": lens[-1], "mean": sum(lens) / len(lens),
            "over_384": sum(1 for x in lens if x > 384)}


def parity_report(by_frame: dict, tolerance: float = 0.10) -> dict:
    """Whether every frame's median prompt length sits inside one band."""
    meds = {k: v["median"] for k, v in by_frame.items() if v.get("n")}
    if not meds:
        return {"frames": 0, "passes": False}
    grand = sorted(meds.values())[len(meds) // 2]
    dev = {k: (m - grand) / grand for k, m in meds.items()}
    worst = max(dev, key=lambda k: abs(dev[k]))
    return {
        "frames": len(meds),
        "grand_median": grand,
        "tolerance": tolerance,
        "worst_frame": worst,
        "worst_deviation": dev[worst],
        "n_outside_tolerance": sum(1 for d in dev.values()
                                   if abs(d) > tolerance),
        "passes": all(abs(d) <= tolerance for d in dev.values()),
        "per_frame_median": meds,
    }


# --------------------------------------------------------- gold agreement

def gold_agreement(records_by_frame: dict) -> dict:
    """Every frame must give the same gold answer for the same seed and qid.

    This is the check that says the frame bank varies the wording and nothing
    else. A mismatch means a frame is changing the task, and any accuracy
    difference across frames would then be uninterpretable.
    """
    keys = None
    mismatches = []
    n = 0
    ref_name = None
    ref = {}
    for fid, recs in sorted(records_by_frame.items()):
        table = {}
        for r in recs:
            for q in r["questions"]:
                table[(r["seed"], r["family"], q["qid"])] = str(q["answer"])
        if keys is None:
            keys, ref, ref_name = set(table), table, fid
            n = len(table)
            continue
        if set(table) != keys:
            mismatches.append({"frame": fid, "reason": "key set differs",
                               "missing": len(keys - set(table)),
                               "extra": len(set(table) - keys)})
            continue
        bad = [k for k in keys if table[k] != ref[k]]
        if bad:
            mismatches.append({"frame": fid, "reason": "gold differs",
                               "n_bad": len(bad),
                               "example": [list(bad[0]), ref[bad[0]],
                                           table[bad[0]]]})
    return {"reference_frame": ref_name, "n_items_per_frame": n,
            "n_frames": len(records_by_frame), "n_mismatched_frames":
            len(mismatches), "mismatches": mismatches[:8],
            "passes": not mismatches}


# ------------------------------------------------------------ disjointness

# Every seed namespace another evaluation set already owns. A corpus seed
# inside any of these would put a training item and an evaluation item in the
# same world.
RESERVED_SEED_RANGES = {
    "latentret_eval": (900_000, 1_000_000),
    "pointer_copy_bench_eval": (1_000_000, 1_100_000),
    "falsify_conditions": (2_900_000, 3_150_000),
    "falsify_twin_offset": (3_324_242, 3_574_242),
    "falsify_wrong_textbook_offset": (3_677_000, 3_927_000),
    "dependency_sweep": (4_100_000, 4_200_000),
    "falsify_template_vocab_simple": (5_000_000, 5_001_000),
    "falsify_template_vocab_new": (5_500_000, 5_501_000),
    "audit_twin_worlds": (700_000_000, 700_100_000),
    "opgraph_eval_worlds": (900_000_000, 906_100_000),
    # src/pilot/items.py: the acquisition pilot's items (910M-934M), its
    # smoke set (5M above those) and its floor pools (945M-948M).
    "pilot_acq_items_and_floor_pools": (910_000_000, 950_000_000),
    "worldgen_heldout_index": (1_000_000_000, 1 << 62),
}

CORPUS_TRAIN_SEED0 = 300_000_000
CORPUS_TRAIN_SEED1 = 340_000_000
CORPUS_HELDOUT_SEED0 = 350_000_000
CORPUS_HELDOUT_SEED1 = 351_000_000


def seed_disjointness(used_seeds) -> dict:
    """Name the check: reserved range interval test, over the seeds actually used."""
    used = sorted(set(int(s) for s in used_seeds))
    clashes = {}
    for name, (lo, hi) in RESERVED_SEED_RANGES.items():
        hit = [s for s in used if lo <= s < hi]
        if hit:
            clashes[name] = {"n": len(hit), "example": hit[:4]}
    in_train = [s for s in used if CORPUS_TRAIN_SEED0 <= s < CORPUS_TRAIN_SEED1]
    in_held = [s for s in used
               if CORPUS_HELDOUT_SEED0 <= s < CORPUS_HELDOUT_SEED1]
    return {
        "check": "reserved_seed_range_interval_test",
        "n_seeds": len(used),
        "min": used[0] if used else None,
        "max": used[-1] if used else None,
        "n_in_corpus_train_band": len(in_train),
        "n_in_corpus_heldout_band": len(in_held),
        "n_outside_both_bands": len(used) - len(in_train) - len(in_held),
        "clashes": clashes,
        "passes": not clashes and len(in_train) + len(in_held) == len(used),
    }


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def question_hash(question_text: str, answer: str) -> str:
    return content_hash(f"{question_text.strip()}\x00{str(answer).strip()}")


def hash_disjointness(train_hashes, heldout_hashes, external_hashes) -> dict:
    """Name the check: sha256 question and answer content hash intersection.

    Seeds alone are not enough. Two different seeds can draw the same short
    question, and a held-out set that shares an item with training is leaked
    whatever its seed says. The hash is over the question text and the gold
    answer together, so an item counts as shared only when both match.
    """
    tr = set(train_hashes)
    ho = set(heldout_hashes)
    out = {
        "check": "sha256_question_answer_content_hash_intersection",
        "n_train": len(tr),
        "n_heldout": len(ho),
        "train_heldout_overlap": len(tr & ho),
        "external": {},
        "passes": True,
    }
    for name, hs in external_hashes.items():
        h = set(hs)
        k = len(tr & h)
        out["external"][name] = {"n_external": len(h), "overlap_with_train": k}
        if k:
            out["passes"] = False
    if tr & ho:
        out["passes"] = False
    return out
