# OURS rerun shortlist (no runs launched)

Goal: pick a small set of high-leverage datasets to re-run OURS on after the code change, using existing CSVs only.

| dataset | best OURS method | OURS upset_simple | best classical (method, upset_simple) | oracle (method, upset_simple) | reason for inclusion |
|---------|------------------|-------------------|----------------------------------------|-------------------------------|----------------------|
| Football_data_England_Premier_League/England_2009_2010 | OURS_MFAS | 0.634 | SpringRank (0.610) | SpringRank (0.610) | OURS within 0.024 of best classical |
| Football_data_England_Premier_League/England_2012_2013 | OURS_MFAS | 0.889 | SVD_NRS (0.863) | SVD_NRS (0.863) | OURS within 0.026 of best classical |