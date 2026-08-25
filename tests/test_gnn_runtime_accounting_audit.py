"""Fast checks for GNN runtime accounting audit artifacts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "journal_supercomputing_revision_20260825" / "GNN_RUNTIME_ACCOUNTING_AUDIT.md"
TRAIN = ROOT / "GNNRank-main" / "src" / "train.py"


def test_audit_verdict_b_and_no_rerun():
    text = DOC.read_text()
    assert "EXISTING_EVIDENCE_PARTIAL_BUT_MANUSCRIPT_CAN_QUALIFY" in text
    assert "NO GNN RERUN" in text
    assert "not** inference-only" in text or "not inference-only" in text.lower()


def test_train_py_documents_gnn_training_timer():
    text = TRAIN.read_text()
    assert "GNN_METHOD_TIMEOUT" in text
    assert "t_gnn_start" in text
    assert "DEFAULT_METHOD_TIMEOUT" in text
