## MODIFIED Requirements: Inputs/Outputs for OCR True Scaling

#### Requirement: Accept symmetric reference/eval sources
- Both reference and eval MUST accept CSV or PHITS .out for PDD and OCR.

#### Scenario: Mixed source comparison
- Given reference PDD+OCR from CSV and eval PDD+OCR from PHITS
- When true scaling is requested
- Then the tool constructs True(x,z) for both and compares γ/RMSE.

#### Requirement: Normalized units
- Positions MUST be treated as cm at the I/O boundary.
- Dose values MUST be normalized to [0,1] prior to true scaling.

