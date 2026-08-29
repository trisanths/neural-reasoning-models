"""Correctness of the data parallel path.

The multi process tests run a real gloo process group over spawned processes
on cpu, so they check DistributedDataParallel, no_sync accumulation, the
logging all reduce and checkpoint compatibility without needing a GPU and
without touching one that another run owns.
"""

import json
import socket
from pathlib import Path

import numpy as np
import pytest
import torch
import torch.multiprocessing as mp
import yaml

from src.train.data import ArraySource, BatchLoader
from src.train.distributed import (
    BatchPlanError,
    add_ddp_prefix,
    resolve_batch_plan,
    strip_ddp_prefix,
)
from src.train.tests import ddp_workers as W

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "configs"


# ---------------- batch plan ----------------


def test_batch_plan_divides_the_global_batch_across_ranks():
    train_cfg = {"batch_size": 4, "grad_accum_steps": 16, "global_batch_size": 64}
    for world_size, expected_accum in ((1, 16), (2, 8), (4, 4), (8, 2), (16, 1)):
        plan = resolve_batch_plan(train_cfg, world_size)
        assert plan.grad_accum_steps == expected_accum
        assert plan.micro_batch_size == 4
        assert plan.global_batch_size == 64
        # The whole point: sequences per step do not grow with the world.
        assert plan.micro_batch_size * plan.grad_accum_steps * world_size == 64
        assert plan.tokens_per_step(4096) == 64 * 4096


def test_batch_plan_rejects_a_world_size_that_does_not_divide():
    train_cfg = {"batch_size": 4, "grad_accum_steps": 16, "global_batch_size": 64}
    with pytest.raises(BatchPlanError, match="not divisible"):
        resolve_batch_plan(train_cfg, 3)
    with pytest.raises(BatchPlanError, match="not divisible"):
        resolve_batch_plan(train_cfg, 32)


def test_batch_plan_rejects_a_config_that_contradicts_itself():
    train_cfg = {"batch_size": 4, "grad_accum_steps": 16, "global_batch_size": 128}
    with pytest.raises(BatchPlanError, match="inconsistent"):
        resolve_batch_plan(train_cfg, 1)


def test_batch_plan_falls_back_to_the_legacy_product():
    """A config written before global_batch_size existed states the same
    quantity as batch_size times grad_accum_steps at world size one."""
    train_cfg = {"batch_size": 8, "grad_accum_steps": 8}
    assert resolve_batch_plan(train_cfg, 1).global_batch_size == 64
    assert resolve_batch_plan(train_cfg, 4).grad_accum_steps == 2


def test_batch_plan_honours_an_explicit_accumulation():
    train_cfg = {"batch_size": 4, "grad_accum_steps": 16, "global_batch_size": 64}
    plan = resolve_batch_plan(train_cfg, 4, micro_batch_size=2, grad_accum_steps=3)
    assert (plan.micro_batch_size, plan.grad_accum_steps, plan.world_size) == (2, 3, 4)
    assert plan.global_batch_size == 24


PRETRAINING_CONFIGS = ["smoke.yaml", "150m.yaml", "350m.yaml", "350m-loop.yaml",
                       "700m.yaml", "1300m.yaml", "1b.yaml"]


@pytest.mark.parametrize(
    "name", sorted(p.name for p in CONFIG_DIR.glob("*.yaml")) if CONFIG_DIR.exists() else []
)
def test_shipped_configs_state_a_global_batch_that_splits(name):
    with open(CONFIG_DIR / name) as fh:
        cfg = yaml.safe_load(fh)
    train_cfg = cfg.get("train")
    if not train_cfg or "batch_size" not in train_cfg or "grad_accum_steps" not in train_cfg:
        pytest.skip(f"{name} has no train batch section")
    plan = resolve_batch_plan(train_cfg, 1)
    assert plan.global_batch_size == train_cfg["batch_size"] * train_cfg["grad_accum_steps"]
    # Every config has to survive the world sizes a single node can offer.
    for world_size in (1, 2, 4, 8):
        if plan.global_batch_size % (plan.micro_batch_size * world_size) == 0:
            split = resolve_batch_plan(train_cfg, world_size)
            assert split.global_batch_size == plan.global_batch_size
            assert (
                split.micro_batch_size * split.grad_accum_steps * world_size
                == plan.global_batch_size
            )


@pytest.mark.parametrize("name", PRETRAINING_CONFIGS)
def test_pretraining_configs_declare_the_global_batch(name):
    """The convention is documented where the numbers live, not only in code."""
    text = (CONFIG_DIR / name).read_text()
    assert "global_batch_size == batch_size * grad_accum_steps * world_size" in text
    train_cfg = yaml.safe_load(text)["train"]
    assert "global_batch_size" in train_cfg
    resolve_batch_plan(train_cfg, 1)


