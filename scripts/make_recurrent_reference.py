"""Build the bit identity references for depth recurrence.

Both references are produced by the pre recurrence model.py, taken straight out
of git, so they are a genuine "old code" artifact rather than something the new
code wrote about itself. src/train/tests/test_recurrent.py then loads them with
the new model.py, recurrence disabled, and demands bit identical logits.

  uv run python scripts/make_recurrent_reference.py --ref-rev HEAD

Writes src/train/tests/data/ref_disabled_tiny.pt (small, lives in the repo) and,
with --with-350m, a full 350m checkpoint under the path given by --large-out,
which is about 1.5 GiB and is not meant to be committed.
"""

import argparse
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

import torch
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

TINY = {
    "vocab_size": 256,
    "d_model": 64,
    "n_layers": 3,
    "n_heads": 4,
    "d_ff": 176,
    "max_seq_len": 64,
}
TINY_SEED = 1234
TINY_INPUT_SEED = 99
LARGE_SEED = 4321
LARGE_INPUT_SEED = 77


def load_reference_module(rev: str):
    """Import the model.py of a git revision under its own module name."""
    source = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{rev}:src/train/model.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    tmp = Path(tempfile.mkdtemp()) / "model_reference.py"
    tmp.write_text(source)
    spec = importlib.util.spec_from_file_location("model_reference", tmp)
    module = importlib.util.module_from_spec(spec)
    sys.modules["model_reference"] = module
    spec.loader.exec_module(module)
    return module


def build_reference(module, model_cfg: dict, seed: int, input_seed: int, batch, seq_len: int):
    torch.manual_seed(seed)
    model = module.TransformerLM(module.ModelConfig(**model_cfg))
    model.eval()
    gen = torch.Generator().manual_seed(input_seed)
    idx = torch.randint(0, model_cfg["vocab_size"], (batch, seq_len), generator=gen)
    with torch.no_grad():
        logits, _ = model(idx)
    return {
        "model_config": model_cfg,
        "seed": seed,
        "input_seed": input_seed,
        "input": idx,
        "logits": logits,
        "state_dict": model.state_dict(),
        "params_total": sum(p.numel() for p in model.parameters()),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-rev", default="HEAD", help="git revision holding the old model.py")
    parser.add_argument("--with-350m", action="store_true")
    parser.add_argument("--large-out", default=str(Path.home() / "runs" / "ref350" / "ref_350m.pt"))
    args = parser.parse_args(argv)

    module = load_reference_module(args.ref_rev)
    if getattr(module.ModelConfig, "recurrent", None) is not None:
        print("warning: the reference revision already knows about recurrence")

    tiny = build_reference(module, TINY, TINY_SEED, TINY_INPUT_SEED, batch=2, seq_len=24)
    tiny_path = REPO_ROOT / "src" / "train" / "tests" / "data" / "ref_disabled_tiny.pt"
    tiny_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(tiny, tiny_path)
    print(f"wrote {tiny_path} ({tiny_path.stat().st_size / 1e6:.2f} MB, "
          f"{tiny['params_total']:,} params)")

    if args.with_350m:
        with open(REPO_ROOT / "configs" / "350m.yaml") as fh:
            large_cfg = yaml.safe_load(fh)["model"]
        large = build_reference(
            module, large_cfg, LARGE_SEED, LARGE_INPUT_SEED, batch=1, seq_len=64
        )
        out = Path(args.large_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        torch.save(large, out)
        print(f"wrote {out} ({out.stat().st_size / 1e9:.2f} GB, "
              f"{large['params_total']:,} params)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
