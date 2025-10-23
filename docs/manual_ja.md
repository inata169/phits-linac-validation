# PHITS–実測 OCR/PDD 比較ツール 仕様書（日本語）

最終更新: v0.2.2（src/ocr_true_scaling.py と整合）

## 目的
- PHITS 出力（`.out`）と実測 CSV を読み込み、OCR（横方向）プロファイルを PDD（深さ方向）で重み付けした“真値スケーリング”により、より物理的に妥当な比較（RMSE/ガンマ）を行う。

## 対象と非対象
- 対象:
  - 水等価環境での基本場（例: 5×5, 10×10, 30×30 cm²）の PDD と OCR
  - 入力は reference/eval ともに CSV または PHITS `.out` を混在可
- 非対象:
  - 個別治療（患者）計画、複雑な非等質モデリング、MU 校正の院内基準策定

## 手法の概要（真値スケーリング）
1) PDD 正規化（既定: dmax=1.00、代替: `z_ref` の値で正規化）
2) OCR の中心正規化（x=0 を 1.00）
3) 深さごとのスケール因子を定義: `S_axis(z) = PDD_norm(z)`
4) 真値化: `True(x,z) = S_axis(z) * OCR_rel(x,z)` を reference/eval の双方に適用
5) 真値系列同士で RMSE と γ を評価

式の意図: 両系列を同一の深さ依存スケールに乗せることで、相対プロファイル比較よりも物理的一貫性が高い評価を可能にします。

## 入力データ仕様
- 実測 CSV
  - 文字コード: `utf-8-sig`（BOM 可）
  - 2 列相当: `pos`（cm）, `dose`（任意単位）
  - ヘッダ無し/ヘッダ有りの双方を許容（`(cm)` を含む先頭 2 列を採用）
  - ローダで最大値基準に正規化（ピーク=1.0）
- PHITS `.out`
  - `[ T-Deposit ]` 系の最終ブロックから 1D テーブルを抽出
  - 位置は bin center（(lower+upper)/2）を cm に換算
  - 線量は系列最大値で正規化（ピーク=1.0）
- OCR の深さ決定（レポート/スケール整合用）
  - CSV: ファイル名 `<...><depth>cm` から取得、無ければ `--z-ref`
  - PHITS: ヘッダ `# y = (y0 .. y1)` の中心を優先、無ければファイル名末尾 `-<mm>[x|z].out`（mm/10=cm）、どちらも無ければ `--z-ref`。フォールバック時は stderr に警告

## 正規化と前処理
- PDD 正規化 `--norm-mode {dmax,z_ref}`（既定 dmax）
  - `z_ref`: `--z-ref <cm>` の値で割る（0 以下はエラー）
- OCR 中心正規化
  - `--center-tol-cm <cm>` 内に原点サンプルがあればその値で 1.0 化
  - サンプルが無い場合: `--center-interp` 指定で線形補間の x=0 値を使用、無指定時はピーク値で代用
- 平滑化（任意）
  - `--no-smooth` で無効化、既定は Savitzky–Golay（`--smooth-window 5`, `--smooth-order 2`）。平滑後は再度ピーク=1.0 へスケール

## 評価指標
- RMSE: 真値系列同士で算出
  - 共通グリッドが有効なら線形補間して RMSE を計算
  - グリッド刻みの決定順: `--grid` > `config.ini [Processing].resample_grid_cm` > 既定 `0.1` cm
- ガンマ（γ）: `pymedphys.gamma` を使用
  - 既定の基準: (DD=2%, DTA=2mm, Cutoff=10%) と (DD=3%, DTA=3mm, Cutoff=10%) を両方出力
  - `--gamma-mode {global,local}`（既定 global）
    - global: 参照真値系列の最大値で%差を評価
    - local: 各点の局所値で%差を評価
- FWHM チェック（OCR の相対プロファイル幅）
  - レポートに `FWHM(ref)`, `FWHM(eval)`, `Δ` を出力
  - `--fwhm-warn-cm <cm>` 超過で stderr に警告（既定 1.0 cm）

## CLI（src/ocr_true_scaling.py）
一般:
- `-V`, `--version` ツールのバージョン表示

必須入力（参照/評価）:
- `--ref-pdd-type {csv,phits}` `--ref-pdd-file <path>`
- `--eval-pdd-type {csv,phits}` `--eval-pdd-file <path>`
- `--ref-ocr-type {csv,phits}` `--ref-ocr-file <path>`
- `--eval-ocr-type {csv,phits}` `--eval-ocr-file <path>`

正規化と深さ:
- `--norm-mode {dmax,z_ref}`（既定 dmax）
- `--z-ref <cm>`（既定 10.0）

ガンマ基準/モード:
- `--dd1 <percent>` `--dta1 <mm>`（既定 2, 2）
- `--dd2 <percent>` `--dta2 <mm>`（既定 3, 3）
- `--gamma-mode {global,local}`（既定 global）
- `--cutoff <percent>`（既定 10）

前処理（OCR）:
- `--center-tol-cm <cm>`（既定 0.05）
- `--center-interp`（x=0 補間）
- `--no-smooth` / `--smooth-window <odd>` / `--smooth-order <int>`

描画/出力/その他:
- `--grid <cm>`（RMSE/CSV 用の共通グリッド）
- `--ymin <v>` `--ymax <v>`、`--xlim-symmetric`
- `--legend-ref <str>` `--legend-eval <str>`
- `--fwhm-warn-cm <cm>`（既定 1.0）
- `--output-dir <dir>`（既定 `output/`）
- `--export-csv`（真値/再サンプル CSV を出力）
- `--export-gamma`（γ 配列を CSV 出力（基準1））
- `--report-json <path>`（機械可読な JSON レポートを出力）
- `--no-pdd-report`（PDD レポート/図の生成を抑止）

