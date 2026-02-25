# ours_mfas.py
# RMFA / OURS_MFAS with:
#  (A) local-ratio MFAS cycle breaking (edge-accurate, fast)
#  (B) add-back in descending weight order with INS passes (1/2/3)
#  (C) optional ratio-upset postprocessing using ternary-search while preserving order
#
# Designed to be fast, deterministic, and time-limit friendly.

from __future__ import annotations

import time
from collections import deque
from typing import Dict, List, Tuple, Optional, Sequence

import numpy as np
import scipy.sparse as sp


# =============================================================================
# Helpers: build edges and adjacency (EDGE-ID based)
# =============================================================================

def _csr_to_edges(A: sp.spmatrix) -> Tuple[int, np.ndarray, np.ndarray, np.ndarray]:
    """
    Return (n, src, dst, w) for all directed edges with w>0.
    """
    A = A.tocsr()
    A.eliminate_zeros()
    n = int(A.shape[0])
    src, dst = A.nonzero()
    w = np.asarray(A[src, dst]).reshape(-1)
    # filter strictly positive (guard against numeric noise)
    mask = w > 0
    return n, src[mask].astype(np.int64), dst[mask].astype(np.int64), w[mask].astype(np.float64)


def _build_adj_edges(n: int, src: np.ndarray, dst: np.ndarray, alive: np.ndarray) -> List[List[int]]:
    """
    Build adjacency list of EDGE IDS: adj_e[u] = [eid1, eid2, ...] where eid is alive and src[eid]=u.
    """
    adj_e: List[List[int]] = [[] for _ in range(n)]
    alive_idx = np.nonzero(alive)[0]
    for ei in alive_idx:
        adj_e[int(src[ei])].append(int(ei))
    return adj_e


def _toposort_kahn_from_edges(n: int, src: np.ndarray, dst: np.ndarray, kept: np.ndarray) -> Optional[List[int]]:
    """
    Topological order for a graph given by kept edge mask over edge list (src,dst).
    Return None if cyclic (should not happen if kept is a DAG).
    """
    indeg = np.zeros(n, dtype=np.int64)
    for ei in np.nonzero(kept)[0]:
        indeg[int(dst[ei])] += 1

    q = deque([i for i in range(n) if indeg[i] == 0])
    order: List[int] = []
    # adjacency from kept edges (vertex -> list of neighbors)
    adj = [[] for _ in range(n)]
    for ei in np.nonzero(kept)[0]:
        adj[int(src[ei])].append(int(dst[ei]))

    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if len(order) != n:
        return None
    return order


# =============================================================================
# Phase A: DFS cycle detection returning EDGE-ID cycle + local-ratio reduction
# =============================================================================

