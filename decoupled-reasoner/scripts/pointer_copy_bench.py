"""Two identical models on the same copy-heavy task, one with a pointer head.

This is the measurement that decides whether the 1B gets the head. The task is
the computation-free families of src/skillacq/simple.py, which is where the
failure was measured: a page states that a request of some invented type is
handled by the tutez desk, and the model that had read the page answered
"wrenbra desk". The system is regenerated per seed, so memorizing any
particular routing table has zero value across episodes, and the held-out
episodes are systems the model has never seen. Getting one right means having
read this episode's page.

Both arms are the same ModelConfig, the same seed, the same batches in the same
order, the same optimizer, the same budget. The pointer head's parameters are
drawn after every shared parameter, so the two models start from identical
values wherever they overlap. Both arms compute their logits only at the
supervised positions, so the compute difference between them is the head and
nothing else.

Reported per arm: held-out exact match on the answer span, held-out token
accuracy, and the step at which each accuracy threshold was first reached.

  uv run python scripts/pointer_copy_bench.py --device cuda:7 --out results/pointer
"""

import argparse
import json
import math
import time
from pathlib import Path

import torch

from src.train.model import ModelConfig, TransformerLM
from src.train.pointer_data import (IGNORE_INDEX, PointerCollator,
                                    build_examples, pointer_stats)
from src.train.tokenizer import load_tokenizer

COPY_FAMILIES = ["threshold_rule", "substitution_rule", "exception_rule"]
COMPUTE_FAMILIES = ["binary_op", "units", "procedure"]
THRESHOLDS = (0.25, 0.5, 0.75, 0.9)


def make_batches(examples, collator, batch_size: int, seed: int, device: str):
    """Collate once, shuffle deterministically, keep the tensors on the device."""
    order = torch.randperm(len(examples), generator=torch.Generator().manual_seed(seed))
    ordered = [examples[i] for i in order.tolist()]
    batches = []
    for start in range(0, len(ordered) - batch_size + 1, batch_size):
        batches.append(collator(ordered[start:start + batch_size]).to(device))
    return batches


def forward(model, batch, with_pointer: bool):
    kwargs = {"select": batch.authored_positions}
    if with_pointer:
        kwargs["evidence_positions"] = batch.evidence_positions
    return model(batch.input_ids, batch.authored_targets, **kwargs)


@torch.no_grad()
def evaluate(model, batches, with_pointer: bool) -> dict:
    """Teacher-forced token accuracy and exact match over the answer span.

    The closing <|eot|> is dropped from both, because every model gets it right
    immediately and including it would put a floor under a model that never
    answers anything.
    """
    model.eval()
    n_tokens = n_correct = n_examples = n_exact = 0
    total_loss = 0.0
    n_batches = 0
    for batch in batches:
        out, loss = forward(model, batch, with_pointer)
        predicted = out.argmax(dim=-1)
        targets = batch.authored_targets
        answer = torch.zeros_like(targets, dtype=torch.bool)
        for b, length in enumerate(batch.answer_lengths.tolist()):
            answer[b, :max(length - 1, 0)] = True  # every token but the <|eot|>
        answer &= targets != IGNORE_INDEX
        hit = (predicted == targets) & answer
        n_tokens += int(answer.sum())
        n_correct += int(hit.sum())
        per_row_ok = (hit.sum(1) == answer.sum(1)) & (answer.sum(1) > 0)
        n_exact += int(per_row_ok.sum())
        n_examples += int((answer.sum(1) > 0).sum())
        total_loss += float(loss)
        n_batches += 1
    model.train()
    return {
        "token_accuracy": n_correct / max(n_tokens, 1),
        "exact_match": n_exact / max(n_examples, 1),
        "loss": total_loss / max(n_batches, 1),
        "examples": n_examples,
    }


@torch.no_grad()
def gate_report(model, batches, limit: int = 4) -> dict:
    """What the gate is doing on held-out answers, for the pointer arm."""
    from src.train.pointer import copy_fraction

    model.eval()
    gates, copied = [], []
    for batch in batches[:limit]:
        out, _ = model.pointer_forward(
            batch.input_ids, batch.authored_targets,
            evidence_positions=batch.evidence_positions,
            select=batch.authored_positions,
        )
        gates.append(float(out.gate.mean()))
        share = copy_fraction(out, batch.authored_targets)
        if not math.isnan(share):
            copied.append(share)
    model.train()
    return {
        "mean_gate": sum(gates) / max(len(gates), 1),
        "copy_share_of_target_probability": sum(copied) / max(len(copied), 1) if copied else None,
    }


def lr_at(step: int, total: int, peak: float, warmup: int, floor_ratio: float = 0.1) -> float:
    if step < warmup:
        return peak * (step + 1) / warmup
    progress = (step - warmup) / max(total - warmup, 1)
    cosine = 0.5 * (1 + math.cos(math.pi * min(progress, 1.0)))
    return peak * (floor_ratio + (1 - floor_ratio) * cosine)


