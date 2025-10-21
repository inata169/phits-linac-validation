# Known Limitations

- Scope is 1D profile comparison (OCR/PDD). No 2D/3D gamma here.
- PHITS parser reads the last `[ T-Deposit ]` block only and expects xyz mesh tables. Non-standard outputs may fail.
- OCR depth inference prefers header y-slab centre; filename inference requires suffix like `...-200x.out` (200 → 20.0 cm). Other naming schemes are not parsed.
- Type auto-correction is extension-based (e.g. `.out` → PHITS). Mislabelled files without standard extensions may not be detected.
- Gamma uses `pymedphys.gamma`; large arrays or very fine grids can be slow and memory hungry. Keep `--grid` sensible (e.g. 0.1 cm).
- Local gamma is more sensitive to low-dose regions; results can vary with smoothing/cutoff settings. Use `--cutoff` and smoothing judiciously.
- CSV loader attempts whitespace fallback when standard CSV read fails; exotic encodings or mixed delimiters might still require manual cleanup.
- Plots are generated via Matplotlib; font availability may affect Unicode rendering. We use ASCII-only for critical strings to avoid mojibake on Windows.
- Line endings are CRLF on Windows by convention; editing on Unix may change them unless configured.

