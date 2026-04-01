# Targeted OURS positive-search report (repository only)

- Source metrics: `GNNRank-main/paper_csv/results_from_result_arrays.csv`
- Source inventory: `GNNRank-main/outputs/audits/canonical_dataset_inventory.csv`
- Phase ablation status: **blocked: Missing numeric dependencies: No module named 'numpy'**

## INS pass proxy (A+B+C variants with 1/2/3 insertion passes)
- Datasets with INS1/2/3 all present: 79
- Median upset_simple: OURS_MFAS_INS1=0.880927, OURS_MFAS_INS2=0.878049, OURS_MFAS_INS3=0.878049
- Median upset_ratio: OURS_MFAS_INS1=0.508648, OURS_MFAS_INS2=0.509080, OURS_MFAS_INS3=0.509080
- Median upset_naive: OURS_MFAS_INS1=0.220232, OURS_MFAS_INS2=0.219512, OURS_MFAS_INS3=0.219512
- Median runtime_sec: OURS_MFAS_INS1=1.072993, OURS_MFAS_INS2=1.079557, OURS_MFAS_INS3=1.079134

## Direct pairwise vs strongest classical candidates
- SpringRank: n=77, W/T/L=41/0/36, mean_margin=0.086789, median_margin=-0.078431, median_runtime_ratio(OURS/SpringRank)=17.86
- davidScore: n=77, W/T/L=40/1/36, mean_margin=0.062799, median_margin=-0.024242, median_runtime_ratio(OURS/davidScore)=337.10
- SVD_NRS: n=77, W/T/L=40/2/35, mean_margin=0.007051, median_margin=-0.024845, median_runtime_ratio(OURS/SVD_NRS)=180.11

## Regime scan vs SpringRank (direct)
- [density_bin] mid<=0.15: n=32, W/T/L=2/0/30, median_margin=0.387071, advantage=none
- [density_bin] sparse<=0.05: n=31, W/T/L=31/0/0, median_margin=-0.132039, advantage=direct
- [density_bin] dense>0.15: n=14, W/T/L=7/1/6, median_margin=-0.025262, advantage=direct
- [family] Basketball_temporal: n=60, W/T/L=30/0/30, median_margin=0.096840, advantage=none
- [family] Football_data_England_Premier_League: n=12, W/T/L=6/0/6, median_margin=-0.025262, advantage=none
- [runtime_bin] mid<=2s: n=31, W/T/L=31/0/0, median_margin=-0.132039, advantage=direct
- [runtime_bin] slow>2s: n=31, W/T/L=0/1/30, median_margin=0.388454, advantage=none
- [runtime_bin] fast<=0.5s: n=16, W/T/L=10/0/6, median_margin=-0.076599, advantage=direct
- [size_bin] large>150: n=62, W/T/L=31/1/30, median_margin=0.108640, advantage=direct
- [size_bin] small<=50: n=14, W/T/L=8/0/6, median_margin=-0.076599, advantage=direct
