# Phase 1: Local-Ratio Cycle Breaking / Acyclic Backbone — Methods audit

Exact algorithmic steps and guarantees implemented in Phase A of OURS, with `src/ours_mfas.py` file:line references.

---

## 1) State maintained in Phase A

- **Residual weights:** `residual` — length-*m* float array; initialized as `w.copy()` and updated each cycle step (**171–172**).
- **Alive/kept mask:** `alive` — length-*m* boolean array; `alive[ei]` True iff edge *ei* is still in the graph. Initialized to all True (**173**). Edges are “killed” by setting `alive[ei] = False` and `residual[ei] = 0` (**203–204**, **207–208**).
- **Adjacency structure:** `adj_e` — list of lists of **edge IDs**: `adj_e[u] = [eid1, eid2, ...]` for edges with `src[eid]=u`. Built **once** at the start from all *m* edges (**174–177**). Dead edges are not removed from `adj_e`; the cycle finder skips them by checking `alive[adj_e[u][it]]` (**113–114**).  
  - Comment at **179–180**: “To keep deterministic behavior, we rebuild adj from alive each iteration” — in the current code, `adj_e` is **not** rebuilt; only the **cycle search** ignores dead edges via the `alive` check. So “rebuild” here means “effective graph is defined by alive mask.”
- **Other:** `num_iterations` — count of cycle-peel steps (**178**, **191**).  
  Returned “kept” is `alive`; “removed” is `~alive` (**211–212**).

**References:** `src/ours_mfas.py` 152–212 (`_local_ratio_break_cycles`).

---

## 2) How a directed cycle is found (DFS)

- **Routine:** `_find_one_cycle_edges` (**81–148**). Returns a list of **edge IDs** forming one directed cycle, or `None` if the current (alive) graph is acyclic.

- **Colors:** WHITE=0, GRAY=1, BLACK=2; `color[u]` per vertex (**93–94**).  
  WHITE = unvisited, GRAY = on stack (current DFS path), BLACK = finished.

- **Parent pointers:**  
  - `parent_v[u]` = predecessor vertex in the DFS tree (**96**).  
  - `parent_e[u]` = edge ID from `parent_v[u]` to `u` (**97**).  
  Set when extending the DFS: when moving from *u* to *v* (edge *ei*), `parent_v[v] = u`, `parent_e[v] = ei` (**126–127**).

- **DFS:** Iterative (stack of `(vertex, next edge index)`). Roots in ascending vertex order: `for s in range(n)` (**99–100**). For each vertex, only **alive** outgoing edges are followed (**113–114**). When a neighbor *v* is GRAY, a back edge is detected: the edge *ei* (u→v) closes a cycle (**129–131**).

- **Cycle reconstruction:** Back edge *ei* (u→v) is the first cycle edge (**133**). Then walk back via `parent_e` and `parent_v` from *u* until reaching *v*; collect those edge IDs (**134–143**). Reverse the list so the cycle is in traversal order v…u then u→v (**144**). Return that list of edge IDs (**145**). If parent chain is broken (`parent_e[cur]==-1`), return `None` (**137–139**, **143**).

**References:** `src/ours_mfas.py` 81–148 (`_find_one_cycle_edges`).

---

## 3) Update when a cycle is found

- **Δ (delta):** Minimum residual on the cycle edges.  
  **`delta = float(np.min(residual[cyc_e]))`** (**193**).

- **Residual update:**  
  - If **delta > 0:** subtract Δ from every edge on the cycle: **`residual[cyc_e] -= delta`** (**199**).  
  - If **delta ≤ 0:** no subtraction; “numerical guard” branch runs (**194–197**).

- **Which edges are removed:** Any edge with **`residual[ei] <= zero_tol`** and currently alive is marked dead: **`dead = (residual <= zero_tol) & alive`**, then **`alive[dead] = False`** (**202–204**).

- **zero_tol:** Parameter of `_local_ratio_break_cycles`, default **`1e-15`** (**166**). Not overridable from the public API (no argument passed from `ours_mfas_rmfa` at **598–602**).

- **Forced progress when no edge hits zero:** If after the update **no** edge in the cycle has residual ≤ `zero_tol` (**`else`** at **206–209**), then: pick one edge on the cycle with **minimum residual** (**206**, **206**): `ei_min = cyc_e[int(np.argmin(residual[cyc_e]))]`, set **`alive[ei_min] = False`** and **`residual[ei_min] = 0.0`**. So at least one edge is removed every iteration. The same “kill minimum on cycle” rule is used in the **delta ≤ 0** branch (**195–197**): set that edge’s residual to 0 and (implicitly) it will be killed in the next `dead` check unless `zero_tol` is negative (it is not).

