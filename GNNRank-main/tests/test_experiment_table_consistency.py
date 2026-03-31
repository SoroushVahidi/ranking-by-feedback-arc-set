import json
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def test_dataset_denominator_consistency():
    inv = read_csv(ROOT / "outputs/audits/canonical_dataset_inventory.csv")
    t4 = read_csv(ROOT / "outputs/paper_tables/table4_full_suite.csv")
    ds_count = len(inv)
    assert ds_count == 81
    assert all(int(r["coverage"].split("/")[-1].strip()) == ds_count for r in t4)


def test_claims_alignment():
    claims = json.loads((ROOT / "outputs/paper_tables/paper_claims_master.json").read_text())
    t8 = read_csv(ROOT / "outputs/paper_tables/table8_runtime_tradeoff.csv")
    assert claims["canonical_dataset_count"] == 81
    assert claims["pareto_denominator"] == len(t8)


def test_provenance_and_method_mapping_present():
    provenance = json.loads((ROOT / "outputs/paper_tables/provenance_manifest.json").read_text())
    method_map = json.loads((ROOT / "outputs/audits/method_name_canonicalization.json").read_text())
    assert provenance["dataset_count_policy"].find("81") >= 0
    assert "outputs/paper_tables/table4_full_suite.csv" in provenance["generated_outputs"]
    assert "outputs/paper_tables/claim_traceability.json" in provenance["generated_outputs"]
    assert method_map["canonical_aliases"]["BTL"] == "btl"
    assert "OURS_MFAS_INS3" in method_map["observed_canonical_methods"]


def test_claim_traceability_integrity():
    claim_trace = json.loads((ROOT / "outputs/paper_tables/claim_traceability.json").read_text())
    method_map = json.loads((ROOT / "outputs/audits/method_name_canonicalization.json").read_text())
    assert "table4_full_suite_claims" in claim_trace
    for _, meta in claim_trace.items():
        assert (ROOT / meta["canonical_output_file"]).exists()
        for src in meta.get("upstream_sources", []):
            assert (ROOT / src).exists()
    assert "davidScore" in method_map["observed_canonical_methods"]
