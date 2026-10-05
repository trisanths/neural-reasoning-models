"""Build the PopQA forced-choice item set (CPU, needs the datasets package).

Thin entry point; the code and its documentation live in src/pilot/popqa.py.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.pilot.popqa import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
