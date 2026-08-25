#!/usr/bin/env python3
"""Rerun ONLY corrected RankCentrality on the 78 loadable suite graphs.

Rebuilds RankCentrality rows in the canonical A4 pairwise / per-dataset
tables and recomputes Holm adjustment for the upset_simple primary family.
Does not recompute other baselines.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import torch
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TOP = REPO.parent
SCRIPT = Path(__file__).resolve().parent
OUT = TOP / "outputs" / "revision_analysis_20260825" / "canonical_reachability_baseline_comparison"
RC_OUT = TOP / "outputs" / "revision_analysis_20260825" / "rankcentrality_correction_20260825"
RC_OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(SCRIPT))
sys.path.insert(0, str(SCRIPT.parent / "revision_analysis_20260824"))

from comparison import rankCentrality  # noqa: E402
from metrics import calculate_upsets  # noqa: E402
from preprocess import load_real_data  # noqa: E402
from run_mincut_cap_audit import _robust_load_real_data  # noqa: E402

TIE = 1e-6
BOOT_N = 2000
BOOT_SEED = 20260825


def load_A(dataset: str):
    return _robust_load_real_data(load_real_data, dataset)


def gnnrank_upsets(A_csr, scores: np.ndarray):
    A = A_csr.tocsr()
    n = A.shape[0]
    Ad = torch.FloatTensor(A.toarray())
    score = torch.FloatTensor(scores.reshape(n, 1))
    simple = float(calculate_upsets(Ad, score, style="simple").detach().item())
    naive = float(calculate_upsets(Ad, score, style="naive").detach().item())
    ratio = float(calculate_upsets(Ad, score, style="ratio").detach().item())
    return simple, naive, ratio


def holm(pvals):
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [1.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        scaled = pvals[i] * (m - rank)
        running = max(running, scaled)
        adj[i] = min(1.0, running)
    return adj


def bootstrap_median_ci(deltas, n_boot=BOOT_N, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    d = np.asarray(deltas, dtype=float)
    if len(d) == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    meds = np.median(d[idx], axis=1)
    return float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))


def wtl(deltas):
    w = t = l = 0
    for x in deltas:
        if abs(x) <= TIE:
            t += 1
        elif x < 0:
            w += 1
        else:
            l += 1
    return w, t, l


def wilcoxon_p(deltas):
    d = np.asarray(deltas, dtype=float)
    d = d[np.abs(d) > TIE]
    if len(d) < 1:
        return float("nan")
    try:
        return float(wilcoxon(d, alternative="two-sided").pvalue)
    except Exception:
        return float("nan")


def suite_datasets():
    """78 loadable datasets: A4's 77 non-Finance + finance."""
    a4 = list(csv.DictReader((OUT / "a4_gnnrank_metrics.csv").open()))
    rows = [(r["dataset"], r.get("family", "")) for r in a4 if r.get("status") == "complete"]
    rows.append(("finance", "Finance"))
    # stable unique
    seen = set()
    out = []
    for d, f in rows:
        if d not in seen:
            seen.add(d)
            out.append((d, f))
    return out


