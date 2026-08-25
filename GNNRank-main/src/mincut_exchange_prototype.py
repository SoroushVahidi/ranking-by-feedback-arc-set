# mincut_exchange_prototype.py
#
# PROTOTYPE, NOT WIRED INTO THE PRODUCTION PIPELINE.
#
# Implements a single candidate operator identified in
# docs/journal_supercomputing_revision_20260824/MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md
# and formalized further in JSUPER_CANDIDATE_DIRECTIONS_AND_FORMAL_CHECKS.md section I:
#
#   Given a kept DAG D, an excluded edge e=(u,v) with v reaching u in D (so plain
#   exact-reachability add-back -- ours_mfas.py::_addback_reachability -- already
#   rejects it), find a minimum-capacity directed v->u edge cut C in D (capacities
#   = kept-edge weights). If w(C) < w(e) (strictly, beyond a numerical tolerance),
#   accept the exchange D' = (D \ C) u {e}; otherwise reject and leave D unchanged.
#
# Deliberately kept as a separate module from ours_mfas.py (rather than added
# there) so that:
#   (a) this prototype's new networkx dependency is not silently added to the
#       production pipeline file's import surface;
#   (b) it is trivially auditable that ours_mfas_rmfa() and comparison.py's
#       public wrappers (ours_MFAS, ours_MFAS_REACH) are UNCHANGED by this file
#       -- confirmed by `git diff` showing no modification to either.
#
# This module intentionally does NOT implement: top-K sweeps, time budgets,
# adaptive operator selection, interval-local cuts, vertex relocation, or exact
# small-region solving. It implements exactly one operator and one minimal,
# deterministic, first-accepted-exchange candidate selector, per
# docs/journal_supercomputing_revision_20260824/MINCUT_EXCHANGE_PROTOTYPE_NOTES.md.

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import networkx as nx
from networkx.algorithms.flow import preflow_push

from ours_mfas import _toposort_kahn_from_edges

# Explicitly pinned deterministic max-flow backend for nx.minimum_cut.
#
# networkx's own default for minimum_cut is already preflow_push (confirmed by
# inspecting networkx.algorithms.flow.maxflow.default_flow_func at the time
# this pilot pass was written), so pinning it here changes no behavior versus
# the prototype branch's implicit default -- it only removes the dependency on
# that default *staying* preflow_push across future networkx versions. This is
# a version-safety pin, not a behavior change (confirmed by the prototype's
# existing 70-test suite still passing unmodified after this change).
_FLOW_FUNC = preflow_push


# Possible values of the "reason" field returned by _try_mincut_exchange.
REASON_ACCEPTED = "ACCEPTED"
REASON_INVALID_INPUT = "INVALID_INPUT"
REASON_SAFE_EDGE_NOT_EXCHANGE_CASE = "SAFE_EDGE_NOT_EXCHANGE_CASE"
REASON_NO_V_TO_U_PATH = "NO_V_TO_U_PATH"
REASON_NO_FINITE_CUT = "NO_FINITE_CUT"
REASON_NON_IMPROVING_CUT = "NON_IMPROVING_CUT"
REASON_NUMERICAL_TIE_REJECTED = "NUMERICAL_TIE_REJECTED"


def _build_kept_digraph(n: int, kept: np.ndarray, src: np.ndarray, dst: np.ndarray, w: np.ndarray) -> "nx.DiGraph":
    """Build a networkx DiGraph over the currently-kept edges, with edge weight
    stored both as the 'weight' attribute (used as max-flow capacity) and as
    'edge_id' (the index into the original src/dst/w arrays, needed to map cut
    edges back to edge ids for the caller).

    Deterministic construction: nodes added in a fixed 0..n-1 order, edges added
    by a single fixed-order pass over range(m) -- this determinism is required
    for the DETERMINISM property test, since networkx's default max-flow
    algorithm is not randomized but IS sensitive to graph construction order
    when multiple minimum cuts of equal weight exist (see
    MINCUT_EXCHANGE_PROTOTYPE_NOTES.md "deterministic tie handling" section).

    Parallel edges: not representable in this codebase's data model (each
    (u, v) ordered pair has at most one weight, since edges are derived from a
    single sparse adjacency matrix entry -- see ours_mfas.py::_csr_to_edges).
    If this module is ever fed a representation with true parallel arcs,
    plain nx.DiGraph would silently keep only the last-added edge for a given
    (u, v) pair; this has not been an issue in this pass, and is not tested,
    but is recorded here as a known limitation.
    """
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    m = int(len(w))
    for ei in range(m):
        if kept[ei]:
            u2 = int(src[ei])
            v2 = int(dst[ei])
            G.add_edge(u2, v2, weight=float(w[ei]), edge_id=int(ei))
    return G


