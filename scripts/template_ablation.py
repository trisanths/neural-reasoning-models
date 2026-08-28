"""Hold the task fixed and move only the wording.

`src/disc/SLATE.md` section 3 records a swing from at most 0.19 to 0.84 at
depth one between a fresh abstract notation and the routing idiom the RL stage
trained on, with presentation moving at the same time. This driver measures the
same swing with everything except the wording nailed down: same seeds, same
alphabet, same depth, same gold answers, same retrieval presentation, same page
count, same checkpoint, same grader.

Three commands.

  gen     write episode files for every renderer, both task groups
  audit   exclusions, shortcut baselines, page counts, prompt token lengths
  eval    roll the policy over the files, one model load for the whole sweep

Nothing here trains anything.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter

from src.disc.renderers import (CHAIN_RENDERERS, SIMPLE_FAMS,
                                SIMPLE_RENDERERS, chain_episode,
                                chain_violations, simple_episode)
from src.disc.minrepro import _mentions, hits_target


def _write(path: str, episodes: list[dict]) -> None:
    with open(path, "w") as fh:
        for ep in episodes:
            fh.write(json.dumps(ep) + "\n")


# ---------------------------------------------------------------- generation


def cmd_gen(args) -> int:
    os.makedirs(args.out, exist_ok=True)
    seeds = list(range(args.seed0, args.seed0 + args.episodes))
    depths = [int(d) for d in args.depths.split(",") if d]
    manifest = []

    for rname in args.chain_renderers.split(","):
        r = CHAIN_RENDERERS[rname]
        for d in depths:
            for mode in args.page_modes.split(","):
                eps = [chain_episode(s, d, r, n_problems=args.problems,
                                     alphabet_size=args.alphabet,
                                     max_depth=args.max_depth,
                                     pages_mode=mode) for s in seeds]
                tag = "" if mode == "minimal" else f"-{mode}"
                path = os.path.join(args.out, f"chain-{rname}-d{d}{tag}.jsonl")
                _write(path, eps)
                manifest.append({"group": "chain", "renderer": rname,
                                 "depth": d, "condition": mode, "path": path,
                                 "episodes": len(eps),
                                 "questions": sum(len(e["questions"])
                                                  for e in eps)})

    sseeds = list(range(args.simple_start, args.simple_start + args.simple_count))
    for rname in args.simple_renderers.split(","):
        r = SIMPLE_RENDERERS[rname]
        for cond in args.conditions.split(","):
            eps = []
            for s in sseeds:
                fam = SIMPLE_FAMS[s % len(SIMPLE_FAMS)]
                eps.append(simple_episode(s, fam, r,
                                          n_problems=args.simple_problems,
                                          pages=cond))
            path = os.path.join(args.out, f"simple-{rname}-{cond}.jsonl")
            _write(path, eps)
            manifest.append({"group": "simple", "renderer": rname,
                             "condition": cond, "path": path,
                             "episodes": len(eps),
                             "questions": sum(len(e["questions"]) for e in eps)})

    with open(os.path.join(args.out, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps({"files": len(manifest),
                      "chain_questions": sum(m["questions"] for m in manifest
                                             if m["group"] == "chain"),
                      "simple_questions": sum(m["questions"] for m in manifest
                                              if m["group"] == "simple")}))
    return 0


# -------------------------------------------------------------- gold parity


def cmd_parity(args) -> int:
    """The renderers must differ in wording and in nothing else.

    Two checks. The routing renderer must reproduce the published instrument
    byte for byte, so the reference arm is the published task and not a
    lookalike. Then every renderer must agree with every other on the gold
    answer, the starting token and the chain, question by question.
    """
    from src.disc import minrepro

    seeds = list(range(args.seed0, args.seed0 + args.episodes))
    depths = [int(d) for d in args.depths.split(",") if d]
    problems = args.problems
    bad = []

    for d in depths:
        for s in seeds:
            ref = minrepro.generate_episode(s, d, n_problems=problems,
                                            pages="minimal",
                                            alphabet_size=args.alphabet,
                                            max_depth=args.max_depth)
            mine = chain_episode(s, d, CHAIN_RENDERERS["routing"],
                                 n_problems=problems,
                                 alphabet_size=args.alphabet,
                                 max_depth=args.max_depth)
            if [q["text"] for q in ref["questions"]] != \
               [q["text"] for q in mine["questions"]]:
                bad.append(("routing_question_text", d, s))
            if [q["answer"] for q in ref["questions"]] != \
               [q["answer"] for q in mine["questions"]]:
                bad.append(("routing_answers", d, s))
            if [x["text"] for x in ref["documents"]] != \
               [x["text"] for x in mine["documents"]]:
                bad.append(("routing_pages", d, s))

    names = list(CHAIN_RENDERERS)
    for d in depths:
        for s in seeds:
            eps = {n: chain_episode(s, d, CHAIN_RENDERERS[n],
                                    n_problems=problems,
                                    alphabet_size=args.alphabet,
                                    max_depth=args.max_depth)
                   for n in names}
            base = eps[names[0]]
            key = [(q["qid"], q["answer"], q["start"], tuple(q["stages"]))
                   for q in base["questions"]]
            for n in names[1:]:
                other = [(q["qid"], q["answer"], q["start"], tuple(q["stages"]))
                         for q in eps[n]["questions"]]
                if other != key:
                    bad.append(("chain_gold_mismatch", n, d, s))
            texts = {n: tuple(q["text"] for q in eps[n]["questions"])
                     for n in names}
            if len(set(texts.values())) != len(names):
                bad.append(("chain_wording_not_distinct", d, s))

    sseeds = list(range(args.simple_start, args.simple_start + args.simple_count))
    snames = list(SIMPLE_RENDERERS)
    for s in sseeds:
        fam = SIMPLE_FAMS[s % len(SIMPLE_FAMS)]
        eps = {n: simple_episode(s, fam, SIMPLE_RENDERERS[n],
                                 n_problems=args.simple_problems)
               for n in snames}
        base = [(q["qid"], q["answer"]) for q in eps[snames[0]]["questions"]]
        for n in snames[1:]:
            other = [(q["qid"], q["answer"]) for q in eps[n]["questions"]]
            if other != base:
                bad.append(("simple_gold_mismatch", n, fam, s))
        texts = {n: tuple(q["text"] for q in eps[n]["questions"])
                 for n in snames}
        if len(set(texts.values())) != len(snames):
            bad.append(("simple_wording_not_distinct", fam, s))

    print(json.dumps({"mismatches": len(bad), "examples": bad[:10]}, indent=2))
    return 0 if not bad else 1


# -------------------------------------------------------------------- audit


def _page_token_stats(texts: list[str], tok) -> dict:
    lens = [len(tok.encode(t)) for t in texts]
    return {"n_pages": len(texts), "page_tokens_total": sum(lens),
            "page_tokens_mean": sum(lens) / max(1, len(lens))}


def _chain_audit(path: str, rname: str, tok) -> dict:
    from src.rl.env import build_prompt
    from src.train.retrieval import BM25Index

    r = CHAIN_RENDERERS[rname]
    viol = Counter()
    hits = Counter()
    n = 0
    prompt_lens: list[int] = []
    page_stats: list[dict] = []
    spreads: list[int] = []
    with open(path) as fh:
        for line in fh:
            ep = json.loads(line)
            for k, v in chain_violations(ep, r).items():
                viol[k] += v
            texts = [d["text"] for d in ep["documents"]]
            page_stats.append(_page_token_stats(texts, tok))
            blob = "\n".join(texts)
            alpha = ep["alphabet"]
            counts = {a: len(re.findall(rf"(?<![\w]){re.escape(a)}(?![\w])", blob))
                      for a in alpha}
            top = max(counts, key=lambda a: counts[a])
            present = [c for c in counts.values() if c]
            spreads.append(max(present) - min(present) if present else 0)
            index = BM25Index(texts, reliabilities=[1.0] * len(texts))
            for q in ep["questions"]:
                n += 1
                prompt_lens.append(len(build_prompt(ep, q, tok)))
                gold = q["answer"]
                if gold == top:
                    hits["most_frequent_token"] += 1
                try:
                    page = texts[index.top(q["text"], exclude=set())]
                except (ValueError, IndexError):
                    page = ""
                m = re.search(r.lookup(q["stages"][0]), page)
                if m and m.group(1) == gold:
                    hits["keyword_nearest"] += 1
                # A reader that scans every page rather than only the one BM25
                # ranks first. At depth one this is the answer by construction,
                # so it is the solvability check: the task must be exactly as
                # readable in one wording as in another.
                for t in texts:
                    mm = re.search(r.lookup(q["stages"][0]), t)
                    if mm and mm.group(1) == gold:
                        hits["row_reader_all_pages"] += 1
                        break
                if gold == q["stages"][0]:
                    hits["copy_start"] += 1
    npages = {p["n_pages"] for p in page_stats}
    return {
        "path": path, "renderer": rname, "n_questions": n,
        "violations": dict(viol),
        "baselines": {k: v / max(1, n) for k, v in hits.items()},
        "chance": 1.0 / 6.0,
        "max_token_frequency_spread": max(spreads) if spreads else 0,
        "page_counts": sorted(npages),
        "page_tokens_mean": sum(p["page_tokens_total"] for p in page_stats)
                            / max(1, len(page_stats)),
        "prompt_tokens_mean": sum(prompt_lens) / max(1, len(prompt_lens)),
        "prompt_tokens_max": max(prompt_lens) if prompt_lens else 0,
        "prompt_tokens_min": min(prompt_lens) if prompt_lens else 0,
    }


def _simple_audit(path: str, rname: str, tok) -> dict:
    from src.rl.env import build_prompt
    from src.train.retrieval import BM25Index

    viol = Counter()
    hits = Counter()
    n = 0
    chance_sum = 0.0
    prompt_lens: list[int] = []
    page_stats: list[dict] = []
    by_family: Counter = Counter()
    with open(path) as fh:
        for line in fh:
            ep = json.loads(line)
            texts = [d["text"] for d in ep["documents"]]
            page_stats.append(_page_token_stats(texts, tok))
            blob = "\n".join(texts)
            cands = ep["candidates"]
            counts = {c: len(re.findall(rf"(?<![\w]){re.escape(c)}(?![\w])", blob))
                      for c in cands}
            top = max(counts, key=lambda c: counts[c]) if counts else ""
            index = BM25Index(texts, reliabilities=[1.0] * len(texts)) if texts \
                else None
            for q in ep["questions"]:
                n += 1
                by_family[ep["family"]] += 1
                chance_sum += 1.0 / max(1, len(cands))
                prompt_lens.append(len(build_prompt(ep, q, tok)))
                gold = q["answer"]
                if _mentions(gold, q["text"]):
                    viol["answer_in_question"] += 1
                if gold == top:
                    hits["most_frequent_candidate"] += 1
                page = ""
                if index is not None:
                    try:
                        page = texts[index.top(q["text"], exclude=set())]
                    except (ValueError, IndexError):
                        page = ""
                pc = {c: len(re.findall(rf"(?<![\w]){re.escape(c)}(?![\w])", page))
                      for c in cands}
                near = max(pc, key=lambda c: pc[c]) if pc and max(pc.values()) else ""
                if near == gold:
                    hits["keyword_nearest"] += 1
    npages = {p["n_pages"] for p in page_stats}
    return {
        "path": path, "renderer": rname, "n_questions": n,
        "by_family": dict(by_family),
        "violations": dict(viol),
        "baselines": {k: v / max(1, n) for k, v in hits.items()},
        "chance": chance_sum / max(1, n),
        "page_counts": sorted(npages),
        "page_tokens_mean": sum(p["page_tokens_total"] for p in page_stats)
                            / max(1, len(page_stats)),
        "prompt_tokens_mean": sum(prompt_lens) / max(1, len(prompt_lens)),
        "prompt_tokens_max": max(prompt_lens) if prompt_lens else 0,
        "prompt_tokens_min": min(prompt_lens) if prompt_lens else 0,
    }


def cmd_audit(args) -> int:
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    with open(os.path.join(args.dir, "manifest.json")) as fh:
        manifest = json.load(fh)
    out = []
    for m in manifest:
        if m["group"] == "chain":
            rec = _chain_audit(m["path"], m["renderer"], tok)
            rec["depth"] = m["depth"]
        else:
            rec = _simple_audit(m["path"], m["renderer"], tok)
            rec["condition"] = m["condition"]
        rec["group"] = m["group"]
        rec["condition"] = m.get("condition", rec.get("condition"))
        out.append(rec)
        print(json.dumps({k: rec[k] for k in
                          ("group", "renderer", "n_questions", "violations",
                           "baselines", "page_counts", "prompt_tokens_mean",
                           "page_tokens_mean")}), flush=True)
    with open(os.path.join(args.dir, "audit.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    return 0


# --------------------------------------------------------------------- eval


def _classify_chain(answer: str, q: dict, alphabet: list[str]) -> str:
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


def _served(rounds: list[dict], gold: str) -> bool:
    for r in rounds:
        if re.search(rf"(?<![\w]){re.escape(gold)}(?![\w])", r.get("chunk", "")):
            return True
    return False


def evaluate(model, tok, device, path: str, group: str, samples: int,
             temperature: float, batch: int, env_cfg, max_len: int,
             max_prompt_tokens: int, questions_per_episode: int,
             seed: int, dump_path: str | None = None) -> dict:
    from src.rl.env import EpisodeEnv, load_tasks, rollout_stats
    from src.rl.sampler import CachedPolicy

    lookup: dict[tuple[int, str], dict] = {}
    alphabets: dict[int, list[str]] = {}
    meta: dict[int, dict] = {}
    with open(path) as fh:
        for i, line in enumerate(fh):
            ep = json.loads(line)
            alphabets[i] = ep.get("alphabet", ep.get("candidates", []))
            meta[i] = {"family": ep.get("family"), "n_pages": len(ep["documents"]),
                       "twin": ep.get("twin_candidates", [])}
            for q in ep["questions"]:
                lookup[(i, q["qid"])] = q

    env = EpisodeEnv(tok, env_cfg)
    tasks = load_tasks(path, tok, questions_per_episode=questions_per_episode,
                       min_hops=1, max_prompt_tokens=max_prompt_tokens,
                       limit_episodes=None, seed=0)
    if not tasks:
        raise SystemExit(f"no tasks survived load_tasks for {path}")
    wide = [t for t in tasks for _ in range(samples)]
    policy = CachedPolicy(model, device, max_len=max_len,
                          temperature=temperature, seed=seed)
    rolls = []
    for i in range(0, len(wide), batch):
        rolls.extend(env.rollout(policy, wide[i:i + batch]))

    per_question: dict[tuple[int, str], list[bool]] = {}
    kinds = Counter()
    fam_hits = Counter()
    fam_n = Counter()
    n_served = 0
    n_correct_served = 0
    n_correct = 0
    env_correct = 0
    traces = []
    dump_rows = []
    for r in rolls:
        key = (r.task.episode_index, r.task.qid)
        q = lookup[key]
        if group == "chain":
            cls = _classify_chain(r.answer_text, q,
                                  alphabets[r.task.episode_index])
            ok = cls == "correct"
        else:
            ok = env.is_correct(r.answer_text, r.task.gold)
            cls = "correct" if ok else "wrong"
        kinds[cls] += 1
        n_correct += int(ok)
        env_correct += int(r.correct)
        fam = meta[r.task.episode_index]["family"] or "chain"
        fam_n[fam] += 1
        fam_hits[fam] += int(r.correct if group != "chain" else ok)
        per_question.setdefault(key, []).append(ok)
        sv = _served(r.rounds, r.task.gold)
        n_served += int(sv)
        n_correct_served += int(sv and ok)
        if dump_path:
            dump_rows.append({
                "ep": r.task.episode_index, "qid": r.task.qid, "family": fam,
                "gold": r.task.gold, "answer": r.answer_text,
                "candidates": alphabets[r.task.episode_index],
                "stages": q.get("stages"),
                "twin_candidates": meta[r.task.episode_index]["twin"],
                "chunks": [x.get("chunk", "") for x in r.rounds],
                "served": sv, "shipped_ok": bool(ok), "class": cls,
            })
        if len(traces) < 8:
            traces.append({"question": r.task.question, "gold": r.task.gold,
                           "answer": r.answer_text, "class": cls,
                           "queries": [x["query"] for x in r.rounds],
                           "served": sv, "stop": r.stop_reason})
    stats = rollout_stats(rolls)
    if dump_path:
        with open(dump_path, "w") as fh:
            for row in dump_rows:
                fh.write(json.dumps(row) + "\n")
    n_q = len(per_question)
    return {
        "path": path, "group": group, "n_questions": n_q,
        "n_rollouts": len(rolls), "samples": samples,
        "temperature": temperature,
        "prompt_tokens_mean": sum(len(t.prompt) for t in tasks) / len(tasks),
        "accuracy": n_correct / max(1, len(rolls)),
        "accuracy_env_rule": env_correct / max(1, len(rolls)),
        "pass_at_k": sum(any(v) for v in per_question.values()) / max(1, n_q),
        "classes": {k: v / max(1, len(rolls)) for k, v in kinds.items()},
        "by_family": {f: fam_hits[f] / fam_n[f] for f in fam_n},
        "answering_page_served": n_served / max(1, len(rolls)),
        "accuracy_when_served": n_correct_served / max(1, n_served),
        "mean_rounds": stats["mean_rounds"],
        "any_retrieval": stats["any_retrieval"],
        "well_formed": stats["well_formed"],
        "stop_reasons": stats["stop_reasons"],
        "traces": traces,
    }


def cmd_eval(args) -> int:
    import torch

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
    want_group = args.group
    plan = [m for m in manifest if m["group"] == want_group]
    if args.filter:
        plan = [m for m in plan if args.filter in m["path"]]

    out = []
    for m in plan:
        dpath = None
        if args.dump_dir:
            os.makedirs(args.dump_dir, exist_ok=True)
            base = os.path.basename(m["path"])
            if base.endswith(".jsonl"):
                base = base[:-6]
            dpath = os.path.join(args.dump_dir, base + ".rolls.jsonl")
        res = evaluate(model, tok, device, m["path"], m["group"], args.samples,
                       args.temperature, args.batch, env_cfg, args.max_len,
                       args.max_prompt_tokens, args.questions_per_episode,
                       args.seed, dump_path=dpath)
        res["dump"] = dpath
        res["renderer"] = m["renderer"]
        res["depth"] = m.get("depth")
        res["condition"] = m.get("condition")
        out.append(res)
        slim = {k: v for k, v in res.items() if k != "traces"}
        print(json.dumps(slim), flush=True)
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=2)
    return 0


# ---------------------------------------------------------------------- cli


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("gen", "parity"):
        g = sub.add_parser(name)
        if name == "gen":
            g.add_argument("--out", required=True)
        g.add_argument("--depths", default="1,2")
        g.add_argument("--episodes", type=int, default=20)
        g.add_argument("--problems", type=int, default=8)
        g.add_argument("--seed0", type=int, default=1000)
        g.add_argument("--alphabet", type=int, default=6)
        g.add_argument("--max-depth", type=int, default=4)
        g.add_argument("--chain-renderers",
                       default=",".join(CHAIN_RENDERERS))
        g.add_argument("--simple-renderers",
                       default=",".join(SIMPLE_RENDERERS))
        g.add_argument("--conditions",
                       default="textbook,wrong_textbook,no_documents")
        g.add_argument("--page-modes", default="minimal")
        g.add_argument("--simple-start", type=int, default=2900000)
        g.add_argument("--simple-count", type=int, default=100)
        g.add_argument("--simple-problems", type=int, default=6)

    a = sub.add_parser("audit")
    a.add_argument("--dir", required=True)
    a.add_argument("--tokenizer", required=True)

    e = sub.add_parser("eval")
    e.add_argument("--dir", required=True)
    e.add_argument("--checkpoint", required=True)
    e.add_argument("--tokenizer", required=True)
    e.add_argument("--out", required=True)
    e.add_argument("--group", default="chain", choices=["chain", "simple"])
    e.add_argument("--filter", default="")
    e.add_argument("--samples", type=int, default=1)
    e.add_argument("--temperature", type=float, default=0.0)
    e.add_argument("--batch", type=int, default=32)
    e.add_argument("--max-len", type=int, default=1536)
    e.add_argument("--max-prompt-tokens", type=int, default=1100)
    e.add_argument("--max-rounds", type=int, default=6)
    e.add_argument("--max-new-tokens", type=int, default=96)
    e.add_argument("--questions-per-episode", type=int, default=10 ** 6)
    e.add_argument("--seed", type=int, default=99)
    e.add_argument("--dump-dir", default=None,
                   help="write one per-rollout jsonl per file here")

    args = ap.parse_args()
    if args.cmd == "gen":
        return cmd_gen(args)
    if args.cmd == "parity":
        return cmd_parity(args)
    if args.cmd == "audit":
        return cmd_audit(args)
    return cmd_eval(args)


if __name__ == "__main__":
    raise SystemExit(main())
