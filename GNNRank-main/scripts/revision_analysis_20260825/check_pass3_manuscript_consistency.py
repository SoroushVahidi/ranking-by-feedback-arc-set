#!/usr/bin/env python3
"""Fast Pass-3 consistency checks (no experiments)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
TEX = (ROOT / "manuscript/revision_20260825/source/main_ik.tex").read_text()
F = pd.read_csv(ROOT / "outputs/revision_analysis_20260824/runtime_coverage_final/f_pairwise_common_completion.csv")
E1 = pd.read_csv(ROOT / "outputs/revision_analysis_20260824/runtime_coverage_final/e1_runtime_wtl.csv")
PP = pd.read_csv(
    ROOT / "outputs/revision_analysis_20260825/reviewer_ablation_scalability/primary_pairwise_statistics.csv"
)


def must(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL: {msg}")
    print("PASS:", msg)


def main() -> None:
    diff = subprocess.check_output(["git", "diff", "--", "manuscript/submitted_original/"], cwd=ROOT)
    must(len(diff) == 0, "submitted_original unchanged")
    must("_AUTO" in TEX, "AUTO exclusion mentioned")
    must("slower than lightweight classical" in TEX, "classical runtime honesty")
    must("do not claim universal dominance" in TEX.lower() or "We do not claim universal dominance" in TEX, "no universal dominance")
    must("best-in-suite" in TEX.lower() or "Oracle best-in-suite" in TEX, "oracle qualified")
    r = F[(F.baseline == "btl") & (F.metric == "upset_ratio")].iloc[0]
    must(int(r.ours_wins) == 1 and int(r.ours_loses) == 76, "BTL upset_ratio W/T/L")
    d = E1[E1.baseline == "DIGRAC"].iloc[0]
    must(int(d.ours_faster) == 60 and int(d.ours_slower) == 0, "DIGRAC runtime 60/60")
    a02 = PP[(PP.comparison == "A0_vs_A2") & (PP.metric == "upset_simple")].iloc[0]
    must(int(a02.wins_b) == 76 and int(a02.losses_b) == 1, "A0→A2 76/0/1")
    must("FINANCE_A6" in TEX or "TIMEOUT" in TEX, "Finance timeout present")
    must("faster than all classical" not in TEX.lower(), "no classical speed claim")
    print("All Pass-3 checks passed.")


if __name__ == "__main__":
    main()
