#!/usr/bin/env python3
"""Targeted OURS phase-ablation runner (A-only / A+B / A+B+C)."""

from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "outputs" / "ablation"
OUT_CSV = OUT_DIR / "phase_ablation_results.csv"
OUT_MD = OUT_DIR / "phase_ablation_summary.md"

DATASETS = [
    "Dryad_animal_society",
    "FacultyHiringNetworks/Business/Business_FM_Full_",
    "Football_data_England_Premier_League/England_2013_2014",
]


def _write_blocked(reason: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "dataset",
                "variant",
                "phase_mode",
                "upset_simple",
                "upset_ratio",
                "upset_naive",
                "runtime_sec",
                "time_phase1_sec",
                "time_phase2_sec",
                "time_phaseC_sec",
                "removed_phaseA",
                "reinserted_per_pass",
                "status",
                "note",
            ],
        )
        w.writeheader()
        w.writerow({"status": "blocked", "note": reason})
    OUT_MD.write_text(
        "# Phase ablation summary\n\n"
        "Execution blocked in this environment.\n\n"
        f"Reason: {reason}\n"
    )


def _upset_simple(A, scores):
    import numpy as np

    src, dst = A.nonzero()
    w = A[src, dst].A1 if hasattr(A[src, dst], "A1") else np.asarray(A[src, dst]).reshape(-1)
    si = scores[src]
    sj = scores[dst]
    mask = si <= sj
    if len(w) == 0:
        return math.nan
    return float(np.sum(w[mask]) / np.sum(w))


def _upset_naive(A, scores):
    import numpy as np

    src, dst = A.nonzero()
    w = A[src, dst].A1 if hasattr(A[src, dst], "A1") else np.asarray(A[src, dst]).reshape(-1)
    mask = scores[src] <= scores[dst]
    return float(np.sum(w[mask])) if len(w) else math.nan


def _upset_ratio(A, scores, eps: float = 1e-12):
    import numpy as np

    A = A.tocsr()
    n = A.shape[0]
    loss = 0.0
    cnt = 0
    for i in range(n):
        row = A.getrow(i)
        js = row.indices
        ws = row.data
        for j, wij in zip(js, ws):
            if i >= j:
                continue
            wji = A[j, i] if A[j, i] != 0 else 0.0
            den = float(wij + wji + eps)
            if den <= eps:
                continue
            m3 = float((wij - wji) / den)
            t = float((scores[i] - scores[j]) / (scores[i] + scores[j] + eps))
            loss += (m3 - t) ** 2
            cnt += 1
    return float(loss / cnt) if cnt else math.nan


def main() -> int:
    try:
        import numpy as np  # noqa: F401
        import scipy  # noqa: F401
    except Exception as e:
        _write_blocked(f"Missing numeric dependencies: {e}")
        print(f"Blocked: {e}")
        return 0

    sys.path.append(str(REPO_ROOT / "src"))
    try:
        from comparison import ours_MFAS, ours_MFAS_INS3
        from preprocess import load_real_data
    except Exception as e:
        _write_blocked(f"Unable to import project modules: {e}")
        print(f"Blocked: {e}")
        return 0

    phase_modes = [
        ("A_only", False, False),
        ("A_plus_B", True, False),
        ("A_plus_B_plus_C", True, True),
    ]
    variants = [
        ("OURS_MFAS", ours_MFAS),
        ("OURS_MFAS_INS3", ours_MFAS_INS3),
    ]

    rows = []
    for ds in DATASETS:
        A = load_real_data(ds)
        for vname, fn in variants:
            for mode, eb, ec in phase_modes:
                t0 = time.time()
                scores, meta = fn(
                    A,
                    enable_phase_b=eb,
                    enable_phase_c=ec,
                    time_limit_sec=120.0,
                    refine_ratio=ec,
                    refine_time_sec=5.0,
                    refine_passes=1,
                )
                row = {
                    "dataset": ds,
                    "variant": vname,
                    "phase_mode": mode,
                    "upset_simple": _upset_simple(A, scores),
                    "upset_ratio": _upset_ratio(A, scores),
                    "upset_naive": _upset_naive(A, scores),
                    "runtime_sec": float(meta.get("runtime_sec", time.time() - t0)),
                    "time_phase1_sec": float(meta.get("time_phase1_sec", math.nan)),
                    "time_phase2_sec": float(meta.get("time_phase2_sec", math.nan)),
                    "time_phaseC_sec": float(meta.get("time_phaseC_sec", math.nan)),
                    "removed_phaseA": int(meta.get("removed_phaseA", -1)),
                    "reinserted_per_pass": "|".join(str(x) for x in meta.get("reinserted_per_pass", [])),
                    "status": "ok",
                    "note": "",
                }
                rows.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    OUT_MD.write_text(
        "# Phase ablation summary\n\n"
        "Command:\n\n"
        "`python scripts/paper/run_phase_ablation.py`\n\n"
        f"Datasets: {', '.join(DATASETS)}\n\n"
        f"Rows written: {len(rows)}\n"
    )
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
