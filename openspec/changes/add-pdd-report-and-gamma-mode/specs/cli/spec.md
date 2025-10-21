# CLI Spec: PDD Report/Plot and Gamma Mode

## New Options
- `--gamma-mode {global,local}`
  - Default: `global`
  - Implementation: `pymedphys.gamma(local_gamma=(mode=='local'), global_normalisation=max(ref))`
  - Evaluated on true-value series (absolute scale), not pre-normalised percent arrays.

- `--no-pdd-report`
  - Default: disabled (PDD report/plot is generated)
  - When set, PDD comparison report and plot are not generated.

## Existing Behaviour (unchanged)
- True-scaling: `True(x,z) = PDD_norm(z) * OCR_rel(x,z)`
- Normalisation: `--norm-mode {dmax,z_ref}` with `--z-ref` as needed
- Center normalisation: `--center-tol-cm`, `--center-interp`
- Smoothing: Savitzky-Golay by `--smooth-window`, `--smooth-order` (unless `--no-smooth`)
- Grid for RMSE/visual: `--grid` or `[Processing].resample_grid_cm` (fallback 0.1 cm)
- FWHM check: `--fwhm-warn-cm <cm>` -> stderr warning; FWHM(ref/eval/delta) written to OCR report
- Depth inference for PHITS OCR: header y-slab (preferred) → filename `...-200x.out` → fallback `--z-ref`
- Type auto-correction: `.out` with `--*-type csv` switches to `phits` with stderr warning

## Outputs
- OCR comparison
  - Plot: `output/plots/TrueComp_{refOCR}_vs_{evalOCR}_norm-{norm}_zref-{zref}_z-{zrefcm}-{zevalcm}.png`
    - Title includes `[gamma: <mode>]`
    - Legend title `gamma-mode: <mode>`
  - Report: `output/reports/TrueReport_{...}.txt`
    - Params include `gamma-mode: <mode>`
    - Results include RMSE, Gamma1/2, FWHM(ref/eval/delta)

- PDD comparison (unless `--no-pdd-report`)
  - Plot: `output/plots/PDDComp_{refPDD}_vs_{evalPDD}_norm-{norm}_zref-{zref}.png`
  - Report: `output/reports/PDDReport_{refPDD}_vs_{evalPDD}_norm-{norm}_zref-{zref}.txt`
    - Includes RMSE and Gamma1/2 computed on PDD curves

