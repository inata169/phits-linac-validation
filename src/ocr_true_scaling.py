import argparse
import os
import re
import sys
import configparser
from typing import Tuple, Optional

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
    from scipy.signal import savgol_filter
    import pymedphys
except ModuleNotFoundError as e:
    print(
        "Missing dependencies: "
        + str(e)
        + ". Please install: pip install pandas numpy matplotlib scipy pymedphys",
        file=sys.stderr,
    )
    sys.exit(1)


def load_csv_profile(path: str) -> Tuple[np.ndarray, np.ndarray]:
    # Robust CSV loader: try standard CSV, then fallback to whitespace-delimited
    try:
        df0 = pd.read_csv(path, encoding="utf-8-sig", header=None)
    except Exception:
        df0 = pd.read_csv(path, encoding="utf-8-sig", header=None, delim_whitespace=True)
    if df0.shape[1] >= 2 and isinstance(df0.iloc[0, 0], str) and "(cm)" in str(df0.iloc[0, 0]):
        df = pd.read_csv(path, encoding="utf-8-sig")
        cols = list(df.columns)[:2]
        df = df[cols]
        df.columns = ["pos", "dose"]
    else:
        df = df0.iloc[:, :2]
        df.columns = ["pos", "dose"]
    pos = pd.to_numeric(df["pos"], errors="coerce").to_numpy()
    dose = pd.to_numeric(df["dose"], errors="coerce").to_numpy()
    m = np.isfinite(pos) & np.isfinite(dose)
    pos = pos[m]
    dose = dose[m]
    order = np.argsort(pos)
    pos = pos[order]
    dose = dose[order]
    if dose.size == 0:
        raise ValueError(f"CSV has no valid numeric data: {path}")
    dmax = float(np.max(dose))
    if dmax <= 0:
        raise ValueError(f"CSV dose max <= 0: {path}")
    return pos.astype(float), (dose / dmax).astype(float)


def parse_phits_out_profile(path: str) -> Tuple[str, np.ndarray, np.ndarray, dict]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    axis = None
    y_center = None
    for line in lines:
        s = line.strip().lower().replace(" ", "")
        if s.startswith("axis="):
            axis = line.split("=")[1].strip().split("#")[0].strip()
        if re.search(r"^\s*#\s*y\s*=\s*\(", line, flags=re.IGNORECASE):
            nums = re.findall(r"([\-\+\d\.Ee]+)", line)
            if len(nums) >= 2:
                try:
                    y0 = float(nums[0]); y1 = float(nums[1])
                    y_center = 0.5 * (y0 + y1)
                except Exception:
                    pass
    data_start = None
    for i, line in enumerate(lines):
        t = line.strip().lower()
        if t.startswith("#  y-lower") or t.startswith("#  z-lower") or t.startswith("#  x-lower"):
            data_start = i + 1
            break
    if data_start is None:
        raise ValueError(f"Could not find PHITS data table header: {path}")
    pos_centers, vals = [], []
    for line in lines[data_start:]:
        s = line.strip()
        if not s or s.startswith("#"):
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
    if dose.size == 0:
        raise ValueError(f"PHITS data is empty: {path}")
    dmax = float(np.max(dose))
    if dmax <= 0:
        raise ValueError(f"PHITS dose max <= 0: {path}")
    meta = {}
    if y_center is not None:
        meta["y_center_cm"] = y_center
    return axis or "", pos, (dose / dmax), meta


def _extract_depth_cm_from_phits_filename(path: str) -> Optional[float]:
    try:
        base = os.path.basename(path)
        # match ...-200z.out or ...-200x.out or ...-200.out
        m = re.search(r"-(\d+)([a-z])?\.out$", base, flags=re.IGNORECASE)
        if not m:
            return None
        mm = float(m.group(1))
        return mm / 10.0
    except Exception:
        return None


