"""The checks that have to hold before the corpus is worth generating.

    python -m src.corpus.selftest --tokenizer /home/ec2-user/data/tokenizer_v2.json

Runs on a small sample and prints counts. The full corpus is audited by
`python -m src.corpus.report`, which uses these same functions.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict

from src.corpus import audit, build, relations
from src.corpus.cli import DEPTH_SCHEDULE, HELDOUT_FAMILIES, TRAIN_FAMILIES

from src.corpus.frames import global_reserved, load_frames as _lf
from src.corpus.lexicon import collisions, reserved_words


def families_smoke(frames, encode, seed=300_000_001) -> dict:
    rng = random.Random(0)
    rows = []
    for fam in sorted(relations.STRUCTURES):
        f = frames[(abs(hash(fam)) % len(frames))]
        d = 3 if fam in relations.DEPTH_STRUCTURES else 1
        try:
            ep = build.build_relation_episode(seed, fam, f, encode, depth=d,
                                            global_reserved=GR)
            rep = build.audit_relation_episode(ep, f, rng)
            ok, why = build.keep_relation_episode(ep, rep)
            q = ep["questions"][0]
            rows.append({
                "family": fam, "frame": f.fid, "n_questions": len(ep["questions"]),
                "kept": ok, "why": why,
                "violations": sum(rep["violations"].values()),
                "answer_source": q["answer_source"],
                "plan_len": q["plan_len"], "n_distinct_ops": q["n_distinct_ops"],
                "n_pages": len(ep["documents"]),
                "question": q["text"],
                "answer": q["answer"],
            })
        except Exception as exc:  # noqa: BLE001
            rows.append({"family": fam, "error": f"{type(exc).__name__}: {exc}"})
    return {"rows": rows}


def cross_frame_agreement(frames, encode, families, n_frames=24, n_seeds=6,
                          seed0=300_000_100) -> dict:
    """The parity check: same seed, every frame, one gold answer.

    Frames are taken evenly across the bank so the sample spans every
    statement mode and every question form rather than one corner of it.
    """
    step = max(1, len(frames) // n_frames)
    picked = frames[::step][:n_frames]
    by_frame = defaultdict(list)
    for f in picked:
        for fam in families:
            depths = DEPTH_SCHEDULE.get(fam, (1,))
            for r in range(n_seeds):
                ep = build.build_relation_episode(
                    seed0 + r, fam, f, encode, depth=depths[r % len(depths)],
                    global_reserved=GR)
                by_frame[f.fid].append(ep)
    rep = audit.gold_agreement(by_frame)
    rep["frames_compared"] = [f.fid for f in picked]
    return rep


def parity(frames, encode, families, n_frames=24, n_seeds=6,
           seed0=300_000_100) -> dict:
    """Prompt and page token lengths per frame, computed per family.

    Parity is required across frames inside a family, not across families. Two
    families legitimately differ in how much page a question needs, and pooling
    them would hide the thing the check is for, which is a frame that runs
    systematically longer than its siblings on the same task.
    """
    step = max(1, len(frames) // n_frames)
    picked = frames[::step][:n_frames]
    out = {}
    for fam in families:
        depths = DEPTH_SCHEDULE.get(fam, (1,))
        per_frame = {}
        for f in picked:
            eps = [build.build_relation_episode(
                seed0 + r, fam, f, encode, depth=depths[r % len(depths)],
                global_reserved=GR) for r in range(n_seeds)]
            prompts, pages = [], []
            for ep in eps:
                pg = sum(len(encode(d["text"])) for d in ep["documents"])
                pages.append(pg)
                for q in ep["questions"]:
                    prompts.append(len(encode(q["text"])) + 8)
            prompts.sort()
            pages.sort()
            per_frame[f.fid] = {
                "n": len(prompts),
                "median": prompts[len(prompts) // 2],
                "prompt_max": prompts[-1],
                "prompt_over_384": sum(1 for x in prompts if x > 384),
                "page_median": pages[len(pages) // 2],
            }
        page_view = {k: {"n": v["n"], "median": v["page_median"]}
                     for k, v in per_frame.items()}
        out[fam] = {
            "prompt": audit.parity_report(per_frame),
            "page": audit.parity_report(page_view, tolerance=0.15),
            "page_median_spread": {
                "min": min(v["page_median"] for v in per_frame.values()),
                "max": max(v["page_median"] for v in per_frame.values()),
            },
            "prompt_over_384": sum(v["prompt_over_384"]
                                   for v in per_frame.values()),
        }
        out[fam]["prompt"].pop("per_frame_median", None)
        out[fam]["page"].pop("per_frame_median", None)
    return out


def per_frame_vocabulary(frames, encode, n_frames=32, seed=300_000_200) -> dict:
    """The vocabulary is drawn per frame, and no invented word is a frame's English."""
    step = max(1, len(frames) // n_frames)
    picked = frames[::step][:n_frames]
    bad = []
    draws = {}
    for f in picked:
        ep = build.build_relation_episode(seed, "substitution", f, encode,
                                          global_reserved=GR)
        rw = reserved_words(f)
        inv = set()
        for q in ep["questions"]:
            inv.add(q["answer"])
        c = collisions(rw, inv)
        if c:
            bad.append({"frame": f.fid, "collisions": c})
        draws[f.fid] = len(rw)
    sizes = sorted(draws.values())
    return {"frames_checked": len(picked), "n_collisions": len(bad),
            "reserved_size_min": sizes[0], "reserved_size_max": sizes[-1],
            "distinct_reserved_sets": len(set(
                frozenset(reserved_words(f)) for f in picked)),
            "examples": bad[:4], "passes": not bad}


def shortcut_floors(frames, encode, families, n_frames=8, n_seeds=120,
                    seed0=300_000_300) -> dict:
    """Every value blind reader against the chance floor, per family.

    Scored over independent items. The same seed rendered in eight frames is
    eight copies of one item as far as a value blind reader is concerned,
    because none of those readers looks at the wording; counting them eight
    times would shrink the interval eightfold and turn ordinary sampling noise
    into a finding. Items are therefore deduplicated by seed and question id
    before the interval is taken, and a reader is called above chance only when
    its Wilson lower bound clears the floor.
    """
    step = max(1, len(frames) // n_frames)
    picked = frames[::step][:n_frames]
    rng = random.Random(7)
    out = {}
    for fam in families:
        depths = DEPTH_SCHEDULE.get(fam, (1,))
        seen = {}
        chances = []
        for f in picked:
            for r in range(n_seeds):
                ep = build.build_relation_episode(
                    seed0 + r, fam, f, encode, depth=depths[r % len(depths)],
                    global_reserved=GR)
                rep = build.audit_relation_episode(ep, f, rng)
                # Value blind readers do not look at the wording, so one seed
                # is one item however many frames render it. The first frame
                # to produce a seed owns it.
                if ep["seed"] in seen:
                    continue
                seen[ep["seed"]] = rep["shortcuts"]
                for q in ep["questions"]:
                    if q["chance"]:
                        chances.append(q["chance"])
        n = sum(v["n_questions"] for v in seen.values())
        hits = Counter()
        for v in seen.values():
            for k, x in v["hits"].items():
                hits[k] += x
        chance = sum(chances) / len(chances) if chances else 0.0
        blind = {}
        worst = None
        for k in audit.BLIND_READERS:
            p, lo, hi = audit.wilson(hits.get(k, 0), n)
            blind[k] = {"rate": round(p, 4), "lo": round(lo, 4),
                        "hi": round(hi, 4), "above_chance": lo > chance}
            if worst is None or p > blind[worst]["rate"]:
                worst = k
        page = {}
        for k in audit.PAGE_READERS:
            p, lo, hi = audit.wilson(hits.get(k, 0), n)
            page[k] = round(p, 4)
        out[fam] = {
            "n_independent_seeds": len(seen),
            "n_questions": n,
            "chance": round(chance, 4),
            "blind_readers": blind,
            "worst_blind_reader": worst,
            "worst_blind_rate": blind[worst]["rate"] if worst else 0.0,
            "n_blind_readers_above_chance": sum(
                1 for v in blind.values() if v["above_chance"]),
            "blind_at_or_below_chance": not any(
                v["above_chance"] for v in blind.values()),
            "page_readers": page,
        }
    return out


def lookup_regex_check(frames) -> dict:
    """The shortcut reader's pattern must match its own frame's rule line.

    A frame whose pattern did not match would show a keyword reader at zero and
    look safe for a reason that has nothing to do with the frame, which is the
    mistake the audit exists to avoid.
    """
    import re

    from src.corpus.relations import Fact
    bad = []
    for f in frames:
        line = f.fact_line(Fact("assoc", "Scope", "kayvor", "milzel"))
        m = re.search(f.lookup_regex("kayvor"), line)
        if not m or m.group(1) != "milzel":
            bad.append({"frame": f.fid, "line": line,
                        "pattern": f.lookup_regex("kayvor")})
    return {"frames_checked": len(frames), "n_failing": len(bad),
            "examples": bad[:5], "passes": not bad}


def plan_axis(n=4) -> dict:
    """Long plans and wide symbol counts, and what the shipped parser does."""
    from src.corpus.plans import verify_roundtrip
    rng = random.Random(11)
    rows = []
    for ns in (1, 2, 3, 4, 8, 16, 32, 40, 48):
        for k in (1, 2, 3, 4, 5):
            if k > ns:
                continue
            ok = 0
            rt = None
            for r in range(n):
                res, why = build.build_plan_records(
                    350_000_000 + ns * 1000 + k * 100 + r, ns, k, "evaluate",
                    rng)
                if res is None:
                    continue
                ok += 1
                if rt is None:
                    w, _ = res
                    from src.opgraph.invent import make_world
                    from src.corpus.plans import numeric_ops
                    rt = verify_roundtrip(w["target"],
                                          numeric_ops(make_world(
                                              350_000_000 + ns * 1000 +
                                              k * 100 + r)))
            rows.append({"n_steps": ns, "n_symbols": k, "built": ok,
                         "tried": n,
                         "parses": rt["parses"] if rt else None,
                         "runs": rt["runs"] if rt else None})
    return {"rows": rows, "max_steps_in_shipped_parser": 32}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    from src.corpus.cli import _make_encode
    frames, source = _lf()
    globals()["GR"] = global_reserved(frames)
    encode, enc_kind = _make_encode(args.tokenizer)
    fams = list(TRAIN_FAMILIES)
    rep = {
        "frame_source": source,
        "n_frames": len(frames),
        "encoder": enc_kind,
        "train_families": list(TRAIN_FAMILIES),
        "heldout_families": list(HELDOUT_FAMILIES),
        "families_smoke": families_smoke(frames, encode),
        "per_frame_vocabulary": per_frame_vocabulary(frames, encode),
        "lookup_regex_check": lookup_regex_check(frames),
    }
    if not args.quick:
        rep["cross_frame_gold_agreement"] = cross_frame_agreement(
            frames, encode, fams)
        rep["token_parity"] = parity(frames, encode, fams)
        rep["shortcut_floors"] = shortcut_floors(frames, encode, fams)
        rep["plan_axis"] = plan_axis()
    text = json.dumps(rep, indent=1)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
        print(f"wrote {args.out} ({len(text)} bytes)")
        errs = [r for r in rep["families_smoke"]["rows"] if "error" in r]
        print("family errors:", len(errs))
        for e in errs[:6]:
            print("  ", e["family"], e["error"][:120])
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
