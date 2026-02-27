
#!/usr/bin/env python3
"""Compare OURS metrics before vs after reruns.

Usage (from repo root):

  # Save a copy of the current leaderboard before rerunning OURS
  cp paper_csv/leaderboard_per_method.csv paper_csv/leaderboard_per_method_before_ours.csv

  # ... run tools/run_ours_shortlist.sh and rebuild artifacts ...

  python tools/compare_ours_before_after.py     --old paper_csv/leaderboard_per_method_before_ours.csv     --new paper_csv/leaderboard_per_method.csv

This script:
  - Restricts to OURS methods only.
  - For each dataset, finds the best OURS variant (min upset_simple) in the
    old and new files separately.
  - Computes per-dataset deltas (new - old) for upset_* and runtime_sec.
  - Aggregates median deltas and win/tie/loss counts.
  - Writes a human-readable report to docs/Ours_change_impact_report.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import argparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
DOCS.mkdir(exist_ok=True)

OURS_METHODS = {"OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"}


@dataclass
class BestRow:
  dataset: str
  method: str
  upset_simple: float
  upset_ratio: float
  upset_naive: float
  runtime_sec: float


def load_best_ours(path: Path) -> pd.DataFrame:
  df = pd.read_csv(path)
  df = df[df["method"].isin(OURS_METHODS)].copy()
  df = df.dropna(subset=["upset_simple"])
  if df.empty:
    return pd.DataFrame(columns=[
      "dataset", "method", "upset_simple", "upset_ratio", "upset_naive", "runtime_sec",
    ])
  df = df.sort_values(["dataset", "upset_simple"], ascending=[True, True])
  best = df.groupby("dataset", as_index=False).first()[
    ["dataset", "method", "upset_simple", "upset_ratio", "upset_naive", "runtime_sec"]
  ]
  return best


def compare(old_path: Path, new_path: Path) -> Tuple[pd.DataFrame, dict]:
  old_best = load_best_ours(old_path)
  new_best = load_best_ours(new_path)

  merged = old_best.merge(
    new_best,
    on="dataset",
    how="inner",
    suffixes=("_old", "_new"),
  )

  if merged.empty:
    return merged, {"n_datasets": 0}

  for metric in ["upset_simple", "upset_ratio", "upset_naive", "runtime_sec"]:
    merged[f"delta_{metric}"] = merged[f"{metric}_new"] - merged[f"{metric}_old"]

  # Win/tie/loss vs old OURS using upset_simple
  eps = 1e-3
  diff = merged["delta_upset_simple"]
  n_win = int((diff < -eps).sum())
  n_tie = int((diff.abs() <= eps).sum())
  n_loss = int((diff > eps).sum())

  summary = {
    "n_datasets": int(len(merged)),
    "median_delta_upset_simple": float(merged["delta_upset_simple"].median()),
    "median_delta_runtime_sec": float(merged["delta_runtime_sec"].median()),
    "n_win": n_win,
    "n_tie": n_tie,
    "n_loss": n_loss,
  }

  return merged, summary


def write_report(per_ds: pd.DataFrame, summary: dict, old_path: Path, new_path: Path) -> None:
  lines = []
  lines.append("# OURS change impact report\n\n")
  lines.append(f"Old leaderboard: `{old_path}`\n")
  lines.append(f"New leaderboard: `{new_path}`\n\n")

  n = summary.get("n_datasets", 0)
  if n == 0:
    lines.append("No overlapping datasets with OURS found between old and new leaderboards.\n")
    (DOCS / "Ours_change_impact_report.md").write_text("".join(lines))
    return

  lines.append("## Aggregated impact (best OURS per dataset)\n\n")
  lines.append(f"- Datasets compared: **{n}**\n")
  lines.append(f"- Median Δ upset_simple (new - old): **{summary['median_delta_upset_simple']:.4f}**\n")
  lines.append(f"- Median Δ runtime_sec (new - old): **{summary['median_delta_runtime_sec']:.4f}**\n")
  lines.append(f"- Win / tie / loss vs old OURS (upset_simple): **{summary['n_win']} / {summary['n_tie']} / {summary['n_loss']}**\n\n")

  # Per-dataset table
  lines.append("## Per-dataset deltas (best OURS per dataset)\n\n")
  cols = [
    "dataset",
    "method_old", "upset_simple_old", "runtime_sec_old",
    "method_new", "upset_simple_new", "runtime_sec_new",
    "delta_upset_simple", "delta_runtime_sec",
  ]
  view = per_ds[cols].copy()
  view = view.sort_values("delta_upset_simple")

  lines.append("| dataset | old method | old upset_simple | old runtime_sec | new method | new upset_simple | new runtime_sec | Δ upset_simple | Δ runtime_sec |\n")
  lines.append("|---------|------------|------------------|-----------------|------------|------------------|-----------------|---------------|--------------|\n")
  for _, r in view.iterrows():
    lines.append(
      f"| {r['dataset']} | {r['method_old']} | {r['upset_simple_old']:.3f} | {r['runtime_sec_old']:.3f} | "
      f"{r['method_new']} | {r['upset_simple_new']:.3f} | {r['runtime_sec_new']:.3f} | "
      f"{r['delta_upset_simple']:.3f} | {r['delta_runtime_sec']:.3f} |\n"
    )

  (DOCS / "Ours_change_impact_report.md").write_text("".join(lines))


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--old", type=str, default=str(REPO_ROOT / "paper_csv" / "leaderboard_per_method_before_ours.csv"))
  ap.add_argument("--new", type=str, default=str(REPO_ROOT / "paper_csv" / "leaderboard_per_method.csv"))
  args = ap.parse_args()

  old_path = Path(args.old)
  new_path = Path(args.new)

  per_ds, summary = compare(old_path, new_path)
  write_report(per_ds, summary, old_path, new_path)


if __name__ == "__main__":
  main()