自動判別の便宜:
- `--*-type csv` でもパスが `.out` の場合は自動的に `phits` に切替（stderr 警告）。OCR も同様

## 実行例
reference=CSV, eval=PHITS, 深さ 10 cm の OCR を比較（真値スケーリング、CSV/γ出力あり）:

```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --gamma-mode global --cutoff 10 \
  --fwhm-warn-cm 1.0 --export-csv --export-gamma
```

## 出力仕様
- 図（PNG）: `output/plots/TrueComp_{ref}_vs_{eval}_norm-{mode}_zref-{zref}_z-{zRef}-{zEval}.png`
- レポート（TXT）: `output/reports/TrueReport_{ref}_vs_{eval}_... .txt`
  - Inputs/Params/Results を記載
  - Params: `norm-mode`, `z_ref`, `gamma-mode`, `ref depth`, `eval depth`, `S_axis(ref/eval)`, `grid (cm)`
  - Results: `RMSE`, `Gamma 1/2`, `FWHM(ref/eval/delta)`
- PDD レポート/図（既定オン、`--no-pdd-report` で抑止）
  - `PDDReport_{refPDD}_vs_{evalPDD}_... .txt`, `PDDComp_{refPDD}_vs_{evalPDD}_... .png`
- CSV（`--export-csv`）
  - `data/TrueRef_{ref}_z{zRef}.csv`、`data/TrueEval_{eval}_z{zEval}.csv`
  - 共通グリッド有効時: `TrueRefResampled_*`, `TrueEvalResampled_*`
- γ 配列（`--export-gamma`）
  - `data/Gamma_{ref}_vs_{eval}_z{zRef}-{zEval}.csv`
- JSON（`--report-json`）
  - 入力・パラメータ・派生値（深さ/スケール/FWHM）・結果（RMSE/GPR）・生成ファイルパス

## 設定ファイル（config.ini）
- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`（RMSE/可視化の共通グリッド刻み、cm。既定 0.1）
- スクリプトはプロジェクトルートの `config.ini` を参照。絶対パスは `config.ini` に集約

## FWHM と照射野幅の整合
- PHITS OCR は照射野サイズをファイル名から直接判別できないケースがあるため、FWHM(ref/eval) の整合確認が重要
- 目安（|Δ| 許容差）: 5×5=±0.5 cm、10×10=±1.0 cm、30×30=±2.0 cm
- 事前チェック: `scripts/compute_fwhm.py` で CSV/PHITS の FWHM を比較

## トラブルシューティング（GPR 低下時）
- 前提整合
  - 深さ: レポートの `ref depth / eval depth`、`S_axis(ref/eval)` が一致しているか
  - 幅: FWHM(ref/eval) の差が許容範囲か
- 中心正規化
  - 原点近傍サンプルが粗いと形状が歪むことあり → `--center-tol-cm` の拡大、`--center-interp` の使用
- 平滑化の感度
  - `--no-smooth`、または軽めの平滑（`--smooth-window 11 --smooth-order 3`）で比較
- カットオフ
  - `--cutoff 20` で尾部ノイズの影響低減
- ガンマ基準
  - 幾何差より線量差を強く見たい → `--gamma-mode local`
- 共通グリッド
  - `--grid 0.1` は RMSE/可視化の安定に有効（γは元軸で評価）
- 軸対応ミスの排除
  - `xXlat` ↔ PHITS 側 lateral（`...x.out`）、`zYlng` ↔ longitudinal（`...z.out`）

## Windows バイナリ（EXE）
- 取得: GitHub Releases（`ocr_true_scaling-v<ver>-windows-x64.exe`）
- ハッシュ検証（PowerShell）:
  - `Get-FileHash .\ocr_true_scaling-<ver>-windows-x64.exe -Algorithm SHA256`
  - `Get-Content .\ocr_true_scaling-<ver>-windows-x64.exe.sha256`
  - 値の一致を確認（または `certutil -hashfile ... SHA256`）
- SmartScreen/AV 対応
  - ブロックされた場合: `Unblock-File .\ocr_true_scaling-<ver>-windows-x64.exe`、または右クリック→プロパティ→「ブロックの解除」

## GUI（補助ツール）
- `scripts/run_true_scaling_gui.ps1`
  - 入力（PDD/OCR）、各種パラメータ、ガンマモード、PDDレポ ON/OFF、中心補間/平滑化/FWHM 閾値などを GUI 操作で設定
  - 出力フォルダから直近のレポート/図をワンクリックで開く補助機能あり

## 既知の制限・今後
- DICOM‑RT 直接入力（RTDOSE/RTPLAN）のサポートは計画中（OpenSpec: `plan-dicom-rt-support-spec`）
- コードサイン未対応（将来的に検討）

## 変更履歴（ハイライト）
- v0.2.2
  - ドキュメント整備（日本語 README/Examples、SHA256 手順）、CI 安定化、Release 自動化（EXE + .sha256 添付）
- v0.2.1
  - `-V/--version`、γモード（global/local）、PDD レポート/図の追加
- v0.2.0 以前
  - 真値スケーリング一式、JSON/CSV 出力、FWHM レポート等

## 参照
- ツール本体: `src/ocr_true_scaling.py`
- 設定: `config.ini`
- サンプル: `data/measured_csv/`, `data/phits_output/`
- 付属スクリプト: `scripts/compute_fwhm.py`, `scripts/run_true_scaling_gui.ps1`
- OpenSpec（英語）: `docs/openspec.md`