def _try_mincut_exchange(
    n: int,
    kept: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    w: np.ndarray,
    ei: int,
    objective_tol: float = 1e-9,
) -> Dict:
    """Attempt one min-cut weighted exchange for the single excluded candidate
    edge with index `ei` (i.e. src[ei] -> dst[ei], weight w[ei]).

    Does NOT mutate `kept`. Returns a diagnostics dict; on ACCEPTED, the dict's
    'new_kept' field holds a *new* boolean array (kept.copy() with the cut edges
    turned off and `ei` turned on) -- the caller decides whether/how to adopt it.
    On any non-accepted outcome, 'new_kept' is None and the caller's `kept`
    remains the authoritative, unmodified state (state is never touched before
    acceptance is determined, and is never touched at all on rejection).

    Returned dict keys (always present):
      attempted, accepted, candidate_edge, candidate_weight, cut_edges,
      cut_weight, objective_delta, reason, reachability_before, acyclic_after,
      runtime_sec, new_kept.
    """
    t0 = time.time()
    diag: Dict = {
        "attempted": False,
        "accepted": False,
        "candidate_edge": None,
        "candidate_weight": None,
        "cut_edges": None,
        "cut_weight": None,
        "objective_delta": None,
        "reason": None,
        "reachability_before": None,
        "acyclic_after": None,
        "runtime_sec": None,
        "new_kept": None,
    }

    m = int(len(w))

    # ---- Input validation ----
    if not (0 <= ei < m):
        diag["reason"] = REASON_INVALID_INPUT
        diag["runtime_sec"] = time.time() - t0
        return diag

    u = int(src[ei])
    v = int(dst[ei])
    diag["candidate_edge"] = (u, v)
    diag["candidate_weight"] = float(w[ei])

    if u == v or not (0 <= u < n) or not (0 <= v < n):
        diag["reason"] = REASON_INVALID_INPUT
        diag["runtime_sec"] = time.time() - t0
        return diag

    if kept[ei]:
        # Nothing to exchange: this edge is not currently excluded.
        diag["reason"] = REASON_SAFE_EDGE_NOT_EXCHANGE_CASE
        diag["runtime_sec"] = time.time() - t0
        return diag

    diag["attempted"] = True

    # ---- Build the current kept subgraph and check reachability ----
    G = _build_kept_digraph(n, kept, src, dst, w)
    reach_v_to_u = nx.has_path(G, v, u) if (v in G and u in G) else False
    diag["reachability_before"] = bool(reach_v_to_u)

    if not reach_v_to_u:
        # This is exactly the case plain exact-reachability add-back already
        # handles (Setup item 1 of MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md)
        # -- this operator does not apply.
        diag["reason"] = REASON_NO_V_TO_U_PATH
        diag["runtime_sec"] = time.time() - t0
        return diag

    # ---- Minimum v->u edge cut, capacities = kept-edge weights ----
    try:
        cut_value, (S, T) = nx.minimum_cut(G, v, u, capacity="weight", flow_func=_FLOW_FUNC)
    except Exception:
        diag["reason"] = REASON_NO_FINITE_CUT
        diag["runtime_sec"] = time.time() - t0
        return diag

    cut_edge_ids: List[int] = sorted(
        int(G[a][b]["edge_id"]) for a, b in G.edges() if a in S and b in T
    )
    cut_weight = float(sum(float(w[eid]) for eid in cut_edge_ids))
    diag["cut_edges"] = cut_edge_ids
    diag["cut_weight"] = cut_weight

    candidate_weight = float(w[ei])
    delta = cut_weight - candidate_weight  # w(C) - w(e), matches the research-question doc's Claim 2
    diag["objective_delta"] = delta

    # ---- Acceptance rule: strict improvement beyond a numerical tolerance ----
    if cut_weight + objective_tol < candidate_weight:
        accept = True
    else:
        accept = False
        if abs(delta) <= objective_tol:
            diag["reason"] = REASON_NUMERICAL_TIE_REJECTED
        else:
            diag["reason"] = REASON_NON_IMPROVING_CUT

    if not accept:
        diag["runtime_sec"] = time.time() - t0
        return diag

    # ---- Apply the exchange to a NEW array; input `kept` is never mutated ----
    new_kept = kept.copy()
    for eid in cut_edge_ids:
        new_kept[eid] = False
    new_kept[ei] = True

    acyclic_after = _toposort_kahn_from_edges(n, src, dst, new_kept) is not None
    diag["acyclic_after"] = bool(acyclic_after)
    diag["accepted"] = True
    diag["reason"] = REASON_ACCEPTED
    diag["new_kept"] = new_kept
    diag["runtime_sec"] = time.time() - t0
    return diag


