#!/usr/bin/env python3
"""MINCUT_PILOT candidate-cap audit: exhaustive (not top-K-capped) scan of the
min-cut exchange operator's unsafe-candidate population, to determine whether
the original pilot's top-20 cap caused false negatives.

NOT a canonical/manuscript-facing script. Operator semantics (min-cut
definition, acceptance rule, deterministic preflow_push backend, numerical
tolerance, reachability restoration, weighted-objective accounting) are
UNCHANGED from GNNRank-main/src/mincut_exchange_prototype.py -- this script
only changes how many candidates are attempted and adds telemetry/feature
recording. comparison.py and ours_mfas.py are not imported for writing,
only read.

Protocol: docs/journal_supercomputing_revision_20260824/MINCUT_CANDIDATE_CAP_AUDIT.md
(analysis document; this script has no separate frozen protocol file since
the task itself is the protocol: exhaustive scan of the two datasets whose
zero-acceptance result under the top-20 cap needs a true-negative /
false-negative determination, per the parent task's Section C).

For each dataset, ONE exhaustive scan is run (all unsafe candidates, stable
descending-weight order, matching the original pilot's convention exactly).
Because nothing in the exchange loop depends on candidates not yet reached,
the first K attempts of an exhaustive scan are bit-for-bit identical to a
top-K-capped run from the same starting state -- so "top-20" / "top-50" /
"top-100" results are derived as PREFIX CHECKPOINTS of the single exhaustive
run, not as separate re-runs, guaranteeing internal consistency by
construction.
"""

from __future__ import annotations

import csv
import math
import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]   # GNNRank-main/
TOP_ROOT = REPO_ROOT.parent
OUT_DIR = TOP_ROOT / "outputs" / "revision_analysis_20260824" / "mincut_candidate_cap_audit"

sys.path.insert(0, str(REPO_ROOT / "src"))

# Primary datasets: EXHAUSTIVE scan, all unsafe candidates.
PRIMARY_DATASETS = [
    ("Dryad_animal_society", "Animal"),
    ("FacultyHiringNetworks/Business/Business_FM_Full_", "Faculty"),
]
# Optional control: exhaustive scan, with top-20/50/100/ALL checkpoints, on a
# dataset that already had accepted exchanges under the top-20 cap.
CONTROL_DATASET = ("Basketball_temporal/1985", "Basketball_coarse")

CHECKPOINTS = [20, 50, 100]  # plus "ALL" implicitly at the end of each scan

# Unchanged from the original pilot (Section D: do not alter operator/budget semantics
# beyond the candidate cap itself).
MAX_ACCEPTED_EXCHANGES = 10
MINCUT_TIME_BUDGET_SEC = 60.0  # generous vs. the ~30s used before, since scans are now longer
PHASE_TIME_LIMIT_SEC = 300.0


def _robust_load_real_data(load_real_data_fn, dataset: str):
    try:
        return load_real_data_fn(dataset)
    except FileNotFoundError:
        pass
    import scipy.sparse as sp
    return sp.load_npz(str(REPO_ROOT / "data" / dataset / "adj.npz"))


def _upset_simple(A, scores):
    import numpy as np
    src, dst = A.nonzero()
    w = np.asarray(A[src, dst]).reshape(-1)
    mask = scores[src] <= scores[dst]
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


def _cheap_pre_mincut_features(n, kept, src, dst, w, u, v, adj_out, adj_in, topo_pos):
    """Compute cheap (no min-cut) features for one candidate edge (u, v),
    per this task's Section I. All computed from the CURRENT kept graph."""
    import networkx as nx

    out_deg_u = len(adj_out.get(u, ()))
    in_deg_u = len(adj_in.get(u, ()))
    out_deg_v = len(adj_out.get(v, ()))
    in_deg_v = len(adj_in.get(v, ()))
    rank_distance = abs(topo_pos[u] - topo_pos[v]) if (u in topo_pos and v in topo_pos) else None

    # Conflict region: descendants(v) intersect ancestors(u), inclusive.
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for ei2 in range(len(src)):
        if kept[ei2]:
            G.add_edge(int(src[ei2]), int(dst[ei2]), weight=float(w[ei2]))
    desc_v = set(nx.descendants(G, v)) | {v} if v in G else {v}
    anc_u = set(nx.descendants(G.reverse(copy=False), u)) | {u} if u in G else {u}
    region = desc_v & anc_u
    region_vertex_count = len(region)
    region_edge_count = sum(1 for a2, b2 in G.edges() if a2 in region and b2 in region)
    region_total_weight = sum(
        G[a2][b2]["weight"] for a2, b2 in G.edges() if a2 in region and b2 in region
    )
    possible_pairs = region_vertex_count * (region_vertex_count - 1) if region_vertex_count > 1 else 0
    region_density = (region_edge_count / possible_pairs) if possible_pairs > 0 else 0.0

    # One deterministic v->u path: BFS by hop count (fixed neighbor iteration
    # order via adj_out's insertion order), first path found.
    path_min_edge_weight = None
    path_total_weight = None
    if v in G and u in G and nx.has_path(G, v, u):
        try:
            path_nodes = nx.shortest_path(G, v, u)  # unweighted (hop-count) shortest path, deterministic for a fixed graph
            path_edge_weights = [
                G[path_nodes[i]][path_nodes[i + 1]]["weight"] for i in range(len(path_nodes) - 1)
            ]
            path_min_edge_weight = min(path_edge_weights) if path_edge_weights else None
            path_total_weight = sum(path_edge_weights) if path_edge_weights else None
        except Exception:
            pass

    return {
        "out_deg_u": out_deg_u, "in_deg_u": in_deg_u,
        "out_deg_v": out_deg_v, "in_deg_v": in_deg_v,
        "rank_distance": rank_distance,
        "conflict_region_vertices": region_vertex_count,
        "conflict_region_edges": region_edge_count,
        "conflict_region_total_weight": region_total_weight,
        "conflict_region_density": region_density,
        "conflict_region_vertex_fraction": region_vertex_count / n if n else 0.0,
        "path_min_edge_weight": path_min_edge_weight,
        "path_total_weight": path_total_weight,
    }


