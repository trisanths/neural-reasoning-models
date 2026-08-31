"""Scoring the normalizer, and the trivial programs it has to beat.

A structure that is nearly right is wrong, because the interpreter executes it
exactly, so the headline is structure level exact match against the structure
that wrote the text. Four outcomes are counted and they are not the same:

    exact       the emitted structure equals the gold structure
    malformed   the token stream is not a structure at all, so nothing
                reaches the interpreter
    refused     the interpreter is handed the structure and declines it
    wrong       the structure executes and is not the gold structure

The first three are safe. The fourth is the dangerous one: a page read into a
plausible structure that runs and returns an answer nobody can tell is wrong.
The ratio between the safe failures and that one is a property of the design
and is reported on every split.

Three baselines travel with every number.

    parser      `src/norm/parse.py`, the hand written reference parser, on
                the same items. It is handed the frame id and the normalizer
                is not, so this is a generous baseline and beating it is the
                bar the task sets.
    modal       the most frequent target sequence in training, emitted for
                every item.
    modal/shape the most frequent target sequence for the item's own shape,
                which is the floor for a reader that is told the shape and
                then guesses the canonical filling of it. Slot ids are
                positional, so on the fixed arity shapes this floor is not
                near zero and reporting it matters.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict

import numpy as np
import torch

from src.norm.interp import run
from src.norm.lang import NormError, Program, program_load
from src.norm.ndata import load_meta, load_split
from src.norm.ntok import OutVocab, deserialize
from src.norm.parse import parse


def load_eval(path: str, limit: int = 0):
    ins, outs, ioff, ooff = load_split(path)
    meta = load_meta(path)
    n = len(meta) if not limit else min(limit, len(meta))
    items = []
    for i in range(n):
        m = meta[i]
        items.append({
            "ids": ins[ioff[i]:ioff[i + 1]].astype(np.int64),
            "gold_ids": outs[ooff[i]:ooff[i + 1]].astype(np.int64),
            "slots": m["slots"], "fid": m["fid"], "shape": m["shape"],
            "prog": program_load(m["prog"]), "text": m.get("text", ""),
        })
    return items


# ---------------------------------------------------------------- decoding


@torch.no_grad()
def emit(model, items, ov: OutVocab, device, mode="greedy", temperature=1.0,
         batch=64, max_len=320, seed=0):
    """Token sequences the model writes for each item, in item order."""
    order = sorted(range(len(items)), key=lambda i: len(items[i]["ids"]))
    out = [None] * len(items)
    g = torch.Generator(device=device)
    g.manual_seed(seed)
    model.eval()
    for b0 in range(0, len(order), batch):
        idx = order[b0:b0 + batch]
        lens = [len(items[i]["ids"]) for i in idx]
        w = max(lens)
        src = torch.full((len(idx), w), 0, dtype=torch.long)
        pad = torch.ones((len(idx), w), dtype=torch.bool)
        for r, i in enumerate(idx):
            a = items[i]["ids"]
            src[r, :len(a)] = torch.from_numpy(a)
            pad[r, :len(a)] = False
        src, pad = src.to(device), pad.to(device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            mem, mask = model.encode(src, pad)
            ys = torch.full((len(idx), 1), ov.bos, dtype=torch.long,
                            device=device)
            done = torch.zeros(len(idx), dtype=torch.bool, device=device)
            for _ in range(max_len):
                logits = model.decode(ys, mem, mask)[:, -1].float()
                if mode == "greedy":
                    nxt = logits.argmax(-1)
                else:
                    p = torch.softmax(logits / temperature, -1)
                    nxt = torch.multinomial(p, 1, generator=g).squeeze(-1)
                nxt = torch.where(done, torch.full_like(nxt, ov.pad), nxt)
                ys = torch.cat([ys, nxt[:, None]], 1)
                done = done | (nxt == ov.eos)
                if bool(done.all()):
                    break
        seq = ys[:, 1:].tolist()
        for r, i in enumerate(idx):
            s = seq[r]
            if ov.eos in s:
                s = s[:s.index(ov.eos)]
            out[i] = s
    return out


# ----------------------------------------------------------------- scoring


def candidates(p: Program):
    """The values the plan's last step could have returned, or None if open."""
    if not p.steps:
        return None
    s = p.steps[-1]
    names = [a for a in s.args if isinstance(a, str)]
    if s.op in ("weigh", "add", "sub", "mul", "step", "call"):
        return None
    want = {"lookup": "table", "lookup_ordered": "table", "invert": "table",
            "odd_one_out": "table", "prefer": "table", "band": "bands",
            "rule": "rule"}.get(s.op)
    if want is None:
        return None
    ds = [d for d in p.defs if d.kind == want and d.name in names]
    if not ds:
        return None
    out = set()
    for d in ds:
        if want == "table":
            if s.op in ("invert", "odd_one_out"):
                out |= {k for k, _ in d.entries}
            else:
                out |= {v for _, v in d.entries}
                if d.default is not None:
                    out.add(d.default)
        elif want == "bands":
            out |= set(d.labels)
        else:
            out.add(d.general)
            out |= {v for _, v in d.exceptions}
    return out or None


