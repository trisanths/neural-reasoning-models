"""Kill-test eval battery driver.

Runs the full evaluation battery against one or more trainer checkpoints
and writes one JSON per checkpoint plus a combined results.json. The
battery per checkpoint:

  naturalized reading  all items, greedy decode, EM and contains-answer,
                       plus a contradiction-injected variant (rate 0.15)
                       and an OCR-noised variant (rate 0.05); each regime
                       gets its native elicitation format (prose
                       continuation for A, episode trace for C)
  knowledge probes     four-way multiple choice, accuracy vs chance and
                       the leakage flag
  held-out worlds      C-regime checkpoints run the interactive
                       emit-query-read loop, A-regime checkpoints read
                       packed documents in context
  noise axis           C-regime checkpoints only, corruption rates over
                       the interactive loop

Checkpoints are given as run directories (the highest numbered
ckpt-*.pt is used, never latest.pt) or as direct .pt paths. The regime
and seed are parsed from the killtest-{a,c}-{seed} run name.

Example:

    CUDA_VISIBLE_DEVICES=6 python -m scripts.eval_battery \
        --checkpoints ~/runs/killtest-a-101 ~/runs/killtest-c-201 \
        --tokenizer ~/data/tokenizer_v2.json \
        --heldout ~/data/regime_c/heldout.jsonl \
        --out ~/eval-out/rehearsal --device cuda
"""

import argparse
import glob
import json
import os
import re
import time
import zlib
from pathlib import Path

RUN_NAME_RE = re.compile(r"killtest-([ac])-(\d+)")

CONTRADICTION_RATE = 0.15
CONTRADICTION_SEED = 20260824
OCR_RATE = 0.05
OCR_SEED = 20260825


def parse_regime(path: str):
    """Return (regime, seed) parsed from a killtest-{a,c}-{seed} path."""
    m = RUN_NAME_RE.search(str(path))
    if not m:
        raise ValueError(
            f"cannot parse regime from {path!r}; expected killtest-a-<seed> "
            f"or killtest-c-<seed> in the path")
    return m.group(1), int(m.group(2))


def resolve_checkpoint(path: str, step=None) -> str:
    """Resolve a run dir to a numbered checkpoint file.

    A direct .pt path passes through. Otherwise the run dir is searched
    for ckpt-*.pt; --step picks that exact step, else the highest
    numbered checkpoint wins. latest.pt is never used because trainers
    rewrite it continuously.
    """
    p = Path(path)
    if p.is_file():
        return str(p)
    if step is not None:
        cand = p / f"ckpt-{step:07d}.pt"
        if not cand.is_file():
            raise FileNotFoundError(f"{cand} does not exist")
        return str(cand)
    ckpts = sorted(p.glob("ckpt-*.pt"))
    if not ckpts:
        raise FileNotFoundError(f"no ckpt-*.pt under {p}")
    return str(ckpts[-1])


def load_heldout_episodes(path: str, n: int):
    episodes = []
    with open(path) as fh:
        for line in fh:
            if len(episodes) >= n:
                break
            line = line.strip()
            if line:
                episodes.append(json.loads(line))
    if len(episodes) < n:
        raise ValueError(f"asked for {n} episodes, {path} holds {len(episodes)}")
    return episodes


def stratified_subset(items, n: int):
    """Take n items round-robin across registers, preserving file order."""
    if n <= 0 or n >= len(items):
        return list(items)
    by_register = {}
    for item in items:
        by_register.setdefault(item["register"], []).append(item)
    order = sorted(by_register)
    out = []
    depth = 0
    while len(out) < n:
        for register in order:
            bucket = by_register[register]
            if depth < len(bucket):
                out.append(bucket[depth])
                if len(out) == n:
                    return out
        depth += 1
    return out


def _greedy_tail(step_fn, tokenizer, tokens, max_new_tokens: int) -> str:
    """Greedy-decode from tokens until a special token or the budget."""
    import numpy as np

    special_ids = set(tokenizer.special_ids.values())
    generated = []
    for _ in range(max_new_tokens):
        nxt = int(np.argmax(np.asarray(step_fn(tokens)).reshape(-1)))
        if nxt in special_ids:
            break
        tokens.append(nxt)
        generated.append(nxt)
    return tokenizer.decode(generated)


