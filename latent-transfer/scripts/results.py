"""Builds the final comparison table: accuracy against per-query inference FLOPs.

Rows are read from a manifest so controls sit in the same table as the headline
result -- the pipeline number only means something next to the small-model
floor, the big-model ceiling, and the two controls.
"""

import argparse
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coconut import Coconut  # noqa: E402
from src.data import load  # noqa: E402
from src.tasks import get_tokenizer  # noqa: E402
from src.dataset import CurriculumConfig  # noqa: E402
from src.engine import FINAL_STAGE, evaluate, get_device  # noqa: E402
from src.flops import Arch, coconut_flops, cot_flops, fmt, pipeline_flops  # noqa: E402
from src.model import ModelConfig, TinyLM  # noqa: E402
from src.pipeline import CrossModelPipeline  # noqa: E402
from src.projectors import Projector, apply_lora  # noqa: E402


def load_backbone(path, device, randomize=False):
    ck = torch.load(path, map_location="cpu", weights_only=False)
    m = TinyLM(ModelConfig(**ck["cfg"]))
    if not randomize:
        m.load_state_dict(ck["model"])
    return m.to(device), ck


def arch_of(m: TinyLM, vocab: int) -> Arch:
    return Arch(d_model=m.cfg.d_model, n_layers=m.cfg.n_layers, vocab_size=vocab)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--task", default="prosqa", choices=["prosqa", "compose"])
    p.add_argument("--data", default="data")
    p.add_argument("--out", default="runs/results.json")
    p.add_argument("--n_test", type=int, default=2000)
    p.add_argument("--max_latent_stage", type=int, default=5)
    a = p.parse_args()

    dev = get_device()
    tok = get_tokenizer(a.task)
    test_ex = load(f"{a.data}/test.json")[: a.n_test]
    cur = CurriculumConfig(max_latent_stage=a.max_latent_stage, c_thought=1)
    n_q = max(len(tok.encode(e.question)) for e in test_ex[:200])
    k = cur.max_latent_stage
    # Derived from the data so FLOPs stay correct across tasks.
    n_cot = max(
        sum(len(tok.encode(s)) for s in e.steps) for e in test_ex[:200]
    )
    n_dec = max(len(tok.encode(e.answer)) + 1 for e in test_ex[:200])  # +1 for <eos>

    with open(a.manifest) as f:
        manifest = json.load(f)

    rows = []
    for entry in manifest:
        name, kind = entry["name"], entry["kind"]
        if kind in ("coconut", "cot", "nocot"):
            model, _ = load_backbone(entry["ckpt"], dev)
            coco = Coconut(model)
            cfg = CurriculumConfig(
                max_latent_stage=a.max_latent_stage, c_thought=1,
                no_cot=(kind == "nocot"), cot_only=(kind == "cot"),
            )
            stage = FINAL_STAGE if kind == "coconut" else 0
            m = evaluate(coco, test_ex, tok, cfg, dev, stage=stage)
            ar = arch_of(model, len(tok))
            if kind == "coconut":
                fl = coconut_flops(ar, n_q, k, n_dec)
            elif kind == "cot":
                fl = cot_flops(ar, n_q, n_cot, n_dec)
            else:
                fl = cot_flops(ar, n_q, 0, n_dec)
            rows.append({
                "name": name, "exact": m["exact"], "concept": m["concept"],
                "flops": fl, "params": model.n_params(),
            })
            del model, coco
        elif kind == "pipeline":
            small, _ = load_backbone(entry["small_ckpt"], dev)
            big, _ = load_backbone(entry["big_ckpt"], dev, randomize=entry.get("random_big", False))
            ck = torch.load(entry["ckpt"], map_location="cpu", weights_only=False)
            pk = ck["args"].get("proj_kind", "mlp")
            rms = bool(ck["args"].get("rms_match", 1))
            d_s, d_b = small.cfg.d_model, big.cfg.d_model
            pu = Projector(d_s, d_b, kind=pk, rms_match=rms).to(dev)
            pd = Projector(d_b, d_s, kind=pk, rms_match=rms).to(dev)
            pu.load_state_dict(ck["proj_up"])
            pd.load_state_dict(ck["proj_down"])
            apply_lora(small, rank=ck["args"].get("lora_rank", 8))
            small.to(dev)
            small.load_state_dict(ck["small_lora"], strict=False)
            if ck["args"].get("lora_big", 0) and ck.get("big_lora"):
                apply_lora(big, rank=ck["args"]["lora_big"])
                big.to(dev)
                big.load_state_dict(ck["big_lora"], strict=False)
            n_msg = ck["args"].get("n_message", 0) or None
            pipe = CrossModelPipeline(
                small, big, pu, pd,
                add_positional_big=bool(ck["args"].get("add_positional_big", 1)),
                n_message=n_msg,
                tap_layer=(None if ck["args"].get("tap_layer", -1) < 0 else ck["args"]["tap_layer"]),
            ).to(dev)
            m = evaluate(pipe, test_ex, tok, cur, dev)
            fl = pipeline_flops(
                arch_of(small, len(tok)), arch_of(big, len(tok)), n_q, k, n_dec,
                n_message=n_msg,
            )
            rows.append({
                "name": name, "exact": m["exact"], "concept": m["concept"],
                "flops": fl["total"], "flops_breakdown": fl,
                "params": small.n_params() + big.n_params(),
            })
            del small, big, pipe
        if dev.type == "mps":
            torch.mps.empty_cache()
        print(f"  scored {name}: concept={rows[-1]['concept']:.4f}", flush=True)

    base = min(r["flops"] for r in rows)
    print()
    print(f"{'configuration':<34} {'exact':>7} {'concept':>8} {'FLOPs/query':>12} {'rel':>7}")
    print("-" * 72)
    for r in rows:
        print(f"{r['name']:<34} {r['exact']:>7.3f} {r['concept']:>8.3f} "
              f"{fmt(r['flops']):>12} {r['flops'] / base:>6.1f}x")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as f:
        json.dump({"rows": rows, "n_question": n_q, "k_latent": k}, f, indent=2)
    print(f"\nsaved -> {a.out}")


if __name__ == "__main__":
    main()