@pytest.mark.parametrize("name", [n for n in PRETRAINING_CONFIGS if n != "smoke.yaml"])
def test_pretraining_configs_split_to_eight_gpus(name):
    """smoke.yaml is a one GPU toy; everything else has to run on a full node
    without the tokens per step moving."""
    train_cfg = yaml.safe_load((CONFIG_DIR / name).read_text())["train"]
    for world_size in (1, 2, 4, 8):
        plan = resolve_batch_plan(train_cfg, world_size)
        assert plan.global_batch_size == train_cfg["global_batch_size"]
        assert plan.grad_accum_steps >= 1


# ---------------- rank sharding ----------------


def make_source(total=100_000, seed=3):
    tokens = np.random.default_rng(seed).integers(0, 500, size=total, dtype=np.uint16)
    return ArraySource(tokens)


def touched_tokens(loader, batches):
    """Every token index the loader can hand to the model over n batches."""
    seen = set()
    for _ in range(batches):
        starts = loader.region_start + loader.rng.integers(
            0, loader.high, size=loader.batch_size, endpoint=True
        )
        for start in starts:
            seen.update(range(int(start), int(start) + loader.seq_len + 1))
    return seen


def test_rank_regions_are_disjoint_and_cover_the_stream():
    source = make_source()
    world_size = 4
    loaders = [
        BatchLoader(source, 2, 64, seed=11, rank=r, world_size=world_size)
        for r in range(world_size)
    ]
    spans = [(ldr.region_start, ldr.region_end) for ldr in loaders]
    assert spans[0][0] == 0
    assert spans[-1][1] == source.total_tokens
    for (_, end), (start, _) in zip(spans, spans[1:]):
        assert end == start
    # Reachable tokens never cross a region boundary.
    for rank, loader in enumerate(loaders):
        seen = touched_tokens(loader, 400)
        assert min(seen) >= loader.region_start
        assert max(seen) < loader.region_end
        for other, other_loader in enumerate(loaders):
            if other == rank:
                continue
            assert not (
                loader.region_start < other_loader.region_end
                and other_loader.region_start < loader.region_end
            )


def test_rank_regions_reach_almost_every_token():
    source = make_source(total=20_000)
    world_size = 4
    seq_len = 64
    covered = set()
    for rank in range(world_size):
        loader = BatchLoader(source, 4, seq_len, seed=5, rank=rank, world_size=world_size)
        covered |= touched_tokens(loader, 3000)
    # Only the tail of each region is unreachable, because a start there would
    # run off the end of the region.
    assert len(covered) >= source.total_tokens - world_size * (seq_len + 1)


def test_rank_zero_of_a_world_of_one_draws_the_single_gpu_stream():
    """The offsets a lone process draws must not move, so single GPU runs and
    everything resumed from them are unaffected by rank sharding."""
    source = make_source(total=5000)
    loader = BatchLoader(source, 4, 64, seed=9)
    reference = np.random.default_rng(9)
    high = source.total_tokens - 64 - 1
    for _ in range(5):
        inputs, targets = loader.next_batch()
        starts = reference.integers(0, high, size=4, endpoint=True)
        rows = np.stack([source.get_slice(int(s), 65).astype(np.int64) for s in starts])
        expected = torch.from_numpy(rows)
        assert torch.equal(inputs, expected[:, :-1])
        assert torch.equal(targets, expected[:, 1:])


def test_ranks_of_the_same_world_draw_different_data():
    source = make_source(total=50_000)
    first = BatchLoader(source, 2, 64, seed=4, rank=0, world_size=2).next_batch()[0]
    second = BatchLoader(source, 2, 64, seed=4, rank=1, world_size=2).next_batch()[0]
    assert not torch.equal(first, second)


def test_loader_rejects_a_world_too_wide_for_the_data():
    source = make_source(total=1000)
    with pytest.raises(ValueError, match="shorter than one training sequence"):
        BatchLoader(source, 1, 64, seed=0, rank=0, world_size=100)


def test_skipping_matches_drawing_batch_by_batch():
    source = make_source(total=30_000)
    walked = BatchLoader(source, 3, 32, seed=17, rank=1, world_size=3)
    for _ in range(7):
        walked.next_batch()
    jumped = BatchLoader(source, 3, 32, seed=17, rank=1, world_size=3)
    jumped.skip(7)
    assert torch.equal(walked.next_batch()[0], jumped.next_batch()[0])
    assert walked.batches_drawn == jumped.batches_drawn


def test_loader_resumes_to_the_same_position():
    source = make_source(total=30_000)
    original = BatchLoader(source, 2, 32, seed=21, rank=2, world_size=4)
    for _ in range(11):
        original.next_batch()
    state = original.state_dict()
    assert state["batches_drawn"] == 11
    resumed = BatchLoader(source, 2, 32, seed=21, rank=2, world_size=4)
    resumed.load_state_dict(state)
    assert torch.equal(original.next_batch()[0], resumed.next_batch()[0])


# ---------------- checkpoint key prefixes ----------------


