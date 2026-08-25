#!/usr/bin/env python3
"""Family-aware baseline sensitivity analysis (Reviewer 2 independence concern).

Uses EXISTING canonical leaderboard only — no algorithm reruns.
Primary source: GNNRank-main/paper_csv/leaderboard_per_method.csv

Implements:
  - frozen family mapping
  - per-dataset paired W/T/L vs OURS_MFAS
  - per-family macro (median/mean Δ, family W/T/L)
  - equal-family macro average
  - leave-one-family-out (LOFO)
  - Basketball-collapsed analysis
  - optional hierarchical bootstrap (families first, datasets second)
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
TOP = REPO.parent
LB_PATH = REPO / "paper_csv" / "leaderboard_per_method.csv"
OUT = TOP / "outputs" / "revision_analysis_20260825" / "family_aware_baselines"

PREFERRED_CONFIG = "trials10train_r100test_r100AllTrue"
# For DIGRAC/ib pick the dominant K20+dist SpringRank-init style config prefix
GNN_CONFIG_CONTAINS = "K20dropout50ratio_coe100margin_coe0withdistFiedler"

PRINCIPAL = [
    "SpringRank",
    "davidScore",
    "SVD_NRS",
    "btl",
    "PageRank",
    "syncRank",
    "rankCentrality",
    "serialRank",
    "DIGRAC",
    "ib",
]
OURS = "OURS_MFAS"
METRICS = ["upset_simple", "upset_naive", "upset_ratio"]
TIE_EPS = 1e-9
BOOT_N = 2000
BOOT_SEED = 20260825


def _f(x):
    if x is None or x == "":
        return np.nan
    try:
        v = float(x)
        if math.isnan(v):
            return np.nan
        return v
    except (TypeError, ValueError):
        return np.nan


def assign_family(dataset: str) -> tuple[str, str, str, str]:
    """Return (family, subfamily, included, reason)."""
    d = dataset
    if d == "finance" or d.endswith("/finance") or d == "Finance":
        return "Finance", "finance", "excluded_from_macro", "stress/timeout case; exclude from quality macros"
    if d.startswith("Basketball_temporal/finer") or "/finer" in d and "Basketball" in d:
        return "Basketball_finer", "temporal_year", "included", "basketball finer temporal instance"
    if d.startswith("Basketball_temporal/") or d.startswith("_AUTO/Basketball"):
        return "Basketball_coarse", "temporal_year", "included", "basketball coarse temporal instance"
    if "Football" in d or "Premier_League" in d:
        if "finer" in d:
            return "Football_finer", "season", "included", "football finer"
        return "Football_coarse", "season", "included", "football coarse"
    if "FacultyHiring" in d or d.startswith("Faculty"):
        return "Faculty", "discipline", "included", "faculty hiring"
    if "Dryad" in d or "animal" in d.lower():
        return "Animal", "society", "included", "animal society"
    if "Halo" in d:
        return "Halo", "head_to_head", "included", "halo / head-to-head"
    if "ERO" in d or "ero" in d.lower():
        return "ERO", "synthetic", "included_if_present", "ERO-style if present"
    if d.startswith("_AUTO/"):
        return "Other_AUTO", "auto", "excluded_from_macro", "non-canonical auto alias"
    return "Other", "other", "excluded_from_macro", "unmapped taxonomy"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    keys: list[str] = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def select_row(rows: list[dict], method: str) -> dict | None:
    """Pick a single canonical row for a method among candidates for one dataset."""
    if not rows:
        return None
    if method in ("DIGRAC", "ib"):
        pref = [r for r in rows if GNN_CONFIG_CONTAINS in (r.get("config") or "")]
        pool = pref or rows
    else:
        pref = [r for r in rows if (r.get("config") or "") == PREFERRED_CONFIG]
        pool = pref or rows
    # Prefer rows with finite upset_simple
    finite = [r for r in pool if not np.isnan(_f(r.get("upset_simple")))]
    pool = finite or pool
    # Stable: lexicographically smallest config for determinism
    pool = sorted(pool, key=lambda r: r.get("config") or "")
    return pool[0]


def load_canonical_table(path: Path) -> dict[str, dict[str, dict]]:
    """dataset -> method -> row"""
    by_ds_method: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    with path.open() as f:
        for r in csv.DictReader(f):
            by_ds_method[r["dataset"]][r["method"]].append(r)
    out: dict[str, dict[str, dict]] = {}
    for ds, methods in by_ds_method.items():
        out[ds] = {}
        for m, rows in methods.items():
            sel = select_row(rows, m)
            if sel is not None:
                out[ds][m] = sel
    return out


def paired_stats(deltas: list[float], lower_better: bool = True) -> dict:
    if not deltas:
        return {
            "n": 0, "wins": 0, "ties": 0, "losses": 0,
            "mean_delta": np.nan, "median_delta": np.nan,
            "ci_lo": np.nan, "ci_hi": np.nan,
        }
    w = t = l = 0
    for d in deltas:
        if abs(d) < TIE_EPS:
            t += 1
        elif (d < 0) if lower_better else (d > 0):
            w += 1  # OURS better when lower-better and delta=ours-baseline < 0
        else:
            l += 1
    arr = np.asarray(deltas, dtype=float)
    rng = np.random.default_rng(BOOT_SEED)
    means = []
    n = len(arr)
    for _ in range(min(BOOT_N, 2000)):
        means.append(float(np.mean(arr[rng.integers(0, n, size=n)])))
    lo, hi = np.quantile(means, [0.025, 0.975])
    return {
        "n": n,
        "wins": w,
        "ties": t,
        "losses": l,
        "mean_delta": float(np.mean(arr)),
        "median_delta": float(np.median(arr)),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "ci_excludes_zero": bool(lo > 0 or hi < 0),
    }


def analyze(lb_path: Path = LB_PATH, out_dir: Path = OUT) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    table = load_canonical_table(lb_path)
    datasets = sorted(table.keys())

    # Family mapping
    fam_rows = []
    fam_of = {}
    for ds in datasets:
        fam, sub, incl, reason = assign_family(ds)
        fam_of[ds] = fam
        fam_rows.append({
            "dataset": ds,
            "family": fam,
            "subfamily": sub,
            "included_excluded": incl,
            "reason": reason,
            "has_ours": str(OURS in table[ds]).lower(),
        })
    write_csv(out_dir / "family_mapping.csv", fam_rows)

    # Build per-dataset paired deltas: delta = ours - baseline (lower better => negative favors OURS)
    pairwise_rows = []
    # method -> list of (dataset, family, delta_by_metric, runtime_delta)
    method_pairs: dict[str, list] = defaultdict(list)

    for ds in datasets:
        if OURS not in table[ds]:
            continue
        ours = table[ds][OURS]
        fam = fam_of[ds]
        for m in PRINCIPAL:
            if m not in table[ds]:
                continue
            base = table[ds][m]
            # skip timeouts for quality pairing
            if str(ours.get("timeout_flag", "")).lower() in ("true", "1"):
                continue
            if str(base.get("timeout_flag", "")).lower() in ("true", "1"):
                continue
            entry = {"dataset": ds, "family": fam, "baseline": m}
            ok_metrics = True
            for metric in METRICS:
                ov, bv = _f(ours.get(metric)), _f(base.get(metric))
                if np.isnan(ov) or np.isnan(bv):
                    ok_metrics = False
                    entry[f"delta_{metric}"] = ""
                    entry[f"ours_{metric}"] = ours.get(metric, "")
                    entry[f"base_{metric}"] = base.get(metric, "")
                else:
                    entry[f"delta_{metric}"] = ov - bv
                    entry[f"ours_{metric}"] = ov
                    entry[f"base_{metric}"] = bv
            ort, brt = _f(ours.get("runtime_sec")), _f(base.get("runtime_sec"))
            entry["delta_runtime_sec"] = (ort - brt) if (ort == ort and brt == brt) else ""
            entry["ours_runtime_sec"] = ours.get("runtime_sec", "")
            entry["base_runtime_sec"] = base.get("runtime_sec", "")
            entry["ours_config"] = ours.get("config", "")
            entry["base_config"] = base.get("config", "")
            pairwise_rows.append(entry)
            if ok_metrics:
                method_pairs[m].append(entry)

    write_csv(out_dir / "family_pairwise_summary.csv", pairwise_rows)

    # Per-family + overall macros
    family_macro_rows = []
    equal_family_rows = []
    claims = {"methods": {}, "notes": []}

    included_families = sorted({
        r["family"] for r in fam_rows if r["included_excluded"] == "included"
    })

    for m in PRINCIPAL:
        entries = method_pairs[m]
        claims["methods"][m] = {}
        for metric in METRICS:
            # per-dataset
            deltas = [_f(e[f"delta_{metric}"]) for e in entries]
            deltas = [d for d in deltas if d == d]
            overall = paired_stats(deltas)
            family_macro_rows.append({
                "baseline": m, "metric": metric, "scope": "per_dataset_all",
                "family": "ALL", **{k: overall[k] for k in overall},
            })

            # per-family medians then equal-family average of family-median deltas
            fam_medians = []
            fam_means = []
            fam_wtl = []
            for fam in included_families:
                fd = [_f(e[f"delta_{metric}"]) for e in entries if e["family"] == fam]
                fd = [d for d in fd if d == d]
                if not fd:
                    continue
                st = paired_stats(fd)
                family_macro_rows.append({
                    "baseline": m, "metric": metric, "scope": "per_family",
                    "family": fam, **{k: st[k] for k in st},
                })
                fam_medians.append(st["median_delta"])
                fam_means.append(st["mean_delta"])
                fam_wtl.append((st["wins"], st["ties"], st["losses"], fam))

            if fam_medians:
                # equal-family: each family one point = family median delta
                eq = paired_stats(fam_medians)
                # reinterpret W/T/L of family-median points
                equal_family_rows.append({
                    "baseline": m, "metric": metric,
                    "n_families": len(fam_medians),
                    "mean_of_family_medians": float(np.mean(fam_medians)),
                    "median_of_family_medians": float(np.median(fam_medians)),
                    "family_points_favor_ours": eq["wins"],
                    "family_points_tie": eq["ties"],
                    "family_points_favor_baseline": eq["losses"],
                    "ci_lo": eq["ci_lo"], "ci_hi": eq["ci_hi"],
                    "ci_excludes_zero": eq["ci_excludes_zero"],
                    "families": "|".join(f for *_, f in fam_wtl),
                })
                claims["methods"][m][metric] = {
                    "per_dataset": overall,
                    "equal_family_mean_of_medians": float(np.mean(fam_medians)),
                    "equal_family_n": len(fam_medians),
                    "ours_better_if_negative_mean": True,
                }

    write_csv(out_dir / "family_macro_summary.csv", family_macro_rows)
    write_csv(out_dir / "equal_family_macro.csv", equal_family_rows)

    # LOFO: drop each family, recompute equal-family mean of family-medians for upset_simple
    lofo_rows = []
    for m in PRINCIPAL:
        entries = method_pairs[m]
        for drop in included_families + ["NONE"]:
            keep = [f for f in included_families if f != drop]
            fam_meds = []
            for fam in keep:
                fd = [_f(e["delta_upset_simple"]) for e in entries if e["family"] == fam]
                fd = [d for d in fd if d == d]
                if fd:
                    fam_meds.append(float(np.median(fd)))
            if not fam_meds:
                continue
            lofo_rows.append({
                "baseline": m,
                "dropped_family": drop,
                "n_families": len(fam_meds),
                "equal_family_mean_delta_upset_simple": float(np.mean(fam_meds)),
                "equal_family_median_delta_upset_simple": float(np.median(fam_meds)),
                "n_family_points_ours_better": sum(1 for d in fam_meds if d < -TIE_EPS),
                "n_family_points_baseline_better": sum(1 for d in fam_meds if d > TIE_EPS),
                "n_family_points_tie": sum(1 for d in fam_meds if abs(d) <= TIE_EPS),
            })
    write_csv(out_dir / "leave_one_family_out.csv", lofo_rows)

    # Basketball-collapsed: treat Basketball_coarse ∪ Basketball_finer as one meta-family
    bb_rows = []
    for m in PRINCIPAL:
        entries = method_pairs[m]
        for metric in METRICS:
            collapsed = []
            # non-basketball families as-is
            for fam in included_families:
                if fam.startswith("Basketball"):
                    continue
                fd = [_f(e[f"delta_{metric}"]) for e in entries if e["family"] == fam]
                fd = [d for d in fd if d == d]
                if fd:
                    collapsed.append(("family:" + fam, float(np.median(fd))))
            # one basketball point
            bb = [_f(e[f"delta_{metric}"]) for e in entries if e["family"].startswith("Basketball")]
            bb = [d for d in bb if d == d]
            if bb:
                collapsed.append(("meta:Basketball_all", float(np.median(bb))))
            vals = [v for _, v in collapsed]
            st = paired_stats(vals)
            bb_rows.append({
                "baseline": m, "metric": metric,
                "n_points": len(vals),
                "points": "|".join(n for n, _ in collapsed),
                "mean_of_point_medians": float(np.mean(vals)) if vals else np.nan,
                "median_of_point_medians": float(np.median(vals)) if vals else np.nan,
                "wins_ours": st["wins"], "ties": st["ties"], "losses_ours": st["losses"],
            })
    write_csv(out_dir / "basketball_collapsed_summary.csv", bb_rows)

    # Hierarchical bootstrap: resample families, then datasets within family
    hier_rows = []
    rng = np.random.default_rng(BOOT_SEED)
    for m in PRINCIPAL:
        entries = method_pairs[m]
        by_fam = defaultdict(list)
        for e in entries:
            if e["family"] not in included_families:
                continue
            d = _f(e["delta_upset_simple"])
            if d == d:
                by_fam[e["family"]].append(d)
        fams = [f for f in included_families if by_fam[f]]
        if len(fams) < 2:
            continue
        boot_means = []
        for _ in range(BOOT_N):
            # resample families with replacement
            chosen = [fams[i] for i in rng.integers(0, len(fams), size=len(fams))]
            fam_meds = []
            for fam in chosen:
                vals = by_fam[fam]
                # resample datasets within family
                sample = [vals[i] for i in rng.integers(0, len(vals), size=len(vals))]
                fam_meds.append(float(np.median(sample)))
            boot_means.append(float(np.mean(fam_meds)))
        lo, hi = np.quantile(boot_means, [0.025, 0.975])
        hier_rows.append({
            "baseline": m,
            "metric": "upset_simple",
            "n_families": len(fams),
            "hierarchical_mean": float(np.mean(boot_means)),
            "ci95_lo": float(lo),
            "ci95_hi": float(hi),
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
            "direction": "negative_favors_ours",
        })
    write_csv(out_dir / "hierarchical_bootstrap.csv", hier_rows)

    # High-level claim extraction for upset_simple
    summary_claims = {
        "orientation": "delta = OURS - baseline; negative favors OURS (lower upset)",
        "principal_baselines": PRINCIPAL,
        "included_families": included_families,
        "per_baseline_upset_simple": {},
        "survival": {},
    }
    for m in PRINCIPAL:
        eq = next((r for r in equal_family_rows if r["baseline"] == m and r["metric"] == "upset_simple"), None)
        per = next((r for r in family_macro_rows if r["baseline"] == m and r["metric"] == "upset_simple" and r["scope"] == "per_dataset_all"), None)
        lofo_drop_bb = [r for r in lofo_rows if r["baseline"] == m and r["dropped_family"] in ("Basketball_coarse", "Basketball_finer", "NONE")]
        hier = next((r for r in hier_rows if r["baseline"] == m), None)
        summary_claims["per_baseline_upset_simple"][m] = {
            "per_dataset_n": per["n"] if per else 0,
            "per_dataset_wtl": f"{per['wins']}/{per['ties']}/{per['losses']}" if per else None,
            "per_dataset_median_delta": per["median_delta"] if per else None,
            "equal_family_mean_of_medians": eq["mean_of_family_medians"] if eq else None,
            "equal_family_family_wtl": (
                f"{eq['family_points_favor_ours']}/{eq['family_points_tie']}/{eq['family_points_favor_baseline']}"
                if eq else None
            ),
            "hierarchical_ci_excludes_zero": hier["ci_excludes_zero"] if hier else None,
            "hierarchical_mean": hier["hierarchical_mean"] if hier else None,
        }
        # Does equal-family still favor OURS?
        if eq:
            survives = eq["mean_of_family_medians"] < 0
            summary_claims["survival"][m] = {
                "equal_family_favors_ours": survives,
                "per_dataset_favors_ours": (per["median_delta"] < 0) if per else None,
            }

    # Basketball dependence: compare NONE vs dropping both basketball families
    bb_dep = {}
    for m in PRINCIPAL:
        none = next((r for r in lofo_rows if r["baseline"] == m and r["dropped_family"] == "NONE"), None)
        # drop coarse then look at mean; also simulate drop both by filtering
        entries = method_pairs[m]
        keep_fams = [f for f in included_families if not f.startswith("Basketball")]
        fam_meds = []
        for fam in keep_fams:
            fd = [_f(e["delta_upset_simple"]) for e in entries if e["family"] == fam]
            fd = [d for d in fd if d == d]
            if fd:
                fam_meds.append(float(np.median(fd)))
        bb_dep[m] = {
            "with_basketball_equal_family_mean": none["equal_family_mean_delta_upset_simple"] if none else None,
            "without_any_basketball_equal_family_mean": float(np.mean(fam_meds)) if fam_meds else None,
            "n_families_without_basketball": len(fam_meds),
            "sign_flip": (
                none is not None and fam_meds and
                (none["equal_family_mean_delta_upset_simple"] < 0) != (float(np.mean(fam_meds)) < 0)
            ),
        }
    summary_claims["basketball_dependence"] = bb_dep

    # BTL upset_ratio specifically
    btl_ratio = next((r for r in equal_family_rows if r["baseline"] == "btl" and r["metric"] == "upset_ratio"), None)
    summary_claims["btl_upset_ratio_equal_family"] = btl_ratio

    with (out_dir / "family_aware_claims.json").open("w") as f:
        json.dump(summary_claims, f, indent=2, default=str)

    return summary_claims


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--leaderboard", type=Path, default=LB_PATH)
    p.add_argument("--out-dir", type=Path, default=OUT)
    args = p.parse_args(argv)
    claims = analyze(args.leaderboard, args.out_dir)
    print(json.dumps({
        "out": str(args.out_dir),
        "survival": claims.get("survival"),
        "basketball_dependence_sign_flips": {
            k: v["sign_flip"] for k, v in claims.get("basketball_dependence", {}).items()
        },
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
