Release v0.2.2

Date: 2025-10-23

Highlights

- Docs: Fix mojibake and provide clean Japanese README/examples; add SHA256 verification steps.
- CI: Improve stability (pip cache path, prefer-binary on Windows, disable pip version check); make Python 3.9 use `pymedphys==0.40.*` and >=3.10 use `0.41.*`.
- Release: Build EXE with PyInstaller; smoke-run `-V`; attach versioned EXE and `.sha256`; guard tag vs `__version__`.

How to upgrade

- From source: `pip install -r requirements.txt` then run examples in `docs/examples.md`.
- From Release: download `ocr_true_scaling-v0.2.2-windows-x64.exe` and run `-V`; verify with the provided `.sha256`.

Notes

- For Python 3.9, PyMedPhys 0.40.* is installed; for >=3.10, 0.41.* is used. EXE users do not need Python packages.

