# AGENTS.md — phits-linac-validation

このファイルは、開発者/エージェントが本リポジトリで作業する際の約束事と手順です。スコープはリポジトリ全体です。

## 目的と概要
- PHITS 出力（`.out`）と実測 CSV を読み込み、線量プロファイルの比較・評価（ガンマ、RMSE）を行います。
- 新CLI（推奨）: `src/ocr_true_scaling.py`（PDD重み付けの真値スケーリングで比較）
- レガシー: `src/Comp_measured_phits_v9_1_legacy.py`（従来の比較）。`src/Comp_measured_phits_v9.1.py` は互換ラッパーです。
- 設定: `config.ini`（パス/処理の既定値）。データ: `data/measured_csv/`, `data/phits_output/`。出力: `output/plots/`, `output/reports/`, `output/data/`。

## 実行（ローカル）
- 依存関係: `python>=3.9`, `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`
- 仮想環境（Windows 例）:
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
  - `pip install -U pip`
  - `pip install pandas numpy matplotlib scipy pymedphys`

### 実務メモ: 絶対比較とFWHMチェック（重要）
- 真値（絶対寄り）の比較を行う場合は、eval 側 PDD に PHITS の `deposit-z-water.out` を指定する（ref 側は測定PDD）。
- PHITS OCR の照射野サイズはファイル名からは直接判別できないため、FWHMで幅整合を確認する。
  - 推奨: CLI引数 `--fwhm-warn-cm <cm>`（既定 1.0）を用い、FWHM(ref/eval) の |Δ| が閾値を超えたら stderr 警告を有効化。レポートにも FWHM(ref/eval) と Δ を出力。
  - 事前チェック: `scripts/compute_fwhm.py` で測定CSVとPHITS `.out` のFWHMを比較可能。
- 参考Rev（経験則・フィールド合致の目安）
  - 5×5 → `Rev80-5x5-...`（または `Rev60-5x5-...`）
  - 10×10 → `Rev70-c8-0.49n`
  - 30×30 → `Rev50-30x30--c8-0.49n`

### 新CLI（推奨）: PDD重み付け真値スケーリング
- エントリ: `python src/ocr_true_scaling.py`
- 例（reference=CSV, eval=PHITS, 深さ10 cm）:
  - `python src/ocr_true_scaling.py --ref-pdd-type csv --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out --ref-ocr-type csv --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out --norm-mode dmax --cutoff 10 --export-csv --export-gamma`

### トラブルシューティング: 深さ20 cm などでGPRが低い
- 前提整合の確認（必須）
  - 深さ: レポートの `ref depth / eval depth` と `S_axis(ref/eval)` が一致していること。
  - 幅: FWHM(ref/eval) が許容差（目安: 5×5=±0.5 cm、10×10=±1.0 cm、30×30=±2.0 cm）内。
- 中心正規化
  - x=0 ±0.05 cm にサンプルが無いと最大値正規化へフォールバックし、肩形状が歪むことがある。
  - 目視と最小 |x| の確認（原点近傍サンプルが十分か）。
- 平滑化の感度
  - `--no-smooth`／`--smooth-window 11 --smooth-order 3` などで挙動比較。深部は軽めの平滑が無難なことが多い。
- カットオフの感度
  - `--cutoff 20` で尾部ノイズの影響を抑えて改善するかを確認。
- ガンマ基準の感度
  - 診断用に `--dd1 3 --dta1 3` で改善度合いを確認（分解能/幾何差の影響切り分け）。
- 軸対応ミスの排除
  - `xXlat` ↔ `...x.out`、`zYlng` ↔ `...z.out` を厳密に合わせる。
- 共通グリッド
  - `--grid 0.1` はRMSE/可視化安定化に有用（γは元軸で評価）。

### レガシー（互換）
- `src/Comp_measured_phits_v9.1.py` はラッパーで、実体は `src/Comp_measured_phits_v9_1_legacy.py` にあります。

## 設定（config.ini）
- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`（RMSE/可視化の共通グリッド刻み、cm。既定0.1）
- スクリプトはプロジェクトルートの `config.ini` を探し、相対解決を試みます。絶対パスは `config.ini` に集約してください。

## データ仕様
- 実測 CSV: `pos_cm`, `dose` の2列相当（BOM付UTF-8可）。[0,1]に正規化して比較。
- PHITS `.out`: `[ T-Deposit ]` 最終ブロックから1Dプロファイル抽出。位置は cm へ、線量は最大で正規化。

## 出力
- 図: `output/plots/TrueComp_... .png`
- レポート: `output/reports/TrueReport_... .txt`
- 真値/再サンプル/γ配列: `output/data/*.csv`（`--export-csv`, `--export-gamma` 指定時）

## コーディング規約（src 配下）
- PEP 8 ベース、UTF-8（BOM許容）。例外メッセージは日本語でstderrへ。
- 最小差分を維持し、既存I/O仕様を破壊しない。
- 解析ロジック変更時は、レポート出力のパラメータ/根拠も更新。

## 依存ライブラリ
- `pip install pandas numpy matplotlib scipy pymedphys`
- ネットワーク制限環境ではインストール手順のみ提示し、ツール側で自動実行しない。

## よくある落とし穴
- 文字化け: CSV/INIは `utf-8-sig` 読みを推奨。
- 改行: 既存に合わせる（Windows: CRLF）。
- 絶対パスの直書き禁止。`config.ini` に集約。

## 参照
- 新CLI: `src/ocr_true_scaling.py`
- レガシー: `src/Comp_measured_phits_v9_1_legacy.py`, ラッパー: `src/Comp_measured_phits_v9.1.py`
- 設定: `config.ini`
- サンプル: `data/measured_csv/`, `data/phits_output/`


-----

### 追加オプション（中心正規化の調整）
- --center-tol-cm <cm>: x=0 近傍と見なす許容範囲（既定 0.05 cm）。原点近傍サンプルが粗い場合のロバスト化に有効。
- --center-interp: x=0 にサンプルが無い場合に線形補間で x=0 の値を推定し、中心正規化の基準に使用（無指定時は最大値代用）。

-----

### ガンマモード（global/local）
- CLI/GUIともにガンマ基準を切替可能。
  - `--gamma-mode {global,local}`（既定: global）
  - global: 参照系列の全体最大値で%差を評価（一般的な臨床QA設定）
  - local: 各点の局所値で%差を評価（微細差に敏感、厳しめ）
- トラブルシュート時の切替例:
  - 幾何差より強く線量差を見たい場合 → `--gamma-mode local`
  - 通常評価・装置間比較などの慣例に合わせる → 既定（global）

