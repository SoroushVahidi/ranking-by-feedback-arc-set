# Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction

**Journal of Supercomputing — Accepted (2026), sole-authored**

This repository contains the implementation, experiments, and manuscript materials for a training-free, deterministic ranking pipeline that builds an acyclic backbone from directed pairwise comparisons using a minimum weighted feedback arc set (MWFAS) inspired local-ratio heuristic, restores high-weight arcs via exact reachability-aware cycle-safe reinsertion, and optionally applies refinement.

---

## Start Here

**For reviewers**, these are the most important entries:

| # | Item | Path |
|---|------|------|
| 1 | **Final manuscript (LaTeX + PDF)** | `manuscript/revision_20260825/source/main_ik.tex` / `.pdf` |
| 2 | **Springer editable LaTeX ZIP** | `manuscript/Journal_of_Supercomputing_revised_manuscript_LaTeX.zip` |
| 3 | **Response to reviewers** | `manuscript/revision_20260825/response_to_reviewers.tex` / `.pdf` |
| 4 | **Cover letter** | `manuscript/revision_20260825/cover_letter_revision.tex` / `.pdf` |
| 5 | **Final submission package** | `manuscript/final_submission_package/` |
| 6 | **Canonical method implementation** | `GNNRank-main/src/ours_mfas.py` (entry: `addback_mode="reach"`) |
| 7 | **Main experiment script** | `GNNRank-main/src/train.py` |
| 8 | **Canonical experiment outputs (Tables 4–8)** | `outputs/paper_tables/` |
| 9 | **Revision analysis outputs** | `outputs/revision_analysis_20260825/` |
| 10 | **Structural ablation outputs (Tables 7–8)** | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/` |
| 11 | **Figure generation** | `GNNRank-main/scripts/paper/` and `scripts/paper/` |
| 12 | **Figure PDFs** | `manuscript/revision_20260825/figures/` and `GNNRank-main/paper_figs/` |
| 13 | **RankCentrality correction** | `outputs/revision_analysis_20260825/rankcentrality_correction_20260825/` |
| 14 | **Runtime provenance audit** | `docs/journal_supercomputing_revision_20260825/RUNTIME_PROVENANCE_AUDIT.md` |
| 15 | **Reproducibility / full build** | `GNNRank-main/README.md` + `GNNRank-main/scripts/paper/run_all_paper_artifacts.py` |
| 16 | **Reproducibility guide** | `REPRODUCIBILITY.md` — quick verification, artifact regeneration, raw experiments |

---

## Canonical Method

**OURS-Reach** (Phase~A + Phase~B exact reachability + Phase~C refinement)

| Component | Description |
|-----------|-------------|
| **Phase A** | Local-ratio cycle breaking (prior: Demetrescu--Finocchi) |
| **Phase B** | Exact reachability-aware add-back (fidelity restoration) |
| **Phase C** | Adjacent-swap + order-preserving ternary refinement (prior lineage) |

**Implementation entry points:**
- `GNNRank-main/src/ours_mfas.py` — `addback_mode="reach"` (Phase~B), `enable_phase_b=True`, `enable_phase_c=True`
- `GNNRank-main/scripts/revision_analysis_20260825/run_reviewer_ablation.py` — A4 configuration (OURS-Reach)

**Legacy variants retained for ablation/history:**
- `OURS_MFAS_INS1` / `INS2` / `INS3` — fixed-topological-position proxy add-back. These are ablation-only. They are **not** the canonical revised method.

**Optional secondary repair:**
- Weighted min-cut exchange (Proposition 3) — excluded from headline Tables 4–6. Appears in Tables 7–8 as structural FAS-weight evidence.

---

## What Prior vs. What Is New

| **Prior / Lineage** | **This Revision** |
|---------------------|-------------------|
| Local-ratio cycle breaking (Demetrescu--Finocchi, 2003) | Formal ranking--MWFAS equivalence and guarantee boundaries (Proposition 1, Proposition 4) |
| Exact cycle-safe reinsertion concept | Implementation-fidelity restoration: exact reachability replaces fixed-topological proxy |
| Weight-prioritized add-back | Secondary weighted min-cut exchange (Proposition 3) |
| Ternary refinement lineage | Expanded classical + GNN evaluation, family-aware statistics, structural ablation, runtime provenance |

The method is **not** a new general MWFAS approximation algorithm. It is a training-free deterministic pipeline that applies established components with precise theoretical grounding and extensive empirical validation.

---

## Reproduce the Paper — Artifact Map

| Paper Artifact | Source Path |
|----------------|-------------|
| **Table 4** (`upset_simple`) | `outputs/paper_tables/table4_full_suite.csv` |
| **Table 5** (`upset_ratio`) | `outputs/paper_tables/table5_compute_matched.csv` |
| **Table 6** (runtime W/T/L) | `outputs/revision_analysis_20260825/canonical_reachability_baseline_comparison/e1_runtime_wtl.csv` |
| **Table 7** (ablation primary tests) | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/primary_pairwise_statistics.csv` |
| **Table 8** (stage ablation) | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation_summary.csv` |
| **Figure 1** (runtime vs. edges) | Generated from `outputs/paper_tables/`; script: `scripts/paper/generate_paper_tables.py` |
| **Figure 2** (structural ablation) | Generated from `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv`; script: `GNNRank-main/scripts/paper/run_phase_ablation.py` |
| **Figure 2 raw data** | `outputs/revision_analysis_20260825/reviewer_ablation_scalability/structural_ablation.csv` |
| **Family-aware analysis** | `outputs/revision_analysis_20260825/family_aware_baselines/` |
| **Runtime provenance** | `outputs/revision_analysis_20260825/canonical_reachability_baseline_comparison/e1_runtime_wtl.csv` |

**Full artifact rebuild:**

```bash
cd GNNRank-main/scripts/paper
python run_all_paper_artifacts.py
```

Outputs go to `GNNRank-main/outputs/paper_tables/` and `GNNRank-main/outputs/audits/`.

---

## Revision Notes / Important Corrections

1. **Exact reachability add-back** replaced the earlier fixed-topological-position proxy (legacy INS1–3). The canonical method (OURS-Reach) uses `addback_mode="reach"` in `ours_mfas.py`.
2. **Headline method is OURS-Reach** (Phase~A + exact reachability + Phase~C refinement), **not** legacy INS variants.
3. **RankCentrality bug correction**: an inherited implementation bug (transition matrix overwritten before eigenvector step) was corrected to the Negahban--Oh--Shah construction. Only that baseline was recomputed. See `outputs/revision_analysis_20260825/rankcentrality_correction_20260825/`.
4. **Runtime definition**: manuscript-facing runtime is the single-invocation algorithm runtime (Phase~A + Phase~B + Phase~C), not harness diagnostic wall time.
5. **Dataset denominator**: 80 intended suite members; 2 adjacency files unavailable. Loadable analyses use **78** graphs. Finance is the large-dense boundary (OURS-Reach: 77/78 due to timeout).
6. **Matched support**: Figure 2 and Table 8 use matched dataset support to avoid conflating stage effects with dataset composition differences.
7. **Optional min-cut** is a secondary structural repair (monotone FAS-weight improvement). It is excluded from headline Tables 4–6.

---

## Repository Structure

```
.
├── README.md                  # This file — reviewer navigation
├── manuscript/                # Manuscript, response letter, cover letter, submission packages
│   ├── revision_20260825/     # Authoritative revision source (tex, figures, response, cover)
│   ├── final_submission_package/  # Final packaged documents for Journal of Supercomputing
│   ├── springer_revised_manuscript_upload/  # Springer LaTeX source ZIP (editable)
│   ├── Journal_of_Supercomputing_revised_manuscript_LaTeX.zip  # Upload ZIP
│   └── submitted_original/    # Immutable original submission (do not modify)
├── GNNRank-main/              # Core: method implementation, baselines, pipelines
│   ├── src/                   # Implementation: ours_mfas.py, train.py, baselines
│   ├── scripts/paper/         # Paper artifact rebuild scripts
│   ├── scripts/revision_analysis_20260825/  # Revision-specific experiments
│   ├── tools/                 # Pipeline utilities (leaderboards, validation)
│   ├── paper_csv/             # Leaderboard CSVs, unified comparisons
│   ├── paper_figs/            # Generated figure PDFs
│   ├── outputs/               # Experiment outputs
│   ├── data/                  # Datasets (partial; not all pushed to GitHub)
│   └── result_arrays/         # Saved metrics per (dataset, method, config)
├── outputs/                   # Root-level revision outputs (canonical tables, audits)
│   ├── paper_tables/          # Final manuscript-facing tables (Tables 4--8)
│   ├── audits/                # Validation and consistency audits
│   └── revision_analysis_20260825/  # Full revision experiment outputs
├── scripts/paper/             # Paper table generation scripts
├── docs/                      # Revision audits, provenance, novelty checks
│   ├── journal_supercomputing_revision_20260824/
│   └── journal_supercomputing_revision_20260825/
├── tests/                     # Targeted correctness tests (ablation, add-back, etc.)
├── github_readmes/            # Auto-sync READMEs for other repos
└── LICENSE
```

**Note on `GNNRank-main/`:** This directory extends the [GNNRank](https://github.com/SherylHYX/GNNRank) codebase with our method and evaluation pipeline. The original GNNRank repository and its baselines (DIGRAC, ib) are included here. See `GNNRank-main/README.md` for detailed run options.

---

## Legacy Files — What to Ignore

The following items are retained for research history and ablation but are **not** the final canonical method:

| Item | Status |
|------|--------|
| `OURS_MFAS_INS1` / `INS2` / `INS3` | Fixed-topological proxy add-back. Ablation/historical only. |
| `paper_tables/` in `GNNRank-main/` | Legacy historical exports. Not authoritative. |
| `outputs/revision_analysis_20260824/` | Pre-final revision analysis. Use `20260825/` series. |
| `docs/journal_supercomputing_revision_20260824/` | Pre-final revision audit materials. |

Use `outputs/paper_tables/` and `outputs/revision_analysis_20260825/` as the authoritative canonical outputs.

---

## Citation

- **GNNRank (underlying framework and GNN baselines):**

  ```bibtex
  @inproceedings{he2022gnnrank,
    title={GNNRank: Learning Global Rankings from Pairwise Comparisons via Directed Graph Neural Networks},
    author={He, Yixuan and Gan, Quan and Wipf, David and Reinert, Gesine D and Yan, Junchi and Cucuringu, Mihai},
    booktitle={ICML},
    pages={8581--8612},
    year={2022},
    organization={PMLR}
  }
  ```

- **This repository / ranking by feedback arc set:**

  ```bibtex
  @article{vahidi2026training,
    author  = {Vahidi, Soroush},
    title   = {Training-Free Ranking from Pairwise Comparisons via Acyclic Graph Construction},
    journal = {The Journal of Supercomputing},
    year    = {2026},
    note    = {Accepted}
  }
  ```

  and the [GNNRank repo](https://github.com/SherylHYX/GNNRank).

---

## License

MIT (see **LICENSE**).

**Code Availability:** All source code, processed data, and scripts required to reproduce the experiments are publicly available at <https://github.com/SoroushVahidi/ranking-by-feedback-arc-set>.
