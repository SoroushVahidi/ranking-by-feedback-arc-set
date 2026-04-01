#!/usr/bin/env python3
"""Repository-only targeted search for strongest honest positive evidence for OURS."""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "GNNRank-main" / "paper_csv" / "results_from_result_arrays.csv"
INV = ROOT / "GNNRank-main" / "outputs" / "audits" / "canonical_dataset_inventory.csv"
PHASE = ROOT / "GNNRank-main" / "outputs" / "ablation" / "phase_ablation_results.csv"
OUT_DIR = ROOT / "outputs" / "audits"
OUT_MD = OUT_DIR / "targeted_ours_positive_search.md"
OUT_CSV = OUT_DIR / "targeted_pairwise_summary.csv"

OURS = "OURS_MFAS"
OURS_INS = ["OURS_MFAS_INS1", "OURS_MFAS_INS2", "OURS_MFAS_INS3"]
FOCUS_CLASSICAL = ["SpringRank", "davidScore", "SVD_NRS"]


def f(x: str) -> float:
    try:
        return float(x)
    except Exception:
        return math.nan


def load_inventory():
    out = {}
    with INV.open() as fh:
        for r in csv.DictReader(fh):
            n = int(r["n_nodes"]) if r["n_nodes"] else 0
            m = int(r["m_edges"]) if r["m_edges"] else 0
            dens = (m / (n * (n - 1))) if n > 1 else math.nan
            out[r["dataset"]] = {
                "family": r["family"],
                "n_nodes": n,
                "m_edges": m,
                "density": dens,
            }
    return out


def pick_best_configs():
    # best row per (dataset, method) by upset_simple_mean then upset_ratio_mean
    best = {}
    methods = set()
    with DATA.open() as fh:
        for r in csv.DictReader(fh):
            if r.get("which") != "upset":
                continue
            ds, m = r["dataset"], r["method"]
            methods.add(m)
            cur = {
                "upset_simple": f(r["upset_simple_mean"]),
                "upset_ratio": f(r["upset_ratio_mean"]),
                "upset_naive": f(r["upset_naive_mean"]),
                "runtime_sec": f(r["runtime_sec_mean"]),
                "config": r["config"],
            }
            k = (ds, m)
            old = best.get(k)
            if old is None:
                best[k] = cur
            else:
                a = (cur["upset_simple"], cur["upset_ratio"], cur["runtime_sec"])
                b = (old["upset_simple"], old["upset_ratio"], old["runtime_sec"])
                if a < b:
                    best[k] = cur
    return best, methods


def win_tie_loss(best, inv, ours, comp, metric):
    wins = ties = losses = 0
    margins = []
    runt = []
    by_family = defaultdict(lambda: [0, 0, 0])
    for ds in inv:
        ko, kc = (ds, ours), (ds, comp)
        if ko not in best or kc not in best:
            continue
        vo = best[ko][metric]
        vc = best[kc][metric]
        if math.isnan(vo) or math.isnan(vc):
            continue
        d = vo - vc
        margins.append(d)
        fam = inv[ds]["family"]
        if abs(d) <= 1e-12:
            ties += 1
            by_family[fam][1] += 1
        elif d < 0:
            wins += 1
            by_family[fam][0] += 1
        else:
            losses += 1
            by_family[fam][2] += 1
        ro, rc = best[ko]["runtime_sec"], best[kc]["runtime_sec"]
        if rc and not math.isnan(ro) and not math.isnan(rc):
            runt.append(ro / rc)
    return {
        "n": wins + ties + losses,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "mean_margin": mean(margins) if margins else math.nan,
        "median_margin": median(margins) if margins else math.nan,
        "median_runtime_ratio_ours_over_comp": median(runt) if runt else math.nan,
        "family": by_family,
    }


def bin_name(v, cuts, labels):
    for c, lab in zip(cuts, labels):
        if v <= c:
            return lab
    return labels[-1]


