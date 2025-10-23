Changelog

All notable changes to this project are documented here.

v0.2.2 - 2025-10-23

- Docs: README/examples/dependency_check をUTF-8日本語で整備、SHA256検証手順を追記。
- CI: Windows/Ubuntu 安定化（pip cache path, prefer-binary, PIP_DISABLE_PIP_VERSION_CHECK）。
- CI: Python 3.9 で `pymedphys==0.40.*`、>=3.10 で `0.41.*` を利用するよう環境マーカーを導入。
- Release: EXE を -V でスモーク実行、バージョン付きファイル名と SHA256 を添付、.ps1 をASCII安全化。
- Release: タグ名と `__version__` の整合をワークフローで検証。

v0.2.1 - 2025-10-23

- CLI: add `-V/--version` (reports tool version; 0.2.1).
- Docs: README quickstart + Windows EXE usage note; OpenSpec aligned with v0.2.1 and documented `--version`.
- CI: headless stability (MPLBACKEND=Agg, UTF-8); pip cache via requirements.txt; Windows fixes by adding `numba`, `llvmlite`, `interpolation`.
- Release: GitHub Actions workflow to build Windows EXE and upload to Release on tag/release.

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
