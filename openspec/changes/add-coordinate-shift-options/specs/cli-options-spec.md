# CLI Options Specification: Coordinate Shift Parameters

## Overview
This specification defines two new command-line options for coordinate system correction in `ocr_true_scaling.py`.

## New Parameters

### `--eval-z-shift`
- **Type**: `float`
- **Default**: `0.0`
- **Unit**: cm
- **Description**: Shifts evaluation OCR z-coordinates by the specified amount.
- **Behavior**:
  - Applied to OCR depth extraction when reading PHITS files (line 301).
  - Applied to z-axis coordinate data when axis is 'z' (line 303).
  - Does not affect reference data.
- **Usage Example**:
  ```bash
  --eval-z-shift 5.0  # Shift evaluation coordinates +5 cm
  ```

### `--eval-pdd-z-shift`
- **Type**: `float`
- **Default**: `0.0`
- **Unit**: cm
- **Description**: Shifts evaluation PDD z-coordinates by the specified amount.
- **Behavior**:
  - Applied to PDD position array after loading (line 241).
  - Independent from `--eval-z-shift`.
  - Does not affect reference PDD.
- **Usage Example**:
  ```bash
  --eval-pdd-z-shift 5.0  # Shift evaluation PDD depth +5 cm
  ```

## Implementation Details

### Code Changes

#### Argument Parser (lines 210-211)
```python
ap.add_argument('--eval-z-shift', type=float, default=0.0)
ap.add_argument('--eval-pdd-z-shift', type=float, default=0.0)
```

#### PDD Shift Application (line 241)
```python
z_eval_pos = z_eval_pos + args.eval_pdd_z_shift
```

#### OCR Depth Shift (line 301)
```python
z_depth_eval = z_depth_eval + args.eval_z_shift
```

#### OCR Coordinate Shift (lines 302-303)
```python
if axis == 'z':
    x_eval = x_eval + args.eval_z_shift
```

### Report Integration

#### Text Report (lines 459-461)
```python
if args.eval_z_shift != 0 or args.eval_pdd_z_shift != 0:
    f.write(f"eval-z-shift: {args.eval_z_shift} cm, eval-pdd-z-shift: {args.eval_pdd_z_shift} cm\n")
```

#### Re-run Command (lines 501-502, 660-661)
Both text report and PDD report include shift parameters in the re-run command:
```python
'--eval-z-shift', str(args.eval_z_shift),
'--eval-pdd-z-shift', str(args.eval_pdd_z_shift),
```

#### JSON Report (lines 566-567)
```python
'eval_z_shift': float(args.eval_z_shift),
'eval_pdd_z_shift': float(args.eval_pdd_z_shift),
```

## Validation

### Expected Behavior
1. When both parameters are 0.0 (default), no coordinate shifts occur.
2. Positive values shift coordinates in the positive direction.
3. Negative values shift coordinates in the negative direction.
4. Shift parameters are independent and can be set separately.

### Test Cases
1. **No shift (default)**:
   - Command: `... --eval-z-shift 0.0 --eval-pdd-z-shift 0.0`
   - Expected: Original coordinates unchanged.

2. **OCR shift only**:
   - Command: `... --eval-z-shift 5.0`
   - Expected: OCR depth and z-axis coordinates shifted +5 cm, PDD unchanged.

3. **PDD shift only**:
   - Command: `... --eval-pdd-z-shift 3.0`
   - Expected: PDD coordinates shifted +3 cm, OCR unchanged.

4. **Both shifts**:
   - Command: `... --eval-z-shift 5.0 --eval-pdd-z-shift 5.0`
   - Expected: Both OCR and PDD coordinates shifted +5 cm.

5. **Negative shift**:
   - Command: `... --eval-z-shift -2.5`
   - Expected: OCR coordinates shifted -2.5 cm.

## Documentation Requirements

### README.md Updates
1. Feature list: Mention coordinate shift capability.
2. Usage examples: Show common shift scenarios.
3. Troubleshooting: Explain when coordinate shifts are needed.

### Report Output
All reports must include:
- Shift parameter values in "Params" section (when non-zero).
- Shift parameters in re-run command for reproducibility.
- Shift values in JSON output for automation.

## Backwards Compatibility
- Fully backward compatible.
- Existing commands without shift parameters behave identically (default 0.0).
- No changes to file formats or core algorithms.

## Future Considerations
- Could extend to x/y coordinate shifts if needed.
- Could add reference data shift options (currently only eval side).
- Could validate shift against physical constraints (e.g., warning for unreasonable values).
