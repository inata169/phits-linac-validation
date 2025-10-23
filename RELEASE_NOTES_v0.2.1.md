Release v0.2.1

Date: 2025-10-23

Highlights

- CLI: `-V/--version` added (current version: 0.2.1).
- Docs: Quickstart and Windows EXE usage guidance added; OpenSpec updated to align with v0.2.1 and document `--version`.
- CI: Improved stability for headless environments (MPLBACKEND=Agg, UTF-8). Enabled pip cache via requirements.txt. Fixed Windows matrix by including `numba`, `llvmlite`, and `interpolation` for PyMedPhys gamma.
- Release: Automated workflow to build Windows EXE on tag/release and upload to GitHub Release.

How to upgrade

- Update from source: `pip install -r requirements.txt`
- Or download the EXE from the GitHub Release (tag v0.2.1) and run `ocr_true_scaling.exe --help`.

Notes

- Gamma evaluation uses PyMedPhys; on Python installs (non-EXE) Windows may require `numba/llvmlite` and `interpolation` per requirements.txt.
- See `docs/openspec.md` for full CLI and processing specification aligned with this release.

