#!/usr/bin/env python3
"""Post-process reviewer ablation raw_runs into manuscript/appendix tables.

Consumes ONLY:
  - experiment_manifest.json
  - dataset_manifest.csv
  - raw_runs.csv

Interpretation follows:
  docs/journal_supercomputing_revision_20260825/EXPERIMENT_INTERPRETATION_RULES.md
  docs/journal_supercomputing_revision_20260825/ABLATION_MANUSCRIPT_TABLE_PLAN.md

Does NOT redesign comparisons after seeing results. Does NOT modify raw_runs.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
TOP_ROOT = REPO_ROOT.parent
OUT_DIR = TOP_ROOT / "outputs" / "revision_analysis_20260825" / "reviewer_ablation_scalability"

# Tie thresholds from EXPERIMENT_INTERPRETATION_RULES.md
TIE_UPSET = 1e-9
TIE_RUNTIME = 0.005
DUP_TOL_REL = 1e-9
DUP_TOL_ABS = 1e-12
BOOTSTRAP_N = 2000
BOOTSTRAP_SEED = 20260825

# Lower-is-better metrics (ranking / removed-weight style)
LOWER_BETTER = {
    "upset_simple",
    "upset_ratio",
    "upset_naive",
    "removed_final_weight",
    "normalized_removed_weight",
    "runtime_total_sec",
    "runtime_phaseA_sec",
    "runtime_phaseB_sec",
    "runtime_phaseC_sec",
    "runtime_mincut_sec",
}

# Higher-is-better structural gains
HIGHER_BETTER = {
    "restored_edge_count",
    "mincut_accepted",
    "mincut_gain",
    "mincut_attempts",
}

PRIMARY_PAIRWISE = [
    ("A0", "A2", "A0_vs_A2", "upset_simple"),
    ("A1", "A2", "A1_vs_A2", "upset_simple"),
    ("A2", "A5", "A2_vs_A5", "removed_final_weight"),
    ("A4", "A6", "A4_vs_A6", "removed_final_weight"),
    ("A0", "A4", "A0_vs_A4", "upset_simple"),
]

PRIMARY_METRICS = [
    "upset_simple",
    "upset_ratio",
    "upset_naive",
    "removed_final_weight",
    "normalized_removed_weight",
    "restored_edge_count",
    "mincut_accepted",
    "mincut_gain",
    "runtime_total_sec",
]


def _f(x, default=np.nan):
    if x is None or x == "":
        return default
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _i(x, default=0):
    v = _f(x, default=np.nan)
    if np.isnan(v):
        return default
    return int(v)


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    # Stable union of keys preserving first-row order then extras
    keys: list[str] = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def _is_terminal_success_like(row: dict) -> bool:
    """Rows eligible for metric pairwise comparisons."""
    status = str(row.get("status", ""))
    if status == "complete":
        return True
    return False


def _is_timeout_like(row: dict) -> bool:
    status = str(row.get("status", ""))
    if status in ("TIMEOUT_HARD_WALLCLOCK", "timeout"):
        return True
    if status == "complete" and str(row.get("break_reason", "")) == "time_limit":
        return True
    return False


def _terminal_label(row: dict) -> str:
    if row.get("terminal_classification"):
        return str(row["terminal_classification"])
    status = str(row.get("status", ""))
    if status == "TIMEOUT_HARD_WALLCLOCK":
        return "TIMEOUT_HARD_WALLCLOCK"
    if status in ("error", "data_unavailable"):
        return "ERROR"
    if status == "complete" and str(row.get("break_reason", "")) == "time_limit":
        return "INTERNAL_TIME_LIMIT"
    if status == "complete":
        return "SUCCESS"
    return status or "unknown"


def audit_and_dedup(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Detect duplicate (dataset, config); verify agreement; keep first for stats."""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["dataset"], r["config"])].append(r)

    audit = []
    deduped = []
    # Scientific metrics must agree; runtime may jitter across duplicate launches.
    metric_keys = [
        "upset_simple", "upset_ratio", "upset_naive",
        "removed_final_weight", "normalized_removed_weight",
        "restored_edge_count", "mincut_accepted", "mincut_gain",
        "n", "m",
    ]
    runtime_keys = ["runtime_total_sec"]
    numeric_keys = metric_keys + runtime_keys
    for (ds, cfg), group in sorted(groups.items()):
        if len(group) == 1:
            deduped.append(group[0])
            continue
        metrics_consistent = True
        runtime_varies = False
        max_abs = 0.0
        max_rel = 0.0
        disagree_fields = []
        ref = group[0]
        for other in group[1:]:
            for k in numeric_keys:
                a, b = _f(ref.get(k)), _f(other.get(k))
                if np.isnan(a) and np.isnan(b):
                    continue
                if np.isnan(a) or np.isnan(b):
                    if k in metric_keys:
                        metrics_consistent = False
                    disagree_fields.append(k)
                    continue
                abs_d = abs(a - b)
                rel_d = abs_d / max(abs(a), abs(b), 1e-30)
                max_abs = max(max_abs, abs_d)
                max_rel = max(max_rel, rel_d)
                if abs_d > DUP_TOL_ABS and rel_d > DUP_TOL_REL:
                    disagree_fields.append(k)
                    if k in runtime_keys:
                        runtime_varies = True
                    else:
                        metrics_consistent = False
        audit.append({
            "dataset": ds,
            "config": cfg,
            "n_copies": len(group),
            "families": "|".join(sorted({g.get("family", "") for g in group})),
            "numerically_consistent": str(metrics_consistent).lower(),
            "runtime_varies": str(runtime_varies).lower(),
            "max_abs_diff": max_abs,
            "max_rel_diff": max_rel,
            "disagree_fields": ",".join(sorted(set(disagree_fields))),
            "dedup_rule": "keep_first_raw_row_order; metrics must agree; runtime jitter ignored for consistency",
        })
        deduped.append(group[0])
    return deduped, audit


