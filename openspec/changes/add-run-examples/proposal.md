## Change-ID
add-run-examples

## Summary
Add runnable examples: simple batch script(s) and a Jupyter notebook demonstrating PDD-weighted true scaling OCR comparison, producing plots/reports/CSVs reproducibly.

## Why
Concrete, copy-pasteable examples reduce onboarding friction and help verify outputs match expectations.

## What Changes
- Add `scripts/` with Windows `.bat` (and optional `.ps1`) to run a representative comparison.
- Add `notebooks/ocr_true_scaling_demo.ipynb` to walk through loading data, building True(x,z), and computing γ/RMSE.
- Document expected outputs and where files are written.

