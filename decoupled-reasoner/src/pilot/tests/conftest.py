import json

import pytest

from src.pilot.items import build_items, write_items


@pytest.fixture(scope="session")
def manifest_dir(tmp_path_factory):
    """A stand-in for runs/data-manifests with the real manifests' shape."""
    d = tmp_path_factory.mktemp("manifests")
    for name, base, chunks in (("regime_e.json", 51515, 304),
                               ("regime_e3.json", 20260827, 398)):
        with open(d / name, "w") as fh:
            json.dump({"base_seed": base, "episode_stride": 100000,
                       "chunks": [{"id": i} for i in range(chunks)]}, fh)
    return str(d)


@pytest.fixture(scope="session")
def smoke_built():
    return build_items(smoke=True)


@pytest.fixture(scope="session")
def smoke_items_path(tmp_path_factory, smoke_built, manifest_dir):
    path = str(tmp_path_factory.mktemp("items") / "items.jsonl")
    write_items(path, smoke_built, manifest_dir, smoke=True)
    return path
