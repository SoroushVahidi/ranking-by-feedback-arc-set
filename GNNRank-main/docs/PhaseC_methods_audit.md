# Ranking Extraction and Order-Preserving Score Refinement / Phase C — Methods audit

Exact behavior of score extraction from the kept DAG and optional refinements in `src/ours_mfas.py`, with file:line references.

---

## 1) Score extraction from kept edges

- **Function:** **`_scores_from_kept_edges(n, kept, src, dst)`** (**289–306**). Called with `kept_final` to get the main scores (**619**), and with each `kept_mask` in `kept_after_pass` when building pass scores (**639**).

- **Topological order:** Uses **`_toposort_kahn_from_edges(n, src, dst, kept)`** (**294**) — same Kahn implementation as Phase B. Tie-breaking: initial queue = vertices with indeg 0 in **ascending vertex id** (**56** in 48–75); new zeros appended (**70**). If the graph is cyclic, topo returns `None` and the code falls back to **`topo = list(range(n))`** (**295–296**).

- **Score formula:** **`pos[v] = i`** where `topo[i] == v` (**299–301**). Then **`scores = (n - pos).astype(np.float64)`** (**302**): earlier in topo ⇒ smaller `pos` ⇒ larger score. Scores are then clamped: **`scores = np.maximum(scores, 1.0)`** (**304**). So **score[v] = max(1, n - pos[v])** with **larger score = better rank**.

**References:** `src/ours_mfas.py` 289–306, 619, 639; 48–75 (`_toposort_kahn_from_edges`), 56, 70.

---

## 2) Optional refinement steps inside `ours_mfas_rmfa`

### (a) Naive-order refinement

- **Function:** **`_refine_order_naive_swaps`** (**331–396**). Called after initial score extraction (**623–633**) and, when `return_all_pass_scores=True`, on each pass’s scores with a reduced time budget (**641–652**).

- **What it changes:** It modifies the **ordering** (ranking), not raw score magnitudes. It maintains an explicit **order** array (higher score ⇒ earlier in order); scores are derived from that order as **`scores[order] = np.arange(n, 0, -1, dtype=np.float64)`** (**357**, **370–371**, **369–371**, **394**), then clamped **`np.maximum(..., 1.0)`** (**371**, **395**). So it only changes **which** permutation (order) is used; score values are 1..n by rank.

- **Objective:** Minimize **weighted naive upset loss**: sum of weights of edges that go “backwards” in the ordering (i.e. `score[src] <= score[dst]`). **`_weighted_naive_upset(src, dst, w, scores)`** (**313–328**, **360**, **381**): `mask = si <= sj`, return `np.sum(w[mask])`.

- **Method:** Local search: left-to-right over **adjacent pairs** in the current order; try swapping the two; accept swap iff **`loss_new + 1e-12 < best_loss`** (**382**). **`max_passes`** sweeps (**372**); stops early if no improvement in a pass (**390–391**).

- **Constraints / time budget:** **`local_budget_sec`** (default 2.0) and **global `time_limit_sec`**: at each pair check **`(now - start) > local_budget_sec or (now - t0) > time_limit_sec`** (**368–377**); if exceeded, return current best scores. **`max_passes`** (default 2) caps sweeps (**340**, **372**).

- **Determinism:** **`order = np.argsort(-s, kind="mergesort")`** (**356**) — stable. Sweep order and swap acceptance are deterministic.

**References:** `src/ours_mfas.py` 331–396, 313–328, 621–633, 636–652.

### (b) Ratio refinement (ternary search)

- **Function:** **`refine_scores_ratio_ternary(A, scores, passes, ternary_iters, time_limit_sec, eps)`** (**518–567**). Invoked via **`_maybe_refine(s_in)`** (**663–676**) which gates on `refine_ratio` and time budget.

- **Objective:** Minimize **ratio upset loss** (mean squared error between target pairwise ratio and score-derived ratio). **`ratio_upset_loss_from_pairs(I, J, M3, s, eps)`** (**448–454**): for pairs (I[k], J[k]), target is M3[k] = (A_ij - A_ji)/(A_ij + A_ji + eps); predicted is T = (s[i]-s[j])/(s[i]+s[j]+eps); loss = **mean((M3 - T)^2)**. I, J, M3 come from **`_pair_arrays_from_A(A, eps)`** (**403–445**, **527**): one entry per unordered pair with A_ij + A_ji > 0.

- **Order preservation:** Nodes are processed in **ascending score order** (**536**). For each node `idx`, the new score is constrained to **`[lo, hi]`** so the ordering does not change: **`lo = s[order[k-1]] + margin`**, **`hi = s[order[k+1]] - margin`** (with boundary cases at k==0 and k==len-1); **`margin = 1e-6`** (**532**, **544–552**). So **score[idx]** is optimized inside the interval between predecessor and successor in the current order. After each coordinate update, a **monotone repair** (**568–572**) ensures **`s[b] > s[a]`** for consecutive nodes (set `s[b] = s[a] + margin` if violated).