def normalize_pdd(pos_cm: np.ndarray, dose_norm: np.ndarray, mode: str, z_ref_cm: float):
    if mode == "z_ref":
        ref = float(np.interp(z_ref_cm, pos_cm, dose_norm))
        if ref <= 0:
            raise ValueError(f"PDD at z_ref={z_ref_cm} cm <= 0, cannot normalise")
        return pos_cm, (dose_norm / ref)
    dmax = float(np.max(dose_norm))
    return pos_cm, (dose_norm / dmax)


def center_normalise(pos_cm: np.ndarray, dose: np.ndarray, tol_cm: float, interp: bool):
    if pos_cm.size == 0:
        return pos_cm, dose
    idx = int(np.argmin(np.abs(pos_cm)))
    x0 = float(pos_cm[idx])
    pos = pos_cm - x0
    if abs(x0) <= tol_cm:
        c = float(dose[idx])
    else:
        c = None
        if interp and pos_cm.size >= 2:
            for i in range(1, len(pos_cm)):
                xa, xb = float(pos_cm[i - 1]), float(pos_cm[i])
                ya, yb = float(dose[i - 1]), float(dose[i])
                if (xa <= 0.0 <= xb) or (xb <= 0.0 <= xa):
                    c = float(ya + (0.0 - xa) * (yb - ya) / (xb - xa)) if xb != xa else float(ya)
                    break
        if c is None:
            c = float(np.max(dose)) if dose.size else 1.0
    if c <= 0:
        raise ValueError("Center normalisation base <= 0")
    return pos, (dose / c)


def compute_gamma(x_ref_cm, y_ref, x_eval_cm, y_eval, dd, dta, cutoff):
    if np.max(y_ref) <= 0:
        return 0.0
    ref_pct = (y_ref / np.max(y_ref)) * 100.0
    eval_pct = (y_eval / np.max(y_ref)) * 100.0
    g = pymedphys.gamma(
        axes_reference=(x_ref_cm * 10.0,), dose_reference=ref_pct,
        axes_evaluation=(x_eval_cm * 10.0,), dose_evaluation=eval_pct,
        dose_percent_threshold=dd, distance_mm_threshold=dta,
        lower_percent_dose_cutoff=cutoff,
    )
    v = g[~np.isnan(g)]
    return float(np.sum(v <= 1.0) / v.size * 100.0) if v.size else 0.0


