# Sparse-regime robustness audit (repository-only)

- Metrics source: GNNRank-main/paper_csv/results_from_result_arrays.csv
- Dataset inventory source: GNNRank-main/outputs/audits/canonical_dataset_inventory.csv
- Density formula: m_edges / (n_nodes * (n_nodes - 1)).
- Comparator value per dataset/method: best config chosen by min(upset_simple), tie-break min(upset_ratio), tie-break min(runtime).

## Exact sparse dataset set (threshold <= 0.05, OURS vs SpringRank)
- Sample size: 31
- Datasets: Basketball_temporal/1985, Basketball_temporal/1986, Basketball_temporal/1987, Basketball_temporal/1988, Basketball_temporal/1989, Basketball_temporal/1990, Basketball_temporal/1991, Basketball_temporal/1992, Basketball_temporal/1993, Basketball_temporal/1994, Basketball_temporal/1995, Basketball_temporal/1996, Basketball_temporal/1997, Basketball_temporal/1998, Basketball_temporal/1999, Basketball_temporal/2000, Basketball_temporal/2001, Basketball_temporal/2002, Basketball_temporal/2003, Basketball_temporal/2004, Basketball_temporal/2005, Basketball_temporal/2006, Basketball_temporal/2007, Basketball_temporal/2008, Basketball_temporal/2009, Basketball_temporal/2010, Basketball_temporal/2011, Basketball_temporal/2012, Basketball_temporal/2013, Basketball_temporal/2014, FacultyHiringNetworks/ComputerScience/ComputerScience_FM_Full_

## Threshold sensitivity (OURS vs SpringRank)
- <= 0.02: n=0, W/T/L=0/0/0, mean_margin=nan, median_margin=nan, favorable=False
- <= 0.03: n=0, W/T/L=0/0/0, mean_margin=nan, median_margin=nan, favorable=False
- <= 0.05: n=31, W/T/L=31/0/0, mean_margin=-0.134252, median_margin=-0.132039, favorable=True
- <= 0.08: n=62, W/T/L=32/0/30, mean_margin=0.116840, median_margin=-0.090098, favorable=True

## Quantile bins (OURS vs SpringRank)
- Q1: n=19, W/T/L=19/0/0, mean_margin=-0.130869, median_margin=-0.130669, favorable=True
- Q2-Q4: n=57, W/T/L=21/0/36, mean_margin=0.163023, median_margin=0.321265, favorable=False
- Q1-Q2: n=38, W/T/L=32/0/6, mean_margin=-0.048487, median_margin=-0.128000, favorable=True
- Q3-Q4: n=38, W/T/L=8/0/30, mean_margin=0.227588, median_margin=0.350519, favorable=False

## Family composition in sparse subset (density <= 0.05, vs SpringRank)
- Basketball_temporal: 30
- FacultyHiringNetworks: 1

### Family-level W/T/L (families with n>=3)
- Basketball_temporal: n=30, W/T/L=30/0/0, mean_margin=-0.135600, median_margin=-0.132074

## Sparse-threshold cross-baseline check (density <= 0.05)
- vs SpringRank: n=31, W/T/L=31/0/0, mean_margin=-0.134252, median_margin=-0.132039, favorable=True
- vs davidScore: n=31, W/T/L=31/0/0, mean_margin=-0.144198, median_margin=-0.133031, favorable=True
- vs SVD_NRS: n=31, W/T/L=31/0/0, mean_margin=-0.243603, median_margin=-0.244049, favorable=True
- vs btl: n=31, W/T/L=31/0/0, mean_margin=-0.259263, median_margin=-0.279261, favorable=True

## Manuscript-safety verdict
- Verdict: **promising but narrow**
- Safe wording: 'OURS shows a consistent direct advantage over SpringRank on low-density subsets (e.g., <=0.05), but this is regime-specific and should not be presented as global dominance.'
