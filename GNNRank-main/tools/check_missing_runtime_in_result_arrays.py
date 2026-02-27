#!/usr/bin/env python3
"""
Search result_arrays/ for the (dataset, method) pairs that have upset_simple
but historically had missing runtime (see docs/Targeted_reruns_plan.md).

Pairs checked:
  - Halo2BetaData: SVD_NRS, SVD_RS, SpringRank
  - _AUTO/Basketball_temporal__1985adj: SpringRank

Exits 0 if all four have both upset and runtime data in result_arrays;
exits 1 if any is missing (so you can run targeted batch after 841303 or instead).

Run from repo root: python tools/check_missing_runtime_in_result_arrays.py
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULT_ARRAYS = REPO_ROOT / "result_arrays"

# From docs/Targeted_reruns_plan.md: dataset key as in result_arrays path
TARGET_PAIRS = [
    ("Halo2BetaData", "SVD_NRS"),
    ("Halo2BetaData", "SVD_RS"),
    ("Halo2BetaData", "SpringRank"),
    ("_AUTO/Basketball_temporal__1985adj", "SpringRank"),
]


def has_upset(dataset_key: str, method: str) -> bool:
    base = RESULT_ARRAYS / dataset_key
    if not base.is_dir():
        return False
    for sub in ("upset", "upset_latest"):
        mdir = base / sub / method
        if mdir.is_dir() and any(mdir.glob("*.npy")):
            return True
    return False


def has_runtime(dataset_key: str, method: str) -> bool:
    base = RESULT_ARRAYS / dataset_key
    if not base.is_dir():
        return False
    for sub in ("runtime", "runtime_latest"):
        mdir = base / sub / method
        if mdir.is_dir() and any(mdir.glob("*.npy")):
            return True
    return False


def main():
    if not RESULT_ARRAYS.is_dir():
        print("result_arrays/ not found; nothing to check.", file=sys.stderr)
        sys.exit(0)

    missing = []
    for dataset_key, method in TARGET_PAIRS:
        u = has_upset(dataset_key, method)
        r = has_runtime(dataset_key, method)
        if u and not r:
            missing.append((dataset_key, method))
            status = "missing_runtime"
        else:
            status = "ok" if (u and r) else "no_upset"
        print(f"  {dataset_key} | {method}: upset={u}, runtime={r} -> {status}")

    if missing:
        print("\nMissing runtime (or data) for:", [f"{d}|{m}" for d, m in missing])
        print("If job 841303 has finished and these are still missing, run: bash tools/run_targeted_missing_runtime.sh")
        sys.exit(1)
    print("\nAll target pairs have both upset and runtime in result_arrays.")
    sys.exit(0)


if __name__ == "__main__":
    main()
