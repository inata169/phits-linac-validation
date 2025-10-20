# PHITS 医療用リニアック線量評価ツール

このプロジェクトは、モンテカルロ計算コード PHITS の出力（.out）と実測データ（CSV）を比較・評価するための Python ツール群を提供します。放射線治療の品質保証（QA）で日常的に行う「計算値と実測値の比較」を研究レベルで実践するための道具です。

-----

## 新しい真値スケーリングCLI（推奨）

PDD重み付けの“真値”スケーリングでOCRを比較する新CLIを提供します。project.md に定義の True(x,z) = PDD_norm(z) × OCR_rel(x,z) を用いて、γ/RMSE を真値スケール上で評価します。

- エントリ: `python src/ocr_true_scaling.py`
- 入力: reference/eval ともに CSV または PHITS `.out`（混在可）
- PDD正規化: 既定 dmax、選択肢 z_ref=10 cm
- OCR中心正規化: x=0 最近傍（±0.05 cm）→無ければ最大値
- 指標: γ（主要 2%/2mm/10%、副次 3%/3mm/10%）、RMSE
- 出力: `output/plots/*.png`, `output/reports/*.txt`, `output/data/*.csv`（必要に応じ）

### 使用例（reference=CSV, eval=PHITS, 深さ10 cm）

```bash
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --cutoff 10 --export-csv --export-gamma
```

オプション（抜粋）
- `--grid <cm>`: RMSE/可視化の共通グリッド刻み（既定: `config.ini` の `[Processing].resample_grid_cm`）
- `--ymin/--ymax`: プロットのY軸範囲
- `--xlim-symmetric`: 横軸を原点対称に設定
- `--legend-ref/--legend-eval`: 凡例ラベルを任意指定
- `--export-csv/--export-gamma`: 真値系列/γ配列をCSVに保存

-----

## 機能概要

- 線量プロファイル比較: PHITS `.out` と実測 `.csv` を読み込み比較
- 前処理/補正: スケーリング、Savitzky–Golay による平滑化
- 評価指標: ガンマインデックス（γ-Index）、RMSE
- 自動出力: グラフ（`.png`）/ レポート（`.txt`）/ 比較用CSV（任意）

-----

## 依存関係と実行

- 依存: `python>=3.9`, `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`
- 仮想環境（Windows 例）:
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
  - `pip install -U pip`
  - `pip install pandas numpy matplotlib scipy pymedphys`

-----

## レガシー互換

- 従来の `src/Comp_measured_phits_v9.1.py` はラッパーとなり、実体は `src/Comp_measured_phits_v9_1_legacy.py` に移動しました。

-----

## 出力先

- 図: `output/plots/TrueComp_... .png`
- レポート: `output/reports/TrueReport_... .txt`
- 真値/再サンプル/γ配列: `output/data/*.csv`（`--export-csv`, `--export-gamma` 指定時）

-----

## ライセンス

MIT ライセンス


-----

## 補足: 絶対比較とFWHMチェック

- 絶対（真値）比較に寄せたい場合、eval 側 PDD は PHITS の `deposit-z-water.out` を指定してください（ref 側は測定PDD）。
- OCR の照射野はPHITSのファイル名からは直接分からないため、FWHMで幅整合を確認するのが有効です。
- CLIオプション `--fwhm-warn-cm <cm>` を用いると、実行時に相対OCRから推定した FWHM(ref/eval) の |Δ| が閾値を超えた場合に stderr へ警告を出します（既定 1.0 cm）。レポートにも FWHM(ref/eval) と Δ を追記します。
- 事前に幅を数値確認したい場合は `scripts/compute_fwhm.py` を利用してください。
- 参考Rev（経験則）: 5×5→`Rev80-5x5-...`（または `Rev60-5x5-...`）、10×10→`Rev70-c8-0.49n`、30×30→`Rev50-30x30--c8-0.49n`。

### 追加オプション（中心正規化の調整）
- `--center-tol-cm <cm>`: x=0 近傍と見なす許容範囲（既定 0.05 cm）。原点近傍サンプルが粗い場合のロバスト化に有効。
- `--center-interp`: x=0 にサンプルが無い場合に線形補間で x=0 の値を推定し、中心正規化の基準に使用（無指定時は最大値代用）。
