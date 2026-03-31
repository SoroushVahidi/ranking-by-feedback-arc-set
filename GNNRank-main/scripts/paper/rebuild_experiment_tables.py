#!/usr/bin/env python3
"""Rebuild manuscript-facing experiment tables from canonical repository artifacts.

Uses only stdlib so it can run in minimal environments.
"""

from __future__ import annotations

import csv
import datetime
import json
import math
import statistics
import subprocess
import zipfile
from ast import literal_eval
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Tuple

from method_names import CANONICAL_METHOD_ALIASES, canonicalize_method_name

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_CSV = REPO_ROOT / "paper_csv"
OUTPUT_AUDITS = REPO_ROOT / "outputs" / "audits"
OUTPUT_TABLES = REPO_ROOT / "outputs" / "paper_tables"

LEADERBOARD_PER_METHOD = PAPER_CSV / "leaderboard_per_method.csv"
RESULTS_RA = PAPER_CSV / "results_from_result_arrays.csv"

TIME_BUDGET_SEC = 1800.0
CLASSICAL = {
    "SpringRank", "syncRank", "serialRank", "btl", "davidScore",
    "eigenvectorCentrality", "PageRank", "rankCentrality", "SVD_RS", "SVD_NRS", "mvr",
}
GNN = {"DIGRAC", "ib", "DIGRACib"}
OURS = {"OURS_MFAS", "OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"}