def make_prose_predict_fn(step_fn, tokenizer, max_new_tokens: int):
    """Native elicitation for regime A: plain-prose continuation.

    Regime A training data is raw BPE text with one <|eot|> per document
    (scripts/render_regime_a.py); the other special tokens never occur,
    so the prompt uses none. The passage is followed by a question line
    and an answer cue, and the prediction is the first generated line.
    """

    def predict(passage: str, question: str) -> str:
        prompt = f"{passage}\n\nQuestion: {question}\nAnswer:"
        text = _greedy_tail(step_fn, tokenizer,
                            tokenizer.encode(prompt), max_new_tokens)
        return text.split("\n")[0].strip()

    return predict


def make_episode_predict_fn(step_fn, tokenizer, max_new_tokens: int):
    """Native elicitation for regime C: a minimal episode-format trace.

    Follows src/train/data.py render_episode exactly: <|world|> plus the
    rendered preamble, <|doc|> plus the passage as the single document,
    then <|q|> question <|a|>, and decoding runs until a special token,
    normally <|eot|>. No retrieval loop: the passage sits in context
    because reading, not retrieval, is the skill under test here.
    """
    from src.train.data import render_world_preamble

    sid = tokenizer.special_ids
    preamble = tokenizer.encode(render_world_preamble({"domain": "naturalized"}))

    def predict(passage: str, question: str) -> str:
        tokens = [sid["<|world|>"], *preamble,
                  sid["<|doc|>"], *tokenizer.encode(passage),
                  sid["<|q|>"], *tokenizer.encode(question), sid["<|a|>"]]
        return _greedy_tail(step_fn, tokenizer, tokens, max_new_tokens).strip()

    return predict


def score_naturalized(items, predict_fn):
    """Score items and keep per-item outcomes for the verdict bootstrap."""
    from src.evals.naturalized import (SUITE_VERSION, contains_answer,
                                       exact_match)

    per_item = []
    per_register = {}
    n_em = 0
    n_contains = 0
    for item in items:
        pred = predict_fn(item["passage"], item["question"])
        em = exact_match(pred, item["answer"])
        contains = contains_answer(pred, item["answer"])
        n_em += int(em)
        n_contains += int(contains)
        per_item.append({"id": item["id"], "em": bool(em),
                         "contains": bool(contains), "pred": pred})
        stats = per_register.setdefault(
            item["register"], {"n": 0, "em": 0, "contains": 0})
        stats["n"] += 1
        stats["em"] += int(em)
        stats["contains"] += int(contains)
    for stats in per_register.values():
        stats["em"] = round(stats["em"] / stats["n"], 4)
        stats["contains"] = round(stats["contains"] / stats["n"], 4)
    n = len(items)
    return {
        "suite": "naturalized_reading",
        "version": SUITE_VERSION,
        "n": n,
        "em": n_em / n,
        "contains": n_contains / n,
        "per_register": per_register,
        "per_item": per_item,
    }


def run_naturalized_block(items, predict_fn, timings: dict) -> dict:
    """Clean, contradiction-injected, and OCR-noised passes over the suite."""
    from src.evals.naturalized import inject_contradiction, ocr_noise

    t0 = time.monotonic()
    clean = score_naturalized(items, predict_fn)
    timings["naturalized_clean_s"] = round(time.monotonic() - t0, 1)

    t0 = time.monotonic()
    contradicted = inject_contradiction(
        items, CONTRADICTION_RATE, CONTRADICTION_SEED)
    contra = score_naturalized(contradicted, predict_fn)
    contra["injection_rate"] = CONTRADICTION_RATE
    contra["injection_seed"] = CONTRADICTION_SEED
    contra["n_contradicted"] = sum(
        1 for it in contradicted if it["contradicted"])
    timings["naturalized_contradiction_s"] = round(time.monotonic() - t0, 1)

    t0 = time.monotonic()
    noised = []
    for item in items:
        new = dict(item)
        item_seed = (zlib.crc32(item["id"].encode()) ^ OCR_SEED) & 0xFFFFFFFF
        new["passage"] = ocr_noise(item["passage"], OCR_RATE, item_seed)
        noised.append(new)
    ocr = score_naturalized(noised, predict_fn)
    ocr["ocr_rate"] = OCR_RATE
    ocr["ocr_seed"] = OCR_SEED
    timings["naturalized_ocr_s"] = round(time.monotonic() - t0, 1)

    return {"clean": clean, "contradiction": contra, "ocr": ocr}


