import argparse
import os
import re
import sys
from typing import Tuple, Optional

import numpy as np
import pandas as pd


def load_csv_profile(path: str) -> Tuple[np.ndarray, np.ndarray]:
    try:
        df = pd.read_csv(path, encoding='utf-8-sig', header=None)
        if df.shape[1] >= 2 and isinstance(df.iloc[0, 0], str) and '(cm)' in df.iloc[0, 0]:
            df = pd.read_csv(path, encoding='utf-8-sig')
            cols = list(df.columns)[:2]
            df = df[cols]
            df.columns = ['pos', 'dose']
        else:
            df = df.iloc[:, :2]
            df.columns = ['pos', 'dose']
        pos = pd.to_numeric(df['pos'], errors='coerce').to_numpy()
        dose = pd.to_numeric(df['dose'], errors='coerce').to_numpy()
        mask = np.isfinite(pos) & np.isfinite(dose)
        pos = pos[mask]
        dose = dose[mask]
        order = np.argsort(pos)
        pos = pos[order].astype(float)
        dose = dose[order].astype(float)
        if dose.size == 0:
            raise ValueError(f"CSVに有効な数値データがありません: {path}")
        dmax = float(np.max(dose))
        if dmax <= 0:
            raise ValueError(f"CSVの線量最大値が0以下です: {path}")
        return pos, (dose / dmax)
    except Exception as e:
        print(f"エラー: CSV読み込み中に問題が発生しました: {e}", file=sys.stderr)
        raise


def parse_phits_out_profile(path: str) -> Tuple[np.ndarray, np.ndarray, str]:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        # 軸/データ表の検出（簡易）
        axis = ''
        for line in lines:
            s = line.strip().lower().replace(' ', '')
            if s.startswith('axis='):
                axis = line.split('=')[1].strip().split('#')[0].strip()
        data_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('#  y-lower') or line.strip().startswith('#  z-lower') or line.strip().startswith('#  x-lower'):
                data_start = i + 1
                break
        if data_start is None:
            raise ValueError('PHITSデータ表の開始位置が見つかりません')
        pos_centers, vals = [], []
        for line in lines[data_start:]:
            s = line.strip()
            if not s or s.startswith('#'):
                break
            parts = s.split()
            if len(parts) < 3:
                continue
            try:
                lower = float(parts[0])
                upper = float(parts[1])
                v = float(parts[2])
            except Exception:
                continue
            pos_centers.append((lower + upper) / 2.0)
            vals.append(v)
        pos = np.asarray(pos_centers, dtype=float)
        dose = np.asarray(vals, dtype=float)
        if dose.size == 0:
            raise ValueError('PHITSデータが空です')
        dmax = float(np.max(dose))
        if dmax <= 0:
            raise ValueError('PHITS線量最大値が0以下です')
        return pos, (dose / dmax), axis

    except Exception as e:
        print(f"エラー: PHITS読み込み中に問題が発生しました: {e}", file=sys.stderr)
        raise


def compute_fwhm(pos_cm: np.ndarray, dose_norm: np.ndarray) -> Optional[float]:
    if pos_cm.size < 3:
        return None
    # 最大位置（ピーク）
    imax = int(np.argmax(dose_norm))
    peak = float(dose_norm[imax])
    if peak <= 0:
        return None
    half = peak * 0.5
    # 左側交点
    left = None
    for i in range(imax, 0, -1):
        if dose_norm[i - 1] <= half <= dose_norm[i] or dose_norm[i] <= half <= dose_norm[i - 1]:
            x1, y1 = pos_cm[i - 1], dose_norm[i - 1]
            x2, y2 = pos_cm[i], dose_norm[i]
            if y2 != y1:
                left = float(x1 + (half - y1) * (x2 - x1) / (y2 - y1))
            else:
                left = float(x1)
            break
    # 右側交点
    right = None
    for i in range(imax, len(pos_cm) - 1):
        if dose_norm[i] <= half <= dose_norm[i + 1] or dose_norm[i + 1] <= half <= dose_norm[i]:
            x1, y1 = pos_cm[i], dose_norm[i]
            x2, y2 = pos_cm[i + 1], dose_norm[i + 1]
            if y2 != y1:
                right = float(x1 + (half - y1) * (x2 - x1) / (y2 - y1))
            else:
                right = float(x2)
            break
    if left is None or right is None:
        return None
    return float(abs(right - left))


def main():
    parser = argparse.ArgumentParser(description='1DプロファイルのFWHM(半値全幅)を計算します。')
    parser.add_argument('--type1', choices=['csv', 'phits'], required=True)
    parser.add_argument('--file1', required=True)
    parser.add_argument('--type2', choices=['csv', 'phits'])
    parser.add_argument('--file2')
    args = parser.parse_args()

    # 1本目
    if args.type1 == 'csv':
        x1, y1 = load_csv_profile(args.file1)
    else:
        x1, y1, _ = parse_phits_out_profile(args.file1)
    fwhm1 = compute_fwhm(x1, y1)
    if fwhm1 is None:
        print('エラー: 1本目のFWHMを決定できませんでした。', file=sys.stderr)
        sys.exit(1)

    print(f"FWHM1: {fwhm1:.4f} cm  ({args.type1} | {args.file1})")

    # 2本目（任意）
    if args.type2 and args.file2:
        if args.type2 == 'csv':
            x2, y2 = load_csv_profile(args.file2)
        else:
            x2, y2, _ = parse_phits_out_profile(args.file2)
        fwhm2 = compute_fwhm(x2, y2)
        if fwhm2 is None:
            print('エラー: 2本目のFWHMを決定できませんでした。', file=sys.stderr)
            sys.exit(1)
        delta = fwhm2 - fwhm1
        print(f"FWHM2: {fwhm2:.4f} cm  ({args.type2} | {args.file2})")
        print(f"ΔFWHM: {delta:+.4f} cm (2 - 1)")


if __name__ == '__main__':
    main()

