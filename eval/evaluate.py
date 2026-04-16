"""Evaluation harness for latent-space translation and baselines.

Evaluates exact-match accuracy on GSM8K final numerical answers.
Supports four configurations:
  1. Full pipeline (small -> large -> small)
  2. Small model only (0.5B)
  3. Large model only (3B)
  4. Small model with Coconut loop (no cross-model transfer)
"""

import re
import torch
import torch.nn as nn
from typing import Dict, Optional
from tqdm import tqdm

from config import PipelineConfig, ModelConfig, resolve_module
from models.pipeline import LatentTranslationPipeline
from data.gsm8k import GSM8KDataset, extract_answer


NUMBER_PATTERN = re.compile(r"[-+]?\d[\d,]*\.?\d*")


def extract_predicted_number(text: str) -> str:
    """Extract the numerical answer from generated text.

    Handles three formats:
    - GSM8K chain-of-thought: "#### 18"
    - Trained pipeline format: "The answer is 18"
    - Fallback: last number in the text
    """
    # GSM8K standard format (used by baseline instruct models)
    match = re.search(r"####\s*\$?([-\d,]+\.?\d*)", text)
    if match:
        return match.group(1).replace(",", "")

    # Trained pipeline format
    match = re.search(r"[Tt]he answer is\s*\$?([\d,]+\.?\d*)", text)
    if match:
        return match.group(1).replace(",", "")

    # Fallback: last number in the text
    numbers = NUMBER_PATTERN.findall(text)
    if numbers:
        return numbers[-1].replace(",", "")
    return ""


def evaluate_pipeline(
    pipeline: LatentTranslationPipeline,
    dataset: GSM8KDataset,
    max_samples: Optional[int] = None,
    max_new_tokens: int = 512,
) -> Dict[str, float]:
    """Evaluate the full cross-model pipeline on GSM8K.

    Returns dict with 'accuracy' and 'num_correct' / 'num_total'.
    """
    pipeline.eval()
    n = min(len(dataset), max_samples) if max_samples else len(dataset)
    correct = 0

    def build_large_ids(prompt_text: str, target_len: int):
        ids = pipeline.large_tokenizer.encode(prompt_text, add_special_tokens=False)
        if len(ids) < target_len:
            ids = ids + [pipeline.large_tokenizer.pad_token_id] * (target_len - len(ids))
        else:
            ids = ids[:target_len]
        tensor = torch.tensor([ids], device=pipeline.config.device)
        return tensor, torch.ones_like(tensor)

    for i in tqdm(range(n), desc="Evaluating pipeline"):
        gold = dataset.answers[i]
        question = dataset.questions[i]
        messages = [{"role": "user", "content": question}]
        prompt_small = pipeline.small_tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
        prompt_large = pipeline.large_tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
        ids_small = pipeline.small_tokenizer.encode(prompt_small, add_special_tokens=False)
        input_ids_small = torch.tensor([ids_small], device=pipeline.config.device)
        attn_small = torch.ones_like(input_ids_small)
        input_ids_large, attn_large = build_large_ids(prompt_large, input_ids_small.shape[1])

        with torch.no_grad():
            output_ids = pipeline.generate(
                input_ids_small, attn_small,
                input_ids_large, attn_large,
                max_new_tokens=max_new_tokens,
            )

        text = pipeline.small_tokenizer.decode(
            output_ids[0], skip_special_tokens=True
        )
        predicted = extract_predicted_number(text)

        if predicted == gold:
            correct += 1

    return {
        "accuracy": correct / max(n, 1),
        "num_correct": correct,
        "num_total": n,
    }