def regime_scan(best, inv, comparator="SpringRank"):
    rows = []
    for ds, meta in inv.items():
        ko, kc = (ds, OURS), (ds, comparator)
        if ko not in best or kc not in best:
            continue
        rows.append((ds, meta, best[ko], best[kc]))

    reg = defaultdict(list)
    for ds, meta, o, c in rows:
        reg[("family", meta["family"])].append((o, c))
        reg[("size_bin", bin_name(meta["n_nodes"], [50, 150], ["small<=50", "mid<=150", "large>150"]))].append((o, c))
        d = meta["density"]
        if not math.isnan(d):
            reg[("density_bin", bin_name(d, [0.05, 0.15], ["sparse<=0.05", "mid<=0.15", "dense>0.15"]))].append((o, c))
        reg[("runtime_bin", bin_name(o["runtime_sec"], [0.5, 2.0], ["fast<=0.5s", "mid<=2s", "slow>2s"]))].append((o, c))

    out = []
    for (kind, label), vals in reg.items():
        n = len(vals)
        w = sum(1 for o, c in vals if o["upset_simple"] < c["upset_simple"])
        l = sum(1 for o, c in vals if o["upset_simple"] > c["upset_simple"])
        t = n - w - l
        margins = [o["upset_simple"] - c["upset_simple"] for o, c in vals]
        out.append({
            "slice_type": kind,
            "slice": label,
            "comparator": comparator,
            "metric": "upset_simple",
            "n": n,
            "wins": w,
            "ties": t,
            "losses": l,
            "mean_margin": mean(margins) if margins else math.nan,
            "median_margin": median(margins) if margins else math.nan,
            "advantage": "direct" if w > l else "none",
        })
    out.sort(key=lambda r: (r["slice_type"], -r["n"], r["slice"]))
    return out


def phase_status():
    if not PHASE.exists():
        return "missing"
    with PHASE.open() as fh:
        rows = list(csv.DictReader(fh))
    if rows and rows[0].get("status") == "blocked":
        return f"blocked: {rows[0].get('note','').strip()}"
    modes = sorted({r.get("phase_mode", "") for r in rows if r.get("phase_mode")})
    return "ok: " + ", ".join(modes)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inv = load_inventory()
    best, methods = pick_best_configs()

    pair_rows = []
    report = []

    report.append("# Targeted OURS positive-search report (repository only)\n")
    report.append(f"- Source metrics: `{DATA.relative_to(ROOT)}`")
    report.append(f"- Source inventory: `{INV.relative_to(ROOT)}`")
    report.append(f"- Phase ablation status: **{phase_status()}**\n")

    # phase proxy INS1/2/3
    ins_sets = [m for m in OURS_INS if m in methods]
    report.append("## INS pass proxy (A+B+C variants with 1/2/3 insertion passes)")
    if len(ins_sets) == 3:
        commons = [ds for ds in inv if all((ds, m) in best for m in ins_sets)]
        report.append(f"- Datasets with INS1/2/3 all present: {len(commons)}")
        for metric in ("upset_simple", "upset_ratio", "upset_naive", "runtime_sec"):
            med = {}
            for m in ins_sets:
                med[m] = median([best[(ds, m)][metric] for ds in commons])
            report.append(f"- Median {metric}: " + ", ".join(f"{k}={v:.6f}" for k,v in med.items()))
    else:
        report.append("- INS1/2/3 are not all available in repository artifacts.")

    report.append("\n## Direct pairwise vs strongest classical candidates")
    for comp in FOCUS_CLASSICAL:
        if comp not in methods:
            continue
        stat = win_tie_loss(best, inv, OURS, comp, "upset_simple")
        pair_rows.append({"comparator": comp, **{k:v for k,v in stat.items() if k!="family"}})
        report.append(
            f"- {comp}: n={stat['n']}, W/T/L={stat['wins']}/{stat['ties']}/{stat['losses']}, "
            f"mean_margin={stat['mean_margin']:.6f}, median_margin={stat['median_margin']:.6f}, "
            f"median_runtime_ratio(OURS/{comp})={stat['median_runtime_ratio_ours_over_comp']:.2f}"
        )

    report.append("\n## Regime scan vs SpringRank (direct)")
    reg = regime_scan(best, inv, comparator="SpringRank")
    top = [r for r in reg if r["n"] >= 5]
    for r in top[:18]:
        report.append(
            f"- [{r['slice_type']}] {r['slice']}: n={r['n']}, W/T/L={r['wins']}/{r['ties']}/{r['losses']}, "
            f"median_margin={r['median_margin']:.6f}, advantage={r['advantage']}"
        )

    with OUT_CSV.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pair_rows[0].keys()))
        w.writeheader(); w.writerows(pair_rows)

    OUT_MD.write_text("\n".join(report) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
