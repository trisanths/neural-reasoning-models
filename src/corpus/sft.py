"""Supervised fine tuning over the diversity corpus.

Three commands.

  build   turns one corpus component into the trace the episode environment
          writes for a correct rollout, packed as three flat arrays plus a
          line per example.
  merge   concatenates component packs into one pack, shuffled.
  train   one supervised pass over a pack from a checkpoint.

The trace shape is the one `src/frames/sweep.py:build_trace` writes, which is
the one `src/rl/env.py` replays at evaluation time: the world header prompt
from `src/rl/env.py:build_prompt`, then a retrieve marker, a query, a result
marker and a served page for each round, then the answer and the end marker.
Served page tokens carry no loss; the markers, the query and the answer do.
Training any other shape would teach a policy a trace the environment cannot
walk, and the checkpoint answers nothing at all without the world header.

The query is the tail of the question, not its head. Corpus questions carry a
variable length lead in whose only job is to hold prompt token counts equal
across frames, so the head of a question is padding in some frames and content
in others. A query policy reading the head would vary in quality with the
frame, which is the axis being measured.

The plan component is already written as prompt and target strings with the
markers inside them, so it is encoded directly with the prompt masked, which
is what `src/opgraph/data.py:encode_example` does.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time

import numpy as np

QUERY_MAX_TOKENS = 24

EPISODE_COMPONENTS = {
    # component: (file, max retrieval rounds)
    "relation": ("relation_train.jsonl", 4),
    "external": ("external_train.jsonl", 4),
    "mathgen": ("mathgen_train.jsonl", 3),
}
FLAT_COMPONENTS = {
    "plan_whole": "plan_train_whole.jsonl",
    "plan_step": "plan_train_step.jsonl",
}


def gold_in(chunk: str, gold: str) -> bool:
    """The gold answer standing as a whole token in a served page."""
    return re.search(rf"(?<![A-Za-z]){re.escape(gold)}(?![A-Za-z])",
                     chunk, re.I) is not None


def episode_trace(ep: dict, q: dict, tok, max_rounds: int,
                  max_prompt_tokens: int, max_len: int):
    """The trace the environment would have written for a correct rollout."""
    from src.rl.env import build_prompt, make_service

    sid = tok.special_ids
    prompt = build_prompt(ep, q, tok)
    if len(prompt) > max_prompt_tokens:
        return None, "prompt"
    service = make_service(ep.get("documents", []))
    if service is None:
        return None, "nodocs"
    qtoks = tok.encode(q["text"])[-QUERY_MAX_TOKENS:]
    query_text = tok.decode(qtoks)

    tokens, mask, amask = list(prompt), [0] * len(prompt), [0] * len(prompt)
    served_gold = False
    exhausted = False
    rounds = 0
    for _ in range(max_rounds):
        hit = service.top(query_text)
        if hit is None:
            exhausted = True
            break
        rounds += 1
        chunk = hit[1]
        ct = tok.encode(chunk)
        tokens.append(sid["<|retrieve|>"]); mask.append(1); amask.append(0)
        tokens.extend(qtoks); mask.extend([1] * len(qtoks)); amask.extend([0] * len(qtoks))
        tokens.append(sid["<|result|>"]); mask.append(1); amask.append(0)
        tokens.extend(ct); mask.extend([0] * len(ct)); amask.extend([0] * len(ct))
        if gold_in(chunk, q["answer"]):
            served_gold = True
            break
    else:
        exhausted = service.exhausted()

    derived = q.get("answer_source") == "derived_by_computation"
    if not (served_gold or exhausted or derived):
        return None, "unserved"

    at = tok.encode(" " + str(q["answer"]))
    tokens.append(sid["<|a|>"]); mask.append(1); amask.append(1)
    tokens.extend(at); mask.extend([1] * len(at)); amask.extend([1] * len(at))
    tokens.append(sid["<|eot|>"]); mask.append(1); amask.append(1)
    if len(tokens) > max_len:
        return None, "length"
    return {"tokens": tokens, "mask": mask, "amask": amask,
            "rounds": rounds, "served_gold": served_gold}, "ok"


def flat_trace(rec: dict, tok, max_len: int):
    """A prompt/target record, prompt masked, exactly as opgraph encodes it."""
    p = tok.encode(rec["prompt"])
    t = tok.encode(" " + rec["target"]) + [tok.special_ids["<|eot|>"]]
    tokens = p + t
    if len(tokens) > max_len:
        return None, "length"
    mask = [0] * len(p) + [1] * len(t)
    return {"tokens": tokens, "mask": mask, "amask": list(mask),
            "rounds": 0, "served_gold": False}, "ok"


class Pack:
    """Three flat arrays and one index line per example."""

    def __init__(self, out_prefix: str):
        self.tok_f = open(out_prefix + ".tokens.u16", "wb")
        self.msk_f = open(out_prefix + ".mask.u8", "wb")
        self.amk_f = open(out_prefix + ".amask.u8", "wb")
        self.idx_f = open(out_prefix + ".index.jsonl", "w")
        self.offset = 0
        self.n = 0

    def add(self, tr: dict, meta: dict) -> None:
        t = np.asarray(tr["tokens"], dtype=np.uint16)
        self.tok_f.write(t.tobytes())
        self.msk_f.write(np.asarray(tr["mask"], dtype=np.uint8).tobytes())
        self.amk_f.write(np.asarray(tr["amask"], dtype=np.uint8).tobytes())
        row = {"off": self.offset, "len": int(t.size),
               "sup": int(sum(tr["mask"])), "ans": int(sum(tr["amask"])),
               "rounds": tr["rounds"], "served_gold": tr["served_gold"], **meta}
        self.idx_f.write(json.dumps(row) + "\n")
        self.offset += int(t.size)
        self.n += 1

    def close(self) -> dict:
        for f in (self.tok_f, self.msk_f, self.amk_f, self.idx_f):
            f.close()
        return {"n": self.n, "tokens": self.offset}


def count_lines(path: str) -> int:
    n = 0
    with open(path, "rb") as fh:
        for _ in fh:
            n += 1
    return n


def cmd_build(args) -> int:
    from src.train.tokenizer import load_tokenizer

    tok = load_tokenizer(args.tokenizer)
    comp = args.component
    path = os.path.join(args.corpus, (EPISODE_COMPONENTS.get(comp, (None,))[0]
                                      or FLAT_COMPONENTS.get(comp)))
    total_lines = args.lines or count_lines(path)
    is_episode = comp in EPISODE_COMPONENTS
    per_line = args.questions_per_episode if is_episode else 1
    want_lines = max(1, int(round(args.take / per_line)))
    stride = max(1, total_lines // want_lines)
    rounds = EPISODE_COMPONENTS[comp][1] if is_episode else 0

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    pack = Pack(args.out)
    drops = {"prompt": 0, "nodocs": 0, "unserved": 0, "length": 0}
    kept = 0
    t0 = time.time()
    with open(path) as fh:
        for line_no, line in enumerate(fh):
            if line_no % stride:
                continue
            if kept >= args.take:
                break
            rec = json.loads(line)
            if is_episode:
                qs = list(rec.get("questions", []))
                order = list(range(len(qs)))
                random.Random(line_no).shuffle(order)
                for qi in order[:args.questions_per_episode]:
                    q = qs[qi]
                    if not q.get("answer"):
                        continue
                    tr, why = episode_trace(rec, q, tok, rounds,
                                            args.max_prompt_tokens, args.max_len)
                    if tr is None:
                        drops[why] += 1
                        continue
                    pack.add(tr, {"component": comp,
                                  "family": rec.get("family"),
                                  "frame": rec.get("frame"),
                                  "answer_source": q.get("answer_source"),
                                  "plan_len": q.get("plan_len"),
                                  "line": line_no, "qid": q.get("qid")})
                    kept += 1
            else:
                tr, why = flat_trace(rec, tok, args.max_len)
                if tr is None:
                    drops[why] += 1
                    continue
                pack.add(tr, {"component": comp,
                              "family": rec.get("record"),
                              "n_steps": rec.get("n_steps"),
                              "n_symbols": rec.get("n_symbols"),
                              "line": line_no})
                kept += 1
            if kept and kept % 20000 == 0:
                print(f"{comp}: {kept} kept, {time.time() - t0:.0f}s", flush=True)
    stats = pack.close()
    summary = {"component": comp, "path": path, "total_lines": total_lines,
               "stride": stride, "take": args.take, "kept": kept,
               "drops": drops, "tokens": stats["tokens"],
               "seconds": round(time.time() - t0, 1)}
    with open(args.out + ".summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary), flush=True)
    return 0


def cmd_merge(args) -> int:
    rows = []
    for prefix in args.packs:
        toks = np.memmap(prefix + ".tokens.u16", dtype=np.uint16, mode="r")
        msk = np.memmap(prefix + ".mask.u8", dtype=np.uint8, mode="r")
        amk = np.memmap(prefix + ".amask.u8", dtype=np.uint8, mode="r")
        with open(prefix + ".index.jsonl") as fh:
            for line in fh:
                r = json.loads(line)
                rows.append((prefix, r, toks, msk, amk))
    rng = random.Random(args.seed)
    rng.shuffle(rows)
    out = Pack(args.out)
    counts: dict = {}
    for prefix, r, toks, msk, amk in rows:
        a, b = r["off"], r["off"] + r["len"]
        tr = {"tokens": toks[a:b].tolist(), "mask": msk[a:b].tolist(),
              "amask": amk[a:b].tolist(), "rounds": r["rounds"],
              "served_gold": r["served_gold"]}
        meta = {k: v for k, v in r.items()
                if k not in ("off", "len", "sup", "ans", "rounds", "served_gold")}
        out.add(tr, meta)
        counts[r["component"]] = counts.get(r["component"], 0) + 1
    stats = out.close()
    summary = {"n": stats["n"], "tokens": stats["tokens"], "per_component": counts,
               "seed": args.seed, "packs": args.packs}
    with open(args.out + ".summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary), flush=True)
    return 0


def cmd_train(args) -> int:
    import math

    import torch
    import torch.nn.functional as F

    from src.evals.mc import load_checkpoint_model

    torch.manual_seed(args.seed)
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    model, state = load_checkpoint_model(args.checkpoint, device)
    model.train()

    toks = np.memmap(args.pack + ".tokens.u16", dtype=np.uint16, mode="r")
    msk = np.memmap(args.pack + ".mask.u8", dtype=np.uint8, mode="r")
    amk = np.memmap(args.pack + ".amask.u8", dtype=np.uint8, mode="r")
    index = [json.loads(l) for l in open(args.pack + ".index.jsonl")]
    n = len(index)
    micro = args.micro_batch
    accum = args.batch // micro
    if accum * micro != args.batch:
        raise SystemExit("batch must be a multiple of micro-batch")

    order = list(range(n))
    rng = random.Random(args.shuffle_seed)
    rng.shuffle(order)
    cursor = 0

    def next_micro():
        nonlocal cursor, order
        if cursor + micro > len(order):
            rng.shuffle(order)
            cursor = 0
        rows = [index[i] for i in order[cursor:cursor + micro]]
        cursor += micro
        width = max(r["len"] for r in rows)
        t = torch.zeros(len(rows), width, dtype=torch.long)
        m = torch.zeros(len(rows), width, dtype=torch.float)
        a = torch.zeros(len(rows), width, dtype=torch.float)
        for i, r in enumerate(rows):
            s, e = r["off"], r["off"] + r["len"]
            t[i, :r["len"]] = torch.from_numpy(np.asarray(toks[s:e], dtype=np.int64))
            m[i, :r["len"]] = torch.from_numpy(np.asarray(msk[s:e], dtype=np.float32))
            a[i, :r["len"]] = torch.from_numpy(np.asarray(amk[s:e], dtype=np.float32))
        return t, m, a

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, betas=(0.9, 0.95),
                            weight_decay=args.weight_decay, eps=1e-8)
    print(f"{n} examples, batch {args.batch} = {micro} x {accum}, "
          f"{args.steps} steps, lr {args.lr}", flush=True)
    log = open(args.log, "a")
    started = time.time()
    for step in range(1, args.steps + 1):
        warm = min(1.0, step / max(1, args.warmup))
        frac = step / max(1, args.steps)
        lr = args.lr * warm * (args.min_lr_ratio + (1 - args.min_lr_ratio)
                               * 0.5 * (1 + math.cos(math.pi * frac)))
        for g in opt.param_groups:
            g["lr"] = lr
        opt.zero_grad(set_to_none=True)
        tot_a = tot_q = 0.0
        for _ in range(accum):
            t, m, a = next_micro()
            t, m, a = t.to(device), m.to(device), a.to(device)
            x, y = t[:, :-1], t[:, 1:]
            mm, am = m[:, 1:], a[:, 1:]
            qm = (mm - am).clamp(min=0.0)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits, _ = model(x)
            ce = F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]),
                                 y.reshape(-1), reduction="none")
            loss_a = (ce * am.reshape(-1)).sum() / am.sum().clamp(min=1.0)
            loss_q = (ce * qm.reshape(-1)).sum() / qm.sum().clamp(min=1.0)
            loss = (loss_a + args.query_weight * loss_q) / accum
            loss.backward()
            tot_a += float(loss_a) / accum
            tot_q += float(loss_q) / accum
            del logits, ce, loss
        gn = torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        opt.step()
        if step % args.log_every == 0 or step == 1:
            rec = {"step": step, "loss_answer": round(tot_a, 5),
                   "loss_query": round(tot_q, 5), "lr": lr,
                   "grad_norm": round(float(gn), 4),
                   "elapsed_s": round(time.time() - started, 1),
                   "gpu_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)
                   if device == "cuda" else 0}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(json.dumps(rec), flush=True)
        if args.ckpt_every and step % args.ckpt_every == 0 and step < args.steps:
            _save(model, state, args, step, args.out + f".step{step}")
    _save(model, state, args, args.steps, args.out)
    print(f"[done] {args.out} after {args.steps} steps, "
          f"{(time.time() - started) / 60:.1f} min", flush=True)
    return 0


def _save(model, state, args, step, path) -> None:
    import torch
    save = {"model": model.state_dict(), "config": state["config"],
            "step": step,
            "sft": {"pack": args.pack, "steps": args.steps, "batch": args.batch,
                    "micro_batch": args.micro_batch, "lr": args.lr,
                    "warmup": args.warmup, "seed": args.seed,
                    "base": args.checkpoint}}
    tmp = path + ".tmp"
    torch.save(save, tmp)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--corpus", required=True)
    b.add_argument("--tokenizer", required=True)
    b.add_argument("--component", required=True,
                   choices=sorted(set(EPISODE_COMPONENTS) | set(FLAT_COMPONENTS)))
    b.add_argument("--out", required=True)
    b.add_argument("--take", type=int, required=True)
    b.add_argument("--lines", type=int, default=0)
    b.add_argument("--questions-per-episode", type=int, default=2)
    b.add_argument("--max-prompt-tokens", type=int, default=384)
    b.add_argument("--max-len", type=int, default=1024)
    b.set_defaults(fn=cmd_build)

    m = sub.add_parser("merge")
    m.add_argument("--packs", nargs="+", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--seed", type=int, default=90210)
    m.set_defaults(fn=cmd_merge)

    t = sub.add_parser("train")
    t.add_argument("--checkpoint", required=True)
    t.add_argument("--pack", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--log", required=True)
    t.add_argument("--steps", type=int, default=8000)
    t.add_argument("--batch", type=int, default=32)
    t.add_argument("--micro-batch", type=int, default=8)
    t.add_argument("--lr", type=float, default=2.0e-5)
    t.add_argument("--warmup", type=int, default=200)
    t.add_argument("--min-lr-ratio", type=float, default=0.1)
    t.add_argument("--weight-decay", type=float, default=0.0)
    t.add_argument("--grad-clip", type=float, default=1.0)
    t.add_argument("--query-weight", type=float, default=1.0)
    t.add_argument("--log-every", type=int, default=50)
    t.add_argument("--ckpt-every", type=int, default=0)
    t.add_argument("--seed", type=int, default=7701)
    t.add_argument("--shuffle-seed", type=int, default=4113)
    t.add_argument("--device", default=None)
    t.set_defaults(fn=cmd_train)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
