# PHITS 蛹ｻ逋ら畑繝ｪ繝九い繝・け邱夐㍼隧穂ｾ｡繝・・繝ｫ

[![release](https://img.shields.io/github/v/release/inata169/phits-linac-validation?include_prereleases&label=release)](LICENSE)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)

PHITS 縺ｮ蜃ｺ蜉幢ｼ・out・峨→螳滓ｸｬ CSV 繧定ｪｭ縺ｿ霎ｼ縺ｿ縲∫ｷ夐㍼繝励Ο繝輔ぃ繧､繝ｫ・・DD/OCR・峨・豈碑ｼ・ｩ穂ｾ｡・医ぎ繝ｳ繝槭ヽMSE・峨ｒ陦後≧繝・・繝ｫ鄒､縺ｧ縺吶よ耳螂ｨ繝輔Ο繝ｼ縺ｯ PDD 繧堤畑縺・◆逵溷､繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ縺ｫ繧医ｋ OCR 豈碑ｼ・〒縺吶・
-----

## 莉墓ｧ假ｼ・penspec・・- 繧ｪ繝ｼ繝励Φ莉墓ｧ假ｼ医ョ繝ｼ繧ｿ蠖｢蠑上，LI蠑墓焚縲∝・逅・ヵ繝ｭ繝ｼ縲・明蛟､縲∝・蜉帛･醍ｴ・√お繝ｩ繝ｼ譁ｹ驥晢ｼ峨・ `docs/openspec.md` 繧貞盾辣ｧ縺励※縺上□縺輔＞縲・- 螳溯｣・・ `src/ocr_true_scaling.py` 縺ｮ謖吝虚縺ｫ謨ｴ蜷医＠縺ｦ縺・∪縺呻ｼ医ラ繝ｩ繝輔ヨ・峨・
-----

## 謗ｨ螂ｨCLI・夂悄蛟､繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ・・DD驥阪∩莉倥￠・・- 繧ｨ繝ｳ繝医Μ: `python src/ocr_true_scaling.py`
- 逵溷､縺ｮ讒区・: `True(x,z) = PDD_norm(z) ﾃ・OCR_rel(x,z)`
- 蜈･蜉・ reference/evaluation 縺ｨ繧ゅ↓ CSV 縺ｾ縺溘・ PHITS `.out` 繧呈欠螳壼庄閭ｽ
- 豁｣隕丞喧: 譌｢螳壹・ `dmax`縲ょｿ・ｦ√↓蠢懊§縺ｦ `--z-ref <cm>` 縺ｧ蜿ら・豺ｱ繧呈欠螳・- 荳ｭ蠢・ｭ｣隕丞喧: x=0 霑大ｍ ﾂｱ0.05 cm 繧剃ｸｭ蠢・､縺ｨ縺励∫┌縺代ｌ縺ｰ `--center-interp` 縺ｧ邱壼ｽ｢陬憺俣縲√◎繧後ｂ辟｡縺代ｌ縺ｰ譛螟ｧ蛟､繧剃ｽｿ逕ｨ
- 蜃ｺ蜉・ `output/plots/*.png`, `output/reports/*.txt`, `output/data/*.csv`
- 萓九・螳溯｡後Ξ繧ｷ繝斐・ `docs/examples.md` 繧貞盾辣ｧ

萓具ｼ・eference=CSV, eval=PHITS, 豺ｱ縺・0 cm・・
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

## 邨ｶ蟇ｾ豈碑ｼ・→ FWHM 繝√ぉ繝・け・磯㍾隕・ｼ・- 逵溷､・育ｵｶ蟇ｾ蟇・ｊ・峨・豈碑ｼ・ｒ陦後≧蝣ｴ蜷医・縲‘val 蛛ｴ PDD 縺ｫ PHITS 縺ｮ `deposit-z-water.out` 繧呈欠螳夲ｼ・ef 蛛ｴ縺ｯ貂ｬ螳啀DD・峨・- PHITS OCR 縺ｮ辣ｧ蟆・㍽繧ｵ繧､繧ｺ縺ｯ繝輔ぃ繧､繝ｫ蜷阪°繧臥峩謗･蛻､蛻･縺ｧ縺阪↑縺・◆繧√：WHM縺ｧ蟷・紛蜷医ｒ遒ｺ隱阪・  - `--fwhm-warn-cm <cm>`・域里螳・1.0・峨〒 FWHM(ref/eval) 縺ｮ |ﾎ培 縺碁明蛟､雜・℃譎ゅ↓ stderr 隴ｦ蜻翫ゅΞ繝昴・繝医↓繧・FWHM(ref/eval) 縺ｨ ﾎ・繧貞・蜉帙・  - 莠句燕繝√ぉ繝・け縺ｯ `scripts/compute_fwhm.py` 繧貞茜逕ｨ蜿ｯ縲・
-----

## 繝医Λ繝悶Ν繧ｷ繝･繝ｼ繝・ぅ繝ｳ繧ｰ・・PR 縺御ｽ弱＞遲会ｼ・- 豺ｱ縺・ 繝ｬ繝昴・繝医・ `ref depth / eval depth` 縺ｨ `S_axis(ref/eval)` 縺御ｸ閾ｴ縺励※縺・ｋ縺薙→縲・- 蟷・ FWHM(ref/eval) 縺瑚ｨｱ螳ｹ蟾ｮ蜀・ｼ育岼螳・ 5ﾃ・=ﾂｱ0.5 cm縲・0ﾃ・0=ﾂｱ1.0 cm縲・0ﾃ・0=ﾂｱ2.0 cm・峨・- 荳ｭ蠢・ｭ｣隕丞喧: 蜴溽せ霑大ｍ繧ｵ繝ｳ繝励Ν縺檎┌縺・→譛螟ｧ蛟､豁｣隕丞喧縺ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ縺苓か縺梧ｭｪ繧縺薙→縺ゅｊ縲Ａ--center-interp` 繧呈､懆ｨ弱・- 蟷ｳ貊大喧: `--no-smooth` / `--smooth-window 11 --smooth-order 3` 縺ｧ謖吝虚豈碑ｼ・ｼ域ｷｱ驛ｨ縺ｯ霆ｽ繧√′辟｡髮｣・峨・- 繧ｫ繝・ヨ繧ｪ繝・ `--cutoff 20` 縺ｧ蟆ｾ驛ｨ繝弱う繧ｺ縺ｮ蠖ｱ髻ｿ繧呈椛蛻ｶ縲・- 繧ｬ繝ｳ繝槫渕貅・ 險ｺ譁ｭ逕ｨ騾斐〒 `--dd1 3 --dta1 3` 縺ｫ蛻・崛縲～--gamma-mode local` 縺ｧ邱夐㍼蟾ｮ驥崎ｦ悶・- 霆ｸ蟇ｾ蠢・ `xXlat` 竊・`...x.out`縲～zYlng` 竊・`...z.out` 繧貞宍蟇・ｸ閾ｴ縲・- 蜈ｱ騾壹げ繝ｪ繝・ラ: `--grid 0.1` 縺ｯRMSE/蜿ｯ隕門喧螳牙ｮ壼喧縺ｫ譛臥畑・夷ｳ縺ｯ蜈・ｻｸ縺ｧ隧穂ｾ｡・峨・
-----

## 險ｭ螳夲ｼ・onfig.ini・・- `[Paths]`: `phits_data_dir`, `measured_data_dir`, `output_dir`
- `[Processing]`: `resample_grid_cm`・・MSE/蜿ｯ隕門喧縺ｮ蜈ｱ騾壹げ繝ｪ繝・ラ蛻ｻ縺ｿ縲…m縲よ里螳・0.1・・- 繧ｵ繝ｳ繝励Ν: `config.ini.example` 繧定､・｣ｽ縺励Ο繝ｼ繧ｫ繝ｫ迺ｰ蠅・↓蜷医ｏ縺帙※菴懈・縲らｵｶ蟇ｾ繝代せ縺ｯ `config.ini` 縺ｫ髮・ｴ・・
-----

## 繝・・繧ｿ莉墓ｧ假ｼ郁ｦ∫せ・・- 螳滓ｸｬ CSV: 2蛻暦ｼ・pos_cm`, `dose` 逶ｸ蠖難ｼ峨Ａutf-8-sig` 謗ｨ螂ｨ縲る撼謨ｰ縺ｯ髯､螟悶＠菴咲ｽｮ縺ｧ繧ｽ繝ｼ繝医∵怙螟ｧ縺ｧ豁｣隕丞喧縲・- PHITS `.out`: `[ T-Deposit ]` 縺ｮ譛邨り｡ｨ縺九ｉ1D繝励Ο繝輔ぃ繧､繝ｫ謚ｽ蜃ｺ縲ゆｽ咲ｽｮ縺ｯ bin 荳ｭ蠢・ｼ・m・峨∫ｷ夐㍼縺ｯ譛螟ｧ縺ｧ豁｣隕丞喧縲０CR豺ｱ縺輔・繝倥ャ繝荳ｭ蠢・∪縺溘・繝輔ぃ繧､繝ｫ蜷・`-<mm>[x|z].out` 縺九ｉ謗ｨ螳壹＠縲∫┌縺代ｌ縺ｰ `--z-ref`縲・
-----

## 蜃ｺ蜉・- 蝗ｳ: `output/plots/TrueComp_... .png`
- 繝ｬ繝昴・繝・ `output/reports/TrueReport_... .txt`・・nputs/Params/Results縲：WHM隕∫ｴ・性繧・・- PDD繝ｬ繝昴・繝・蝗ｳ: `PDDReport_... .txt`, `PDDComp_... .png`・・--no-pdd-report` 縺ｧ謚第ｭ｢蜿ｯ・・- CSV繧ｨ繧ｯ繧ｹ繝昴・繝・ `output/data/*.csv`・・--export-csv`, `--export-gamma` 譎ゑｼ・- JSON繝ｬ繝昴・繝・ `--report-json <path>` 縺ｧ讖滓｢ｰ蜿ｯ隱ｭ繧ｵ繝槭Μ繧剃ｿ晏ｭ假ｼ・nputs/params/derived/results・・
-----

## 繧､繝ｳ繧ｹ繝医・繝ｫ/萓晏ｭ・- Python: `>=3.9`
- 萓晏ｭ・ `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`
- 謇矩・→繝√ぉ繝・け縺ｯ `docs/dependency_check.md` 繧貞盾辣ｧ

-----

## 繧ｬ繝ｳ繝槭Δ繝ｼ繝会ｼ・lobal/local・・- `--gamma-mode {global,local}` 縺ｧ蛻・崛縲・- global: 蜿ら・邉ｻ蛻励・蜈ｨ菴捺怙螟ｧ蛟､縺ｧ%蟾ｮ繧定ｩ穂ｾ｡・郁・蠎害A縺ｮ諷｣萓具ｼ峨・- local: 螻謇蛟､縺ｧ%蟾ｮ繧定ｩ穂ｾ｡・亥ｾｮ邏ｰ蟾ｮ縺ｫ謨乗─縲∝宍縺励ａ・峨・
-----

## 繝ｩ繧､繧ｻ繝ｳ繧ｹ
MIT License

-----

## クイックスタート（推奨）
- 依存導入: `pip install -r requirements.txt`
- 実行: `python src/ocr_true_scaling.py --help`（`-V/--version` でバージョン表示）
- 例: 本文の推奨CLI節または `docs/examples.md` を参照

### Windows 用実行ファイル（EXE）
- GitHub Releases に `ocr_true_scaling.exe` を添付（タグ作成/リリース時に自動ビルド）
- ダウンロード後、コマンドプロンプトで `ocr_true_scaling.exe --help` を実行


