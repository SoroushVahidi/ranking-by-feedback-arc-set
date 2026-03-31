#!/usr/bin/env python3
"""Single entrypoint: rebuild + validate + test canonical paper artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

COMMANDS = [
    [sys.executable, "scripts/paper/rebuild_experiment_tables.py"],
    [sys.executable, "scripts/paper/validate_experiment_tables.py"],
    [sys.executable, "-m", "pytest", "tests/test_experiment_table_consistency.py"],
]


def main() -> int:
    for cmd in COMMANDS:
        print("+", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(REPO_ROOT))
    print("All canonical paper artifact checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
