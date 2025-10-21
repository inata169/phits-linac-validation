# IO Delta: Files and Naming

## OCR Comparison
- Plot: `TrueComp_{refOCR}_vs_{evalOCR}_norm-{norm}_zref-{zref}_z-{zrefcm}-{zevalcm}.png`
  - Title: `True-scaling (PDD-weighted) [gamma: <mode>]` on first line
  - Legend title: `gamma-mode: <mode>`
- Report: `TrueReport_{...}.txt`
  - Params include: `norm-mode`, `z_ref`, `gamma-mode`, depths, `S_axis(...)`, `grid`
  - Results include: `RMSE`, `Gamma 1/2`, `FWHM(ref/eval/delta)`

## PDD Comparison
- Plot: `PDDComp_{refPDD}_vs_{evalPDD}_norm-{norm}_zref-{zref}.png`
  - Title includes `[gamma: <mode>]`
- Report: `PDDReport_{refPDD}_vs_{evalPDD}_norm-{norm}_zref-{zref}.txt`
  - Includes RMSE and Gamma 1/2

## Output Root
- Determined by `--output-dir` if provided; otherwise `${repo}/output`.
- Subfolders: `plots/`, `reports/`, `data/` (created if missing).

