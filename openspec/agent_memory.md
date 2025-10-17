# 次回作業メモ（エージェント用）

## 次回の開始プロンプト（そのまま使用可）
あれ、直っていないね。たとえば、
`C:\Users\放射治療研究用PC\Documents\Python\phits-linac-validation\output\Rev50-30x30--c8-0.49n\reports\TrueReport_30x30m20cm-zYlng_vs_deposit-y-water-200z_norm-dmax_zref-10_z-20-10.txt`
の「## 解析パラメータ norm-mode: dmax, z_ref: 10.0 cm ref depth (cm): 20.000000, eval depth (cm): 10.000000 S_axis(ref): 0.434240, S_axis(eval): 0.649465」」」というように、ref depth (cm)とeval depth (cm)が合っていない。あなたは「深さ(cm)」の情報を読み取れないのではないですか？深さの情報は、測定値であれば「05x05m20cm-zYlng.csv」の”05x05”は照射野、"m"は測定値、"20cm"は深さ、”zYlng”は測定器の軸方向のデータである、と表されています。PHITSのアウトプットファイル「deposit-y-water-200x.out」では、”deposit”はPHITSのdoseデータを入力していることを表している、”y-water-200x”は深さy=20cmでx軸方向に測定していったデータである、ということを表しています。理解できましたか？

## 背景と問題点
- レポート上の `ref depth (cm)` と `eval depth (cm)` が一致しないケースがある。
- 原因: OCRの深さ決定で、PHITSファイルから深さが取得できない時に既定 `z_ref`（例: 10 cm）へフォールバックしてしまうため。

## 修正方針（src/ocr_true_scaling.py）
1) 深さ抽出ユーティリティを追加:
   - `_extract_depth_cm_from_csv_filename(name) -> Optional[float]`
     - `([0-9]+(?:\.[0-9]+)?)cm` を検出して cm を返す（小数対応）。
   - `_extract_depth_cm_from_phits_filename(name) -> Optional[float]`
     - 末尾の `-(\d+)([a-z])?\.out` の数値を mm とみなし `cm = mm/10` で返す。
2) OCR側の深さ決定ロジックを変更:
   - CSV: ファイル名から cm を取得。なければ `z_ref` へフォールバック（stderrへ警告）。
   - PHITS: 本文の `y_slab` 中心（cm）を最優先。なければファイル名から推定。どちらもなければ `z_ref`（警告）。
3) レポート出力は、この決定ロジックで得た深さで `ref depth / eval depth` と `S_axis(ref/eval)` を記載。

## 参考（現状コードの該当箇所）
- `src/ocr_true_scaling.py` の OCR 読み込み部で `z_depth_ref` / `z_depth_eval` を設定している行。
- 現状は CSV/PHITSともにフォールバックが早く、PHITSファイル名からの深さ推定が未実装。

## 確認手順（修正後）
1) 例の組み合わせで CLI を実行し、TrueReport の `ref depth / eval depth` が期待通り一致することを確認。
2) `S_axis(ref)` と `S_axis(eval)` が各深さの PDD 正規化値に一致することを確認。
3) 既存の他ケース（深さ 0.5/10/20 cm）でも同様に確認。

## 注意
- 文字コードは `utf-8-sig` 読みを維持（既存仕様）。
- 改行は可能ならCRLF（Windows）に合わせる。
- 絶対パスの直書きはしない。設定は `config.ini` に集約。