def classify_emission(toks, slots, gold: Program) -> dict:
    """One item's outcome: exact, malformed, refused, or wrong."""
    rec = {"malformed": False, "refused": False, "wrong": False,
           "exact": False, "answer": "", "reason": ""}
    try:
        prog = deserialize(toks, slots)
    except (NormError, Exception) as exc:      # a bad stream is a safe failure
        rec["malformed"] = True
        rec["reason"] = f"{type(exc).__name__}: {exc}"[:160]
        return rec
    rec["exact"] = (prog == gold)
    r = run(prog)
    if not r.ok:
        rec["refused"] = True
        rec["reason"] = r.reason[:160]
        return rec
    rec["answer"] = r.text
    rec["wrong"] = not rec["exact"]
    return rec


def modal_targets(train_path: str, meta_path: str = "", cap: int = 60000):
    """The most frequent training target overall and per shape."""
    ins, outs, ioff, ooff = load_split(train_path)
    n = min(cap, len(ooff) - 1)
    whole = Counter()
    for i in range(n):
        whole[tuple(outs[ooff[i]:ooff[i + 1]].tolist())] += 1
    return whole.most_common(1)[0][0]


def modal_by_shape(items, golds):
    """The most frequent gold target per shape, read off the eval split.

    Given to the baseline for free, which makes it a generous floor.
    """
    by = defaultdict(Counter)
    for it, g in zip(items, golds):
        by[it["shape"]][tuple(g)] += 1
    return {k: v.most_common(1)[0][0] for k, v in by.items()}


def score(items, emitted, ov: OutVocab, tag: str, want_parser=True):
    """Per shape rows and a pooled row that is never used as a headline."""
    rows = defaultdict(lambda: Counter())
    floors = defaultdict(list)
    records = []
    golds = [it["gold_ids"][1:-1].tolist() for it in items]
    modal_shape = modal_by_shape(items, golds)
    modal_all = Counter(tuple(g) for g in golds).most_common(1)[0][0]
    for it, e in zip(items, emitted):
        sh = it["shape"]
        gold = it["prog"]
        gr = run(gold)
        toks = ov.decode(e)
        rec = classify_emission(toks, it["slots"], gold)
        c = rows[sh]
        c["n"] += 1
        for k in ("exact", "malformed", "refused", "wrong"):
            c[k] += int(rec[k])
        if gr.ok:
            c["gold_exec"] += 1
            c["answer_ok"] += int(rec["answer"] == gr.text and rec["answer"])
        cand = candidates(gold)
        if cand:
            floors[sh].append(1.0 / len(cand))
        for name, seq in (("modal", modal_all),
                          ("modal_shape", modal_shape[sh])):
            mr = classify_emission(ov.decode(list(seq)), it["slots"], gold)
            c[f"{name}_exact"] += int(mr["exact"])
            if gr.ok:
                c[f"{name}_answer_ok"] += int(mr["answer"] == gr.text
                                              and mr["answer"])
        if want_parser and it["text"]:
            pp = parse(it["text"], it["fid"])
            c["parser_read"] += int(pp.ok)
            if pp.ok:
                c["parser_exact"] += int(pp.program == gold)
                pr = run(pp.program)
                if gr.ok:
                    c["parser_answer_ok"] += int(pr.ok and pr.text == gr.text)
        records.append({"fid": it["fid"], "shape": sh, "tag": tag,
                        "exact": rec["exact"], "malformed": rec["malformed"],
                        "refused": rec["refused"], "wrong": rec["wrong"],
                        "answer": rec["answer"], "gold_answer": gr.text,
                        "reason": rec["reason"]})
    out = {"tag": tag, "by_shape": {}, "pooled_do_not_headline": {}}
    tot = Counter()
    for sh, c in sorted(rows.items()):
        n = c["n"]
        row = {"n": n}
        for k in ("exact", "malformed", "refused", "wrong", "modal_exact",
                  "modal_shape_exact", "parser_exact"):
            row[k] = round(c[k] / n, 4)
        ge = c["gold_exec"]
        row["n_gold_executes"] = ge
        for k in ("answer_ok", "modal_answer_ok", "modal_shape_answer_ok",
                  "parser_answer_ok"):
            row[k] = round(c[k] / ge, 4) if ge else None
        row["parser_read"] = round(c["parser_read"] / n, 4)
        row["answer_chance_floor"] = (round(float(np.mean(floors[sh])), 4)
                                      if floors[sh] else None)
        out["by_shape"][sh] = row
        tot += c
    n = tot["n"]
    out["pooled_do_not_headline"] = {
        "n": n,
        "exact": round(tot["exact"] / n, 4),
        "malformed": round(tot["malformed"] / n, 4),
        "refused": round(tot["refused"] / n, 4),
        "wrong": round(tot["wrong"] / n, 4),
        "parser_exact": round(tot["parser_exact"] / n, 4),
    }
    return out, records


def write_records(path: str, records):
    with gzip.open(path, "wt") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
