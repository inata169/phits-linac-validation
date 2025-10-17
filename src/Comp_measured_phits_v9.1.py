import sys

def main():
    print("[DEPRECATION] このスクリプトはレガシー化されました。", file=sys.stderr)
    print("新しいPDD重み付け真値スケーリングCLI: src/ocr_true_scaling.py をご利用ください。", file=sys.stderr)
    try:
        from Comp_measured_phits_v9_1_legacy import main as legacy_main
        return legacy_main()
    except Exception as e:
        print(f"レガシースクリプトの実行中にエラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

