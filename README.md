# PHITS 医療用リニアック線量評価ツール

[![release](https://img.shields.io/github/v/release/inata169/phits-linac-validation?include_prereleases&label=release)](https://github.com/inata169/phits-linac-validation/releases/latest)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)

日本語の仕様書: docs/manual_ja.md

PHITS の出力（`.out`）と実測 CSV を読み込み、線量プロファイル（PDD/OCR）の比較（ガンマ、RMSE）を行うツール群です。推奨フローは PDD を用いた「真値スケーリング」による OCR 比較です。

---

## 主な機能
- PDD/OCR の入力に CSV と PHITS `.out` を対称に対応（自動型判定あり）
- OCR の中心正規化、任意の平滑化（Savitzky–Golay）
- PDD による重み付け（真値スケーリング）で物理的に妥当な比較
- ガンマ（2%/2mm, 3%/3mm）と RMSE の評価、グローバル/ローカル切替
- 図・レポート・CSV（真値/再サンプル/γ）および JSON レポートの出力

詳細仕様は `docs/openspec.md` を参照してください（実装 v0.2.1 と整合）。

---

## クイックスタート
1) 依存導入
```
pip install -r requirements.txt
```
2) 使い方（バージョン表示）
```
python src/ocr_true_scaling.py -V
```
3) 例（reference=CSV, eval=PHITS, 深さ10 cm）
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --gamma-mode global --cutoff 10 \
  --fwhm-warn-cm 1.0 --export-csv --export-gamma \
  --output-dir output --report-json output/data/true_report.json
```

実行レシピは `docs/examples.md` も参照してください。

---

## 絶対比較と FWHM チェック（重要）
- 絶対寄りの比較では eval 側 PDD に PHITS の `deposit-z-water.out` を指定（ref 側は測定 PDD）
- PHITS OCR の照射野サイズはファイル名から直接判別しにくいため、FWHM(ref/eval) の差で整合確認
  - `--fwhm-warn-cm <cm>`（既定 1.0）で差が閾値を超えると警告・レポート出力
  - 事前チェックは `scripts/compute_fwhm.py` が便利

---

## トラブルシューティング（GPRが低い等）
- 深さ: レポートの `ref depth / eval depth` と `S_axis(ref/eval)` を確認（一致が前提）
- 幅: FWHM(ref/eval) を確認（5×5:±0.5 cm、10×10:±1.0 cm、30×30:±2.0 cm 目安）
- 中心正規化: 原点近傍サンプル不足時は `--center-interp` や `--center-tol-cm` 調整
- 平滑化: `--no-smooth` または軽め（`--smooth-window 11 --smooth-order 3`）
- カットオフ: `--cutoff 20` で尾部ノイズを抑制
- ガンマ基準: 線量差重視は `--gamma-mode local`、通常は `global`
- 共通グリッド: `--grid 0.1` は RMSE/可視化の安定化に有効（γは元軸で評価）

---

## 設定（config.ini）
- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`（RMSE/可視化の共通グリッド刻み、cm）
- サンプル: `config.ini.example`。絶対パスは `config.ini` に集約

---

## データ仕様（要点）
- 実測 CSV: 2列（`pos_cm`, `dose` 相当、`utf-8-sig` 推奨）。最大で正規化、位置でソート
- PHITS `.out`: `[ T-Deposit ]` 最終ブロックの1Dを抽出。位置は bin 中心（cm）、線量は最大で正規化。OCR深さはヘッダ/ファイル名/`--z-ref` の順で決定

---

## 出力
- 図: `output/plots/TrueComp_... .png`
- レポート: `output/reports/TrueReport_... .txt`（Inputs/Params/Results、FWHM含む）
- PDDレポ/図: `PDDReport_... .txt`, `PDDComp_... .png`（`--no-pdd-report` で抑止）
- CSV: `output/data/*.csv`（`--export-csv`, `--export-gamma`）
- JSON: `--report-json <path>`（機械可読サマリ）

---

## Windows 用実行ファイル（EXE）
- 最新版のダウンロード: https://github.com/inata169/phits-linac-validation/releases/latest
- 起動テスト: ダウンロード後に `ocr_true_scaling-<version>-windows-x64.exe -V` を実行
- 整合性チェック（SHA256）:
  - PowerShell:
    ```
    $exe = 'ocr_true_scaling-<version>-windows-x64.exe'
    $sha = Get-FileHash -Algorithm SHA256 $exe
    $ref = (Get-Content "$exe.sha256").Split()[0]
    if ($sha.Hash -eq $ref) { 'OK' } else { throw 'SHA256 mismatch' }
    ```
  - Linux/macOS:
    ```
    sha256sum -c <(sed "s#^#$PWD/#" "$exe.sha256")
    ```

---

## ライセンス
MIT License
