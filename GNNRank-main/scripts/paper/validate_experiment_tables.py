#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDITS = REPO_ROOT / "outputs" / "audits"
TABLES = REPO_ROOT / "outputs" / "paper_tables"


def read_csv(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    inv = read_csv(AUDITS / "canonical_dataset_inventory.csv")
    summary = json.loads((AUDITS / "canonical_dataset_inventory_summary.json").read_text())
    t4 = read_csv(TABLES / "table4_full_suite.csv")
    t7 = read_csv(TABLES / "table7_best_in_suite.csv")
    t8 = read_csv(TABLES / "table8_runtime_tradeoff.csv")
    claims = json.loads((TABLES / "paper_claims_master.json").read_text())
    provenance = json.loads((TABLES / "provenance_manifest.json").read_text())
    method_map = json.loads((AUDITS / "method_name_canonicalization.json").read_text())
    claim_trace = json.loads((TABLES / "claim_traceability.json").read_text())
    summary_md = (TABLES / "canonical_artifacts_summary.md").read_text()

    errors = []
    ds_count = len(inv)
    if ds_count != int(summary["canonical_dataset_count"]):
        errors.append("dataset count mismatch between inventory csv and summary json")

    for row in t4:
        cov = row["coverage"].split("/")[-1].strip()
        if int(cov) != ds_count:
            errors.append(f"table4 denominator mismatch for {row['method']}|{row['config']}")
            break

    if len(t7) != ds_count:
        errors.append("table7 dataset row count must equal canonical dataset count")

    if claims["canonical_dataset_count"] != ds_count:
        errors.append("claims master canonical_dataset_count mismatch")

    if claims["pareto_denominator"] != len(t8):
        errors.append("pareto denominator must match table8 row count")

    expected_outputs = {
        "outputs/audits/canonical_dataset_inventory.csv",
        "outputs/audits/canonical_dataset_inventory_summary.json",
        "outputs/audits/method_name_canonicalization.json",
        "outputs/paper_tables/table4_full_suite.csv",
        "outputs/paper_tables/table5_compute_matched.csv",
        "outputs/paper_tables/table6_missingness.csv",
        "outputs/paper_tables/table7_best_in_suite.csv",
        "outputs/paper_tables/table8_runtime_tradeoff.csv",
        "outputs/paper_tables/paper_claims_master.json",
        "outputs/paper_tables/claim_traceability.json",
        "outputs/paper_tables/canonical_artifacts_summary.md",
    }
    if not expected_outputs.issubset(set(provenance.get("generated_outputs", []))):
        errors.append("provenance manifest missing required generated outputs")
    if "dataset_count_policy" not in provenance:
        errors.append("provenance manifest missing dataset_count_policy")
    if int(summary["canonical_dataset_count"]) != 81:
        errors.append("canonical dataset count drifted from policy value 81")

    observed_methods = set(method_map.get("observed_canonical_methods", []))
    if "OURS_MFAS_INS1" not in observed_methods or "davidScore" not in observed_methods:
        errors.append("method canonicalization artifact missing expected canonical labels")

    # Claim traceability integrity
    for claim_name, meta in claim_trace.items():
        out_file = meta.get("canonical_output_file")
        if not out_file:
            errors.append(f"claim {claim_name} missing canonical_output_file")
            continue
        if not (REPO_ROOT / out_file).exists():
            errors.append(f"claim {claim_name} references missing file {out_file}")
        for src in meta.get("upstream_sources", []):
            if not (REPO_ROOT / src).exists():
                errors.append(f"claim {claim_name} references missing upstream source {src}")

    if f"**{ds_count}**" not in summary_md:
        errors.append("canonical summary markdown does not include canonical dataset count")
    if "no canonical 80-dataset subset" not in summary_md:
        errors.append("canonical summary markdown missing no-80-subset caveat")

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print("-", e)
        return 1

    print("VALIDATION PASSED")
    print(f"canonical_dataset_count={ds_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
