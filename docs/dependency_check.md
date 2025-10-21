# 依存関係チェックとインストール

## 必須バージョン/パッケージ
- Python: `>=3.9`
- パッケージ: `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`

## 自動チェック
```
python scripts/check_deps.py
```
- インストール漏れやバージョン不一致を検出します。

## 仮想環境（例: Windows PowerShell）
```
python -m venv .venv
.\.venv\Scripts\Activate
pip install -U pip
pip install pandas numpy matplotlib scipy pymedphys
```

※ ネットワーク制限環境では上記コマンドのみ提示し、ツール側で自動実行はしません。

