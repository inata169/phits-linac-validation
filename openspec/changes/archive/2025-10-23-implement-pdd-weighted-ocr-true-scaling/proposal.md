## Change-ID
implement-pdd-weighted-ocr-true-scaling

## Summary
Add end-to-end PDD-weighted “true” scaling for OCR comparison as defined in project.md: build True(x,z) = PDD_norm(z) * OCR_rel(x,z) for both reference and eval (CSV or PHITS), then compute γ and RMSE on these true-scaled profiles.

## Why
- Provide physically grounded comparison by weighting OCR with depth-dependent PDD, aligning with clinical QA expectations and project.md goals.

## Rationale
- Current comparisons focus on normalized profiles. Using PDD as depth weight provides more physically meaningful evaluation.

## What Changes
- Add data plumbing and normalization to accept PDD/OCR from CSV or PHITS for both reference and eval.
- Add true-scaling pipeline: PDD normalization (dmax default, z_ref option) and OCR center normalization, then construct True(x,z).
- Compute RMSE and dual γ (2%/2mm/10%, 3%/3mm/10%) on true-scaled profiles.
- Minimal CLI/config additions to select norm-mode and PDD sources.

## Scope
- Inputs: reference/eval from CSV or PHITS .out for both PDD and OCR.
- Processing: PDD normalization (dmax default, z_ref option), OCR center normalization (±0.05 cm nearest or max), construct true series, optional resampling for RMSE/plots.
- Outputs: γ pass rates (2%/2mm primary, 3%/3mm secondary), RMSE, plots/ reports indicating PDD-based true scaling and parameters.

## Non-Goals
- 3D DICOM-RT support (future work), MU absolute dose anchoring.

## Acceptance Criteria
- Builds True(x,z) as per spec for both reference and eval.
- Reports γ(2%/2mm,10%) and γ(3%/3mm,10%) pass rates and RMSE on true-scaled profiles.
- Handles mixed input sources (CSV/PHITS) symmetrically.