def _find_one_cycle_edges(
    n: int,
    src: np.ndarray,
    dst: np.ndarray,
    adj_e: List[List[int]],
) -> Optional[List[int]]:
    """
    Find one directed cycle in the current graph and return it as a list of EDGE IDs:
      [e0, e1, ..., ek-1] representing vertices v0->v1->...->vk->v0.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = np.zeros(n, dtype=np.int8)

    parent_v = np.full(n, -1, dtype=np.int64)
    parent_e = np.full(n, -1, dtype=np.int64)

    # iterative DFS to avoid recursion depth issues
    for s in range(n):
        if color[s] != WHITE:
            continue

        stack: List[Tuple[int, int]] = [(s, 0)]  # (vertex, next edge index to explore)
        parent_v[s] = -1
        parent_e[s] = -1

        while stack:
            u, it = stack[-1]
            if color[u] == WHITE:
                color[u] = GRAY

            if it >= len(adj_e[u]):
                color[u] = BLACK
                stack.pop()
                continue

            ei = adj_e[u][it]
            v = int(dst[ei])
            stack[-1] = (u, it + 1)

            if color[v] == WHITE:
                parent_v[v] = u
                parent_e[v] = ei
                stack.append((v, 0))
            elif color[v] == GRAY:
                # Found back edge u -> v (ei), reconstruct cycle as EDGE IDs
                # Path: v ... u plus the back edge u->v.
                cycle_edges: List[int] = [int(ei)]
                cur = u
                # walk parents until reaching v
                while cur != v and cur != -1:
                    pe = int(parent_e[cur])
                    if pe == -1:
                        # reconstruction failed (should be rare)
                        return None
                    cycle_edges.append(pe)
                    cur = int(parent_v[cur])
                if cur != v:
                    return None
                cycle_edges.reverse()  # now in traversal order around the cycle
                return cycle_edges

    return None


def _local_ratio_break_cycles(
    n: int,
    src: np.ndarray,
    dst: np.ndarray,
    w: np.ndarray,
    time_limit_sec: float,
    t0: float,
    zero_tol: float = 1e-15,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Local-ratio style:
      - maintain residual weights r
      - while cycle exists: subtract min residual on cycle edges from all edges in that cycle
      - remove edges whose residual hits 0
    Returns:
      kept_phaseA (bool over edges kept after reduction),
      removed_phaseA (bool over edges removed in Phase A),
      residual (final residual weights for all edges)
    """
    m = int(len(w))
    residual = w.copy()
    alive = np.ones(m, dtype=bool)

    # To keep deterministic behavior, we rebuild adj from alive each iteration.
    # This is okay with the global time limit; edge-level reconstruction avoids O(m) scans.
    while True:
        if time.time() - t0 > time_limit_sec:
            break

        adj_e = _build_adj_edges(n, src, dst, alive)
        cyc_e = _find_one_cycle_edges(n, src, dst, adj_e)
        if cyc_e is None:
            break

        # subtract delta = min residual on the cycle edges
        delta = float(np.min(residual[cyc_e]))
        if delta <= 0.0:
            # numerical guard; force progress by killing the minimum edge
            ei_min = int(cyc_e[int(np.argmin(residual[cyc_e]))])
            residual[ei_min] = 0.0
        else:
            residual[cyc_e] -= delta

        # kill edges that reached ~0
        dead = (residual <= zero_tol) & alive
        if np.any(dead):
            alive[dead] = False
        else:
            # In very rare numeric corner cases, ensure progress: kill the minimum edge on cycle
            ei_min = int(cyc_e[int(np.argmin(residual[cyc_e]))])
            alive[ei_min] = False
            residual[ei_min] = 0.0

    removed = ~alive
    return alive, removed, residual


# =============================================================================
# Phase B: add-back in descending weight order with INS passes
# =============================================================================

