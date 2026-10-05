"""Run the acquisition pilot over models x thinking x conditions, plus PopQA.

Thin entry point; the code and its documentation live in src/pilot/runner.py.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.pilot.runner import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
