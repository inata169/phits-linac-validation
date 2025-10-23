# PHITS–Measured OCR/PDD Comparison — Open Spec (Draft)

This document defines the open specification for comparing measured CSV profiles and PHITS `.out` outputs using the PDD‑weighted “true scaling” method. It standardises data formats, CLI interface, processing flow, thresholds, outputs, and error policy to enable reproducible analysis across environments.

Status: aligned with `src/ocr_true_scaling.py` v0.2.1 (stable).

## Scope
- Inputs: measured CSV (PDD/OCR), PHITS `.out` (PDD/OCR)
- Metrics: RMSE, Gamma (two criteria, global/local modes), FWHM check
- Processing: PDD normalisation and weighting, OCR center normalisation, optional smoothing, optional resampling grid
- Outputs: plots, reports, data exports (CSV, gamma arrays)

## Data Specification
- Measured CSV
  - Encoding: `utf-8-sig` (BOM allowed)
  - Columns: two numeric columns interpreted as `pos` (cm), `dose` (a.u.)
    - Headerless two columns are allowed.
    - If the first row contains labels with “(cm)”, the first two named columns are used.
  - Sorting: rows are sorted by position; non‑finite values are dropped.
  - Normalisation: values are divided by their maximum (peak=1) on read.
- PHITS `.out`
  - Source: final numeric table under `[ T-Deposit ]` style blocks.
  - Position: bin centers computed as `(lower + upper)/2`; units converted to cm.
  - Dose: raw values normalised by series maximum (peak=1) on read.
  - Depth metadata for OCR: prefer header `# y = (y0 .. y1)` as center; else infer from filename suffix `-<mm>[x|z].out` → depth cm; else fallback to `--z-ref`.

## CLI Interface (ocr_true_scaling)
General:
- `-V` `--version` print tool version and exit.

Required pairs (reference vs evaluation):
- `--ref-pdd-type {csv,phits}` `--ref-pdd-file <path>`
- `--eval-pdd-type {csv,phits}` `--eval-pdd-file <path>`
- `--ref-ocr-type {csv,phits}` `--ref-ocr-file <path>`
- `--eval-ocr-type {csv,phits}` `--eval-ocr-file <path>`

Normalisation and depth:
- `--norm-mode {dmax,z_ref}` (default `dmax`)
- `--z-ref <cm>` reference depth for PDD normalisation and weighting (default `10.0`)

Gamma criteria and mode:
- `--dd1 <percent>` `--dta1 <mm>` (default `2, 2`)
- `--dd2 <percent>` `--dta2 <mm>` (default `3, 3`)
- `--gamma-mode {global,local}` (default `global`)
- `--cutoff <percent>` lower dose cutoff (default `10`)

Preprocessing:
- `--center-tol-cm <cm>` tolerance to treat sample near x=0 as center (default `0.05`)
- `--center-interp` enable linear interpolation to estimate value at x=0 if no sample within tolerance; fallback is peak value
- `--no-smooth` disable Savitzky–Golay smoothing
- `--smooth-window <odd>` window length (default `5`), coerced to odd
- `--smooth-order <int>` polynomial order (default `2`)

Resampling/grid and axis limits:
- `--grid <cm>` resampling step for RMSE and data exports (gamma is evaluated on native axes)
- `--ymin <v>` `--ymax <v>` plot y‑limits
- `--xlim-symmetric` symmetric x‑limits by max(|min|, |max|)

Labelling and outputs:
- `--legend-ref <str>` `--legend-eval <str>` legend labels
- `--fwhm-warn-cm <cm>` warn if |FWHM(eval)−FWHM(ref)| exceeds threshold (default `1.0` cm)
- `--output-dir <dir>` override base output directory (default `<project>/output`)
- `--export-csv` export true‑scaled arrays and resampled arrays
- `--export-gamma` export per‑point gamma on the resampled reference grid (criteria 1)
- `--report-json <path>` export machine‑readable report (inputs, params, derived, results)
- `--no-pdd-report` suppress separate PDD report/plot generation

Autodetection conveniences:
- If `--*-type csv` is given but the path ends with `.out`, type switches to `phits` with a stderr warning; similarly for OCR type detection.

## Processing Flow
1) Load PDD (ref/eval)
   - Read according to type.
   - Normalise per `--norm-mode`:
     - `dmax`: divide by max of series.
     - `z_ref`: divide by value at `--z-ref` (interp); error if ≤0.
2) Load OCR (ref/eval)
   - Read according to type.
   - Determine depth (for reporting/weighting alignment):
     - CSV: try `<...><depth>cm` in filename; else `--z-ref`.
     - PHITS: prefer header center; else filename `-<mm>[x|z].out`; else `--z-ref` with stderr warning.
   - Center normalisation: shift x so closest to 0 becomes origin; scale by center value if within `--center-tol-cm`; else interpolate at 0 if `--center-interp`; else scale by peak.
   - Optional smoothing: Savitzky–Golay on OCR (ref/eval), renormalise peaks to 1 afterwards.
3) True scaling (PDD weighting)
   - Compute scaling factors at each series depth:
     - `S_axis(ref) = PDD_ref(z_depth_ref)`; `S_axis(eval) = PDD_eval(z_depth_eval)` via linear interpolation on the (normalised) PDDs.
   - True‑scaled OCRs: `y_true_ref = S_axis(ref) * OCR_ref_rel`, `y_true_eval = S_axis(eval) * OCR_eval_rel`.
