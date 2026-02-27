#!/usr/bin/env python3
"""
How-far-from-best distributions from per_dataset_summary.csv.
Filter: 77 datasets with non-NA OURS_upset_simple (exclude finance).
gap = OURS - best,  rel_gap = gap / best.
"""
import csv
import math
from collections import defaultdict

def parse_float(s):
    if s in ("", "NA", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None

def family(kind):
    if not kind:
        return "Other"
    if kind == "basketball_temporal":
        return "Basketball"
    if kind == "football_temporal":
        return "Football"
    if kind in ("faculty_business", "faculty_cs", "faculty_history"):
        return "Faculty"
    if kind == "animal_static":
        return "Animal"
    if kind == "headtohead_static":
        return "Head-to-head"
    if kind == "finance_static":
        return "Finance"
    return kind

def stats(arr):
    """Count, mean, std, min, P10, P25, median, P75, P90, max."""
    if not arr:
        return None
    n = len(arr)
    s = sorted(arr)
    mean = sum(arr) / n
    var = sum((x - mean) ** 2 for x in arr) / n if n else 0
    std = math.sqrt(var) if var else 0.0
    def p(q):
        idx = max(0, min(n - 1, int(round((q / 100) * (n - 1)))))
        return s[idx]
    return {
        "count": n,
        "mean": mean,
        "std": std,
        "min": s[0],
        "p10": p(10),
        "p25": p(25),
        "median": p(50),
        "p75": p(75),
        "p90": p(90),
        "max": s[-1],
    }

def tie_counts(gaps, rel_gaps):
    c_1e6 = sum(1 for g in gaps if abs(g) <= 1e-6)
    c_1e3 = sum(1 for g in gaps if abs(g) <= 1e-3)
    c_rel1 = sum(1 for r in rel_gaps if r is not None and abs(r) <= 0.01)
    return c_1e6, c_1e3, c_rel1

def main():
    path = "per_dataset_summary.csv"
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    valid = []
    for r in rows:
        ours = parse_float(r.get("OURS_upset_simple"))
        if ours is None:
            continue
        best_base = parse_float(r.get("best_non_ours_upset_simple"))
        best_gnn = parse_float(r.get("best_gnn_upset_simple"))
        kind = r.get("kind", "")
        valid.append({
            "kind": kind,
            "family": family(kind),
            "ours": ours,
            "best_baseline": best_base,
            "best_gnn": best_gnn,
        })

    n = len(valid)
    print("Count used (non-NA OURS_upset_simple):", n)
    print()

    # Compute gap and rel_gap for classical and GNN
    gap_classical = []
    rel_gap_classical = []
    gap_gnn = []
    rel_gap_gnn = []
    by_fam = defaultdict(lambda: {"gap_c": [], "rel_c": [], "gap_g": [], "rel_g": []})

    for v in valid:
        ours, best_b, best_g = v["ours"], v["best_baseline"], v["best_gnn"]
        fam = v["family"]

        if best_b is not None:
            g_c = ours - best_b
            gap_classical.append(g_c)
            rel_c = (g_c / best_b) if best_b > 0 else None
            if rel_c is not None:
                rel_gap_classical.append(rel_c)
            by_fam[fam]["gap_c"].append(g_c)
            if rel_c is not None:
                by_fam[fam]["rel_c"].append(rel_c)

        if best_g is not None:
            g_g = ours - best_g
            gap_gnn.append(g_g)
            rel_g = (g_g / best_g) if best_g > 0 else None
            if rel_g is not None:
                rel_gap_gnn.append(rel_g)
            by_fam[fam]["gap_g"].append(g_g)
            if rel_g is not None:
                by_fam[fam]["rel_g"].append(rel_g)

    fam_order = ["Basketball", "Football", "Faculty", "Animal", "Head-to-head", "Finance"]

    def print_stats(name, gap_arr, rel_arr):
        print(name)
        if gap_arr:
            s = stats(gap_arr)
            print("  gap: count=%d mean=%.6f std=%.6f min=%.6f P10=%.6f P25=%.6f median=%.6f P75=%.6f P90=%.6f max=%.6f" % (
                s["count"], s["mean"], s["std"], s["min"], s["p10"], s["p25"], s["median"], s["p75"], s["p90"], s["max"]))
        if rel_arr:
            s = stats(rel_arr)
            print("  rel_gap: count=%d mean=%.4f std=%.4f min=%.4f P10=%.4f P25=%.4f median=%.4f P75=%.4f P90=%.4f max=%.4f" % (
                s["count"], s["mean"], s["std"], s["min"], s["p10"], s["p25"], s["median"], s["p75"], s["p90"], s["max"]))
        c6, c3, cr1 = tie_counts(gap_arr, rel_arr)
        print("  ties: |gap|<=1e-6: %d  |gap|<=1e-3: %d  |rel_gap|<=1%%: %d" % (c6, c3, cr1))
        print()

    # (A) OURS vs best classical
    print("=" * 60)
    print("(A) OURS vs best classical baseline")
    print("=" * 60)
    print("1) Overall distribution stats")
    print_stats("Overall", gap_classical, rel_gap_classical)

    print("2) By family (gap and rel_gap stats)")
    for fam in fam_order:
        Lc = by_fam[fam]["gap_c"]
        Lr = by_fam[fam]["rel_c"]
        if not Lc:
            if fam == "Finance":
                print("  Finance: (0 datasets)")
            continue
        print("  %s (n=%d):" % (fam, len(Lc)))
        if Lc:
            s = stats(Lc)
            print("    gap: mean=%.6f median=%.6f P75=%.6f P90=%.6f" % (s["mean"], s["median"], s["p75"], s["p90"]))
        if Lr:
            s = stats(Lr)
            print("    rel_gap: mean=%.4f median=%.4f P75=%.4f P90=%.4f" % (s["mean"], s["median"], s["p75"], s["p90"]))
        c6, c3, cr1 = tie_counts(Lc, Lr)
        print("    ties: |gap|<=1e-6: %d  |gap|<=1e-3: %d  |rel_gap|<=1%%: %d" % (c6, c3, cr1))
    print()

    # (B) OURS vs best GNN
    print("=" * 60)
    print("(B) OURS vs best GNN variant")
    print("=" * 60)
    print("1) Overall distribution stats")
    print_stats("Overall", gap_gnn, rel_gap_gnn)

    print("2) By family")
    for fam in fam_order:
        Lc = by_fam[fam]["gap_g"]
        Lr = by_fam[fam]["rel_g"]
        if not Lc:
            if fam == "Finance":
                print("  Finance: (0 datasets)")
            continue
        print("  %s (n=%d):" % (fam, len(Lc)))
        if Lc:
            s = stats(Lc)
            print("    gap: mean=%.6f median=%.6f P75=%.6f P90=%.6f" % (s["mean"], s["median"], s["p75"], s["p90"]))
        if Lr:
            s = stats(Lr)
            print("    rel_gap: mean=%.4f median=%.4f P75=%.4f P90=%.4f" % (s["mean"], s["median"], s["p75"], s["p90"]))
        c6, c3, cr1 = tie_counts(Lc, Lr)
        print("    ties: |gap|<=1e-6: %d  |gap|<=1e-3: %d  |rel_gap|<=1%%: %d" % (c6, c3, cr1))
    print()

    # 3) Tie counts summary
    print("3) Tie counts (overall)")
    print("  (A) vs classical: |gap|<=1e-6: %d  |gap|<=1e-3: %d  |rel_gap|<=1%%: %d" % tie_counts(gap_classical, rel_gap_classical))
    print("  (B) vs GNN:       |gap|<=1e-6: %d  |gap|<=1e-3: %d  |rel_gap|<=1%%: %d" % tie_counts(gap_gnn, rel_gap_gnn))
    print()

    # 4) LaTeX-ready family table: rel_gap median, P75, P90, tie counts
    print("4) LaTeX-ready family table (rel_gap median, P75, P90; tie counts)")
    print()
    print("--- (A) OURS vs best classical ---")
    print("Family & $n$ & rel\\_gap med & P75 & P90 & $|$gap$|\\le 10^{-6}$ & $|$gap$|\\le 10^{-3}$ & $|$rel\\_gap$|\\le 1\\%$ \\\\")
    for fam in fam_order:
        Lc = by_fam[fam]["gap_c"]
        Lr = by_fam[fam]["rel_c"]
        if not Lc:
            if fam == "Finance":
                print("Finance & 0 & -- & -- & -- & -- & -- & -- \\\\")
            continue
        c6, c3, cr1 = tie_counts(Lc, Lr)
        if Lr:
            s = stats(Lr)
            med, p75, p90 = s["median"], s["p75"], s["p90"]
            print("%s & %d & %.4f & %.4f & %.4f & %d & %d & %d \\\\" % (fam, len(Lc), med, p75, p90, c6, c3, cr1))
        else:
            print("%s & %d & -- & -- & -- & %d & %d & %d \\\\" % (fam, len(Lc), c6, c3, cr1))

    print()
    print("--- (B) OURS vs best GNN ---")
    print("Family & $n$ & rel\\_gap med & P75 & P90 & $|$gap$|\\le 10^{-6}$ & $|$gap$|\\le 10^{-3}$ & $|$rel\\_gap$|\\le 1\\%$ \\\\")
    for fam in fam_order:
        Lc = by_fam[fam]["gap_g"]
        Lr = by_fam[fam]["rel_g"]
        if not Lc:
            if fam == "Finance":
                print("Finance & 0 & -- & -- & -- & -- & -- & -- \\\\")
            continue
        c6, c3, cr1 = tie_counts(Lc, Lr)
        if Lr:
            s = stats(Lr)
            med, p75, p90 = s["median"], s["p75"], s["p90"]
            print("%s & %d & %.4f & %.4f & %.4f & %d & %d & %d \\\\" % (fam, len(Lc), med, p75, p90, c6, c3, cr1))
        else:
            print("%s & %d & -- & -- & -- & %d & %d & %d \\\\" % (fam, len(Lc), c6, c3, cr1))

if __name__ == "__main__":
    main()