def _run_exhaustive_scan(ds, family, checkpoints):
    import numpy as np
    from ours_mfas import ours_mfas_rmfa, _csr_to_edges, _scores_from_kept_edges, _toposort_kahn_from_edges
    from mincut_exchange_prototype import _try_mincut_exchange
    from preprocess import load_real_data

    A = _robust_load_real_data(load_real_data, ds)
    n = int(A.shape[0])
    m = int(A.nnz)
    n_, src, dst, w = _csr_to_edges(A)
    assert n_ == n

    _, meta1 = ours_mfas_rmfa(A, enable_phase_b=True, addback_mode="reach", enable_phase_c=False,
                               refine_naive=False, time_limit_sec=PHASE_TIME_LIMIT_SEC, return_meta=True)
    kept1 = np.array(meta1["kept_final_mask"], dtype=bool)

    topo = _toposort_kahn_from_edges(n, src, dst, kept1)
    topo_pos = {int(node): i for i, node in enumerate(topo)} if topo is not None else {}

    adj_out, adj_in = {}, {}
    for ei in range(len(src)):
        if kept1[ei]:
            adj_out.setdefault(int(src[ei]), []).append(ei)
            adj_in.setdefault(int(dst[ei]), []).append(ei)

    order = np.argsort(-w, kind="mergesort")
    unsafe = [int(ei) for ei in order if not kept1[ei]]
    n_unsafe_total = len(unsafe)

    kept_running = kept1.copy()
    n_accepted = 0
    attempt_log = []
    checkpoint_snapshots = {}  # checkpoint (int or "ALL") -> kept mask copy at that point
    t_loop0 = time.time()

    for rank, ei in enumerate(unsafe):
        if n_accepted >= MAX_ACCEPTED_EXCHANGES:
            break
        if (time.time() - t_loop0) > MINCUT_TIME_BUDGET_SEC:
            break

        u = int(src[ei])
        v = int(dst[ei])
        features = _cheap_pre_mincut_features(n, kept_running, src, dst, w, u, v, adj_out, adj_in, topo_pos)

        diag = _try_mincut_exchange(n, kept_running, src, dst, w, ei)
        removed_before = float(w[~kept_running].sum())

        attempted_index = rank + 1  # 1-indexed count of attempts made so far (this one included)

        row = {
            "dataset": ds, "n": n, "m": m,
            "original_candidate_rank": rank,  # 0-indexed static rank in descending-weight order
            "attempt_index": attempted_index,
            "u": u, "v": v,
            "candidate_weight": diag["candidate_weight"],
            "reachability_before": diag["reachability_before"],
            "cut_value": diag["cut_weight"],
            "cut_size": len(diag["cut_edges"]) if diag["cut_edges"] is not None else "",
            "improvement_margin": (
                diag["candidate_weight"] - diag["cut_weight"]
                if (diag["candidate_weight"] is not None and diag["cut_weight"] is not None) else ""
            ),
            "objective_delta": diag["objective_delta"],
            "accepted": diag["accepted"],
            "reason": diag["reason"],
            "mincut_runtime_sec": diag["runtime_sec"],
            "cumulative_runtime_sec": time.time() - t_loop0,
            "structural_objective_before": removed_before,
            "would_be_excluded_by_top20": attempted_index > 20,
            **features,
        }
        attempt_log.append(row)

        if diag["accepted"]:
            kept_running = diag["new_kept"]
            n_accepted += 1

        for cp in checkpoints:
            if attempted_index == cp and cp not in checkpoint_snapshots:
                checkpoint_snapshots[cp] = kept_running.copy()

    checkpoint_snapshots["ALL"] = kept_running.copy()
    # structural_objective_after per row: carried forward exactly via the accounting
    # identity (removed_after = removed_before - candidate_weight + cut_value) rather
    # than replaying edge masks, since non-accepted rows never change state.
    running_removed = float(w[~kept1].sum())
    for row in attempt_log:
        if row["accepted"]:
            running_removed = running_removed - row["candidate_weight"] + row["cut_value"]
        row["structural_objective_after"] = running_removed

    return {
        "ds": ds, "family": family, "n": n, "m": m,
        "n_unsafe_total": n_unsafe_total,
        "attempt_log": attempt_log,
        "checkpoint_snapshots": checkpoint_snapshots,
        "kept1": kept1,
        "A": A,
        "src": src, "dst": dst, "w": w,
        "n_accepted_total": n_accepted,
        "total_scan_time_sec": time.time() - t_loop0,
    }