def main():
    ap = argparse.ArgumentParser(description='True-scaling OCR comparison (PDD-weighted)')
    ap.add_argument('--ref-pdd-type', choices=['csv', 'phits'], required=True)
    ap.add_argument('--ref-pdd-file', required=True)
    ap.add_argument('--eval-pdd-type', choices=['csv', 'phits'], required=True)
    ap.add_argument('--eval-pdd-file', required=True)
    ap.add_argument('--ref-ocr-type', choices=['csv', 'phits'], required=True)
    ap.add_argument('--ref-ocr-file', required=True)
    ap.add_argument('--eval-ocr-type', choices=['csv', 'phits'], required=True)
    ap.add_argument('--eval-ocr-file', required=True)
    ap.add_argument('--norm-mode', choices=['dmax', 'z_ref'], default='dmax')
    ap.add_argument('--z-ref', type=float, default=10.0)
    ap.add_argument('--dd1', type=float, default=2.0)
    ap.add_argument('--dta1', type=float, default=2.0)
    ap.add_argument('--dd2', type=float, default=3.0)
    ap.add_argument('--dta2', type=float, default=3.0)
    ap.add_argument('--cutoff', type=float, default=10.0)
    ap.add_argument('--smooth-window', type=int, default=5)
    ap.add_argument('--smooth-order', type=int, default=2)
    ap.add_argument('--no-smooth', action='store_true')
    ap.add_argument('--grid', type=float, default=None)
    ap.add_argument('--ymin', type=float, default=None)
    ap.add_argument('--ymax', type=float, default=None)
    ap.add_argument('--export-csv', action='store_true')
    ap.add_argument('--export-gamma', action='store_true')
    ap.add_argument('--xlim-symmetric', action='store_true')
    ap.add_argument('--legend-ref', type=str, default=None)
    ap.add_argument('--legend-eval', type=str, default=None)
    ap.add_argument('--center-tol-cm', type=float, default=0.05)
    ap.add_argument('--center-interp', action='store_true')
    ap.add_argument('--fwhm-warn-cm', type=float, default=1.0)
    ap.add_argument('--output-dir', type=str, default=None)
    args = ap.parse_args()

    # PDD load & normalise (auto-correct types for convenience)
    ref_pdd_type = args.ref_pdd_type
    if ref_pdd_type == 'csv' and os.path.basename(args.ref_pdd_file).lower().endswith('.out'):
        try:
            print(f"警告: ref PDD が .out のため CSV→PHITS に自動切替: {args.ref_pdd_file}", file=sys.stderr)
        except Exception:
            pass
        ref_pdd_type = 'phits'
    if ref_pdd_type == 'csv':
        z_ref_pos, z_ref_dose = load_csv_profile(args.ref_pdd_file)
    else:
        _, z_ref_pos, z_ref_dose, _ = parse_phits_out_profile(args.ref_pdd_file)
    z_ref_pos, z_ref_norm = normalize_pdd(z_ref_pos, z_ref_dose, args.norm_mode, args.z_ref)

    eval_pdd_type = args.eval_pdd_type
    if eval_pdd_type == 'csv' and os.path.basename(args.eval_pdd_file).lower().endswith('.out'):
        try:
            print(f"警告: eval PDD が .out のため CSV→PHITS に自動切替: {args.eval_pdd_file}", file=sys.stderr)
        except Exception:
            pass
        eval_pdd_type = 'phits'
    if eval_pdd_type == 'csv':
        z_eval_pos, z_eval_dose = load_csv_profile(args.eval_pdd_file)
    else:
        _, z_eval_pos, z_eval_dose, _ = parse_phits_out_profile(args.eval_pdd_file)
    z_eval_pos, z_eval_norm = normalize_pdd(z_eval_pos, z_eval_dose, args.norm_mode, args.z_ref)

    # OCR load & center-normalise
    def _guess_type(p: str) -> str:
        b = os.path.basename(p).lower()
        if b.endswith('.out') or b.endswith('.eps'):
            return 'phits'
        if b.endswith('.csv'):
            return 'csv'
        return 'csv'

    ref_ocr_type = args.ref_ocr_type
    if ref_ocr_type == 'csv' and _guess_type(args.ref_ocr_file) == 'phits':
        try:
            print(f"警告: ref OCR が .out のため CSV→PHITS に自動切替: {args.ref_ocr_file}", file=sys.stderr)
        except Exception:
            pass
        ref_ocr_type = 'phits'
    if ref_ocr_type == 'csv':
        x_ref, ocr_ref = load_csv_profile(args.ref_ocr_file)
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*cm", os.path.basename(args.ref_ocr_file), re.IGNORECASE)
        z_depth_ref = float(m.group(1)) if m else args.z_ref
    else:
        axis, pos, dose, meta = parse_phits_out_profile(args.ref_ocr_file)
        z_depth_ref = meta.get('y_center_cm', None)
        if z_depth_ref is None:
            z_depth_ref = _extract_depth_cm_from_phits_filename(args.ref_ocr_file)
        if z_depth_ref is None:
            z_depth_ref = args.z_ref
            try:
                print(f"警告: PHITS OCR(ref) の深さをヘッダ/ファイル名から取得できず z_ref={args.z_ref} cm を使用", file=sys.stderr)
            except Exception:
                pass
        x_ref, ocr_ref = pos, dose
    x_ref, ocr_ref_rel = center_normalise(x_ref, ocr_ref, tol_cm=args.center_tol_cm, interp=args.center_interp)

    eval_ocr_type = args.eval_ocr_type
    if eval_ocr_type == 'csv' and _guess_type(args.eval_ocr_file) == 'phits':
        try:
            print(f"警告: eval OCR が .out のため CSV→PHITS に自動切替: {args.eval_ocr_file}", file=sys.stderr)
        except Exception:
            pass
        eval_ocr_type = 'phits'
    if eval_ocr_type == 'csv':
        x_eval, ocr_eval = load_csv_profile(args.eval_ocr_file)
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*cm", os.path.basename(args.eval_ocr_file), re.IGNORECASE)
        z_depth_eval = float(m.group(1)) if m else args.z_ref
    else:
        axis, pos, dose, meta = parse_phits_out_profile(args.eval_ocr_file)
        z_depth_eval = meta.get('y_center_cm', None)
        if z_depth_eval is None:
            z_depth_eval = _extract_depth_cm_from_phits_filename(args.eval_ocr_file)
        if z_depth_eval is None:
            z_depth_eval = args.z_ref
            try:
                print(f"警告: PHITS OCR(eval) の深さをヘッダ/ファイル名から取得できず z_ref={args.z_ref} cm を使用", file=sys.stderr)
            except Exception:
                pass
        x_eval, ocr_eval = pos, dose
    x_eval, ocr_eval_rel = center_normalise(x_eval, ocr_eval, tol_cm=args.center_tol_cm, interp=args.center_interp)

    # Optional smoothing (renormalise to peak=1 afterwards)
    if not args.no_smooth:
        try:
            w = args.smooth_window if args.smooth_window % 2 == 1 else args.smooth_window + 1
            o = args.smooth_order
            if w > o and len(ocr_ref_rel) >= w:
                ocr_ref_rel = savgol_filter(ocr_ref_rel, w, o)
            if w > o and len(ocr_eval_rel) >= w:
                ocr_eval_rel = savgol_filter(ocr_eval_rel, w, o)
            if np.max(ocr_ref_rel) > 0:
                ocr_ref_rel = ocr_ref_rel / np.max(ocr_ref_rel)
            if np.max(ocr_eval_rel) > 0:
                ocr_eval_rel = ocr_eval_rel / np.max(ocr_eval_rel)
        except Exception:
            pass

    # True series
    s_axis_ref = float(np.interp(z_depth_ref, z_ref_pos, z_ref_norm))
    s_axis_eval = float(np.interp(z_depth_eval, z_eval_pos, z_eval_norm))
    y_true_ref = s_axis_ref * ocr_ref_rel
    y_true_eval = s_axis_eval * ocr_eval_rel

    # RMSE and gamma
    grid_step = args.grid
    if grid_step is None:
        cfg = configparser.ConfigParser()
        prj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg_path = os.path.join(prj_root, 'config.ini')
        if os.path.exists(cfg_path):
            try:
                cfg.read(cfg_path, encoding='utf-8')
                grid_step = float(cfg.get('Processing', 'resample_grid_cm', fallback='0.1'))
            except Exception:
                grid_step = 0.1
        else:
            grid_step = 0.1

    def resample(x1, y1, x2, y2, step):
        if not step or step <= 0:
            return None, None, None
        xmin = max(np.min(x1), np.min(x2)); xmax = min(np.max(x1), np.max(x2))
        if xmax - xmin <= step * 2:
            return None, None, None
        n = int(np.floor((xmax - xmin) / step)) + 1
        grid = xmin + np.arange(n + 1) * step
        return grid, np.interp(grid, x1, y1), np.interp(grid, x2, y2)

    grid, y_ref_g, y_eval_g = resample(x_ref, y_true_ref, x_eval, y_true_eval, grid_step)
    if grid is not None:
        rmse = float(np.sqrt(np.mean((y_ref_g - y_eval_g) ** 2)))
        xr, yr = grid, y_ref_g
        xe, ye = grid, y_eval_g
    else:
        rmse = float(np.sqrt(np.mean((np.interp(x_ref, x_eval, y_true_eval) - y_true_ref) ** 2)))
        xr, yr = x_ref, y_true_ref
        xe, ye = x_eval, y_true_eval

    g1 = compute_gamma(xr, yr, xe, ye, args.dd1, args.dta1, args.cutoff)
    g2 = compute_gamma(xr, yr, xe, ye, args.dd2, args.dta2, args.cutoff)
    print("RMSE: {:.6f}".format(rmse))
    print("Gamma pass (DD={:.1f}%, DTA={:.1f}mm, Cutoff={:.1f}%): {:.2f}%".format(args.dd1, args.dta1, args.cutoff, g1))
    print("Gamma pass (DD={:.1f}%, DTA={:.1f}mm, Cutoff={:.1f}%): {:.2f}%".format(args.dd2, args.dta2, args.cutoff, g2))

    # FWHM check
    def fwhm(x, y):
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
        return None if (L is None or R is None) else float(abs(R - L))

    f1 = fwhm(x_ref, ocr_ref_rel); f2 = fwhm(x_eval, ocr_eval_rel)
    f_delta = None
    if f1 is not None and f2 is not None:
        f_delta = f2 - f1
        if abs(f_delta) > float(args.fwhm_warn_cm):
            print(
                "Warning: FWHM mismatch |delta|={:.3f} cm (> {:.3f} cm). ref={:.3f} cm, eval={:.3f} cm".format(
                    abs(f_delta), float(args.fwhm_warn_cm), f1, f2
                ),
                file=sys.stderr,
            )

    # Outputs
    prj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_root = args.output_dir or os.path.join(prj_root, 'output')
    plot_dir = os.path.join(out_root, 'plots')
    report_dir = os.path.join(out_root, 'reports')
    data_dir = os.path.join(out_root, 'data')
    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    ref_base = os.path.splitext(os.path.basename(args.ref_ocr_file))[0]
    eval_base = os.path.splitext(os.path.basename(args.eval_ocr_file))[0]
    title = (
        "True-scaling (PDD-weighted)\n"
        + "norm={}, z_ref={} cm / ref_z={:.3f} cm, eval_z={:.3f} cm".format(
            args.norm_mode, args.z_ref, z_depth_ref, z_depth_eval
        )
    )
    try:
        import matplotlib as _mpl
        _mpl.rcParams['font.family'] = ['DejaVu Sans', 'Arial']
        _mpl.rcParams['axes.unicode_minus'] = False
    except Exception:
        pass

    plt.figure(figsize=(12, 8))
    plt.plot(x_ref, y_true_ref, label=args.legend_ref or 'Reference')
    plt.plot(x_eval, y_true_eval, label=args.legend_eval or 'Evaluation')
    plt.title(title)
    plt.xlabel('x (cm)')
    plt.ylabel('True dose (a.u.)')
    plt.grid(True, alpha=0.3)
    if args.ymin is not None or args.ymax is not None:
        plt.ylim(args.ymin, args.ymax)
    if args.xlim_symmetric:
        xmax = max(abs(np.min(x_ref)), abs(np.max(x_ref)), abs(np.min(x_eval)), abs(np.max(x_eval)))
        plt.xlim(-xmax, xmax)
    plt.legend()
    plot_path = os.path.join(plot_dir, f"TrueComp_{ref_base}_vs_{eval_base}_norm-{args.norm_mode}_zref-{args.z_ref:g}_z-{z_depth_ref:g}-{z_depth_eval:g}.png")
    plt.savefig(plot_path)
    print("Plot saved: " + plot_path)

    report_path = os.path.join(report_dir, f"TrueReport_{ref_base}_vs_{eval_base}_norm-{args.norm_mode}_zref-{args.z_ref:g}_z-{z_depth_ref:g}-{z_depth_eval:g}.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# True scaling report\n\n')
        f.write('## Inputs\n')
        f.write(f"ref PDD: {args.ref_pdd_type} | {args.ref_pdd_file}\n")
        f.write(f"eval PDD: {args.eval_pdd_type} | {args.eval_pdd_file}\n")
        f.write(f"ref OCR: {args.ref_ocr_type} | {args.ref_ocr_file}\n")
        f.write(f"eval OCR: {args.eval_ocr_type} | {args.eval_ocr_file}\n")
        f.write('\n## Params\n')
        f.write(f"norm-mode: {args.norm_mode}, z_ref: {args.z_ref} cm\n")
        f.write(f"ref depth (cm): {z_depth_ref:.6f}, eval depth (cm): {z_depth_eval:.6f}\n")
        f.write(f"S_axis(ref): {s_axis_ref:.6f}, S_axis(eval): {s_axis_eval:.6f}\n")
        f.write(f"grid (cm): {grid_step:.6f}\n")
        f.write('\n## Results\n')
        f.write(f"RMSE: {rmse:.6f}\n")
        f.write(f"Gamma 1 (DD={args.dd1:.1f}%, DTA={args.dta1:.1f}mm, Cutoff={args.cutoff:.1f}%): {g1:.2f}%\n")
        f.write(f"Gamma 2 (DD={args.dd2:.1f}%, DTA={args.dta2:.1f}mm, Cutoff={args.cutoff:.1f}%): {g2:.2f}%\n")
        # FWHM summary in report
        def _fmt(v):
            try:
                return ("{:.6f}".format(float(v))) if (v is not None and np.isfinite(float(v))) else "N/A"
            except Exception:
                return "N/A"
        f.write(f"FWHM(ref) (cm): {_fmt(f1)}\n")
        f.write(f"FWHM(eval) (cm): {_fmt(f2)}\n")
        f.write(f"FWHM delta (eval-ref) (cm): {_fmt(f_delta)}\n")
    print("Report saved: " + report_path)

    # CSV exports
    if args.export_csv:
        pd.DataFrame({'x_cm': x_ref, 'true_dose': y_true_ref}).to_csv(
            os.path.join(data_dir, f"TrueRef_{ref_base}_z{z_depth_ref:g}.csv"), index=False, encoding='utf-8'
        )
        pd.DataFrame({'x_cm': x_eval, 'true_dose': y_true_eval}).to_csv(
            os.path.join(data_dir, f"TrueEval_{eval_base}_z{z_depth_eval:g}.csv"), index=False, encoding='utf-8'
        )
        if grid is not None:
            pd.DataFrame({'x_cm': xr, 'true_dose': yr}).to_csv(
                os.path.join(data_dir, f"TrueRefResampled_{ref_base}_z{z_depth_ref:g}_grid{grid_step:g}.csv"), index=False, encoding='utf-8'
            )
            pd.DataFrame({'x_cm': xe, 'true_dose': ye}).to_csv(
                os.path.join(data_dir, f"TrueEvalResampled_{eval_base}_z{z_depth_eval:g}_grid{grid_step:g}.csv"), index=False, encoding='utf-8'
            )
        if args.export_gamma:
            ref_pct = (yr / np.max(yr)) * 100.0 if np.max(yr) > 0 else yr
            eval_pct = (ye / np.max(yr)) * 100.0 if np.max(yr) > 0 else ye
            g = pymedphys.gamma(
                axes_reference=(xr * 10.0,), dose_reference=ref_pct,
                axes_evaluation=(xe * 10.0,), dose_evaluation=eval_pct,
                dose_percent_threshold=args.dd1,
                distance_mm_threshold=args.dta1,
                lower_percent_dose_cutoff=args.cutoff,
            )
            pd.DataFrame({'x_cm': xr, 'true_ref': yr, 'true_eval_interp': np.interp(xr, xe, ye), 'gamma': g}).to_csv(
                os.path.join(data_dir, f"Gamma_{ref_base}_vs_{eval_base}_z{z_depth_ref:g}-{z_depth_eval:g}.csv"), index=False, encoding='utf-8'
            )


if __name__ == '__main__':
    main()
