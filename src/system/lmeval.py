"""Scoring the language model's structures, on the ladder's own grader.

The model writes text. Splitting that text on whitespace gives the token list
`src/norm/ntok.py:deserialize` consumes, so the emission goes through exactly
the same `src/norm/neval.py:classify_emission` the encoder-decoder rungs go
through: exact, malformed, refused or wrong, per shape, against the same gold
program, with the same parser and modal baselines beside it.

Nothing is graded by asking whether an answer contains something.
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch

from src.norm import ndata, neval, nreport
from src.system import lmdata

SPLITS = ("train_frames_eval", "qframe", "lexicon", "mode", "mixed")


@torch.no_grad()
def generate(model, tok, device, prompts, max_new, temperature, seed,
             batch_size=24):
    """Batched decoding to <|eot|>, greedy at temperature 0.

    The shape `src/corpus/evalrun.py:generate_batch` uses, taking token ids
    rather than text because the prompt carries special markers.
    """
    from src.rl.sampler import CachedPolicy

    eot = tok.token_id("<|eot|>")
    out = []
    for i in range(0, len(prompts), batch_size):
        ids = prompts[i:i + batch_size]
        width = max(len(x) for x in ids)
        cap = min(width + max_new + 2, model.cfg.max_seq_len)
        policy = CachedPolicy(model, device, max_len=cap,
                              temperature=temperature, top_k=0, seed=seed + i)
        nxt = policy.begin([list(x) for x in ids])
        done = [False] * len(ids)
        gen = [[] for _ in ids]
        for _ in range(max_new):
            step = []
            for j, t in enumerate(nxt):
                if done[j]:
                    step.append(0)
                    continue
                if int(t) == eot:
                    done[j] = True
                    step.append(0)
                    continue
                gen[j].append(int(t))
                step.append(int(t))
            if all(done):
                break
            nxt = policy.advance(step)
        out.extend(tok.decode(g).strip() for g in gen)
    return out


class TextVocab:
    """The decode side of `OutVocab`, for emissions that arrive as strings.

    `neval.score` calls `ov.decode(e)` on whatever `emit` returned. Here the
    emission is already a token list, so decode is the identity, and the
    modal baselines still arrive as id sequences and are decoded properly.
    """

    def __init__(self, ov):
        self.ov = ov
        self.pad, self.bos, self.eos = ov.pad, ov.bos, ov.eos
        self.itos, self.stoi = ov.itos, ov.stoi

    def decode(self, ids):
        if ids and isinstance(ids[0], str):
            return list(ids)
        return self.ov.decode(ids)

    def encode(self, toks):
        return self.ov.encode(toks)

    def __len__(self):
        return len(self.ov)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", default=lmdata.TOKENIZER)
    ap.add_argument("--data", default="data/norm")
    ap.add_argument("--out", default="results/system/lmeval")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n", type=int, default=1400)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--max-new", type=int, default=640)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--splits", default=",".join(SPLITS))
    ap.add_argument("--modes", default="greedy,sampled")
    a = ap.parse_args()

    from src.evals.mc import load_checkpoint_model
    from src.train.tokenizer import load_tokenizer

    device = "cuda"
    tok = load_tokenizer(a.tokenizer)
    model, state = load_checkpoint_model(a.ckpt, device)
    iv, ov = ndata._vocab()
    tv = TextVocab(ov)
    outdir = os.path.join(a.out, a.tag)
    os.makedirs(outdir, exist_ok=True)

    report = {"ckpt": os.path.abspath(a.ckpt), "tag": a.tag,
              "cfg": state["config"]["model"],
              "params": sum(p.numel() for p in model.parameters()),
              "step": state.get("step"), "eval_n": a.n,
              "max_new": a.max_new, "temperature": a.temperature,
              "splits": {}}
    for sp in a.splits.split(","):
        items = neval.load_eval(os.path.join(a.data, sp), a.n)
        prompts = [lmdata.prompt_ids(tok, it["text"], it["slots"])
                   for it in items]
        report["splits"][sp] = {"n": len(items),
                                "prompt_len_max": max(len(p) for p in prompts),
                                "modes": {}}
        for mode in a.modes.split(","):
            t0 = time.time()
            temp = 0.0 if mode == "greedy" else a.temperature
            texts = generate(model, tok, device, prompts, a.max_new, temp,
                             seed=0, batch_size=a.batch)
            em = [t.split() for t in texts]
            summ, recs = neval.score(items, em, tv, f"{a.tag}/{sp}/{mode}",
                                     want_parser=(mode == "greedy"))
            for r, t in zip(recs, texts):
                r["emitted"] = t[:400]
            rp = os.path.join(outdir, f"records_{sp}_{mode}.jsonl.gz")
            neval.write_records(rp, recs)
            summ["records"] = os.path.abspath(rp)
            summ["by_axis"] = nreport.by_axis(recs)
            summ["seconds"] = round(time.time() - t0, 1)
            summ["empty_emissions"] = sum(1 for t in texts if not t.strip())
            report["splits"][sp]["modes"][mode] = summ
            print(json.dumps({"split": sp, "mode": mode,
                              "pooled": summ["pooled_do_not_headline"],
                              "sec": summ["seconds"]}), flush=True)
    path = os.path.join(outdir, "summary.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", os.path.abspath(path))


if __name__ == "__main__":
    main()
