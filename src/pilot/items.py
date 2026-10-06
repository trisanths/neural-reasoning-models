"""The pilot item set: three families of never-seen procedures, four page conditions.

  refuniverse  src/mathgen/refuniverse.py with int_answers, levels 1 to 8,
               one item per level per universe. Every answer is one whole
               number below a prime modulus between 97 and 131.
  algebra      src/mathgen/adapter.py, levels 2 to 5, at most two items per
               level per universe. Answers are object names, lists of them,
               or counts.
  skillacq     src/pilot/skills.py over binary_op and the three simple rule
               families.

Floors are per item and per condition; the section "floors" below says how
they are made. In short: an integer item's floor is the larger of one over
its answer space and the best single answer's rate in a pool of items the
same pipeline emits from separate seeds; a names item's floor is one over its
answer space where the names can be read, and zero in closed book and blank,
where they cannot.

Every item passes the eight-check guard in src/mathgen/bench.py against its
own library, and again (Guard.check_served) against the pages its sibling and
blank conditions serve. The sibling must also serve the oracle's chapter
ids, carry every question word the oracle pages carry, and answer the
question (bench.sibling_match). Integer items pass one more screen first,
naive_arithmetic: the gold must not be reachable by combining the integers
printed in the question with real operators (+ - * % / ^ & | and |a - b|).
A model that reads an invented glyph as one of those and skips the modular
reduction would otherwise land some answers closed book, which is a leak of
prior knowledge rather than of the pages, and rule 1 of the pilot would read
it as a broken guard. And an item the hedging canary answers (an algebra
extension that holds of every object, so naming all of them is the gold) is
dropped, because the strict grader cannot tell knowing from hedging on it.

Rule families pose their fallback case far more often than their stated case,
so their gold labels are balanced: each label is capped at an equal share of
the family's quota and a universe gives at most one item per label.

Seeds are drawn from bases at 910,000,000 and above, and every seed is checked
against the ranges the training manifests in runs/data-manifests occupy
before anything is generated: each base seed, the worldgen episode index
range [0, chunks * episode_stride), and the derived episode seed range
base * 1,000,003 plus that index range.

  python -m src.pilot.items --manifests /mnt/nvme/pilot/data-manifests \\
      --floor-table /mnt/nvme/pilot/items/floor_table.json \\
      --out /mnt/nvme/pilot/items/items.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from collections import Counter, defaultdict

from src.mathgen.bench import (build_problem_set, prompt_blank,
                               prompt_closed_book, prompt_oracle,
                               prompt_sibling, served_blank, served_oracle,
                               served_sibling, sibling_of)
from src.mathgen.interface import LEVEL_NAMES
from src.pilot.grade import canary_reply, grade

CONDITIONS = ("closed_book", "oracle", "sibling", "blank")

SEED_BASE = {
    "refuniverse": 910_000_000,
    "algebra": 920_000_000,
    "binary_op": 930_000_000,
    "threshold_rule": 931_000_000,
    "substitution_rule": 932_000_000,
    "exception_rule": 933_000_000,
}
SMOKE_OFFSET = 5_000_000
EPISODE_STRIDE_MULT = 1_000_003   # src/worldgen/engine.py SEED_STRIDE

FULL_QUOTA = {
    "refuniverse": {lv: 100 for lv in range(1, 9)},
    "algebra": {lv: 110 for lv in (2, 3, 4, 5)},
    "binary_op": {None: 50},
    "threshold_rule": {None: 50},
    "substitution_rule": {None: 50},
    "exception_rule": {None: 50},
}
SMOKE_QUOTA = {
    "refuniverse": {lv: 1 for lv in range(1, 9)},
    "algebra": {lv: 2 for lv in (2, 3, 4, 5)},
    "binary_op": {None: 2},
    "threshold_rule": {None: 2},
    "substitution_rule": {None: 2},
    "exception_rule": {None: 2},
}
ALGEBRA_PER_LEVEL = 2     # cap per algebra universe per level
SKILL_PER_UNIVERSE = 2
SKILL_CANDIDATES = 8      # guarded candidates drawn per skill universe


# --------------------------------------------------------------------------
# seeds and the training manifests
# --------------------------------------------------------------------------
def manifest_ranges(manifest_dir: str) -> list[dict]:
    """Integer seed ranges the training manifests occupy, half-open."""
    out = []
    for name in sorted(os.listdir(manifest_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(manifest_dir, name)) as fh:
            m = json.load(fh)
        base = int(m["base_seed"])
        stride = int(m.get("episode_stride") or 0)
        n_chunks = len(m.get("chunks") or [])
        span = max(stride * n_chunks, 1)
        out.append({"manifest": name, "what": "base_seed",
                    "lo": base, "hi": base + 1})
        out.append({"manifest": name, "what": "worldgen_index",
                    "lo": 0, "hi": span})
        out.append({"manifest": name, "what": "episode_seed",
                    "lo": base * EPISODE_STRIDE_MULT,
                    "hi": base * EPISODE_STRIDE_MULT + span})
    if not out:
        raise SystemExit(f"no manifests found in {manifest_dir}")
    return out


def check_seed_ranges(seed_ranges: dict, ranges: list[dict]) -> list[str]:
    """Overlaps between [lo, hi) seed ranges used here and the manifests."""
    bad = []
    for fam, (lo, hi) in seed_ranges.items():
        for r in ranges:
            if lo < r["hi"] and r["lo"] < hi:
                bad.append(f"{fam} [{lo},{hi}) overlaps {r['manifest']} "
                           f"{r['what']} [{r['lo']},{r['hi']})")
    return bad


# --------------------------------------------------------------------------
# the naive-arithmetic screen
# --------------------------------------------------------------------------
# Every glyph in skillacq.systems.GLYPHS that is also a real operator gets
# its ordinary reading here: + - * for arithmetic, % as remainder, / as
# whole division, ^ as a power (and as exclusive or), & and | as bitwise
# and/or, and | also as the absolute difference |a - b|.
_POW_MAX_EXP = 4
_VALUE_CAP = 10 ** 7


def _apply_ops(a: int, b: int) -> set[int]:
    out = {a + b, a - b, a * b, abs(a - b), a & b, a | b, a ^ b}
    if b != 0:
        out.add(a % b)
        out.add(a // b)
    if 0 <= b <= _POW_MAX_EXP and abs(a) <= 10 ** 4:
        out.add(a ** b)
    return {v for v in out if abs(v) <= _VALUE_CAP}


def naive_values(text: str) -> set[int]:
    """Every value reachable from the question's integers with real operators.

    Any subset of the first four integers, combined in any order and any
    bracketing (a dynamic programme over index subsets), each number used
    at most once.
    """
    nums = [int(v) for v in re.findall(r"(?<![\w.])-?\d+(?![\w])", text)][:4]
    if not nums:
        return set()
    vals: dict[int, set[int]] = {1 << i: {v} for i, v in enumerate(nums)}
    full = (1 << len(nums)) - 1
    for mask in sorted(range(1, full + 1), key=lambda m: bin(m).count("1")):
        if mask in vals:
            continue
        acc: set[int] = set()
        sub = (mask - 1) & mask
        while sub:
            rest = mask ^ sub
            for a in vals[sub]:
                for b in vals[rest]:
                    acc |= _apply_ops(a, b)
            sub = (sub - 1) & mask
        vals[mask] = acc
    out: set[int] = set()
    for v in vals.values():
        out |= v
    return out


def naive_screen(p) -> str | None:
    if not re.fullmatch(r"-?\d+", p.answer.strip()):
        return None
    if int(p.answer) in naive_values(p.text):
        return "naive_arithmetic"
    return None


# --------------------------------------------------------------------------
# item records
# --------------------------------------------------------------------------
def _json_safe(meta: dict) -> dict:
    return json.loads(json.dumps(meta, default=str))


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def _answer_fields(family: str, p, universe) -> dict:
    if family == "refuniverse":
        m = universe.p.modulus
        return {"answer_kind": "int", "candidates": None, "answer_space": m,
                "floor_space": 1.0 / m, "modulus": m}
    if family == "algebra":
        from src.mathgen.exercises import GUESS_SPACE

        s = universe.theory.structure
        kind = p.meta["answer_kind"]
        space = GUESS_SPACE[kind](s)
        if kind == "count":
            return {"answer_kind": "int", "candidates": None,
                    "answer_space": space, "floor_space": 1.0 / space,
                    "algebra_kind": kind, "modulus": None}
        return {"answer_kind": "names", "candidates": list(s.elements),
                "answer_space": space, "floor_space": 1.0 / space,
                "algebra_kind": kind, "modulus": None}
    cands = p.meta.get("candidates")
    space = p.meta["answer_space"]
    if cands:
        return {"answer_kind": "names", "candidates": cands,
                "answer_space": len(cands), "floor_space": 1.0 / len(cands),
                "modulus": None}
    return {"answer_kind": "int", "candidates": None, "answer_space": space,
            "floor_space": 1.0 / space,
            "modulus": getattr(universe.system, "modulus", None) or None}


# --------------------------------------------------------------------------
# floors
# --------------------------------------------------------------------------
# An integer item's floor is the larger of two rates: one over its answer
# space, and the rate of the best single answer across a pool of items the
# same pipeline (generator, guard, controls, screen) emits from seeds kept
# for that purpose. The pool rate is what a reader who has never seen the
# item's pages can reach by always giving the commonest gold of the item's
# level or question kind; one over the modulus is far below it wherever the
# generator's answers are not uniform (a conductor is an orbit length, a
# tied argmax is often 0 or 1). The pool is read by bucket:
#
#   refuniverse|L<level>          every refuniverse level
#   algebra|L<level>|count        algebra count questions
#   binary_op|<kind>              direct, nested and solve_for questions
#
# A names item's floor is one over its answer space where the candidate
# names can be read. Where the prompt does not show every gold name (closed
# book, and blank pages, for every names item in this set: the guard keeps
# the gold out of the question), no reader that has not seen the pages can
# produce the gold, so the floor in those two conditions is zero.
FLOOR_FAMILIES = ("refuniverse", "algebra", "binary_op")
FLOOR_SEED_BASE = {"refuniverse": 945_000_000, "algebra": 946_000_000,
                   "binary_op": 947_000_000}
FLOOR_POOL_UNIVERSES = {"refuniverse": 3000, "algebra": 400, "binary_op": 1500}


def floor_bucket(family: str, level, answer_kind: str, meta: dict) -> str | None:
    if answer_kind != "int":
        return None
    if family == "refuniverse":
        return f"refuniverse|L{level}"
    if family == "algebra":
        return f"algebra|L{level}|{meta.get('answer_kind')}"
    if family == "binary_op":
        return f"binary_op|{meta.get('kind')}"
    return None


def _family_build(family: str):
    """(universe module, universe kwargs, levels, per_level) for a family."""
    if family == "refuniverse":
        return None, {"int_answers": True}, tuple(range(1, 9)), 1
    if family == "algebra":
        return "src.mathgen.adapter", {}, (2, 3, 4, 5), ALGEBRA_PER_LEVEL
    return "src.pilot.skills", {"family": family}, (1,), SKILL_CANDIDATES


def compute_floor_table(n_universes: dict | None = None,
                        families=FLOOR_FAMILIES) -> dict:
    """The best-single-answer rate per bucket, over a pool of guarded items."""
    n_universes = {**FLOOR_POOL_UNIVERSES, **(n_universes or {})}
    counts: dict = defaultdict(Counter)
    seeds: dict = {}
    for fam in families:
        module, kwargs, levels, per_level = _family_build(fam)
        if fam == "algebra":
            per_level = 50          # every guarded exercise of the level
        base = FLOOR_SEED_BASE[fam]
        seeds[fam] = [base, base + n_universes[fam]]
        for seed in range(base, base + n_universes[fam]):
            ps = build_problem_set([seed], per_level=per_level, levels=levels,
                                   universe_module=module, rng_seed=seed,
                                   controls=("sibling", "blank"),
                                   screen=naive_screen, universe_kwargs=kwargs)
            for p in ps.problems:
                if not re.fullmatch(r"-?\d+", p.answer.strip()):
                    continue
                key = floor_bucket(fam, p.level, "int", p.meta)
                if key:
                    counts[key][str(int(p.answer))] += 1
    table = {}
    for key, c in sorted(counts.items()):
        n = sum(c.values())
        mode, top = min(c.items(), key=lambda kv: (-kv[1], int(kv[0])))
        table[key] = {"n": n, "mode": mode, "rate": top / n,
                      "n_distinct": len(c)}
    return {"buckets": table, "seed_ranges": seeds,
            "pool_universes": {f: n_universes[f] for f in families}}


def _gold_visible(rec: dict, cond: str) -> bool:
    prompt = rec["prompts"][cond].lower()
    golds = [g.strip().lower() for g in rec["answer"].split(",") if g.strip()]
    return all(re.search(rf"(?<![\w]){re.escape(g)}(?![\w])", prompt)
               for g in golds)


def item_floors(rec: dict, floor_table: dict | None) -> dict:
    """Per-condition floors, and what they were made from."""
    key = floor_bucket(rec["family"], rec["level"], rec["answer_kind"],
                       rec["meta"])
    best = None
    if key and floor_table:
        entry = floor_table.get("buckets", {}).get(key)
        best = entry["rate"] if entry else None
    open_floor = max(rec["floor_space"], best or 0.0)
    floors = {"oracle": open_floor, "sibling": open_floor}
    for cond in ("closed_book", "blank"):
        if rec["answer_kind"] == "names" and not _gold_visible(rec, cond):
            floors[cond] = 0.0
        else:
            floors[cond] = open_floor
    return {"floor": open_floor, "floors": floors, "floor_bucket": key,
            "floor_best_constant": best}


def item_record(family: str, p, universe, sibling,
                floor_table: dict | None = None) -> dict:
    prompts = {
        "closed_book": prompt_closed_book(p),
        "oracle": prompt_oracle(p, universe),
        "sibling": prompt_sibling(p, universe, sibling),
        "blank": prompt_blank(p, universe),
    }
    pages = {
        "closed_book": [],
        "oracle": served_oracle(p, universe),
        "sibling": served_sibling(p, universe, sibling),
        "blank": served_blank(p, universe),
    }
    rec = {
        "item_id": p.problem_id,
        "family": family,
        "level": p.level if family in ("refuniverse", "algebra") else None,
        "level_name": (LEVEL_NAMES[p.level]
                       if family in ("refuniverse", "algebra") else None),
        "universe_id": p.universe_id,
        "seed": universe.seed,
        "question": p.text,
        "answer": p.answer,
        "target_chapters": list(p.target_chapters),
        "sibling_universe": sibling.universe_id,
        "sibling_answer": sibling.reference_answer(p),
        "pages": pages,
        "prompts": prompts,
        "prompt_hashes": {c: prompt_hash(v) for c, v in prompts.items()},
        "meta": _json_safe(p.meta),
    }
    rec.update(_answer_fields(family, p, universe))
    rec.update(item_floors(rec, floor_table))
    return rec


# --------------------------------------------------------------------------
# generation per family
# --------------------------------------------------------------------------
def _merge_discards(acc: dict, ps) -> None:
    for name, entry in ps.discards.items():
        slot = acc.setdefault(name, Counter())
        slot["distinct_emitted"] += entry["distinct_emitted"]
        slot["kept"] += entry["kept"]
        for check, n in entry["by_check"].items():
            slot[check] += n


def _label(rec: dict):
    """The gold's position in a closed candidate list, None for numbers."""
    if rec["answer_kind"] != "names" or rec["family"] == "algebra":
        return None
    return rec["candidates"].index(rec["answer"])


