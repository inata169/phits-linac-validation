# Proposal: Add Coordinate Shift Options for Analysis Convenience

## Summary
- Add `--eval-z-shift` and `--eval-pdd-z-shift` options to `ocr_true_scaling.py` for coordinate system correction during analysis.
- These options allow shifting PHITS coordinate data to match measurement reference frames without modifying input files.
- Document the new options in README.md with usage examples.

## Motivation
- PHITS simulations may define coordinate origins differently from measurement setups (e.g., water surface position).
- Manual coordinate correction in input files is error-prone and makes reproducibility difficult.
- Providing shift parameters in the analysis tool improves workflow efficiency and traceability.

## Use Cases
- Correcting depth coordinate mismatches between PHITS and measurement data.
- Quick sensitivity analysis by varying coordinate offsets.
- Maintaining original PHITS output files while adjusting analysis parameters.

## Implementation
- `--eval-z-shift <float>`: Shifts evaluation OCR z-coordinates by specified amount (cm). Applied to OCR depth extraction and z-axis data.
- `--eval-pdd-z-shift <float>`: Shifts evaluation PDD z-coordinates by specified amount (cm).
- Both parameters default to 0.0 (no shift).
- Shift values are recorded in report files for reproducibility.

## Non-goals
- No changes to input file formats or parsers beyond applying the shift.
- No GUI changes (CLI-only feature for advanced users).
- No automatic coordinate detection or correction.

## Affected Areas
- CLI: `src/ocr_true_scaling.py` (lines 210-211, 241, 301, 303, 459-461, 501-502, 566-567, 660-661)
- Docs: README.md (lines 17, 44-54, 70)

## Testing & Validation
Users should verify:
1. Shift parameters appear correctly in output reports.
2. PDD and OCR plots reflect the applied coordinate shifts.
3. Gamma pass rates and RMSE values are consistent with shifted coordinates.