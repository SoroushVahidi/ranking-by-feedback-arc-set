# Phase 2: Weight-Prioritized Add-Back / INS1–3 variants — Methods audit

Exact Phase B algorithm from `src/ours_mfas.py` with file:line references.

---

## 1) Call site and inputs/outputs

- **Called from:** `ours_mfas_rmfa` (**606–616**). Phase B runs immediately after Phase A; its result is the DAG used for scoring (and for optional pass-wise scores when `return_all_pass_scores=True`).

- **Function:** `_addback_desc_weight_multi` (**217–282**).

- **Inputs:**
  - `n`: number of vertices (**218**).
  - `kept_initial`: boolean mask of length *m* (edges kept after Phase A) (**219**).
  - `src`, `dst`, `w`: length-*m* arrays (edge sources, targets, **original** weights) (**220–222**).
  - `insertion_passes`: number of passes (INS1=1, INS2=2, INS3=3) (**223**).
  - `time_limit_sec`, `t0`: global time limit and start time (**224–225**).

- **Outputs** (**226**, **239–237**, **282**):
  - `kept`: final boolean mask (edges in the DAG after all passes).
  - `kept_after`: list of kept masks after each pass (`kept.copy()` at end of pass) (**276**).
  - `reinserted_per_pass`: list of counts of edges reinserted in each pass (**277**).
  - `changed_edges_per_pass`: same as `reinserted_per_pass` in the current implementation (**278**).
  - `break_reason`: string — `"max_passes"` | `"time_limit"` | `"topo_failure"` | `"no_change"` (**246**, **251**, **256**, **261**, **281**).

**References:** `src/ours_mfas.py` 606–616 (call), 217–226, 239, 276–282 (signature and returns).

---

## 2) Edge processing order

- **Sort:** **Descending by original weight `w`**, with **stable** sort so equal weights keep a fixed order.  
  **`order = np.argsort(-w, kind="mergesort")`** (**240**). So `order` is a permutation of edge indices: first index is the edge with largest `w`, etc.

- **Scan:** Over **all** edges in that order. For each edge index `ei` in `order` (**265**):  
  - If **`kept[ei]`** is already True, **skip** (**268–269**).  
  - Otherwise (edge was removed in Phase A or not yet reinserted this pass), test reinsertion.  
  So we scan the full edge list each pass; only currently-not-kept edges are candidates for reinsertion. No separate “removed only” list; the `kept[ei]` check implements “skip already kept.”

**References:** `src/ours_mfas.py` 240, 265–275.

---

## 3) Acyclicity check

- **Topological order:** Computed by **`_toposort_kahn_from_edges(n, src, dst, kept)`** (**254**). That function implements **Kahn’s algorithm**: indegrees from `kept` edges, queue of indeg-0 vertices, then repeatedly pop and decrement indeg of neighbors (**48–75**).

- **Reinsertion criterion:** An edge *ei* (u→v) is reinserted **iff** **`pos[u] < pos[v]`** (**273**), where `pos` is the position in the topological order: `pos[v] = i` for `topo[i] == v` (**259–261**). So only **forward** edges in the current topo order are added. The docstring (**231–232**) states that adding such edges preserves acyclicity because the same order remains a valid topological order.

- **When topo is computed:** **Once per pass**, at the **start** of the pass (**253**). It is **not** updated after each insertion within the pass. So within a single pass, eligibility is fixed: an edge u→v is eligible iff it is not yet kept and `pos[u] < pos[v]` in that pass’s topo.

**References:** `src/ours_mfas.py` 48–75 (`_toposort_kahn_from_edges`), 253–275, 229–232 (docstring).

---

## 4) Multi-pass behavior (INS1 / INS2 / INS3)

- **Number of passes:** **`passes = max(1, int(insertion_passes))`** (**246**). So INS1→1 pass, INS2→2, INS3→3.

- **Early exit conditions (in order checked):**
  1. **Time limit:** At start of each pass, **`if time.time() - t0 > time_limit_sec: break`** → `break_reason = "time_limit"` (**249–251**).
  2. **Topo failure:** If **`_toposort_kahn_from_edges`** returns **`None`** (graph with `kept` is cyclic), break → `break_reason = "topo_failure"` (**254–257**).
  3. **No change:** After scanning all edges in a pass, if **`changed == 0`** (no edge reinserted this pass), break → `break_reason = "no_change"` (**279–281**).
  4. Otherwise loop runs for `passes` iterations, then `break_reason = "max_passes"` (**246**).

