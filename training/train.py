"""Training loop for the latent-space translation adapters.

Trains only the adapter parameters (both models frozen).  Supports:
  - AdamW with linear warmup + cosine decay
  - Gradient clipping
  - Separate loss component logging (wandb or print)
  - Periodic checkpoint saving
  - Periodic evaluation on GSM8K test set
"""

import os
import sys
import math

# Ensure project root is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
from typing import Optional

from config import PipelineConfig, TrainingConfig, resolve_module
from models.pipeline import LatentTranslationPipeline
from models.adapters import AdapterPair
from models.hooks import NativeHiddenCapture
from training.losses import CombinedLoss
from data.gsm8k import GSM8KDataset, GSM8KCollator, get_probe_texts


def get_cosine_schedule_with_warmup(
    optimizer, num_warmup_steps: int, num_training_steps: int
) -> LambdaLR:
    """Linear warmup for ``num_warmup_steps``, then cosine decay to 0."""

    def lr_lambda(current_step: int) -> float:
        if current_step < num_warmup_steps:
            return current_step / max(1, num_warmup_steps)
        progress = (current_step - num_warmup_steps) / max(
            1, num_training_steps - num_warmup_steps
        )
        return max(0.0, 0.5 * (1.0 + math.cos(math.pi * progress)))

    return LambdaLR(optimizer, lr_lambda)


def compute_native_hidden_states(
    large_model: nn.Module,
    large_tokenizer,
    large_config,
    inject_layer: int,
    texts: list[str],
    device: str,
) -> torch.Tensor:
    """Run the large model on probe texts and capture its native hidden state
    at the injection layer.  Used for the alignment loss.

    Returns: (n_texts, hidden_dim) mean-pooled hidden states.
    """
    layer_idx = inject_layer - 1  # 0-based
    layer_module = resolve_module(
        large_model, large_config.layer_template.format(i=layer_idx)
    )
    capture = NativeHiddenCapture().register(layer_module)

    states = []
    large_model.eval()
    with torch.no_grad():
        for text in texts:
            messages = [{"role": "user", "content": text}]
            inputs = large_tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(device)

            large_model(**inputs)
            h = capture.get().float().mean(dim=1).squeeze(0)  # (hidden_dim,)
            states.append(h)

    capture.remove()
    return torch.stack(states)  # (n_texts, hidden_dim)