def evaluate_checkpoint(spec, args, tokenizer, nat_items, episodes,
                        components) -> dict:
    import torch

    from src.evals.heldout import run_heldout
    from src.evals.interactive import make_model_step_fn
    from src.evals.mc import load_checkpoint_model
    from src.evals.noise_axis import build_examples, run_noise_axis_interactive
    from src.evals.probes import PROBES, run_probes

    timings = {}
    t_start = time.monotonic()
    model, state = load_checkpoint_model(spec["ckpt"], args.device)
    step = int(state.get("step", -1))
    model_config = state["config"]["model"]
    del state
    timings["load_s"] = round(time.monotonic() - t_start, 1)

    step_fn = make_model_step_fn(model, args.device)
    result = {
        "meta": {
            "run_dir": spec["run_dir"],
            "checkpoint": spec["ckpt"],
            "step": step,
            "regime": spec["regime"],
            "train_seed": spec["seed"],
            "model_config": model_config,
            "device": args.device,
            "battery_args": {
                k: v for k, v in vars(args).items()
                if k not in ("combine", "checkpoints")},
        },
    }

    if "naturalized" in components:
        if spec["regime"] == "c":
            predict_fn = make_episode_predict_fn(
                step_fn, tokenizer, args.nat_max_new)
            elicitation = "episode_trace"
        else:
            predict_fn = make_prose_predict_fn(
                step_fn, tokenizer, args.nat_max_new)
            elicitation = "prose_continuation"
        result["naturalized"] = run_naturalized_block(
            nat_items, predict_fn, timings)
        result["naturalized"]["elicitation"] = elicitation

    if "probes" in components:
        t0 = time.monotonic()
        probes = PROBES[:args.probes_n] if args.probes_n > 0 else None
        result["probes"] = run_probes(
            model, tokenizer, args.device, probes=probes)
        timings["probes_s"] = round(time.monotonic() - t0, 1)

    if "heldout" in components:
        t0 = time.monotonic()
        use_retrieval = spec["regime"] == "c"
        result["heldout"] = run_heldout(
            model, tokenizer, episodes, args.device, seed=args.seed,
            use_retrieval=use_retrieval, max_rounds=args.max_rounds,
            max_new_tokens=args.heldout_max_new)
        timings["heldout_s"] = round(time.monotonic() - t0, 1)

    if "noise" in components and spec["regime"] == "c":
        t0 = time.monotonic()
        examples = build_examples(episodes[:args.noise_episodes])
        result["noise_axis"] = run_noise_axis_interactive(
            step_fn, tokenizer, examples, rates=args.noise_rates,
            seed=args.seed, max_rounds=args.max_rounds,
            max_new_tokens=args.noise_max_new)
        result["noise_axis"]["n_episodes"] = min(
            args.noise_episodes, len(episodes))
        timings["noise_axis_s"] = round(time.monotonic() - t0, 1)

    timings["total_s"] = round(time.monotonic() - t_start, 1)
    result["timings"] = timings

    del model
    if args.device.startswith("cuda"):
        torch.cuda.empty_cache()
    return result


def summarize(cp: dict) -> dict:
    """One prominent row per checkpoint for the combined results file."""
    meta = cp["meta"]
    row = {
        "name": f"killtest-{meta['regime']}-{meta['train_seed']}",
        "regime": meta["regime"],
        "train_seed": meta["train_seed"],
        "step": meta["step"],
    }
    nat = cp.get("naturalized")
    if nat:
        row["naturalized_elicitation"] = nat.get("elicitation")
        row["naturalized_contains"] = nat["clean"]["contains"]
        row["naturalized_em"] = nat["clean"]["em"]
        row["naturalized_contains_contradiction"] = \
            nat["contradiction"]["contains"]
        row["naturalized_contains_ocr"] = nat["ocr"]["contains"]
    probes = cp.get("probes")
    if probes:
        row["probes_accuracy"] = probes["accuracy"]
        row["probes_leakage_flag"] = probes["leakage_flag"]
    heldout = cp.get("heldout")
    if heldout:
        row["heldout_accuracy"] = heldout["accuracy"]
        row["heldout_mean_rounds"] = heldout.get("mean_rounds")
    noise = cp.get("noise_axis")
    if noise:
        row["noise_slope"] = round(noise["slope"], 4)
        row["noise_clean_accuracy"] = round(noise["clean_accuracy"], 4)
    return row


