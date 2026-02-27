#!/usr/bin/env python3
"""
Competitiveness of OURS_MFAS_INS3 from per_dataset_summary.csv.
Within k%: (OURS - best) <= k * best  =>  OURS <= best * (1 + k).
Exclude datasets where OURS_upset_simple is NA.
"""
import csv
from collections import defaultdict

def parse_float(s):
    if s in ("", "NA", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None

def main():
    path = "per_dataset_summary.csv"
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Family mapping for display (kind -> paper family name)
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

    def within_k(ours, best, k):
        if ours is None or best is None:
            return False
        if best <= 0:
            return ours <= 0  # edge case
        return (ours - best) <= k * best

    # Filter: OURS present
    valid = []
    for r in rows:
        ours = parse_float(r.get("OURS_upset_simple"))
        if ours is None:
            continue
        best_base = parse_float(r.get("best_non_ours_upset_simple"))
        best_gnn = parse_float(r.get("best_gnn_upset_simple"))
        valid.append({
            "kind": r.get("kind", ""),
            "family": family(r.get("kind", "")),
            "ours": ours,
            "best_baseline": best_base,
            "best_gnn": best_gnn,
        })

    n_total = len(valid)
    print("Count used (datasets with non-NA OURS_upset_simple):", n_total)
    print()

    # Overall: OURS vs best classical
    w1 = sum(1 for v in valid if v["best_baseline"] is not None and within_k(v["ours"], v["best_baseline"], 0.01))
    w5 = sum(1 for v in valid if v["best_baseline"] is not None and within_k(v["ours"], v["best_baseline"], 0.05))
    w10 = sum(1 for v in valid if v["best_baseline"] is not None and within_k(v["ours"], v["best_baseline"], 0.10))
    total_base = sum(1 for v in valid if v["best_baseline"] is not None)
    print("=== OURS vs best classical baseline (upset-simple) ===")
    print("Overall:")
    print(f"  total={total_base}, within_1pct={w1} ({100*w1/total_base:.1f}%), within_5pct={w5} ({100*w5/total_base:.1f}%), within_10pct={w10} ({100*w10/total_base:.1f}%)")
    print()

    # By family: OURS vs best classical
    by_fam_base = defaultdict(list)
    for v in valid:
        if v["best_baseline"] is not None:
            by_fam_base[v["family"]].append(v)

    print("By family (OURS vs best classical):")
    fam_order = ["Basketball", "Football", "Faculty", "Animal", "Head-to-head", "Finance"]
    for fam in fam_order:
        L = by_fam_base.get(fam, [])
        if not L:
            continue
        t = len(L)
        w1f = sum(1 for v in L if within_k(v["ours"], v["best_baseline"], 0.01))
        w5f = sum(1 for v in L if within_k(v["ours"], v["best_baseline"], 0.05))
        w10f = sum(1 for v in L if within_k(v["ours"], v["best_baseline"], 0.10))
        print(f"  {fam}: total={t}, within_1pct={w1f} ({100*w1f/t:.1f}%), within_5pct={w5f} ({100*w5f/t:.1f}%), within_10pct={w10f} ({100*w10f/t:.1f}%)")
    print()

    # Overall: OURS vs best GNN
    total_gnn = sum(1 for v in valid if v["best_gnn"] is not None)
    w1g = sum(1 for v in valid if v["best_gnn"] is not None and within_k(v["ours"], v["best_gnn"], 0.01))
    w5g = sum(1 for v in valid if v["best_gnn"] is not None and within_k(v["ours"], v["best_gnn"], 0.05))
    w10g = sum(1 for v in valid if v["best_gnn"] is not None and within_k(v["ours"], v["best_gnn"], 0.10))
    print("=== OURS vs best GNN variant (upset-simple) ===")
    print("Overall:")
    print(f"  total={total_gnn}, within_1pct={w1g} ({100*w1g/total_gnn:.1f}%), within_5pct={w5g} ({100*w5g/total_gnn:.1f}%), within_10pct={w10g} ({100*w10g/total_gnn:.1f}%)")
    print()

    by_fam_gnn = defaultdict(list)
    for v in valid:
        if v["best_gnn"] is not None:
            by_fam_gnn[v["family"]].append(v)

    print("By family (OURS vs best GNN):")
    for fam in fam_order:
        L = by_fam_gnn.get(fam, [])
        if not L:
            continue
        t = len(L)
        w1f = sum(1 for v in L if within_k(v["ours"], v["best_gnn"], 0.01))
        w5f = sum(1 for v in L if within_k(v["ours"], v["best_gnn"], 0.05))
        w10f = sum(1 for v in L if within_k(v["ours"], v["best_gnn"], 0.10))
        print(f"  {fam}: total={t}, within_1pct={w1f} ({100*w1f/t:.1f}%), within_5pct={w5f} ({100*w5f/t:.1f}%), within_10pct={w10f} ({100*w10f/t:.1f}%)")
    print()

    # Small table (counts and percentages)
    print("--- Small overall table (counts and %) ---")
    print("Comparison,Total,within_1pct,within_5pct,within_10pct")
    print(f"OURS vs best baseline,{total_base},{w1} ({100*w1/total_base:.1f}%),{w5} ({100*w5/total_base:.1f}%),{w10} ({100*w10/total_base:.1f}%)")
    print(f"OURS vs best GNN,{total_gnn},{w1g} ({100*w1g/total_gnn:.1f}%),{w5g} ({100*w5g/total_gnn:.1f}%),{w10g} ({100*w10g/total_gnn:.1f}%)")
    print()

    # LaTeX rows by family
    print("--- LaTeX-ready rows (OURS vs best classical baseline) ---")
    for fam in fam_order:
        L = by_fam_base.get(fam, [])
        if not L:
            if fam == "Finance":
                print("Finance & 0 & -- & -- & -- \\\\")
            continue
        t = len(L)
        w1f = sum(1 for v in L if within_k(v["ours"], v["best_baseline"], 0.01))
        w5f = sum(1 for v in L if within_k(v["ours"], v["best_baseline"], 0.05))
        w10f = sum(1 for v in L if within_k(v["ours"], v["best_baseline"], 0.10))
        p1 = 100 * w1f / t
        p5 = 100 * w5f / t
        p10 = 100 * w10f / t
        fam_tex = "Head-to-head" if fam == "Head-to-head" else fam
        print(f"{fam_tex} & {t} & {w1f} ({p1:.1f}\\%) & {w5f} ({p5:.1f}\\%) & {w10f} ({p10:.1f}\\%) \\\\")

    print()
    print("--- LaTeX-ready rows (OURS vs best GNN) ---")
    for fam in fam_order:
        L = by_fam_gnn.get(fam, [])
        if not L:
            if fam == "Finance":
                print("Finance & 0 & -- & -- & -- \\\\")
            continue
        t = len(L)
        w1f = sum(1 for v in L if within_k(v["ours"], v["best_gnn"], 0.01))
        w5f = sum(1 for v in L if within_k(v["ours"], v["best_gnn"], 0.05))
        w10f = sum(1 for v in L if within_k(v["ours"], v["best_gnn"], 0.10))
        p1 = 100 * w1f / t
        p5 = 100 * w5f / t
        p10 = 100 * w10f / t
        fam_tex = "Head-to-head" if fam == "Head-to-head" else fam
        print(f"{fam_tex} & {t} & {w1f} ({p1:.1f}\\%) & {w5f} ({p5:.1f}\\%) & {w10f} ({p10:.1f}\\%) \\\\")

if __name__ == "__main__":
    main()
