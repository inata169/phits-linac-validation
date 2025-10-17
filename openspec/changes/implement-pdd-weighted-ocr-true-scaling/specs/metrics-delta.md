## ADDED Requirements: Metrics on True-Scaled Profiles

#### Requirement: RMSE on true-scaled profiles
- RMSE MUST be computed on True(x,z) profiles at matched depths.

#### Requirement: Gamma on true-scaled profiles
- Primary γ criteria MUST be DD=2%, DTA=2 mm, Cutoff=10%.
- Secondary γ criteria MUST be reported for DD=3%, DTA=3 mm, Cutoff=10%.

#### Scenario: Dual gamma reporting
- Given true-scaled reference/eval OCR at depth z
- When computing γ
- Then results include pass rates for 2%/2mm/10% and 3%/3mm/10%.

