"""Driver for the frame generator. Nothing here trains anything.

  frames    list the frame space and the held-out split
  parity    gold agreement, native reproduction, vocabulary and candidate
            parity, per-frame answer-in-question violations
  distance  frame distances, split distributions, and the calibration run
            over the hand-written renderers whose accuracies are known
  gen       write episode files for a set of frames
  audit     token-length parity, using the project tokenizer
  parsers   the trivial-program baselines over generated episodes
  eval      roll the checkpoint over the generated files, one model load
  score     rescore the dumps under forced choice, with the canary
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
from collections import defaultdict

from src.disc.minrepro import _mentions
from src.disc.renderers import NativeSimple, simple_episode
from src.frames import distance as dist
from src.frames import score as sc
from src.frames.generate import (FAMILIES, FRAMES, LOAD_BEARING, NATIVE_FRAME,
                                 episodes_for, split_frames, write_episodes)
from src.frames.parsers import run_parsers
from src.skillacq.simple import SIMPLE_FAMILIES


def _seeds(args):
    return list(range(args.seed0, args.seed0 + args.episodes))


def _fams(args):
    return [f for f in args.families.split(",") if f]


def _frames(args) -> list[str]:
    if args.frames:
        return [f for f in args.frames.split(",") if f]
    return sorted(FRAMES)


# ---------------------------------------------------------------- frames


def cmd_frames(args) -> int:
    sp = split_frames(args.split, args.split_seed, args.test_lexicons,
                      args.test_shapes)
    out = {
        "n_frames": len(FRAMES),
        "n_lexicons": len({f.lexicon.name for f in FRAMES.values()}),
        "n_shapes": len({f.shape.name for f in FRAMES.values()}),
        "native_frame": NATIVE_FRAME,
        "split": {k: v for k, v in sp.items() if k not in ("train", "test",
                                                           "bridge")},
        "n_train": len(sp["train"]), "n_test": len(sp["test"]),
        "n_bridge": len(sp["bridge"]),
    }
    print(json.dumps(out, indent=2))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(sp, fh, indent=2)
        print(f"wrote {args.out}")
    return 0


# ---------------------------------------------------------------- parity


def cmd_parity(args) -> int:
    seeds = _seeds(args)
    fams = _fams(args)
    names = _frames(args)
    bad: list = []
    checks: dict = {}

    # 1. the grammar point (routing lexicon, native shape) must reproduce
    #    src/skillacq/simple.py word for word, through the published builder.
    nat = FRAMES[NATIVE_FRAME]
    ref = NativeSimple()
    n_native = 0
    for fam in fams:
        for s in seeds:
            a = simple_episode(s, fam, nat, n_problems=args.problems)
            b = simple_episode(s, fam, ref, n_problems=args.problems)
            n_native += 1
            if [d["text"] for d in a["documents"]] != \
               [d["text"] for d in b["documents"]]:
                bad.append(["native_pages_differ", fam, s])
            if [q["text"] for q in a["questions"]] != \
               [q["text"] for q in b["questions"]]:
                bad.append(["native_questions_differ", fam, s])
    checks["native_reproduction_episodes"] = n_native

    # 2. same seed, every frame: same gold answers, same candidate set size,
    #    same invented words on the page, distinct wording.
    n_cells = 0
    viol = defaultdict(int)
    cand_sizes = defaultdict(set)
    shared_q: list[int] = []
    for fam in fams:
        for s in seeds:
            eps = {n: simple_episode(s, fam, FRAMES[n],
                                     n_problems=args.problems) for n in names}
            base_name = names[0]
            base = [(q["qid"], q["answer"]) for q in eps[base_name]["questions"]]
            base_cands = sorted(eps[base_name]["candidates"])
            sysobj = SIMPLE_FAMILIES[fam](random.Random(s))
            nonce = sorted(dist.NONCE[fam](sysobj))
            base_seen = None
            texts = {}
            for n in names:
                ep = eps[n]
                n_cells += 1
                if [(q["qid"], q["answer"]) for q in ep["questions"]] != base:
                    bad.append(["gold_mismatch", n, fam, s])
                if sorted(ep["candidates"]) != base_cands:
                    bad.append(["candidate_set_mismatch", n, fam, s])
                cand_sizes[fam].add(len(ep["candidates"]))
                if len(ep["documents"]) != len(eps[base_name]["documents"]):
                    bad.append(["page_count_mismatch", n, fam, s])
                blob = "\n".join(d["text"] for d in ep["documents"]).lower()
                seen = tuple(w for w in nonce
                             if _mentions(w, blob))
                if base_seen is None:
                    base_seen = seen
                elif seen != base_seen:
                    bad.append(["nonce_words_on_page_differ", n, fam, s])
                for q in ep["questions"]:
                    if _mentions(q["answer"], q["text"]):
                        viol[f"{n}|{fam}|answer_in_question"] += 1
                texts[n] = (tuple(d["text"] for d in ep["documents"]),
                            tuple(q["text"] for q in ep["questions"]))
            if len(set(texts.values())) != len(names):
                dupes = defaultdict(list)
                for n, t in texts.items():
                    dupes[t].append(n)
                bad.append(["wording_not_distinct", fam, s,
                            [v for v in dupes.values() if len(v) > 1]])
            qonly = {t[1] for t in texts.values()}
            shared_q.append(len(names) - len(qonly))

    # 3. no invented word collides with any frame's English.
    english = set()
    for fr in FRAMES.values():
        for fam in FAMILIES:
            w = fr.lexicon.words(fam)
            english |= {str(v).lower() for v in w.__dict__.values()}
    collisions = []
    for fam in fams:
        for s in seeds:
            sysobj = SIMPLE_FAMILIES[fam](random.Random(s))
            for w in dist.NONCE[fam](sysobj):
                if w in english:
                    collisions.append([fam, s, w])
    checks["nonce_english_collisions"] = len(collisions)
    if collisions:
        bad.append(["nonce_english_collision", collisions[:5]])

    checks["frames"] = len(names)
    checks["families"] = fams
    checks["seeds"] = len(seeds)
    checks["frame_family_cells_checked"] = n_cells
    checks["candidate_set_sizes"] = {k: sorted(v) for k, v in cand_sizes.items()}
    checks["answer_in_question_violations"] = dict(viol)
    # Frames may pose the question identically and differ only on the rule
    # page. `postvalue` against `native` is the generated twin of the
    # published `routing_postvalue` arm, which keeps routing's question word
    # for word. Distinctness is required of the whole surface, not the
    # question alone, and the overlap is reported rather than hidden.
    checks["frames_sharing_a_question_wording_mean"] = (
        sum(shared_q) / max(1, len(shared_q)))
    checks["mismatches"] = len(bad)
    checks["examples"] = bad[:6]
    print(json.dumps({k: v for k, v in checks.items()
                      if k != "examples"}, indent=2)[:6000])
    if bad:
        print("first mismatches:", json.dumps(bad[:6])[:2000])
    if args.out:
        with open(args.out, "w") as fh:
            json.dump({"checks": checks, "all_mismatches": bad}, fh, indent=2)
        print(f"wrote {args.out}")
    return 0 if not bad else 1


# -------------------------------------------------------------- distance


def cmd_distance(args) -> int:
    names = _frames(args)
    report = {"family": args.family, "seed": args.dist_seed}

    if args.calibrate:
        sigs = dist.chain_signatures()
        anchor = "routing"
        d = dist.distances_to(sigs, anchor)
        report["calibration_chain_vs_routing"] = {
            k: {"shape": round(v["shape"], 3), "lex": round(v["lex"], 3)}
            for k, v in sorted(d.items(), key=lambda x: x[1]["shape"])}

    sigs = dist.frame_signatures(names, args.family, args.dist_seed)
    to_native = dist.distances_to(sigs, NATIVE_FRAME)
    report["n_frames"] = len(names)
    report["skeleton_len_native"] = len(sigs[NATIVE_FRAME]["skeleton"])
    report["to_native"] = {k: {"shape": round(v["shape"], 3),
                               "lex": round(v["lex"], 3)}
                           for k, v in sorted(to_native.items(),
                                              key=lambda x: x[1]["shape"])}

    pw = dist.pairwise(sigs)

    # How much of the shape axis is noise. Two frames of the same shape should
    # differ only in words, but a lexicon role can carry its own preposition
    # and prepositions survive delexicalisation, so the floor is not exactly
    # zero. Separation is the gap between that floor and the smallest genuine
    # shape difference.
    same_shape = [v["shape"] for (a, b), v in pw.items()
                  if FRAMES[a].shape.name == FRAMES[b].shape.name]
    diff_shape = [v["shape"] for (a, b), v in pw.items()
                  if FRAMES[a].shape.name != FRAMES[b].shape.name]
    same_lex = [v["lex"] for (a, b), v in pw.items()
                if FRAMES[a].lexicon.name == FRAMES[b].lexicon.name]
    diff_lex = [v["lex"] for (a, b), v in pw.items()
                if FRAMES[a].lexicon.name != FRAMES[b].lexicon.name]
    report["metric_separation"] = {
        "shape_noise_floor_max_same_shape": max(same_shape) if same_shape else 0,
        "shape_min_across_shapes": min(diff_shape) if diff_shape else 0,
        "lex_max_same_lexicon": max(same_lex) if same_lex else 0,
        "lex_min_across_lexicons": min(diff_lex) if diff_lex else 0,
    }

    sp = split_frames(args.split, args.split_seed, args.test_lexicons,
                      args.test_shapes)
    tr, te = set(sp["train"]), set(sp["test"])
    buckets = {"within_train": [], "within_test": [], "train_test": []}
    for (a, b), v in pw.items():
        if a in tr and b in tr:
            buckets["within_train"].append(v)
        elif a in te and b in te:
            buckets["within_test"].append(v)
        elif (a in tr and b in te) or (a in te and b in tr):
            buckets["train_test"].append(v)
    report["split"] = {k: v for k, v in sp.items()
                       if k not in ("train", "test", "bridge")}
    report["split_sizes"] = {"train": len(sp["train"]), "test": len(sp["test"]),
                             "bridge": len(sp["bridge"])}
    report["distance_distributions"] = {
        b: {comp: dist.describe_distribution([x[comp] for x in vals])
            for comp in ("shape", "lex", "mean")}
        for b, vals in buckets.items()}
    report["test_frames_to_native"] = {
        k: {"shape": round(to_native[k]["shape"], 3),
            "lex": round(to_native[k]["lex"], 3)}
        for k in sorted(sp["test"])}

    print(json.dumps({k: report[k] for k in report
                      if k not in ("to_native",)}, indent=2)[:9000])
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=2)
        print(f"wrote {args.out}")
    return 0


# ------------------------------------------------------------------- gen


def cmd_gen(args) -> int:
    m = write_episodes(args.out, _frames(args), _fams(args), _seeds(args),
                       [c for c in args.conditions.split(",") if c],
                       args.problems)
    print(json.dumps({"files": len(m),
                      "questions": sum(x["questions"] for x in m),
                      "dir": args.out}))
    return 0


# ----------------------------------------------------------------- audit


def cmd_audit(args) -> int:
    from src.rl.env import build_prompt
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    with open(os.path.join(args.dir, "manifest.json")) as fh:
        manifest = json.load(fh)
    out = []
    for m in manifest:
        page_tot, prompt_lens, npages, ncands = [], [], set(), set()
        with open(m["path"]) as fh:
            for line in fh:
                ep = json.loads(line)
                texts = [d["text"] for d in ep["documents"]]
                npages.add(len(texts))
                ncands.add(len(ep["candidates"]))
                page_tot.append(sum(len(tok.encode(t)) for t in texts))
                for q in ep["questions"]:
                    prompt_lens.append(len(build_prompt(ep, q, tok)))
        dropped = sum(1 for x in prompt_lens if x > args.max_prompt_tokens)
        out.append({
            "frame": m["frame"], "family": m["family"],
            "condition": m["condition"], "n_questions": len(prompt_lens),
            "page_counts": sorted(npages), "candidate_counts": sorted(ncands),
            "page_tokens_mean": sum(page_tot) / max(1, len(page_tot)),
            "page_tokens_max": max(page_tot) if page_tot else 0,
            "prompt_tokens_mean": sum(prompt_lens) / max(1, len(prompt_lens)),
            "prompt_tokens_max": max(prompt_lens) if prompt_lens else 0,
            "dropped_at_cap": dropped,
            "dropped_frac": dropped / max(1, len(prompt_lens)),
        })
    # parity is read against the native frame, family by family.
    base = {r["family"]: r for r in out if r["frame"] == NATIVE_FRAME}
    for r in out:
        b = base.get(r["family"])
        if b:
            r["page_tokens_ratio_to_native"] = (r["page_tokens_mean"]
                                                / max(1e-9,
                                                      b["page_tokens_mean"]))
            r["prompt_tokens_ratio_to_native"] = (r["prompt_tokens_mean"]
                                                  / max(1e-9,
                                                        b["prompt_tokens_mean"]))
    with open(os.path.join(args.dir, "audit.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("%-28s %-18s %6s %7s %7s %7s %7s %6s"
          % ("frame", "family", "n", "pgTok", "pgR", "prTok", "prR", "drop"))
    for r in sorted(out, key=lambda x: (x["family"], x["frame"])):
        print("%-28s %-18s %6d %7.1f %7.3f %7.1f %7.3f %6.3f"
              % (r["frame"], r["family"], r["n_questions"],
                 r["page_tokens_mean"], r.get("page_tokens_ratio_to_native", 0),
                 r["prompt_tokens_mean"],
                 r.get("prompt_tokens_ratio_to_native", 0),
                 r["dropped_frac"]))
    print(f"wrote {os.path.join(args.dir, 'audit.json')}")
    return 0


# --------------------------------------------------------------- parsers


def cmd_parsers(args) -> int:
    with open(os.path.join(args.dir, "manifest.json")) as fh:
        manifest = json.load(fh)
    rows_out = []
    print(sc.HEADER.replace("shipped", " parser"))
    for m in manifest:
        if m["family"] not in LOAD_BEARING:
            continue
        eps = [json.loads(l) for l in open(m["path"])]
        rows = run_parsers(eps, m["family"], m["frame"], args.problems)
        vocab = sc.nonce_vocab(rows)
        for which in ("frame_aware", "native_tuned"):
            s = sc.summarize(rows, vocab, answer_key=f"answer_{which}")
            rec = {"frame": m["frame"], "family": m["family"],
                   "condition": m["condition"], "parser": which, **s}
            rows_out.append(rec)
            print("%-28s %-18s %5d %8s %7.3f %7.3f %6.3f %6.3f %7.3f %7.3f"
                  % (m["frame"], m["family"] + "/" + which[:5], s["n"], "-",
                     s["acc_forced"], s["acc_first"], s["hedge_rate"],
                     s["none_rate"], s["chance_cand"], s["chance_page"]))
    with open(args.out, "w") as fh:
        json.dump(rows_out, fh, indent=2)
    print(f"wrote {args.out}")
    return 0


# ------------------------------------------------------------------ eval


def cmd_eval(args) -> int:
    import torch

    from scripts.template_ablation import evaluate
    from src.evals.mc import load_checkpoint_model
    from src.rl.env import EnvConfig
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint_model(args.checkpoint, device)
    model.eval()
    env_cfg = EnvConfig(max_rounds=args.max_rounds,
                        max_new_tokens=args.max_new_tokens,
                        max_len=args.max_len)
    with open(os.path.join(args.dir, "manifest.json")) as fh:
        manifest = json.load(fh)
    plan = [m for m in manifest if not args.filter or args.filter in m["path"]]
    os.makedirs(args.dump_dir, exist_ok=True)
    out = []
    for m in plan:
        base = os.path.basename(m["path"])[:-6]
        dpath = os.path.join(args.dump_dir, base + ".rolls.jsonl")
        res = evaluate(model, tok, device, m["path"], "simple", args.samples,
                       args.temperature, args.batch, env_cfg, args.max_len,
                       args.max_prompt_tokens, args.questions_per_episode,
                       args.seed, dump_path=dpath)
        res.pop("traces", None)
        res.update({"frame": m["frame"], "family": m["family"],
                    "condition": m["condition"], "dump": dpath})
        out.append(res)
        print(json.dumps({k: res[k] for k in
                          ("frame", "family", "condition", "n_questions",
                           "n_rollouts", "accuracy", "prompt_tokens_mean")}),
              flush=True)
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=2)
    return 0


# ----------------------------------------------------------------- score


def cmd_score(args) -> int:
    with open(os.path.join(args.dir, "manifest.json")) as fh:
        manifest = json.load(fh)
    by_base = {os.path.basename(m["path"])[:-6]: m for m in manifest}
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(args.dump_dir, "*.rolls.jsonl"))):
        base = os.path.basename(p)[: -len(".rolls.jsonl")]
        m = by_base.get(base)
        if m is None:
            raise SystemExit(f"dump {p} has no manifest entry")
        with open(p) as fh:
            for line in fh:
                cells[(m["frame"], m["family"], m["condition"])].append(
                    json.loads(line))
    if not cells:
        raise SystemExit("no dumps found")

    records = {}
    print(sc.HEADER)
    for key in sorted(cells):
        rows = cells[key]
        vocab = sc.nonce_vocab(rows)          # per frame and family, never pooled
        s = sc.summarize(rows, vocab)
        can = sc.summarize(sc.canary_rows(rows), vocab)
        s["canary_forced"] = can["acc_forced"]
        s["canary_hedge"] = can["hedge_rate"]
        s["nonce_vocab_size"] = len(vocab)
        if can["acc_forced"] != 0.0:
            raise SystemExit(f"HEDGING CANARY FAILED on {key}: "
                             f"forced={can['acc_forced']}")
        records["|".join(key)] = s
        print(sc.row_line(key[0], key[1], s))

    macro = {}
    for fam in sorted({k[1] for k in cells}):
        cellvals = [(records["|".join(k)]["acc_forced"],
                     records["|".join(k)]["chance_cand"])
                    for k in sorted(cells) if k[1] == fam]
        macro[fam] = sc.macro_both_orders(cellvals)
    out = {"records": records, "macro_by_family": macro,
           "note": "families are never pooled; macro is over frames within "
                   "one family"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("\nmacro over frames, within family, both aggregation orders:")
    for fam, mv in macro.items():
        print("  %-18s cells=%d macroAcc=%.3f macroChance=%.3f "
              "A=%.3f B=%.3f" % (fam, mv["cells"], mv["macro_accuracy"],
                                 mv["macro_chance"],
                                 mv["order_A_corrected_macro"],
                                 mv["order_B_mean_of_corrected"]))
    print(f"wrote {args.out}")
    return 0


# ------------------------------------------------------------------- cli


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, with_seeds=True):
        p.add_argument("--frames", default="")
        p.add_argument("--families", default=",".join(FAMILIES))
        p.add_argument("--problems", type=int, default=6)
        if with_seeds:
            p.add_argument("--seed0", type=int, default=2900000)
            p.add_argument("--episodes", type=int, default=100)

    def splitargs(p):
        p.add_argument("--split", default="both",
                       choices=["lexicon", "shape", "both"])
        p.add_argument("--split-seed", type=int, default=20260828)
        p.add_argument("--test-lexicons", type=int, default=4)
        p.add_argument("--test-shapes", type=int, default=4)

    f = sub.add_parser("frames")
    splitargs(f)
    f.add_argument("--out", default="")

    p = sub.add_parser("parity")
    common(p)
    p.add_argument("--out", default="")

    d = sub.add_parser("distance")
    common(d, with_seeds=False)
    splitargs(d)
    d.add_argument("--family", default="substitution_rule")
    d.add_argument("--dist-seed", type=int, default=4242)
    d.add_argument("--calibrate", action="store_true")
    d.add_argument("--out", default="")

    g = sub.add_parser("gen")
    common(g)
    g.add_argument("--out", required=True)
    g.add_argument("--conditions", default="textbook")

    a = sub.add_parser("audit")
    a.add_argument("--dir", required=True)
    a.add_argument("--tokenizer", required=True)
    a.add_argument("--max-prompt-tokens", type=int, default=384)

    pp = sub.add_parser("parsers")
    pp.add_argument("--dir", required=True)
    pp.add_argument("--out", required=True)
    pp.add_argument("--problems", type=int, default=6)

    e = sub.add_parser("eval")
    e.add_argument("--dir", required=True)
    e.add_argument("--checkpoint", required=True)
    e.add_argument("--tokenizer", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--dump-dir", required=True)
    e.add_argument("--filter", default="")
    e.add_argument("--samples", type=int, default=1)
    e.add_argument("--temperature", type=float, default=0.0)
    e.add_argument("--batch", type=int, default=32)
    e.add_argument("--max-len", type=int, default=640)
    e.add_argument("--max-prompt-tokens", type=int, default=384)
    e.add_argument("--max-rounds", type=int, default=4)
    e.add_argument("--max-new-tokens", type=int, default=96)
    e.add_argument("--questions-per-episode", type=int, default=2)
    e.add_argument("--seed", type=int, default=99)

    s = sub.add_parser("score")
    s.add_argument("--dir", required=True)
    s.add_argument("--dump-dir", required=True)
    s.add_argument("--out", required=True)

    args = ap.parse_args()
    return {"frames": cmd_frames, "parity": cmd_parity,
            "distance": cmd_distance, "gen": cmd_gen, "audit": cmd_audit,
            "parsers": cmd_parsers, "eval": cmd_eval,
            "score": cmd_score}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
