# 実行例とスクリプトの使い方

## True-scaling（PDD重み付け）OCR比較（推奨CLI）
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file data/measured_csv/10x10mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file data/phits_output/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file data/phits_output/I600/deposit-y-water-100.out \
  --norm-mode dmax --cutoff 10 --export-csv --export-gamma \
  --gamma-mode global --fwhm-warn-cm 1.0 \
  --output-dir output
```

- JSONレポートを保存したい場合:
```
  --report-json output/data/true_report.json
```

## FWHMの事前確認
```
python scripts/compute_fwhm.py \
  --ref-csv data/measured_csv/10x10m10cm-xXlat.csv \
  --eval-out data/phits_output/I600/deposit-y-water-100.out
```

## PDDのγ解析
```
python scripts/compute_pdd_gamma.py \
  --ref data/measured_csv/10x10mPDD-zZver.csv \
  --eval data/phits_output/deposit-z-water.out \
  --gamma-mode global --dd 3 --dta 3 --cutoff 10
```

## バッチ（例）
- PowerShell: `scripts/run_all.ps1`
- Python: `scripts/run_all.py`
- GUI: `scripts/run_true_scaling_gui.ps1` または `run_gui.bat`

