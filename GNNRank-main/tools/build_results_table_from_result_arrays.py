#!/usr/bin/env python3
"""
Recursively aggregate GNN and other method results from result_arrays/ into a
single CSV with full-precision floats.

Finds every result_arrays/**/upset/, **/runtime/, **/upset_latest/, **/runtime_latest/.
Uses the relative path from result_arrays/ to the parent of 'upset' as dataset name
(e.g. Basketball_temporal/1985, Dryad_animal_society).

Output CSV columns:
  dataset, method, config, which,
  upset_simple_mean, upset_simple_std, upset_ratio_mean, upset_ratio_std,
  upset_naive_mean, upset_naive_std,
  runtime_sec_mean, runtime_sec_std,
  num_runs, num_nans

Run from repo root: python tools/build_results_table_from_result_arrays.py
"""

from pathlib import Path
import csv
import math

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULT_ARRAYS = REPO_ROOT / "result_arrays"
OUT_CSV = REPO_ROOT / "paper_csv" / "results_from_result_arrays.csv"

# Skip combo method dirs (e.g. SpringRanksyncRank...)
def is_combo_method(name: str) -> bool:
    if "SpringRanksyncRankserialRank" in name:
        return True
    if len(name) > 60 and "SpringRank" in name and "syncRank" in name:
        return True
    return False


def find_dataset_dirs():
    """Yield (dataset_relpath, dataset_abspath) for every dir that has upset/ or runtime/."""
    seen = set()
    for subdir in ["upset", "upset_latest", "runtime", "runtime_latest"]:
        for p in RESULT_ARRAYS.rglob(subdir):
            if not p.is_dir():
                continue
            # dataset_dir = parent of 'upset' or 'runtime'
            dataset_dir = p.parent
            # Skip debug
            if "debug" in dataset_dir.parts:
                continue
            try:
                rel = dataset_dir.relative_to(RESULT_ARRAYS)
            except ValueError:
                continue
            key = str(rel)
            if key not in seen:
                seen.add(key)
                yield key, dataset_dir


def load_upset_npy(path: Path) -> np.ndarray:
    """Load one .npy; return (N, 3) array (upset_simple, upset_ratio, upset_naive)."""
    a = np.load(path)
    a = np.asarray(a)
    if a.ndim == 3 and a.shape[-1] == 3:
        return a.reshape(-1, 3)
    if a.ndim == 2 and a.shape[-1] == 3:
        return a
    if a.ndim == 1 and a.size == 3:
        return a.reshape(1, 3)
    return np.empty((0, 3))


def load_runtime_npy(path: Path) -> np.ndarray:
    """Load one .npy; return (N,) array of runtimes in seconds."""
    a = np.load(path)
    a = np.asarray(a)
    if a.ndim >= 1:
        return a.ravel()
    return np.array([float(a)])


def agg_metrics(vals: np.ndarray, is_runtime: bool) -> tuple:
    """Compute mean, std, count, nan count. vals shape (N,) or (N, 3)."""
    if vals.size == 0:
        if is_runtime:
            return (np.nan, np.nan, 0, int(np.isnan(vals).sum()))
        return (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 0, int(np.isnan(vals).sum()))
    flat = vals.reshape(-1) if is_runtime else vals.reshape(-1, vals.shape[-1])
    n = flat.shape[0]
    nans = int(np.isnan(flat).sum())
    if is_runtime:
        good = flat[np.isfinite(flat)]
        mu = np.mean(good) if len(good) else np.nan
        std = np.std(good) if len(good) > 1 else (0.0 if len(good) == 1 else np.nan)
        return (float(mu), float(std), n, nans)
    # (N, 3) -> mean/std per column
    means = []
    stds = []
    for j in range(flat.shape[1]):
        col = flat[:, j]
        good = col[np.isfinite(col)]
        mu = np.mean(good) if len(good) else np.nan
        std = np.std(good) if len(good) > 1 else (0.0 if len(good) == 1 else np.nan)
        means.append(float(mu))
        stds.append(float(std))
    return (*means, *stds, n, nans)


def main():
    RESULT_ARRAYS.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    dataset_dirs = list(find_dataset_dirs())
    for dataset_name, dataset_dir in sorted(dataset_dirs, key=lambda x: x[0]):
        for which in ["upset", "upset_latest"]:
            subdir = dataset_dir / which
            if not subdir.is_dir():
                continue
            for method_dir in sorted(subdir.iterdir()):
                if not method_dir.is_dir():
                    continue
                method = method_dir.name
                if is_combo_method(method):
                    continue
                npys = sorted(method_dir.glob("*.npy"))
                for npy_path in npys:
                    config = npy_path.stem
                    all_vals = load_upset_npy(npy_path)
                    if all_vals.size == 0:
                        continue
                    n = all_vals.shape[0]
                    nans = int(np.isnan(all_vals).sum())
                    us_mean = float(np.nanmean(all_vals[:, 0])) if n else np.nan
                    us_std = float(np.nanstd(all_vals[:, 0])) if n > 1 else (0.0 if n == 1 else np.nan)
                    ur_mean = float(np.nanmean(all_vals[:, 1])) if n else np.nan
                    ur_std = float(np.nanstd(all_vals[:, 1])) if n > 1 else (0.0 if n == 1 else np.nan)
                    un_mean = float(np.nanmean(all_vals[:, 2])) if n else np.nan
                    un_std = float(np.nanstd(all_vals[:, 2])) if n > 1 else (0.0 if n == 1 else np.nan)
                    runtime_sec_mean = np.nan
                    runtime_sec_std = np.nan
                    runtime_which = "runtime_latest" if "latest" in which else "runtime"
                    runtime_dir = dataset_dir / runtime_which / method
                    if runtime_dir.is_dir():
                        rt_file = runtime_dir / (npy_path.name)
                        if not rt_file.exists():
                            rt_candidates = list(runtime_dir.glob("*.npy"))
                            rt_file = rt_candidates[0] if len(rt_candidates) == 1 else None
                            for c in rt_candidates:
                                if c.stem == config:
                                    rt_file = c
                                    break
                        if rt_file and rt_file.exists():
                            rt_vals = load_runtime_npy(rt_file)
                            if rt_vals.size:
                                good = rt_vals[np.isfinite(rt_vals)]
                                runtime_sec_mean = float(np.mean(good)) if len(good) else np.nan
                                runtime_sec_std = float(np.std(good)) if len(good) > 1 else (0.0 if len(good) == 1 else np.nan)
                    rows.append({
                        "dataset": dataset_name,
                        "method": method,
                        "config": config,
                        "which": which,
                        "upset_simple_mean": us_mean,
                        "upset_simple_std": us_std,
                        "upset_ratio_mean": ur_mean,
                        "upset_ratio_std": ur_std,
                        "upset_naive_mean": un_mean,
                        "upset_naive_std": un_std,
                        "runtime_sec_mean": runtime_sec_mean,
                        "runtime_sec_std": runtime_sec_std,
                        "num_runs": n,
                        "num_nans": nans,
                    })

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "dataset", "method", "config", "which",
            "upset_simple_mean", "upset_simple_std", "upset_ratio_mean", "upset_ratio_std",
            "upset_naive_mean", "upset_naive_std",
            "runtime_sec_mean", "runtime_sec_std",
            "num_runs", "num_nans",
        ], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    return OUT_CSV


if __name__ == "__main__":
    main()
