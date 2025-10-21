# Examples & Sample Logs

## CLI: OCR + PDD (global gamma)
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file test/measured_csv/05x05mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file test/PHITS/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file test/measured_csv/05x05m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file test/PHITS/deposit-y-water-100x.out \
  --norm-mode dmax --cutoff 10 --output-dir output/test/sample-global
```

Sample stdout:
```
RMSE: 0.024224
Gamma pass (DD=2.0%, DTA=2.0mm, Cutoff=10.0%): 81.82%
Gamma pass (DD=3.0%, DTA=3.0mm, Cutoff=10.0%): 95.45%
Plot saved: output/test/sample-global/plots/TrueComp_...
Report saved: output/test/sample-global/reports/TrueReport_...
PDD Report saved: output/test/sample-global/reports/PDDReport_...
PDD Plot saved: output/test/sample-global/plots/PDDComp_...
```

## CLI: OCR + PDD (local gamma)
```
python src/ocr_true_scaling.py \
  --ref-pdd-type csv  --ref-pdd-file test/measured_csv/05x05mPDD-zZver.csv \
  --eval-pdd-type phits --eval-pdd-file test/PHITS/deposit-z-water.out \
  --ref-ocr-type csv   --ref-ocr-file test/measured_csv/05x05m10cm-xXlat.csv \
  --eval-ocr-type phits --eval-ocr-file test/PHITS/deposit-y-water-100x.out \
  --norm-mode dmax --cutoff 10 --gamma-mode local --output-dir output/test/sample-local
```

Sample stdout (more stringent than global):
```
RMSE: 0.024224
Gamma pass (DD=2.0%, DTA=2.0mm, Cutoff=10.0%): 74.24%
Gamma pass (DD=3.0%, DTA=3.0mm, Cutoff=10.0%): 84.85%
```

## Suppress PDD outputs
```
... --no-pdd-report
```
No `PDDReport_*.txt` nor `PDDComp_*.png` are created.

## PHITS filename-based depth inference
- `...-050x.out` → 5.0 cm, `...-100z.out` → 10.0 cm, `...-200x.out` → 20.0 cm.
- Header y-slab centre (if present) overrides filename inference.