4) Metric evaluation
   - RMSE: by default on a common grid if provided; otherwise on native axes with evaluation interpolated to reference.
     - Grid step priority: `--grid` → `config.ini [Processing].resample_grid_cm` → `0.1` cm.
   - Gamma (criteria 1 and 2): evaluated on native axes using `pymedphys.gamma` with:
     - Percent thresholds: `--dd{1,2}`; distance: `--dta{1,2}` mm; cutoff: `--cutoff` percent.
     - `--gamma-mode global`: global normalisation = max of reference series; `local`: pointwise.
5) FWHM check (OCR width)
   - FWHM computed on center‑normalised OCRs (pre‑weighting). If `|Δ| > --fwhm-warn-cm`, print stderr warning and record values in report.
6) Outputs (see below)

## Thresholds and Defaults
- Gamma criteria defaults: (2%, 2 mm) and (3%, 3 mm)
- Lower dose cutoff: 10%
- Grid step default: 0.1 cm if unspecified and missing in `config.ini`
- FWHM warning threshold: 1.0 cm
- Center tolerance: 0.05 cm
- Smoothing: window=5 (odd‑coerced), order=2

## Outputs (Contract)
Directories (created under base `output` or `--output-dir`):
- Plots: `<out>/plots`
- Reports: `<out>/reports`
- Data: `<out>/data`

Artifacts and filenames:
- OCR true‑scaling plot: `plots/TrueComp_{refBase}_vs_{evalBase}_norm-{mode}_zref-{zref}_z-{zRef}-{zEval}.png`
- OCR report: `reports/TrueReport_{refBase}_vs_{evalBase}_norm-{mode}_zref-{zref}_z-{zRef}-{zEval}.txt`
  - Sections: Inputs, Params, Results
  - Params include: `norm-mode`, `z_ref`, `gamma-mode`, `ref depth`, `eval depth`, `S_axis(ref/eval)`, `grid (cm)`
  - Results include: `RMSE`, `Gamma 1`, `Gamma 2`, `FWHM(ref)`, `FWHM(eval)`, `FWHM delta`
- PDD report (unless `--no-pdd-report`): `reports/PDDReport_{refPDD}_vs_{evalPDD}_norm-{mode}_zref-{zref}.txt`
  - Same structure; RMSE and Gamma over PDD series
- PDD comparison plot (unless `--no-pdd-report`): `plots/PDDComp_{refPDD}_vs_{evalPDD}_norm-{mode}_zref-{zref}.png`
- CSV exports (`--export-csv`):
  - `data/TrueRef_{refBase}_z{zRef}.csv` (`x_cm`, `true_dose`)
  - `data/TrueEval_{evalBase}_z{zEval}.csv`
  - Resampled (if grid active): `data/TrueRefResampled_{refBase}_z{zRef}_grid{step}.csv`, `data/TrueEvalResampled_{evalBase}_z{zEval}_grid{step}.csv`
- Gamma export (`--export-gamma`):
  - `data/Gamma_{refBase}_vs_{evalBase}_z{zRef}-{zEval}.csv` with columns: `x_cm`, `true_ref`, `true_eval_interp`, `gamma` (criteria 1)
 - JSON report (`--report-json`): machine‑readable summary including inputs, params, derived values (depths, S_axis, FWHM), results (RMSE, gamma, artifact paths)

## Config Resolution
- Project root `config.ini` is read if present; `Processing.resample_grid_cm` overrides default grid step when `--grid` is omitted.
- Absolute paths should reside in `config.ini`; scripts resolve relative to project root when possible.

## Error & Warning Policy
- Missing dependencies: stderr message with required packages; process exits with code 1.
- CSV/PHITS parse or normalisation errors raise `ValueError`; messages surface to stderr.
- Type autodetection or depth inference fallbacks emit stderr warnings (e.g., switching to `phits`, using `--z-ref`).
- FWHM: if `|ΔFWHM| > --fwhm-warn-cm`, print a stderr warning and include values in the OCR report.

## Axis & Alignment Notes
- Ensure OCR axes match orientation: measured `xXlat` ↔ PHITS lateral (`...x.out`), measured `zYlng` ↔ PHITS longitudinal (`...z.out`).
- Depth alignment is critical: verify `ref depth / eval depth` and `S_axis(ref/eval)` in reports.

## Examples
- Reference=CSV, Evaluation=PHITS, depth 10 cm, PDD‑weighted true scaling with exports and gamma CSV:
  - `python src/ocr_true_scaling.py --ref-pdd-type csv --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out --ref-ocr-type csv --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out --norm-mode dmax --cutoff 10 --export-csv --export-gamma`

## Troubleshooting Hints
- Low GPR at deep depths:
  - Confirm depth and axis alignment; check report `ref depth / eval depth` and `S_axis` values.
  - Inspect FWHM(ref/eval); ensure differences are within typical tolerances (5×5: ±0.5 cm, 10×10: ±1.0 cm, 30×30: ±2.0 cm). Adjust `--fwhm-warn-cm` or data selection accordingly.
  - Try `--no-smooth` or lighter smoothing (`--smooth-window 11 --smooth-order 3`) for deep tails.
  - Increase cutoff (`--cutoff 20`) to reduce noise impact.
  - Toggle gamma mode: `--gamma-mode local` to emphasise dose differences; default `global` for general QA.
  - Use `--grid 0.1` to stabilise RMSE and plots (gamma remains on native axes).
- Center normalisation pitfalls:
  - If no sample within `±0.05 cm` at x=0, enable `--center-interp` or widen `--center-tol-cm`.

## Versioning & Change Tracking
- This spec is a living document. Changes are tracked under `openspec/changes/` and reflected here as the CLI evolves.