def _paired_deltas(a_vals, b_vals, lower_better: bool):
    """Return deltas as (B - A). For lower-better, negative delta favors B."""
    return [b - a for a, b in zip(a_vals, b_vals)]


def _wtl(deltas, tie_eps: float, lower_better: bool):
    """Wins for B / ties / losses for B."""
    w = t = l = 0
    for d in deltas:
        if abs(d) < tie_eps:
            t += 1
        elif lower_better:
            if d < 0:
                w += 1
            else:
                l += 1
        else:
            if d > 0:
                w += 1
            else:
                l += 1
    return w, t, l


def _bootstrap_ci(deltas, n_boot=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    if not deltas:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    arr = np.asarray(deltas, dtype=float)
    n = len(arr)
    means = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample = arr[rng.integers(0, n, size=n)]
        means[i] = float(np.mean(sample))
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(np.mean(arr)), float(lo), float(hi)


def _wilcoxon_p(deltas):
    arr = np.asarray(deltas, dtype=float)
    # Drop exact zeros for Wilcoxon signed-rank
    arr = arr[np.abs(arr) > 0]
    if len(arr) < 5:
        return np.nan
    try:
        from scipy.stats import wilcoxon
        res = wilcoxon(arr, alternative="two-sided", zero_method="wilcox")
        return float(res.pvalue)
    except Exception:
        return np.nan


def _effect_size_cliff(deltas, lower_better: bool):
    """Cliff's delta favoring B. Uses sign of (B-A) with orientation."""
    if not deltas:
        return np.nan
    # For lower-better, favorable = negative delta
    fav = 0
    unfav = 0
    for d in deltas:
        if abs(d) < TIE_UPSET:
            continue
        if lower_better:
            if d < 0:
                fav += 1
            else:
                unfav += 1
        else:
            if d > 0:
                fav += 1
            else:
                unfav += 1
    n = fav + unfav
    if n == 0:
        return 0.0
    return (fav - unfav) / n


def _holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    indexed = sorted(enumerate(pvals), key=lambda x: (math.inf if (x[1] != x[1]) else x[1]))
    adj = [np.nan] * m
    prev = 0.0
    for rank, (idx, p) in enumerate(indexed):
        if p != p:  # NaN
            adj[idx] = np.nan
            continue
        # Holm: (m - rank) * p
        val = min(1.0, (m - rank) * p)
        val = max(val, prev)
        adj[idx] = val
        prev = val
    return adj


def pairwise_compare(rows_by_cfg: dict[str, dict[str, dict]], cfg_a: str, cfg_b: str,
                     metric: str, exclude_finance: bool = True) -> dict:
    a_map = rows_by_cfg.get(cfg_a, {})
    b_map = rows_by_cfg.get(cfg_b, {})
    common = sorted(set(a_map) & set(b_map))
    excluded_timeout = 0
    pairs_a, pairs_b = [], []
    for ds in common:
        ra, rb = a_map[ds], b_map[ds]
        if exclude_finance and ds == "finance":
            continue
        if _is_timeout_like(ra) or _is_timeout_like(rb):
            excluded_timeout += 1
            continue
        if not (_is_terminal_success_like(ra) and _is_terminal_success_like(rb)):
            continue
        va, vb = _f(ra.get(metric)), _f(rb.get(metric))
        if np.isnan(va) or np.isnan(vb):
            continue
        pairs_a.append(va)
        pairs_b.append(vb)

    lower = metric in LOWER_BETTER
    tie_eps = TIE_RUNTIME if "runtime" in metric else TIE_UPSET
    deltas = _paired_deltas(pairs_a, pairs_b, lower)
    w, t, l = _wtl(deltas, tie_eps, lower)
    mean_d, ci_lo, ci_hi = _bootstrap_ci(deltas)
    med_d = float(np.median(deltas)) if deltas else np.nan
    p = _wilcoxon_p(deltas)
    eff = _effect_size_cliff(deltas, lower)
    return {
        "comparison": f"{cfg_a}_vs_{cfg_b}",
        "config_a": cfg_a,
        "config_b": cfg_b,
        "metric": metric,
        "orientation": "lower_better" if lower else "higher_better",
        "n_common": len(deltas),
        "excluded_timeout_pairs": excluded_timeout,
        "wins_b": w,
        "ties": t,
        "losses_b": l,
        "mean_delta_b_minus_a": mean_d,
        "median_delta_b_minus_a": med_d,
        "bootstrap_ci95_lo": ci_lo,
        "bootstrap_ci95_hi": ci_hi,
        "wilcoxon_p": p,
        "effect_size_cliff": eff,
        "ci_excludes_zero": str(bool(deltas) and (ci_lo > 0 or ci_hi < 0)).lower(),
    }


def classify_sensitivity(stats_rows: list[dict], metric: str = "upset_simple") -> str:
    """STABLE / MILDLY_SENSITIVE / MATERIALLY_SENSITIVE from primary metric W/T/L + median."""
    # Use median |delta| relative and W/T/L imbalance
    relevant = [r for r in stats_rows if r["metric"] == metric]
    if not relevant:
        return "STABLE"
    # If all mostly ties
    max_med = max(abs(_f(r["median_delta_b_minus_a"], 0.0)) for r in relevant)
    min_tie_frac = min(
        (_i(r["ties"]) / max(_i(r["n_common"]), 1)) for r in relevant
    )
    any_sig = any(
        str(r.get("ci_excludes_zero", "false")).lower() == "true"
        or (_f(r.get("wilcoxon_p")) == _f(r.get("wilcoxon_p")) and _f(r.get("wilcoxon_p")) < 0.05)
        for r in relevant
    )
    if min_tie_frac >= 0.9 and max_med < 1e-6:
        return "STABLE"
    if any_sig and max_med > 1e-4:
        return "MATERIALLY_SENSITIVE"
    if max_med > 1e-6 or min_tie_frac < 0.9:
        return "MILDLY_SENSITIVE"
    return "STABLE"


def summarize_config_group(rows: list[dict], configs: list[str], out_name_prefix: str = "") -> list[dict]:
    out = []
    for cfg in configs:
        sub = [r for r in rows if r["config"] == cfg and _is_terminal_success_like(r) and r["dataset"] != "finance"]
        if not sub:
            out.append({"config": cfg, "n_datasets": 0})
            continue
        def med(k):
            vals = [_f(r.get(k)) for r in sub]
            vals = [v for v in vals if not np.isnan(v)]
            return float(np.median(vals)) if vals else np.nan
        def mean(k):
            vals = [_f(r.get(k)) for r in sub]
            vals = [v for v in vals if not np.isnan(v)]
            return float(np.mean(vals)) if vals else np.nan
        out.append({
            "config": cfg,
            "n_datasets": len(sub),
            "median_upset_simple": med("upset_simple"),
            "mean_upset_simple": mean("upset_simple"),
            "median_upset_ratio": med("upset_ratio"),
            "mean_upset_ratio": mean("upset_ratio"),
            "median_upset_naive": med("upset_naive"),
            "mean_upset_naive": mean("upset_naive"),
            "median_removed_final_weight": med("removed_final_weight"),
            "mean_removed_final_weight": mean("removed_final_weight"),
            "median_normalized_removed_weight": med("normalized_removed_weight"),
            "median_restored_edge_count": med("restored_edge_count"),
            "median_mincut_attempts": med("mincut_attempts"),
            "median_mincut_accepted": med("mincut_accepted"),
            "median_mincut_gain": med("mincut_gain"),
            "median_runtime_total_sec": med("runtime_total_sec"),
            "mean_runtime_total_sec": mean("runtime_total_sec"),
            "median_runtime_phaseA_sec": med("runtime_phaseA_sec"),
            "median_runtime_phaseB_sec": med("runtime_phaseB_sec"),
            "median_runtime_phaseC_sec": med("runtime_phaseC_sec"),
            "median_runtime_mincut_sec": med("runtime_mincut_sec"),
            "median_permutation_distance_vs_p1": med("permutation_distance_vs_p1"),
        })
    return out


def build_completion_matrix(rows: list[dict], configs: list[str]) -> list[dict]:
    by_ds = defaultdict(dict)
    for r in rows:
        by_ds[r["dataset"]][r["config"]] = r
    out = []
    for ds in sorted(by_ds):
        row = {"dataset": ds, "family": next(iter(by_ds[ds].values())).get("family", "")}
        for cfg in configs:
            if cfg not in by_ds[ds]:
                row[cfg] = "MISSING"
            else:
                row[cfg] = _terminal_label(by_ds[ds][cfg])
        out.append(row)
    return out


def build_scaling(rows: list[dict]) -> list[dict]:
    """Per-dataset scaling rows for A0/A2/A4/A6 (non-finance + finance flagged)."""
    out = []
    for r in rows:
        if r["config"] not in ("A0", "A2", "A4", "A6", "FINANCE_A0", "FINANCE_A2", "FINANCE_A4", "FINANCE_A6"):
            continue
        n = _f(r.get("n"))
        m = _f(r.get("m"))
        dens = _f(r.get("density"))
        if dens == dens:
            if dens < 0.05:
                regime = "sparse_<0.05"
            elif dens < 0.2:
                regime = "medium_0.05_0.2"
            else:
                regime = "dense_>=0.2"
        else:
            regime = "unknown"
        out.append({
            "dataset": r["dataset"],
            "family": r.get("family", ""),
            "config": r["config"],
            "is_finance": str(r["dataset"] == "finance").lower(),
            "status": r.get("status", ""),
            "terminal_classification": _terminal_label(r),
            "n": r.get("n", ""),
            "m": r.get("m", ""),
            "density": r.get("density", ""),
            "density_regime": regime,
            "m_times_n": (m * n) if (m == m and n == n) else "",
            "m_squared": (m * m) if m == m else "",
            "runtime_total_sec": r.get("runtime_total_sec", ""),
            "runtime_phaseA_sec": r.get("runtime_phaseA_sec", ""),
            "runtime_phaseB_sec": r.get("runtime_phaseB_sec", ""),
            "runtime_phaseC_sec": r.get("runtime_phaseC_sec", ""),
            "runtime_mincut_sec": r.get("runtime_mincut_sec", ""),
            "break_reason": r.get("break_reason", ""),
        })
    return out


def build_family_summary(rows: list[dict], configs: list[str]) -> list[dict]:
    out = []
    families = sorted({r["family"] for r in rows if r["dataset"] != "finance"})
    for fam in families:
        for cfg in configs:
            sub = [
                r for r in rows
                if r["family"] == fam and r["config"] == cfg and _is_terminal_success_like(r)
            ]
            if not sub:
                continue
            def med(k):
                vals = [_f(r.get(k)) for r in sub]
                vals = [v for v in vals if not np.isnan(v)]
                return float(np.median(vals)) if vals else np.nan
            out.append({
                "family": fam,
                "config": cfg,
                "n_datasets": len(sub),
                "median_upset_simple": med("upset_simple"),
                "median_upset_ratio": med("upset_ratio"),
                "median_upset_naive": med("upset_naive"),
                "median_removed_final_weight": med("removed_final_weight"),
                "median_mincut_gain": med("mincut_gain"),
                "median_runtime_total_sec": med("runtime_total_sec"),
            })
    return out


def family_aggregated_pairwise(rows: list[dict], cfg_a: str, cfg_b: str, metric: str) -> dict:
    """One point per family (median within family), then compare."""
    fams = sorted({r["family"] for r in rows if r["dataset"] != "finance"})
    a_pts, b_pts = [], []
    used = []
    for fam in fams:
        sa = [
            _f(r.get(metric)) for r in rows
            if r["family"] == fam and r["config"] == cfg_a and _is_terminal_success_like(r)
        ]
        sb = [
            _f(r.get(metric)) for r in rows
            if r["family"] == fam and r["config"] == cfg_b and _is_terminal_success_like(r)
        ]
        sa = [v for v in sa if not np.isnan(v)]
        sb = [v for v in sb if not np.isnan(v)]
        if not sa or not sb:
            continue
        a_pts.append(float(np.median(sa)))
        b_pts.append(float(np.median(sb)))
        used.append(fam)
    lower = metric in LOWER_BETTER
    deltas = _paired_deltas(a_pts, b_pts, lower)
    tie_eps = TIE_RUNTIME if "runtime" in metric else TIE_UPSET
    w, t, l = _wtl(deltas, tie_eps, lower)
    mean_d, ci_lo, ci_hi = _bootstrap_ci(deltas, n_boot=min(BOOTSTRAP_N, 1000))
    return {
        "comparison": f"{cfg_a}_vs_{cfg_b}_family_agg",
        "metric": metric,
        "n_families": len(used),
        "families": "|".join(used),
        "wins_b": w, "ties": t, "losses_b": l,
        "mean_delta_b_minus_a": mean_d,
        "median_delta_b_minus_a": float(np.median(deltas)) if deltas else np.nan,
        "bootstrap_ci95_lo": ci_lo,
        "bootstrap_ci95_hi": ci_hi,
        "note": "each_family_one_median_point;_no_family_wilcoxon",
    }


def analyze(out_dir: Path) -> dict:
    manif = json.loads((out_dir / "experiment_manifest.json").read_text())
    raw = _read_csv(out_dir / "raw_runs.csv")
    expected_hash = manif.get("config_hash")
    bad_hash = [r for r in raw if r.get("config_hash") != expected_hash]
    if bad_hash:
        raise RuntimeError(f"config_hash mismatch on {len(bad_hash)} rows")

    deduped, dup_audit = audit_and_dedup(raw)
    _write_csv(out_dir / "duplicate_run_audit.csv", dup_audit)

    # Index by config -> dataset -> row (deduped)
    by_cfg: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in deduped:
        by_cfg[r["config"]][r["dataset"]] = r

    structural_cfgs = ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]
    structural_ablation = summarize_config_group(deduped, structural_cfgs)
    # Also keep per-dataset structural rows (deduped)
    structural_detail = [
        r for r in deduped
        if r["config"] in structural_cfgs and r["dataset"] != "finance"
    ]
    _write_csv(out_dir / "structural_ablation.csv", structural_detail)

    # Sensitivities
    cycle_cfgs = ["C0_A0", "C0_A4", "C1_A0", "C1_A4"]
    zero_cfgs = ["Z12_A4", "Z15_A4", "Z18_A4"]
    refine_cfgs = ["R0_A4", "R1_A4", "R2_A4", "R3_A4"]
    pass_cfgs = ["P0", "P1", "P2", "P3"]
    k_cfgs = ["K20_A5", "K50_A5", "K100_A5"]

    _write_csv(out_dir / "cycle_selection_sensitivity.csv",
               [r for r in deduped if r["config"] in cycle_cfgs])
    _write_csv(out_dir / "zero_tol_sensitivity.csv",
               [r for r in deduped if r["config"] in zero_cfgs])
    _write_csv(out_dir / "refinement_sensitivity.csv",
               [r for r in deduped if r["config"] in refine_cfgs])
    _write_csv(out_dir / "legacy_pass_sensitivity.csv",
               [r for r in deduped if r["config"] in pass_cfgs])
    _write_csv(out_dir / "mincut_budget_sensitivity.csv",
               [r for r in deduped if r["config"] in k_cfgs])

    # Primary pairwise + full metric family for primary comps
    pairwise_rows = []
    primary_p_for_holm = []
    primary_indices = []
    for a, b, _name, primary_metric in PRIMARY_PAIRWISE:
        for metric in PRIMARY_METRICS:
            # Skip metrics that don't apply to both sides (e.g. mincut on A0)
            row = pairwise_compare(by_cfg, a, b, metric)
            pairwise_rows.append(row)
            if metric == primary_metric:
                primary_indices.append(len(pairwise_rows) - 1)
                primary_p_for_holm.append(_f(row["wilcoxon_p"]))

    # P0 vs P1/P2/P3 on upset_simple + restored
    for b in ("P1", "P2", "P3"):
        for metric in ("upset_simple", "restored_edge_count", "runtime_total_sec",
                       "permutation_distance_vs_p1"):
            pairwise_rows.append(pairwise_compare(by_cfg, "P0", b, metric))

    # Cycle comparisons
    cycle_stats = []
    for a, b in (("C0_A0", "C1_A0"), ("C0_A4", "C1_A4")):
        for metric in ("upset_simple", "upset_ratio", "removed_final_weight",
                       "runtime_total_sec", "permutation_distance_vs_p1"):
            row = pairwise_compare(by_cfg, a, b, metric)
            cycle_stats.append(row)
            pairwise_rows.append(row)

    # Zero tol vs canonical Z15
    zero_stats = []
    for other in ("Z12_A4", "Z18_A4"):
        for metric in ("upset_simple", "removed_final_weight", "runtime_total_sec"):
            row = pairwise_compare(by_cfg, "Z15_A4", other, metric)
            zero_stats.append(row)
            pairwise_rows.append(row)

    # Refinement vs R2 canonical
    refine_stats = []
    for other in ("R0_A4", "R1_A4", "R3_A4"):
        for metric in ("upset_simple", "upset_ratio", "runtime_total_sec",
                       "permutation_distance_vs_p1"):
            row = pairwise_compare(by_cfg, "R2_A4", other, metric)
            refine_stats.append(row)
            pairwise_rows.append(row)

    # Min-cut K: K20 vs K50, K50 vs K100
    k_stats = []
    for a, b in (("K20_A5", "K50_A5"), ("K50_A5", "K100_A5"), ("K20_A5", "K100_A5")):
        for metric in ("mincut_attempts", "mincut_accepted", "mincut_gain",
                       "upset_simple", "runtime_total_sec"):
            row = pairwise_compare(by_cfg, a, b, metric)
            k_stats.append(row)
            pairwise_rows.append(row)

    holm_adj = _holm(primary_p_for_holm)
    for idx, adj in zip(primary_indices, holm_adj):
        pairwise_rows[idx]["holm_adjusted_p"] = adj
        pairwise_rows[idx]["is_primary_comparison"] = "true"
    for i, row in enumerate(pairwise_rows):
        if "is_primary_comparison" not in row:
            pairwise_rows[i]["is_primary_comparison"] = "false"
            pairwise_rows[i]["holm_adjusted_p"] = ""

    # Family-aggregated primary comparisons
    fam_agg = []
    for a, b, _n, metric in PRIMARY_PAIRWISE:
        fam_agg.append(family_aggregated_pairwise(deduped, a, b, metric))

    _write_csv(out_dir / "primary_pairwise_statistics.csv", pairwise_rows)
    _write_csv(out_dir / "family_aggregated_pairwise.csv", fam_agg)

    scaling = build_scaling(deduped)
    _write_csv(out_dir / "scaling_results.csv", scaling)

    # Completion matrix: structural + finance labels
    completion_cfgs = structural_cfgs + ["FINANCE_A0", "FINANCE_A2", "FINANCE_A4", "FINANCE_A6"]
    # Map finance rows: dataset finance with FINANCE_* configs
    _write_csv(out_dir / "completion_matrix.csv",
               build_completion_matrix(deduped, completion_cfgs))

    _write_csv(out_dir / "family_summary.csv",
               build_family_summary(deduped, structural_cfgs))

    # Summary JSON for the narrative document
    finance_rows = [r for r in deduped if r["dataset"] == "finance" or r["config"].startswith("FINANCE_")]
    # Also include FINANCE_* even if dataset field set
    finance_by_cfg = {r["config"]: r for r in deduped if r["config"].startswith("FINANCE_")}

    summary = {
        "config_hash": expected_hash,
        "n_raw_rows": len(raw),
        "n_deduped_rows": len(deduped),
        "n_duplicate_groups": len(dup_audit),
        "duplicate_datasets": sorted({a["dataset"] for a in dup_audit}),
        "structural_summary": structural_ablation,
        "sensitivity_classifications": {
            "cycle_selection": classify_sensitivity(cycle_stats),
            "zero_tol": classify_sensitivity(zero_stats),
            "refinement": classify_sensitivity(refine_stats),
            "legacy_pass": classify_sensitivity(
                [r for r in pairwise_rows if r["comparison"].startswith("P0_vs_")],
            ),
            "mincut_budget": classify_sensitivity(
                k_stats, metric="mincut_gain"
            ),
        },
        "finance": [
            {
                "config": cfg,
                "status": finance_by_cfg[cfg].get("status", "MISSING") if cfg in finance_by_cfg else "MISSING",
                "terminal_classification": (
                    _terminal_label(finance_by_cfg[cfg]) if cfg in finance_by_cfg else "MISSING"
                ),
                "runtime_total_sec": finance_by_cfg[cfg].get("runtime_total_sec", "") if cfg in finance_by_cfg else "",
                "break_reason": finance_by_cfg[cfg].get("break_reason", "") if cfg in finance_by_cfg else "",
            }
            for cfg in ("FINANCE_A0", "FINANCE_A2", "FINANCE_A4", "FINANCE_A6")
        ],
        "primary_pairwise": [pairwise_rows[i] for i in primary_indices],
    }
    with (out_dir / "analysis_summary.json").open("w") as f:
        json.dump(summary, f, indent=2, default=str)

    # Also write compact structural summary table
    _write_csv(out_dir / "structural_ablation_summary.csv", structural_ablation)
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)
    summary = analyze(args.out_dir)
    print(f"Analyzed {summary['n_raw_rows']} raw -> {summary['n_deduped_rows']} deduped rows")
    print(f"Duplicates: {summary['n_duplicate_groups']} groups on {summary['duplicate_datasets']}")
    print(f"Sensitivity: {summary['sensitivity_classifications']}")
    print(f"Finance: {summary['finance']}")
    print(f"Outputs in {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
