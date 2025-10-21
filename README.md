# PHITS 医療用リニアック線量評価ツール

[![release](https://img.shields.io/github/v/release/inata169/phits-linac-validation?include_prereleases&label=release)](https://github.com/inata169/phits-linac-validation/releases)
[![license](https://img.shields.io/github/license/inata169/phits-linac-validation)](LICENSE)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)

PHITS の出力（.out）と実測 CSV を読み込み、線量プロファイル（PDD/OCR）の比較・評価（ガンマ、RMSE）を行う Python ツール群です。

-----

## 推奨CLI: 真値スケーリング（PDD重み付け）
- エントリ: `python src/ocr_true_scaling.py`
- 仕様: True(x,z) = PDD_norm(z) × OCR_rel(x,z) を構成し、真値スケール上で γ/RMSE を評価します。
- 入力: reference/eval ともに CSV または PHITS `.out`（混在可）
- 正規化: 既定 `dmax`、オプション `--z-ref <cm>`
- 中心正規化: x=0 近傍 ±0.05 cm。無ければ補間（`--center-interp`）、さらに無ければ最大値
- 出力: `output/plots/*.png`, `output/reports/*.txt`, `output/data/*.csv`
- レポートには FWHM(ref/eval/delta) も追記されます（ASCII表記）。

### 例（reference=CSV, eval=PHITS, 深さ10 cm）
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --cutoff 10 --export-csv --export-gamma
```

### 主なオプション
- `--grid <cm>`: RMSE/可視化の共通グリッド刻み（既定は `config.ini` の `[Processing].resample_grid_cm`）
- `--ymin/--ymax`: プロットY軸範囲
- `--xlim-symmetric`: 横軸を原点対称に設定
- `--legend-ref/--legend-eval`: 凡例ラベル
- `--export-csv/--export-gamma`: 真値系列/γ配列のCSV出力
- `--center-tol-cm`, `--center-interp`: 中心正規化の許容範囲・補間
- `--fwhm-warn-cm`: FWHM差の警告閾値（cm）
- `--output-dir`: 出力ルート（GUIからも指定されます）

-----

## 絶対比較とFWHMチェック（重要）
- 真値（絶対寄り）の比較を行う場合は、eval 側 PDD に PHITS の `deposit-z-water.out` を指定（ref 側は測定PDD）。
- PHITS OCR の照射野サイズはファイル名から直接判別できないため、FWHMで幅整合を確認。
  - `--fwhm-warn-cm <cm>`（既定1.0）で FWHM(ref/eval) の |delta| が閾値超過時にstderrへ警告。
  - 事前チェック: `scripts/compute_fwhm.py` で測定CSVとPHITS `.out` のFWHM比較。

-----

## トラブルシューティング（深さ20 cm等でGPRが低い）
- 深さ/軸: レポートの `ref depth / eval depth` と `S_axis(ref/eval)` が一致しているか。
- 幅: FWHM(ref/eval) が目安（5×5=±0.5 cm、10×10=±1.0 cm、30×30=±2.0 cm）内。
- 中心正規化: 原点近傍サンプル不足時は最大値正規化へフォールバック。`--center-interp` を試す。
- 平滑化: `--no-smooth` や `--smooth-window 11 --smooth-order 3` を比較。
- カットオフ: `--cutoff 20` で尾部ノイズ影響を低減。
- ガンマ基準: 診断用に `--dd1 3 --dta1 3` を試し、分解能/幾何差の影響を切り分け。
- 軸対応: `xXlat` ↔ `...x.out`、`zYlng` ↔ `...z.out` を厳密に合わせる。
- 共通グリッド: `--grid 0.1` はRMSE/可視化安定化に有用（γは元軸で評価）。

-----

## 設定（config.ini）
- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`（RMSE/可視化の共通グリッド刻み、cm。既定0.1）
- サンプル: `config.ini.example` をコピーしてローカル環境に合わせて編集（`config.ini` はGit管理対象外）

## データ仕様
- 実測 CSV: `pos_cm`, `dose` の2列相当（BOM付UTF-8可）。比較時は[0,1]正規化。
- PHITS `.out`: `[ T-Deposit ]` 最終ブロックから1Dプロファイル抽出。位置は cm、線量は最大で正規化。

## 出力
- 図: `output/plots/TrueComp_... .png`
- レポート: `output/reports/TrueReport_... .txt`
- 真値/再サンプル/γ配列: `output/data/*.csv`（`--export-csv`, `--export-gamma` 指定時）

## GUI
- 起動: `powershell -ExecutionPolicy Bypass -File scripts/run_true_scaling_gui.ps1`
- 依存未導入時: `pip install pandas numpy matplotlib scipy pymedphys`
- フォームで Ref/Eval の PDD/OCR と出力先を選び、Run を押下（出力配下に `plots/`、`reports/`、`data/` が生成）

## 依存ライブラリ
- `python>=3.9`, `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`

## ライセンス
MIT License
