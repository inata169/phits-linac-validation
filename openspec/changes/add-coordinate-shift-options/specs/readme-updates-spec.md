# README Updates Specification

## Overview
This specification documents the README.md changes to describe the new coordinate shift functionality.

## Changes

### 1. Feature List Update (Line 17)
**Added**:
```markdown
- 座標系補正: PHITS データの Z 軸オフセット (`--eval-z-shift`, `--eval-pdd-z-shift`)
```

**Translation**: "Coordinate system correction: PHITS data Z-axis offset (`--eval-z-shift`, `--eval-pdd-z-shift`)"

**Purpose**: Inform users of the coordinate correction capability in the feature list.

### 2. Usage Example Addition (Lines 44-54)
**Added Section**:
```markdown
4) 例(座標系補正あり:PHITS の Z 座標を +5 cm シフト)
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv   --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file phits_output/deposit-pdd.out \
  --ref-ocr-type csv    --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits  --eval-ocr-file phits_output/deposit-z-water-100x.out \
  --eval-z-shift 5.0 --eval-pdd-z-shift 5.0 \
  --norm-mode dmax --output-dir output
```
```

**Translation**: "Example 4) With coordinate correction: Shift PHITS Z coordinates by +5 cm"

**Purpose**:
- Provide a concrete example of coordinate shift usage.
- Show that both shift parameters can be used together.
- Demonstrate typical use case (aligning PHITS and measurement coordinate systems).

**Note**: The example shows identical shift values (5.0 cm) for both PDD and OCR, which is a common scenario when the entire coordinate system needs alignment.

### 3. Troubleshooting Section Update (Line 70)
**Added Bullet**:
```markdown
- 深さ: レポートの `ref depth / eval depth` と `S_axis(ref/eval)` を確認(一致が前提)
  - PHITS の座標定義(水表面位置)が実測と異なる場合、`--eval-z-shift 5.0` 等で補正可能
```

**Translation**:
"- Depth: Check `ref depth / eval depth` and `S_axis(ref/eval)` in report (should match)
  - If PHITS coordinate definition (water surface position) differs from measurement, use `--eval-z-shift 5.0` etc. for correction"

**Purpose**:
- Guide users to diagnose coordinate mismatch issues.
- Explain when and how to use the shift parameters.
- Reference common scenario (water surface position differences).

## Documentation Principles

### 1. Clarity
- Use concrete values (e.g., 5.0 cm) rather than placeholders.
- Provide context (why you might need coordinate shifts).
- Show complete command examples, not fragments.

### 2. Accessibility
- Place examples in the "Quick Start" section for visibility.
- Include troubleshooting guidance for common issues.
- Use Japanese language for Japanese documentation sections.

### 3. Completeness
- Cover both OCR and PDD shift parameters.
- Show individual and combined usage.
- Reference related concepts (coordinate systems, water surface).

## User Workflow

### Typical Use Case
1. User runs analysis and notices depth mismatch in report.
2. User checks troubleshooting section and identifies coordinate issue.
3. User refers to Example 4 for shift parameter syntax.
4. User applies appropriate shift values and re-runs analysis.
5. User verifies corrected coordinates in updated report.

### Expected Output
After applying coordinate shifts:
- Report "Params" section shows shift values.
- Plot titles reflect shifted coordinates.
- Gamma pass rates improve if mismatch was the issue.
- Re-run command includes shift parameters for reproducibility.

## Related Documentation
- CLI options spec: [cli-options-spec.md](./cli-options-spec.md)
- Proposal: [proposal.md](../proposal.md)
- Main OpenSpec: `docs/openspec.md` (may need future update)

## Validation
Users should verify:
1. README examples are copy-paste executable (with correct paths).
2. Troubleshooting guidance leads to correct parameter usage.
3. Japanese translation is accurate and clear.
4. Example commands produce expected report output.
