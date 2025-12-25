# Implementation Tasks: Coordinate Shift Options

## Status: COMPLETED

## Overview
Add coordinate shift options to analysis tool for convenient coordinate system correction.

## Completed Tasks

### 1. CLI Implementation ✓
- [x] Add `--eval-z-shift` argument (line 210)
- [x] Add `--eval-pdd-z-shift` argument (line 211)
- [x] Apply PDD shift to evaluation data (line 241)
- [x] Apply OCR depth shift (line 301)
- [x] Apply OCR coordinate shift for z-axis (lines 302-303)

### 2. Report Integration ✓
- [x] Add shift parameters to text report output (lines 459-461)
- [x] Include shifts in re-run command (lines 501-502, 660-661)
- [x] Add shifts to JSON report (lines 566-567)

### 3. Documentation ✓
- [x] Update README.md feature list (line 17)
- [x] Add usage example with coordinate shift (lines 44-54)
- [x] Add troubleshooting guidance (line 70)
- [x] Create OpenSpec proposal document
- [x] Create CLI options specification
- [x] Create README updates specification

### 4. Version Control ✓
- [x] Stage modified files (src/ocr_true_scaling.py, README.md)
- [x] Create OpenSpec change documentation
- [x] Ready for commit

## Implementation Notes

### Code Changes Summary
**File**: `src/ocr_true_scaling.py`
- Added two float arguments with default value 0.0
- Applied shifts at appropriate locations in data processing pipeline
- Preserved all shift values in output reports for traceability

**File**: `README.md`
- Added feature description in Japanese
- Provided practical usage example with 5 cm shift
- Enhanced troubleshooting section with coordinate correction guidance

### Design Decisions
1. **Eval-only shifts**: Only evaluation data is shifted, keeping reference data unchanged.
   - Rationale: Reference is typically measurement data with known coordinates.

2. **Separate PDD/OCR shifts**: Independent parameters for maximum flexibility.
   - Rationale: Allows correction of depth vs. lateral coordinate mismatches independently.

3. **Default 0.0**: No shift by default for backward compatibility.
   - Rationale: Existing workflows remain unchanged.

4. **Report all shifts**: Always include shift values in reports, even if zero.
   - Rationale: Complete traceability for reproducibility (implemented as conditional output).

### Testing Performed
- Manual verification of argument parsing
- Confirmation of shift application in data loading
- Validation of report output formatting

## Next Steps (if needed)
- [ ] Add GUI support for shift parameters (future enhancement)
- [ ] Consider automatic coordinate detection (future research)
- [ ] Extend to x/y shifts if use cases emerge (future enhancement)

## Related Files
- Implementation: `src/ocr_true_scaling.py`
- Documentation: `README.md`
- Proposal: `openspec/changes/add-coordinate-shift-options/proposal.md`
- Specs:
  - `openspec/changes/add-coordinate-shift-options/specs/cli-options-spec.md`
  - `openspec/changes/add-coordinate-shift-options/specs/readme-updates-spec.md`

## References
- PHITS manual (coordinate system definitions)
- pymedphys gamma analysis documentation
- Project coding standards
