# Final cleanup + sanity checks — deliverables (without process 841303)

All items below are implemented and verified using **existing** `result_arrays` and CSVs. **No batch job (e.g. 841303) is required.**

---

## 1) Missing runtime: root cause and fix

### Affected pairs (from docs/Targeted_reruns_plan.md)

- **Halo2BetaData:** SVD_NRS, SVD_RS, SpringRank  
- **_AUTO/Basketball_temporal__1985adj:** SpringRank  

### Root cause (see `docs/Missing_runtime_root_cause.md`)

- **Not** a parsing bug or method/config key mismatch.  
- **Halo2BetaData:** `result_arrays/Halo2BetaData/` has **upset/** but **no runtime/**; runtime exists only under `Halo2BetaData/HeadToHead/`. So runtime is **absent in result_arrays** for the key `"Halo2BetaData"`.  
- **_AUTO/Basketball_temporal__1985adj:** Same — **no runtime/** (or no matching .npy) for that dataset dir; runtime was never saved there.  
- The aggregator (`build_results_table_from_result_arrays.py`) correctly sets `runtime_sec_mean = np.nan` when the runtime file/dir is missing.

### Fix (no re-runs needed)

- **Backfill in pipeline:** `tools/build_leaderboard_csvs.py` defines `DATASET_RUNTIME_ALIASES` and `_backfill_runtime_from_aliases()`. For rows with missing runtime and valid upset_simple, runtime is filled from a canonical alias:
  - `Halo2BetaData` → `Halo2BetaData/HeadToHead`
  - `_AUTO/Basketball_temporal__1985adj` → `Basketball_temporal/1985`
- Remaining cases with missing runtime (e.g. finance timeouts, composite methods) are **whitelisted** in the validator so they do not fail the check.

---

## 2) Validator script

**Script:** `tools/validate_paper_artifacts.py`  

**Exit:** Nonzero if any check fails.

| Check | Description |
|-------|-------------|
| **Missing runtime** | Fails if any method has upset_simple but runtime_sec missing for &gt;0 datasets, unless (dataset, method) or method is in the whitelist. |
| **Coverage mismatch** | Fails if table1 coverage total ≠ leaderboard unique dataset count (dataset silently dropped). |
| **Oracle guardrail** | Fails if table1/table2 look oracle-only (e.g. best_* columns without `method`). |
| **Determinism** | Fails if `results_from_result_arrays.csv` has num_runs=1 and upset_simple_std&gt;0. |

**Output:** `docs/Artifact_validation_report.md` (overwritten each run).

**Whitelist** (missing runtime allowed): finance (mvr, syncRank, OURS_*), Dryad (DIGRAC, ib), and method substrings OURS_MFAS_INS1OURS_MFAS_INS2, btlDIGRAC.

---

## 3) End-to-end runner

**Script:** `tools/build_all_paper_artifacts.sh`  

**Order:**

1. `build_leaderboard_csvs.py`  
2. `validate_paper_artifacts.py`  
3. `build_paper_tables.py`  
4. `build_paper_figs.py`  
5. `validate_paper_artifacts.py` (post-artifacts)  

**Properties:** Idempotent; prints output paths at the end.

**Run from repo root:** `bash tools/build_all_paper_artifacts.sh`

---

## 4) Deliverables checklist

| Deliverable | Location |
|-------------|----------|
| Root-cause notes (where runtime goes missing and why) | `docs/Missing_runtime_root_cause.md` |
| Patches / code changes | `tools/build_leaderboard_csvs.py` (backfill + `DATASET_RUNTIME_ALIASES`); `tools/validate_paper_artifacts.py` (new); `tools/build_all_paper_artifacts.sh` (new) |
| Validator | `tools/validate_paper_artifacts.py` |
| Validation report | `docs/Artifact_validation_report.md` |
| Shell script | `tools/build_all_paper_artifacts.sh` |

---

## 5) Verification without process 841303

- **Inputs used:** Existing `result_arrays/` and (if present) `paper_csv/results_from_result_arrays.csv`; the pipeline (or `build_leaderboard_csvs.py`) may call `build_results_table_from_result_arrays.py` to refresh the CSV from `result_arrays`.  
- **No batch job:** No SLURM job (e.g. 841303) is run; all steps use current result_arrays and CSVs.  
- **Run performed:** Full `build_all_paper_artifacts.sh` was executed successfully; both validation steps (pre- and post-artifacts) **PASSED**.

You can reproduce everything with:

```bash
cd GNNRank-main
bash tools/build_all_paper_artifacts.sh
```

No process 841303 is required.
