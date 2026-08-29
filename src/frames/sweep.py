"""The frame-diversity sweep: hold the examples fixed, vary the wordings.

Five arms start from one checkpoint and see the SAME rule systems, the SAME
seeds, the SAME number of examples, in the same order, for the same number of
optimizer steps at the same batch size. The only difference is how many
distinct sentence frames those examples are rendered in: 1, 3, 10, 30, and
every frame on the train side of the split.

Example i of a family is rendered in `order[i % n_frames]`, so an arm with 30
frames sees each frame a thirtieth as often as the 1-frame arm sees its one
frame. Total examples never move. The frame lists are nested, so the 30-frame
arm's wordings are a superset of the 10-frame arm's.

Why supervised traces and not RL. The base checkpoint was made with GRPO, but
GRPO drops a group whose rewards are all equal, and the distant frames are
exactly where the policy scores zero everywhere. Under RL the many-frame arms
would quietly train on fewer gradients than the one-frame arm, so "more
frames" would become "less training" and the comparison would be void.
Behaviour cloning of a correct trace gives every example the same weight in
every arm, which is the constant the experiment needs.

A trace is what the environment itself would have written for a competent
policy: <|retrieve|> the question text as the query, <|result|>, the chunk
BM25 actually returns for that query over that episode's own store, then
<|a|> the gold word <|eot|>. Loss falls only on the tokens the policy would
have emitted; the served chunk is masked out exactly as src/rl/grpo.py masks
it, so nothing here teaches the model to predict documents.

Commands:
  plan      arms, eval frames, and the frame distances each arm is read at
  data      build the shared example set and every arm's token traces
  train     one arm
  evalset   the episode files every arm is evaluated on
  report    the curve: accuracy against frame distance, per family, per arm
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from collections import defaultdict

from src.disc.renderers import SIMPLE_RENDERERS, simple_episode
from src.frames import distance as dist
from src.frames.generate import FRAMES, NATIVE_FRAME, split_frames

# threshold_rule is a grading artifact in this instrument (it hedges on
# essentially every greedy answer; see src/disc/TEMPLATE.md and
# src/frames/FRAMES.md), so it is neither trained on nor evaluated here.
TRAIN_FAMILIES = ("substitution_rule", "exception_rule")

TRAIN_SEED0 = 3_100_000        # disjoint from the eval pool by construction
EVAL_SEED0 = 2_900_000         # the smoke's pool, so the base numbers carry over
ARM_SIZES = (1, 3, 10, 30)     # the full train side is appended at runtime

# Positions in the nested frame order that get evaluated. Chosen before any
# number was seen, to put eval frames inside and outside each arm's list.
ORDER_PICKS = (0, 1, 2, 4, 6, 8, 12, 18, 24, 28, 35, 50, 65)
N_TEST_PICKS = 5
N_BRIDGE_PICKS = 2


# ------------------------------------------------------------------- plan


def frame_order(split_seed: int, order_seed: int) -> tuple[list[str], dict]:
    sp = split_frames("both", split_seed)
    rest = [f for f in sp["train"] if f != NATIVE_FRAME]
    random.Random(order_seed).shuffle(rest)
    return [NATIVE_FRAME] + rest, sp


def arm_sizes(order: list[str]) -> list[int]:
    return [n for n in ARM_SIZES if n < len(order)] + [len(order)]


def eval_frames(order: list[str], sp: dict) -> list[dict]:
    picks = []
    for i in ORDER_PICKS:
        if i < len(order):
            picks.append({"frame": order[i], "pool": "train", "order_index": i})
    test = sp["test"]
    step = max(1, len(test) // N_TEST_PICKS)
    for f in test[::step][:N_TEST_PICKS]:
        picks.append({"frame": f, "pool": "test", "order_index": -1})
    bridge = sp["bridge"]
    bstep = max(1, len(bridge) // N_BRIDGE_PICKS)
    for f in bridge[::bstep][:N_BRIDGE_PICKS]:
        picks.append({"frame": f, "pool": "bridge", "order_index": -1})
    seen = set()
    out = []
    for p in picks:
        if p["frame"] not in seen:
            seen.add(p["frame"])
            out.append(p)
    return out


def arm_distances(order: list[str], sizes: list[int], evals: list[dict],
                  family: str, dist_seed: int) -> dict:
    """For each arm and eval frame: the smallest distance to anything trained.

    Reported per family because the skeleton and the open-class words are
    read off that family's own rendered page.
    """
    names = sorted(set(order) | {e["frame"] for e in evals})
    sigs = dist.frame_signatures(names, family, dist_seed)
    out = {}
    for n in sizes:
        trained = order[:n]
        row = {}
        for e in evals:
            f = e["frame"]
            sd = min(dist.shape_distance(sigs[t]["skeleton"],
                                         sigs[f]["skeleton"]) for t in trained)
            ld = min(dist.lex_distance(set(sigs[t]["words"]),
                                       set(sigs[f]["words"])) for t in trained)
            row[f] = {"shape_min": round(sd, 4), "lex_min": round(ld, 4),
                      "seen": f in set(trained)}
        out[str(n)] = row
    return out


def cmd_plan(args) -> int:
    order, sp = frame_order(args.split_seed, args.order_seed)
    sizes = arm_sizes(order)
    evals = eval_frames(order, sp)
    plan = {
        "split": {k: v for k, v in sp.items()
                  if k not in ("train", "test", "bridge")},
        "split_sizes": {k: len(sp[k]) for k in ("train", "test", "bridge")},
        "order_seed": args.order_seed,
        "frame_order": order,
        "arm_sizes": sizes,
        "arms": {str(n): order[:n] for n in sizes},
        "eval_frames": evals,
        "handwritten": sorted(SIMPLE_RENDERERS),
        "train_families": list(TRAIN_FAMILIES),
        "train_seed0": TRAIN_SEED0, "eval_seed0": EVAL_SEED0,
        "distances": {fam: arm_distances(order, sizes, evals, fam,
                                         args.dist_seed)
                      for fam in TRAIN_FAMILIES},
    }
    with open(args.out, "w") as fh:
        json.dump(plan, fh, indent=2)
    print(json.dumps({"arm_sizes": sizes, "n_eval_frames": len(evals),
                      "split_sizes": plan["split_sizes"],
                      "eval_pools": {p: sum(1 for e in evals if e["pool"] == p)
                                     for p in ("train", "test", "bridge")}},
                     indent=2))
    print(f"wrote {args.out}")
    return 0


# ------------------------------------------------------------------- data


def _gold_in(chunk: str, gold: str) -> bool:
    import re
    return re.search(rf"(?<![A-Za-z]){re.escape(gold)}(?![A-Za-z])", chunk,
                     re.I) is not None


def build_trace(ep: dict, q: dict, tok, max_prompt_tokens: int,
                query_max_tokens: int, max_rounds: int, max_len: int,
                require_served: bool = True):
    """The trace the environment would have written for a correct rollout."""
    from src.rl.env import build_prompt, make_service

    sid = tok.special_ids
    prompt = build_prompt(ep, q, tok)
    if len(prompt) > max_prompt_tokens:
        return None
    service = make_service(ep["documents"])
    qtoks = tok.encode(q["text"])[:query_max_tokens]
    query_text = tok.decode(qtoks)
    tokens, mask, amask = list(prompt), [0] * len(prompt), [0] * len(prompt)
    served = False
    rounds = 0
    for _ in range(max_rounds):
        hit = service.top(query_text)
        if hit is None:
            break
        rounds += 1
        _, chunk = hit
        ct = tok.encode(chunk)
        tokens.append(sid["<|retrieve|>"]); mask.append(1); amask.append(0)
        tokens.extend(qtoks); mask.extend([1] * len(qtoks))
        amask.extend([0] * len(qtoks))
        tokens.append(sid["<|result|>"]); mask.append(1); amask.append(0)
        tokens.extend(ct); mask.extend([0] * len(ct))
        amask.extend([0] * len(ct))
        if _gold_in(chunk, q["answer"]):
            served = True
            break
    if require_served and not served:
        # A trace that never surfaced the answering page teaches the model to
        # produce the gold word without evidence. BM25 surfaces it on every
        # native-frame question and on about three quarters elsewhere, so
        # keeping those would hand the one-frame arm clean demonstrations and
        # the many-frame arms a quarter of guesswork. They are dropped, and
        # the arms are then intersected, so every arm demonstrates the same
        # questions with the page in context.
        return None
    at = tok.encode(" " + q["answer"])
    tokens.append(sid["<|a|>"]); mask.append(1); amask.append(1)
    tokens.extend(at); mask.extend([1] * len(at)); amask.extend([1] * len(at))
    tokens.append(sid["<|eot|>"]); mask.append(1); amask.append(1)
    if len(tokens) > max_len:
        return None
    return {"tokens": tokens, "mask": mask, "amask": amask, "served": served,
            "rounds": rounds}


def arm_examples(order: list[str], n_frames: int, seeds: list[int],
                 problems: int, questions_per_episode: int, tok, args):
    """Every example this arm would train on, keyed by content not wording."""
    out = {}
    stats = defaultdict(int)
    for k in ("built", "dropped_length", "dropped_unserved", "served"):
        stats[k] = 0
    for fam in TRAIN_FAMILIES:
        for i, seed in enumerate(seeds):
            fname = order[i % n_frames]
            ep = simple_episode(seed, fam, FRAMES[fname], n_problems=problems)
            for q in ep["questions"][:questions_per_episode]:
                key = f"{fam}|{seed}|{q['qid']}"
                stats["built"] += 1
                raw = build_trace(ep, q, tok, args.max_prompt_tokens,
                                  args.query_max_tokens, args.max_rounds,
                                  args.max_len, require_served=False)
                if raw is None:
                    stats["dropped_length"] += 1
                    continue
                if args.require_served and not raw["served"]:
                    stats["dropped_unserved"] += 1
                    continue
                tr = raw
                stats["served"] += int(tr["served"])
                tr["frame"] = fname
                tr["family"] = fam
                out[key] = tr
    return out, dict(stats)


def cmd_data(args) -> int:
    from src.train.tokenizer import load_tokenizer

    with open(args.plan) as fh:
        plan = json.load(fh)
    order = plan["frame_order"]
    sizes = plan["arm_sizes"]
    tok = load_tokenizer(args.tokenizer)
    seeds = list(range(TRAIN_SEED0, TRAIN_SEED0 + args.episodes))

    per_arm, per_stats = {}, {}
    for n in sizes:
        t0 = time.time()
        ex, st = arm_examples(order, n, seeds, args.problems,
                              args.questions_per_episode, tok, args)
        per_arm[n], per_stats[n] = ex, st
        print(f"arm {n:3d}: {len(ex)} kept of {st['built']}, "
              f"len-drop {st['dropped_length']}, "
              f"unserved-drop {st['dropped_unserved']}, "
              f"{time.time() - t0:.0f}s", flush=True)

    # The shared set: an example only trains if every arm could build it.
    # Without this an arm whose frames run long would silently train on fewer
    # examples than the others, and "more frames" would become "less data".
    keep = set(per_arm[sizes[0]])
    for n in sizes[1:]:
        keep &= set(per_arm[n])
    keep = sorted(keep)
    rng = random.Random(args.shuffle_seed)
    rng.shuffle(keep)
    print(f"shared example set: {len(keep)}")

    os.makedirs(args.out, exist_ok=True)
    meta = {"n_examples": len(keep), "arm_sizes": sizes,
            "episodes_per_family": args.episodes,
            "questions_per_episode": args.questions_per_episode,
            "families": list(TRAIN_FAMILIES), "seed0": TRAIN_SEED0,
            "shuffle_seed": args.shuffle_seed,
            "per_arm_before_intersection": {str(n): len(per_arm[n])
                                            for n in sizes},
            "per_arm_stats": {str(n): per_stats[n] for n in sizes},
            "order": keep}
    for n in sizes:
        path = os.path.join(args.out, f"arm{n:03d}.jsonl")
        served = 0
        with open(path, "w") as fh:
            for k in keep:
                tr = per_arm[n][k]
                served += int(tr["served"])
                fh.write(json.dumps({"key": k, **tr}) + "\n")
        meta.setdefault("arm_files", {})[str(n)] = {
            "path": path, "n": len(keep), "served_rate": served / len(keep),
            "frames_used": len(sorted({per_arm[n][k]["frame"] for k in keep})),
            "tokens": sum(len(per_arm[n][k]["tokens"]) for k in keep),
            "supervised_tokens": sum(sum(per_arm[n][k]["mask"]) for k in keep),
            "answer_tokens": sum(sum(per_arm[n][k]["amask"]) for k in keep),
            "query_tokens": sum(sum(per_arm[n][k]["mask"])
                                - sum(per_arm[n][k]["amask"]) for k in keep),
        }
        print(json.dumps({"arm": n, **meta["arm_files"][str(n)]}))
    with open(os.path.join(args.out, "data.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"wrote {os.path.join(args.out, 'data.json')}")
    return 0


# ------------------------------------------------------------------ train


def cmd_train(args) -> int:
    import torch
    import torch.nn.functional as F

    from src.evals.mc import load_checkpoint_model

    torch.manual_seed(args.seed)
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    model, state = load_checkpoint_model(args.checkpoint, device)
    model_config = state["config"]
    model.train()

    rows = [json.loads(l) for l in open(args.data)]
    n = len(rows)
    steps_per_epoch = n // args.batch
    total_steps = steps_per_epoch * args.epochs
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95),
                            weight_decay=args.weight_decay, eps=1e-8)
    print(f"{n} examples, batch {args.batch}, {steps_per_epoch} steps/epoch, "
          f"{args.epochs} epochs, {total_steps} steps, lr {args.lr}",
          flush=True)

    log = open(args.log, "a")
    step = 0
    started = time.time()
    for epoch in range(args.epochs):
        for b in range(steps_per_epoch):
            chunk = rows[b * args.batch:(b + 1) * args.batch]
            width = max(len(r["tokens"]) for r in chunk)
            toks = torch.zeros(len(chunk), width, dtype=torch.long)
            msk = torch.zeros(len(chunk), width, dtype=torch.float)
            amk = torch.zeros(len(chunk), width, dtype=torch.float)
            for i, r in enumerate(chunk):
                t = r["tokens"]
                toks[i, :len(t)] = torch.tensor(t, dtype=torch.long)
                msk[i, :len(t)] = torch.tensor(r["mask"], dtype=torch.float)
                amk[i, :len(t)] = torch.tensor(r["amask"], dtype=torch.float)
            toks, msk, amk = toks.to(device), msk.to(device), amk.to(device)
            x, y, m = toks[:, :-1], toks[:, 1:], msk[:, 1:]
            am = amk[:, 1:]
            qm = (m - am).clamp(min=0.0)
            warm = min(1.0, (step + 1) / max(1, args.warmup))
            frac = step / max(1, total_steps)
            lr = args.lr * warm * (args.min_lr_ratio + (1 - args.min_lr_ratio)
                                   * 0.5 * (1 + math.cos(math.pi * frac)))
            for g in opt.param_groups:
                g["lr"] = lr
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits, _ = model(x)
            ce = F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]),
                                 y.reshape(-1), reduction="none")
            # Two terms, each normalized by its own token count. The answer
            # segment is the same gold word in every arm, so the answer term
            # carries exactly the same weight in every arm; the query segment
            # is the question in that arm's wording and tokenizes to different
            # lengths, which a single pooled denominator would let bleed into
            # how hard the answer is trained.
            denom = am.sum().clamp(min=1.0)
            qdenom = qm.sum().clamp(min=1.0)
            loss_a = (ce * am.reshape(-1)).sum() / denom
            loss_q = (ce * qm.reshape(-1)).sum() / qdenom
            loss = loss_a + args.query_weight * loss_q
            opt.zero_grad(set_to_none=True)
            loss.backward()
            gn = torch.nn.utils.clip_grad_norm_(model.parameters(),
                                                args.grad_clip)
            opt.step()
            step += 1
            if step % args.log_every == 0 or step == total_steps:
                rec = {"step": step, "epoch": epoch, "loss": float(loss),
                       "loss_answer": float(loss_a), "loss_query": float(loss_q),
                       "lr": lr, "grad_norm": float(gn),
                       "answer_tokens": int(denom), "query_tokens": int(qdenom),
                       "elapsed_s": round(time.time() - started, 1)}
                log.write(json.dumps(rec) + "\n")
                log.flush()
                print(json.dumps(rec), flush=True)
    save = {"model": model.state_dict(), "config": model_config,
            "step": step, "sft": {"data": args.data, "epochs": args.epochs,
                                  "batch": args.batch, "lr": args.lr,
                                  "n_examples": n, "seed": args.seed}}
    tmp = args.out + ".tmp"
    torch.save(save, tmp)
    os.replace(tmp, args.out)
    print(f"wrote {args.out} after {step} steps, "
          f"{(time.time() - started) / 60:.1f} min")
    return 0


# ---------------------------------------------------------------- evalset


def _write_dir(out_dir: str, renderers: dict, families, seeds, problems,
               condition: str) -> list[dict]:
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for name, r in renderers.items():
        for fam in families:
            eps = []
            for s in seeds:
                ep = simple_episode(s, fam, r, n_problems=problems,
                                    pages=condition)
                ep["frame"] = name
                eps.append(ep)
            path = os.path.join(out_dir, f"frames-{name}-{fam}-{condition}"
                                         ".jsonl")
            with open(path, "w") as fh:
                for ep in eps:
                    fh.write(json.dumps(ep) + "\n")
            manifest.append({"group": "simple", "renderer": name,
                             "frame": name, "family": fam,
                             "condition": condition, "path": path,
                             "episodes": len(eps),
                             "questions": sum(len(e["questions"])
                                              for e in eps),
                             "candidates": len(eps[0]["candidates"])})
    with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def cmd_evalset(args) -> int:
    with open(args.plan) as fh:
        plan = json.load(fh)
    seeds = list(range(EVAL_SEED0, EVAL_SEED0 + args.episodes))
    gen = {e["frame"]: FRAMES[e["frame"]] for e in plan["eval_frames"]}
    m1 = _write_dir(os.path.join(args.out, "gen"), gen, TRAIN_FAMILIES, seeds,
                    args.problems, args.condition)
    m2 = _write_dir(os.path.join(args.out, "hand"), SIMPLE_RENDERERS,
                    TRAIN_FAMILIES, seeds, args.problems, args.condition)
    print(json.dumps({"gen_cells": len(m1), "hand_cells": len(m2),
                      "questions_per_cell": m1[0]["questions"],
                      "dir": args.out}))
    return 0


# ----------------------------------------------------------------- report


BINS = ((0.001, "0.00 identical"), (0.10, "0.00-0.10"), (0.25, "0.10-0.25"),
        (0.40, "0.25-0.40"), (0.55, "0.40-0.55"), (9.9, "0.55+"))


def _bin(d: float) -> str:
    for hi, name in BINS:
        if d <= hi:
            return name
    return BINS[-1][1]


def _arm_key(label: str) -> str:
    """Which arm's training frames a label is read against.

    `base` is the RL checkpoint the arms start from. Its own RL run was on
    src/skillacq's native wording only, so its trained-frame set is the same
    single frame as arm 1 and it is read at arm 1's distances.
    """
    if label == "base":
        return "1"
    return str(int(label.replace("arm", "")))


def hand_distances(plan: dict, family: str, dist_seed: int) -> dict:
    """The same metric applied to the hand-written renderers, per arm."""
    order = plan["frame_order"]
    sigs = dist.frame_signatures(order, family, dist_seed)
    for name, r in SIMPLE_RENDERERS.items():
        sigs[name] = dist.signature(r, family, dist_seed)
    out = {}
    for n in plan["arm_sizes"]:
        trained = order[:n]
        out[str(n)] = {
            name: {
                "shape_min": round(min(dist.shape_distance(
                    sigs[t]["skeleton"], sigs[name]["skeleton"])
                    for t in trained), 4),
                "lex_min": round(min(dist.lex_distance(
                    set(sigs[t]["words"]), set(sigs[name]["words"]))
                    for t in trained), 4),
                # `native` is the hand-written renderer the generator's native
                # frame reproduces word for word, so it counts as seen.
                "seen": name == "native",
            }
            for name in SIMPLE_RENDERERS}
    return out


def _weighted(sel, key):
    tot = sum(r["n"] for r in sel)
    return sum(r[key] * r["n"] for r in sel) / tot if tot else float("nan")


def _group(sel, sc):
    cells = [(r["acc_forced"], r["chance_cand"]) for r in sel]
    return {**sc.macro_both_orders(cells), "frames": len(sel),
            "n_questions": sum(r["n"] for r in sel),
            "acc_first": _weighted(sel, "acc_first"),
            "hedge_rate": _weighted(sel, "hedge_rate"),
            "none_rate": _weighted(sel, "none_rate"),
            "served_rate": _weighted(sel, "served_rate"),
            "shape_min_mean": _weighted(sel, "shape_min"),
            "lex_min_mean": _weighted(sel, "lex_min")}


def cmd_report(args) -> int:
    import glob as _glob

    from src.frames import score as sc

    with open(args.plan) as fh:
        plan = json.load(fh)
    hand = {fam: hand_distances(plan, fam, args.dist_seed)
            for fam in TRAIN_FAMILIES}
    pool = {e["frame"]: e["pool"] for e in plan["eval_frames"]}
    rows = []
    sources = {}
    for path in sorted(_glob.glob(os.path.join(args.res, "score_*.json"))):
        stem = os.path.basename(path)[len("score_"):-len(".json")]
        label, kind, temp = stem.split("-")
        with open(path) as fh:
            blob = json.load(fh)
        sources[stem] = {"path": path,
                         "mtime": os.path.getmtime(path),
                         "cells": len(blob["records"])}
        table = plan["distances"] if kind == "gen" else hand
        for key, s in blob["records"].items():
            frame, family, cond = key.split("|")
            d = table.get(family, {}).get(_arm_key(label), {}).get(frame)
            if d is None:
                raise SystemExit(f"no distance for {label} {family} {frame}")
            if s.get("canary_forced") not in (0.0, None):
                raise SystemExit(f"canary above zero in {path} on {key}")
            rows.append({
                "label": label, "arm_key": _arm_key(label), "set": kind,
                "decode": temp, "frame": frame, "family": family,
                "pool": pool.get(frame, "handwritten"),
                "condition": cond, "n": s["n"], "seen": bool(d["seen"]),
                "shape_min": d["shape_min"], "lex_min": d["lex_min"],
                "acc_forced": s["acc_forced"], "acc_first": s["acc_first"],
                "acc_shipped": s["acc_shipped"],
                "hedge_rate": s["hedge_rate"], "none_rate": s["none_rate"],
                "chance_cand": s["chance_cand"],
                "chance_page": s["chance_page"],
                "served_rate": s["served_rate"],
                "acc_forced_when_served": s["acc_forced_when_served"],
                "canary_forced": s.get("canary_forced"),
                "n_candidates_mean": s["n_candidates_mean"]})
    if not rows:
        raise SystemExit(f"no score files under {args.res}")

    labels = sorted({r["label"] for r in rows},
                    key=lambda x: (x != "base", x))
    fams = sorted({r["family"] for r in rows})
    decodes = sorted({r["decode"] for r in rows})

    agg = {}
    for lb in labels:
        for dc in decodes:
            for fam in fams:
                for grp in ("seen", "held_out"):
                    sel = [r for r in rows if r["label"] == lb
                           and r["decode"] == dc and r["family"] == fam
                           and r["set"] == "gen"
                           and (r["seen"] if grp == "seen" else not r["seen"])]
                    if sel:
                        agg[f"{lb}|{dc}|{fam}|{grp}"] = _group(sel, sc)

    # The strictest comparison the design allows: the seven frames on the
    # test and bridge sides that NO arm ever trained on, the same episodes
    # for every arm, so only the training frame count differs.
    fixed = {}
    for lb in labels:
        for dc in decodes:
            for fam in fams:
                sel = [r for r in rows if r["label"] == lb
                       and r["decode"] == dc and r["family"] == fam
                       and r["set"] == "gen"
                       and r["pool"] in ("test", "bridge")]
                if sel:
                    fixed[f"{lb}|{dc}|{fam}"] = _group(sel, sc)

    curve = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["set"] == "gen":
            curve[f"{r['label']}|{r['decode']}|{r['family']}"][
                _bin(r["shape_min"])].append(r)
    curve_out = {k: {b: _group(v, sc) for b, v in
                     sorted(bins.items(),
                            key=lambda x: [n for _, n in BINS].index(x[0]))}
                 for k, bins in sorted(curve.items())}

    handrows = {}
    for r in rows:
        if r["set"] == "hand":
            handrows[f"{r['label']}|{r['decode']}|{r['family']}|"
                     f"{r['frame']}"] = r

    out = {"cells": rows, "seen_vs_heldout": agg,
           "never_trained_frames": fixed, "curve": curve_out,
           "handwritten": handrows, "sources": sources,
           "note": "families are never pooled; every macro is over frames "
                   "inside one family, both aggregation orders reported"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)

    print("seen versus held out, generated frames, forced choice\n")
    print("%-7s %-7s %-18s %-9s %5s %6s %7s %7s %7s %7s %7s %7s"
          % ("arm", "decode", "family", "group", "frms", "n", "forced",
             "first", "chance", "corrA", "none", "served"))
    for k in sorted(agg, key=lambda x: (x.split("|")[2], x.split("|")[1],
                                        labels.index(x.split("|")[0]),
                                        x.split("|")[3])):
        lb, dc, fam, grp = k.split("|")
        a = agg[k]
        print("%-7s %-7s %-18s %-9s %5d %6d %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f"
              % (lb, dc, fam, grp, a["frames"], a["n_questions"],
                 a["macro_accuracy"], a["acc_first"], a["macro_chance"],
                 a["order_A_corrected_macro"], a["none_rate"],
                 a["served_rate"]))
    print("\nthe seven frames no arm ever trained on, same episodes "
          "for every arm\n")
    print("%-7s %-7s %-18s %5s %6s %7s %7s %7s %7s %7s %7s"
          % ("arm", "decode", "family", "frms", "n", "forced", "first",
             "chance", "corrA", "none", "served"))
    for k in sorted(fixed, key=lambda x: (x.split("|")[2], x.split("|")[1],
                                          labels.index(x.split("|")[0]))):
        lb, dc, fam = k.split("|")
        a = fixed[k]
        print("%-7s %-7s %-18s %5d %6d %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f"
              % (lb, dc, fam, a["frames"], a["n_questions"],
                 a["macro_accuracy"], a["acc_first"], a["macro_chance"],
                 a["order_A_corrected_macro"], a["none_rate"],
                 a["served_rate"]))
    print(f"\nwrote {args.out}")
    return 0


# -------------------------------------------------------------------- cli


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan")
    p.add_argument("--split-seed", type=int, default=20260828)
    p.add_argument("--order-seed", type=int, default=770001)
    p.add_argument("--dist-seed", type=int, default=4242)
    p.add_argument("--out", required=True)

    d = sub.add_parser("data")
    d.add_argument("--plan", required=True)
    d.add_argument("--tokenizer", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--episodes", type=int, default=2000)
    d.add_argument("--problems", type=int, default=6)
    d.add_argument("--questions-per-episode", type=int, default=2)
    d.add_argument("--max-prompt-tokens", type=int, default=384)
    d.add_argument("--query-max-tokens", type=int, default=24)
    d.add_argument("--max-rounds", type=int, default=3)
    d.add_argument("--max-len", type=int, default=800)
    d.add_argument("--shuffle-seed", type=int, default=4113)
    d.add_argument("--require-served", type=int, default=1)

    t = sub.add_parser("train")
    t.add_argument("--checkpoint", required=True)
    t.add_argument("--data", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--log", required=True)
    t.add_argument("--epochs", type=int, default=3)
    t.add_argument("--batch", type=int, default=16)
    t.add_argument("--lr", type=float, default=1.0e-5)
    t.add_argument("--min-lr-ratio", type=float, default=0.1)
    t.add_argument("--warmup", type=int, default=40)
    t.add_argument("--weight-decay", type=float, default=0.0)
    t.add_argument("--grad-clip", type=float, default=1.0)
    t.add_argument("--query-weight", type=float, default=1.0)
    t.add_argument("--log-every", type=int, default=25)
    t.add_argument("--seed", type=int, default=7701)
    t.add_argument("--device", default=None)

    e = sub.add_parser("evalset")
    e.add_argument("--plan", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--episodes", type=int, default=100)
    e.add_argument("--problems", type=int, default=6)
    e.add_argument("--condition", default="textbook")

    r = sub.add_parser("report")
    r.add_argument("--plan", required=True)
    r.add_argument("--res", required=True,
                   help="directory holding score_LABEL-SET-DECODE.json")
    r.add_argument("--dist-seed", type=int, default=4242)
    r.add_argument("--out", required=True)

    args = ap.parse_args()
    return {"plan": cmd_plan, "data": cmd_data, "train": cmd_train,
            "evalset": cmd_evalset, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
