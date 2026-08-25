#!/usr/bin/env python3
"""Pass-4 manuscript consistency checks (no experiments)."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEX = (ROOT / "manuscript/revision_20260825/source/main_ik.tex").read_text()


def must(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL: {msg}")
    print("PASS:", msg)


def main() -> None:
    diff = subprocess.check_output(["git", "diff", "--", "manuscript/submitted_original/"], cwd=ROOT)
    must(len(diff) == 0, "submitted_original unchanged")
    must(r"\title{Training-Free Ranking" in TEX, "title without Scalable")
    must("Scalable and Training-Free" not in TEX, "old scalable title gone")
    must(r"\section{Limitations}" in TEX and r"\section{Conclusion}" in TEX, "Limitations+Conclusion present")
    must(r"\section{Future Work}" in TEX, "Future Work present")
    must("slower than lightweight classical" in TEX, "classical runtime honesty")
    must("We do not claim universal dominance" in TEX, "no universal dominance")
    must("We do not claim the DF03 approximation guarantee for prematurely terminated" in TEX, "no practical DF03 claim")
    must("fidelity" in TEX.lower() and "newly invented" in TEX, "reachability not claimed new")
    must("no global optimality" in TEX.lower() or "no global optimality and no approximation ratio" in TEX, "min-cut not global opt")
    must("BTL remains stronger" in TEX or "weaker than BTL" in TEX, "BTL upset_ratio caveat")
    must("TIMEOUT_HARD_WALLCLOCK" in TEX.replace("\\", "") or "TIMEOUT\\_HARD\\_WALLCLOCK" in TEX, "Finance limitation")
    must("end-to-end" in TEX.lower(), "GNN end-to-end qualification")
    must("not independent ranking observations" in TEX or "rather than ranking uncertainty" in TEX, "deterministic-repeat interpretation")
    must("Legacy INS Labels" not in TEX, "legacy INS subsection removed")
    # contribution list not triplicated as identical enumerate in Abstract
    abs_ = TEX[TEX.find(r"\begin{abstract}") : TEX.find(r"\end{abstract}")]
    must(r"\begin{enumerate}" not in abs_, "Abstract has no contribution enumerate")
    must("scalable alternative" not in abs_.lower(), "Abstract no scalable marketing")
    # Intro has the detailed contribution list; Conclusion must not copy the same 4 bold itemize headers
    must("Implementation-fidelity correction" not in TEX[TEX.find(r"\section{Conclusion}"):], "Conclusion no contrib-item clone")
    must(TEX.count("Secondary structural repair") <= 2, "structural repair phrase not over-repeated")
    must("10.16" not in TEX, "no stale 10.16x")
    must("best-in-suite" in TEX.lower() or "Oracle best-in-suite" in TEX, "oracle qualified if mentioned")
    print("All Pass-4 checks passed.")


if __name__ == "__main__":
    main()
