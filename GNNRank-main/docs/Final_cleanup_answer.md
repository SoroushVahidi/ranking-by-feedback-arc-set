# Final cleanup + sanity checks for experiments artifacts

**Goal:** Eliminate remaining “missing runtime” holes and add automated consistency checks so artifacts can’t regress.

---

## 1) Missing runtime (upset_simple present): investigation and root cause

### Affected cases (from `docs/Targeted_reruns_plan.md`)

| dataset | methods |
|---------|---------|
| **Halo2BetaData** | SVD_NRS, SVD_RS, SpringRank |
| **_AUTO/Basketball_temporal__1985adj** | SpringRank |

(Note: the plan uses `_AUTO/Basketball_temporal__1985adj`; the dataset key may appear as `Basketball_temporal1985adj` in some contexts — same logical dataset.)

### Root cause (not a parsing or naming bug)

- **Runtime is absent in the result_arrays scan** for those dataset keys. The aggregator (`build_results_table_from_result_arrays.py`) correctly sets `runtime_sec_mean = np.nan` when no runtime file/dir exists; it is not NaN inside the arrays or a method/config key mismatch.
- **Halo2BetaData:** Under `result_arrays/Halo2BetaData/` there is **upset/** (SpringRank, SVD_NRS, SVD_RS) but **no runtime/**. Runtime exists only under `result_arrays/Halo2BetaData/HeadToHead/`. So for the key `"Halo2BetaData"` there is no runtime data to read.
- **_AUTO/Basketball_temporal__1985adj:** There is **upset/** for SpringRank but **no runtime/** (or no matching .npy) for that dataset dir; runtime was never written for this key.

**Summary:** Runtime was never saved under those dataset paths. Fix options: (1) backfill from alias datasets in the pipeline, (2) re-run the affected (dataset, method) so runtime is written.

**Detailed notes:** `docs/Missing_runtime_root_cause.md`

---

## 2) Validator script

**Script:** `tools/validate_paper_artifacts.py`  
**Exit:** Nonzero if any check fails.

| Check | Description |
|-------|-------------|
| **Missing runtime** | Fails if any method has upset_simple but runtime_sec missing for >0 datasets, unless (dataset, method) or method is whitelisted (e.g. finance timeouts, composite methods). |
| **Coverage mismatch** | Fails if any dataset is silently dropped: per-method table (table1) coverage total ≠ raw leaderboard unique dataset count. |
| **Oracle guardrail** | Table1/table2 must be built from per-method CSVs only; fails if tables look oracle-only (e.g. only best_* columns, no method-level columns). |
| **Determinism** | Deterministic methods must not report std>0 for single-run rows unless explained by timeouts/missingness; fails if such rows exist in `results_from_result_arrays.csv` (or leaderboard). |

**Report:** `docs/Artifact_validation_report.md` (overwritten each run).

---

## 3) End-to-end runner

**Script:** `tools/build_all_paper_artifacts.sh`

**Order:**

1. `build_leaderboard_csvs.py`
2. `validate_paper_artifacts.py`
3. `build_paper_tables.py`
4. `build_paper_figs.py`
5. `validate_paper_artifacts.py` again (post-artifacts)

**Properties:** Idempotent; prints output paths at the end.

**Run from repo root:** `bash tools/build_all_paper_artifacts.sh`

---

## 4) Finding and filling missing data: workflow

**For the missing runtime cases, use this order:**

1. **Search the directory first**  
   Run:
   ```bash
   python tools/check_missing_runtime_in_result_arrays.py
   ```
   This scans `result_arrays/` for the four (dataset, method) pairs and reports for each: upset present?, runtime present?. Exit 0 = all have both; exit 1 = at least one has upset but no runtime.

2. **If still missing after 841303**  
   Job **841303** runs `run_final_all.sbatch` (full grid over datasets/methods). If you rely on it:
   - Wait for 841303 to finish.
   - Run the check again: `python tools/check_missing_runtime_in_result_arrays.py`.
   - If it now exits 0, rebuild artifacts: `bash tools/build_all_paper_artifacts.sh`.

3. **If 841303 does not fill them (or you don’t run 841303)**  
   Run the **targeted** script to re-run only the four (dataset, method) pairs so that runtime is written:
   ```bash
   bash tools/run_targeted_missing_runtime.sh
   ```
   Then re-run the check and, if clean, `bash tools/build_all_paper_artifacts.sh`.

**Summary:** Search result_arrays first → if missing, (optionally) wait for 841303 and re-check → if still missing, run `run_targeted_missing_runtime.sh` (or a batch job that runs it).

---

## 5) Deliverables checklist

| Deliverable | Location |
|-------------|----------|
| Root-cause notes (where runtime goes missing and why) | `docs/Missing_runtime_root_cause.md` |
| Pipeline backfill (no re-run required for consistent leaderboard) | `tools/build_leaderboard_csvs.py` (`DATASET_RUNTIME_ALIASES`, `_backfill_runtime_from_aliases`) |
| Validator | `tools/validate_paper_artifacts.py` |
| Validation report | `docs/Artifact_validation_report.md` |
| End-to-end runner | `tools/build_all_paper_artifacts.sh` |
| Search result_arrays for missing runtime | `tools/check_missing_runtime_in_result_arrays.py` |
| Targeted run if 841303 doesn’t fill gaps | `tools/run_targeted_missing_runtime.sh` |

---

## 6) Quick reference commands

```bash
# Check if result_arrays has both upset and runtime for the four target pairs
python tools/check_missing_runtime_in_result_arrays.py

# If still missing after 841303 (or instead of 841303): run only those four (dataset, method)
bash tools/run_targeted_missing_runtime.sh

# Rebuild and validate all paper artifacts (idempotent)
bash tools/build_all_paper_artifacts.sh
```
