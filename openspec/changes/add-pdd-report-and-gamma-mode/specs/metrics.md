# Metrics Spec

## True Series
- `y_true_ref(x) = PDD_norm_ref(z_ref) * OCR_rel_ref(x)`
- `y_true_eval(x) = PDD_norm_eval(z_eval) * OCR_rel_eval(x)`
- Depths: from PHITS header y-slab center if available; else file name `...-NNNx.out` → `NNN/10` cm; else fallback to `--z-ref`.

## RMSE
- If `--grid` or config `[Processing].resample_grid_cm` yields a valid common grid:
  - Resample both series via linear interpolation over overlap `[xmin,xmax]`, step = grid.
  - `RMSE = sqrt(mean((ref - eval)^2))` on the common grid.
- Else: evaluate eval on ref x-grid for RMSE.

## Gamma
- Computed with `pymedphys.gamma`.
- Inputs are absolute true series (not scaled to 100% first).
- `local_gamma = (mode=='local')`
- `global_normalisation = max(ref)`
- `dose_percent_threshold = DD`, `distance_mm_threshold = DTA`, `lower_percent_dose_cutoff = cutoff`.

## PDD Metrics
- Same RMSE/gamma process applied to PDD curves (normalised by `--norm-mode`).

## FWHM
- Width at half maximum from the relative OCR curves (after center normalisation and optional smoothing).
- Report includes `FWHM(ref)`, `FWHM(eval)`, `FWHM delta (eval-ref)`; stderr warns when `|delta| > --fwhm-warn-cm`.

