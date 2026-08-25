#!/usr/bin/env python3
"""Targeted A4 re-score with GNNRank calculate_upsets metrics (CPU only).

Reads the 77 non-Finance datasets already completed under structural A4,
re-runs the same A4 parameterisation, and writes GNNRank-compatible
upset_simple / upset_naive / upset_ratio plus runtime for headline tables.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import torch

REPO = Path(__file__).resolve().parents[2]
TOP = REPO.parent
SCRIPT = Path(__file__).resolve().parent
OUT = TOP / "outputs" / "revision_analysis_20260825" / "canonical_reachability_baseline_comparison"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(SCRIPT))
sys.path.insert(0, str(SCRIPT.parent / "revision_analysis_20260824"))

from metrics import calculate_upsets  # noqa: E402
from ours_mfas import ours_mfas_rmfa  # noqa: E402
from run_reviewer_ablation import STRUCTURAL_VARIANTS, LAYER1, LAYER2  # noqa: E402
from run_mincut_cap_audit import _robust_load_real_data  # noqa: E402

try:
    from comparison import load_real_data as _load_real_data
except Exception:
    _load_real_data = None


def load_A(dataset: str):
    from preprocess import load_real_data
    return _robust_load_real_data(load_real_data, dataset)


def gnnrank_upsets(A_csr, scores: np.ndarray):
    A = A_csr.tocsr()
    n = A.shape[0]
    # densify small graphs; for large use torch sparse carefully — suite n<=602 here
    if n > 2500:
        raise RuntimeError(f"unexpected large n={n}")
    Ad = torch.FloatTensor(A.toarray())
    score = torch.FloatTensor(scores.reshape(n, 1))
    simple = float(calculate_upsets(Ad, score, style="simple").detach().item())
    naive = float(calculate_upsets(Ad, score, style="naive").detach().item())
    ratio = float(calculate_upsets(Ad, score, style="ratio").detach().item())
    return simple, naive, ratio


def main():
    params = dict(STRUCTURAL_VARIANTS["A4"])
    # datasets: union layer1+layer2 names as used in structural csv
    ds_list = []
    with (TOP / "outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv").open() as f:
        for r in csv.DictReader(f):
            if r["config"] == "A4" and r["status"] == "complete":
                ds_list.append((r["dataset"], r["family"], int(float(r["n"])), int(float(r["m"]))))

    out_path = OUT / "a4_gnnrank_metrics.csv"
    progress = OUT / "a4_gnnrank_progress.jsonl"
    done = set()
    if progress.exists():
        for line in progress.read_text().splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if o.get("status") == "complete":
                done.add(o["dataset"])

    fieldnames = [
        "dataset", "family", "config", "status", "n", "m",
        "upset_simple", "upset_naive", "upset_ratio",
        "runtime_total_sec", "error",
    ]
    # rewrite CSV from progress+new
    rows_by_ds = {}
    if out_path.exists():
        with out_path.open() as f:
            for r in csv.DictReader(f):
                rows_by_ds[r["dataset"]] = r

    print(f"A4 GNNRank re-score: {len(ds_list)} datasets; {len(done)} already done", flush=True)
    t_all = time.time()
    for i, (dataset, family, n0, m0) in enumerate(ds_list):
        if dataset in done:
            continue
        t0 = time.time()
        rec = {
            "dataset": dataset,
            "family": family,
            "config": "A4",
            "status": "failed",
            "n": n0,
            "m": m0,
            "upset_simple": "",
            "upset_naive": "",
            "upset_ratio": "",
            "runtime_total_sec": "",
            "error": "",
        }
        try:
            A = load_A(dataset)
            A = A.tocsr()
            scores, meta = ours_mfas_rmfa(
                A,
                insertion_passes=params["insertion_passes"],
                enable_phase_b=params["enable_phase_b"],
                addback_mode=params["addback_mode"],
                enable_phase_c=params["enable_phase_c"],
                time_limit_sec=params["time_limit_sec"],
                refine_naive=params["refine_naive"],
                naive_refine_time_sec=params["naive_refine_time_sec"],
                naive_refine_passes=params["naive_refine_passes"],
                refine_ratio=params["refine_ratio"],
                refine_time_sec=params["refine_time_sec"],
                refine_passes=params["refine_passes"],
                ternary_iters=params["ternary_iters"],
                return_meta=True,
            )
            simple, naive, ratio = gnnrank_upsets(A, np.asarray(scores, dtype=float))
            rt = time.time() - t0
            rec.update({
                "status": "complete",
                "n": int(A.shape[0]),
                "m": int(A.nnz),
                "upset_simple": f"{simple:.12g}",
                "upset_naive": f"{naive:.12g}",
                "upset_ratio": f"{ratio:.12g}",
                "runtime_total_sec": f"{rt:.6f}",
            })
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["runtime_total_sec"] = f"{time.time()-t0:.6f}"
            traceback.print_exc()

        with progress.open("a") as pf:
            pf.write(json.dumps(rec) + "\n")
        rows_by_ds[dataset] = rec
        with out_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for ds, _, _, _ in ds_list:
                if ds in rows_by_ds:
                    w.writerow(rows_by_ds[ds])
        print(f"[{i+1}/{len(ds_list)}] {dataset} {rec['status']} "
              f"simple={rec['upset_simple']} rt={rec['runtime_total_sec']}", flush=True)

    summary = {
        "n_target": len(ds_list),
        "n_complete": sum(1 for r in rows_by_ds.values() if r.get("status") == "complete"),
        "n_failed": sum(1 for r in rows_by_ds.values() if r.get("status") != "complete"),
        "elapsed_sec": time.time() - t_all,
        "out": str(out_path),
    }
    (OUT / "a4_gnnrank_run_summary.json").write_text(json.dumps(summary, indent=2))
    print("SUMMARY", summary, flush=True)


if __name__ == "__main__":
    main()
