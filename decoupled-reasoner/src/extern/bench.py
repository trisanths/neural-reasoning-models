"""Public benchmarks, scored the way the field scores them.

MMLU, ARC-Challenge and WinoGrande are multiple choice and are scored by
comparing the model's log likelihood of each candidate continuation, which is
the lm-evaluation-harness convention and is what published numbers are
computed from. Nothing is generated for those three, so a model is never
penalised for failing to follow an answer format.

Two prompt formats are run and both are reported, because which one a
publisher used changes the number and guessing wrong would put a harness gap
into every cell:

    completion   the raw few shot text an lm-eval task builds, with no chat
                 template, continuations " A" / " B" / " C" / " D"
    chat         the model's own chat template around the same question, with
                 the continuation scored after the assistant turn opens

The chance floor is 1 over the number of candidates and is reported on every
cell. Nothing is pooled across benchmarks.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time

import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

LETTERS = ["A", "B", "C", "D", "E"]

# Set from --bos. lm-eval prepends the bos token for models that define one,
# and LFM2 defines <|startoftext|>. Leaving it off shifts every position by
# one relative to how the model was trained to read a document start, so it is
# a candidate whenever a reproduction comes in under its published figure.
PREPEND_BOS = False


def read_parquet(path):
    return pq.read_table(path).to_pylist()


# ------------------------------------------------------------------ tasks

def load_mmlu(root, n, seed):
    test = read_parquet(f"{root}/mmlu/all/test-00000-of-00001.parquet")
    dev = read_parquet(f"{root}/mmlu/all/dev-00000-of-00001.parquet")
    by_sub = {}
    for r in dev:
        by_sub.setdefault(r["subject"], []).append(r)
    rng = random.Random(seed)
    rng.shuffle(test)
    rows = []
    for r in test[:n]:
        rows.append({
            "id": f"mmlu/{r['subject']}/{len(rows)}",
            "subject": r["subject"], "question": r["question"],
            "choices": list(r["choices"]), "gold": int(r["answer"]),
            "shots": by_sub.get(r["subject"], [])[:5],
        })
    return rows


def load_arc(root, n, seed):
    t = read_parquet(f"{root}/ai2_arc/ARC-Challenge/test-00000-of-00001.parquet")
    rng = random.Random(seed)
    rng.shuffle(t)
    rows = []
    for r in t:
        ch = r["choices"]
        texts, labels = list(ch["text"]), list(ch["label"])
        if r["answerKey"] not in labels:
            continue
        rows.append({"id": f"arc/{r['id']}", "subject": "arc",
                     "question": r["question"], "choices": texts,
                     "gold": labels.index(r["answerKey"]), "shots": []})
        if len(rows) >= n:
            break
    return rows


def load_winogrande(root, n, seed):
    t = read_parquet(
        f"{root}/winogrande/winogrande_xl/validation-00000-of-00001.parquet")
    rng = random.Random(seed)
    rng.shuffle(t)
    rows = []
    for r in t[:n]:
        rows.append({"id": f"wino/{len(rows)}", "subject": "winogrande",
                     "sentence": r["sentence"],
                     "choices": [r["option1"], r["option2"]],
                     "gold": int(r["answer"]) - 1, "shots": []})
    return rows


TASKS = {"mmlu": load_mmlu, "arc": load_arc, "winogrande": load_winogrande}


# ------------------------------------------------------------- prompting

def mmlu_block(q, choices, answer=None):
    s = q.strip() + "\n"
    for i, c in enumerate(choices):
        s += f"{LETTERS[i]}. {c}\n"
    s += "Answer:"
    if answer is not None:
        s += f" {LETTERS[answer]}\n\n"
    return s


def build_mc(row, task, fmt, tok, extra=""):
    """Returns (context, [continuations]) for a multiple choice item."""
    if task == "winogrande":
        # The lm-eval convention: the option replaces the blank and the
        # continuation is the rest of the sentence, so the two candidates
        # share a suffix and differ only in what fills the gap.
        pre, _, post = row["sentence"].partition("_")
        return [(pre + opt, post) for opt in row["choices"]], "pair"
    head = ""
    if task == "mmlu":
        subj = row["subject"].replace("_", " ")
        head = ("The following are multiple choice questions (with answers) "
                f"about {subj}.\n\n")
        for s in row["shots"]:
            head += mmlu_block(s["question"], list(s["choices"]),
                               int(s["answer"]))
    body = mmlu_block(row["question"], row["choices"])
    ctx = extra + head + body
    if fmt == "chat":
        msgs = [{"role": "user",
                 "content": (extra + "Answer this multiple choice question "
                             "with a single letter.\n\n"
                             + mmlu_block(row["question"], row["choices"]))}]
        ctx = tok.apply_chat_template(msgs, tokenize=False,
                                      add_generation_prompt=True)
        return [(ctx, LETTERS[i]) for i in range(len(row["choices"]))], "letter"
    return [(ctx, " " + LETTERS[i])
            for i in range(len(row["choices"]))], "letter"


# --------------------------------------------------------------- scoring

@torch.no_grad()
def loglik(model, tok, pairs, device, batch=8):
    """Sum log probability of each continuation given its context."""
    out = []
    for i in range(0, len(pairs), batch):
        chunk = pairs[i:i + batch]
        ctx_ids, full_ids = [], []
        for c, k in chunk:
            a = tok(c, add_special_tokens=False)["input_ids"]
            if PREPEND_BOS and tok.bos_token_id is not None:
                a = [tok.bos_token_id] + a
            b = tok(k, add_special_tokens=False)["input_ids"]
            if not b:
                b = tok(" " + k.strip(), add_special_tokens=False)["input_ids"]
            ctx_ids.append(a)
            full_ids.append(a + b)
        width = max(len(x) for x in full_ids)
        pad = tok.pad_token_id or 0
        inp = torch.full((len(chunk), width), pad, dtype=torch.long)
        att = torch.zeros((len(chunk), width), dtype=torch.long)
        for j, f in enumerate(full_ids):
            inp[j, width - len(f):] = torch.tensor(f)   # left pad
            att[j, width - len(f):] = 1
        logits = model(input_ids=inp.to(device),
                       attention_mask=att.to(device)).logits.float()
        lp = torch.log_softmax(logits, dim=-1)
        for j, (a, f) in enumerate(zip(ctx_ids, full_ids)):
            n_cont = len(f) - len(a)
            tot = 0.0
            for t in range(n_cont):
                pos = width - n_cont + t - 1      # predicts token at pos+1
                tgt = f[len(a) + t]
                tot += float(lp[j, pos, tgt])
            out.append((tot, n_cont))
    return out


@torch.no_grad()
def loglik_shared_ctx(model, tok, pairs, device, batch=4):
    """The fast path for candidates that are one token and share a context.

    Every MMLU and ARC candidate under both formats is a single letter token
    after a common prompt, so one forward over that prompt scores all of them:
    the log probabilities of the candidate tokens are read off the final
    position. This is arithmetically the same as scoring each candidate with
    its own forward, and `--no-fast-path` runs the slow form so the two can be
    checked against each other.
    """
    ctxs = [p[0] for p in pairs]
    conts = [p[1] for p in pairs]
    assert len(set(ctxs)) == 1, "shared context expected"
    ids = [tok(c, add_special_tokens=False)["input_ids"] for c in conts]
    if any(len(i) != 1 for i in ids):
        return None
    a = tok(ctxs[0], add_special_tokens=False)["input_ids"]
    if PREPEND_BOS and tok.bos_token_id is not None:
        a = [tok.bos_token_id] + a
    inp = torch.tensor([a], dtype=torch.long, device=device)
    logits = model(input_ids=inp).logits.float()
    lp = torch.log_softmax(logits[0, -1], dim=-1)
    return [(float(lp[i[0]]), 1) for i in ids]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--task", required=True, choices=list(TASKS))
    ap.add_argument("--fmt", default="completion", choices=("completion", "chat"))
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--root", default="data/extern")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--no-fast-path", action="store_true")
    ap.add_argument("--bos", action="store_true",
                    help="prepend the tokenizer's bos token to the context, "
                         "which lm-eval does by default for models that "
                         "define one")
    a = ap.parse_args()

    global PREPEND_BOS
    PREPEND_BOS = a.bos
    rows = TASKS[a.task](a.root, a.n, a.seed)
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()
    n_params = sum(p.numel() for p in model.parameters())

    t0 = time.time()
    recs = []
    for k, row in enumerate(rows):
        pairs, kind = build_mc(row, a.task, a.fmt, tok)
        sc = None
        if kind == "letter" and not a.no_fast_path:
            sc = loglik_shared_ctx(model, tok, pairs, a.device)
        if sc is None:
            sc = loglik(model, tok, pairs, a.device, a.batch)
        raw = [s for s, _ in sc]
        norm = [s / max(n, 1) for s, n in sc]
        recs.append({"id": row["id"], "subject": row["subject"],
                     "gold": row["gold"], "n_choices": len(pairs),
                     "pred": int(max(range(len(raw)), key=lambda i: raw[i])),
                     "pred_norm": int(max(range(len(norm)),
                                          key=lambda i: norm[i])),
                     "logp": raw})
        if (k + 1) % 25 == 0:
            el = time.time() - t0
            print(f"{k+1}/{len(rows)} {el:.0f}s "
                  f"eta {el/(k+1)*(len(rows)-k-1):.0f}s", flush=True)

    n = len(recs)
    acc = sum(r["pred"] == r["gold"] for r in recs) / n
    accn = sum(r["pred_norm"] == r["gold"] for r in recs) / n
    floor = sum(1.0 / r["n_choices"] for r in recs) / n
    res = {"model": a.model, "task": a.task, "fmt": a.fmt, "n": n,
           "seed": a.seed, "params_total": n_params,
           "acc": round(acc, 4), "acc_norm": round(accn, 4),
           "floor": round(floor, 4), "dtype": a.dtype,
           "seconds": round(time.time() - t0, 1),
           "shots": 5 if (a.task == "mmlu" and a.fmt == "completion") else 0,
           "fast_path": not a.no_fast_path, "bos": a.bos,
           "records": recs}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "records"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
