## ADDED Requirements

### Requirement: R1: Accept DICOM-RT inputs
The tool MUST accept RTDOSE as the primary 3D dose source, with optional RTPLAN/RTSTRUCT for geometry and contour context.
#### Scenario: Load RTDOSE
Given a valid RTDOSE file with proper grid spacing and units (Gy)
When loaded
Then the tool reads the 3D dose array and metadata (grid spacing, orientation)

### Requirement: R2: Coordinate alignment
The tool MUST align dose grid coordinates to physical space and provide mapping for extracting axial/beam-axis-aligned profiles.
#### Scenario: Align to isocenter
Given RTPLAN beam geometry
When alignment is computed
Then profile extraction along the beam axis and lateral directions becomes reproducible

### Requirement: R3: Profile extraction (PDD/OCR)
The tool MUST extract PDD (depth along beam axis) and OCR (lateral at specified depths) from the 3D dose grid with linear or cubic interpolation.
#### Scenario: Extract profiles
Given an isocenter and a set of depths (e.g., 5/10/20 cm)
When extracting PDD/OCR
Then 1D arrays of (pos_cm, dose) are returned for each requested depth

### Requirement: R4: Normalization modes
The tool MUST support dmax and z_ref normalization for extracted PDD, and center normalization for OCR as in PHITS workflows.
#### Scenario: z_ref normalization
Given z_ref=10 cm
When PDD is normalized
Then PDD_norm(10 cm)=1.00

### Requirement: R5: Metrics on extracted profiles
The tool MUST compute RMSE and γ on extracted profiles with primary 2%/2mm/10% and secondary 3%/3mm/10% criteria.
#### Scenario: Dual gamma
Given reference/eval profiles at depth z
When computing γ
Then both 2%/2mm/10% and 3%/3mm/10% pass rates are reported

### Requirement: R6: 2D/3D gamma support
The tool MUST support 2D γ on dose planes and SHOULD support 3D γ on dose volumes when inputs and performance allow.
#### Scenario: 3D gamma
Given reference/eval RTDOSE grids with matching spacing
When computing 3D γ
Then a pass rate is reported for the given DD/DTA/Cutoff criteria
