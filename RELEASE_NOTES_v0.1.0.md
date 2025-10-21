Release v0.1.0

Date: 2025-10-21

Highlights

- CLI: unify ASCII improvements into main `src/ocr_true_scaling.py`.
  - Robust CSV loader with whitespace fallback
  - Auto type switch CSV→PHITS by extension with stderr warnings
  - PHITS OCR depth inference from header y-slab or filename (…-200z.out → 20.0 cm), fallback to `--z-ref`
  - Report includes FWHM(ref/eval/delta)
- GUI: call main CLI instead of ASCII wrapper
- Messages: ASCII-safe wording for FWHM to avoid mojibake on Windows

How to upgrade

- Pull `main` (or download source ZIP) at tag `v0.1.0`.
- Use GUI via `scripts/run_true_scaling_gui.ps1` or CLI `python src/ocr_true_scaling.py`.

Notes

- Dependencies: python>=3.9, pandas, numpy, matplotlib, scipy, pymedphys
- Data/paths: see `config.ini` and `AGENTS.md`