@torch.no_grad()
def evaluate_single_model(
    model: nn.Module,
    tokenizer,
    dataset: GSM8KDataset,
    model_name: str = "model",
    max_samples: Optional[int] = None,
    max_new_tokens: int = 512,
    device: str = "cuda",
) -> Dict[str, float]:
    """Evaluate a single model (baseline) on GSM8K.

    Works for both the small (0.5B) and large (3B) model baselines.
    """
    model.eval()
    n = min(len(dataset), max_samples) if max_samples else len(dataset)
    correct = 0

    for i in tqdm(range(n), desc=f"Evaluating {model_name}"):
        question = dataset.questions[i]
        gold = dataset.answers[i]

        messages = [{"role": "user", "content": question}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(device)

        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

        prompt_len = inputs["input_ids"].shape[-1]
        text = tokenizer.decode(output_ids[0][prompt_len:], skip_special_tokens=True)
        predicted = extract_predicted_number(text)

        if predicted == gold:
            correct += 1

    return {
        "accuracy": correct / max(n, 1),
        "num_correct": correct,
        "num_total": n,
    }


@torch.no_grad()
def evaluate_small_with_coconut(
    small_model: nn.Module,
    tokenizer,
    small_config: ModelConfig,
    dataset: GSM8KDataset,
    num_iters: int = 6,
    max_samples: Optional[int] = None,
    max_new_tokens: int = 512,
    device: str = "cuda",
) -> Dict[str, float]:
    """Evaluate the small model with a Coconut loop (no cross-model transfer).

    This baseline runs the Coconut continuous-thought loop entirely within the
    small model to isolate the contribution of the cross-model transfer.

    DESIGN DECISION: For this baseline, we run all 24 layers of the small model
    in the loop (not a tail subset), because there's no injection point — the
    model iterates on its own representation.  This matches the original Coconut
    paper where the full model is looped.
    """
    small_model.eval()
    embed = resolve_module(small_model, small_config.embed_path)
    lm_head = resolve_module(small_model, small_config.lm_head_path)
    backbone = small_model.model
    n = min(len(dataset), max_samples) if max_samples else len(dataset)
    correct = 0

    for i in tqdm(range(n), desc="Evaluating small+coconut"):
        question = dataset.questions[i]
        gold = dataset.answers[i]

        messages = [{"role": "user", "content": question}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(device)

        input_ids = inputs["input_ids"]
        h = embed(input_ids)

        # Initial pass through the frozen backbone.
        h = backbone(
            input_ids=input_ids,
            attention_mask=inputs["attention_mask"],
        ).last_hidden_state

        # Coconut loop: feed output back N times
        for _ in range(num_iters):
            h = backbone(
                inputs_embeds=h,
                attention_mask=inputs["attention_mask"],
            ).last_hidden_state

        logits = lm_head(h.to(lm_head.weight.dtype))

        # Greedy decode — track generated tokens separately to avoid decoding the prompt
        next_token = logits[0, -1].argmax().item()
        generated = [next_token]

        for _ in range(max_new_tokens - 1):
            if next_token == tokenizer.eos_token_id:
                break
            new_embed = embed(torch.tensor([[next_token]], device=device))
            h = torch.cat([h, new_embed], dim=1)
            attn = torch.ones(h.shape[:2], dtype=torch.long, device=device)
            h = backbone(inputs_embeds=h, attention_mask=attn).last_hidden_state
            next_logits = lm_head(h[:, -1:, :].to(lm_head.weight.dtype))
            next_token = next_logits[0, -1].argmax().item()
            generated.append(next_token)

        text = tokenizer.decode(generated, skip_special_tokens=True)
        predicted = extract_predicted_number(text)

        if predicted == gold:
            correct += 1

    return {
        "accuracy": correct / max(n, 1),
        "num_correct": correct,
        "num_total": n,
    }


def run_all_evaluations(
    pipeline: LatentTranslationPipeline,
    test_dataset: GSM8KDataset,
    pipeline_config: PipelineConfig,
    max_samples: Optional[int] = None,
) -> Dict[str, Dict[str, float]]:
    """Run all evaluations: pipeline + three baselines.

    Returns a dict mapping evaluation name to metrics dict.
    """
    results = {}
    device = pipeline_config.device

    print("\n" + "=" * 60)
    print("EVALUATION: Full Pipeline (Small -> Large -> Small)")
    print("=" * 60)
    results["pipeline"] = evaluate_pipeline(
        pipeline, test_dataset, max_samples=max_samples
    )
    print(f"  Accuracy: {results['pipeline']['accuracy']:.4f}")

    print("\n" + "=" * 60)
    print("BASELINE 1: Small Model Only (0.5B)")
    print("=" * 60)
    results["small_only"] = evaluate_single_model(
        pipeline.small_model,
        pipeline.small_tokenizer,
        test_dataset,
        model_name="Qwen2.5-0.5B",
        max_samples=max_samples,
        device=device,
    )
    print(f"  Accuracy: {results['small_only']['accuracy']:.4f}")

    print("\n" + "=" * 60)
    print("BASELINE 2: Large Model Only (3B)")
    print("=" * 60)
    results["large_only"] = evaluate_single_model(
        pipeline.large_model,
        pipeline.large_tokenizer,
        test_dataset,
        model_name="Qwen2.5-3B",
        max_samples=max_samples,
        device=device,
    )
    print(f"  Accuracy: {results['large_only']['accuracy']:.4f}")

    print("\n" + "=" * 60)
    print("BASELINE 3: Small Model + Coconut Loop (no cross-model)")
    print("=" * 60)
    results["small_coconut"] = evaluate_small_with_coconut(
        pipeline.small_model,
        pipeline.small_tokenizer,
        pipeline_config.small_model,
        test_dataset,
        num_iters=pipeline_config.coconut_num_iters,
        max_samples=max_samples,
        device=device,
    )
    print(f"  Accuracy: {results['small_coconut']['accuracy']:.4f}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, metrics in results.items():
        print(f"  {name:25s} {metrics['accuracy']:.4f} "
              f"({metrics['num_correct']}/{metrics['num_total']})")

    return results
