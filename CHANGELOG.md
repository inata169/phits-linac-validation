Changelog

All notable changes to this project are documented here.

v0.2.0 - 2025-10-21

- Docs: 新規 `docs/openspec.md`（オープン仕様ドラフト）、`docs/examples.md`（実行例）、`docs/dependency_check.md`（依存導入）。
- CLI: `--report-json` を追加。入力/パラメータ/派生値（深さ、S_axis、FWHM）/結果（RMSE、GPR、出力パス）をJSON保存。
- CLI: TrueReportに「再実行用コマンドライン」を追記（再現性向上）。
- Tests: パーサ単体＋CLIスモークテストを追加（`pytest`）。
- Repo: `.gitattributes` で `*.csv`/`*.txt` を CRLF 固定、READMEの文字化け解消と構成整理。
- CI: GitHub Actions（Windows/Ubuntu×Python 3.9/3.11）でpytestを実行。

v0.1.0 - 2025-10-21

- CLI: unify ASCII improvements into main `src/ocr_true_scaling.py`.
  - Robust CSV loader with whitespace fallback
  - Auto type switch CSV→PHITS by extension, with stderr warnings
  - PHITS OCR depth inference from header y-slab or filename (…-200z.out → 20.0 cm), fallback to `--z-ref`
  - Report now includes FWHM(ref/eval/delta) values
- GUI: call main `src/ocr_true_scaling.py` instead of ASCII wrapper for consistency
- Usability: FWHM warning/report messages use ASCII-safe wording to avoid mojibake on Windows
- Existing options supported end-to-end via GUI and CLI:
  - `--center-tol-cm`, `--center-interp`, `--fwhm-warn-cm`, `--output-dir`

v0.1.1 - 2025-10-21

- CLI: add `--gamma-mode {global,local}`; compute gamma via pymedphys with proper `local_gamma`/`global_normalisation`; include gamma-mode in report Params and plot title/legend.
- CLI: add PDD comparison report and plot (default ON); `--no-pdd-report` to suppress.
- GUI: add Gamma combobox (global/local) and checkbox "PDD GPR レポートなし"; persist `gamma_mode`/`no_pdd_report` in defaults JSON.
- Docs: README/AGENTS updated for gamma-mode; add openspec specs (proposal, CLI/GUI spec, IO delta, metrics, validation, limitations, future-work, examples).
