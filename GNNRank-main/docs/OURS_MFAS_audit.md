# OURS (MFAS-based ranking) — Input/Output and determinism audit

Repo-only audit with file:line references.

---

## 1) Input representation

- **Canonical input type:** Scipy sparse matrix (CSR) or numpy dense converted to CSR. The OURS entry accepts `scores_matrix` (N×N directed weight matrix) as either scipy sparse or array-like; it is converted to `scipy.sparse.csr_matrix` before the core routine.
  - **`src/comparison.py`** 389–393: `if sp.issparse(W): A = W.tocsr(); else: A = sp.csr_matrix(np.asarray(W))`
  - **`src/ours_mfas.py`** 573–574: `ours_mfas_rmfa(A: sp.spmatrix, ...)` takes a scipy sparse matrix.

- **Where the dataset is loaded and converted:** Data is loaded in `preprocess.load_data`; the adjacency is stored as `data.A` (already scipy sparse) and passed to OURS without further conversion in the trainer.
  - **`src/preprocess.py`** 32–56: `load_data(args, random_seed)` returns `label, train_mask, val_mask, test_mask, data.x, data.A`; for real data it uses `load_real_data(args.dataset)` which returns `A`; for ERO it uses `extract_network` then `to_dataset_no_split` which sets `data.A = sp.csr_matrix(A)`.
  - **`src/train.py`** 119: `self.label, ..., self.A = load_data(args, random_seed)`; **640–646**: `ours_MFAS_INS1(self.A)` etc. So the trainer passes `self.A` (scipy sparse from `data.A`) directly.

- **Dataset file formats supported:** For real data, only **`adj.npz`** (scipy sparse saved with `scipy.sparse.save_npz`) is used.
  - **`src/preprocess.py`** 27–29: `load_real_data(dataset)` loads `A = sp.load_npz(os.path.join(..., '../data/'+dataset+'adj.npz'))`. No edge-list or other formats are loaded in this code path; ERO data is generated in memory, not from file.

---

## 2) Edge weights and graph semantics

- **Nonnegative weights:** Not enforced in OURS. Only edges with **w > 0** are used: `_csr_to_edges` filters with `mask = w > 0` (**`src/ours_mfas.py`** 32–33). Negative or zero entries are dropped and never appear in the internal edge list.

- **Both directions nonzero:** Allowed. The matrix can have both A[i,j] and A[j,i] nonzero; each nonzero is one directed edge. **`src/ours_mfas.py`** 23–33: one edge per nonzero; **394–434** `_pair_arrays_from_A`: pairs (i,j) with A_ij and A_ji are aggregated for ratio refinement (aij, aji summed per unordered pair).

- **Multiple edges between the same ordered pair:** In the sparse matrix, each stored nonzero is one edge. If the same (i,j) appears multiple times in the stored structure, `A.nonzero()` yields multiple (i,j) entries and they become multiple edges in (src, dst, w). There is **no aggregation** of (i,j) in `_csr_to_edges`; aggregation only happens in Phase C for **unordered** pairs in `_pair_arrays_from_A`. So for the main MFAS path, duplicate (i,j) in the matrix yield duplicate directed edges with (possibly) the same or different weights.

---

## 3) Converting input to internal edge list

- **Function that converts A to (src, dst, w):** **`_csr_to_edges`** in **`src/ours_mfas.py`** 23–33.

- **One directed edge per nonzero:** Yes. `src, dst = A.nonzero()`; `w = np.asarray(A[src, dst]).reshape(-1)`; one (src, dst, w) per nonzero (**`src/ours_mfas.py`** 29–30).

- **Filter by w > 0:** Yes. `mask = w > 0`; returns `n, src[mask], dst[mask], w[mask]` (**`src/ours_mfas.py`** 32–33).

- **Normalization or weight modification before Phase A:** None. Weights are used as returned from `_csr_to_edges` (positive only); no scaling or normalization is applied before Phase A (**`src/ours_mfas.py`** 419–422: `n, src, dst, w = _csr_to_edges(A)` then passed to `_local_ratio_break_cycles`).

---

## 4) Outputs of OURS

- **What the wrapper returns to the caller:** **Scores** (1D array, length n) and an **extra dict** with runtime and meta. No permutation/order array is returned; the ordering is implied by scores (higher score = better rank).
  - **`src/comparison.py`** 396–405, 408–426: `score_vec, meta = ours_mfas_rmfa(...)`; returns `(np.asarray(score_vec, dtype=float), extra)` with `extra` containing e.g. `runtime_sec`, `n`, `m`, `phase1_iterations`, `removed_phaseA`, `kept_final`, `reinserted_per_pass`, `time_phase1_sec`, etc.
  - **`src/train.py`** 640–646: `score, _ = ours_MFAS_INS3(self.A)` — only the score vector is used for evaluation.