def main() -> int:
    import numpy as np
    from ours_mfas import _scores_from_kept_edges

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_attempt_rows = []
    dataset_comparison_rows = []
    feature_rows = []

    scan_targets = list(PRIMARY_DATASETS)
    # Optional control: include if primary scans are fast (checked after running them).
    results = {}
    for ds, family in scan_targets:
        print(f"[{ds}] exhaustive scan starting...", flush=True)
        t0 = time.time()
        res = _run_exhaustive_scan(ds, family, CHECKPOINTS)
        dt = time.time() - t0
        results[ds] = res
        print(f"[{ds}] n={res['n']} m={res['m']} unsafe_total={res['n_unsafe_total']} "
              f"accepted_total={res['n_accepted_total']} scan_time={dt:.3f}s", flush=True)

    # Decide on optional control dataset based on primary scan speed.
    primary_total_time = sum(r["total_scan_time_sec"] for r in results.values())
    if primary_total_time < 10.0:
        ds, family = CONTROL_DATASET
        print(f"[{ds}] (control) exhaustive scan starting...", flush=True)
        t0 = time.time()
        res = _run_exhaustive_scan(ds, family, CHECKPOINTS)
        dt = time.time() - t0
        results[ds] = res
        print(f"[{ds}] n={res['n']} m={res['m']} unsafe_total={res['n_unsafe_total']} "
              f"accepted_total={res['n_accepted_total']} scan_time={dt:.3f}s", flush=True)
    else:
        print(f"Skipping optional control dataset: primary scans took {primary_total_time:.1f}s already", flush=True)

    for ds, res in results.items():
        A = res["A"]
        src, dst, w = res["src"], res["dst"], res["w"]
        n = res["n"]

        for row in res["attempt_log"]:
            all_attempt_rows.append(row)
            feature_rows.append({k: row[k] for k in [
                "dataset", "u", "v", "candidate_weight", "out_deg_u", "in_deg_u", "out_deg_v", "in_deg_v",
                "rank_distance", "conflict_region_vertices", "conflict_region_edges",
                "conflict_region_total_weight",
                "conflict_region_density", "conflict_region_vertex_fraction",
                "path_min_edge_weight", "path_total_weight", "improvement_margin", "accepted",
                "objective_delta",
            ]})

        checkpoints_to_report = [cp for cp in CHECKPOINTS if cp <= res["n_unsafe_total"]] + ["ALL"]
        for cp in dict.fromkeys(checkpoints_to_report):  # dedupe, keep order
            kept_cp = res["checkpoint_snapshots"].get(cp)
            if kept_cp is None:
                continue
            s_cp = _scores_from_kept_edges(n, kept_cp, src, dst)
            n_accepted_cp = sum(1 for r in res["attempt_log"] if r["accepted"] and r["attempt_index"] <= (cp if cp != "ALL" else 10 ** 9))
            removed_before = float(np.sum(w[~res["kept1"]]))
            removed_after = float(np.sum(w[~kept_cp]))
            total_w = float(np.sum(w))
            dataset_comparison_rows.append({
                "dataset": ds, "family": res["family"], "n": res["n"], "m": res["m"],
                "checkpoint": cp,
                "n_unsafe_total": res["n_unsafe_total"],
                "n_accepted_at_checkpoint": n_accepted_cp,
                "normalized_removed_weight_before": removed_before / total_w,
                "normalized_removed_weight_after": removed_after / total_w,
                "absolute_improvement": removed_before - removed_after,
                "relative_improvement": (removed_before - removed_after) / removed_before if removed_before > 0 else 0.0,
                "upset_simple": _upset_simple(A, s_cp),
                "upset_ratio": _upset_ratio(A, s_cp),
                "upset_naive": _upset_naive(A, s_cp),
            })

    def _write_csv(path, rows):
        if not rows:
            return
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    _write_csv(OUT_DIR / "candidate_attempts.csv", all_attempt_rows)
    _write_csv(OUT_DIR / "dataset_comparison.csv", dataset_comparison_rows)
    _write_csv(OUT_DIR / "candidate_feature_analysis.csv", feature_rows)

    print(f"Wrote outputs to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