def train(
    pipeline: LatentTranslationPipeline,
    adapter_pair: AdapterPair,
    train_dataset: GSM8KDataset,
    val_dataset: GSM8KDataset,
    pipeline_config: PipelineConfig,
    training_config: TrainingConfig,
    eval_fn=None,
):
    """Main training loop."""

    # ── Logging setup ────────────────────────────────────────────────────────
    wandb_run = None
    if training_config.use_wandb:
        try:
            import wandb
            wandb_run = wandb.init(
                project=training_config.wandb_project,
                name=training_config.wandb_run_name,
                config={
                    "pipeline": vars(pipeline_config) if hasattr(pipeline_config, '__dict__') else str(pipeline_config),
                    "training": vars(training_config) if hasattr(training_config, '__dict__') else str(training_config),
                },
            )
        except ImportError:
            print("[train] wandb not available, logging to stdout")

    # ── Data loaders ─────────────────────────────────────────────────────────
    collator = GSM8KCollator(
        pad_token_id_small=pipeline.small_tokenizer.pad_token_id,
        pad_token_id_large=pipeline.large_tokenizer.pad_token_id,
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=training_config.batch_size,
        shuffle=True,
        collate_fn=collator,
        num_workers=training_config.num_workers,
        pin_memory=True,
    )

    # ── Optimizer & scheduler ────────────────────────────────────────────────
    optimizer = AdamW(
        adapter_pair.parameters(),
        lr=training_config.lr,
        weight_decay=training_config.weight_decay,
    )

    total_steps = (
        len(train_loader)
        // training_config.gradient_accumulation_steps
        * training_config.num_epochs
    )
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, training_config.warmup_steps, total_steps
    )

    # ── Loss function ────────────────────────────────────────────────────────
    loss_fn = CombinedLoss(
        lambda_answer=training_config.lambda_answer,
        lambda_cycle=training_config.lambda_cycle,
        lambda_align=training_config.lambda_align,
    )

    # ── Checkpoint directory ─────────────────────────────────────────────────
    os.makedirs(training_config.checkpoint_dir, exist_ok=True)

    device = pipeline_config.device
    global_step = 0

    # ── Training loop ────────────────────────────────────────────────────────
    for epoch in range(training_config.num_epochs):
        print(f"\n{'='*60}")
        print(f"Epoch {epoch + 1}/{training_config.num_epochs}")
        print(f"{'='*60}")

        # Compute native hidden states for alignment loss (once per epoch)
        probe_texts = get_probe_texts(training_config.procrustes_num_samples)
        h_native_large = compute_native_hidden_states(
            pipeline.large_model,
            pipeline.large_tokenizer,
            pipeline_config.large_model,
            pipeline_config.large_inject_layer,
            probe_texts[:32],  # Use a small subset per epoch for efficiency
            device,
        )

        adapter_pair.train()
        optimizer.zero_grad()
        epoch_losses = {"total": 0, "answer": 0, "cycle": 0, "align": 0}

        for step, batch in enumerate(train_loader):
            batch = {k: v.to(device) for k, v in batch.items()}

            # Forward pass through the pipeline
            outputs = pipeline(
                input_ids_small=batch["input_ids_small"],
                attention_mask_small=batch["attention_mask_small"],
                input_ids_large=batch["input_ids_large"],
                attention_mask_large=batch["attention_mask_large"],
                labels=batch["labels"],
            )

            # DESIGN DECISION: For the alignment loss, we use the mean-pooled
            # native hidden state computed on the probe set (above), not on the
            # current batch.  This is because the alignment loss is a regularizer
            # that keeps the adapter's output in a reasonable region of the large
            # model's space, not a per-example supervision signal.  Computing it
            # on the batch would require an extra large-model forward pass per step.
            #
            # We sample a small slice of the probe states to match batch size.
            batch_size = batch["input_ids_small"].shape[0]
            n_probe = h_native_large.shape[0]
            if batch_size > n_probe:
                raise ValueError(
                    f"batch_size ({batch_size}) exceeds probe set size ({n_probe}). "
                    "Reduce batch_size or increase probe_texts slice in train()."
                )
            probe_slice = h_native_large[:batch_size].unsqueeze(1)  # (B, 1, dim)
            # Expand to match translated state's seq dim
            seq_len = outputs["h_translated"].shape[1]
            probe_expanded = probe_slice.expand(-1, seq_len, -1)

            losses = loss_fn(
                logits=outputs["logits"],
                labels=batch["labels"],
                h_small=outputs["h_small"],
                adapter_pair=adapter_pair,
                h_translated=outputs["h_translated"],
                h_native_large=probe_expanded,
            )

            loss = losses["total"] / training_config.gradient_accumulation_steps
            loss.backward()

            # Track losses
            for k in epoch_losses:
                if k in losses:
                    epoch_losses[k] += losses[k].item()

            if (step + 1) % training_config.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(
                    adapter_pair.parameters(), training_config.grad_clip
                )
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1

                # ── Logging ──────────────────────────────────────────────
                if global_step % 10 == 0:
                    log_dict = {
                        "train/loss_total": losses["total"].item(),
                        "train/loss_answer": losses["answer"].item(),
                        "train/loss_cycle": losses["cycle"].item(),
                        "train/lr": scheduler.get_last_lr()[0],
                        "train/epoch": epoch + 1,
                        "train/step": global_step,
                    }
                    if "align" in losses:
                        log_dict["train/loss_align"] = losses["align"].item()

                    if wandb_run:
                        wandb_run.log(log_dict, step=global_step)
                    else:
                        print(
                            f"  step {global_step}: "
                            f"total={losses['total'].item():.4f} "
                            f"answer={losses['answer'].item():.4f} "
                            f"cycle={losses['cycle'].item():.4f} "
                            + (f"align={losses['align'].item():.4f}" if "align" in losses else "")
                        )

                # ── Checkpointing ────────────────────────────────────────
                if global_step % training_config.save_every_steps == 0:
                    ckpt_path = os.path.join(
                        training_config.checkpoint_dir,
                        f"adapter_step_{global_step}.pt",
                    )
                    torch.save(adapter_pair.state_dict(), ckpt_path)
                    print(f"  [checkpoint] Saved to {ckpt_path}")

                # ── Evaluation ───────────────────────────────────────────
                if (
                    global_step % training_config.eval_every_steps == 0
                    and eval_fn is not None
                ):
                    print(f"  [eval] Running evaluation at step {global_step}...")
                    metrics = eval_fn(pipeline, val_dataset)
                    if wandb_run:
                        wandb_run.log(
                            {f"eval/{k}": v for k, v in metrics.items()},
                            step=global_step,
                        )
                    else:
                        print(f"  [eval] {metrics}")

        # End-of-epoch summary
        n_steps = len(train_loader)
        print(
            f"  Epoch {epoch+1} avg losses: "
            f"total={epoch_losses['total']/n_steps:.4f} "
            f"answer={epoch_losses['answer']/n_steps:.4f} "
            f"cycle={epoch_losses['cycle']/n_steps:.4f} "
            f"align={epoch_losses['align']/n_steps:.4f}"
        )

    # ── Final save ───────────────────────────────────────────────────────────
    final_path = os.path.join(training_config.checkpoint_dir, "adapter_final.pt")
    torch.save(adapter_pair.state_dict(), final_path)
    print(f"\n[train] Training complete. Final checkpoint: {final_path}")

    if wandb_run:
        wandb_run.finish()
