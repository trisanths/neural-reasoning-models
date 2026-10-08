"""Stage 0 on HuggingFace backbones: Coconut curriculum on real ProsQA.

Produces the floor and ceiling checkpoints the cross-model pipeline needs, e.g.

    python scripts/train_hf.py --model Qwen/Qwen2.5-1.5B --out runs/qwen1.5b
    python scripts/train_hf.py --model Qwen/Qwen2.5-7B   --out runs/qwen7b --lora 16

Full finetuning a 7B is unnecessary here and does not fit alongside the small
model later, so --lora adapts it instead. Only the adapter and the three marker
embeddings are saved.
"""

import argparse
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coconut import Coconut  # noqa: E402
from src.dataset import CurriculumConfig  # noqa: E402
from src.engine import (  # noqa: E402
    FINAL_STAGE,
    TrainConfig,
    evaluate,
    get_device,
    train_curriculum,
)
from src.hf_backbone import HFBackbone, HFTokenizerAdapter  # noqa: E402
from src.projectors import apply_lora  # noqa: E402
from src.benchmarks import load_benchmark  # noqa: E402
from src.prosqa import (  # noqa: E402
    ProsQAHFTokenizer,
    assert_tokenizer_compatible,
)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="HF model id")
    p.add_argument("--out", required=True)
    p.add_argument("--data", default="data_prosqa")
    p.add_argument("--benchmark", default="prosqa", choices=["prosqa", "gsm", "hotpot"])
    p.add_argument("--n_train", type=int, default=17886)
    p.add_argument("--n_val", type=int, default=300)
    p.add_argument("--n_test", type=int, default=500)
    p.add_argument("--epochs_per_stage", type=int, default=3)
    p.add_argument("--batch_size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--max_latent_stage", type=int, default=6)
    p.add_argument("--c_thought", type=int, default=1)
    p.add_argument("--lora", type=int, default=0, help="LoRA rank; 0 = full finetune")
    p.add_argument("--dtype", default="bfloat16")
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    torch.manual_seed(a.seed)
    os.makedirs(a.out, exist_ok=True)
    dev = get_device()
    dtype = getattr(torch, a.dtype)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    hf_tok = AutoTokenizer.from_pretrained(a.model)
    adapter = HFTokenizerAdapter(hf_tok)
    tok = ProsQAHFTokenizer(adapter)

    train_ex, val_ex, test_ex = load_benchmark(
        a.benchmark, a.data, a.n_train, a.n_val, a.n_test
    )

    # Refuse to train on a curriculum whose truncated chains do not tokenise the
    # same way as the full sequence; the damage would be silent.
    assert_tokenizer_compatible(tok, train_ex)

    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=dtype)
    model.resize_token_embeddings(len(hf_tok))
    backbone = HFBackbone(model, hf_tok).to(dev)

    if a.lora:
        params = apply_lora(backbone.model, rank=a.lora)
        # apply_lora only wraps nn.Linear. Qwen and Llama use it throughout, but
        # GPT-2 uses Conv1D, where only lm_head would be adapted and the run
        # would train almost nothing while appearing to work.
        n_adapted = len(params) // 2
        if n_adapted < backbone.cfg.n_layers:
            raise RuntimeError(
                f"LoRA adapted only {n_adapted} modules across "
                f"{backbone.cfg.n_layers} layers. This architecture likely does "
                "not use nn.Linear (GPT-2 uses Conv1D); use --lora 0, or extend "
                "apply_lora to cover its layer type."
            )
        # The marker embeddings are new and carry no pretrained meaning, so they
        # have to stay trainable even when the backbone is frozen.
        emb = backbone.model.get_input_embeddings().weight
        emb.requires_grad = True
        params = params + [emb]
    else:
        params = list(backbone.parameters())

    coco = Coconut(backbone)
    logf = open(os.path.join(a.out, "log.txt"), "a")

    def log(m: str) -> None:
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()

    n_train_p = sum(p_.numel() for p_ in params if p_.requires_grad)
    log(f"=== {a.model} on ProsQA  device={dev} dtype={a.dtype} ===")
    log(f"params total={backbone.n_params() / 1e9:.2f}B trainable={n_train_p / 1e6:.1f}M")
    log(f"train={len(train_ex)} val={len(val_ex)} test={len(test_ex)}")

    cur = CurriculumConfig(
        max_latent_stage=a.max_latent_stage,
        c_thought=a.c_thought,
        pad_latent_to_max=True,  # required: ProsQA chains vary from 3 to 6 steps
    )
    tc = TrainConfig(
        epochs_per_stage=a.epochs_per_stage, batch_size=a.batch_size, lr=a.lr
    )
    def save_ckpt(tag=""):
        state = (
            {k: v for k, v in backbone.model.state_dict().items()
             if k.endswith(".a") or k.endswith(".b") or "embed" in k}
            if a.lora
            else backbone.model.state_dict()
        )
        torch.save(
            {"model": state, "hf_model": a.model, "lora": a.lora, "args": vars(a)},
            os.path.join(a.out, "model.pt"),
        )

    stages = list(range(a.max_latent_stage + 1)) + [FINAL_STAGE]
    res = train_curriculum(
        coco, train_ex, val_ex, tok, cur, tc, dev, stages=stages, log=log,
        params=params, on_stage_end=lambda st: save_ckpt(str(st)),
    )

    metrics = evaluate(coco, test_ex, tok, cur, dev, stage=FINAL_STAGE, batch_size=16)
    log(f"TEST exact={metrics['exact']:.4f} concept={metrics['concept']:.4f}")

    state = (
        {k: v for k, v in backbone.model.state_dict().items()
         if k.endswith(".a") or k.endswith(".b") or "embed" in k}
        if a.lora
        else backbone.model.state_dict()
    )
    torch.save(
        {"model": state, "hf_model": a.model, "lora": a.lora, "args": vars(a)},
        os.path.join(a.out, "model.pt"),
    )
    with open(os.path.join(a.out, "metrics.json"), "w") as f:
        json.dump({"test": metrics, "train": res}, f, indent=2)
    log(f"saved -> {a.out}")


if __name__ == "__main__":
    main()
