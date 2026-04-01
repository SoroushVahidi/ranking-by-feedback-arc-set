# Canonical Artifacts Summary

- Canonical dataset count: **81**
- Canonical methods (18): `DIGRAC, OURS_MFAS, OURS_MFAS_INS1, OURS_MFAS_INS2, OURS_MFAS_INS3, PageRank, SVD_NRS, SVD_RS, SpringRank, btl, btlDIGRAC, davidScore, eigenvectorCentrality, ib, mvr, rankCentrality, serialRank, syncRank`
- Canonical dataset policy: 81 datasets; no canonical 80-dataset subset.

## Use these files for claims
- Dataset inventory/counts: `outputs/audits/canonical_dataset_inventory.csv`, `outputs/audits/canonical_dataset_inventory_summary.json`
- Full-suite method rows: `outputs/paper_tables/table4_full_suite.csv`
- Compute-matched rows: `outputs/paper_tables/table5_compute_matched.csv`
- Missingness/timeout: `outputs/paper_tables/table6_missingness.csv`
- Best-in-suite: `outputs/paper_tables/table7_best_in_suite.csv`
- Runtime/Pareto tradeoff: `outputs/paper_tables/table8_runtime_tradeoff.csv`
- Claims bundle: `outputs/paper_tables/paper_claims_master.json`
- Claim trace map: `outputs/paper_tables/claim_traceability.json`

## Caveats
- Finance completion/timeout is method+config specific (see table6 and paper_claims_master).
- Archived legacy manuscript-support files are provenance-only and not canonical.