def test_ddp_prefix_helpers_round_trip():
    bare = {"tok_emb.weight": torch.zeros(2), "blocks.0.attn.wq.weight": torch.ones(2)}
    wrapped = add_ddp_prefix(bare)
    assert set(wrapped) == {"module.tok_emb.weight", "module.blocks.0.attn.wq.weight"}
    assert strip_ddp_prefix(wrapped).keys() == bare.keys()
    # Already bare, already wrapped: both are no ops.
    assert strip_ddp_prefix(bare) is bare
    assert add_ddp_prefix(wrapped) is wrapped


# ---------------- multi process ----------------


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def run_workers(fn, world_size, out_dir, *args):
    mp.spawn(
        fn,
        args=(world_size, free_port(), str(out_dir), *args),
        nprocs=world_size,
        join=True,
    )
    return [
        json.loads((Path(out_dir) / f"result-{rank}.json").read_text())
        for rank in range(world_size)
    ]


def reference_losses(out_dir, steps):
    """The same run with no process group anywhere in sight."""
    cfg = W.tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=steps)
    trainer = W.build_trainer(cfg, out_dir)
    loader = BatchLoader(
        ArraySource(W.token_stream()),
        trainer.plan.micro_batch_size,
        W.SEQ_LEN,
        seed=int(cfg["train"]["seed"]) + 1,
        rank=0,
        world_size=1,
    )
    return trainer.train(loader, save_at_end=False)


def test_world_size_one_is_identical_to_the_single_gpu_path(tmp_path):
    """Requirement: turning the distributed path on must not move a single
    process run by one bit."""
    steps = 6
    plain = reference_losses(tmp_path / "plain", steps)
    results = run_workers(W.loss_worker, 1, tmp_path / "dist", steps)
    assert results[0]["grad_accum_steps"] == 4
    assert len(plain) == steps
    assert [repr(x) for x in plain] == results[0]["losses"]


def test_no_sync_accumulation_matches_a_single_process(tmp_path):
    """Two ranks accumulating twice must land on the parameters one process
    accumulating four times lands on."""
    cfg = W.tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=1)
    single = W.build_trainer(cfg, tmp_path / "single")
    assert single.grad_accum_steps == 4
    single.train(W.fixed_batches(4, 1), until_step=1, save_at_end=False)
    reference = single.model.state_dict()

    results = run_workers(W.nosync_worker, 2, tmp_path / "pair")
    assert [r["grad_accum_steps"] for r in results] == [2, 2]
    for rank in range(2):
        got = torch.load(tmp_path / "pair" / f"params-{rank}.pt", map_location="cpu")
        assert got.keys() == reference.keys()
        for key, value in reference.items():
            assert torch.allclose(got[key], value, rtol=1e-5, atol=1e-6), key


def test_gradients_reduce_once_per_optimizer_step(tmp_path):
    """no_sync in one number: four micro batches must cost the same number of
    bucket reductions as one."""
    results = run_workers(W.comm_count_worker, 2, tmp_path / "counts")
    for result in results:
        counts = result["bucket_reductions"]
        assert counts["1"] > 0
        assert counts["4"] == counts["1"]


def test_checkpoint_written_by_ddp_loads_in_a_single_process(tmp_path):
    steps = 3
    results = run_workers(W.ckpt_write_worker, 2, tmp_path / "written", steps)
    assert [r["step"] for r in results] == [steps, steps]
    run_dir = tmp_path / "written" / "ddp_run"
    reference = torch.load(run_dir / "reference-params.pt", map_location="cpu")
    for name in ("ddp.pt", "latest.pt", "ddp-wrapped.pt"):
        cfg = W.tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=steps)
        single = W.build_trainer(cfg, tmp_path / f"reader-{name}")
        single.load_checkpoint(str(run_dir / name))
        assert single.step == steps
        loaded = single.model.state_dict()
        assert loaded.keys() == reference.keys()
        for key, value in reference.items():
            assert torch.equal(loaded[key], value), f"{name}:{key}"


def test_checkpoint_written_by_a_single_process_loads_in_ddp(tmp_path):
    steps = 3
    cfg = W.tiny_cfg(global_batch_size=4, micro_batch_size=1, max_steps=steps)
    run_dir = tmp_path / "single_run"
    single = W.build_trainer(cfg, run_dir)
    loader = BatchLoader(
        ArraySource(W.token_stream()), single.plan.micro_batch_size, W.SEQ_LEN,
        seed=int(cfg["train"]["seed"]) + 1, rank=0, world_size=1,
    )
    single.train(loader, save_at_end=False)
    single.save_checkpoint(name="single.pt", loader=loader)
    reference = single.model.state_dict()
    assert not any(key.startswith("module.") for key in reference)

    out_dir = tmp_path / "read"
    results = run_workers(W.ckpt_read_worker, 2, out_dir, str(run_dir / "single.pt"))
    assert [r["step"] for r in results] == [steps, steps]
    for rank in range(2):
        loaded = torch.load(out_dir / f"loaded-{rank}.pt", map_location="cpu")
        for key, value in reference.items():
            assert torch.equal(loaded[key], value), f"rank {rank} {key}"
