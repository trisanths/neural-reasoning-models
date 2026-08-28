"""Command line entry point for the evidence cross-attention lane.

Usage:
  uv run python -m src.train.evidence_cli --config configs/350m-xattn.yaml \
      --tokenizer ~/data/tokenizer_v2.json --out RUNDIR [--web-episodes PATH] \
      [--resume] [--max-steps N] [--dry-run N]

This is the src/train/cli.py of the evidence lane. It differs in what it
reads: there is no shard directory, because an example is a question, a bank
of retrievable chunks, and an answer rather than a window of a token stream.
Worldgen episodes are generated inside the stream and scrubbed-web episodes
come from the file scripts/render_evidence_web.py pre-renders.

RESUME. The stream is a pure function of (seed, global example index), and
the index is start_step * grad_accum_steps * batch_size, so resuming at step
N replays exactly the examples the run would have reached. Nothing about the
data order lives in the checkpoint.

--dry-run builds N optimizer steps' worth of batches, prints the bank report
and the parameter breakdown, and exits without touching the optimizer. That
is the check bootstrap4.sh runs before the block opens.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import yaml

from src.train.evidence_data import EvidenceCollator
from src.train.evidence_model import EvidenceTransformerLM, config_from_yaml
from src.train.evidence_stream import EvidenceStream
from src.train.evidence_stream import config_from_yaml as stream_config_from_yaml
from src.train.evidence_stream import load_web_episodes
from src.train.evidence_trainer import EvidenceTrainer
from src.train.tokenizer import load_tokenizer


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="src.train.evidence_cli")
    parser.add_argument("--config", required=True, help="yaml config path")
    parser.add_argument("--tokenizer", required=True, help="tokenizer json path")
    parser.add_argument("--out", required=True, help="run directory")
    parser.add_argument("--web-episodes", default=None,
                        help="jsonl from scripts/render_evidence_web.py")
    parser.add_argument("--resume", action="store_true", help="resume from OUT/latest.pt")
    parser.add_argument("--device", default=None, help="cuda or cpu, default auto")
    parser.add_argument("--max-steps", type=int, default=None,
                        help="override schedule.max_steps")
    parser.add_argument("--dry-run", type=int, default=0,
                        help="build this many steps of batches and exit")
    return parser


def build_stream(cfg: dict, tokenizer, web_path: str | None):
    """Stream and collator for a loaded config."""
    data_cfg = dict(cfg.get("data") or {})
    data_cfg.setdefault("seed", int(cfg.get("train", {}).get("seed", 0)))
    stream_cfg = stream_config_from_yaml(data_cfg)
    if stream_cfg.web_share > 0 and not web_path:
        raise SystemExit(
            f"data.web_share is {stream_cfg.web_share} but --web-episodes was "
            "not given; pass the rendered file or set web_share to 0"
        )
    web = load_web_episodes(web_path) if stream_cfg.web_share > 0 else []
    stream = EvidenceStream(tokenizer, stream_cfg, web_episodes=web)
    collator = EvidenceCollator(
        tokenizer, stream_cfg.bank_size, stream_cfg.chunk_len,
        int(cfg["model"]["max_seq_len"]),
    )
    return stream, collator, stream_cfg


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    with open(args.config) as fh:
        cfg = yaml.safe_load(fh)
    if args.max_steps is not None:
        cfg["schedule"]["max_steps"] = args.max_steps

    tokenizer = load_tokenizer(args.tokenizer)
    model_cfg = config_from_yaml(cfg["model"])
    if model_cfg.vocab_size != tokenizer.vocab_size:
        raise SystemExit(
            f"config vocab_size {model_cfg.vocab_size} does not match the "
            f"tokenizer's {tokenizer.vocab_size}"
        )
    stream, collator, stream_cfg = build_stream(cfg, tokenizer, args.web_episodes)
    if stream_cfg.bank_size > model_cfg.max_chunks:
        raise SystemExit(
            f"data.bank_size {stream_cfg.bank_size} exceeds model.max_chunks "
            f"{model_cfg.max_chunks}"
        )
    if stream_cfg.chunk_len != model_cfg.chunk_len:
        raise SystemExit(
            f"data.chunk_len {stream_cfg.chunk_len} does not match "
            f"model.chunk_len {model_cfg.chunk_len}"
        )

    model = EvidenceTransformerLM(model_cfg)
    breakdown = model.param_breakdown()
    print("param breakdown " + json.dumps(breakdown))
    print(f"model params {breakdown['total']:,} "
          f"({breakdown['non_embedding']:,} non embedding)")
    print(f"bank {stream_cfg.bank_size} chunks of {stream_cfg.chunk_len} tokens "
          f"= {stream_cfg.bank_size * stream_cfg.chunk_len:,} evidence tokens per "
          f"sequence, mode {model_cfg.evidence_mode}, bank_mode {stream_cfg.bank_mode}, "
          f"web share {stream_cfg.web_share}")

    train_cfg = cfg["train"]
    batch_size = int(train_cfg["batch_size"])
    grad_accum = int(train_cfg.get("grad_accum_steps", 1))

    if args.dry_run:
        t0 = time.time()
        n = args.dry_run * grad_accum
        batches = []
        it = stream.batches(batch_size, collator, start=0)
        for _ in range(n):
            batches.append(next(it))
        seconds = time.time() - t0
        report = stream.bank_report(n=min(64, batch_size * n))
        print("bank report " + json.dumps(report))
        answer = sum(b.n_answer_tokens for b in batches)
        evidence = sum(b.n_evidence_tokens for b in batches)
        print(f"built {n} micro batches of {batch_size} in {seconds:.1f}s "
              f"({batch_size * n / seconds:.1f} examples/s), "
              f"{answer:,} answer tokens, {evidence:,} evidence tokens")
        print(f"working sequence width {batches[0].input_ids.shape[1]}, "
              f"evidence tensor {tuple(batches[0].evidence_ids.shape)}")
        print("DRY_RUN_OK")
        return 0

    trainer = EvidenceTrainer(model, cfg, args.out, device=args.device,
                              evidence_mode=model_cfg.evidence_mode)
    print(f"device {trainer.device}")
    if args.resume:
        latest = Path(args.out) / "latest.pt"
        if latest.exists():
            trainer.load_checkpoint(str(latest))
            print(f"resumed at step {trainer.step}")

    start_index = trainer.step * grad_accum * batch_size
    print(f"stream starts at global example {start_index:,} "
          f"(step {trainer.step} x accum {grad_accum} x micro {batch_size})")
    loader = stream.batches(batch_size, collator, start=start_index)
    trainer.train(loader)
    print(f"done at step {trainer.step}, "
          f"{trainer.tokens_seen:,} answer tokens, "
          f"{trainer.evidence_tokens_seen:,} evidence tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
