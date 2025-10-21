Release v0.2.0

Date: 2025-10-21

Highlights

- Open Spec: Added `docs/openspec.md` (data spec, CLI, processing flow, thresholds, outputs, error policy). Added `docs/examples.md` and `docs/dependency_check.md`.
- CLI: New `--report-json <path>` option to export machine-readable reports (inputs/params/derived: depths, S_axis, FWHM; results: RMSE/GPR, artifact paths).
- Reports: TrueReport now appends a reproducible "Re-run" command line.
- Tests: Added parser unit tests and end-to-end CLI smoke test.
- CI: Introduced GitHub Actions (Windows/Ubuntu × Python 3.9/3.11) running pytest.
- Docs: Refreshed README (encoding fixed, links to openspec/examples/deps).
- Repo: `.gitattributes` enforces CRLF for `*.csv` and `*.txt`.

How to upgrade

- Pull `main` (or download source ZIP) at tag `v0.2.0`.
- Install dependencies: `pip install pandas numpy matplotlib scipy pymedphys` (Python >= 3.9).
- Run CLI per examples in `docs/examples.md`, optionally add `--report-json` to integrate with pipelines.

Notes

- Gamma mode `--gamma-mode {global,local}` is supported end-to-end; see openspec for behavior.
- FWHM mismatch warnings are printed to stderr and recorded in reports.
- For absolute-like comparisons, use PHITS `deposit-z-water.out` as eval PDD; verify depths/FWHM in reports.

