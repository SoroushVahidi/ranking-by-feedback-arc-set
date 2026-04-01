import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase_toggle_defaults_are_true():
    src = (ROOT / "src/ours_mfas.py").read_text()
    assert "enable_phase_b: bool = True" in src
    assert "enable_phase_c: bool = True" in src

    comp = (ROOT / "src/comparison.py").read_text()
    assert "enable_phase_b: bool = True" in comp
    assert "enable_phase_c: bool = True" in comp


def test_phase_ablation_runner_executes_or_blocks_cleanly():
    cmd = [sys.executable, "scripts/paper/run_phase_ablation.py"]
    subprocess.check_call(cmd, cwd=str(ROOT))

    out_csv = ROOT / "outputs/ablation/phase_ablation_results.csv"
    assert out_csv.exists()
    rows = list(csv.DictReader(out_csv.open()))
    assert rows, "ablation CSV should have at least one row"
    assert rows[0]["status"] in {"ok", "blocked"}
