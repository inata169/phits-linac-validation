import argparse
import csv
import sys
from typing import Optional, Tuple

import numpy as np
import pandas as pd


def load_csv_profile(path: str) -> Tuple[np.ndarray, np.ndarray]:
    df0 = pd.read_csv(path, encoding='utf-8-sig', header=None)
    if df0.shape[1] >= 2 and isinstance(df0.iloc[0, 0], str) and '(cm)' in str(df0.iloc[0, 0]):
        df = pd.read_csv(path, encoding='utf-8-sig')
        cols = list(df.columns)[:2]
        df = df[cols]
        df.columns = ['pos', 'dose']
    else:
        df = df0.iloc[:, :2]
        df.columns = ['pos', 'dose']
    pos = pd.to_numeric(df['pos'], errors='coerce').to_numpy()
    dose = pd.to_numeric(df['dose'], errors='coerce').to_numpy()
    m = np.isfinite(pos) & np.isfinite(dose)
    pos = pos[m]
    dose = dose[m]
    order = np.argsort(pos)
    pos = pos[order].astype(float)
    dose = dose[order].astype(float)
    dmax = float(np.max(dose)) if dose.size else 0.0
    if dmax <= 0:
        raise ValueError('dose max <= 0 or empty')
    return pos, (dose / dmax)


def parse_phits_out_profile(path: str) -> Tuple[np.ndarray, np.ndarray]:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    data_start = None
    for i, line in enumerate(lines):
        t = line.strip().lower()
        if t.startswith('#  y-lower') or t.startswith('#  z-lower') or t.startswith('#  x-lower'):
            data_start = i + 1
            break
    if data_start is None:
        raise ValueError('cannot find PHITS data table header')
    pos_centers, vals = [], []
    for line in lines[data_start:]:
        s = line.strip()
        if not s or s.startswith('#'):
            break
        parts = s.split()
        if len(parts) < 3:
            continue
        try:
            lo = float(parts[0]); hi = float(parts[1]); v = float(parts[2])
        except Exception:
            continue
        pos_centers.append(0.5 * (lo + hi))
        vals.append(v)
    pos = np.asarray(pos_centers, float)
    dose = np.asarray(vals, float)
    dmax = float(np.max(dose)) if dose.size else 0.0
    if dmax <= 0:
        raise ValueError('PHITS dose max <= 0 or empty')
    return pos, (dose / dmax)


def compute_fwhm(x: np.ndarray, y: np.ndarray) -> Optional[float]:
    if x.size < 3:
        return None
    i = int(np.argmax(y)); peak = float(y[i])
    if peak <= 0:
        return None
    half = 0.5 * peak
    L = None
    for k in range(i, 0, -1):
        y0, y1 = y[k - 1], y[k]
        if (y0 <= half <= y1) or (y1 <= half <= y0):
            x0, x1 = x[k - 1], x[k]
            L = float(x0 if y1 == y0 else x0 + (half - y0) * (x1 - x0) / (y1 - y0))
            break
    R = None
    for k in range(i, len(x) - 1):
        y0, y1 = y[k], y[k + 1]
        if (y0 <= half <= y1) or (y1 <= half <= y0):
            x0, x1 = x[k], x[k + 1]
            R = float(x1 if y1 == y0 else x0 + (half - y0) * (x1 - x0) / (y1 - y0))
            break
    if L is None or R is None:
        return None
    return float(abs(R - L))


def main():
    ap = argparse.ArgumentParser(description='Batch FWHM compare tool')
    ap.add_argument('--in-csv', required=True, help='input CSV with columns: type1,file1,type2,file2')
    ap.add_argument('--out-csv', required=True, help='output CSV path')
    args = ap.parse_args()

    rows = []
    with open(args.in_csv, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            t1, f1 = (r.get('type1') or '').strip().lower(), r.get('file1')
            t2, f2 = (r.get('type2') or '').strip().lower(), r.get('file2')
            try:
                if t1 == 'csv':
                    x1, y1 = load_csv_profile(f1)
                elif t1 == 'phits':
                    x1, y1 = parse_phits_out_profile(f1)
                else:
                    raise ValueError('type1 must be csv or phits')
                fwhm1 = compute_fwhm(x1, y1)
            except Exception as e:
                fwhm1 = None
            try:
                if t2 == 'csv':
                    x2, y2 = load_csv_profile(f2)
                elif t2 == 'phits':
                    x2, y2 = parse_phits_out_profile(f2)
                else:
                    raise ValueError('type2 must be csv or phits')
                fwhm2 = compute_fwhm(x2, y2)
            except Exception as e:
                fwhm2 = None
            delta = (fwhm2 - fwhm1) if (fwhm1 is not None and fwhm2 is not None) else None
            rows.append({
                'type1': t1, 'file1': f1, 'FWHM1_cm': ('' if fwhm1 is None else f'{fwhm1:.6f}'),
                'type2': t2, 'file2': f2, 'FWHM2_cm': ('' if fwhm2 is None else f'{fwhm2:.6f}'),
                'Delta_cm': ('' if delta is None else f'{delta:+.6f}')
            })

    with open(args.out_csv, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['type1','file1','FWHM1_cm','type2','file2','FWHM2_cm','Delta_cm'])
        w.writeheader()
        w.writerows(rows)

    print(f'Wrote: {args.out_csv}')


if __name__ == '__main__':
    main()

