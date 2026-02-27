# Contribution and Practical Advantages — Numeric Claims

Source: `paper_csv/unified_comparison.csv` (77 datasets with OURS).

---

## A) OURS vs best classical

### Upset simple
- **W/T/L** (tie 1e-6): 38 / 0 / 39  (n=77)
- **W/T/L** (tie 1e-3): 38 / 0 / 39
- **gap_simple**: median = 0.024390, mean = 0.103204, P25 = -0.123077, P75 = 0.377279, P90 = 0.397865, max = 0.498113
- **rel_gap_simple**: median = 0.030303, mean = 0.125001, P25 = -0.157895, P75 = 0.463659, P90 = 0.507597, max = 0.658537
- **Near-best**: within 1% = 38, within 5% = 41, within 10% = 42; **OURS better** (rel_gap < −1e-6) = 38

### Upset ratio
- **W/T/L** (1e-6): 45 / 0 / 32
- **W/T/L** (1e-3): 45 / 0 / 32
- **gap_ratio**: median = -0.038433, mean = -0.001347, P25 = -0.097720, P75 = 0.130738, P90 = 0.136223, max = 0.282442
- **rel_gap_ratio**: median = -0.078120, mean = 7.147246, P25 = -0.139657, P75 = 18.106268, P90 = 21.424675, max = 26.271752
- **Near-best**: within 1% = 45, within 5% = 46, within 10% = 47; **OURS better** = 45

---

## B) OURS vs best GNN

### Upset simple
- **W/T/L** (1e-6): 45 / 1 / 31  (n=77)
- **W/T/L** (1e-3): 45 / 1 / 31
- **gap_simple**: median = -0.182222, mean = -0.091876, P25 = -0.301624, P75 = 0.150983, P90 = 0.188737, max = 0.312646
- **rel_gap_simple**: median = -0.170124, mean = -0.103757, P25 = -0.321116, P75 = 0.144618, P90 = 0.188237, max = 0.331944
- **Near-best**: within 1% = 46, within 5% = 47, within 10% = 48; **OURS better** = 45

### Upset ratio
- **W/T/L** (1e-6): 47 / 0 / 30
- **W/T/L** (1e-3): 47 / 0 / 30
- **gap_ratio**: median = -0.170624, mean = -0.062642, P25 = -0.191455, P75 = 0.130394, P90 = 0.135379, max = 0.141579
- **rel_gap_ratio**: median = -0.228211, mean = 6.610344, P25 = -0.253627, P75 = 15.937049, P90 = 18.888540, max = 23.251944
- **Near-best**: within 1% = 47, within 5% = 47, within 10% = 47; **OURS better** = 47

---

## C) Tail diagnosis

### Top 20 datasets — largest rel_gap_simple vs best GNN (OURS worse)

| # | dataset | family | rel_gap_simple | ours | best_gnn |
|---|--------|--------|----------------|------|----------|
| 1 | Basketball_temporal/finer1985 | basketball_temporal_finer | 0.331944 | 1.2545 | 0.9419 |
| 2 | Basketball_temporal/finer1988 | basketball_temporal_finer | 0.235219 | 1.1746 | 0.9509 |
| 3 | Basketball_temporal/finer2011 | basketball_temporal_finer | 0.227219 | 1.2489 | 1.0176 |
| 4 | Basketball_temporal/finer2005 | basketball_temporal_finer | 0.215363 | 1.2335 | 1.0150 |
| 5 | Basketball_temporal/finer2013 | basketball_temporal_finer | 0.212211 | 1.2069 | 0.9956 |
| 6 | Basketball_temporal/finer1987 | basketball_temporal_finer | 0.207352 | 1.2075 | 1.0001 |
| 7 | Basketball_temporal/finer1994 | basketball_temporal_finer | 0.197327 | 1.1510 | 0.9613 |
| 8 | Basketball_temporal/finer1995 | basketball_temporal_finer | 0.196529 | 1.1869 | 0.9919 |
| 9 | Basketball_temporal/finer2012 | basketball_temporal_finer | 0.182710 | 1.1929 | 1.0086 |
| 10 | Basketball_temporal/finer1993 | basketball_temporal_finer | 0.182048 | 1.1540 | 0.9763 |
| 11 | Basketball_temporal/finer2007 | basketball_temporal_finer | 0.180526 | 1.2301 | 1.0420 |
| 12 | Basketball_temporal/finer2004 | basketball_temporal_finer | 0.177680 | 1.2069 | 1.0248 |
| 13 | Basketball_temporal/finer1990 | basketball_temporal_finer | 0.173632 | 1.1567 | 0.9855 |
| 14 | Basketball_temporal/finer2009 | basketball_temporal_finer | 0.170513 | 1.2247 | 1.0463 |
| 15 | Basketball_temporal/finer1997 | basketball_temporal_finer | 0.164594 | 1.2220 | 1.0493 |
| 16 | Basketball_temporal/finer2003 | basketball_temporal_finer | 0.158269 | 1.2177 | 1.0513 |
| 17 | Basketball_temporal/finer2014 | basketball_temporal_finer | 0.156464 | 1.2121 | 1.0481 |
| 18 | Basketball_temporal/finer1998 | basketball_temporal_finer | 0.156385 | 1.1994 | 1.0372 |
| 19 | Basketball_temporal/finer2010 | basketball_temporal_finer | 0.151590 | 1.1958 | 1.0384 |
| 20 | Basketball_temporal/finer1991 | basketball_temporal_finer | 0.144618 | 1.1435 | 0.9990 |

### Top 10 datasets — largest rel_gap_simple vs best classical

| # | dataset | family | rel_gap_simple | ours | best_classical |
|---|--------|--------|----------------|------|----------------|
| 1 | Basketball_temporal/finer1985 | basketball_temporal_finer | 0.658537 | 1.2545 | 0.7564 |
| 2 | Basketball_temporal/finer2004 | basketball_temporal_finer | 0.561984 | 1.2069 | 0.7727 |
| 3 | Basketball_temporal/finer1994 | basketball_temporal_finer | 0.560417 | 1.1510 | 0.7376 |
| 4 | Basketball_temporal/finer1993 | basketball_temporal_finer | 0.531120 | 1.1540 | 0.7537 |
| 5 | Basketball_temporal/finer1998 | basketball_temporal_finer | 0.530686 | 1.1994 | 0.7836 |
| 6 | Basketball_temporal/finer1992 | basketball_temporal_finer | 0.527495 | 1.1099 | 0.7266 |
| 7 | Basketball_temporal/finer1988 | basketball_temporal_finer | 0.515152 | 1.1746 | 0.7753 |
| 8 | Basketball_temporal/finer1995 | basketball_temporal_finer | 0.508637 | 1.1869 | 0.7867 |
| 9 | Basketball_temporal/finer1989 | basketball_temporal_finer | 0.506903 | 1.1558 | 0.7670 |
| 10 | Basketball_temporal/finer1996 | basketball_temporal_finer | 0.503636 | 1.2113 | 0.8056 |

---

## D) Runtime and Pareto

- **Speedup** (best_gnn_runtime / ours_runtime): n = 76
  - P25 = 4.72, median = 10.16, P75 = 18.18, mean = 62.69
  - Counts: ≥10× = 38, ≥50× = 17, ≥100× = 13

**Pareto (upset_simple vs best GNN, tie 1e-6):**
- Better & faster: 45
- Better but slower: 0
- Worse but faster: 31
- Worse & slower: 0