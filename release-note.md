# Release v0.2.2

Date: 2025-10-23

## ハイライト
- ドキュメント: 日本語 README/Examples を整備、SHA256 検証手順を追記
- CI: Windows/Ubuntu の安定化（pip cache、prefer-binary、MPLBACKEND=Agg、UTF-8）
- 依存: Python 3.9 は `pymedphys==0.40.*`、Python >=3.10 は `0.41.*` を利用
- リリース: PyInstaller で Windows EXE をビルド、`-V` スモーク実行、バージョン付き EXE と `.sha256` を添付（タグと `__version__` の整合を検証）

## アセット
- `ocr_true_scaling-v0.2.2-windows-x64.exe`
- `ocr_true_scaling-v0.2.2-windows-x64.exe.sha256`

### ハッシュ検証（PowerShell）
```
Get-FileHash .\ocr_true_scaling-v0.2.2-windows-x64.exe -Algorithm SHA256
Get-Content .\ocr_true_scaling-v0.2.2-windows-x64.exe.sha256
```
両者の SHA256 が一致することを確認してください。

代替: `certutil -hashfile .\ocr_true_scaling-v0.2.2-windows-x64.exe SHA256`

## クイックスタート

### EXE（Python 不要）
- バージョン表示: `./ocr_true_scaling-v0.2.2-windows-x64.exe -V`
- サンプル実行（リポジトリ直下で）:
```
./ocr_true_scaling-v0.2.2-windows-x64.exe \
  --ref-pdd-type csv  --ref-pdd-file data\measured_csv\10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data\phits_output\deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data\measured_csv\10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data\phits_output\I600\deposit-y-water-100.out \
  --norm-mode dmax --gamma-mode global --cutoff 10 \
  --fwhm-warn-cm 1.0 --export-csv --export-gamma
```
出力: `output\plots\`, `output\reports\`, `output\data\`

SmartScreen でブロックされる場合は、`Unblock-File .\ocr_true_scaling-v0.2.2-windows-x64.exe` を実行、もしくはファイルのプロパティから「ブロックの解除」を行ってください。

### ソースから（Python 環境）
```
pip install -r requirements.txt
python src/ocr_true_scaling.py -V
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --gamma-mode global --cutoff 10 \
  --fwhm-warn-cm 1.0 --export-csv --export-gamma
```

## 変更点（詳細）
- Docs: 日本語ドキュメントの整備、`docs/openspec.md` と実装の整合、ハッシュ検証手順の追記
- CI: pip キャッシュ利用・prefer-binary・ヘッドレス安定化設定、pymedphys バージョンの環境別切替
- Release: EXE のビルド・スモーク実行・アセット添付、タグと `__version__` の不一致防止

## 互換性
- Python 3.9: `pymedphys==0.40.*`
- Python >=3.10: `pymedphys==0.41.*`
- EXE 利用時は Python のインストール不要

## 参考
- 日本語仕様書: `docs/manual_ja.md`
- Open Spec（英語）: `docs/openspec.md`