def _addback_desc_weight_multi(
    n: int,
    kept_initial: np.ndarray,      # bool over edges kept after Phase A
    src: np.ndarray,
    dst: np.ndarray,
    w: np.ndarray,
    insertion_passes: int,         # INS1/2/3 -> 1/2/3 passes
    time_limit_sec: float,
    t0: float,
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Add-back edges in descending weight order, but only if they keep the graph acyclic.

    We compute a topological order of the current kept graph at the start of each pass.
    Adding any edge u->v that is forward in that order (pos[u] < pos[v]) preserves acyclicity
    because the same order remains a valid topological order after adding forward edges.

    Returns:
      kept_final,
      kept_after_each_pass: list of kept masks after pass1, pass2, ...
    """
    kept = kept_initial.copy()
    order = np.argsort(-w, kind="mergesort")  # stable descending by weight

    kept_after: List[np.ndarray] = []
    passes = max(1, int(insertion_passes))

    for _p in range(passes):
        if time.time() - t0 > time_limit_sec:
            break

        topo = _toposort_kahn_from_edges(n, src, dst, kept)
        if topo is None:
            # should not happen if kept is a DAG
            break

        pos = np.empty(n, dtype=np.int64)
        for i, v in enumerate(topo):
            pos[int(v)] = i

        changed = 0
        for ei in order:
            if time.time() - t0 > time_limit_sec:
                break
            if kept[ei]:
                continue
            u = int(src[ei])
            v = int(dst[ei])
            if pos[u] < pos[v]:
                kept[ei] = True
                changed += 1

        kept_after.append(kept.copy())
        if changed == 0:
            break

    return kept, kept_after


# =============================================================================
# Convert DAG -> scores (topo order)
# =============================================================================

def _scores_from_kept_edges(n: int, kept: np.ndarray, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """
    Return scores where larger score = better rank.
    We use a topo order: earlier in topo => larger score.
    """
    topo = _toposort_kahn_from_edges(n, src, dst, kept)
    if topo is None:
        topo = list(range(n))

    pos = np.empty(n, dtype=np.int64)
    for i, v in enumerate(topo):
        pos[int(v)] = i

    scores = (n - pos).astype(np.float64)
    # keep strictly positive
    scores = np.maximum(scores, 1.0)
    return scores


# =============================================================================
# Phase C: ratio upset loss + ternary coordinate refinement (order-preserving)
# =============================================================================

def _pair_arrays_from_A(A: sp.spmatrix, eps: float = 1e-12) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build pairwise arrays for ratio upset:
      For each unordered pair (i<j) with A_ij + A_ji > 0:
        m3 = (A_ij - A_ji) / (A_ij + A_ji + eps)
    Returns arrays (I, J, M3).
    """
    A = A.tocsr()
    A.eliminate_zeros()
    n = A.shape[0]

    # We'll accumulate using a dict keyed by (i,j). This is correct and robust.
    # If you later need more speed, we can do a sparse trick; keep correctness first.
    r, c = A.nonzero()
    data = np.asarray(A[r, c]).reshape(-1)

    pair: Dict[Tuple[int, int], List[float]] = {}
    for u, v, ww in zip(r, c, data):
        if ww <= 0:
            continue
        i = int(u); j = int(v)
        if i == j:
            continue
        a, b = (i, j) if i < j else (j, i)
        cur = pair.get((a, b))
        if cur is None:
            cur = [0.0, 0.0]
            pair[(a, b)] = cur
        if i < j:
            cur[0] += float(ww)  # a->b
        else:
            cur[1] += float(ww)  # b->a

    I = np.empty(len(pair), dtype=np.int64)
    J = np.empty(len(pair), dtype=np.int64)
    M3 = np.empty(len(pair), dtype=np.float64)
    for k, ((i, j), (aij, aji)) in enumerate(pair.items()):
        den = aij + aji + eps
        I[k] = i
        J[k] = j
        M3[k] = (aij - aji) / den

    return I, J, M3


def ratio_upset_loss_from_pairs(I: np.ndarray, J: np.ndarray, M3: np.ndarray, s: np.ndarray, eps: float = 1e-12) -> float:
    si = s[I]
    sj = s[J]
    T = (si - sj) / (si + sj + eps)
    diff = (M3 - T)
    return float(np.mean(diff * diff))


def _ternary_opt_one(
    I: np.ndarray, J: np.ndarray, M3: np.ndarray,
    s: np.ndarray,
    idx: int,
    lo: float,
    hi: float,
    iters: int,
    eps: float = 1e-12,
) -> float:
    """
    Ternary search to minimize ratio upset loss w.r.t s[idx] with all other s fixed,
    but only on pairs that include idx.
    """
    if not (hi > lo):
        return float(s[idx])

    mask = (I == idx) | (J == idx)
    if not np.any(mask):
        return float(s[idx])

    I2 = I[mask]
    J2 = J[mask]
    M32 = M3[mask]

    other = s  # reuse array; we'll restore s[idx] after checks
    oldv = float(other[idx])

    def loss_at(x: float) -> float:
        other[idx] = x
        return ratio_upset_loss_from_pairs(I2, J2, M32, other, eps=eps)

    a = float(lo)
    b = float(hi)
    for _ in range(int(iters)):
        m1 = a + (b - a) / 3.0
        m2 = b - (b - a) / 3.0
        f1 = loss_at(m1)
        f2 = loss_at(m2)
        if f1 < f2:
            b = m2
        else:
            a = m1
        if (b - a) < 1e-9:
            break

    mid = 0.5 * (a + b)
    candidates = [(a, loss_at(a)), (mid, loss_at(mid)), (b, loss_at(b))]
    xbest = min(candidates, key=lambda t: t[1])[0]
    other[idx] = oldv
    return float(xbest)


def refine_scores_ratio_ternary(
    A: sp.spmatrix,
    scores: np.ndarray,
    passes: int = 3,
    ternary_iters: int = 25,
    time_limit_sec: float = 15.0,
    eps: float = 1e-12,
) -> np.ndarray:
    """
    Coordinate-wise refinement that preserves ordering:
      - sort nodes by current score
      - update each node's score within neighbor bounds [prev+margin, next-margin]
      - uses ternary search to reduce ratio upset loss
    """
    tstart = time.time()
    s = scores.astype(np.float64).copy()
    s = np.maximum(s, 1.0)

    I, J, M3 = _pair_arrays_from_A(A, eps=eps)
    if len(I) == 0:
        return s

    margin = 1e-6

    for _p in range(max(1, int(passes))):
        if time.time() - tstart > time_limit_sec:
            break

        order = np.argsort(s)  # ascending
        for k in range(len(order)):
            if time.time() - tstart > time_limit_sec:
                break
            idx = int(order[k])

            if k == 0:
                lo = 1.0
                hi = (s[int(order[k + 1])] - margin) if len(order) > 1 else (s[idx] + 1.0)
            elif k == len(order) - 1:
                lo = s[int(order[k - 1])] + margin
                hi = float(np.max(s) + 1.0)
            else:
                lo = s[int(order[k - 1])] + margin
                hi = s[int(order[k + 1])] - margin

            if hi <= lo:
                continue

            newv = _ternary_opt_one(I, J, M3, s, idx, lo, hi, ternary_iters, eps=eps)
            s[idx] = newv

        # monotone repair
        order = np.argsort(s)
        for k in range(1, len(order)):
            a = int(order[k - 1])
            b = int(order[k])
            if s[b] <= s[a]:
                s[b] = s[a] + margin

    return s


# =============================================================================
# Main entry used by comparison code
# =============================================================================

def ours_mfas_rmfa(
    A: sp.spmatrix,
    insertion_passes: int = 3,          # INS1=1, INS2=2, INS3=3
    time_limit_sec: float = 900.0,
    refine_ratio: bool = True,
    refine_time_sec: float = 20.0,
    refine_passes: int = 2,
    ternary_iters: int = 20,
    return_meta: bool = False,
    return_all_pass_scores: bool = False,   # NEW: return scores after each pass (INS1/2/3)
):
    """
    Returns:
      scores (np.ndarray shape (n,))
      if return_all_pass_scores=True: also returns a list [scores_after_pass1, pass2, ...]
      if return_meta=True: returns (scores, meta) or (scores, pass_scores, meta)
    """
    t0 = time.time()

    n, src, dst, w = _csr_to_edges(A)

    # Phase A: local-ratio cycle breaking
    keptA, removedA, residual = _local_ratio_break_cycles(
        n, src, dst, w,
        time_limit_sec=float(time_limit_sec),
        t0=t0
    )

    # Phase B: add-back (desc weight) with INS passes
    kept_final, kept_after_pass = _addback_desc_weight_multi(
        n=n,
        kept_initial=keptA,
        src=src,
        dst=dst,
        w=w,
        insertion_passes=int(insertion_passes),
        time_limit_sec=float(time_limit_sec),
        t0=t0,
    )

    # Scores from DAG after final kept
    scores_final = _scores_from_kept_edges(n, kept_final, src, dst)

    # If requested, build scores after each pass (INS1/INS2/INS3)
    pass_scores: List[np.ndarray] = []
    if return_all_pass_scores:
        for kept_mask in kept_after_pass:
            pass_scores.append(_scores_from_kept_edges(n, kept_mask, src, dst))

        # If fewer passes executed (timeouts / early stop), still include final as last
        if len(pass_scores) == 0:
            pass_scores = [scores_final.copy()]
        elif len(pass_scores) < int(insertion_passes):
            # append the last available (already final or close)
            while len(pass_scores) < int(insertion_passes):
                pass_scores.append(pass_scores[-1].copy())

    # Phase C: optional ratio refinement (bounded by refine_time_sec, also never exceeding global limit)
    def _maybe_refine(s_in: np.ndarray) -> np.ndarray:
        if not refine_ratio:
            return s_in
        remaining = max(0.0, float(time_limit_sec) - (time.time() - t0))
        budget = min(float(refine_time_sec), remaining)
        if budget <= 0.05:
            return s_in
        return refine_scores_ratio_ternary(
            A=A,
            scores=s_in,
            passes=int(refine_passes),
            ternary_iters=int(ternary_iters),
            time_limit_sec=float(budget),
        )

    if return_all_pass_scores:
        # refine each pass score with the *same* refinement budget style
        pass_scores = [_maybe_refine(s) for s in pass_scores]
        scores_final = pass_scores[min(len(pass_scores), int(insertion_passes)) - 1].copy()
    else:
        scores_final = _maybe_refine(scores_final)

    if not return_meta:
        if return_all_pass_scores:
            return scores_final, pass_scores
        return scores_final

    meta = {
        "n": int(n),
        "m": int(len(w)),
        "removed_phaseA": int(np.sum(~keptA)),
        "kept_after_phaseA": int(np.sum(keptA)),
        "kept_final": int(np.sum(kept_final)),
        "insertion_passes": int(insertion_passes),
        "executed_passes": int(len(kept_after_pass)),
        "refine_ratio": bool(refine_ratio),
        "runtime_sec": float(time.time() - t0),
        "time_limit_sec": float(time_limit_sec),
    }

    if return_all_pass_scores:
        return scores_final, pass_scores, meta
    return scores_final, meta