- **Per-pass actions:** At start of pass: compute `topo` and `pos`. Then for each `ei` in `order`: if not kept and `pos[u] < pos[v]`, set `kept[ei] = True` and increment `changed`. Append **`kept.copy()`** to `kept_after`, and `changed` to `reinserted_per_pass` and `changed_edges_per_pass` (**276–278**).

- **Meta fields (in `ours_mfas_rmfa` when `return_meta=True`):**
  - **`reinserted_per_pass`**: list of reinsertion counts per pass (**699**).
  - **`changed_edges_per_pass`**: same list (**700**).
  - **`insertion_passes`**: requested number of passes (**701**).
  - **`executed_passes`**: **`len(kept_after_pass)`** — number of passes actually completed (**702**).
  - **`break_reason`**: string as above (**703**).
  - **`kept_final`**: **`int(np.sum(kept_final))`** — total edges in final DAG (**698**).

**References:** `src/ours_mfas.py` 248–281, 698–703.

---

## 5) Determinism

- **Edge order:** **Stable sort** by weight: **`kind="mergesort"`** (**240**). So equal-weight edges have a fixed order (by original edge index).

- **Toposort (Kahn):** Initial queue is **`deque([i for i in range(n) if indeg[i] == 0])`** — vertices with indeg 0 in **ascending vertex id** order (**56**). New zeros are appended when they appear (**70**). So tie-breaking is deterministic (queue order).

- **Scan over edges:** Iteration over `order` (fixed permutation) and over `np.nonzero(kept)[0]` inside the toposort is in array order. No randomness or system-dependent order in Phase B.

**References:** `src/ours_mfas.py` 240, 56, 70.

---

## 6) Limitations and implications

- **Eligible edges in a pass:** In that pass we use **one** topological order of the **current** `kept` graph. An edge u→v (not yet kept) is reinserted **only if** `pos[u] < pos[v]` in that topo. So eligibility is fixed for the whole pass. Edges that are “back” in this topo (pos[u] ≥ pos[v]) are not reinserted in this pass even if adding them could be consistent with some other extension of the DAG; the next pass (if any) recomputes topo from the updated `kept`, so some of those back edges may become forward and get added in a later pass.

- **DAG guarantee:** The code **does** keep the graph acyclic after each reinsertion and after each pass: only edges with `pos[u] < pos[v]` are added, and the docstring (**231–232**) notes that adding such forward edges preserves the same topological order. So the kept graph is a DAG at the start of each pass (by induction: Phase A output is a DAG; each pass only adds forward edges). If `_toposort_kahn_from_edges` were ever given a cyclic `kept` (e.g. bug or non-DAG Phase A output), it would return `None` and Phase B would break with `topo_failure` (**254–257**).

- **No per-insertion topo update:** Because topo is fixed per pass, the order in which edges are considered (by descending `w`) matters: an earlier reinserted edge changes `kept` and thus can change which later edges are still “forward” in the **next** pass, but within the same pass the criterion is fixed. So the algorithm is a multi-pass greedy add-back in weight order, with one topo per pass.

**References:** `src/ours_mfas.py` 229–232, 253–275, 254–257.

---

## Summary table

| Item | Implementation | Reference |
|------|----------------|-----------|
| Caller | `ours_mfas_rmfa` | 606–616 |
| Inputs | `kept_initial`, `src`, `dst`, `w`, `insertion_passes`, `time_limit_sec`, `t0` | 218–225 |
| Edge order | `order = np.argsort(-w, kind="mergesort")` (desc weight, stable) | 240 |
| Scan | All edges in `order`; skip if `kept[ei]` | 265–269 |
| Topo | `_toposort_kahn_from_edges(n, src, dst, kept)` (Kahn) | 254, 48–75 |
| Reinsert criterion | `pos[u] < pos[v]` (forward in topo) | 273, 259–261 |
| Topo frequency | Once per pass at start of pass | 253 |
| Passes | INS1=1, INS2=2, INS3=3; `max(1, int(insertion_passes))` | 246 |
| Early stop | time_limit, topo_failure, no_change (changed==0) | 249–251, 254–257, 279–281 |
| Meta | reinserted_per_pass, executed_passes, break_reason, kept_final | 699–703, 698 |
| Determinism | mergesort; Kahn queue by vertex id; no randomness | 240, 56, 70 |
| DAG guarantee | Only forward edges added; topo recomputed each pass | 231–232, 273 |
