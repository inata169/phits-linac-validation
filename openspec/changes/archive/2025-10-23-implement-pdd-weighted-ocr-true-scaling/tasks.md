## Tasks

- [x] Input plumbing
  - [x] Accept PDD and OCR from CSV or PHITS for both reference and eval.
  - [x] Ensure units: position in cm, dose normalized to [0,1].

- [x] Normalization
  - [x] PDD: dmax=1.00 (default), option z_ref=10 cm.
  - [x] OCR: center x=0 => 1.00; if absent, nearest within +/-0.05 cm, else use max.

- [x] True scaling
  - [x] Compute S_axis(z) = PDD_norm(z) via interpolation at OCR depths.
  - [x] Build True(x,z) = S_axis(z) * OCR_rel(x,z) for both sides.

- [x] Comparison
  - [x] RMSE on true-scaled profiles; optional resample to common grid (config `[Processing].resample_grid_cm`).
  - [x] Gamma on true-scaled profiles with primary 2%/2mm/10% and secondary 3%/3mm/10%.

- [x] Outputs
  - [x] Plots and reports clearly labeled as PDD-weighted true scaling with parameters (norm-mode, z_ref, criteria).
  - [x] CSV export for true series and per-point gamma (optional).

- [x] Wiring & flags
  - [x] Minimal CLI/config to select norm-mode and provide PDD sources for both reference and eval.
  - [x] Backward-compatible legacy wrapper and documentation updates (AGENTS).

