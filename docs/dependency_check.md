# 依存関係チェックとインストール

## 必要バージョン/パッケージ
- Python: `>=3.9`
- パッケージ: `pandas`, `numpy`, `matplotlib`, `scipy`, `pymedphys`

## 自動チェック
```
python scripts/check_deps.py
```
- インストール漏れやバージョン不一致をチェックします。

## 仮想環境（Windows PowerShell）
```
python -m venv .venv
.\.venv\Scripts\Activate
pip install -U pip
pip install -r requirements.txt
```

※ ネットワーク制限環境では上記コマンドのみ提示し、ツール側で自動実行しません。
