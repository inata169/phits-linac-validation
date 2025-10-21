Changelog

All notable changes to this project are documented here.

v0.1.0 - 2025-10-21

- CLI: unify ASCII improvements into main `src/ocr_true_scaling.py`.
  - Robust CSV loader with whitespace fallback
  - Auto type switch CSV→PHITS by extension, with stderr warnings
  - PHITS OCR depth inference from header y-slab or filename (…-200z.out → 20.0 cm), fallback to `--z-ref`
  - Report now includes FWHM(ref/eval/delta) values
- GUI: call main `src/ocr_true_scaling.py` instead of ASCII wrapper for consistency
- Usability: FWHM warning/report messages use ASCII-safe wording to avoid mojibake on Windows
- Existing options supported end-to-end via GUI and CLI:
  - `--center-tol-cm`, `--center-interp`, `--fwhm-warn-cm`, `--output-dir`