def main():
    a4_by_ds = {
        r["dataset"]: r
        for r in csv.DictReader((OUT / "a4_gnnrank_metrics.csv").open())
        if r.get("status") == "complete"
    }

    progress = RC_OUT / "rankcentrality_runs.jsonl"
    done = {}
    if progress.exists():
        for line in progress.read_text().splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if o.get("status") == "complete":
                done[o["dataset"]] = o

    runs = []
    with progress.open("a") as prog:
        for dataset, family in suite_datasets():
            if dataset in done:
                runs.append(done[dataset])
                continue
            t0 = time.time()
            try:
                A = load_A(dataset)
                if not sp.issparse(A):
                    A = sp.csr_matrix(A)
                else:
                    A = A.tocsr()
                scores = rankCentrality(A)
                simple, naive, ratio = gnnrank_upsets(A, scores)
                row = {
                    "dataset": dataset,
                    "family": family,
                    "status": "complete",
                    "n": int(A.shape[0]),
                    "m": int(A.nnz),
                    "upset_simple": simple,
                    "upset_naive": naive,
                    "upset_ratio": ratio,
                    "runtime_sec": time.time() - t0,
                    "error": "",
                }
            except Exception as e:
                row = {
                    "dataset": dataset,
                    "family": family,
                    "status": "error",
                    "n": "",
                    "m": "",
                    "upset_simple": "",
                    "upset_naive": "",
                    "upset_ratio": "",
                    "runtime_sec": time.time() - t0,
                    "error": str(e)[:300],
                }
            prog.write(json.dumps(row) + "\n")
            prog.flush()
            runs.append(row)
            print(row["status"], dataset, row.get("upset_simple"), flush=True)

    # write CSV of RC runs
    rc_csv = RC_OUT / "rankcentrality_fixed_metrics.csv"
    fields = [
        "dataset",
        "family",
        "status",
        "n",
        "m",
        "upset_simple",
        "upset_naive",
        "upset_ratio",
        "runtime_sec",
        "error",
    ]
    with rc_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in runs:
            w.writerow({k: r.get(k, "") for k in fields})

    complete = [r for r in runs if r["status"] == "complete"]
    print(f"complete {len(complete)}/{len(runs)}")

    # Rebuild RankCentrality pairwise vs A4 (non-Finance A4 completions)
    metric_keys = [
        ("upset_simple", "upset_simple"),
        ("upset_naive", "upset_naive"),
        ("upset_ratio", "upset_ratio"),
    ]
    pairwise_new = []
    per_ds_rows = []
    for metric, key in metric_keys:
        deltas = []
        ours_vals = []
        base_vals = []
        runtimes_o = []
        runtimes_b = []
        for r in complete:
            ds = r["dataset"]
            if ds not in a4_by_ds:
                continue  # finance not in A4 pairwise quality
            o = float(a4_by_ds[ds][key])
            b = float(r[key])
            delta = o - b
            deltas.append(delta)
            ours_vals.append(o)
            base_vals.append(b)
            runtimes_o.append(float(a4_by_ds[ds]["runtime_total_sec"]))
            runtimes_b.append(float(r["runtime_sec"]))
            if metric == "upset_simple":
                per_ds_rows.append(
                    {
                        "dataset": ds,
                        "baseline": "rankCentrality",
                        "ours": o,
                        "baseline_val": b,
                        "delta": delta,
                        "family": a4_by_ds[ds].get("family", r.get("family", "")),
                        "runtime_ours": a4_by_ds[ds]["runtime_total_sec"],
                        "runtime_base": r["runtime_sec"],
                    }
                )
        w_, t_, l_ = wtl(deltas)
        med = float(np.median(deltas)) if deltas else float("nan")
        mean = float(np.mean(deltas)) if deltas else float("nan")
        lo, hi = bootstrap_median_ci(deltas)
        pairwise_new.append(
            {
                "baseline": "rankCentrality",
                "metric": metric,
                "n_common": len(deltas),
                "ours_wins": w_,
                "ties": t_,
                "ours_loses": l_,
                "mean_delta": mean,
                "median_delta": med,
                "wilcoxon_p": wilcoxon_p(deltas),
                "bootstrap_median_CI_lo": lo,
                "bootstrap_median_CI_hi": hi,
                "median_ours": float(np.median(ours_vals)) if ours_vals else float("nan"),
                "median_baseline": float(np.median(base_vals)) if base_vals else float("nan"),
                "holm_p": "",  # filled below for upset_simple family
            }
        )

    # Runtime W/T/L for RC vs A4
    rt_deltas = []
    ratios = []
    for r in complete:
        ds = r["dataset"]
        if ds not in a4_by_ds:
            continue
        o = float(a4_by_ds[ds]["runtime_total_sec"])
        b = float(r["runtime_sec"])
        # positive ratio OURS/base; "OURS faster" if o < b
        rt_deltas.append(o - b)
        ratios.append(o / b if b > 0 else float("nan"))
    faster = sum(1 for d in rt_deltas if d < -TIE)
    ties = sum(1 for d in rt_deltas if abs(d) <= TIE)
    slower = sum(1 for d in rt_deltas if d > TIE)
    rt_row = {
        "baseline": "rankCentrality",
        "n_common": len(rt_deltas),
        "ours_faster": faster,
        "ties": ties,
        "ours_slower": slower,
        "median_ratio_ours_over_base": float(np.nanmedian(ratios)) if ratios else float("nan"),
    }

    # Update canonical CSVs: replace rankCentrality rows only
    f_path = OUT / "f_pairwise_common_completion.csv"
    old_f = list(csv.DictReader(f_path.open()))
    kept = [r for r in old_f if r["baseline"] != "rankCentrality"]
    # Recompute Holm on upset_simple primary family (all baselines in table)
    simple_rows = []
    for r in kept:
        if r["metric"] == "upset_simple":
            simple_rows.append(r)
    # add new RC simple
    rc_simple = next(r for r in pairwise_new if r["metric"] == "upset_simple")
    simple_rows.append({k: str(v) for k, v in rc_simple.items()})

    pvals = []
    for r in simple_rows:
        try:
            pvals.append(float(r["wilcoxon_p"]))
        except Exception:
            pvals.append(1.0)
    adj = holm(pvals)
    for r, a in zip(simple_rows, adj):
        r["holm_p"] = a

    # rebuild full f file
    new_f = []
    simple_by_base = {r["baseline"]: r for r in simple_rows}
    for r in kept:
        if r["metric"] == "upset_simple":
            new_f.append(simple_by_base[r["baseline"]])
        else:
            new_f.append(r)
    for r in pairwise_new:
        row = {k: r[k] for k in r}
        if r["metric"] == "upset_simple":
            row = simple_by_base["rankCentrality"]
        new_f.append({k: ("" if v is None else v) for k, v in row.items()})

    # stable column order from old file
    fieldnames = list(old_f[0].keys())
    with f_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in new_f:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    # per-dataset: replace rankCentrality rows
    pd_path = OUT / "per_dataset_upset_simple.csv"
    old_pd = list(csv.DictReader(pd_path.open()))
    kept_pd = [r for r in old_pd if r["baseline"] != "rankCentrality"]
    kept_pd.extend(per_ds_rows)
    with pd_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(old_pd[0].keys()))
        w.writeheader()
        for r in kept_pd:
            w.writerow(r)

    # e1 runtime table: replace RC row
    e1_path = OUT / "e1_runtime_wtl.csv"
    old_e1 = list(csv.DictReader(e1_path.open()))
    # discover schema
    e1_fields = list(old_e1[0].keys())
    new_e1 = [r for r in old_e1 if r.get("baseline") != "rankCentrality"]
    # map our rt_row into existing schema flexibly
    candidate = {
        "baseline": "rankCentrality",
        "n": rt_row["n_common"],
        "n_common": rt_row["n_common"],
        "ours_faster": rt_row["ours_faster"],
        "OURS_faster": rt_row["ours_faster"],
        "ties": rt_row["ties"],
        "slower": rt_row["ours_slower"],
        "ours_slower": rt_row["ours_slower"],
        "median_ratio": rt_row["median_ratio_ours_over_base"],
        "median_ratio_ours_over_base": rt_row["median_ratio_ours_over_base"],
    }
    row_out = {k: candidate.get(k, old_e1[0].get(k, "")) for k in e1_fields}
    # fill known
    for k in e1_fields:
        if k in candidate and candidate[k] != "":
            row_out[k] = candidate[k]
    new_e1.append(row_out)
    with e1_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=e1_fields)
        w.writeheader()
        for r in new_e1:
            w.writerow(r)

    summary = {
        "n_loadable_attempted": len(runs),
        "n_complete": len(complete),
        "pairwise_rankcentrality": pairwise_new,
        "runtime_wtl": rt_row,
        "note": "Inherited GNNRank RankCentrality overwrite bug corrected; only RC recomputed.",
    }
    (RC_OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
