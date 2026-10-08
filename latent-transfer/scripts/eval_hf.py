"""Scores a saved HF checkpoint, overall and split by chain length.

Kept separate from training so a run can be re-scored without retraining, which
matters when the generation budget changes.

The per-hop breakdown is the important part. ProsQA is close to saturated for
small models on short chains, so an overall average can hide whether the big
model contributes anything. If a capacity gap exists it shows on the 5- and
6-step problems while the 3-step ones sit near ceiling for every model.
"""

import argparse
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coconut import Coconut  # noqa: E402
from src.dataset import CurriculumConfig  # noqa: E402
from src.engine import FINAL_STAGE, evaluate, get_device  # noqa: E402
from src.prosqa import ProsQAHFTokenizer, load_prosqa  # noqa: E402


def load_hf_checkpoint(path: str, device, randomize: bool = False):
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    from src.hf_backbone import HFBackbone, HFTokenizerAdapter
    from src.projectors import apply_lora

    ck = torch.load(path, map_location="cpu", weights_only=False)
    name = ck["hf_model"]
    dtype = getattr(torch, ck.get("args", {}).get("dtype", "bfloat16"))
    hf_tok = AutoTokenizer.from_pretrained(name)
    adapter = HFTokenizerAdapter(hf_tok)

    if randomize:
        model = AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(name)).to(dtype)
    else:
        model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype)
    model.resize_token_embeddings(len(hf_tok))
    if not randomize:
        if ck.get("lora"):
            apply_lora(model, rank=ck["lora"])
        _, unexpected = model.load_state_dict(ck["model"], strict=False)
        if unexpected:
            raise RuntimeError(f"checkpoint keys the model lacks: {unexpected[:5]}")
    return HFBackbone(model, hf_tok).to(device), ProsQAHFTokenizer(adapter), ck


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", required=True)
    p.add_argument("--data", default="data_prosqa")
    p.add_argument("--n_test", type=int, default=500)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--max_latent_stage", type=int, default=6)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    dev = get_device()
    model, tok, ck = load_hf_checkpoint(a.ckpt, dev)
    test = load_prosqa(f"{a.data}/prosqa_test.json", a.n_test)
    cur = CurriculumConfig(
        max_latent_stage=a.max_latent_stage, c_thought=1, pad_latent_to_max=True
    )
    coco = Coconut(model)

    overall = evaluate(
        coco, test, tok, cur, dev, stage=FINAL_STAGE, batch_size=a.batch_size
    )
    print(f"{ck['hf_model']}  n={len(test)}")
    print(f"  overall   exact={overall['exact']:.4f}  concept={overall['concept']:.4f}")

    by_hop = {}
    for h in sorted({len(e.steps) for e in test}):
        sub = [e for e in test if len(e.steps) == h]
        m = evaluate(coco, sub, tok, cur, dev, stage=FINAL_STAGE, batch_size=a.batch_size)
        by_hop[h] = {"n": len(sub), **m}
        print(f"  {h}-hop     exact={m['exact']:.4f}  concept={m['concept']:.4f}  (n={len(sub)})")

    if a.out:
        with open(a.out, "w") as f:
            json.dump({"ckpt": a.ckpt, "overall": overall, "by_hop": by_hop}, f, indent=2)
        print(f"saved -> {a.out}")


if __name__ == "__main__":
    main()
