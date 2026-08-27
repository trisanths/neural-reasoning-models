"""The command line path, end to end on cpu with a tiny policy."""

import json

import yaml

from src.rl.cli import main


def test_cli_runs_steps_and_writes_logs(tiny_ckpt, tok, episodes_jsonl,
                                        tmp_path, tmp_path_factory):
    tok_path = tmp_path / "tokenizer.json"
    tok.save(str(tok_path))
    cfg = {
        "env": {"max_rounds": 2, "max_new_tokens": 24, "query_max_tokens": 8,
                "max_len": 448},
        "grpo": {"group_size": 2, "prompts_per_step": 1, "micro_batch_size": 2,
                 "lr": 1e-4, "warmup_steps": 0, "max_steps": 2,
                 "min_lr_ratio": 1.0, "kl_coef": 0.02,
                 "drop_zero_variance_groups": False, "seed": 3},
        "tasks": {"questions_per_episode": 1, "max_prompt_tokens": 224},
        "run": {"temperature": 1.0, "eval_tasks": 2, "eval_batch": 2,
                "eval_every": 2, "sample_every": 1, "sample_n": 2,
                "ckpt_every": 2, "log_every": 1},
    }
    cfg_path = tmp_path / "rl.yaml"
    with open(cfg_path, "w") as fh:
        yaml.safe_dump(cfg, fh)

    out = tmp_path / "run"
    rc = main(["--init-checkpoint", tiny_ckpt, "--config", str(cfg_path),
               "--episodes-jsonl", episodes_jsonl, "--out", str(out),
               "--tokenizer", str(tok_path), "--device", "cpu"])
    assert rc == 0

    records = [json.loads(l) for l in open(out / "rl.jsonl")]
    assert len(records) == 2
    for r in records:
        assert {"reward_mean", "accuracy", "mean_rounds", "mean_query_len",
                "kl", "rollouts_per_s"} <= set(r)
    evals = [json.loads(l) for l in open(out / "eval.jsonl")]
    assert [e["tag"] for e in evals][0] == "before"
    assert (out / "final.pt").exists()
    assert (out / "latest.pt").exists()
    samples = [json.loads(l) for l in open(out / "samples-000001.jsonl")]
    assert samples and "question" in samples[0] and "text" in samples[0]

    # Resuming continues rather than restarting.
    rc = main(["--init-checkpoint", tiny_ckpt, "--config", str(cfg_path),
               "--episodes-jsonl", episodes_jsonl, "--out", str(out),
               "--tokenizer", str(tok_path), "--device", "cpu",
               "--resume", "--steps", "3"])
    assert rc == 0
    records = [json.loads(l) for l in open(out / "rl.jsonl")]
    assert records[-1]["step"] == 3