def read_csv(path: Path) -> List[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def to_float(x: str) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return math.nan
    return v


def parse_family(dataset: str) -> str:
    return dataset.split("/", 1)[0] if "/" in dataset else dataset


def candidate_adj_paths(dataset: str) -> List[Path]:
    data_root = REPO_ROOT / "data"
    cands = [data_root / f"{dataset}adj.npz", data_root / dataset / "adj.npz"]
    if dataset.startswith("_AUTO/"):
        cands.append(data_root / dataset / "adj.npz")
    else:
        auto_name = dataset.replace("/", "__") + "adj"
        cands.append(data_root / "_AUTO" / auto_name / "adj.npz")
    return cands


def parse_npy_header(npy_bytes: bytes):
    if npy_bytes[:6] != b"\x93NUMPY":
        raise ValueError("invalid npy magic")
    major = npy_bytes[6]
    if major == 1:
        header_len = int.from_bytes(npy_bytes[8:10], "little")
        header_start = 10
    else:
        header_len = int.from_bytes(npy_bytes[8:12], "little")
        header_start = 12
    header = npy_bytes[header_start: header_start + header_len].decode("latin1")
    meta = literal_eval(header)
    data = npy_bytes[header_start + header_len:]
    return meta, data


def read_npz_shape_nnz(path: Path) -> Tuple[int, int]:
    with zipfile.ZipFile(path, "r") as zf:
        shape_name = next((n for n in zf.namelist() if n.endswith("shape.npy")), None)
        data_name = next((n for n in zf.namelist() if n.endswith("data.npy")), None)
        if not shape_name or not data_name:
            raise ValueError("missing shape.npy or data.npy")
        shape_meta, shape_data = parse_npy_header(zf.read(shape_name))
        data_meta, _ = parse_npy_header(zf.read(data_name))
        # shape.npy stores [n_rows, n_cols] as int array
        descr = shape_meta.get("descr", "<i8")
        itemsize = int(descr[-1]) if descr[-1].isdigit() else 8
        signed = "i" in descr
        vals = []
        for i in range(0, len(shape_data), itemsize):
            chunk = shape_data[i:i+itemsize]
            if len(chunk) < itemsize:
                break
            vals.append(int.from_bytes(chunk, "little", signed=signed))
        n = int(vals[0]) if vals else int(shape_meta["shape"][0])
        d_shape = tuple(data_meta.get("shape", (0,)))
        m = int(d_shape[0]) if d_shape else 0
        return n, m


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def summarize_group(rows: List[dict], total_datasets: int) -> List[dict]:
    by_key = defaultdict(list)
    for r in rows:
        by_key[(r["method"], r["config"])].append(r)
    out = []
    for (method, config), grp in by_key.items():
        us = [to_float(g["upset_simple_mean"]) for g in grp if not math.isnan(to_float(g["upset_simple_mean"]))]
        ur = [to_float(g["upset_ratio_mean"]) for g in grp if not math.isnan(to_float(g["upset_ratio_mean"]))]
        un = [to_float(g["upset_naive_mean"]) for g in grp if not math.isnan(to_float(g["upset_naive_mean"]))]
        out.append({
            "method": method,
            "config": config,
            "method_family": "OURS" if method in OURS else ("GNN" if method in GNN else ("classical" if method in CLASSICAL else "other")),
            "median_upset_simple": statistics.median(us) if us else "",
            "mean_upset_simple": statistics.fmean(us) if us else "",
            "median_upset_ratio": statistics.median(ur) if ur else "",
            "mean_upset_ratio": statistics.fmean(ur) if ur else "",
            "median_upset_naive": statistics.median(un) if un else "",
            "mean_upset_naive": statistics.fmean(un) if un else "",
            "coverage": f"{len(us)} / {total_datasets}",
        })
    out.sort(key=lambda x: float(x["median_upset_simple"]) if x["median_upset_simple"] != "" else 1e18)
    return out


def main() -> None:
    OUTPUT_AUDITS.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    lb_rows = read_csv(LEADERBOARD_PER_METHOD)
    suite = sorted({r["dataset"] for r in lb_rows})
    suite_set = set(suite)

    ra_rows = [r for r in read_csv(RESULTS_RA) if r.get("which") == "upset" and r["dataset"] in suite_set]
    for r in ra_rows:
        r["method"] = canonicalize_method_name(r.get("method", ""))

    # Canonical dataset inventory
    inventory_rows = []
    fam_counter = Counter()
    fam_n = defaultdict(list)
    fam_m = defaultdict(list)
    for ds in suite:
        fam = parse_family(ds)
        fam_counter[fam] += 1
        n = m = ""
        npz_path = ""
        special = []
        for cand in candidate_adj_paths(ds):
            if cand.exists():
                npz_path = str(cand.relative_to(REPO_ROOT))
                try:
                    n_i, m_i = read_npz_shape_nnz(cand)
                    n, m = n_i, m_i
                    fam_n[fam].append(n_i)
                    fam_m[fam].append(m_i)
                except Exception:
                    special.append("npz_unreadable")
                break
        if not npz_path:
            special.append("no_adj_artifact")
        if ds.startswith("_AUTO/"):
            special.append("auto_generated")
        if ds == "ERO/p5K5N350eta10styleuniform":
            special.append("singleton_special_case")
        inventory_rows.append({
            "dataset": ds,
            "family": fam,
            "n_nodes": n,
            "m_edges": m,
            "adj_artifact": npz_path,
            "notes": ";".join(special),
        })

    write_csv(
        OUTPUT_AUDITS / "canonical_dataset_inventory.csv",
        inventory_rows,
        ["dataset", "family", "n_nodes", "m_edges", "adj_artifact", "notes"],
    )

    fam_summary = {}
    for fam, cnt in sorted(fam_counter.items()):
        ns, ms = fam_n.get(fam, []), fam_m.get(fam, [])
        fam_summary[fam] = {
            "dataset_count": cnt,
            "n_nodes_range": [min(ns), max(ns)] if ns else None,
            "m_edges_range": [min(ms), max(ms)] if ms else None,
        }

    with (OUTPUT_AUDITS / "canonical_dataset_inventory_summary.json").open("w") as f:
        json.dump({
            "canonical_dataset_count": len(suite),
            "dataset_count_policy": "Canonical suite equals unique dataset list in paper_csv/leaderboard_per_method.csv; current expected count is 81.",
            "families": fam_summary,
            "special_cases": {
                "auto_generated_count": sum(1 for d in suite if d.startswith("_AUTO/")),
                "singleton_special_dataset": "ERO/p5K5N350eta10styleuniform",
            },
        }, f, indent=2, sort_keys=True)

    with (OUTPUT_AUDITS / "method_name_canonicalization.json").open("w") as f:
        json.dump(
            {
                "policy": "All generated canonical outputs must use canonical method IDs from this mapping.",
                "canonical_aliases": CANONICAL_METHOD_ALIASES,
                "observed_canonical_methods": sorted({r["method"] for r in ra_rows}),
            },
            f,
            indent=2,
            sort_keys=True,
        )

    # Table4 full suite
    t4 = summarize_group(ra_rows, len(suite))
    write_csv(
        OUTPUT_TABLES / "table4_full_suite.csv",
        t4,
        ["method", "config", "method_family", "median_upset_simple", "mean_upset_simple", "median_upset_ratio", "mean_upset_ratio", "median_upset_naive", "mean_upset_naive", "coverage"],
    )

    # Table5 compute matched
    cm_rows = []
    for r in ra_rows:
        rt = to_float(r.get("runtime_sec_mean", ""))
        if not math.isnan(rt) and rt <= TIME_BUDGET_SEC:
            cm_rows.append(r)
    t5 = summarize_group(cm_rows, len(suite))
    write_csv(OUTPUT_TABLES / "table5_compute_matched.csv", t5, list(t5[0].keys()) if t5 else ["method", "config", "method_family", "median_upset_simple", "mean_upset_simple", "median_upset_ratio", "mean_upset_ratio", "median_upset_naive", "mean_upset_naive", "coverage"])

    # Table6 missingness
    by_key = defaultdict(list)
    for r in ra_rows:
        by_key[(r["method"], r["config"])].append(r)
    t6 = []
    for (method, config), grp in sorted(by_key.items()):
        valid_metrics = sum(1 for g in grp if not math.isnan(to_float(g["upset_simple_mean"])))
        valid_runtime = sum(1 for g in grp if not math.isnan(to_float(g["runtime_sec_mean"])))
        timeouts = sum(1 for g in grp if math.isnan(to_float(g["runtime_sec_mean"])) or to_float(g["runtime_sec_mean"]) >= TIME_BUDGET_SEC)
        fin = [g for g in grp if parse_family(g["dataset"]).lower() == "finance"]
        finance_status = "absent"
        if fin:
            f = fin[0]
            finance_status = "timeout_or_missing" if (math.isnan(to_float(f.get("runtime_sec_mean", ""))) or to_float(f.get("runtime_sec_mean", "")) >= TIME_BUDGET_SEC) else "completed"
        t6.append({
            "method": method,
            "config": config,
            "valid_metrics": valid_metrics,
            "valid_runtime": valid_runtime,
            "timeouts_or_missing_runtime": timeouts,
            "finance_status": finance_status,
        })
    write_csv(OUTPUT_TABLES / "table6_missingness.csv", t6, ["method", "config", "valid_metrics", "valid_runtime", "timeouts_or_missing_runtime", "finance_status"])

    # Table7 best-in-suite comparisons
    by_ds = defaultdict(list)
    for r in ra_rows:
        by_ds[r["dataset"]].append(r)
    ours_vs_classical = ours_vs_gnn = 0
    both_available_classical = both_available_gnn = 0
    best_rows = []
    for ds, grp in sorted(by_ds.items()):
        ours_rows = [g for g in grp if g["method"] in OURS and not math.isnan(to_float(g["upset_simple_mean"]))]
        cl_rows = [g for g in grp if g["method"] in CLASSICAL and not math.isnan(to_float(g["upset_simple_mean"]))]
        gnn_rows = [g for g in grp if g["method"] in GNN and not math.isnan(to_float(g["upset_simple_mean"]))]
        best_ours = min(ours_rows, key=lambda x: to_float(x["upset_simple_mean"])) if ours_rows else None
        best_cl = min(cl_rows, key=lambda x: to_float(x["upset_simple_mean"])) if cl_rows else None
        best_gnn = min(gnn_rows, key=lambda x: to_float(x["upset_simple_mean"])) if gnn_rows else None
        if best_ours and best_cl:
            both_available_classical += 1
            if to_float(best_ours["upset_simple_mean"]) <= to_float(best_cl["upset_simple_mean"]):
                ours_vs_classical += 1
        if best_ours and best_gnn:
            both_available_gnn += 1
            if to_float(best_ours["upset_simple_mean"]) <= to_float(best_gnn["upset_simple_mean"]):
                ours_vs_gnn += 1
        best_rows.append({
            "dataset": ds,
            "best_ours_method": best_ours["method"] if best_ours else "",
            "best_ours_upset_simple": best_ours["upset_simple_mean"] if best_ours else "",
            "best_classical_method": best_cl["method"] if best_cl else "",
            "best_classical_upset_simple": best_cl["upset_simple_mean"] if best_cl else "",
            "best_gnn_method": best_gnn["method"] if best_gnn else "",
            "best_gnn_upset_simple": best_gnn["upset_simple_mean"] if best_gnn else "",
        })
    write_csv(OUTPUT_TABLES / "table7_best_in_suite.csv", best_rows, list(best_rows[0].keys()))

    # Table8 runtime tradeoff + pareto
    rt_rows = []
    pareto_ours = 0
    pareto_total = 0
    for row in best_rows:
        ds = row["dataset"]
        grp = by_ds[ds]
        ours_cands = [g for g in grp if g["method"] in OURS and not math.isnan(to_float(g["runtime_sec_mean"])) and not math.isnan(to_float(g["upset_simple_mean"]))]
        base_cands = [g for g in grp if g["method"] in CLASSICAL.union(GNN) and not math.isnan(to_float(g["runtime_sec_mean"])) and not math.isnan(to_float(g["upset_simple_mean"]))]
        if not ours_cands or not base_cands:
            continue
        pareto_total += 1
        ours_best = min(ours_cands, key=lambda x: to_float(x["upset_simple_mean"]))
        base_best = min(base_cands, key=lambda x: to_float(x["upset_simple_mean"]))
        ours_rt = to_float(ours_best["runtime_sec_mean"])
        base_rt = to_float(base_best["runtime_sec_mean"])
        speedup = (base_rt / ours_rt) if ours_rt > 0 else math.nan
        ours_not_dominated = any(
            to_float(o["upset_simple_mean"]) <= to_float(b["upset_simple_mean"]) and to_float(o["runtime_sec_mean"]) <= to_float(b["runtime_sec_mean"])
            for o in ours_cands for b in base_cands
        )
        if ours_not_dominated:
            pareto_ours += 1
        rt_rows.append({
            "dataset": ds,
            "ours_method": ours_best["method"],
            "ours_runtime_sec": ours_rt,
            "baseline_method": base_best["method"],
            "baseline_runtime_sec": base_rt,
            "speedup_baseline_over_ours": speedup,
            "ours_not_dominated": int(ours_not_dominated),
        })
    write_csv(OUTPUT_TABLES / "table8_runtime_tradeoff.csv", rt_rows, ["dataset", "ours_method", "ours_runtime_sec", "baseline_method", "baseline_runtime_sec", "speedup_baseline_over_ours", "ours_not_dominated"])

    # Master claims
    methods = defaultdict(set)
    for r in ra_rows:
        methods[r["method"]].add(r["dataset"])
    claims = {
        "canonical_dataset_count": len(suite),
        "ours_vs_best_classical_wins": ours_vs_classical,
        "ours_vs_best_classical_denominator": both_available_classical,
        "ours_vs_best_gnn_wins": ours_vs_gnn,
        "ours_vs_best_gnn_denominator": both_available_gnn,
        "pareto_ours_not_dominated": pareto_ours,
        "pareto_denominator": pareto_total,
        "finance_status_by_ours_variant": {
            f"{m}|{c}": next((r["finance_status"] for r in t6 if r["method"] == m and r["config"] == c), "absent")
            for (m, c) in sorted({(r["method"], r["config"]) for r in ra_rows if r["method"] in OURS})
        },
        "method_dataset_coverage": {m: len(ds) for m, ds in sorted(methods.items())},
    }
    with (OUTPUT_TABLES / "paper_claims_master.json").open("w") as f:
        json.dump(claims, f, indent=2, sort_keys=True)

    claim_traceability = {
        "dataset_count_claim": {
            "canonical_output_file": "outputs/audits/canonical_dataset_inventory_summary.json",
            "key": "canonical_dataset_count",
            "upstream_sources": [
                "paper_csv/leaderboard_per_method.csv",
                "paper_csv/results_from_result_arrays.csv",
            ],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
        },
        "table4_full_suite_claims": {
            "canonical_output_file": "outputs/paper_tables/table4_full_suite.csv",
            "row_key": ["method", "config"],
            "upstream_sources": ["paper_csv/results_from_result_arrays.csv"],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
        },
        "table5_compute_matched_claims": {
            "canonical_output_file": "outputs/paper_tables/table5_compute_matched.csv",
            "row_key": ["method", "config"],
            "upstream_sources": ["paper_csv/results_from_result_arrays.csv"],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
            "filter": "runtime_sec_mean <= 1800",
        },
        "missingness_claims": {
            "canonical_output_file": "outputs/paper_tables/table6_missingness.csv",
            "row_key": ["method", "config"],
            "upstream_sources": ["paper_csv/results_from_result_arrays.csv"],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
        },
        "best_in_suite_claims": {
            "canonical_output_file": "outputs/paper_tables/table7_best_in_suite.csv",
            "row_key": ["dataset"],
            "upstream_sources": ["paper_csv/results_from_result_arrays.csv"],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
        },
        "runtime_pareto_claims": {
            "canonical_output_file": "outputs/paper_tables/table8_runtime_tradeoff.csv",
            "row_key": ["dataset"],
            "upstream_sources": ["paper_csv/results_from_result_arrays.csv"],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
        },
        "claims_master": {
            "canonical_output_file": "outputs/paper_tables/paper_claims_master.json",
            "key": "top_level_fields",
            "upstream_sources": [
                "outputs/paper_tables/table6_missingness.csv",
                "outputs/paper_tables/table7_best_in_suite.csv",
                "outputs/paper_tables/table8_runtime_tradeoff.csv",
            ],
            "generation_script": "scripts/paper/rebuild_experiment_tables.py",
        },
    }
    with (OUTPUT_TABLES / "claim_traceability.json").open("w") as f:
        json.dump(claim_traceability, f, indent=2, sort_keys=True)

    canonical_methods = sorted({r["method"] for r in ra_rows})
    lines = [
        "# Canonical Artifacts Summary",
        "",
        f"- Canonical dataset count: **{len(suite)}**",
        f"- Canonical methods ({len(canonical_methods)}): `{', '.join(canonical_methods)}`",
        "- Canonical dataset policy: 81 datasets; no canonical 80-dataset subset.",
        "",
        "## Use these files for claims",
        "- Dataset inventory/counts: `outputs/audits/canonical_dataset_inventory.csv`, `outputs/audits/canonical_dataset_inventory_summary.json`",
        "- Full-suite method rows: `outputs/paper_tables/table4_full_suite.csv`",
        "- Compute-matched rows: `outputs/paper_tables/table5_compute_matched.csv`",
        "- Missingness/timeout: `outputs/paper_tables/table6_missingness.csv`",
        "- Best-in-suite: `outputs/paper_tables/table7_best_in_suite.csv`",
        "- Runtime/Pareto tradeoff: `outputs/paper_tables/table8_runtime_tradeoff.csv`",
        "- Claims bundle: `outputs/paper_tables/paper_claims_master.json`",
        "- Claim trace map: `outputs/paper_tables/claim_traceability.json`",
        "",
        "## Caveats",
        "- Finance completion/timeout is method+config specific (see table6 and paper_claims_master).",
        "- Archived legacy manuscript-support files are provenance-only and not canonical.",
    ]
    (OUTPUT_TABLES / "canonical_artifacts_summary.md").write_text("\n".join(lines) + "\n")

    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    git_commit = ""
    try:
        git_commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True)
            .strip()
        )
    except Exception:
        git_commit = "unknown"
    output_files = [
        "outputs/audits/canonical_dataset_inventory.csv",
        "outputs/audits/canonical_dataset_inventory_summary.json",
        "outputs/audits/method_name_canonicalization.json",
        "outputs/paper_tables/table4_full_suite.csv",
        "outputs/paper_tables/table5_compute_matched.csv",
        "outputs/paper_tables/table6_missingness.csv",
        "outputs/paper_tables/table7_best_in_suite.csv",
        "outputs/paper_tables/table8_runtime_tradeoff.csv",
        "outputs/paper_tables/paper_claims_master.json",
        "outputs/paper_tables/claim_traceability.json",
        "outputs/paper_tables/canonical_artifacts_summary.md",
    ]
    provenance = {
        "generator_script": "scripts/paper/rebuild_experiment_tables.py",
        "generated_at_utc": ts,
        "git_commit": git_commit,
        "upstream_sources": [
            "paper_csv/results_from_result_arrays.csv",
            "paper_csv/leaderboard_per_method.csv",
            "data/**/adj.npz",
            "data/_AUTO/**/adj.npz",
        ],
        "dataset_count_policy": "Canonical dataset count is fixed by the suite manifest in paper_csv/leaderboard_per_method.csv and must equal 81.",
        "filtering_policy": {
            "metrics_rows": "which == upset",
            "dataset_filter": "dataset in canonical suite manifest",
            "compute_matched": "runtime_sec_mean <= 1800",
            "finance_timeout_claim": "reported per method+config, never globally assumed",
        },
        "generated_outputs": output_files,
    }
    with (OUTPUT_TABLES / "provenance_manifest.json").open("w") as f:
        json.dump(provenance, f, indent=2, sort_keys=True)

    print("Rebuilt experiment tables and audits.")


if __name__ == "__main__":
    main()
