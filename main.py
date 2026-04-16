"""Entry point for the latent-space translation pipeline.

Usage:
    python main.py train           # Train adapters on GSM8K
    python main.py eval            # Evaluate pipeline + baselines
    python main.py eval --baselines-only  # Only run baselines
    python main.py probe           # Run Procrustes init only (debug)
"""

import argparse
import sys
import os
import torch
from dataclasses import fields

from config import PipelineConfig, TrainingConfig, QWEN_05B_CONFIG, QWEN_3B_CONFIG, resolve_module
from models.adapters import (
    AdapterPair,
    collect_activations,
    initialize_adapters_procrustes,
)
from models.pipeline import LatentTranslationPipeline
from data.gsm8k import GSM8KDataset, get_probe_texts
from eval.evaluate import run_all_evaluations, evaluate_pipeline
from training.train import train


def load_models(config: PipelineConfig):
    """Load both Qwen models and their tokenizers."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[init] Loading small model: {config.small_model.name}")
    print(f"[init] Loading large model: {config.large_model.name}")

    load_kwargs = {
        "dtype": getattr(torch, config.dtype),
        "device_map": config.device,
    }

    if config.use_8bit:
        try:
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_8bit=True,
            )
            # device_map must be "auto" for 8-bit
            load_kwargs["device_map"] = "auto"
            print("[init] Using 8-bit quantization")
        except ImportError:
            print("[init] WARNING: bitsandbytes not available, falling back to float16")

    tokenizer_small = AutoTokenizer.from_pretrained(config.small_model.name)
    tokenizer_large = AutoTokenizer.from_pretrained(config.large_model.name)

    # Ensure pad tokens are set
    if tokenizer_small.pad_token is None:
        tokenizer_small.pad_token = tokenizer_small.eos_token
    if tokenizer_large.pad_token is None:
        tokenizer_large.pad_token = tokenizer_large.eos_token

    model_small = AutoModelForCausalLM.from_pretrained(
        config.small_model.name, **load_kwargs
    )
    model_large = AutoModelForCausalLM.from_pretrained(
        config.large_model.name, **load_kwargs
    )

    model_small.eval()
    model_large.eval()

    print(f"[init] Small model device: {next(model_small.parameters()).device}")
    print(f"[init] Large model device: {next(model_large.parameters()).device}")

    return model_small, model_large, tokenizer_small, tokenizer_large


def init_adapters(
    config: PipelineConfig,
    training_config: TrainingConfig,
    model_small,
    model_large,
    tokenizer_small,
    tokenizer_large,
) -> AdapterPair:
    """Initialize the adapter pair with Procrustes alignment."""
    adapter_pair = AdapterPair(
        small_dim=config.small_model.hidden_dim,
        large_dim=config.large_model.hidden_dim,
    )

    print(f"[init] Collecting activations for Procrustes init "
          f"({training_config.procrustes_num_samples} samples)...")

    probe_texts = get_probe_texts(training_config.procrustes_num_samples)

    # Get the layer modules for activation collection
    small_layer_idx = config.small_extract_layer - 1
    small_layer = resolve_module(
        model_small, config.small_model.layer_template.format(i=small_layer_idx)
    )
    large_layer_idx = config.large_inject_layer - 1
    large_layer = resolve_module(
        model_large, config.large_model.layer_template.format(i=large_layer_idx)
    )

    h_small = collect_activations(model_small, tokenizer_small, probe_texts, small_layer)
    h_large = collect_activations(model_large, tokenizer_large, probe_texts, large_layer)

    initialize_adapters_procrustes(adapter_pair, h_small, h_large)

    adapter_pair = adapter_pair.to(config.device)
    print(f"[init] Adapter parameters: "
          f"{sum(p.numel() for p in adapter_pair.parameters()):,}")

    return adapter_pair


def cmd_train(args, pipeline_config: PipelineConfig, training_config: TrainingConfig):
    """Train the adapters."""
    model_small, model_large, tok_small, tok_large = load_models(pipeline_config)

    adapter_pair = init_adapters(
        pipeline_config, training_config,
        model_small, model_large, tok_small, tok_large,
    )

    pipeline = LatentTranslationPipeline(
        small_model=model_small,
        large_model=model_large,
        small_tokenizer=tok_small,
        large_tokenizer=tok_large,
        adapter_pair=adapter_pair,
        config=pipeline_config,
    )

    print("[data] Loading GSM8K train split...")
    train_dataset = GSM8KDataset(
        "train", tok_small, tok_large, max_seq_len=training_config.max_seq_len
    )
    print(f"[data] Train: {len(train_dataset)} examples")

    print("[data] Loading GSM8K validation split...")
    val_dataset = GSM8KDataset(
        "val", tok_small, tok_large, max_seq_len=training_config.max_seq_len
    )
    print(f"[data] Val: {len(val_dataset)} examples")

    # Evaluation function passed to the training loop
    def eval_fn(pipeline, dataset):
        return evaluate_pipeline(pipeline, dataset, max_samples=100)

    train(
        pipeline=pipeline,
        adapter_pair=adapter_pair,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        pipeline_config=pipeline_config,
        training_config=training_config,
        eval_fn=eval_fn,
    )


def cmd_eval(args, pipeline_config: PipelineConfig, training_config: TrainingConfig):
    """Evaluate pipeline and baselines."""
    model_small, model_large, tok_small, tok_large = load_models(pipeline_config)

    print("[data] Loading GSM8K test split...")
    test_dataset = GSM8KDataset(
        "test", tok_small, tok_large, max_seq_len=training_config.max_seq_len,
    )
    print(f"[data] Test: {len(test_dataset)} examples")

    if args.baselines_only:
        from eval.evaluate import evaluate_single_model, evaluate_small_with_coconut

        print("\n--- Baselines only (no pipeline) ---")
        results = {}

        results["small_only"] = evaluate_single_model(
            model_small, tok_small, test_dataset,
            model_name="Qwen2.5-0.5B", max_samples=args.max_samples,
            device=pipeline_config.device,
        )
        results["large_only"] = evaluate_single_model(
            model_large, tok_large, test_dataset,
            model_name="Qwen2.5-3B", max_samples=args.max_samples,
            device=pipeline_config.device,
        )
        results["small_coconut"] = evaluate_small_with_coconut(
            model_small, tok_small, pipeline_config.small_model, test_dataset,
            num_iters=pipeline_config.coconut_num_iters,
            max_samples=args.max_samples,
            device=pipeline_config.device,
        )

        print("\nRESULTS:")
        for name, m in results.items():
            print(f"  {name:25s} {m['accuracy']:.4f} ({m['num_correct']}/{m['num_total']})")
        return

    # Full evaluation with pipeline
    adapter_pair = AdapterPair(
        small_dim=pipeline_config.small_model.hidden_dim,
        large_dim=pipeline_config.large_model.hidden_dim,
    ).to(pipeline_config.device)

    if args.checkpoint:
        print(f"[eval] Loading adapter checkpoint: {args.checkpoint}")
        adapter_pair.load_state_dict(torch.load(args.checkpoint, map_location=pipeline_config.device))
    else:
        print("[eval] WARNING: No checkpoint specified, using random adapter weights")

    pipeline = LatentTranslationPipeline(
        small_model=model_small,
        large_model=model_large,
        small_tokenizer=tok_small,
        large_tokenizer=tok_large,
        adapter_pair=adapter_pair,
        config=pipeline_config,
    )

    run_all_evaluations(
        pipeline, test_dataset, pipeline_config,
        max_samples=args.max_samples,
    )


def cmd_probe(args, pipeline_config: PipelineConfig, training_config: TrainingConfig):
    """Debug: run Procrustes init and print diagnostics."""
    model_small, model_large, tok_small, tok_large = load_models(pipeline_config)

    adapter_pair = init_adapters(
        pipeline_config, training_config,
        model_small, model_large, tok_small, tok_large,
    )

    # Test round-trip
    print("\n[probe] Testing round-trip consistency...")
    probe_texts = get_probe_texts(10)
    small_layer_idx = pipeline_config.small_extract_layer - 1
    small_layer = resolve_module(
        model_small,
        pipeline_config.small_model.layer_template.format(i=small_layer_idx),
    )
    h = collect_activations(model_small, tok_small, probe_texts, small_layer)
    h = h.to(pipeline_config.device)

    h_rt = adapter_pair.forward_l2s(adapter_pair.forward_s2l(h))
    mse = torch.nn.functional.mse_loss(h_rt, h).item()
    cos_sim = torch.nn.functional.cosine_similarity(
        h.flatten(), h_rt.flatten(), dim=0
    ).item()

    print(f"  Round-trip MSE: {mse:.6f}")
    print(f"  Round-trip cosine similarity: {cos_sim:.6f}")
    print(f"  Adapter S->L weight norm: {adapter_pair.small_to_large.linear.weight.norm():.4f}")
    print(f"  Adapter L->S weight norm: {adapter_pair.large_to_small.linear.weight.norm():.4f}")


def build_config_from_args(args) -> tuple:
    """Build config objects, applying any CLI overrides."""
    pipeline_config = PipelineConfig()
    training_config = TrainingConfig()

    # Apply CLI overrides
    if hasattr(args, "injection_mode") and args.injection_mode:
        pipeline_config.injection_mode = args.injection_mode
    if hasattr(args, "coconut_iters") and args.coconut_iters is not None:
        pipeline_config.coconut_num_iters = args.coconut_iters
    if hasattr(args, "coconut_full_loop") and args.coconut_full_loop:
        pipeline_config.coconut_full_loop = True
    if hasattr(args, "use_8bit") and args.use_8bit:
        pipeline_config.use_8bit = True
    if hasattr(args, "lr") and args.lr is not None:
        training_config.lr = args.lr
    if hasattr(args, "epochs") and args.epochs is not None:
        training_config.num_epochs = args.epochs
    if hasattr(args, "batch_size") and args.batch_size is not None:
        training_config.batch_size = args.batch_size
    if hasattr(args, "no_wandb") and args.no_wandb:
        training_config.use_wandb = False
    if hasattr(args, "lambda_answer") and args.lambda_answer is not None:
        training_config.lambda_answer = args.lambda_answer
    if hasattr(args, "lambda_cycle") and args.lambda_cycle is not None:
        training_config.lambda_cycle = args.lambda_cycle
    if hasattr(args, "lambda_align") and args.lambda_align is not None:
        training_config.lambda_align = args.lambda_align

    return pipeline_config, training_config


def main():
    parser = argparse.ArgumentParser(
        description="Latent-Space Translation: Cross-Model Reasoning Outsourcing"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Shared arguments
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--injection-mode", choices=["add", "replace"], default=None)
    shared.add_argument("--coconut-iters", type=int, default=None)
    shared.add_argument("--coconut-full-loop", action="store_true")
    shared.add_argument("--use-8bit", action="store_true")

    # Train
    train_parser = subparsers.add_parser("train", parents=[shared])
    train_parser.add_argument("--lr", type=float, default=None)
    train_parser.add_argument("--epochs", type=int, default=None)
    train_parser.add_argument("--batch-size", type=int, default=None)
    train_parser.add_argument("--no-wandb", action="store_true")
    train_parser.add_argument("--lambda-answer", type=float, default=None)
    train_parser.add_argument("--lambda-cycle", type=float, default=None)
    train_parser.add_argument("--lambda-align", type=float, default=None)

    # Eval
    eval_parser = subparsers.add_parser("eval", parents=[shared])
    eval_parser.add_argument("--checkpoint", type=str, default=None)
    eval_parser.add_argument("--baselines-only", action="store_true")
    eval_parser.add_argument("--max-samples", type=int, default=None)

    # Probe (debug)
    subparsers.add_parser("probe", parents=[shared])

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    pipeline_config, training_config = build_config_from_args(args)

    print(f"[main] Command: {args.command}")
    print(f"[main] Injection mode: {pipeline_config.injection_mode}")
    print(f"[main] Coconut iterations: {pipeline_config.coconut_num_iters}")
    print(f"[main] Coconut full loop: {pipeline_config.coconut_full_loop}")
    print(f"[main] 8-bit quantization: {pipeline_config.use_8bit}")

    if args.command == "train":
        cmd_train(args, pipeline_config, training_config)
    elif args.command == "eval":
        cmd_eval(args, pipeline_config, training_config)
    elif args.command == "probe":
        cmd_probe(args, pipeline_config, training_config)


if __name__ == "__main__":
    main()
