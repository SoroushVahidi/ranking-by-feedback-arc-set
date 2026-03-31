#!/usr/bin/env python3
"""Lightweight inspection/traceability CLI for canonical paper artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDITS = REPO_ROOT / "outputs" / "audits"
TABLES = REPO_ROOT / "outputs" / "paper_tables"


def read_csv(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def cmd_summary(_: argparse.Namespace) -> int:
    inv_summary = json.loads((AUDITS / "canonical_dataset_inventory_summary.json").read_text())
    method_map = json.loads((AUDITS / "method_name_canonicalization.json").read_text())
    print(f"canonical_dataset_count: {inv_summary['canonical_dataset_count']}")
    print("family_counts:")
    for fam, meta in inv_summary["families"].items():
        print(f"  - {fam}: {meta['dataset_count']}")
    print(f"canonical_methods ({len(method_map['observed_canonical_methods'])}):")
    for m in method_map["observed_canonical_methods"]:
        print(f"  - {m}")
    return 0


def cmd_list_tables(_: argparse.Namespace) -> int:
    for p in sorted(TABLES.glob("*.csv")):
        print(p.relative_to(REPO_ROOT))
    for p in sorted(TABLES.glob("*.json")):
        print(p.relative_to(REPO_ROOT))
    for p in sorted(TABLES.glob("*.md")):
        print(p.relative_to(REPO_ROOT))
    return 0


def cmd_methods(_: argparse.Namespace) -> int:
    mapping = json.loads((AUDITS / "method_name_canonicalization.json").read_text())
    print("Canonical aliases:")
    for k, v in sorted(mapping["canonical_aliases"].items()):
        print(f"  {k} -> {v}")
    return 0


def cmd_trace_row(args: argparse.Namespace) -> int:
    table_file = TABLES / f"{args.table}.csv"
    rows = read_csv(table_file)
    matches = [r for r in rows if r.get("method") == args.method and r.get("config") == args.config]
    print(f"table: {table_file.relative_to(REPO_ROOT)}")
    print(f"match_count: {len(matches)}")
    for r in matches:
        print(json.dumps(r, indent=2, sort_keys=True))
    print("upstream_source: paper_csv/results_from_result_arrays.csv")
    print("generation_script: scripts/paper/rebuild_experiment_tables.py")
    return 0


def cmd_explain_coverage(args: argparse.Namespace) -> int:
    rows = read_csv(TABLES / f"{args.table}.csv")
    inv = json.loads((AUDITS / "canonical_dataset_inventory_summary.json").read_text())
    total = inv["canonical_dataset_count"]
    hit = next((r for r in rows if r.get("method") == args.method and r.get("config") == args.config), None)
    if not hit:
        print("row not found")
        return 1
    print(f"coverage_field: {hit.get('coverage')}")
    print(f"denominator_explained_by_canonical_count: {total}")
    print("source: outputs/audits/canonical_dataset_inventory_summary.json")
    return 0


def cmd_explain_best(args: argparse.Namespace) -> int:
    rows = read_csv(TABLES / "table7_best_in_suite.csv")
    hit = next((r for r in rows if r["dataset"] == args.dataset), None)
    if not hit:
        print("dataset not found")
        return 1
    print(json.dumps(hit, indent=2, sort_keys=True))
    print("inputs: paper_csv/results_from_result_arrays.csv (which=upset, canonical suite filter)")
    return 0


def cmd_explain_runtime(args: argparse.Namespace) -> int:
    rows = read_csv(TABLES / "table8_runtime_tradeoff.csv")
    hit = next((r for r in rows if r["dataset"] == args.dataset), None)
    if not hit:
        print("dataset not found")
        return 1
    print(json.dumps(hit, indent=2, sort_keys=True))
    print("inputs: paper_csv/results_from_result_arrays.csv (runtime_sec_mean, upset_simple_mean)")
    return 0


def cmd_provenance(args: argparse.Namespace) -> int:
    prov = json.loads((TABLES / "provenance_manifest.json").read_text())
    output_file = args.output_file
    print(f"generator_script: {prov['generator_script']}")
    print(f"git_commit: {prov['git_commit']}")
    print(f"generated_at_utc: {prov['generated_at_utc']}")
    print(f"dataset_count_policy: {prov['dataset_count_policy']}")
    print(f"requested_output_present: {output_file in prov['generated_outputs']}")
    print("upstream_sources:")
    for s in prov["upstream_sources"]:
        print(f"  - {s}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("summary")
    sub.add_parser("list-tables")
    sub.add_parser("methods")

    t = sub.add_parser("trace-row")
    t.add_argument("--table", choices=["table4_full_suite", "table5_compute_matched"], required=True)
    t.add_argument("--method", required=True)
    t.add_argument("--config", required=True)

    c = sub.add_parser("explain-coverage")
    c.add_argument("--table", choices=["table4_full_suite", "table5_compute_matched"], required=True)
    c.add_argument("--method", required=True)
    c.add_argument("--config", required=True)

    b = sub.add_parser("explain-best")
    b.add_argument("--dataset", required=True)

    r = sub.add_parser("explain-runtime")
    r.add_argument("--dataset", required=True)

    pv = sub.add_parser("provenance")
    pv.add_argument("--output-file", required=True)

    return p


def main() -> int:
    args = build_parser().parse_args()
    dispatch = {
        "summary": cmd_summary,
        "list-tables": cmd_list_tables,
        "methods": cmd_methods,
        "trace-row": cmd_trace_row,
        "explain-coverage": cmd_explain_coverage,
        "explain-best": cmd_explain_best,
        "explain-runtime": cmd_explain_runtime,
        "provenance": cmd_provenance,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