- **Method:** Outer **`passes`** (default 3); inner loop over nodes in **ascending score order**; for each node **`_ternary_opt_one(I, J, M3, s, idx, lo, hi, ternary_iters, eps)`** (**366**) — ternary search over `s[idx]` in [lo, hi] to minimize ratio upset over pairs involving `idx` (**457–516**). **`ternary_iters`** (default 25 in the function; 20 from caller) caps ternary steps (**491**).

- **Time budgeting:** **`_maybe_refine`** (**663–676**): **`remaining = time_limit_sec - (time.time() - t0)`**; **`budget = min(refine_time_sec, remaining)`**; if **budget <= 0.05** return unchanged (**667–669**). So ratio refinement uses at most **`refine_time_sec`** and never exceeds the **global time limit**. **`refine_scores_ratio_ternary`** checks **`time.time() - tstart > time_limit_sec`** at the start of each pass and before each node (**534–535**, **538–539**).

**References:** `src/ours_mfas.py` 518–567, 403–445, 448–454, 457–516, 663–676, 532, 544–552, 568–572.

---

## 3) What is returned

- **When `return_all_pass_scores=True`:**  
  - **`pass_scores`** are scores **after each add-back pass**: for each **`kept_mask`** in **`kept_after_pass`**, we compute **`_scores_from_kept_edges(n, kept_mask, src, dst)`**, then apply **naive refinement** (if enabled) with **`local_budget_sec = max(naive_refine_time_sec * 0.5, 0.1)`** (**637–652**). These **pass_scores** do **not** include ratio refinement yet.  
  - Then **ratio refinement** is applied to **each** entry of **`pass_scores`** via **`_maybe_refine(s)`** (**679**). So **`pass_scores`** returned to the user are: [scores after pass 1 DAG + naive refine + ratio refine], [after pass 2 + naive + ratio], …  
  - **`scores_final`** is set to **`pass_scores[insertion_passes - 1]`** (or the last available if fewer passes) (**681**). So the “final” vector is the **last pass’s scores after both refinements**, not a separate refinement of the final DAG only.

- **When `return_all_pass_scores=False`:**  
  - Single path: **`_scores_from_kept_edges(kept_final)`** → optional naive refine → **`_maybe_refine(scores_final)`** (ratio) → **`scores_final`** (**619–683**).

- **Meta fields related to Phase C:**  
  - **`time_phaseC_sec`**: **`t_after_phaseC - t_after_phase2`** — wall time for everything after Phase B (score extraction + naive refine + ratio refine, and when applicable pass_scores construction and refinement) (**708**).  
  - **`refine_ratio`**: boolean, whether ratio refinement was requested (**704**).  
  - There is no separate meta for “refine_naive” or naive-refine time; Phase C time is one block.

**References:** `src/ours_mfas.py` 635–683, 698–709, 677–682.

---

## 4) Determinism caveats

- **`_scores_from_kept_edges`:** Uses same Kahn as Phase B (deterministic queue). **`pos`** and **`scores = n - pos`** are deterministic for a given `kept`.

- **Naive refinement:** **`np.argsort(-s, kind="mergesort")`** (**356**) — **stable**. No non-determinism.

- **Ratio refinement:** **`order = np.argsort(s)`** (**536**, **559**) — **no `kind=`** argument, so NumPy default (**quicksort**) is used. **Quicksort is not stable**, so when there are **score ties**, the order of nodes with the same score can vary between runs. That affects: (1) the order in which coordinates are updated in the inner loop (**538**); (2) the **`lo`/`hi`** bounds (neighbor in order); (3) the result of **monotone repair** (**568–572**). So **Phase C can be non-deterministic when scores tie**; the rest of the pipeline (Phase A, B, score extraction, naive refine) is deterministic.

**References:** `src/ours_mfas.py` 536, 559; NumPy `np.argsort` default.

---

## Summary table

| Item | Implementation | Reference |
|------|----------------|-----------|
| Score-from-DAG | `_scores_from_kept_edges(n, kept, src, dst)` | 289–306, 619, 639 |
| Topo | `_toposort_kahn_from_edges` (Kahn); fallback `list(range(n))` if None | 294–296, 48–75 |
| Score formula | `pos[v]=i` from topo; `scores = (n - pos)`; `max(scores, 1)` | 299–304 |
| Naive refine | `_refine_order_naive_swaps`; order-only; minimize weighted naive upset; adjacent swaps; local_budget_sec + global limit; max_passes | 331–396, 621–633 |
| Ratio refine | `refine_scores_ratio_ternary`; minimize mean (M3-T)^2; lo/hi = neighbor bounds + margin 1e-6; passes × nodes; ternary_iters; budget = min(refine_time_sec, remaining) | 518–567, 663–676 |
| pass_scores | After each add-back pass: topo scores + naive refine; then _maybe_refine (ratio) applied to each | 636–652, 679–681 |
| scores_final when pass_scores | Last pass’s scores after both refinements | 681 |
| Meta Phase C | time_phaseC_sec, refine_ratio | 704, 708 |
| Determinism | Naive: mergesort. Ratio: np.argsort(s) default (quicksort) ⇒ non-deterministic when scores tie | 356, 536, 559 |
