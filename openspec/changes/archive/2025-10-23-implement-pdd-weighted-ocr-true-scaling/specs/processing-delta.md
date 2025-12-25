## ADDED Requirements: PDD-weighted True Scaling

#### Requirement: PDD normalization
- Default PDD normalization MUST be dmax=1.00.
- It MUST support z_ref=10 cm normalization as an option.

#### Scenario: z_ref normalization
- Given z_ref=10 cm
- When PDD is normalized
- Then PDD_norm(10 cm) = 1.00.

#### Requirement: OCR center normalization
- The OCR center at x=0 MUST be normalized to 1.00.
- If x=0 sample is missing, use nearest sample within ±0.05 cm; else use max.

#### Requirement: True series construction
- The tool MUST compute S_axis(z) = PDD_norm(z) at each OCR depth z.
- It MUST compute True(x,z) = S_axis(z) * OCR_rel(x,z).

#### Requirement: Optional resampling for RMSE/plots
- If configured, the tool SHOULD resample both series on a common x grid for RMSE/plots using `resample_grid_cm`.