**References:** `src/ours_mfas.py` 192–210, 166.

---

## 4) Stopping condition

- **Primary:** Exit when **no directed cycle** exists in the current (alive) graph: **`cyc_e = _find_one_cycle_edges(...)`** returns **`None`** → **`break`** (**186–188**).

- **Time limit:** At the start of each iteration, **`if time.time() - t0 > time_limit_sec: break`** (**183–184**). So Phase A can stop with the graph still cyclic if the time limit is hit.

- **Result:** When the loop exits, the remaining graph (edges with `alive`) is **acyclic** only if the exit was due to “no cycle found.” If exit was due to time limit, the state may still contain cycles.

**References:** `src/ours_mfas.py` 183–188.

---

## 5) Outputs / meta fields recording Phase A work

- **Return value of `_local_ratio_break_cycles`** (**165**, **211–212**):  
  - `alive` (kept mask),  
  - `removed` (= ~alive),  
  - `residual` (final residual weights for all edges),  
  - `num_iterations`.

- **Main entry** (`ours_mfas_rmfa`) stores Phase A results in **`meta`** when `return_meta=True` (**704–708**, **707**):  
  - **`phase1_iterations`**: number of cycle-peel steps (**706**).  
  - **`removed_phaseA`**: number of edges removed in Phase A, **`R = int(np.sum(~keptA))`** (**704**, **707**).  
  - **`kept_after_phaseA`**: number of edges kept after Phase A, **`int(np.sum(keptA))`** (**708**).  
  - **`time_phase1_sec`**: wall time for Phase A, **`t_after_phase1 - t0`** (**708**).

- **Not stored in meta:** `residual` array, the actual `keptA` mask (only its sum and the count of removed edges), and `zero_tol`. The full `kept_final_mask` in meta is from **Phase B** (final DAG), not Phase A (**712**).

**References:** `src/ours_mfas.py` 165, 211–212, 598–602, 704–712.

---

## 6) Demetrescu–Finocchi / local-ratio heuristic / λ-approximation

- **In-code references:** There are **no** mentions of “Demetrescu,” “Finocchi,” “λ”, or “approximation” (or “approximation guarantee”) in **`src/ours_mfas.py`** or elsewhere in the repo for this routine.

- **Docstring:** Phase A is described as **“Local-ratio style”** (**163–166**):  
  - maintain residual weights *r*;  
  - while a cycle exists: subtract the **min** residual on the cycle from all edges in that cycle;  
  - remove edges whose residual hits 0.  

- **Implementation vs classic local-ratio:** The steps match the usual “find cycle → subtract min on cycle → drop zero edges” local-ratio heuristic. The code does **not** state or implement a specific λ-approximation guarantee; it implements the heuristic plus numerical safeguards (delta ≤ 0 branch and forced progress when no edge ≤ `zero_tol`).

**References:** `src/ours_mfas.py` 1–7 (header), 152–171 (docstring and signature); grep over repo for “Demetrescu|Finocchi|local-ratio|lambda|approximation” yields no hits in `ours_mfas.py`.

---

## Summary table

| Item | Implementation | Reference |
|------|----------------|-----------|
| Residual array | `residual = w.copy()`; updated by subtracting Δ on cycle | 171–172, 199 |
| Alive mask | `alive`, length *m* bool; kill with `alive[ei]=False`, `residual[ei]=0` | 173, 203–204, 207–208 |
| Adjacency | `adj_e[u]` = list of edge IDs with src=*u*; built once; dead skipped via `alive` in DFS | 174–177, 113–114 |
| Cycle finding | DFS with WHITE/GRAY/BLACK; `parent_v`, `parent_e`; back edge → walk parents to get cycle edge IDs | 93–97, 99–148 |
| Δ | `delta = np.min(residual[cyc_e])` | 193 |
| Residual update | `residual[cyc_e] -= delta` (if delta > 0) | 199 |
| Removal rule | `residual <= zero_tol` → dead; else kill min-residual edge on cycle | 202–209 |
| zero_tol | Default `1e-15` | 166 |
| Stopping | No cycle found **or** time limit exceeded | 183–188 |
| Meta Phase A | `phase1_iterations`, `removed_phaseA`, `kept_after_phaseA`, `time_phase1_sec` | 704–708 |
| Guarantee / citation | None; “Local-ratio style” only; no Demetrescu–Finocchi or λ-approx in repo | 163–166, repo grep |
