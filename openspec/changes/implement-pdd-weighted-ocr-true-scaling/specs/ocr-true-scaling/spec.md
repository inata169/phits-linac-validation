## ADDED Requirements

### Requirement: R1: Symmetric reference/eval inputs
The tool MUST accept reference and eval from CSV or PHITS .out for both PDD and OCR, including mixed-source comparisons.
#### Scenario: Mixed source comparison
Given reference PDD+OCR from CSV and eval PDD+OCR from PHITS
When true scaling is enabled
Then the tool constructs True(x,z) for both sides and compares γ and RMSE

### Requirement: R2: Units and normalization
Positions MUST be treated as cm at I/O boundaries. Dose values MUST be normalized to [0,1] prior to true scaling.
#### Scenario: CSV with unnormalized dose
Given a CSV OCR with arbitrary units
When loaded
Then dose is normalized to [0,1] and center normalization is applied before true scaling

### Requirement: R3: PDD normalization modes
Default PDD normalization MUST be dmax=1.00. An option MUST exist to normalize by z_ref=10 cm (PDD_norm(10 cm)=1.00).
#### Scenario: z_ref normalization
Given z_ref=10 cm
When PDD is normalized
Then PDD_norm at 10 cm equals 1.00 within interpolation tolerance

### Requirement: R4: OCR center normalization
OCR center at x=0 MUST be normalized to 1.00. If x=0 sample is missing, use nearest sample within ±0.05 cm; if none, use max as proxy.
#### Scenario: Missing x=0 sample
Given OCR samples at x=-0.04 cm and x=0.06 cm
When center normalization runs
Then the nearest within ±0.05 cm is selected as center and scaled to 1.00

### Requirement: R5: True series construction
The tool MUST compute S_axis(z) = PDD_norm(z) at each OCR depth via linear interpolation, and compute True(x,z) = S_axis(z) * OCR_rel(x,z) for both reference and eval.
#### Scenario: True scaling at z=10 cm
Given PDD_norm(10)=0.78 and OCR_rel(x,10)
When constructing True(x,10)
Then True(x,10) = 0.78 * OCR_rel(x,10) for all x

### Requirement: R6: Metrics on true-scaled profiles
RMSE MUST be computed on true-scaled profiles at matched depths. γ MUST be computed on true-scaled profiles with primary 2%/2mm/10% and secondary 3%/3mm/10% criteria reported.
#### Scenario: Dual gamma reporting
Given true-scaled reference/eval OCR at depth z
When computing γ
Then pass rates for 2%/2mm/10% and 3%/3mm/10% are both reported

### Requirement: R7: Optional resampling for RMSE/plots
If configured via resample_grid_cm, the tool MUST resample both series to a common x grid for RMSE and plotting stability.
#### Scenario: Resampling enabled
Given resample_grid_cm=0.1
When computing RMSE
Then both profiles are interpolated to a 0.1 cm common grid over their overlapping x-range before RMSE
