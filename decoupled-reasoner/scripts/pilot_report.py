"""Build the pilot report and apply the preregistered decision rule.

Thin entry point; the code and its documentation live in src/pilot/report.py.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.pilot.report import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
