"""LFM2-350M on the key position items, one formulation per invocation.

The model is prompted through its own `tokenizer.apply_chat_template`, which
emits `<|startoftext|>` as the first token of the rendered string, so the bos
token the harness calibration turned on is present by construction rather than
by a flag. `--check-bos` asserts that before anything is scored and writes the
rendered first prompt into the meta file.

Two families of formulation:

  the loglik forms score candidate continuations and generate nothing, so a
  model is never charged for failing an answer format;
  the generation forms decode and parse, greedy and sampled, with a budget
  several times the length of any answer these questions need.

Nothing is pooled across key position. Records carry the raw output so a
rescore never needs a second decode.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

FORMS = ("role_letter_ll", "role_word_ll", "role_letter_gen",
         "role_open_gen", "role_verify_ll", "line_emit_gen", "page_qa_gen",
         "table_emit_gen")


# ------------------------------------------------------------------ prompts

PHRASING = "p1"
SHOTS = 0

# Worked examples, for --shots. Both key positions appear and neither
# sentence shape is `relative_clause`, so what a demonstration teaches is the
# task and never the syntax of the held-out sentence mode or a rule about
# which position the answer sits in. The invented words are not in any split.
DEMO = [
    ("{k} maps to {v}.", True),
    ("{v} is the image of {k}.", False),
    ("The {item} type {k} goes to the {v} {target}.", True),
    ("The {v} {target} takes the {item} type {k}.", False),
]
DEMO_WORDS = [("glimport", "fenwold"), ("brackle", "sunmere"),
              ("polvex", "murrow"), ("tandrel", "kepshaw")]


def demo_recs(rec, seed):
    """The worked examples for one item, as records the prompt builders take."""
    rng = random.Random(f"demo|{seed}|{rec['iid']}")
    idx = list(range(len(DEMO)))
    rng.shuffle(idx)
    out = []
    for j in idx[:SHOTS]:
        tmpl, kf = DEMO[j]
        k, v = DEMO_WORDS[j]
        line = tmpl.format(k=k, v=v, item=rec["item_noun"],
                           target=rec["target_noun"])
        opts = [k, v]
        rng.shuffle(opts)
        out.append({"item_noun": rec["item_noun"],
                    "target_noun": rec["target_noun"],
                    "pair": {"k": k, "v": v, "line": line, "options": opts,
                             "first_symbol": k if kf else v,
                             "probe_symbol": k}})
    return out


def demo_answer(form, d, direction):
    k, v = d["pair"]["k"], d["pair"]["v"]
    gold = k if direction == "key" else v
    if form == "role_letter_ll" or form == "role_letter_gen":
        return "A" if d["pair"]["options"][0] == gold else "B"
    if form == "line_emit_gen":
        return f"{k} -> {v}"
    if form == "role_verify_ll":
        return "yes" if d["pair"]["probe_symbol"] == gold else "no"
    return gold


def noun(rec, direction):
    return rec["item_noun"] if direction == "key" else rec["target_noun"]


def gold_symbol(rec, direction):
    return rec["pair"]["k"] if direction == "key" else rec["pair"]["v"]


def stem(rec, direction):
    """The question, in one of three wordings. All three are reported."""
    it, tg, nn = rec["item_noun"], rec["target_noun"], noun(rec, direction)
    if PHRASING == "p1":
        return f"Which word names the {nn}?"
    if PHRASING == "p2":
        return (f"In that line, one word is the name of a {it} type and the "
                f"other is the name of a {tg}. Which word is the name of the "
                f"{nn}?")
    return (f"That line pairs a {it} type with a {tg}. "
            f"Give the {nn} it names.")


def head(rec):
    return f'Read this line from a reference page.\n\n{rec["pair"]["line"]}\n\n'


def p_role_letter(rec, direction):
    a, b = rec["pair"]["options"]
    return (head(rec) + stem(rec, direction)
            + f'\nA. {a}\nB. {b}\nAnswer with a single letter.')


def p_role_word(rec, direction):
    a, b = rec["pair"]["options"]
    return (head(rec) + stem(rec, direction)
            + f' The answer is {a} or {b}. Answer with the word only.')


def p_role_open(rec, direction):
    return head(rec) + stem(rec, direction) + " Answer with the word only."


def p_role_verify(rec, direction):
    """Is this one symbol the named role? A yes or no with a 0.5 floor."""
    it, tg = rec["item_noun"], rec["target_noun"]
    sym = rec["pair"]["probe_symbol"]
    nn = noun(rec, direction)
    return (head(rec)
            + f'In that line, is {sym} the name of the {nn}? '
            f'(One of the two invented words names a {it} type and the other '
            f'names a {tg}.)\nAnswer yes or no.')


def p_line_emit(rec, direction):
    """One line, rewritten as one arrow rule. Direction is the whole answer."""
    it, tg = rec["item_noun"], rec["target_noun"]
    return (head(rec) + f'Rewrite that line as a single arrow rule of the '
            f'form\n\n{it} -> {tg}\n\nusing the two invented names from the '
            f'line and nothing else.')


def p_page_qa(rec, direction):
    return (f'{rec["pages_text"]}\n\n{rec["question"]}\n\n'
            f'Answer with a single word.')


def p_table_emit(rec, direction):
    it, tg = rec["item_noun"], rec["target_noun"]
    return (f'{rec["pages_text"]}\n\nList every rule stated on this page, one '
            f'per line, in the form\n\n{it} -> {tg}\n\nusing only the names '
            f'given on the page. Leave out the rule that covers anything '
            f'unlisted. Write nothing else.')


PROMPT = {"role_letter_ll": p_role_letter, "role_word_ll": p_role_word,
          "role_letter_gen": p_role_letter, "role_open_gen": p_role_open,
          "role_verify_ll": p_role_verify, "line_emit_gen": p_line_emit,
          "page_qa_gen": p_page_qa, "table_emit_gen": p_table_emit}
NEEDS = {"role_letter_ll": "pair", "role_word_ll": "pair",
         "role_letter_gen": "pair", "role_open_gen": "pair",
         "role_verify_ll": "pair", "line_emit_gen": "pair",
         "page_qa_gen": None, "table_emit_gen": "table"}


# ------------------------------------------------------------------ scoring

def words(s):
    return re.findall(r"[A-Za-z0-9_]+", s)


def score_role_gen(rec, direction, raw, letter_form):
    """Which of the two symbols the answer names, and how it was read off."""
    k, v = rec["pair"]["k"], rec["pair"]["v"]
    a, b = rec["pair"]["options"]
    pick, how = None, "none"
    toks = words(raw)
    if letter_form:
        for t in toks:
            if t in ("A", "B"):
                pick, how = (a if t == "A" else b), "letter"
                break
    if pick is None:
        for t in toks:
            tl = t.lower()
            if tl == k.lower():
                pick, how = k, "word"
                break
            if tl == v.lower():
                pick, how = v, "word"
                break
    gold = k if direction == "key" else v
    first = rec["pair"]["first_symbol"]
    return {"pick": pick, "how": how,
            "correct": int(pick is not None and pick == gold),
            "refused": int(pick is None),
            "picked_first": None if pick is None else int(pick == first)}


def score_line_emit(rec, raw):
    """Whether the arrow was written key on the left, value on the right."""
    k, v = rec["pair"]["k"].lower(), rec["pair"]["v"].lower()
    for ln in raw.split("\n"):
        if "->" not in ln:
            continue
        left, _, right = ln.partition("->")
        lw, rw = [w.lower() for w in words(left)], [w.lower() for w in
                                                    words(right)]
        if not lw or not rw:
            continue
        a, b = lw[-1], rw[0]
        if {a, b} != {k, v}:
            return {"correct": 0, "well_formed": 0, "arrow": f"{a}->{b}",
                    "picked_first": None}
        first = rec["pair"]["first_symbol"].lower()
        return {"correct": int(a == k), "well_formed": 1,
                "arrow": f"{a}->{b}", "picked_first": int(a == first)}
    return {"correct": 0, "well_formed": 0, "arrow": "", "picked_first": None}


def score_page_qa(rec, raw):
    gold = rec["gold_answer"]
    toks = words(raw)
    syms = {w.lower() for w in words(rec["pages_text"])}
    first_sym = None
    for t in toks:
        if t.lower() in syms and t.lower() not in _STOP:
            first_sym = t
            break
    lenient = int(any(t.lower() == gold.lower() for t in toks))
    return {"first_symbol": first_sym,
            "strict": int(first_sym is not None
                          and first_sym.lower() == gold.lower()),
            "lenient": lenient, "empty": int(not toks)}


_STOP = set()


def score_table_emit(rec, raw):
    gold = [(k, v) for k, v in rec["table"]["entries"]]
    gold_un = {frozenset((k.lower(), v.lower())): (k.lower(), v.lower())
               for k, v in gold}
    got = []
    for ln in raw.split("\n"):
        if "->" not in ln:
            continue
        left, _, right = ln.partition("->")
        lw, rw = words(left), words(right)
        if not lw or not rw:
            continue
        got.append((lw[-1].lower(), rw[0].lower()))
    dflt = (rec["table"].get("default") or "").lower()
    kept = [(a, b) for a, b in got
            if a != "unlisted" and b != "unlisted" and b != dflt]
    want = {(k.lower(), v.lower()) for k, v in gold}
    strict = int(set(got) == want and len(got) == len(gold))
    strict_nodefault = int(set(kept) == want and len(kept) == len(gold))
    got = kept
    matched = dirok = 0
    for a, b in got:
        key = frozenset((a, b))
        if key in gold_un and a != b:
            matched += 1
            dirok += int(gold_un[key] == (a, b))
    return {"n_lines": len(got), "strict": strict,
            "strict_nodefault": strict_nodefault,
            "matched_pairs": matched, "direction_correct": dirok,
            "n_gold": len(gold)}


# ------------------------------------------------------------------- engine

@torch.no_grad()
def ll_single_token(model, tok, ctxs, conts, device, batch, pad):
    """Candidates that are one token each: read them off the last position."""
    cid = []
    for c in conts:
        ids = tok(c, add_special_tokens=False)["input_ids"]
        if len(ids) != 1:
            return None
        cid.append(ids[0])
    out = []
    for i in range(0, len(ctxs), batch):
        chunk = ctxs[i:i + batch]
        ids = [tok(c, add_special_tokens=False)["input_ids"] for c in chunk]
        w = max(len(x) for x in ids)
        inp = torch.full((len(chunk), w), pad, dtype=torch.long)
        att = torch.zeros((len(chunk), w), dtype=torch.long)
        for j, f in enumerate(ids):
            inp[j, w - len(f):] = torch.tensor(f)
            att[j, w - len(f):] = 1
        lg = model(input_ids=inp.to(device),
                   attention_mask=att.to(device)).logits[:, -1].float()
        lp = torch.log_softmax(lg, dim=-1)
        for j in range(len(chunk)):
            out.append([float(lp[j, c]) for c in cid])
    return out


@torch.no_grad()
def ll_pairs(model, tok, pairs, device, batch, pad):
    """Sum log probability of each continuation given its own context."""
    out = []
    for i in range(0, len(pairs), batch):
        chunk = pairs[i:i + batch]
        ctx, full = [], []
        for c, k in chunk:
            a = tok(c, add_special_tokens=False)["input_ids"]
            b = tok(k, add_special_tokens=False)["input_ids"]
            ctx.append(a)
            full.append(a + b)
        w = max(len(x) for x in full)
        inp = torch.full((len(chunk), w), pad, dtype=torch.long)
        att = torch.zeros((len(chunk), w), dtype=torch.long)
        for j, f in enumerate(full):
            inp[j, w - len(f):] = torch.tensor(f)
            att[j, w - len(f):] = 1
        lp = torch.log_softmax(
            model(input_ids=inp.to(device),
                  attention_mask=att.to(device)).logits.float(), dim=-1)
        for j, (a, f) in enumerate(zip(ctx, full)):
            n = len(f) - len(a)
            tot = 0.0
            for t in range(n):
                tot += float(lp[j, w - n + t - 1, f[len(a) + t]])
            out.append((tot, n))
    return out


@torch.no_grad()
def gen(model, tok, prompts, device, batch, gkw, max_batch_tokens):
    out = [None] * len(prompts)
    order = sorted(range(len(prompts)), key=lambda i: -len(prompts[i]))
    t0, done, b = time.time(), 0, 0
    while b < len(order):
        idx = order[b:b + batch]
        if max_batch_tokens:
            while len(idx) > 1 and \
                    len(idx) * len(prompts[idx[0]]) // 3 > max_batch_tokens:
                idx = idx[:len(idx) // 2]
        b += len(idx)
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True,
                  add_special_tokens=False).to(device)
        g = model.generate(**enc, **gkw)
        new = g[:, enc["input_ids"].shape[1]:]
        for k, i in enumerate(idx):
            out[i] = {"raw": tok.decode(new[k], skip_special_tokens=True),
                      "n_new": int((new[k] != tok.pad_token_id).sum()),
                      "n_prompt": int(enc["attention_mask"][k].sum())}
        done += len(idx)
        if done % (batch * 8) < batch:
            el = time.time() - t0
            print(f"  {done}/{len(prompts)} {el:.0f}s "
                  f"eta {el / done * (len(prompts) - done):.0f}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="LiquidAI/LFM2-350M")
    ap.add_argument("--form", required=True, choices=FORMS)
    ap.add_argument("--split", required=True)
    ap.add_argument("--direction", default="key", choices=("key", "value"))
    ap.add_argument("--phrasing", default="p1", choices=("p1", "p2", "p3"))
    ap.add_argument("--shots", type=int, default=0)
    ap.add_argument("--items", default="results/role/lfm2/items")
    ap.add_argument("--out", default="results/role/lfm2/runs")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--decode", default="greedy", choices=("greedy", "sampled"))
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--max-batch-tokens", type=int, default=24000)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    a = ap.parse_args()

    global PHRASING, SHOTS
    PHRASING = a.phrasing
    SHOTS = a.shots
    src = os.path.join(a.items, f"{a.split}.jsonl.gz")
    rows = [json.loads(l) for l in gzip.open(src, "rt")]
    need = NEEDS[a.form]
    if need:
        rows = [r for r in rows if need in r]
    if a.form == "role_verify_ll":
        for r in rows:
            rr = random.Random(f'verify|{r["iid"]}')
            r["pair"]["probe_symbol"] = rr.choice(
                [r["pair"]["k"], r["pair"]["v"]])
    if a.limit:
        rows = rows[:a.limit]          # the file is already shuffled
    print(f"{a.form} {a.split} {a.direction} n={len(rows)}", flush=True)

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=getattr(torch, a.dtype)).to(a.device).eval()

    build = PROMPT[a.form]
    def msgs(r):
        m = []
        for d in ([] if a.form in ("page_qa_gen", "table_emit_gen")
                  else demo_recs(r, a.seed)):
            m.append({"role": "user", "content": build(d, a.direction)})
            m.append({"role": "assistant",
                      "content": demo_answer(a.form, d, a.direction)})
        m.append({"role": "user", "content": build(r, a.direction)})
        return m

    rendered = [tok.apply_chat_template(msgs(r), tokenize=False,
                                        add_generation_prompt=True)
                for r in rows]

    # bos check, before anything is scored
    ids0 = tok(rendered[0], add_special_tokens=False)["input_ids"]
    bos = tok.bos_token_id
    assert bos is not None, "LFM2 must define a bos token"
    assert ids0[0] == bos, (
        f"first token {ids0[0]} is not bos {bos}; the chat template must emit "
        f"{tok.bos_token}")
    meta = {"model": a.model, "form": a.form, "split": a.split,
            "direction": a.direction, "n": len(rows), "decode": a.decode,
            "max_new": a.max_new, "dtype": a.dtype, "seed": a.seed,
            "items_file": os.path.abspath(src),
            "params_total": sum(p.numel() for p in model.parameters()),
            "bos_token": tok.bos_token, "bos_token_id": bos,
            "first_prompt_rendered": rendered[0],
            "first_prompt_first_ids": ids0[:8],
            "chat_template_sha256": __import__("hashlib").sha256(
                (tok.chat_template or "").encode()).hexdigest()}

    t0 = time.time()
    recs = []
    if a.form.endswith("_ll"):
        if a.form == "role_verify_ll":
            sc = ll_single_token(model, tok, rendered, ["yes", "no"], a.device,
                                 a.batch, tok.pad_token_id)
            for r, s_ in zip(rows, sc):
                sym = r["pair"]["probe_symbol"]
                gold_yes = int(sym == gold_symbol(r, a.direction))
                said_yes = int(s_[0] >= s_[1])
                recs.append({"iid": r["iid"], "fid": r["fid"], "kp": r["kp"],
                             "mode": r["mode"], "shape": r["shape"],
                             "eight": r["eight"], "logp": s_,
                             "probe_symbol": sym,
                             "probe_is_first": int(
                                 sym == r["pair"]["first_symbol"]),
                             "gold_yes": gold_yes, "said_yes": said_yes,
                             "correct": int(said_yes == gold_yes)})
        elif a.form == "role_letter_ll":
            sc = ll_single_token(model, tok, rendered, ["A", "B"], a.device,
                                 a.batch, tok.pad_token_id)
            for r, s in zip(rows, sc):
                pick = r["pair"]["options"][0 if s[0] >= s[1] else 1]
                gold = gold_symbol(r, a.direction)
                recs.append({"iid": r["iid"], "fid": r["fid"], "kp": r["kp"],
                             "mode": r["mode"], "shape": r["shape"],
                             "eight": r["eight"], "logp": s,
                             "pick": pick, "correct": int(pick == gold),
                             "picked_first": int(
                                 pick == r["pair"]["first_symbol"]),
                             "picked_A": int(s[0] >= s[1])})
        else:
            flat = []
            for r, c in zip(rows, rendered):
                for o in r["pair"]["options"]:
                    flat.append((c, o))
            sc = ll_pairs(model, tok, flat, a.device, max(8, a.batch // 4),
                          tok.pad_token_id)
            for i, r in enumerate(rows):
                (s0, n0), (s1, n1) = sc[2 * i], sc[2 * i + 1]
                pick = r["pair"]["options"][0 if s0 >= s1 else 1]
                pickn = r["pair"]["options"][
                    0 if s0 / max(n0, 1) >= s1 / max(n1, 1) else 1]
                gold = gold_symbol(r, a.direction)
                recs.append({"iid": r["iid"], "fid": r["fid"], "kp": r["kp"],
                             "mode": r["mode"], "shape": r["shape"],
                             "eight": r["eight"], "logp": [s0, s1],
                             "ntok": [n0, n1], "pick": pick,
                             "correct": int(pick == gold),
                             "correct_norm": int(pickn == gold),
                             "picked_first": int(
                                 pick == r["pair"]["first_symbol"])})
    else:
        gkw = {"max_new_tokens": a.max_new, "pad_token_id": tok.pad_token_id}
        if a.decode == "greedy":
            gkw.update(do_sample=False, temperature=None, top_p=None,
                       top_k=None)
        else:
            gkw.update(do_sample=True, temperature=0.1, top_k=50,
                       repetition_penalty=1.05)
            torch.manual_seed(a.seed)
        meta["gen_kwargs"] = {k: v for k, v in gkw.items()
                              if k != "pad_token_id"}
        outs = gen(model, tok, rendered, a.device, a.batch, gkw,
                   a.max_batch_tokens)
        for r, o in zip(rows, outs):
            rec = {"iid": r["iid"], "fid": r["fid"], "kp": r["kp"],
                   "mode": r["mode"], "shape": r["shape"], "eight": r["eight"],
                   "raw": o["raw"], "n_new": o["n_new"],
                   "n_prompt": o["n_prompt"],
                   "truncated": int(o["n_new"] >= a.max_new)}
            if a.form == "role_letter_gen":
                rec.update(score_role_gen(r, a.direction, o["raw"], True))
            elif a.form == "role_open_gen":
                rec.update(score_role_gen(r, a.direction, o["raw"], False))
            elif a.form == "line_emit_gen":
                rec.update(score_line_emit(r, o["raw"]))
            elif a.form == "page_qa_gen":
                rec.update(score_page_qa(r, o["raw"]))
            else:
                rec.update(score_table_emit(r, o["raw"]))
            recs.append(rec)
    meta["seconds"] = round(time.time() - t0, 1)

    meta["phrasing"] = a.phrasing
    meta["shots"] = a.shots
    sh = "" if not a.shots else f"_s{a.shots}"
    tag = f"{a.form}_{a.phrasing}{sh}_{a.split}_{a.direction}_{a.decode}"
    os.makedirs(a.out, exist_ok=True)
    dest = os.path.join(a.out, f"{tag}.jsonl.gz")
    with gzip.open(dest, "wt") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    meta["records"] = os.path.abspath(dest)
    with open(os.path.join(a.out, f"{tag}.meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print("wrote", os.path.abspath(dest), f"{meta['seconds']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