- **Where the final ordering is computed:** From the DAG of “kept” edges: **`_scores_from_kept_edges`** (**`src/ours_mfas.py`** 289–306). It gets a topological order via **`_toposort_kahn_from_edges`** (254), then assigns scores as `scores = (n - pos)` so that **earlier in topo ⇒ larger score** (better rank). Optional **naive-upset refinement** (adjacent swaps) and **ratio refinement** (ternary search) modify scores but preserve the total order except where the refinement explicitly changes it; ties in scores are not defined by the code (scores are floats and typically distinct after refinement).

- **Tie-breaking:** The **ordering** is given by descending score; the code does not expose an explicit tie-breaking rule for equal scores. Internally, **`_scores_from_kept_edges`** assigns `scores = np.maximum(scores, 1.0)` so scores are ≥ 1; relative order is determined by the topo order and any later refinement.

---

## 5) Determinism and tie-breaking

- **Weight-order scan (add-back):** **Stable sort** is used so edge order for equal weights is fixed.
  - **`src/ours_mfas.py`** 240: `order = np.argsort(-w, kind="mergesort")  # stable descending by weight`.

- **Topological sort (Kahn):** Multiple eligible nodes are broken by **queue order**: initial queue is `deque([i for i in range(n) if indeg[i] == 0])` (vertex id 0..n-1), then new zeros are appended. So tie-breaking is **deterministic**: first by initial vertex index order, then by the order in which nodes become ready.
  - **`src/ours_mfas.py`** 56–70: `q = deque([i for i in range(n) if indeg[i] == 0])`; `u = q.popleft()`; when `indeg[v] == 0` then `q.append(v)`.

- **DFS cycle detection (Phase A):** Traversal order is **ascending vertex id**: `for s in range(n):` starts DFS from 0, 1, 2, …; within a vertex, outgoing edges are traversed in **edge-list order** (order in `adj_e[u]`, which is built from the fixed (src, dst, w) order). So deterministic for a given A.
  - **`src/ours_mfas.py`** 99–124: iterative DFS over `s in range(n)`; stack `(u, it)` advances through `adj_e[u]` in index order.

- **Determinism comment in code:** **`src/ours_mfas.py`** 179–180: “To keep deterministic behavior, we rebuild adj from alive each iteration.”

- **Under fixed input and time limit, is output deterministic?** **Almost.** The only non-stable sort is in **Phase C (ratio refinement)**: **`src/ours_mfas.py`** 536 and 559: `order = np.argsort(s)` with no `kind=` (numpy default is quicksort, not stable). So when two nodes have the same score, their order in the refinement loop can vary across runs. For Phase A and B and the naive-swap refinement, sorts use `kind="mergesort"` (240, 355). So: **deterministic except possibly in Phase C when there are score ties**; with no ties or if ratio refinement is disabled, output is deterministic for fixed input and time limit.

---

## Summary table

| Topic | Answer | Reference |
|-------|--------|-----------|
| Input type | scipy.sparse (CSR) or dense → CSR | `comparison.py` 389–393, `ours_mfas.py` 573 |
| Loader | `preprocess.load_data` → `load_real_data` or ERO path | `preprocess.py` 32–56, 27–29 |
| Dataset format | `adj.npz` (scipy sparse) for real data | `preprocess.py` 27–29 |
| Weights nonnegative? | Not required; only w>0 used | `ours_mfas.py` 32–33 |
| Both directions? | Yes | — |
| Multiple edges (i,j)? | One edge per nonzero; no aggregation in Phase A/B | `ours_mfas.py` 23–33 |
| A → (src,dst,w) | `_csr_to_edges` | `ours_mfas.py` 23–33 |
| Filter w>0 | Yes | `ours_mfas.py` 32 |
| Normalization before Phase A | No | `ours_mfas.py` 419–422 |
| Return value | (scores, extra_dict) | `comparison.py` 396–426 |
| Final ordering | Topo order of kept DAG → scores; optional refine | `ours_mfas.py` 289–306, 418–438 |
| Weight sort | stable (mergesort) | `ours_mfas.py` 240 |
| Toposort tie-break | Queue order (vertex id) | `ours_mfas.py` 56–70 |
| DFS order | Vertex 0..n-1, edge index order | `ours_mfas.py` 99–124 |
| Deterministic? | Yes except Phase C with score ties (argsort default) | `ours_mfas.py` 536, 559 |
