import os
import sys
import subprocess


def test_cli_version_flag_exits_zero_and_prints_version():
    repo_root = os.path.abspath(os.getcwd())
    py = sys.executable
    script = os.path.join(repo_root, "src", "ocr_true_scaling.py")

    proc = subprocess.run([py, script, "-V"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = (proc.stdout or "") + (proc.stderr or "")
    # Expect something like: "ocr_true_scaling.py 0.2.1"
    assert "0." in out or "1." in out