def combine(out_dir: Path, battery: dict) -> Path:
    parts = sorted(glob.glob(str(out_dir / "*.eval.json")))
    checkpoints = []
    for path in parts:
        with open(path) as fh:
            checkpoints.append(json.load(fh))
    checkpoints.sort(key=lambda c: (c["meta"]["regime"], c["meta"]["train_seed"]))
    combined = {
        "battery": battery,
        "summary": [summarize(cp) for cp in checkpoints],
        "checkpoints": checkpoints,
    }
    out_path = out_dir / "results.json"
    with open(out_path, "w") as fh:
        json.dump(combined, fh, indent=1)
        fh.write("\n")
    return out_path


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m scripts.eval_battery")
    parser.add_argument("--checkpoints", nargs="+", default=[],
                        help="run dirs (killtest-{a,c}-{seed}) or .pt files")
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--heldout", required=True,
                        help="held-out episodes jsonl")
    parser.add_argument("--out", required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--step", type=int, default=None,
                        help="pick ckpt-<step>.pt instead of the highest")
    parser.add_argument("--naturalized-n", type=int, default=0,
                        help="0 means the full suite")
    parser.add_argument("--probes-n", type=int, default=0,
                        help="0 means all probes")
    parser.add_argument("--heldout-episodes", type=int, default=500)
    parser.add_argument("--noise-episodes", type=int, default=200)
    parser.add_argument("--noise-rates", type=float, nargs="+",
                        default=[0.0, 0.1, 0.25, 0.5])
    parser.add_argument("--max-rounds", type=int, default=6)
    parser.add_argument("--nat-max-new", type=int, default=32)
    parser.add_argument("--heldout-max-new", type=int, default=64)
    parser.add_argument("--noise-max-new", type=int, default=128)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--components", default="naturalized,probes,heldout,noise",
                        help="comma-separated subset of "
                             "naturalized,probes,heldout,noise")
    parser.add_argument("--combine", action="store_true",
                        help="only merge per-checkpoint JSONs into results.json")
    parser.add_argument("--skip-existing", action="store_true",
                        help="skip checkpoints whose per-checkpoint JSON exists")
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    battery = {
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "args": {k: v for k, v in vars(args).items() if k != "combine"},
    }

    if args.combine:
        path = combine(out_dir, battery)
        print(f"combined {path}")
        return 0

    if not args.checkpoints:
        parser.error("--checkpoints is required unless --combine is given")

    components = {c.strip() for c in args.components.split(",") if c.strip()}
    known = {"naturalized", "probes", "heldout", "noise"}
    if not components or components - known:
        parser.error(f"--components must be a subset of {sorted(known)}")

    from src.evals.naturalized import load_suite
    from src.train.tokenizer import load_tokenizer

    tokenizer = load_tokenizer(args.tokenizer)
    nat_items = []
    if "naturalized" in components:
        suite = load_suite()
        nat_items = stratified_subset(suite["items"], args.naturalized_n)
    episodes = []
    if components & {"heldout", "noise"}:
        episodes = load_heldout_episodes(args.heldout, args.heldout_episodes)

    specs = []
    for path in args.checkpoints:
        regime, seed = parse_regime(path)
        ckpt = resolve_checkpoint(path, step=args.step)
        specs.append({"run_dir": str(path), "ckpt": ckpt,
                      "regime": regime, "seed": seed})

    for spec in specs:
        name = f"killtest-{spec['regime']}-{spec['seed']}"
        out_path = out_dir / f"{name}.eval.json"
        if args.skip_existing and out_path.exists():
            print(f"[{name}] exists, skipping")
            continue
        print(f"[{name}] evaluating {spec['ckpt']}", flush=True)
        result = evaluate_checkpoint(spec, args, tokenizer, nat_items,
                                     episodes, components)
        with open(out_path, "w") as fh:
            json.dump(result, fh, indent=1)
            fh.write("\n")
        bits = [f"[{name}] step {result['meta']['step']}"]
        if "naturalized" in result:
            nat = result["naturalized"]["clean"]
            bits.append(f"nat contains {nat['contains']:.4f} "
                        f"em {nat['em']:.4f} "
                        f"({result['naturalized']['elicitation']})")
        if "probes" in result:
            bits.append(f"probes {result['probes']['accuracy']:.4f} "
                        f"(leakage {result['probes']['leakage_flag']})")
        if "heldout" in result:
            bits.append(f"heldout {result['heldout']['accuracy']:.4f} "
                        f"rounds {result['heldout'].get('mean_rounds')}")
        bits.append(f"total {result['timings']['total_s']}s")
        print(" ".join(bits), flush=True)

    path = combine(out_dir, battery)
    print(f"combined {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
