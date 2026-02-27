# Complexity and Practical Considerations — Audit

Precise time/space costs and implementation details from `src/ours_mfas.py` (and callers) that can be honestly claimed, with file:line references.

---

## 1) Phase A costs

- **Adjacency: built once, static.** **`adj_e`** is built **once** at the start of Phase A: **`adj_e = [[] for _ in range(n)]`** then **`for ei in range(m): adj_e[int(src[ei])].append(int(ei))`** (**174–176**). The comment at **179–180** (“we rebuild adj from alive each iteration”) is **not** implemented: **`adj_e`** is never rebuilt. Dead edges are **skipped** during cycle search by advancing **`it`** while **`not alive[adj_e[u][it]]`** (**113–114** in **`_find_one_cycle_edges`**). So: **O(n + m)** to build **`adj_e`** once; no per-iteration adjacency rebuild.

- **Cost per iteration of `_find_one_cycle_edges`:** DFS over the **current** graph (alive edges only). Each vertex is colored at most once; each **alive** edge is considered at most once (when advancing **`it`**, dead edges are skipped in line **113–114**). So **O(n + m_alive)** per call, where **m_alive** = number of alive edges. In the worst case (all edges alive), **O(n + m)** per iteration.

- **Max number of iterations:** At least **one edge** is removed every iteration (**202–209**): either **`alive[dead] = False`** for edges with residual ≤ zero_tol, or one minimum-residual edge on the cycle is killed. So **maximum iterations ≤ m**. The actual count is stored in **`num_iterations`** (**178**, **191**) and returned; the main entry exposes it as **`meta["phase1_iterations"]`** (**695**).

- **Time gating:** **`if time.time() - t0 > time_limit_sec: break`** at the start of each iteration (**182–184**). So Phase A is **time-bounded** by **`time_limit_sec`** (default 900 from **ours_mfas_rmfa** **576**; 1800s is the **wall** timeout in **train.py** **37**, **169**).

**References:** `src/ours_mfas.py` 170–212, 81–148 (DFS), 113–114, 179–180 (comment vs implementation), 695.

---

## 2) Phase B costs

- **Sort (once):** **`order = np.argsort(-w, kind="mergesort")`** over **m** edges (**240**). **O(m log m)**.

- **Per pass:**  
  - **Toposort:** **`_toposort_kahn_from_edges(n, src, dst, kept)`** (**254**): indeg computation **O(m)** (over kept edges), Kahn **O(n + m)**.  
  - **Scan:** **`for ei in order`** over **m** edges (**265**); per edge **O(1)** (kept check, pos lookup, possible kept update). So **O(m)** per pass.  
  - **Total per pass:** **O(n + m)**.

- **Pass count:** **P = max(1, int(insertion_passes))** with **insertion_passes ∈ {1,2,3}** (**246**). So **P ≤ 3**.

- **Early stop:** Time limit at start of pass (**249–251**); topo failure (**254–257**); **changed == 0** after scan (**279–281**). So Phase B is **time-bounded** and may run fewer than P passes.

**References:** `src/ours_mfas.py` 240, 254, 265–275, 246, 249–251, 254–257, 279–281; 48–75 (Kahn).

---

## 3) Phase C costs

### (a) `_refine_order_naive_swaps`

- **Inner loop:** One **sweep** = **`for i in range(n - 1)`** over **n−1** adjacent pairs (**364**). Per pair: swap in **order**, build **trial_scores** in **O(n)** (**377–380**), then **`_weighted_naive_upset(src, dst, w, trial_scores)`** (**381**).

- **Naive-upset computation:** **`_weighted_naive_upset`** (**313–328**): indexes **scores[src]**, **scores[dst]** over **all m** edges, then **`np.sum(w[mask])`**. So **O(m)** per call. Thus **per sweep: O((n−1) · (n + m)) = O(n² + n·m)**. With **max_passes** sweeps (default 2, **340**), total **O(max_passes · (n² + n·m))** plus time checks.

- **Time budgeting:** Check **`(now - start) > local_budget_sec or (now - t0) > time_limit_sec`** at each of the **n−1** pairs (**366–377**). So refinement is **time-bounded** (local and global).

**References:** `src/ours_mfas.py` 331–396, 313–328, 364, 377–381, 340, 366–377.

### (b) `refine_scores_ratio_ternary`

