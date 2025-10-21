# GUI Spec: Gamma Mode and PDD Report Toggle

## Controls
- Gamma combobox
  - Label: `Gamma`
  - Values: `global`, `local`
  - Default: `global`
  - CLI mapping: `--gamma-mode <value>`
  - Defaults JSON: `gamma_mode: "global"`

- PDD report toggle
  - Checkbox label: `PDD GPR レポートなし`
  - Checked: do not generate PDD report/plot
  - CLI mapping: add `--no-pdd-report` when checked
  - Defaults JSON: `no_pdd_report: false`

## Persistence
- `config/true_gui_defaults.json` keys read on startup and written on Save:
  - `gamma_mode`, `no_pdd_report`
  - Existing keys remain unchanged

