#!/usr/bin/env python3
"""OURS phase-ablation runner: Phase-A-only vs legacy topo-order add-back vs
exact reachability-aware add-back, with and without Phase-C ratio refinement.

Journal of Supercomputing major-revision context (see
docs/journal_supercomputing_revision_20260824/): the central question this
script answers is whether replacing the legacy fixed-topological-order add-back
(OURS_MFAS / OURS_MFAS_INS1..3) with an exact-reachability add-back
(OURS_MFAS_REACH) restores more edges, changes the induced ranking, and
improves upset metrics -- rather than merely densifying the same DAG/order.

Dataset coverage
-----------------
This script runs on every dataset in outputs/derived/dataset_inventory.csv
marked in_80_suite=True, EXCEPT:
  - "_AUTO/Basketball_temporal__1985adj": excluded from the canonical 80-suite
    upstream (duplicate/legacy artifact; see docs/audits/).
  - "ERO/p5K5N350eta10styleuniform": the on-disk artifacts for this dataset are
    pickled torch_geometric Data splits, not a bare adjacency .npz, and
    load_real_data() cannot resolve it directly. Reconstructing an adjacency
    matrix from the .pk split would require duplicating generate_data.py's
    edge_index/edge_weight -> sparse-matrix logic. This is a known, clearly
    recorded BLOCKER (see docs/journal_supercomputing_revision_20260824/
    REVISION_EXPERIMENT_PLAN.md); it is not fabricated data and is not
    silently skipped -- it is excluded up front and reported here.

That leaves 79 of the 80 canonical datasets. Four dataset names
(Dryad_animal_society, finance, Halo2BetaData, Halo2BetaData/HeadToHead)
resolve to a different on-disk layout than preprocess.load_real_data()
expects (a bare "<name>/adj.npz" rather than "<name>adj.npz"); this script's
_robust_load_real_data() tries load_real_data() first and falls back to the
"<name>/adj.npz" layout, which resolves all four. This bug in the original
run_phase_ablation.py's hardcoded DATASETS list (it used "Dryad_animal_society"
without the trailing "/") is what caused the harness to error out once its
missing-dependency blockers (numpy/scipy, latextable, torch_geometric) were
resolved in this environment; see ADDBACK_DIAGNOSIS.md for the full account.

Phase modes
-----------
  A0            Phase A only (local-ratio cycle breaking), no add-back, no refinement.
  A1_topo       Phase A + legacy topo-order add-back (INS3, 3 passes), no refinement.
  A2_topo       Phase A + legacy topo-order add-back (INS3) + Phase-C ratio refinement.
  B1_reach      Phase A + exact reachability-aware add-back, no refinement.
  B2_reach      Phase A + exact reachability-aware add-back + Phase-C ratio refinement.

Output
------
  outputs/ablation/phase_ablation_results.csv   one row per (dataset, phase_mode)
  outputs/ablation/phase_ablation_summary.md    aggregate comparison + answers to
                                                 the section-O stopping-point questions
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]      # GNNRank-main/
TOP_ROOT = REPO_ROOT.parent                            # repository root
OUT_DIR = REPO_ROOT / "outputs" / "ablation"
OUT_CSV = OUT_DIR / "phase_ablation_results.csv"
OUT_MD = OUT_DIR / "phase_ablation_summary.md"
INVENTORY_CSV = TOP_ROOT / "outputs" / "derived" / "dataset_inventory.csv"

EXCLUDED_DATASETS = {
    "_AUTO/Basketball_temporal__1985adj": "excluded from canonical 80-suite upstream",
    "ERO/p5K5N350eta10styleuniform": (
        "on-disk artifacts are pickled torch_geometric Data splits, not a bare "
        "adjacency .npz; load_real_data() cannot resolve it (documented blocker)"
    ),
}

FIELDNAMES = [
    "dataset", "family", "n", "m", "density",
    "phase_mode", "addback_mode",
    "upset_simple", "upset_ratio", "upset_naive",
    "runtime_sec", "time_phase1_sec", "time_phase2_sec", "time_phaseC_sec",
    "removed_phaseA", "kept_after_phaseA", "kept_final", "edges_restored",
    "reinserted_per_pass", "break_reason",
    "reach_checked", "reach_inserted", "reach_rejected_reachable", "reach_dense_matrix_used",
    "permutation_changed_vs_A_only",
    "status", "note",
]


def _write_blocked(reason: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerow({"status": "blocked", "note": reason})
    OUT_MD.write_text(
        "# Phase ablation summary\n\nExecution blocked in this environment.\n\n"
        f"Reason: {reason}\n"
    )


def _upset_simple(A, scores):
    import numpy as np
    src, dst = A.nonzero()
    w = np.asarray(A[src, dst]).reshape(-1)
    si = scores[src]
    sj = scores[dst]
    mask = si <= sj
    if len(w) == 0:
        return math.nan
    return float(np.sum(w[mask]) / np.sum(w))


def _upset_naive(A, scores):
    import numpy as np
    src, dst = A.nonzero()
    w = np.asarray(A[src, dst]).reshape(-1)
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


def _robust_load_real_data(load_real_data_fn, dataset: str):
    """load_real_data() with a fallback for the "<name>/adj.npz" on-disk layout."""
    try:
        return load_real_data_fn(dataset)
    except FileNotFoundError:
        pass
    import scipy.sparse as sp
    fallback = REPO_ROOT / "data" / dataset / "adj.npz"
    return sp.load_npz(str(fallback))


def _load_dataset_list():
    if not INVENTORY_CSV.exists():
        raise FileNotFoundError(f"dataset inventory not found: {INVENTORY_CSV}")
    rows = list(csv.DictReader(INVENTORY_CSV.open()))
    out = []
    for r in rows:
        if r.get("in_80_suite") != "True":
            continue
        ds = r["dataset"]
        if ds in EXCLUDED_DATASETS:
            continue
        out.append((ds, r.get("family", "")))
    out.sort()
    return out


def main() -> int:
    try:
        import numpy as np
        import scipy.sparse as sp
    except Exception as e:
        _write_blocked(f"Missing numeric dependencies: {e}")
        print(f"Blocked: {e}")
        return 0

    sys.path.append(str(REPO_ROOT / "src"))
    try:
        from comparison import ours_MFAS_INS3, ours_MFAS_REACH
        from preprocess import load_real_data
    except Exception as e:
        _write_blocked(f"Unable to import project modules: {e}")
        print(f"Blocked: {e}")
        return 0

    try:
        datasets = _load_dataset_list()
    except Exception as e:
        _write_blocked(f"Unable to load dataset inventory: {e}")
        print(f"Blocked: {e}")
        return 0

    # Bounded per-run time budget. Kept well below the 900s default used
    # elsewhere in the repo because one dataset ("finance", n=1315, m=1.7M,
    # density~1.0 -- see REVISION_EXPERIMENT_PLAN.md) is already known from
    # prior audits ("OURS_MFAS times out on finance in all configs") to be
    # pathologically slow for the pure-Python Phase-A cycle-peeling loop; a
    # tight per-run cap plus incremental result writing (below) means a slow
    # or interrupted run never loses already-computed rows for other datasets.
    TIME_LIMIT = 60.0

    rows = []
    load_failures = []

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_file = OUT_CSV.open("w", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
    writer.writeheader()
    csv_file.flush()

    def _emit(row: dict) -> None:
        rows.append(row)
        writer.writerow(row)
        csv_file.flush()

    def _run_dataset(ds: str, family: str) -> None:
        try:
            A = _robust_load_real_data(load_real_data, ds)
        except Exception as e:
            load_failures.append((ds, str(e)))
            _emit({k: "" for k in FIELDNAMES} | {
                "dataset": ds, "family": family, "status": "load_failed", "note": str(e)[:200],
            })
            return

        n = int(A.shape[0])
        m = int(A.nnz)
        density = m / (n * (n - 1)) if n > 1 else float("nan")
        t0 = time.time()

        # A0: Phase A only (baseline permutation for "did the ranking change" checks)
        s_a0, meta_a0 = ours_MFAS_INS3(
            A, enable_phase_b=False, enable_phase_c=False, refine_ratio=False,
            time_limit_sec=TIME_LIMIT,
        )
        perm_a0 = tuple(np.argsort(-s_a0).tolist())
        _emit({
            "dataset": ds, "family": family, "n": n, "m": m, "density": density,
            "phase_mode": "A0", "addback_mode": "none",
            "upset_simple": _upset_simple(A, s_a0),
            "upset_ratio": _upset_ratio(A, s_a0),
            "upset_naive": _upset_naive(A, s_a0),
            "runtime_sec": meta_a0.get("runtime_sec"),
            "time_phase1_sec": meta_a0.get("time_phase1_sec"),
            "time_phase2_sec": meta_a0.get("time_phase2_sec"),
            "time_phaseC_sec": meta_a0.get("time_phaseC_sec"),
            "removed_phaseA": meta_a0.get("removed_phaseA"),
            "kept_after_phaseA": meta_a0.get("kept_after_phaseA"),
            "kept_final": meta_a0.get("kept_final"),
            "edges_restored": 0,
            "reinserted_per_pass": "|".join(str(x) for x in meta_a0.get("reinserted_per_pass", [])),
            "break_reason": meta_a0.get("break_reason"),
            "reach_checked": "", "reach_inserted": "", "reach_rejected_reachable": "",
            "reach_dense_matrix_used": "",
            "permutation_changed_vs_A_only": False,
            "status": "ok", "note": "",
        })

        topo_configs = [
            ("A1_topo", dict(enable_phase_b=True, enable_phase_c=False, refine_ratio=False)),
            ("A2_topo", dict(enable_phase_b=True, enable_phase_c=True, refine_ratio=True,
                              refine_time_sec=10.0, refine_passes=2)),
        ]
        for mode_name, kwargs in topo_configs:
            try:
                s, meta = ours_MFAS_INS3(A, time_limit_sec=TIME_LIMIT, **kwargs)
            except Exception as e:
                _emit({k: "" for k in FIELDNAMES} | {
                    "dataset": ds, "family": family, "n": n, "m": m, "density": density,
                    "phase_mode": mode_name, "addback_mode": "topo",
                    "status": "run_failed", "note": str(e)[:200],
                })
                continue
            perm = tuple(np.argsort(-s).tolist())
            _emit({
                "dataset": ds, "family": family, "n": n, "m": m, "density": density,
                "phase_mode": mode_name, "addback_mode": "topo",
                "upset_simple": _upset_simple(A, s),
                "upset_ratio": _upset_ratio(A, s),
                "upset_naive": _upset_naive(A, s),
                "runtime_sec": meta.get("runtime_sec"),
                "time_phase1_sec": meta.get("time_phase1_sec"),
                "time_phase2_sec": meta.get("time_phase2_sec"),
                "time_phaseC_sec": meta.get("time_phaseC_sec"),
                "removed_phaseA": meta.get("removed_phaseA"),
                "kept_after_phaseA": meta.get("kept_after_phaseA"),
                "kept_final": meta.get("kept_final"),
                "edges_restored": meta.get("kept_final", 0) - meta.get("kept_after_phaseA", 0),
                "reinserted_per_pass": "|".join(str(x) for x in meta.get("reinserted_per_pass", [])),
                "break_reason": meta.get("break_reason"),
                "reach_checked": "", "reach_inserted": "", "reach_rejected_reachable": "",
                "reach_dense_matrix_used": "",
                "permutation_changed_vs_A_only": perm != perm_a0,
                "status": "ok", "note": "",
            })

        reach_configs = [
            ("B1_reach", dict(enable_phase_b=True, enable_phase_c=False, refine_ratio=False)),
            ("B2_reach", dict(enable_phase_b=True, enable_phase_c=True, refine_ratio=True,
                               refine_time_sec=10.0, refine_passes=2)),
        ]
        for mode_name, kwargs in reach_configs:
            try:
                s, meta = ours_MFAS_REACH(A, time_limit_sec=TIME_LIMIT, **kwargs)
            except Exception as e:
                _emit({k: "" for k in FIELDNAMES} | {
                    "dataset": ds, "family": family, "n": n, "m": m, "density": density,
                    "phase_mode": mode_name, "addback_mode": "reach",
                    "status": "run_failed", "note": str(e)[:200],
                })
                continue
            perm = tuple(np.argsort(-s).tolist())
            _emit({
                "dataset": ds, "family": family, "n": n, "m": m, "density": density,
                "phase_mode": mode_name, "addback_mode": "reach",
                "upset_simple": _upset_simple(A, s),
                "upset_ratio": _upset_ratio(A, s),
                "upset_naive": _upset_naive(A, s),
                "runtime_sec": meta.get("runtime_sec"),
                "time_phase1_sec": meta.get("time_phase1_sec"),
                "time_phase2_sec": meta.get("time_phase2_sec"),
                "time_phaseC_sec": meta.get("time_phaseC_sec"),
                "removed_phaseA": meta.get("removed_phaseA"),
                "kept_after_phaseA": meta.get("kept_after_phaseA"),
                "kept_final": meta.get("kept_final"),
                "edges_restored": meta.get("kept_final", 0) - meta.get("kept_after_phaseA", 0),
                "reinserted_per_pass": "|".join(str(x) for x in meta.get("reinserted_per_pass", [])),
                "break_reason": meta.get("break_reason"),
                "reach_checked": meta.get("reach_checked"),
                "reach_inserted": meta.get("reach_inserted"),
                "reach_rejected_reachable": meta.get("reach_rejected_reachable"),
                "reach_dense_matrix_used": meta.get("reach_dense_matrix_used"),
                "permutation_changed_vs_A_only": perm != perm_a0,
                "status": "ok", "note": "",
            })

        dt = time.time() - t0
        print(f"[{ds}] n={n} m={m} done in {dt:.2f}s", flush=True)

    try:
        for ds, family in datasets:
            try:
                _run_dataset(ds, family)
            except Exception as e:
                _emit({k: "" for k in FIELDNAMES} | {
                    "dataset": ds, "family": family, "status": "dataset_failed", "note": str(e)[:200],
                })
                print(f"[{ds}] FAILED: {e}", flush=True)
    finally:
        csv_file.close()
        _write_summary(rows, datasets, load_failures)

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    return 0



def _write_summary(rows, datasets, load_failures) -> None:
    import statistics as st

    ok_rows = [r for r in rows if r["status"] == "ok"]
    by_key = {}
    for r in ok_rows:
        by_key.setdefault((r["dataset"], r["phase_mode"]), r)

    ds_list = sorted({r["dataset"] for r in ok_rows})

    def paired(mode_a, mode_b, metric):
        deltas = []
        for ds in ds_list:
            ra = by_key.get((ds, mode_a))
            rb = by_key.get((ds, mode_b))
            if ra is None or rb is None:
                continue
            va, vb = ra[metric], rb[metric]
            if va in ("", None) or vb in ("", None):
                continue
            if isinstance(va, str) or isinstance(vb, str):
                continue
            if (isinstance(va, float) and math.isnan(va)) or (isinstance(vb, float) and math.isnan(vb)):
                continue
            deltas.append((ds, float(vb) - float(va)))
        return deltas

    def wtl(deltas, better_is_lower=True):
        w = sum(1 for _, d in deltas if (d < -1e-12 if better_is_lower else d > 1e-12))
        l = sum(1 for _, d in deltas if (d > 1e-12 if better_is_lower else d < -1e-12))
        t = len(deltas) - w - l
        return w, t, l

    lines = []
    lines.append("# Phase ablation summary\n")
    lines.append("Command:\n\n`python GNNRank-main/scripts/paper/run_phase_ablation.py`\n")
    lines.append(f"\nDatasets attempted: {len(datasets)} (from outputs/derived/dataset_inventory.csv, "
                  f"in_80_suite=True, minus documented exclusions)\n")
    lines.append(f"Datasets successfully loaded and run: {len(ds_list)}\n")
    if load_failures:
        lines.append(f"\nLoad failures ({len(load_failures)}):\n\n")
        for ds, err in load_failures:
            lines.append(f"- `{ds}`: {err[:200]}\n")
    lines.append(f"\nExcluded up front (documented blockers): {len(EXCLUDED_DATASETS)}\n\n")
    for ds, reason in EXCLUDED_DATASETS.items():
        lines.append(f"- `{ds}`: {reason}\n")

    lines.append("\n## Edges restored: legacy topo add-back vs reachability add-back\n\n")
    restored_topo = [r["edges_restored"] for r in ok_rows if r["phase_mode"] == "A1_topo"]
    restored_reach = [r["edges_restored"] for r in ok_rows if r["phase_mode"] == "B1_reach"]
    if restored_topo and restored_reach:
        lines.append(f"- A1_topo total edges restored across suite: {sum(restored_topo)}\n")
        lines.append(f"- B1_reach total edges restored across suite: {sum(restored_reach)}\n")
        n_more = sum(
            1 for ds in ds_list
            if by_key.get((ds, "B1_reach")) and by_key.get((ds, "A1_topo"))
            and by_key[(ds, "B1_reach")]["edges_restored"] > by_key[(ds, "A1_topo")]["edges_restored"]
        )
        lines.append(f"- Datasets where reach restores strictly MORE edges than topo: {n_more}/{len(ds_list)}\n")

    lines.append("\n## Does add-back change the final ranking relative to Phase-A-only?\n\n")
    n_topo_changed = sum(1 for r in ok_rows if r["phase_mode"] == "A1_topo" and r["permutation_changed_vs_A_only"])
    n_reach_changed = sum(1 for r in ok_rows if r["phase_mode"] == "B1_reach" and r["permutation_changed_vs_A_only"])
    n_topo_total = sum(1 for r in ok_rows if r["phase_mode"] == "A1_topo")
    n_reach_total = sum(1 for r in ok_rows if r["phase_mode"] == "B1_reach")
    lines.append(f"- A1_topo changes the permutation vs A-only on {n_topo_changed}/{n_topo_total} datasets\n")
    lines.append(f"- B1_reach changes the permutation vs A-only on {n_reach_changed}/{n_reach_total} datasets\n")

    lines.append("\n## Upset-simple: paired comparisons (lower is better)\n\n")
    for label, ma, mb in [
        ("A1_topo vs A0", "A0", "A1_topo"),
        ("B1_reach vs A0", "A0", "B1_reach"),
        ("B1_reach vs A1_topo", "A1_topo", "B1_reach"),
        ("A2_topo vs A0", "A0", "A2_topo"),
        ("B2_reach vs A0", "A0", "B2_reach"),
        ("B2_reach vs A2_topo", "A2_topo", "B2_reach"),
    ]:
        deltas = paired(ma, mb, "upset_simple")
        if not deltas:
            continue
        w, t, l = wtl(deltas, better_is_lower=True)
        vals = [d for _, d in deltas]
        lines.append(
            f"- **{label}**: n={len(deltas)}, mean delta={st.mean(vals):.6f}, "
            f"median delta={st.median(vals):.6f}, W/T/L (mb better/tie/worse)={w}/{t}/{l}\n"
        )

    lines.append("\n## Runtime overhead (median, seconds)\n\n")
    for mode in ["A0", "A1_topo", "A2_topo", "B1_reach", "B2_reach"]:
        rts = [r["runtime_sec"] for r in ok_rows if r["phase_mode"] == mode and r["runtime_sec"] not in ("", None)]
        if rts:
            lines.append(f"- {mode}: median={st.median(rts):.4f}s, max={max(rts):.4f}s, n={len(rts)}\n")

    lines.append("\n## Per-family breakdown (upset_simple, B1_reach vs A1_topo)\n\n")
    fam_list = sorted({r["family"] for r in ok_rows if r["family"]})
    for fam in fam_list:
        fam_ds = sorted({r["dataset"] for r in ok_rows if r["family"] == fam})
        deltas = []
        for ds in fam_ds:
            ra = by_key.get((ds, "A1_topo"))
            rb = by_key.get((ds, "B1_reach"))
            if ra and rb and isinstance(ra["upset_simple"], float) and isinstance(rb["upset_simple"], float):
                deltas.append(rb["upset_simple"] - ra["upset_simple"])
        if deltas:
            w, t, l = wtl([(None, d) for d in deltas], better_is_lower=True)
            lines.append(f"- **{fam}** (n={len(deltas)}): mean delta={st.mean(deltas):.6f}, W/T/L={w}/{t}/{l}\n")

    OUT_MD.write_text("".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
