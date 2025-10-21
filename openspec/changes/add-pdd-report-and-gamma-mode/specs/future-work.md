# Future Extensions

- Add gamma/ RMSE annotations onto plots (OCR and PDD) as subtitles.
- Include `gamma-mode` in output filenames (e.g., `_gamma-global`) for quicker triage.
- Batch runner to evaluate multiple depths/fields and summarise to a single CSV/MD.
- Export machine-readable summaries (CSV/JSON/MD) for both OCR and PDD in a unified schema.
- Robust PHITS parsing for alternative tally formats; explicit axis detection from headers.
- Option to fix eval depth to ref depth (override) for sensitivity tests.
- Optional denoising filters (e.g., moving average) in addition to Savitzky–Golay.
- UI: add quick presets for gamma-mode + criteria (2%/2mm global, 3%/3mm local, etc.).
- Validation: unit tests for FWHM/centre-normalisation and PHITS depth inference using small fixtures.

