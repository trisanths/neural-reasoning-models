"""Build the bit identity reference for the pointer head.

The references are produced by the pre pointer model.py, taken straight out of
git, so they are an old code artifact rather than something the new code wrote
about itself. src/train/tests/test_pointer_model.py then loads them with the
new model.py, model.pointer absent, and demands bit identical logits, an
identical init RNG stream and an identical state dict key set.

  uv run python scripts/make_pointer_reference.py --ref-rev c46c8a3

Two references are written into src/train/tests/data/: a plain model and a
recurrent one, because the pointer field sits next to the recurrent field on
the same config and the interaction is worth pinning rather than assuming.
With --with-350m a full 350m checkpoint is also written to --large-out, about
1.5 GiB, not meant to be committed.

The revision has to predate the pointer head, or the reference is the new code
grading its own homework. c46c8a3 is the last such revision and is the default.
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
TINY_RECURRENT = {
    **TINY,
    "n_layers": 4,
    "recurrent": {"prelude_layers": 1, "core_layers": 2, "coda_layers": 1, "loops": 3},
}
PRE_POINTER_REV = "c46c8a3"
TINY_SEED = 4242
TINY_INPUT_SEED = 17
LARGE_SEED = 8484
LARGE_INPUT_SEED = 23


def load_reference_module(rev: str):
    """Import the model.py of a git revision under its own module name."""
    source = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{rev}:src/train/model.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    tmp = Path(tempfile.mkdtemp()) / "model_pre_pointer.py"
    tmp.write_text(source)
    spec = importlib.util.spec_from_file_location("model_pre_pointer", tmp)
    module = importlib.util.module_from_spec(spec)
    sys.modules["model_pre_pointer"] = module
    spec.loader.exec_module(module)
    return module


def build_reference(module, model_cfg: dict, seed: int, input_seed: int,
                    batch: int, seq_len: int) -> dict:
    torch.manual_seed(seed)
    model = module.TransformerLM(module.ModelConfig(**model_cfg))
    model.eval()
    gen = torch.Generator().manual_seed(input_seed)
    idx = torch.randint(0, model_cfg["vocab_size"], (batch, seq_len), generator=gen)
    targets = torch.randint(0, model_cfg["vocab_size"], (batch, seq_len), generator=gen)
    with torch.no_grad():
        logits, loss = model(idx, targets)
    return {
        "model_config": model_cfg,
        "seed": seed,
        "input_seed": input_seed,
        "input": idx,
        "targets": targets,
        "logits": logits,
        "loss": loss,
        "state_dict": model.state_dict(),
        "params_total": sum(p.numel() for p in model.parameters()),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref-rev", default=PRE_POINTER_REV,
                        help="git revision holding the old model.py, which must predate the pointer head")
    parser.add_argument("--allow-pointer-ref", action="store_true",
                        help="build against a revision that already has the pointer head, for debugging only")
    parser.add_argument("--with-350m", action="store_true")
    parser.add_argument("--large-out", default=str(Path.home() / "runs" / "refptr" / "ref_350m_pointer.pt"))
    args = parser.parse_args(argv)

    module = load_reference_module(args.ref_rev)
    if "pointer" in module.ModelConfig.__dataclass_fields__ and not args.allow_pointer_ref:
        raise SystemExit(
            f"revision {args.ref_rev} already knows about the pointer head, so a reference "
            f"built from it would be the new code checking itself. Pass a revision at or "
            f"before {PRE_POINTER_REV}, or --allow-pointer-ref to override."
        )

    out_dir = REPO_ROOT / "src" / "train" / "tests" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, cfg in (("ref_no_pointer_tiny.pt", TINY),
                      ("ref_no_pointer_recurrent.pt", TINY_RECURRENT)):
        ref = build_reference(module, cfg, TINY_SEED, TINY_INPUT_SEED, batch=2, seq_len=24)
        ref["ref_rev"] = args.ref_rev
        path = out_dir / name
        torch.save(ref, path)
        print(f"wrote {path} ({path.stat().st_size / 1e6:.2f} MB, "
              f"{ref['params_total']:,} params, loss {float(ref['loss']):.6f})")

    if args.with_350m:
        with open(REPO_ROOT / "configs" / "350m.yaml") as fh:
            large_cfg = yaml.safe_load(fh)["model"]
        large = build_reference(module, large_cfg, LARGE_SEED, LARGE_INPUT_SEED,
                                batch=1, seq_len=64)
        large["ref_rev"] = args.ref_rev
        out = Path(args.large_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        torch.save(large, out)
        print(f"wrote {out} ({out.stat().st_size / 1e9:.2f} GB, "
              f"{large['params_total']:,} params)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
