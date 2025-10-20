# PHITS 医療用リニアック線量評価ツール

このプロジェクトは、モンテカルロ計算コード PHITS の出力（.out）と実測 CSV を読み込み、線量プロファイル（PDD/OCR）の比較評価（ガンマ、RMSE）を行うための Python ツール群です。

-----

## 推奨CLI（真値スケーリング）
PDD重み付けの“真値”スケーリングでOCRを比較します。True(x,z) = PDD_norm(z) × OCR_rel(x,z) を構成し、真値スケール上で γ/RMSE を評価します。
- エントリ: `python src/ocr_true_scaling.py`
- 入力: reference/eval ともに CSV または PHITS `.out`（混在可）
- PDD正規化: 既定 `dmax`、選択肢 `z_ref=10 cm`
- OCR中心正規化: x=0 近傍（±0.05 cm）。無ければ補間、さらに無ければ最大値
- 評価: γ（主 2%/2mm/10%、副 3%/3mm/10%）、RMSE
- 出力: `output/plots/*.png`, `output/reports/*.txt`, `output/data/*.csv`

使用例（reference=CSV, eval=PHITS, 深さ10 cm）
```bash
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --cutoff 10 --export-csv --export-gamma
```

主なオプション
- `--grid <cm>`: RMSE/可視化の共通グリッド刻み（既定は `config.ini` の `[Processing].resample_grid_cm`）
- `--ymin/--ymax`: プロットY軸範囲
- `--xlim-symmetric`: 横軸を原点対称に設定
- `--legend-ref/--legend-eval`: 凡例ラベル
- `--export-csv/--export-gamma`: 真値系列・γ配列をCSV出力

-----

## GUI
- 起動: `powershell -ExecutionPolicy Bypass -File scripts/run_true_scaling_gui.ps1`
- 依存が未導入の場合: `pip install pandas numpy matplotlib scipy pymedphys`
- フォームで Ref/Eval の PDD/OCR と出力先を選択し、Run を押下。
- 出力先に `plots/`、`reports/`、`data/` が生成されます。

-----

## 絶対比較とFWHMチェック（重要）
- 真値（絶対寄り）の比較を行う場合は、eval 側 PDD に PHITS の `deposit-z-water.out` を指定（ref 側は測定PDD）。
- PHITS OCR の照射野サイズはファイル名から直接判別できないため、FWHMで幅整合を確認。
  - CLI引数 `--fwhm-warn-cm <cm>`（既定 1.0）で、FWHM(ref/eval) の |Δ| が閾値超過時に警告。
  - 事前チェック: `scripts/compute_fwhm.py` で測定CSVとPHITS `.out` のFWHM比較可。
- 参考Rev（経験則）
  - 5×5 → `Rev80-5x5-...`（または `Rev60-5x5-...`）
  - 10×10 → `Rev70-c8-0.49n`
  - 30×30 → `Rev50-30x30--c8-0.49n`

-----

## トラブルシューティング: 深さ20 cm等でGPRが低い
- 深さ: レポートの `ref depth / eval depth` が一致しているか（本リポはPHITSファイル名 `...-200z.out` 等から深さ推定に対応済）。
- 幅: FWHM(ref/eval) が目安内（5×5=±0.5 cm、10×10=±1.0 cm、30×30=±2.0 cm）。
- 中心正規化: x=0 ±0.05 cm にサンプルが無いと最大値正規化へフォールバック。`--center-interp` で改善。
- 平滑化: `--no-smooth`／`--smooth-window 11 --smooth-order 3` を試す。
- カットオフ: `--cutoff 20` で尾部ノイズ影響を低減。
- ガンマ基準: 診断用に `--dd1 3 --dta1 3` で改善度合い確認。
- 軸対応: `xXlat` ↔ `...x.out`、`zYlng` ↔ `...z.out` を厳密に合わせる。
- 共通グリッド: `--grid 0.1` はRMSE/可視化の安定化に有用。

-----

## 設定（config.ini）
- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`（RMSE/可視化の共通グリッド刻み、cm。既定0.1）
- サンプル: `config.ini.example` をコピーしてローカル環境に合わせて編集。`config.ini` はGit管理対象外。

-----

## データ仕様
- 実測 CSV: `pos_cm`, `dose` の2列相当（BOM付UTF-8可）。[0,1]に正規化して比較。
- PHITS `.out`: `[ T-Deposit ]` 最終ブロックから1Dプロファイル抽出。位置は cm へ、線量は最大で正規化。

-----

## 出力
- 図: `output/plots/TrueComp_... .png`
- レポート: `output/reports/TrueReport_... .txt`
- 真値/再サンプル/γ配列: `output/data/*.csv`（`--export-csv`, `--export-gamma` 指定時）

-----

## ライセンス
MIT License

-----

## よくあるエラーと対処
- 依存が無い（No module named ...）
  - `pip install pandas numpy matplotlib scipy pymedphys`
- PowerShell のスクリプトが実行できない
  - `powershell -ExecutionPolicy Bypass -File scripts\run_true_scaling_gui.ps1`
- レポートの深さが一致しない（z が 20/10 など）
  - PHITS OCR のヘッダに y-slab が無い場合、ファイル名 `...-200z.out` などから 20.0 cm を推定します。推定不可時は `z_ref` にフォールバックするため、ファイル名を確認してください。
- γが極端に低い
  - 深さ/軸が一致しているか、FWHM差が大きくないかを確認。
  - `--cutoff 20`、`--no-smooth` や平滑化パラメータを試す。
  - 位置グリッド差の影響が疑わしい場合は `--grid 0.1` を指定。
