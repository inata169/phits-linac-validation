import json
import os
import sys
import subprocess

import pytest


def _require_runtime_deps():
    pytest.importorskip("numpy")
    pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    pytest.importorskip("scipy")
    pytest.importorskip("pymedphys")


@pytest.mark.skipif(sys.platform.startswith("win") is False, reason="path quoting differs; run on Windows or adjust paths")
def test_cli_smoke_generates_reports_and_plots(tmp_path):
    _require_runtime_deps()

    repo_root = os.path.abspath(os.getcwd())
    py = sys.executable
    script = os.path.join(repo_root, "src", "ocr_true_scaling.py")

    ref_pdd = os.path.join(repo_root, "test", "measured_csv", "05x05mPDD-zZver.csv")
    eval_pdd = os.path.join(repo_root, "test", "PHITS", "deposit-z-water.out")
    ref_ocr = os.path.join(repo_root, "test", "measured_csv", "05x05m10cm-xXlat.csv")
    eval_ocr = os.path.join(repo_root, "test", "PHITS", "deposit-y-water-100x.out")

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    json_path = out_dir / "report.json"

    cmd = [
        py, script,
        "--ref-pdd-type", "csv", "--ref-pdd-file", ref_pdd,
        "--eval-pdd-type", "phits", "--eval-pdd-file", str(eval_pdd),
        "--ref-ocr-type", "csv", "--ref-ocr-file", ref_ocr,
        "--eval-ocr-type", "phits", "--eval-ocr-file", str(eval_ocr),
        "--norm-mode", "dmax",
        "--cutoff", "10",
        "--export-csv",
        "--report-json", str(json_path),
        "--output-dir", str(out_dir),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    assert "results" in payload and "plot_path" in payload["results"]
    plot_path = payload["results"]["plot_path"]
    report_path = payload["results"]["report_path"]
    assert os.path.exists(plot_path), "plot not created"
    assert os.path.exists(report_path), "report not created"

