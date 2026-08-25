#!/usr/bin/env python3
"""Min-cut exchange mechanism characterization.

Extends the selector-pilot harness with richer per-candidate and per-graph
telemetry to investigate WHICH graph-level and conflict-level characteristics
distinguish instances where the min-cut exchange operator has meaningful
opportunity from those where it does not.

Primary comparison:
  P1 = Phase A + exact reachability add-back (baseline, unchanged)
  P2 = P1 + min-cut exchange using S1 ordering (selected best selector)

Frozen 11-dataset protocol from MINCUT_SELECTOR_PILOT_PROTOCOL.md is reused
exactly so outcomes can be cross-checked against the committed selector pilot.

Operator semantics (min-cut definition, acceptance rule, deterministic
preflow_push backend, numerical tolerance, reachability restoration,
weighted-objective accounting) are UNCHANGED from
GNNRank-main/src/mincut_exchange_prototype.py. comparison.py and ours_mfas.py
are not modified, only read.

NOT a canonical/manuscript-facing script.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics as st
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOP_ROOT = REPO_ROOT.parent
SCRIPT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from run_mincut_cap_audit import (  # noqa: E402
    _robust_load_real_data,
    _upset_simple, _upset_naive, _upset_ratio,
    PHASE_TIME_LIMIT_SEC,
)

MAX_ACCEPTED_EXCHANGES = 10
MINCUT_TIME_BUDGET_SEC = 120.0
CHARACTERIZATION_BUDGET = 300  # large predefined budget to expose opportunity

_BROAD_DATASETS_JSON = SCRIPT_DIR / "broad_characterization_datasets.json"

PILOT_DATASETS = [
    ("Basketball_temporal/1985", "Basketball_coarse"),
    ("Basketball_temporal/2014", "Basketball_coarse"),
    ("Basketball_temporal/1993", "Basketball_coarse"),
    ("Basketball_temporal/finer1985", "Basketball_finer"),
    ("Football_data_England_Premier_League/England_2009_2010", "Football_coarse"),
    ("Football_data_England_Premier_League/finerEngland_2009_2010", "Football_finer"),
    ("Dryad_animal_society", "Animal"),
    ("FacultyHiringNetworks/Business/Business_FM_Full_", "Faculty"),
    ("FacultyHiringNetworks/History/History_FM_Full_", "Faculty"),
    ("FacultyHiringNetworks/ComputerScience/ComputerScience_FM_Full_", "Faculty"),
    ("Halo2BetaData", "Halo"),
]


def _load_broad_datasets():
    with _BROAD_DATASETS_JSON.open() as f:
        data = json.load(f)
    return [tuple(pair) for pair in data["datasets"]]


_BROAD_MODE = "--broad" in sys.argv

if _BROAD_MODE:
    DATASETS = _load_broad_datasets()
    OUT_DIR = TOP_ROOT / "outputs" / "revision_analysis_20260824" / "mincut_broad_characterization"
    _MODE_TAG = "broad_characterization_v1"
else:
    DATASETS = PILOT_DATASETS
    OUT_DIR = TOP_ROOT / "outputs" / "revision_analysis_20260824" / "mincut_mechanism_characterization"
    _MODE_TAG = "characterization_v1"

CONFIG_HASH = hashlib.sha256(
    json.dumps({
        "datasets": [[d, f] for d, f in DATASETS],
        "selector": "S1",
        "budget": CHARACTERIZATION_BUDGET,
        "max_accepted": MAX_ACCEPTED_EXCHANGES,
        "time_budget": MINCUT_TIME_BUDGET_SEC,
        "phase_time_limit": PHASE_TIME_LIMIT_SEC,
        "mode": _MODE_TAG,
    }, sort_keys=True).encode()
).hexdigest()[:16]


# ---- S1 score function (selected best from selector pilot) ----

def _score_S1(feat, weight, ei):
    return (weight / (1.0 + feat["conflict_region_total_weight"]), -ei)


# ---- Pre-mincut feature computation (extended from cap audit) ----

def _compute_pre_mincut_features(n, kept, src, dst, w, u, v, adj_out, adj_in, topo_pos, total_weight):
    import networkx as nx

    out_deg_u = len(adj_out.get(u, ()))
    in_deg_u = len(adj_in.get(u, ()))
    out_deg_v = len(adj_out.get(v, ()))
    in_deg_v = len(adj_in.get(v, ()))
    rank_distance = abs(topo_pos[u] - topo_pos[v]) if (u in topo_pos and v in topo_pos) else None

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
    region_vertex_fraction = region_vertex_count / n if n else 0.0
    region_edge_fraction = region_edge_count / len(src) if len(src) else 0.0

    path_min_edge_weight = None
    path_total_weight = None
    if v in G and u in G and nx.has_path(G, v, u):
        try:
            path_nodes = nx.shortest_path(G, v, u)
            path_edge_weights = [
                G[path_nodes[i]][path_nodes[i + 1]]["weight"] for i in range(len(path_nodes) - 1)
            ]
            path_min_edge_weight = min(path_edge_weights) if path_edge_weights else None
            path_total_weight = sum(path_edge_weights) if path_edge_weights else None
        except Exception:
            pass

    cw = float(w[0]) if len(w) > 0 else 0.0
    candidate_weight = float(w[src.tolist().index(u) if False else 0]) if False else None
    return {
        "out_deg_u": out_deg_u, "in_deg_u": in_deg_u,
        "out_deg_v": out_deg_v, "in_deg_v": in_deg_v,
        "rank_distance": rank_distance,
        "conflict_region_vertices": region_vertex_count,
        "conflict_region_edges": region_edge_count,
        "conflict_region_total_weight": region_total_weight,
        "conflict_region_vertex_fraction": region_vertex_fraction,
        "conflict_region_edge_fraction": region_edge_fraction,
        "conflict_region_density": region_density,
        "path_min_edge_weight": path_min_edge_weight,
        "path_total_weight": path_total_weight,
    }


def _compute_pre_mincut_features_v2(n, kept, src, dst, w, ei, adj_out, adj_in, topo_pos, total_weight, weight_percentile_map):
    import networkx as nx

    u = int(src[ei])
    v = int(dst[ei])
    cw = float(w[ei])

    out_deg_u = len(adj_out.get(u, ()))
    in_deg_u = len(adj_in.get(u, ()))
    out_deg_v = len(adj_out.get(v, ()))
    in_deg_v = len(adj_in.get(v, ()))
    rank_distance = abs(topo_pos[u] - topo_pos[v]) if (u in topo_pos and v in topo_pos) else None

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
    region_vertex_fraction = region_vertex_count / n if n else 0.0
    region_edge_fraction = region_edge_count / len(src) if len(src) else 0.0

    path_min_edge_weight = None
    path_total_weight = None
    if v in G and u in G and nx.has_path(G, v, u):
        try:
            path_nodes = nx.shortest_path(G, v, u)
            path_edge_weights = [
                G[path_nodes[i]][path_nodes[i + 1]]["weight"] for i in range(len(path_nodes) - 1)
            ]
            path_min_edge_weight = min(path_edge_weights) if path_edge_weights else None
            path_total_weight = sum(path_edge_weights) if path_edge_weights else None
        except Exception:
            pass

    cw_pct = weight_percentile_map.get(ei, None)

    return {
        "candidate_weight": cw,
        "out_deg_u": out_deg_u, "in_deg_u": in_deg_u,
        "out_deg_v": out_deg_v, "in_deg_v": in_deg_v,
        "rank_distance": rank_distance,
        "conflict_region_vertices": region_vertex_count,
        "conflict_region_edges": region_edge_count,
        "conflict_region_total_weight": region_total_weight,
        "conflict_region_vertex_fraction": region_vertex_fraction,
        "conflict_region_edge_fraction": region_edge_fraction,
        "conflict_region_density": region_density,
        "path_min_edge_weight": path_min_edge_weight,
        "path_total_weight": path_total_weight,
        "candidate_weight_percentile": cw_pct,
        "candidate_weight_fraction": cw / total_weight if total_weight > 0 else 0.0,
        "weight_over_conflict_weight": cw / (1.0 + region_total_weight),
        "weight_over_conflict_edges": cw / max(1, region_edge_count),
        "weight_over_conflict_vertices": cw / max(1, region_vertex_count),
    }


# ---- Graph-level feature computation ----

def _gini_coefficient(values):
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 0:
        return 0.0
    cumsum = 0.0
    for i, v in enumerate(sorted_vals, start=1):
        cumsum += i * v
    return (2.0 * cumsum) / (n * sum(sorted_vals)) - (n + 1) / n if sum(sorted_vals) > 0 else 0.0


def _scc_stats(n, src, dst, kept):
    import networkx as nx
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for ei in range(len(src)):
        if kept[ei]:
            G.add_edge(int(src[ei]), int(dst[ei]))
    sccs = list(nx.strongly_connected_components(G))
    sizes = sorted([len(c) for c in sccs], reverse=True)
    return {
        "scc_count": len(sccs),
        "largest_scc_size": sizes[0] if sizes else 0,
        "largest_scc_fraction": sizes[0] / n if sizes and n > 0 else 0.0,
    }


def _compute_graph_features(ds, family, n, src, dst, w, kept1, A):
    import numpy as np
    w_arr = np.asarray(w, dtype=float)
    total_weight = float(w_arr.sum())
    mean_w = float(w_arr.mean()) if len(w_arr) else 0.0
    median_w = float(np.median(w_arr)) if len(w_arr) else 0.0
    std_w = float(w_arr.std()) if len(w_arr) else 0.0
    cv = std_w / mean_w if mean_w > 0 else 0.0
    min_w = float(w_arr.min()) if len(w_arr) else 0.0
    max_w = float(w_arr.max()) if len(w_arr) else 0.0
    q10 = float(np.percentile(w_arr, 10)) if len(w_arr) else 0.0
    q25 = float(np.percentile(w_arr, 25)) if len(w_arr) else 0.0
    q75 = float(np.percentile(w_arr, 75)) if len(w_arr) else 0.0
    q90 = float(np.percentile(w_arr, 90)) if len(w_arr) else 0.0
    q95 = float(np.percentile(w_arr, 95)) if len(w_arr) else 0.0
    max_median_ratio = max_w / median_w if median_w > 0 else 0.0
    gini = _gini_coefficient(w_arr.tolist())

    m = len(src)
    density = m / (n * (n - 1)) if n > 1 else 0.0

    removed_mask = ~kept1
    n_removed = int(removed_mask.sum())
    removed_weight = float(w_arr[removed_mask].sum())
    removed_fraction = n_removed / m if m > 0 else 0.0
    normalized_removed_weight = removed_weight / total_weight if total_weight > 0 else 0.0

    n_reach_restored = int(kept1.sum()) - (m - n_removed)
    restored_weight = total_weight - removed_weight - float(w_arr[kept1].sum())
    n_reach_restored = int(kept1.sum()) - int((~removed_mask).sum())
    n_kept = int(kept1.sum())
    restored_weight = float(w_arr[kept1 & removed_mask].sum()) if False else None

    unsafe_eis = [int(ei) for ei in range(m) if not kept1[ei]]
    n_unsafe = len(unsafe_eis)
    unsafe_fraction = n_unsafe / m if m > 0 else 0.0

    scc = _scc_stats(n, src, dst, kept1)

    out_degrees = defaultdict(int)
    in_degrees = defaultdict(int)
    for ei in range(m):
        if kept1[ei]:
            out_degrees[int(src[ei])] += 1
            in_degrees[int(dst[ei])] += 1
    all_out = list(out_degrees.values()) or [0]
    all_in = list(in_degrees.values()) or [0]

    return {
        "dataset": ds, "family": family,
        "n": n, "m": m, "density": density,
        "total_edge_weight": total_weight,
        "mean_edge_weight": mean_w,
        "median_edge_weight": median_w,
        "std_edge_weight": std_w,
        "cv_edge_weight": cv,
        "min_edge_weight": min_w,
        "max_edge_weight": max_w,
        "q10_edge_weight": q10,
        "q25_edge_weight": q25,
        "q75_edge_weight": q75,
        "q90_edge_weight": q90,
        "q95_edge_weight": q95,
        "max_median_ratio": max_median_ratio,
        "gini_coefficient": gini,
        "n_phase_a_removed": n_removed,
        "phase_a_removed_fraction": removed_fraction,
        "phase_a_removed_weight": removed_weight,
        "normalized_phase_a_removed_weight": normalized_removed_weight,
        "n_kept": n_kept,
        "n_unsafe_excluded": n_unsafe,
        "unsafe_fraction": unsafe_fraction,
        "scc_count": scc["scc_count"],
        "largest_scc_size": scc["largest_scc_size"],
        "largest_scc_fraction": scc["largest_scc_fraction"],
        "mean_out_degree": st.fmean(all_out),
        "mean_in_degree": st.fmean(all_in),
        "median_out_degree": st.median(all_out),
        "median_in_degree": st.median(all_in),
    }


def _conflict_region_summaries(n, kept1, src, dst, w, unsafe_eis):
    import networkx as nx
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for ei2 in range(len(src)):
        if kept1[ei2]:
            G.add_edge(int(src[ei2]), int(dst[ei2]), weight=float(w[ei2]))

    v_counts = []
    e_counts = []
    tw_vals = []
    for ei in unsafe_eis:
        u = int(src[ei]); v = int(dst[ei])
        desc_v = set(nx.descendants(G, v)) | {v} if v in G else {v}
        anc_u = set(nx.descendants(G.reverse(copy=False), u)) | {u} if u in G else {u}
        region = desc_v & anc_u
        vc = len(region)
        ec = sum(1 for a2, b2 in G.edges() if a2 in region and b2 in region)
        tw = sum(G[a2][b2]["weight"] for a2, b2 in G.edges() if a2 in region and b2 in region)
        v_counts.append(vc)
        e_counts.append(ec)
        tw_vals.append(float(tw))

    def _pct(lst, p):
        if not lst:
            return 0.0
        import numpy as np
        return float(np.percentile(lst, p))

    return {
        "conflict_median_vertices": st.median(v_counts) if v_counts else 0,
        "conflict_mean_vertices": st.fmean(v_counts) if v_counts else 0,
        "conflict_p90_vertices": _pct(v_counts, 90),
        "conflict_median_edges": st.median(e_counts) if e_counts else 0,
        "conflict_mean_edges": st.fmean(e_counts) if e_counts else 0,
        "conflict_p90_edges": _pct(e_counts, 90),
        "conflict_median_total_weight": st.median(tw_vals) if tw_vals else 0,
        "conflict_mean_total_weight": st.fmean(tw_vals) if tw_vals else 0,
        "conflict_p90_total_weight": _pct(tw_vals, 90),
    }


# ---- Permutation distance (from selector pilot) ----

def _permutation_distance(scores_a, scores_b):
    import numpy as np
    n = len(scores_a)
    if n < 2:
        return 0.0
    sa = np.asarray(scores_a)
    sb = np.asarray(scores_b)
    iu = np.triu_indices(n, k=1)
    sign_a = np.sign(sa[iu[0]] - sa[iu[1]])
    sign_b = np.sign(sb[iu[0]] - sb[iu[1]])
    discordant = int(np.sum(sign_a != sign_b))
    total = len(iu[0])
    return float(discordant) / float(total) if total else 0.0


# ---- Core P2 simulation with full telemetry ----

def _simulate_p2(n, src, dst, w, kept1, ordered_eis, max_attempts, static_features_map, total_weight):
    from mincut_exchange_prototype import _try_mincut_exchange

    kept_running = kept1.copy()
    n_accepted = 0
    rows = []
    t0 = time.time()

    for attempt_index, ei in enumerate(ordered_eis[:max_attempts], start=1):
        if n_accepted >= MAX_ACCEPTED_EXCHANGES:
            break
        if (time.time() - t0) > MINCUT_TIME_BUDGET_SEC:
            break

        u = int(src[ei]); v = int(dst[ei])
        feat = static_features_map[ei]

        diag = _try_mincut_exchange(n, kept_running, src, dst, w, ei)
        margin = (
            diag["candidate_weight"] - diag["cut_weight"]
            if (diag["candidate_weight"] is not None and diag["cut_weight"] is not None) else None
        )

        row = {
            "dataset": "", "family": "", "mode": "P2",
            "attempt_index": attempt_index, "u": u, "v": v, "edge_index": ei,
            "candidate_weight": diag["candidate_weight"],
            "cut_value": diag["cut_weight"],
            "cut_size": len(diag["cut_edges"]) if diag["cut_edges"] is not None else "",
            "improvement_margin": margin,
            "accepted": diag["accepted"],
            "reason": diag["reason"],
            "objective_delta": diag["objective_delta"],
            "mincut_runtime_sec": diag["runtime_sec"],
            "cumulative_runtime_sec": time.time() - t0,
            "feature_type": "PRE_MINCUT",
            "out_deg_u": feat["out_deg_u"], "in_deg_u": feat["in_deg_u"],
            "out_deg_v": feat["out_deg_v"], "in_deg_v": feat["in_deg_v"],
            "rank_distance": feat["rank_distance"],
            "conflict_region_vertices": feat["conflict_region_vertices"],
            "conflict_region_edges": feat["conflict_region_edges"],
            "conflict_region_total_weight": feat["conflict_region_total_weight"],
            "conflict_region_vertex_fraction": feat["conflict_region_vertex_fraction"],
            "conflict_region_edge_fraction": feat["conflict_region_edge_fraction"],
            "conflict_region_density": feat["conflict_region_density"],
            "path_min_edge_weight": feat["path_min_edge_weight"],
            "path_total_weight": feat["path_total_weight"],
            "candidate_weight_percentile": feat["candidate_weight_percentile"],
            "candidate_weight_fraction": feat["candidate_weight_fraction"],
            "weight_over_conflict_weight": feat["weight_over_conflict_weight"],
            "weight_over_conflict_edges": feat["weight_over_conflict_edges"],
            "weight_over_conflict_vertices": feat["weight_over_conflict_vertices"],
        }
        rows.append(row)

        if diag["accepted"]:
            kept_running = diag["new_kept"]
            n_accepted += 1

    return {
        "rows": rows,
        "n_attempted": len(rows),
        "n_accepted": n_accepted,
        "kept_final": kept_running,
        "wall_time": time.time() - t0,
    }


def _write_csv(path, rows):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    import numpy as np
    from ours_mfas import ours_mfas_rmfa, _csr_to_edges, _scores_from_kept_edges, _toposort_kahn_from_edges
    from preprocess import load_real_data

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger_path = OUT_DIR / "_progress.jsonl"

    done = set()
    if ledger_path.exists():
        with ledger_path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("config_hash") == CONFIG_HASH:
                    done.add(rec["dataset"])

    all_candidate_rows = []
    all_dataset_rows = []

    if done:
        cands_path = OUT_DIR / "candidate_features.csv"
        ds_path = OUT_DIR / "dataset_features.csv"
        if cands_path.exists():
            with cands_path.open() as f:
                for row in csv.DictReader(f):
                    all_candidate_rows.append(row)
        if ds_path.exists():
            with ds_path.open() as f:
                for row in csv.DictReader(f):
                    all_dataset_rows.append(row)
        print(f"Resumed: {len(done)} datasets already complete for CONFIG_HASH={CONFIG_HASH}", flush=True)

    for ds, family in DATASETS:
        if ds in done:
            print(f"  [{ds}] SKIPPED (ledger match)", flush=True)
            continue

        print(f"[{ds}] loading + computing P1 baseline...", flush=True)
        try:
            A = _robust_load_real_data(load_real_data, ds)
        except (FileNotFoundError, OSError) as e:
            print(f"  [{ds}] DATA_AVAILABILITY_SKIP: {e}", flush=True)
            rec = {"dataset": ds, "family": family,
                   "config_hash": CONFIG_HASH, "timestamp": time.time(),
                   "n_unsafe_total": 0, "n_accepted": 0,
                   "sel_time_sec": 0.0, "status": "data_unavailable"}
            with ledger_path.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            continue
        n = int(A.shape[0])
        n_, src, dst, w = _csr_to_edges(A)
        assert n_ == n
        m = len(src)
        total_weight = float(w.sum())

        _, meta1 = ours_mfas_rmfa(A, enable_phase_b=True, addback_mode="reach",
                                   enable_phase_c=False,
                                   refine_naive=False, refine_ratio=False,
                                   time_limit_sec=PHASE_TIME_LIMIT_SEC, return_meta=True)
        kept1 = np.array(meta1["kept_final_mask"], dtype=bool)
        p1_scores = _scores_from_kept_edges(n, kept1, src, dst)

        topo = _toposort_kahn_from_edges(n, src, dst, kept1)
        topo_pos = {int(node): i for i, node in enumerate(topo)} if topo is not None else {}
        adj_out, adj_in = {}, {}
        for ei in range(m):
            if kept1[ei]:
                adj_out.setdefault(int(src[ei]), []).append(ei)
                adj_in.setdefault(int(dst[ei]), []).append(ei)

        order_by_weight = np.argsort(-w, kind="mergesort")
        unsafe_eis = [int(ei) for ei in order_by_weight if not kept1[ei]]
        n_unsafe_total = len(unsafe_eis)

        weight_sorted = np.sort(w)[::-1]
        weight_ranks = np.argsort(np.argsort(-w, kind="mergesort"), kind="mergesort")
        weight_percentile_map = {}
        for ei in range(m):
            rank = int(weight_ranks[ei])
            weight_percentile_map[ei] = 1.0 - (rank / max(1, m - 1))

        print(f"[{ds}] computing pre-mincut features for {n_unsafe_total} unsafe candidates...", flush=True)
        t_feat0 = time.time()
        static_features_map = {}
        for ei in unsafe_eis:
            static_features_map[ei] = _compute_pre_mincut_features_v2(
                n, kept1, src, dst, w, ei, adj_out, adj_in, topo_pos, total_weight, weight_percentile_map
            )
        feature_time = time.time() - t_feat0
        print(f"  feature_time={feature_time:.2f}s", flush=True)

        graph_feat = _compute_graph_features(ds, family, n, src, dst, w, kept1, A)
        conflict_summaries = _conflict_region_summaries(n, kept1, src, dst, w, unsafe_eis)
        graph_feat.update(conflict_summaries)

        ordered_eis = [ei for _, ei in sorted(
            [(_score_S1(static_features_map[ei], float(w[ei]), ei), ei) for ei in unsafe_eis],
            reverse=True
        )]

        max_attempts = min(CHARACTERIZATION_BUDGET, n_unsafe_total)

        print(f"[{ds}] P2 simulation: S1 order, max_attempts={max_attempts}...", flush=True)
        sim = _simulate_p2(n, src, dst, w, kept1, ordered_eis, max_attempts, static_features_map, total_weight)
        print(f"  attempts={sim['n_attempted']} accepted={sim['n_accepted']} time={sim['wall_time']:.2f}s", flush=True)

        kept_p2 = sim["kept_final"]
        p2_scores = _scores_from_kept_edges(n, kept_p2, src, dst)
        removed_before = float(w[~kept1].sum())
        removed_after = float(w[~kept_p2].sum())
        gain = removed_before - removed_after

        graph_feat.update({
            "n_accepted_p2": sim["n_accepted"],
            "total_weighted_gain": gain,
            "normalized_gain": gain / removed_before if removed_before > 0 else 0.0,
            "gain_per_attempt": gain / sim["n_attempted"] if sim["n_attempted"] else 0.0,
            "p1_upset_simple": _upset_simple(A, p1_scores),
            "p1_upset_ratio": _upset_ratio(A, p1_scores),
            "p1_upset_naive": _upset_naive(A, p1_scores),
            "p2_upset_simple": _upset_simple(A, p2_scores),
            "p2_upset_ratio": _upset_ratio(A, p2_scores),
            "p2_upset_naive": _upset_naive(A, p2_scores),
            "upset_simple_delta": _upset_simple(A, p2_scores) - _upset_simple(A, p1_scores),
            "upset_ratio_delta": _upset_ratio(A, p2_scores) - _upset_ratio(A, p1_scores),
            "upset_naive_delta": _upset_naive(A, p2_scores) - _upset_naive(A, p1_scores),
            "permutation_distance_p2_vs_p1": _permutation_distance(p2_scores, p1_scores),
            "p2_wall_time_sec": sim["wall_time"],
            "feature_time_sec": feature_time,
            "operator_active": sim["n_accepted"] > 0,
        })
        all_dataset_rows.append(graph_feat)

        for r in sim["rows"]:
            r["dataset"] = ds
            r["family"] = family
            r["n"] = n
            r["m"] = m
            all_candidate_rows.append(r)

        rec = {"dataset": ds, "family": family,
               "config_hash": CONFIG_HASH, "timestamp": time.time(),
               "n_unsafe_total": n_unsafe_total, "n_accepted": sim["n_accepted"],
               "sel_time_sec": sim["wall_time"], "status": "complete"}
        with ledger_path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

        _write_csv(OUT_DIR / "candidate_features.csv", all_candidate_rows)
        _write_csv(OUT_DIR / "dataset_features.csv", all_dataset_rows)

        print(f"  [{ds}] checkpointed (dataset_features + candidate_features)", flush=True)

    _write_csv(OUT_DIR / "candidate_features.csv", all_candidate_rows)
    _write_csv(OUT_DIR / "dataset_features.csv", all_dataset_rows)

    print(f"Done. Outputs in {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
