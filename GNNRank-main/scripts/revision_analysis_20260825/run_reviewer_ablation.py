#!/usr/bin/env python3
"""Reviewer-driven ablation + sensitivity + scalability study.

Runs a compact, predefined set of configurations that directly answer
reviewer experimental requests:

  - Structural ablation: A0–A6 (Phase A only through reach+mincut+refine)
  - Cycle-selection sensitivity: C0 (DFS first-found) vs C1 (reverse-order DFS)
  - Zero-tolerance sensitivity: 1e-12, 1e-15, 1e-18
  - Refinement sensitivity: R0–R3 (disabled, 0.5x, canonical, 2x passes)
  - Legacy insertion-pass sensitivity: P0–P3
  - Min-cut budget sensitivity: K=20, 50, 100

Two dataset layers:
  Layer 1 (core, 33 datasets): full ablation/sensitivity matrix
  Layer 2 (scale, 45 datasets): only A0, A2, A4, A6
  Finance stress: single run per main config with strict budget

NOT a canonical/manuscript-facing script. Does NOT modify ours_mfas.py or
comparison.py — only calls them with different parameters.

Checkpoint/resume: after each (dataset, config) pair, appends to _progress.jsonl
and rewrites output CSVs. On restart, skips completed pairs with matching
config_hash.
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
OUT_DIR = TOP_ROOT / "outputs" / "revision_analysis_20260825" / "reviewer_ablation_scalability"

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR.parent / "revision_analysis_20260824"))

from run_mincut_cap_audit import (  # noqa: E402
    _robust_load_real_data,
    _upset_simple, _upset_naive, _upset_ratio,
    _cheap_pre_mincut_features,
    PHASE_TIME_LIMIT_SEC,
)

# ---- Constants ----
MAX_ACCEPTED_EXCHANGES = 10
MINCUT_TIME_BUDGET_SEC = 120.0
FINANCE_TIME_BUDGET_SEC = 600.0  # 10 min per config for finance
DEFAULT_PHASE_TIME_LIMIT = 300.0

# ---- Dataset manifest ----
MANIFEST_PATH = SCRIPT_DIR / "ablation_dataset_manifest.json"

with MANIFEST_PATH.open() as _f:
    _MANIFEST = json.load(_f)

LAYER1 = [tuple(x) for x in _MANIFEST["layer1_core"]]
LAYER2 = [tuple(x) for x in _MANIFEST["layer2_scale"]]
FINANCE = [tuple(x) for x in _MANIFEST["finance_stress"]]

# ---- Configuration definitions ----

# Structural ablation variants
# Each is (label, params_dict, layer_assignment)
# layer_assignment: "both" = runs on Layer1+Layer2+finance, "core" = Layer1+finance only

def _base_params():
    return {
        "insertion_passes": 3,
        "enable_phase_b": True,
        "addback_mode": "topo",
        "enable_phase_c": True,
        "time_limit_sec": DEFAULT_PHASE_TIME_LIMIT,
        "refine_naive": True,
        "naive_refine_time_sec": 2.0,
        "naive_refine_passes": 2,
        "refine_ratio": True,
        "refine_time_sec": 20.0,
        "refine_passes": 2,
        "ternary_iters": 20,
        "zero_tol": 1e-15,
        "enable_mincut": False,
        "mincut_budget": 300,
        "mincut_max_accepted": MAX_ACCEPTED_EXCHANGES,
        "cycle_selection": "dfs_first",
    }


STRUCTURAL_VARIANTS = {
    "A0": {**_base_params(), "enable_phase_b": False, "enable_phase_c": False, "refine_naive": False, "refine_ratio": False},
    "A1": {**_base_params(), "addback_mode": "topo", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False},
    "A2": {**_base_params(), "addback_mode": "reach", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False},
    "A3": {**_base_params(), "addback_mode": "topo", "enable_phase_c": True, "refine_naive": True, "refine_ratio": True},
    "A4": {**_base_params(), "addback_mode": "reach", "enable_phase_c": True, "refine_naive": True, "refine_ratio": True},
    "A5": {**_base_params(), "addback_mode": "reach", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "enable_mincut": True},
    "A6": {**_base_params(), "addback_mode": "reach", "enable_phase_c": True, "refine_naive": True, "refine_ratio": True, "enable_mincut": True},
}

# Which variants run on which layers
VARIANT_LAYERS = {
    "A0": "both",
    "A1": "core",
    "A2": "both",
    "A3": "core",
    "A4": "both",
    "A5": "core",
    "A6": "both",
}

# Sensitivity configs (run on Layer 1 only)
# Cycle selection: C0 = dfs_first (default), C1 = dfs_last (reverse vertex order)
CYCLE_CONFIGS = {
    "C0_A0": {**_base_params(), "enable_phase_b": False, "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "cycle_selection": "dfs_first"},
    "C0_A4": {**_base_params(), "addback_mode": "reach", "cycle_selection": "dfs_first"},
    "C1_A0": {**_base_params(), "enable_phase_b": False, "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "cycle_selection": "dfs_last"},
    "C1_A4": {**_base_params(), "addback_mode": "reach", "cycle_selection": "dfs_last"},
}

# Zero tolerance
ZERO_TOL_CONFIGS = {
    "Z12_A4": {**_base_params(), "addback_mode": "reach", "zero_tol": 1e-12},
    "Z15_A4": {**_base_params(), "addback_mode": "reach", "zero_tol": 1e-15},
    "Z18_A4": {**_base_params(), "addback_mode": "reach", "zero_tol": 1e-18},
}

# Refinement sensitivity (on A4 base)
REFINE_CONFIGS = {
    "R0_A4": {**_base_params(), "addback_mode": "reach", "refine_ratio": False, "refine_naive": False, "enable_phase_c": False},
    "R1_A4": {**_base_params(), "addback_mode": "reach", "refine_passes": 1, "refine_time_sec": 10.0, "naive_refine_passes": 1, "naive_refine_time_sec": 1.0},
    "R2_A4": {**_base_params(), "addback_mode": "reach", "refine_passes": 2, "refine_time_sec": 20.0, "naive_refine_passes": 2, "naive_refine_time_sec": 2.0},
    "R3_A4": {**_base_params(), "addback_mode": "reach", "refine_passes": 4, "refine_time_sec": 40.0, "naive_refine_passes": 4, "naive_refine_time_sec": 4.0},
}

# Legacy insertion-pass sensitivity (using topo add-back)
PASS_CONFIGS = {
    "P0": {**_base_params(), "addback_mode": "topo", "enable_phase_b": False, "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "insertion_passes": 0},
    "P1": {**_base_params(), "addback_mode": "topo", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "insertion_passes": 1},
    "P2": {**_base_params(), "addback_mode": "topo", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "insertion_passes": 2},
    "P3": {**_base_params(), "addback_mode": "topo", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "insertion_passes": 3},
}

# Min-cut budget sensitivity (on A5 base)
MINCUT_CONFIGS = {
    "K20_A5": {**_base_params(), "addback_mode": "reach", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "enable_mincut": True, "mincut_budget": 20},
    "K50_A5": {**_base_params(), "addback_mode": "reach", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "enable_mincut": True, "mincut_budget": 50},
    "K100_A5": {**_base_params(), "addback_mode": "reach", "enable_phase_c": False, "refine_naive": False, "refine_ratio": False, "enable_mincut": True, "mincut_budget": 100},
}

# Finance-specific configs (only main variants, strict budget)
FINANCE_CONFIGS = {
    "A0": {**STRUCTURAL_VARIANTS["A0"], "time_limit_sec": FINANCE_TIME_BUDGET_SEC},
    "A2": {**STRUCTURAL_VARIANTS["A2"], "time_limit_sec": FINANCE_TIME_BUDGET_SEC},
    "A4": {**STRUCTURAL_VARIANTS["A4"], "time_limit_sec": FINANCE_TIME_BUDGET_SEC},
    "A6": {**STRUCTURAL_VARIANTS["A6"], "time_limit_sec": FINANCE_TIME_BUDGET_SEC},
}

# All config groups
ALL_CONFIG_GROUPS = {
    "structural": STRUCTURAL_VARIANTS,
    "cycle": CYCLE_CONFIGS,
    "zero_tol": ZERO_TOL_CONFIGS,
    "refinement": REFINE_CONFIGS,
    "legacy_pass": PASS_CONFIGS,
    "mincut_budget": MINCUT_CONFIGS,
}

# Config hash
def _build_config_hash():
    all_configs = {}
    for group, configs in ALL_CONFIG_GROUPS.items():
        for label, params in configs.items():
            all_configs[f"{group}:{label}"] = {k: v for k, v in sorted(params.items())}
    all_configs["finance"] = {k: v for k, v in sorted(FINANCE_CONFIGS["A0"].items())}
    return hashlib.sha256(
        json.dumps(all_configs, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

CONFIG_HASH = _build_config_hash()


# ---- S1 score function (from selector pilot) ----

def _score_S1(feat, weight, ei):
    return (weight / (1.0 + feat["conflict_region_total_weight"]), -ei)


# ---- Permutation distance ----

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


# ---- Min-cut exchange integration ----

def _apply_mincut_exchange(n, src, dst, w, kept, params, total_weight):
    """Apply S1-ordered min-cut exchange on top of the kept DAG."""
    from mincut_exchange_prototype import _try_mincut_exchange

    # Build adjacency for feature computation
    from ours_mfas import _toposort_kahn_from_edges
    topo = _toposort_kahn_from_edges(n, src, dst, kept)
    topo_pos = {int(node): i for i, node in enumerate(topo)} if topo is not None else {}
    adj_out, adj_in = {}, {}
    for ei in range(len(src)):
        if kept[ei]:
            adj_out.setdefault(int(src[ei]), []).append(ei)
            adj_in.setdefault(int(dst[ei]), []).append(ei)

    order_by_weight = __import__("numpy").argsort(-w, kind="mergesort")
    unsafe_eis = [int(ei) for ei in order_by_weight if not kept[ei]]
    n_unsafe = len(unsafe_eis)
    if n_unsafe == 0:
        return kept, 0, 0, 0.0

    # Compute pre-mincut features
    static_features = {}
    for ei in unsafe_eis:
        u = int(src[ei]); v = int(dst[ei])
        static_features[ei] = _cheap_pre_mincut_features(
            n, kept, src, dst, w, u, v, adj_out, adj_in, topo_pos
        )

    # S1 ordering
    ordered = [ei for _, ei in sorted(
        [(_score_S1(static_features[ei], float(w[ei]), ei), ei) for ei in unsafe_eis],
        reverse=True
    )]

    max_attempts = min(params.get("mincut_budget", 300), n_unsafe)
    max_accepted = params.get("mincut_max_accepted", MAX_ACCEPTED_EXCHANGES)

    kept_running = kept.copy()
    n_accepted = 0
    n_attempted = 0
    t0 = time.time()

    for attempt_index, ei in enumerate(ordered[:max_attempts], start=1):
        if n_accepted >= max_accepted:
            break
        if (time.time() - t0) > MINCUT_TIME_BUDGET_SEC:
            break
        n_attempted += 1
        diag = _try_mincut_exchange(n, kept_running, src, dst, w, ei)
        if diag["accepted"]:
            kept_running = diag["new_kept"]
            n_accepted += 1

    removed_before = float(w[~kept].sum())
    removed_after = float(w[~kept_running].sum())
    gain = removed_before - removed_after

    return kept_running, n_attempted, n_accepted, gain


# ---- Run one configuration ----

def run_config(ds, family, config_label, params, is_finance=False):
    """Run one (dataset, config) pair and return result row + raw attempt rows."""
    import numpy as np
    from ours_mfas import ours_mfas_rmfa, _csr_to_edges, _scores_from_kept_edges

    from preprocess import load_real_data

    t0 = time.time()
    result = {
        "dataset": ds, "family": family, "config": config_label,
        "config_hash": CONFIG_HASH, "timestamp": time.time(),
        "status": "running",
    }

    try:
        A = _robust_load_real_data(load_real_data, ds)
    except (FileNotFoundError, OSError) as e:
        result["status"] = "data_unavailable"
        result["error"] = str(e)[:200]
        result["runtime_sec"] = time.time() - t0
        return result, []

    n = int(A.shape[0])
    n_, src, dst, w = _csr_to_edges(A)
    assert n_ == n
    m = len(src)
    total_weight = float(w.sum())
    density = m / (n * (n - 1)) if n > 1 else 0.0

    result["n"] = n
    result["m"] = m
    result["density"] = density

    # Prepare params for ours_mfas_rmfa
    rmfa_params = {
        "insertion_passes": params["insertion_passes"],
        "enable_phase_b": params["enable_phase_b"],
        "addback_mode": params["addback_mode"],
        "enable_phase_c": params["enable_phase_c"],
        "time_limit_sec": params["time_limit_sec"],
        "refine_naive": params["refine_naive"],
        "naive_refine_time_sec": params["naive_refine_time_sec"],
        "naive_refine_passes": params["naive_refine_passes"],
        "refine_ratio": params["refine_ratio"],
        "refine_time_sec": params["refine_time_sec"],
        "refine_passes": params["refine_passes"],
        "ternary_iters": params["ternary_iters"],
        "return_meta": True,
    }

    # Note: zero_tol and cycle_selection are not directly exposed by ours_mfas_rmfa
    # We handle cycle_selection by modifying the DFS order if needed
    # zero_tol is handled by monkey-patching if necessary

    # For cycle_selection = dfs_last, we reverse vertex order in cycle finding
    # This requires a temporary patch — we use a context manager approach
    _original_find_cycle = None
    if params.get("cycle_selection") == "dfs_last":
        import ours_mfas as _om
        _original_find_cycle = _om._find_one_cycle_edges

        def _reverse_find_cycle(n, src, dst, adj_e, alive):
            # Reverse adjacency order to find different cycles
            adj_rev = [list(reversed(lst)) for lst in adj_e]
            return _original_find_cycle(n, src, dst, adj_rev, alive)

        _om._find_one_cycle_edges = _reverse_find_cycle

    # For zero_tol, we need to pass it through — ours_mfas_rmfa doesn't expose it
    # We monkey-patch _local_ratio_break_cycles temporarily
    _original_break = None
    if params.get("zero_tol", 1e-15) != 1e-15:
        import ours_mfas as _om
        _original_break = _om._local_ratio_break_cycles

        _zt = params["zero_tol"]
        def _patched_break(n, src, dst, w, time_limit_sec, t0, zero_tol=_zt):
            return _original_break(n, src, dst, w, time_limit_sec, t0, zero_tol)

        _om._local_ratio_break_cycles = _patched_break

    try:
        scores, meta = ours_mfas_rmfa(A, **rmfa_params)
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
        result["runtime_sec"] = time.time() - t0
        # Restore patches
        if _original_find_cycle is not None:
            import ours_mfas as _om
            _om._find_one_cycle_edges = _original_find_cycle
        if _original_break is not None:
            import ours_mfas as _om
            _om._local_ratio_break_cycles = _original_break
        return result, []
    finally:
        # Restore patches
        if _original_find_cycle is not None:
            import ours_mfas as _om
            _om._find_one_cycle_edges = _original_find_cycle
        if _original_break is not None:
            import ours_mfas as _om
            _om._local_ratio_break_cycles = _original_break

    t_after_rmfa = time.time()

    # Extract Phase A state
    keptA_mask = np.array(meta["kept_final_mask"], dtype=bool)
    # Phase A removed weight = weight of edges removed in Phase A (before add-back)
    # meta["removed_phaseA"] gives the count; we need weight
    # keptA = alive after Phase A; but kept_final may differ after add-back
    # We need the Phase-A-only kept mask — ours_mfas_rmfa doesn't return it directly
    # We can recompute: edges removed in Phase A = those not in keptA_mask but...
    # Actually meta["kept_after_phaseA"] gives the count but not the mask.
    # For structural metrics, we use the final kept mask.
    kept_final = np.array(meta["kept_final_mask"], dtype=bool)

    # Phase A removed weight (approximate from meta)
    removed_phaseA_count = int(meta.get("removed_phaseA", 0))
    removed_weight_phaseA = float(w[~keptA_mask].sum()) if removed_phaseA_count > 0 else 0.0

    # Wait — kept_final_mask IS the final kept mask, not Phase A only
    # We need to get Phase-A-only scores for A0 comparison
    # For A0 (no Phase B), kept_final == keptA
    # For others, kept_final includes add-back changes

    # Apply min-cut if enabled
    mincut_accepted = 0
    mincut_attempts = 0
    mincut_gain = 0.0
    mincut_time = 0.0

    if params.get("enable_mincut", False):
        kept_after_reach = kept_final.copy()
        t_mc0 = time.time()
        kept_final, mincut_attempts, mincut_accepted, mincut_gain = _apply_mincut_exchange(
            n, src, dst, w, kept_after_reach, params, total_weight
        )
        mincut_time = time.time() - t_mc0
        # Recompute scores after min-cut
        scores = _scores_from_kept_edges(n, kept_final, src, dst)

    # Compute metrics
    removed_final_weight = float(w[~kept_final].sum())
    removed_final_count = int((~kept_final).sum())
    restored_count = m - removed_final_count - int(kept_final.sum())  # rough
    # Actually: kept_final.sum() = kept count; removed = ~kept_final; restored = kept_final.sum() - keptA_count
    keptA_count = m - removed_phaseA_count
    restored_count = int(kept_final.sum()) - keptA_count

    upset_s = _upset_simple(A, scores)
    upset_r = _upset_ratio(A, scores)
    upset_n = _upset_naive(A, scores)

    # P1 scores (Phase A only) for permutation distance
    if params["enable_phase_b"]:
        # Run A0 to get P1 baseline scores
        scores_p1, _ = ours_mfas_rmfa(A, enable_phase_b=False, enable_phase_c=False,
                                        refine_naive=False, refine_ratio=False,
                                        time_limit_sec=params["time_limit_sec"], return_meta=True)
    else:
        scores_p1 = scores

    perm_dist_vs_p1 = _permutation_distance(scores, scores_p1)

    result.update({
        "status": "complete",
        "n": n, "m": m, "density": density,
        "total_edge_weight": total_weight,
        "removed_phaseA_count": removed_phaseA_count,
        "removed_phaseA_weight": removed_weight_phaseA,
        "removed_final_count": removed_final_count,
        "removed_final_weight": removed_final_weight,
        "normalized_removed_weight": removed_final_weight / total_weight if total_weight > 0 else 0.0,
        "restored_edge_count": max(0, restored_count),
        "mincut_attempts": mincut_attempts,
        "mincut_accepted": mincut_accepted,
        "mincut_gain": mincut_gain,
        "upset_simple": upset_s,
        "upset_ratio": upset_r,
        "upset_naive": upset_n,
        "permutation_distance_vs_p1": perm_dist_vs_p1,
        "runtime_total_sec": time.time() - t0,
        "runtime_phaseA_sec": float(meta.get("time_phase1_sec", 0)),
        "runtime_phaseB_sec": float(meta.get("time_phase2_sec", 0)),
        "runtime_phaseC_sec": float(meta.get("time_phaseC_sec", 0)),
        "runtime_mincut_sec": mincut_time,
        "phase1_iterations": int(meta.get("phase1_iterations", 0)),
        "reinserted_per_pass": str(meta.get("reinserted_per_pass", [])),
        "break_reason": str(meta.get("break_reason", "")),
    })

    return result, []


def _write_csv(path, rows):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _build_run_plan():
    """Build the full list of (dataset, config_label, params) to run."""
    plan = []

    # Structural variants
    for label, params in STRUCTURAL_VARIANTS.items():
        layer = VARIANT_LAYERS[label]
        datasets = LAYER1 + LAYER2 if layer == "both" else LAYER1
        for ds, fam in datasets:
            plan.append((ds, fam, label, params.copy(), False))

    # Sensitivity configs (Layer 1 only)
    for group_name, configs in ALL_CONFIG_GROUPS.items():
        if group_name == "structural":
            continue
        for label, params in configs.items():
            for ds, fam in LAYER1:
                plan.append((ds, fam, label, params.copy(), False))

    # Finance stress
    for label, params in FINANCE_CONFIGS.items():
        for ds, fam in FINANCE:
            plan.append((ds, fam, f"FINANCE_{label}", params.copy(), True))

    return plan


def _classify_terminal(result: dict) -> str:
    """Map a result row to a terminal classification label."""
    status = str(result.get("status", ""))
    if status == "TIMEOUT_HARD_WALLCLOCK":
        return "TIMEOUT_HARD_WALLCLOCK"
    if status in ("error", "data_unavailable"):
        return "ERROR"
    if status == "complete" and str(result.get("break_reason", "")) == "time_limit":
        return "INTERNAL_TIME_LIMIT"
    if status == "complete":
        return "SUCCESS"
    return status or "unknown"


def _hard_wallclock_timeout_row(ds, family, config_label, wall_sec: float) -> dict:
    return {
        "dataset": ds,
        "family": family,
        "config": config_label,
        "config_hash": CONFIG_HASH,
        "timestamp": time.time(),
        "status": "TIMEOUT_HARD_WALLCLOCK",
        "n": "",
        "m": "",
        "density": "",
        "total_edge_weight": "",
        "removed_phaseA_count": "",
        "removed_phaseA_weight": "",
        "removed_final_count": "",
        "removed_final_weight": "",
        "normalized_removed_weight": "",
        "restored_edge_count": "",
        "mincut_attempts": "",
        "mincut_accepted": "",
        "mincut_gain": "",
        "upset_simple": "",
        "upset_ratio": "",
        "upset_naive": "",
        "permutation_distance_vs_p1": "",
        "runtime_total_sec": wall_sec,
        "runtime_phaseA_sec": "",
        "runtime_phaseB_sec": "",
        "runtime_phaseC_sec": "",
        "runtime_mincut_sec": "",
        "phase1_iterations": "",
        "reinserted_per_pass": "",
        "break_reason": "hard_wallclock_timeout",
        "terminal_classification": "TIMEOUT_HARD_WALLCLOCK",
    }


def _run_config_with_hard_wallclock(ds, family, config_label, params, is_finance, wall_sec: float):
    """Run one config under a hard external wall-clock (process kill).

    Preserves algorithm parameters / internal time_limit_sec unchanged.
    Returns (result_dict, elapsed_sec).
    """
    import multiprocessing as mp

    q: mp.Queue = mp.Queue()

    def _worker(queue, ds_, fam_, label_, params_, is_fin_):
        try:
            result, _ = run_config(ds_, fam_, label_, params_, is_fin_)
            result["terminal_classification"] = _classify_terminal(result)
            queue.put(("ok", result))
        except Exception as exc:  # noqa: BLE001 — must surface to parent
            queue.put(("error", str(exc)[:400]))

    t0 = time.time()
    proc = mp.Process(
        target=_worker,
        args=(q, ds, family, config_label, params, is_finance),
    )
    proc.start()
    proc.join(wall_sec)
    elapsed = time.time() - t0

    if proc.is_alive():
        proc.terminate()
        proc.join(30)
        if proc.is_alive():
            proc.kill()
            proc.join(10)
        result = _hard_wallclock_timeout_row(ds, family, config_label, elapsed)
        return result, elapsed

    if not q.empty():
        kind, payload = q.get()
        if kind == "ok":
            return payload, elapsed
        result = {
            "dataset": ds,
            "family": family,
            "config": config_label,
            "config_hash": CONFIG_HASH,
            "timestamp": time.time(),
            "status": "error",
            "error": payload,
            "runtime_total_sec": elapsed,
            "break_reason": "exception",
            "terminal_classification": "ERROR",
        }
        return result, elapsed

    # Process died without a queue payload
    result = {
        "dataset": ds,
        "family": family,
        "config": config_label,
        "config_hash": CONFIG_HASH,
        "timestamp": time.time(),
        "status": "error",
        "error": f"worker_exitcode={proc.exitcode}",
        "runtime_total_sec": elapsed,
        "break_reason": "worker_crash",
        "terminal_classification": "ERROR",
    }
    return result, elapsed


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only-config",
        default=None,
        help="Run only this config label (e.g. FINANCE_A6). Checkpoint still skips if done.",
    )
    parser.add_argument(
        "--hard-wallclock-sec",
        type=float,
        default=None,
        help="Hard per-config wall-clock (process kill). Applied only to --only-config runs.",
    )
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger_path = OUT_DIR / "_progress.jsonl"

    # Load completed
    done = set()
    if ledger_path.exists():
        with ledger_path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("config_hash") == CONFIG_HASH:
                    done.add((rec["dataset"], rec["config"]))

    plan = _build_run_plan()
    if args.only_config:
        plan = [p for p in plan if p[2] == args.only_config]
        if not plan:
            print(f"ERROR: no plan entries for --only-config={args.only_config}", flush=True)
            return 2

    total = len(plan)
    print(f"Config hash: {CONFIG_HASH}", flush=True)
    print(f"Total planned runs (this invocation): {total}", flush=True)
    print(f"Already completed (ledger unique pairs): {len(done)}", flush=True)
    if args.only_config:
        print(f"Only-config filter: {args.only_config}", flush=True)
    if args.hard_wallclock_sec is not None:
        print(f"Hard wall-clock sec: {args.hard_wallclock_sec}", flush=True)

    # Load existing results
    all_results = []
    raw_path = OUT_DIR / "raw_runs.csv"
    if raw_path.exists():
        with raw_path.open() as f:
            for row in csv.DictReader(f):
                all_results.append(row)

    # Write manifest
    full_plan = _build_run_plan()
    manifest = {
        "config_hash": CONFIG_HASH,
        "total_planned": len(full_plan),
        "layer1_count": len(LAYER1),
        "layer2_count": len(LAYER2),
        "finance_count": len(FINANCE),
        "structural_variants": list(STRUCTURAL_VARIANTS.keys()),
        "cycle_configs": list(CYCLE_CONFIGS.keys()),
        "zero_tol_configs": list(ZERO_TOL_CONFIGS.keys()),
        "refinement_configs": list(REFINE_CONFIGS.keys()),
        "legacy_pass_configs": list(PASS_CONFIGS.keys()),
        "mincut_budget_configs": list(MINCUT_CONFIGS.keys()),
        "finance_configs": list(FINANCE_CONFIGS.keys()),
    }
    with (OUT_DIR / "experiment_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)

    # Write dataset manifest
    ds_rows = []
    for ds, fam in LAYER1:
        ds_rows.append({"dataset": ds, "family": fam, "layer": 1})
    for ds, fam in LAYER2:
        ds_rows.append({"dataset": ds, "family": fam, "layer": 2})
    for ds, fam in FINANCE:
        ds_rows.append({"dataset": ds, "family": fam, "layer": "finance"})
    _write_csv(OUT_DIR / "dataset_manifest.csv", ds_rows)

    ran = 0
    for i, (ds, fam, config_label, params, is_finance) in enumerate(plan):
        key = (ds, config_label)
        if key in done:
            print(f"[skip] {ds} / {config_label} (checkpoint)", flush=True)
            continue

        print(f"[{i+1}/{total}] {ds} / {config_label} ...", flush=True, end=" ")
        t0 = time.time()

        if args.hard_wallclock_sec is not None and args.only_config:
            result, dt = _run_config_with_hard_wallclock(
                ds, fam, config_label, params, is_finance, args.hard_wallclock_sec
            )
        else:
            result, _raw = run_config(ds, fam, config_label, params, is_finance)
            dt = time.time() - t0
            result["terminal_classification"] = _classify_terminal(result)

        status = result.get("status", "unknown")
        term = result.get("terminal_classification", _classify_terminal(result))
        print(f"{status}/{term} ({dt:.2f}s)", flush=True)

        # Append to ledger
        rec = {
            "dataset": ds, "config": config_label,
            "config_hash": CONFIG_HASH, "timestamp": time.time(),
            "status": status, "runtime_sec": dt,
            "terminal_classification": term,
        }
        with ledger_path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

        # Add to results
        all_results.append(result)
        ran += 1

        # Rewrite CSVs periodically
        _write_csv(raw_path, all_results)

    # Final write
    _write_csv(raw_path, all_results)

    print(f"\nDone. ran={ran} total_rows={len(all_results)}. Outputs in {OUT_DIR}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
