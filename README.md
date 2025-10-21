# PHITS 医療用リニアック線量評価ツール

[![release](https://img.shields.io/github/v/release/inata169/phits-linac-validation?include_prereleases&label=release)](LICENSE)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)

PHITS の出力（.out）と実測 CSV を読み込み、線量プロファイル（PDD/OCR）の比較評価（ガンマ、RMSE）を行うツール群です。推奨フローは PDD を用いた真値スケーリングによる OCR 比較です。

-----

## 仕様（openspec）
- オープン仕様（データ形式、CLI引数、処理フロー、閾値、出力契約、エラー方針）は `docs/openspec.md` を参照してください。
- 実装は `src/ocr_true_scaling.py` の挙動に整合しています（ドラフト）。

-----

## 推奨CLI：真値スケーリング（PDD重み付け）
- エントリ: `python src/ocr_true_scaling.py`
- 真値の構成: `True(x,z) = PDD_norm(z) × OCR_rel(x,z)`
- 入力: reference/evaluation ともに CSV または PHITS `.out` を指定可能
- 正規化: 既定は `dmax`。必要に応じて `--z-ref <cm>` で参照深を指定
- 中心正規化: x=0 近傍 ±0.05 cm を中心値とし、無ければ `--center-interp` で線形補間、それも無ければ最大値を使用
- 出力: `output/plots/*.png`, `output/reports/*.txt`, `output/data/*.csv`
- 例・実行レシピは `docs/examples.md` を参照

例（reference=CSV, eval=PHITS, 深さ10 cm）:
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --cutoff 10 --export-csv --export-gamma \
  --gamma-mode global --fwhm-warn-cm 1.0 \
  --output-dir output \
  --report-json output/data/true_report.json
```

-----

## 絶対比較と FWHM チェック（重要）
- 真値（絶対寄り）の比較を行う場合は、eval 側 PDD に PHITS の `deposit-z-water.out` を指定（ref 側は測定PDD）。
- PHITS OCR の照射野サイズはファイル名から直接判別できないため、FWHMで幅整合を確認。
  - `--fwhm-warn-cm <cm>`（既定 1.0）で FWHM(ref/eval) の |Δ| が閾値超過時に stderr 警告。レポートにも FWHM(ref/eval) と Δ を出力。
  - 事前チェックは `scripts/compute_fwhm.py` を利用可。

-----

## トラブルシューティング（GPR が低い等）
- 深さ: レポートの `ref depth / eval depth` と `S_axis(ref/eval)` が一致していること。
- 幅: FWHM(ref/eval) が許容差内（目安: 5×5=±0.5 cm、10×10=±1.0 cm、30×30=±2.0 cm）。
- 中心正規化: 原点近傍サンプルが無いと最大値正規化にフォールバックし肩が歪むことあり。`--center-interp` を検討。
- 平滑化: `--no-smooth` / `--smooth-window 11 --smooth-order 3` で挙動比較（深部は軽めが無難）。
- カットオフ: `--cutoff 20` で尾部ノイズの影響を抑制。
- ガンマ基準: 診断用途で `--dd1 3 --dta1 3` に切替、`--gamma-mode local` で線量差重視。
- 軸対応: `xXlat` ↔ `...x.out`、`zYlng` ↔ `...z.out` を厳密一致。
- 共通グリッド: `--grid 0.1` はRMSE/可視化安定化に有用（γは元軸で評価）。

-----

## 設定（config.ini）
- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`（RMSE/可視化の共通グリッド刻み、cm。既定 0.1）
- サンプル: `config.ini.example` を複製しローカル環境に合わせて作成。絶対パスは `config.ini` に集約。

-----

## データ仕様（要点）
- 実測 CSV: 2列（`pos_cm`, `dose` 相当）。`utf-8-sig` 推奨。非数は除外し位置でソート、最大で正規化。
- PHITS `.out`: `[ T-Deposit ]` の最終表から1Dプロファイル抽出。位置は bin 中心（cm）、線量は最大で正規化。OCR深さはヘッダ中心またはファイル名 `-<mm>[x|z].out` から推定し、無ければ `--z-ref`。

-----

## 出力
- 図: `output/plots/TrueComp_... .png`
- レポート: `output/reports/TrueReport_... .txt`（Inputs/Params/Results、FWHM要約含む）
- PDDレポート/図: `PDDReport_... .txt`, `PDDComp_... .png`（`--no-pdd-report` で抑止可）
- CSVエクスポート: `output/data/*.csv`（`--export-csv`, `--export-gamma` 時）
- JSONレポート: `--report-json <path>` で機械可読サマリを保存（inputs/params/derived/results）

-----

## インストール/依存
- Python: `>=3.9`
- 依存: `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`
- 手順とチェックは `docs/dependency_check.md` を参照

-----

## ガンマモード（global/local）
- `--gamma-mode {global,local}` で切替。
- global: 参照系列の全体最大値で%差を評価（臨床QAの慣例）。
- local: 局所値で%差を評価（微細差に敏感、厳しめ）。

-----

## ライセンス
MIT License