def _fill(family: str, quota: dict, base: int, module: str | None,
          kwargs: dict, per_level: int, max_seeds: int,
          per_universe: int | None = None, balance_labels: bool = False,
          floor_table: dict | None = None):
    """Draw universes from base upward until every level's quota is met.

    Each universe is asked only for the levels still short, so a level whose
    guard discards often is topped up from extra universes and the levels
    that filled on time are not touched by them.

    balance_labels caps each gold label at an equal share of the quota and
    takes at most one item per label from a universe. A rule family asks
    its fallback case far more often than its stated case (one stated
    exception key against any number of other words), so without the cap a
    model that always names the fallback label would sit far above a floor
    of one over the labels.
    """
    have: dict = defaultdict(list)
    label_count: Counter = Counter()
    discards: dict = {}
    used_seeds: list[int] = []
    seed = base
    while any(len(have[lv]) < n for lv, n in quota.items()):
        if seed - base >= max_seeds:
            short = {lv: n - len(have[lv]) for lv, n in quota.items()
                     if len(have[lv]) < n}
            raise RuntimeError(f"{family}: quota not met after {max_seeds} "
                               f"seeds, short {short}")
        levels = tuple(lv for lv, n in quota.items() if len(have[lv]) < n)
        build_levels = tuple(1 if lv is None else lv for lv in levels)
        ps = build_problem_set([seed], per_level=per_level, levels=build_levels,
                               universe_module=module, rng_seed=seed,
                               controls=("sibling", "blank"),
                               screen=naive_screen, universe_kwargs=kwargs)
        _merge_discards(discards, ps)
        u = next(iter(ps.universes.values()))
        took = 0
        labels_here: set = set()
        for p in ps.problems:
            lv = None if None in quota else p.level
            if len(have[lv]) >= quota[lv]:
                continue
            if per_universe is not None and took >= per_universe:
                break
            sib = ps.siblings.get(p.problem_id) or sibling_of(u, 1)
            rec = item_record(family, p, u, sib, floor_table)
            # An item whose gold is every candidate at once (an algebra
            # extension that holds of every object) is answered by the
            # hedging canary, so the strict grader cannot tell knowing from
            # hedging on it. It is not asked.
            if grade(canary_reply(rec), rec)["correct"]:
                slot = discards.setdefault(LEVEL_NAMES.get(p.level, "skill"),
                                           Counter())
                slot["canary_answers_it"] += 1
                slot["kept"] -= 1
                continue
            if balance_labels:
                lab = _label(rec)
                n_labels = len(rec["candidates"])
                cap = -(-quota[lv] // n_labels)
                if lab in labels_here or label_count[lab] >= cap:
                    continue
                labels_here.add(lab)
                label_count[lab] += 1
            have[lv].append(rec)
            took += 1
        if took:
            used_seeds.append(seed)
        seed += 1
    items = [rec for lv in quota for rec in have[lv]]
    return items, discards, used_seeds, (base, seed)


def build_items(smoke: bool = False, families=None,
                floor_table: dict | None = None) -> dict:
    """The item set. floor_table comes from compute_floor_table; without
    one, integer floors are one over the answer space alone."""
    quota = SMOKE_QUOTA if smoke else FULL_QUOTA
    offset = SMOKE_OFFSET if smoke else 0
    families = families or list(quota)
    out = {"items": [], "discards": {}, "seeds_used": {}, "seed_ranges": {}}
    for fam in families:
        base = SEED_BASE[fam] + offset
        if fam == "refuniverse":
            items, disc, used, rng_ = _fill(
                fam, quota[fam], base, None, {"int_answers": True},
                per_level=1, max_seeds=2000, floor_table=floor_table)
        elif fam == "algebra":
            items, disc, used, rng_ = _fill(
                fam, quota[fam], base, "src.mathgen.adapter", {},
                per_level=ALGEBRA_PER_LEVEL, max_seeds=2000,
                floor_table=floor_table)
        else:
            items, disc, used, rng_ = _fill(
                fam, quota[fam], base, "src.pilot.skills", {"family": fam},
                per_level=SKILL_CANDIDATES, max_seeds=2000,
                per_universe=SKILL_PER_UNIVERSE,
                balance_labels=fam != "binary_op", floor_table=floor_table)
        out["items"].extend(items)
        out["discards"][fam] = {k: dict(v) for k, v in disc.items()}
        out["seeds_used"][fam] = used
        out["seed_ranges"][fam] = rng_
    return out


def summarize(items: list[dict]) -> dict:
    cells: dict = defaultdict(lambda: {"n": 0, "floor_sum": 0.0,
                                       "closed_sum": 0.0})
    for it in items:
        key = f"{it['family']}|{it['level']}"
        cells[key]["n"] += 1
        cells[key]["floor_sum"] += it["floor"]
        cells[key]["closed_sum"] += it["floors"]["closed_book"]
    return {k: {"n": v["n"], "mean_floor": round(v["floor_sum"] / v["n"], 5),
                "mean_closed_book_floor": round(v["closed_sum"] / v["n"], 5)}
            for k, v in sorted(cells.items())}


def _git_head() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                   # noqa: BLE001
        return None


def write_items(path: str, built: dict, manifest_dir: str, smoke: bool,
                floor_table: dict | None = None) -> dict:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for it in built["items"]:
            fh.write(json.dumps(it, sort_keys=True) + "\n")
    os.replace(tmp, path)
    sha = file_sha(path)
    manifest = {
        "items_path": path,
        "items_sha256": sha,
        "smoke": smoke,
        "n_items": len(built["items"]),
        "cells": summarize(built["items"]),
        "discards": built["discards"],
        "seed_ranges_scanned": built["seed_ranges"],
        "universes_used": {k: len(v) for k, v in built["seeds_used"].items()},
        "seeds_used": built["seeds_used"],
        "manifest_dir": manifest_dir,
        "manifest_ranges": manifest_ranges(manifest_dir),
        "conditions": list(CONDITIONS),
        "floor_table": floor_table,
        "git_head": _git_head(),
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(path.replace(".jsonl", "") + ".manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=1)
    return manifest


def file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_items(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifests", required=True,
                    help="directory holding the runs/data-manifests json files")
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true",
                    help="the small smoke set, from seeds offset by 5,000,000")
    ap.add_argument("--families", default=None)
    ap.add_argument("--floor-table", required=True,
                    help="json file of pool floors; computed and written "
                         "there when it does not exist yet, read otherwise")
    args = ap.parse_args(argv)

    ranges = manifest_ranges(args.manifests)
    offset = SMOKE_OFFSET if args.smoke else 0
    planned = {f: (b + offset, b + offset + 2000) for f, b in SEED_BASE.items()}
    planned.update({f"floor_pool_{f}": (b, b + FLOOR_POOL_UNIVERSES[f])
                    for f, b in FLOOR_SEED_BASE.items()})
    clash = check_seed_ranges(planned, ranges)
    if clash:
        raise SystemExit("seed ranges overlap the training manifests:\n  "
                         + "\n  ".join(clash))
    t0 = time.time()
    if os.path.exists(args.floor_table):
        with open(args.floor_table) as fh:
            floor_table = json.load(fh)
    else:
        floor_table = compute_floor_table()
        os.makedirs(os.path.dirname(os.path.abspath(args.floor_table)),
                    exist_ok=True)
        with open(args.floor_table, "w") as fh:
            json.dump(floor_table, fh, indent=1, sort_keys=True)
        print(f"floor table computed in {time.time() - t0:.1f}s")
    fams = args.families.split(",") if args.families else None
    built = build_items(smoke=args.smoke, families=fams,
                        floor_table=floor_table)
    clash = check_seed_ranges({f: tuple(r) for f, r in built["seed_ranges"].items()},
                              ranges)
    if clash:
        raise SystemExit("seeds used overlap the training manifests:\n  "
                         + "\n  ".join(clash))
    man = write_items(args.out, built, args.manifests, args.smoke, floor_table)
    print(json.dumps({k: man[k] for k in ("n_items", "cells", "universes_used",
                                          "seed_ranges_scanned",
                                          "items_sha256")}, indent=1))
    print(json.dumps(man["discards"], indent=1))
    print(f"seconds {time.time() - t0:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
