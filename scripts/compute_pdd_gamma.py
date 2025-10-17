import re
import sys
import numpy as np
import pymedphys

def load_csv(path):
    import pandas as pd
    df = pd.read_csv(path, encoding='utf-8-sig')
    cols = list(df.columns)[:2]
    df = df[cols]
    df.columns = ['pos', 'dose']
    pos = df['pos'].astype(float).to_numpy()
    dose = df['dose'].astype(float).to_numpy()
    order = np.argsort(pos)
    pos = pos[order]
    dose = dose[order]
    m = np.max(dose)
    dose = dose / m if m > 0 else dose
    return pos, dose

def parse_phits_pdd(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    data_start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('#  y-lower'):
            data_start = i + 1
            break
    if data_start is None:
        raise RuntimeError('Could not find PDD table header (#  y-lower ...) in PHITS file')
    pos = []
    val = []
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
        pos.append((lo + hi)/2.0)
        val.append(v)
    pos = np.asarray(pos, float)
    val = np.asarray(val, float)
    m = np.max(val)
    val = val / m if m > 0 else val
    return pos, val

def gamma_pass(pos_ref_cm, dose_ref_norm, pos_eval_cm, dose_eval_norm, dd, dta, cutoff):
    if np.max(dose_ref_norm) <= 0:
        return 0.0
    ref_pct = dose_ref_norm / np.max(dose_ref_norm) * 100.0
    eval_pct = dose_eval_norm / np.max(dose_ref_norm) * 100.0
    g = pymedphys.gamma(
        axes_reference=(pos_ref_cm*10.0,),
        dose_reference=ref_pct,
        axes_evaluation=(pos_eval_cm*10.0,),
        dose_evaluation=eval_pct,
        dose_percent_threshold=dd,
        distance_mm_threshold=dta,
        lower_percent_dose_cutoff=cutoff,
    )
    v = g[~np.isnan(g)]
    return float(np.sum(v <= 1.0) / v.size * 100.0) if v.size else 0.0

def main():
    if len(sys.argv) != 3:
        print('Usage: python scripts/compute_pdd_gamma.py <phits_deposit_z_out> <measured_pdd_csv>')
        sys.exit(2)
    phits_file = sys.argv[1]
    csv_file = sys.argv[2]
    ref_pos, ref_dose = load_csv(csv_file)
    eval_pos, eval_dose = parse_phits_pdd(phits_file)
    g22 = gamma_pass(ref_pos, ref_dose, eval_pos, eval_dose, dd=2.0, dta=2.0, cutoff=10.0)
    g33 = gamma_pass(ref_pos, ref_dose, eval_pos, eval_dose, dd=3.0, dta=3.0, cutoff=10.0)
    print(f"PDD Gamma pass (2%/2mm/10%): {g22:.2f}%")
    print(f"PDD Gamma pass (3%/3mm/10%): {g33:.2f}%")

if __name__ == '__main__':
    main()
