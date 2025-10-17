## Change-ID
plan-dicom-rt-support-spec

## Summary
Define specifications to support DICOM-RT (RTDOSE/RTPLAN/RTSTRUCT) based profile extraction and comparison, enabling PDD/OCR generation from 3D dose grids and γ evaluation.

## Why
Extending from 1D/PHITS to clinical DICOM-RT data enables broader validation and bridges to TPS-level QA workflows.

## What Changes
- Add specs describing input handling (RTDOSE 3D dose, spacing/units), coordinate alignment (PLAN/STRUCT), profile extraction (PDD/OCR), and metrics (1D/2D/3D γ).
- No implementation in this change; specs only.