def run_first_accepted_exchange(
    n: int,
    kept_initial: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    w: np.ndarray,
) -> Tuple[np.ndarray, Optional[Dict]]:
    """Minimal, deterministic candidate selector for prototype/testing purposes
    ONLY (per this task's explicit scope: no top-K sweep, no time budget, no
    adaptive selection).

    Considers currently-excluded edges in stable descending weight order
    (matching every other add-back mechanism's ordering convention in this
    project -- see ours_mfas.py::_addback_reachability), attempts one exchange
    per candidate via _try_mincut_exchange, and stops at the FIRST accepted
    exchange. Returns (kept_after, diagnostics_of_the_accepted_attempt) or
    (kept_initial unchanged, None) if no candidate among the excluded edges is
    accepted.
    """
    kept = kept_initial.copy()
    order = np.argsort(-w, kind="mergesort")
    for ei in order:
        ei = int(ei)
        if kept[ei]:
            continue
        diag = _try_mincut_exchange(n, kept, src, dst, w, ei)
        if diag["accepted"]:
            return diag["new_kept"], diag
    return kept, None


def run_repeated_exchanges(
    n: int,
    kept_initial: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    w: np.ndarray,
    max_iterations: int = 50,
) -> Tuple[np.ndarray, List[Dict]]:
    """Repeatedly apply run_first_accepted_exchange-style single exchanges until
    no further strictly-improving exchange is found among currently-excluded
    edges, or `max_iterations` is reached (a safety bound for this prototype
    only -- Claim 4 in MINCUT_WEIGHTED_EXCHANGE_RESEARCH_QUESTION.md establishes
    termination for discrete/rational weights without needing this bound in
    principle; the bound here is defensive prototype scaffolding, not part of
    the theoretical claim).

    Used by the MULTI-EXCHANGE_TERMINATION_TOY test to confirm strictly
    decreasing removed weight and eventual termination on a toy graph.
    """
    kept = kept_initial.copy()
    accepted_log: List[Dict] = []
    for _ in range(max_iterations):
        order = np.argsort(-w, kind="mergesort")
        accepted_this_round = False
        for ei in order:
            ei = int(ei)
            if kept[ei]:
                continue
            diag = _try_mincut_exchange(n, kept, src, dst, w, ei)
            if diag["accepted"]:
                kept = diag["new_kept"]
                accepted_log.append(diag)
                accepted_this_round = True
                break  # restart the scan from the new state, descending-weight order
        if not accepted_this_round:
            break
    return kept, accepted_log
