#!/usr/bin/env python3
"""Single entrypoint: rebuild + validate + test canonical paper artifacts.

Run from the **repository root** (the parent of ``GNNRank-main/``):

    python GNNRank-main/scripts/paper/run_all_paper_artifacts.py

This wrapper delegates to the three pipeline scripts that live under
``GNNRank-main/``.  ``GNNRANK_ROOT`` below refers to that sub-directory,
not the top-level repository root.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Points to the GNNRank-main/ subdirectory (two levels up from this script's
# location: GNNRank-main/scripts/paper/ → GNNRank-main/scripts/ → GNNRank-main/).
# Canonical outputs are written under GNNRank-main/outputs/paper_tables/ and
# GNNRank-main/outputs/audits/.
GNNRANK_ROOT = Path(__file__).resolve().parents[2]

COMMANDS = [
    [sys.executable, "scripts/paper/rebuild_experiment_tables.py"],
    [sys.executable, "scripts/paper/validate_experiment_tables.py"],
    [sys.executable, "-m", "pytest", "tests/test_experiment_table_consistency.py"],
]


def main() -> int:
    for cmd in COMMANDS:
        print("+", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(GNNRANK_ROOT))
    print("All canonical paper artifact checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
