# Proposal: Add PDD Report/Plot and Gamma Mode (global/local)

## Summary
- Add PDD comparison report and plot alongside OCR true-scaling comparison.
- Add `--gamma-mode {global,local}` to control gamma normalisation mode (default: global).
- Surface both options in the GUI (gamma combobox, PDD report suppression checkbox).
- Include gamma-mode in report Params and plot title/legend for traceability.

## Motivation
- PDD GPR is a useful independent check to ensure depth-axis consistency and normalisation before OCR evaluation.
- Global vs Local gamma is a common clinical requirement; both should be supported with a clear default.

## Non-goals
- No change to legacy scripts or external interfaces beyond the new CLI flag and GUI controls.
- No change to existing default gamma criteria or smoothing behaviour.

## Affected Areas
- CLI: `src/ocr_true_scaling.py`
- GUI: `scripts/run_true_scaling_gui.ps1`, defaults at `config/true_gui_defaults.json`
- Docs: README/AGENTS