def train_arm(with_pointer: bool, cfg: ModelConfig, train_batches, eval_batches,
              steps: int, lr: float, warmup: int, seed: int, device: str,
              eval_every: int, amp: bool) -> dict:
    torch.manual_seed(seed)
    model = TransformerLM(cfg if not with_pointer else
                          ModelConfig(**{**cfg.__dict__, "pointer": {}})).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01,
                                  betas=(0.9, 0.95))
    reached = {}
    history = []
    started = time.time()
    for step in range(steps):
        for group in optimizer.param_groups:
            group["lr"] = lr_at(step, steps, lr, warmup)
        batch = train_batches[step % len(train_batches)]
        with torch.autocast(device_type=device.split(":")[0], dtype=torch.bfloat16,
                            enabled=amp):
            _, loss = forward(model, batch, with_pointer)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if (step + 1) % eval_every == 0 or step + 1 == steps:
            scores = evaluate(model, eval_batches, with_pointer)
            scores["step"] = step + 1
            scores["train_loss"] = float(loss.detach())
            history.append(scores)
            for threshold in THRESHOLDS:
                key = f"{threshold}"
                if key not in reached and scores["exact_match"] >= threshold:
                    reached[key] = step + 1
            print(f"    [{'pointer' if with_pointer else 'plain  '}] step {step + 1:5d} "
                  f"train {scores['train_loss']:.4f} held-out {scores['loss']:.4f} "
                  f"em {scores['exact_match']:.3f} tok {scores['token_accuracy']:.3f}",
                  flush=True)
    final = history[-1]
    out = {
        "with_pointer": with_pointer,
        "steps": steps,
        "params_total": model.num_params(non_embedding=False),
        "params_non_embedding": model.num_params(),
        "steps_to_exact_match": reached,
        "final": final,
        "best_exact_match": max(h["exact_match"] for h in history),
        "wall_seconds": time.time() - started,
        "history": history,
    }
    if with_pointer:
        out["gate"] = gate_report(model, eval_batches)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda:7")
    parser.add_argument("--tokenizer", default=None)
    parser.add_argument("--families", default="copy", choices=["copy", "compute"])
    parser.add_argument("--train-seeds", type=int, default=600)
    parser.add_argument("--eval-seeds", type=int, default=96)
    parser.add_argument("--n-problems", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--eval-every", type=int, default=200)
    parser.add_argument("--lr", type=float, default=6e-4)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--d-model", type=int, default=384)
    parser.add_argument("--n-layers", type=int, default=6)
    parser.add_argument("--n-heads", type=int, default=6)
    parser.add_argument("--max-seq-len", type=int, default=512)
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--out", default="results/pointer")
    args = parser.parse_args(argv)

    from src.train.tests.pointer_fixtures import find_tokenizer

    path = args.tokenizer or find_tokenizer()
    if path is None:
        raise SystemExit("no tokenizer; pass --tokenizer or set TOKENIZER_JSON")
    tokenizer = load_tokenizer(str(path))
    families = COPY_FAMILIES if args.families == "copy" else COMPUTE_FAMILIES

    collator = PointerCollator(tokenizer, max_seq_len=args.max_seq_len)
    train_examples = build_examples(tokenizer, range(args.train_seeds), families=families,
                                    n_problems=args.n_problems)
    # Held-out seeds are a disjoint range, so every evaluation episode is a
    # system the model has never been shown under any question.
    eval_examples = build_examples(tokenizer, range(10 ** 6, 10 ** 6 + args.eval_seeds),
                                   families=families, n_problems=args.n_problems)
    stats = {"train": pointer_stats(train_examples, collator),
             "held_out": pointer_stats(eval_examples, collator)}
    print(json.dumps(stats, indent=2), flush=True)

    train_batches = make_batches(train_examples, collator, args.batch_size,
                                 args.seed, args.device)
    eval_batches = make_batches(eval_examples, collator, args.batch_size,
                                args.seed + 1, args.device)
    print(f"  {len(train_batches)} training batches, {len(eval_batches)} held-out batches",
          flush=True)

    cfg = ModelConfig(
        vocab_size=tokenizer.vocab_size, d_model=args.d_model, n_layers=args.n_layers,
        n_heads=args.n_heads, d_ff=args.d_model * 8 // 3 // 64 * 64,
        max_seq_len=args.max_seq_len,
    )
    shared = dict(cfg=cfg, train_batches=train_batches, eval_batches=eval_batches,
                  steps=args.steps, lr=args.lr, warmup=args.warmup, seed=args.seed,
                  device=args.device, eval_every=args.eval_every, amp=not args.no_amp)
    result = {
        "config": vars(args),
        "model_config": {k: v for k, v in cfg.__dict__.items() if k != "recurrent"},
        "data": stats,
        "pointer": train_arm(True, **shared),
        "plain": train_arm(False, **shared),
    }
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"copy_bench_{args.families}_seed{args.seed}.json"
    (out_dir / name).write_text(json.dumps(result, indent=2))

    print("\n=== result ===")
    for arm in ("pointer", "plain"):
        r = result[arm]
        print(f"  {arm:8s} params {r['params_total']:,} "
              f"final em {r['final']['exact_match']:.3f} "
              f"best em {r['best_exact_match']:.3f} "
              f"token acc {r['final']['token_accuracy']:.3f} "
              f"held-out loss {r['final']['loss']:.4f} "
              f"steps to em {r['steps_to_exact_match']} "
              f"({r['wall_seconds']:.0f}s)")
    if "gate" in result["pointer"]:
        print(f"  gate: {result['pointer']['gate']}")
    print(f"  wrote {out_dir / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
