"""The experiment registry: one row per run, and a frontier over them.

    from src.registry import Store, RunRecord
    store = Store("registry")
    store.append(RunRecord(run_id="my-run", lane="explore",
                           belief_changed="none"))

See REGISTRY.md for how to add a row and how to read the frontier.
"""

from .schema import Arch, Compute, Metrics, RunRecord, ValidationError
from .store import Store

__all__ = ["Arch", "Compute", "Metrics", "RunRecord", "Store",
           "ValidationError"]
