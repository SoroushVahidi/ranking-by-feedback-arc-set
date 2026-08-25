# GNN Runtime Accounting Audit

Date: 2026-08-25  
Branch: `jsuper-final-experimental-gaps-20260825`  
Related evidence: `CLASSICAL_RUNTIME_FINAL.md` @ `981dc221`, `GNNRank-main/src/train.py`, README CUDA notes.

---

## Verdict

**B. EXISTING_EVIDENCE_PARTIAL_BUT_MANUSCRIPT_CAN_QUALIFY**

A full staged GPU timing rerun is **not required** to answer the reviewer
concern if the manuscript qualifies the ~8× claim as:

> end-to-end wall time of **trained** DIGRAC/ib pipelines (training + scoring)
> versus end-to-end OURS/classical CPU methods on common completions.

Existing evidence is sufficient for that qualification; it is **not** sufficient
to claim matched hardware stage-by-stage inference-only fairness without a
controlled rerun.

---

## 1. What existing evidence establishes

### Runtime definition (code-authoritative)

| Method class | Timer location | Includes |
|---|---|---|
| Classical / OURS | `train.py` `non_nn` under `DEFAULT_METHOD_TIMEOUT=1800` | End-to-end method call on loaded graph → ranking scores (no learning) |
| DIGRAC / ib | `train.py` GNN branch: `t_gnn_start = time.time()` around training loop; `GNN_METHOD_TIMEOUT=7200` | **Model construction + training epochs + evaluation/scoring** for GNN variants |

Therefore the published ~8× OURS-faster-than-GNN comparison from
`CLASSICAL_RUNTIME_FINAL.md` / `e1_runtime_wtl.csv` is an **end-to-end trained-GNN
vs combinatorial/spectral** comparison on pairwise common completions
(median ratio ≈ 0.12× ⇒ ~8×), **not** inference-only GNN vs OURS.

### Documented numerical claim (existing)

From runtime-coverage final analysis (`981dc221`):

- OURS vs DIGRAC/ib: **60/60** faster on common completions  
- Median paired ratio ≈ **0.12×** (OURS ~8× faster)  
- Coverage: GNN methods complete on fewer datasets (≈61/79) than OURS/classical  

### Hardware

| Item | Evidence status |
|---|---|
| README CUDA 11.0 / PyTorch GPU env examples | Present (capability, not a run ledger) |
| Exact GPU model/count for the archived GNN result_arrays | **Not recovered** in this audit |
| Exact CPU model for classical/OURS archived runs | **Not recovered** as a single manifest |
| Machine-local ad hoc notes | Partial (revision experiment plan mentions ad hoc CPU timings) |

---

## 2. Accounting checklist

| Question | OURS / classical | DIGRAC / ib |
|---|---|---|
| Preprocessing included? | Yes (within method) | Yes (within train pipeline) |
| Model init included? | N/A / trivial | Yes |
| Training included? | No | **Yes** |
| Validation / model selection? | N/A | Yes (within training loop / variants) |
| Inference / final scoring? | Yes (is the method) | Yes |
| Data loading outside timer? | Typically load before method timer | Same pattern in trainer |
| Timeout | 1800 s wall kill | 7200 s GNN alarm |

---

## 3. Classification rationale

- **Not A (fully sufficient):** missing locked hardware manifest and stage splits
  (train vs infer).  
- **Not C (rerun required):** reviewer concern is primarily “are you comparing
  fair runtimes / what does 8× mean?” — answerable by **qualification** using
  code-grounded accounting plus existing pairwise tables.  
- **B:** qualify manuscript language; optional future controlled timing remains
  nice-to-have, not blocking.

## 4. Decision gate outcome

**NO GNN RERUN in this task.**

If a future controlled timing study is desired, it must be predefined
(stratified 8–12 datasets, stage timers, hardware manifest) before launch.

## 5. Manuscript-safe runtime wording (for later writing; not applied here)

“OURS is approximately 8× faster than DIGRAC/ib on pairwise common completions
when GNN runtimes count full training+evaluation end-to-end and OURS/classical
runtimes count full deterministic method execution. This is not an
inference-only comparison.”