- **Data from A:** **`_pair_arrays_from_A(A, eps)`** (**527**) builds **I, J, M3** — one entry per **unordered pair (i,j)** with **A_ij + A_ji > 0** (**403–445**). So **length ≤ n(n−1)/2** (e.g. complete directed graph). Construction: **O(m)** to iterate nonzeros and fill a dict; then **O(#pairs)** to build arrays. So **size = O(min(m, n²))** in practice; **worst case O(n²)**.

- **Per-coordinate update:** **`_ternary_opt_one(I, J, M3, s, idx, lo, hi, ternary_iters, eps)`** (**366**): **mask = (I == idx) | (J == idx)** (**472**); **I2, J2, M32** = subarrays for pairs involving **idx** (**476–478**). **ternary_iters** iterations (**491**); each **loss_at(x)** evaluates **ratio_upset_loss_from_pairs(I2, J2, M32, other, eps)** (**485**), which is **O(len(I2))** = O(degree of idx in pair graph). Over all nodes, one pass is **O(n · (avg pairs per node) · ternary_iters)**. Worst case **O(n · n · ternary_iters)** = **O(n² · ternary_iters)** per pass if many pairs.

- **Passes and iters:** **passes** (default 3, **534**); **ternary_iters** (default 25 in function, 20 from caller **575**). Time checks at start of each pass and before each node (**533–539**).

- **Time budgeting:** **`_maybe_refine`** (**663–676**): **budget = min(refine_time_sec, time_limit_sec - elapsed)** (**666–667**); if **budget ≤ 0.05** skip (**668–669**). **refine_scores_ratio_ternary** uses **time_limit_sec** (the budget) and checks **time.time() - tstart** at pass start and per node (**533–539**). So ratio refinement is **time-bounded**.

**References:** `src/ours_mfas.py` 403–445, 518–567, 457–516, 472–485, 491, 533–539, 663–676, 575.

---

## 4) Memory footprint

- **Main arrays (through pipeline):**  
  - **src, dst, w**: length **m** (**22–33** _csr_to_edges).  
  - **residual**: length **m** (**171**).  
  - **alive**: length **m** bool (**173**).  
  - **adj_e**: **n** lists of edge IDs; total **O(m)** references (**174–176**).  
  - **kept** (Phase B): length **m** bool; **order**: length **m** int (**240**).  
  - **Phase C ratio:** **I, J, M3** — length **#unordered pairs** ≤ **n(n−1)/2** (**436–443**).  
  - **pair** dict in **`_pair_arrays_from_A`** (**419–434**): same number of keys; temporary until I, J, M3 are built.

- **Dense A:** **`ours_mfas.py`** does **not** call **A.toarray()**. All use is via **A.tocsr()**, **A.nonzero()**, **A[r,c]** (single-element or fancy indexing returning 1D arrays). So **no n×n dense matrix** inside **ours_mfas.py**.  
  - **Caller:** **comparison.ours_MFAS** (**391–393**): if **W** is not sparse, **`A = sp.csr_matrix(np.asarray(W))`** — so a **dense copy** of **W** is formed when the caller passes a dense matrix. When **A** comes from **load_data** (sparse), no dense A in OURS.

**References:** `src/ours_mfas.py` 22–33, 170–176, 240, 419–443; no `toarray` in ours_mfas.py; `comparison.py` 391–393.

---

## 5) Why Finance is hard under 1800s (code-based)

- **Time limits:** Non-GNN methods (including OURS) use **DEFAULT_METHOD_TIMEOUT = 1800** s in **train.py** (**37**, **169**): the process is **killed** after 1800s. Inside OURS, **time_limit_sec** defaults to **900** (**ours_mfas_rmfa** **576**; **comparison.ours_MFAS** **368**); Phase A, Phase B, and refinements all check **time.time() - t0** against this (**182–184**, **249–251**, **265–266**, **366**, **666**). So OURS has **900s** of “cooperative” time and **1800s** wall before kill.

- **Phase A:** Worst-case **m** iterations; each iteration **O(n + m)** DFS. So **O(m·(n+m))** in the worst case. For Finance, **m** is large (e.g. ~1.7e6 if that’s the dataset size); even with early exit, many iterations and per-iteration DFS over a large graph can consume most of the budget. **phase1_iterations** records how many cycle-peel steps ran (**695**).

- **Phase B:** **O(m log m)** sort once + **P · O(n + m)** per pass with **P ≤ 3**. Scan is over **all m** edges each pass (**265**). So Phase B is **O(m log m + m)** per run; for large **m** this is non-trivial but typically dominated by Phase A if Phase A runs many iterations.

- **Phase C ratio:** **`_pair_arrays_from_A`** builds one entry per unordered pair with non-zero total weight. For a dense-ish or large graph, **#pairs** can be **O(n²)**. Construction and then **n** coordinate updates (each involving a subset of pairs) with **ternary_iters** can be **O(n²)** or more. **refine_time_sec** (default 20) and remaining **time_limit_sec** cap this (**666–669**), but if Phase A and B use almost all 900s, the ratio refinement budget is small; conversely, if ratio runs, building and scanning **O(n²)** pairs on a large **n** (e.g. Finance) can be expensive.

- **Summary:** Finance is hard because: (1) **Phase A** can do up to **m** iterations with **O(n+m)** DFS each → **O(m·(n+m))** worst case, and is only stopped by **time_limit_sec** or when the graph is acyclic; (2) **Phase B** scans **all m** edges for each of up to 3 passes; (3) **Phase C** ratio refinement builds and uses **pair arrays** of size up to **O(n²)** and does **O(n² · ternary_iters)** work per pass in the worst case; (4) all of these are **gated** by **time_limit_sec** (and naive refine by **local_budget_sec** and time_limit), so the algorithm exits early under load rather than completing, but the work per iteration/pass is large for big **n** and **m**.

**References:** `src/train.py` 37, 169; `src/ours_mfas.py` 576, 182–184, 249–251, 265–266, 366, 666–669, 527, 403–445, 534–539; `src/comparison.py` 368.

---

## Summary table

| Phase   | What is rebuilt / scanned | Per-iteration or per-pass cost | Upper bound / count | Time gating |
|---------|---------------------------|--------------------------------|----------------------|-------------|
| A       | adj_e **once**; dead skipped in DFS | O(n + m_alive) DFS | Iters ≤ m; **phase1_iterations** | Start of each iter (**182–184**) |
| B       | Sort **once**; topo **per pass**; scan **all m** edges per pass | O(m log m) + P·O(n+m) | P ≤ 3; early stop | Start of pass, each edge (**249**, **265**) |
| C naive | n−1 adjacent pairs; **full m** edges per upset eval | O((n−1)(n+m)) per sweep; max_passes sweeps | 2 passes default | Per pair (**366–377**) |
| C ratio | **Pair arrays** size O(#pairs) ≤ n(n−1)/2; n coords × ternary_iters | O(n · pairs_per_node · ternary_iters) per pass | passes × n; ternary_iters | Pass start, per node (**533–539**); budget = min(refine_time_sec, remaining) (**666–669**) |

**Memory:** O(n + m) for src, dst, w, residual, alive, adj_e, kept, order; O(#pairs) for I, J, M3 (≤ n²). No A.toarray() in ours_mfas.py; dense W in caller gives dense copy in comparison (**393**).

---

## Paragraph for the paper (practical scaling and Finance)

**Complexity and practical considerations.** Phase A uses a single static adjacency list over all edges; dead edges are skipped during each DFS, so cycle detection is O(n + m_alive) per iteration. At least one edge is removed per iteration, so the number of iterations is at most m and is recorded in meta as phase1_iterations. Phase B does one O(m log m) stable sort and, for each of at most three passes, one Kahn topological sort and one scan over all m edges with O(1) checks. Phase C naive refinement performs O(n) adjacent swaps per sweep, each requiring an O(m) evaluation of weighted naive upset, and is limited by a local time budget and the global time limit. Ratio refinement builds arrays of size equal to the number of unordered pairs with nonzero total weight (at most O(n²)), then performs coordinate-wise ternary search with strict order-preserving bounds; it is time-bounded by min(refine_time_sec, remaining time). All phases respect a single time_limit_sec (default 900s), and the entire run is subject to a 1800s wall timeout for non-GNN methods in the benchmark. On large graphs such as Finance, Phase A’s worst-case O(m·(n+m)) cycle-removal work, Phase B’s full scan over m edges each pass, and Phase C ratio’s O(n²) pair structure and per-node cost can exhaust the time budget, causing OURS to exit early and making Finance the main scalability bottleneck in practice.
