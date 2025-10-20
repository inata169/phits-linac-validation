import argparse
import os
import re
import sys
import configparser
from typing import Tuple, Optional

import numpy as np
import pandas as pd
import shutil

try:
    import pymedphys
    import matplotlib.pyplot as plt
    from scipy.signal import savgol_filter
except ModuleNotFoundError as e:
    print(f"萓晏ｭ倥Λ繧､繝悶Λ繝ｪ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {e}. pip install pymedphys matplotlib scipy 繧貞ｮ溯｡後＠縺ｦ縺上□縺輔＞縲・, file=sys.stderr)
    sys.exit(1)


def load_csv_profile(path: str) -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(path, encoding='utf-8-sig', header=None)
    # 繝倥ャ繝陦後′縺ゅｋ蝣ｴ蜷医ｒ閠・・: 蜈磯ｭ陦後↓(cm)縺後≠繧後・繧ｹ繧ｭ繝・・
    if df.shape[1] >= 2 and isinstance(df.iloc[0, 0], str) and '(cm)' in df.iloc[0, 0]:
        df = pd.read_csv(path, encoding='utf-8-sig')
        # 蜈磯ｭ2蛻励↓髯仙ｮ・
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
    # 菴咲ｽｮ縺ｧ譏・・た繝ｼ繝茨ｼ郁｣憺俣縺ｮ螳牙ｮ壼喧縺ｮ縺溘ａ・・
    order = np.argsort(pos)
    pos = pos[order]
    dose = dose[order]
    # 豁｣隕丞喧 [0,1]
    if dose.size == 0:
        raise ValueError(f"CSV縺ｫ譛牙柑縺ｪ謨ｰ蛟､繝・・繧ｿ縺後≠繧翫∪縺帙ｓ: {path}")
    dmax = np.max(dose)
    if dmax <= 0:
        raise ValueError(f"CSV縺ｮ邱夐㍼譛螟ｧ蛟､縺・莉･荳九〒縺・ {path}")
    dose_norm = dose / dmax
    return pos.astype(float), dose_norm.astype(float)


def parse_phits_out_profile(path: str) -> Tuple[str, np.ndarray, np.ndarray, dict]:
    """
    PHITS [T-Deposit] 蜃ｺ蜉帙°繧・D繝励Ο繝輔ぃ繧､繝ｫ繧呈歓蜃ｺ縲・
    謌ｻ繧雁､: (axis, pos_cm, dose_norm, meta)
    - axis: 'x'/'y'/'z' 縺ｮ縺・■縲∝・蜉幄ｻｸ・・axis =" 縺ｫ萓晏ｭ假ｼ・
    - pos_cm: 繝薙Φ荳ｭ蠢・ｽ咲ｽｮ・・m・・
    - dose_norm: 繝薙Φ縺ｮ邱夐㍼・域怙螟ｧ=1縺ｧ豁｣隕丞喧・・
    - meta: 霑ｽ蜉諠・ｱ・井ｾ・ y-slab遽・峇縺ｪ縺ｩ・・
    """
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    axis = None
    y_slab = None
    # 霆ｸ繝ｻ繧ｹ繝ｩ繝匁ュ蝣ｱ
    for i, line in enumerate(lines):
        s = line.strip().lower().replace(' ', '')
        if s.startswith('axis='):
            axis = line.split('=')[1].strip().split('#')[0].strip()
        if re.search(r"^\s*#\s*y\s*=\s*\(", line, flags=re.IGNORECASE):
            m = re.findall(r'([\-\+\d\.Ee]+)', line)
            if len(m) >= 2:
                try:
                    y_low = float(m[0])
                    y_high = float(m[1])
                    y_slab = (y_low + y_high) / 2.0
                except Exception:
                    pass

    # 繝・・繧ｿ驛ｨ繧呈爾縺・ 繝倥ャ繝 'h:' 縺ｮ蠕後・#  y-lower      y-upper      all         r.err" 陦後↓邯壹￥謨ｰ陦ｨ
    data_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('#  y-lower'):
            data_start = i + 1
            break
        if line.strip().startswith('#  z-lower'):
            data_start = i + 1
            break
        if line.strip().startswith('#  x-lower'):
            data_start = i + 1
            break
    if data_start is None:
        raise ValueError(f"PHITS繝・・繧ｿ陦ｨ縺ｮ髢句ｧ倶ｽ咲ｽｮ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {path}")

    pos_centers = []
    vals = []
    for line in lines[data_start:]:
        s = line.strip()
        if not s:
            break
        if s.startswith('#'):
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
        raise ValueError(f"PHITS繝・・繧ｿ縺檎ｩｺ縺ｧ縺・ {path}")
    dmax = np.max(dose)
    if dmax <= 0:
        raise ValueError(f"PHITS邱夐㍼譛螟ｧ蛟､縺・莉･荳九〒縺・ {path}")
    dose_norm = dose / dmax
    meta = {}
    if y_slab is not None:
        meta['y_center_cm'] = y_slab
    return (axis or ''), pos, dose_norm, meta

def _extract_depth_cm_from_csv_filename(filename: str) -> Optional[float]:
    try:
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*cm", os.path.basename(filename), re.IGNORECASE)
        return float(m.group(1)) if m else None
    except Exception:
        return None

def _extract_depth_cm_from_phits_filename(filename: str) -> Optional[float]:
    try:
        base = os.path.basename(filename)
        m = re.search(r"-(\d+)([a-z])?\.out$", base, re.IGNORECASE)
        if not m:
            return None
        mm = float(m.group(1))
        return mm / 10.0
    except Exception:
        return None


def normalize_pdd(pos_cm: np.ndarray, dose_norm: np.ndarray, mode: str, z_ref_cm: float) -> Tuple[np.ndarray, np.ndarray]:
    if mode == 'z_ref':
        # 蜿ら・豺ｱ縺ｧ1.0縺ｫ縺ｪ繧九ｈ縺・ｭ｣隕丞喧
        ref = np.interp(z_ref_cm, pos_cm, dose_norm)
        if ref <= 0:
            raise ValueError(f"z_ref={z_ref_cm} cm 縺ｮPDD縺・莉･荳九・縺溘ａ豁｣隕丞喧縺ｧ縺阪∪縺帙ｓ")
        return pos_cm, (dose_norm / ref)
    # 譌｢螳・dmax
    dmax = np.max(dose_norm)
    return pos_cm, (dose_norm / dmax)


def ocr_center_normalize(pos_cm: np.ndarray, dose_norm: np.ndarray, tol_cm: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """荳ｭ蠢・繝薙・繝荳ｭ蠢・縺ｮ菴咲ｽｮ縺ｨ謖ｯ蟷・ｒ豁｣隕丞喧縲・
    - 菴咲ｽｮ: 荳ｭ蠢・呵｣懊・蠎ｧ讓吶ｒ0 cm縺ｫ蟷ｳ陦檎ｧｻ蜍包ｼ亥ｺｧ讓吝・荳ｭ蠢・喧・・
    - 謖ｯ蟷・ 荳ｭ蠢・せ縺ｮ邱夐㍼繧・.00縺ｫ繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ・郁ｿ大ｍﾂｱtol縺ｫ轤ｹ縺檎┌縺代ｌ縺ｰ譛螟ｧ蛟､・・
    """
    # 荳ｭ蠢・呵｣懊・繧､繝ｳ繝・ャ繧ｯ繧ｹ・・=0縺ｫ譛繧りｿ代＞・・
    idx_center = int(np.argmin(np.abs(pos_cm))) if pos_cm.size else 0
    x_center = pos_cm[idx_center] if pos_cm.size else 0.0
    # 蠎ｧ讓吶ｒ荳ｭ蠢・′0縺ｫ縺ｪ繧九ｈ縺・↓蟷ｳ陦檎ｧｻ蜍・
    pos_centered = pos_cm - x_center
    # 謖ｯ蟷・せ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ蜿ら・蛟､
    if abs(x_center) <= tol_cm:
        c = dose_norm[idx_center]
    else:
        # 霑大ｍ縺ｫ荳ｭ蠢・し繝ｳ繝励Ν縺檎┌縺・ｴ蜷医・譛螟ｧ蛟､繧貞渕貅悶→縺吶ｋ
        c = float(np.max(dose_norm)) if dose_norm.size else 1.0
    if c <= 0:
        raise ValueError("OCR荳ｭ蠢・ｭ｣隕丞喧縺ｮ蝓ｺ貅悶′0莉･荳九〒縺・)
    return pos_centered, (dose_norm / c)


def ocr_center_normalize_with_options(pos_cm: np.ndarray, dose_norm: np.ndarray,
                                      tol_cm: float = 0.05, interp: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """荳ｭ蠢・ｽ咲ｽｮ蜷医ｏ縺帙→謖ｯ蟷・・荳ｭ蠢・ｭ｣隕丞喧・郁｣憺俣繧ｪ繝励す繝ｧ繝ｳ莉倥″・峨・    - 菴咲ｽｮ: 荳ｭ蠢・↓譛繧りｿ代＞繧ｵ繝ｳ繝励Ν縺ｮ蠎ｧ讓吶ｒ蜴溽せ縺ｸ蟷ｳ陦檎ｧｻ蜍・    - 謖ｯ蟷・ x=0 縺ｮ蛟､繧貞渕貅悶↓ 1.00 縺ｸ繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ・・=0 繧ｵ繝ｳ繝励Ν縺・tol 莉･蜀・↓辟｡縺・ｴ蜷医（nterp 謖・ｮ壽凾縺ｯ邱壼ｽ｢陬憺俣繧定ｩｦ縺ｿ繧九ゆｸ榊庄縺ｪ繧画怙螟ｧ蛟､縺ｧ莉｣逕ｨ・・    """
    if pos_cm.size == 0:
        return pos_cm, dose_norm
    idx_center = int(np.argmin(np.abs(pos_cm)))
    x_center = float(pos_cm[idx_center])
    pos_centered = pos_cm - x_center
    if abs(x_center) <= float(tol_cm):
        c = float(dose_norm[idx_center])
    else:
        c = None
        if interp and pos_cm.size >= 2:
            for i in range(1, len(pos_cm)):
                x0, x1 = float(pos_cm[i - 1]), float(pos_cm[i])
                y0, y1 = float(dose_norm[i - 1]), float(dose_norm[i])
                if (x0 <= 0.0 <= x1) or (x1 <= 0.0 <= x0):
                    if x1 != x0:
                        c = float(y0 + (0.0 - x0) * (y1 - y0) / (x1 - x0))
                    else:
                        c = float(y0)
                    break
        if c is None:
            c = float(np.max(dose_norm)) if dose_norm.size else 1.0
    if c <= 0:
        raise ValueError("OCR荳ｭ蠢・ｭ｣隕丞喧縺ｮ蝓ｺ貅悶′0莉･荳九〒縺・)
    return pos_centered, (dose_norm / c)

def resample_common_grid(x1: np.ndarray, y1: np.ndarray, x2: np.ndarray, y2: np.ndarray, step_cm: Optional[float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not step_cm or step_cm <= 0:
        return None, None, None
    xmin = max(np.min(x1), np.min(x2))
    xmax = min(np.max(x1), np.max(x2))
    if xmax - xmin <= step_cm * 2:
        return None, None, None
    n = int(np.floor((xmax - xmin) / step_cm)) + 1
    grid = xmin + np.arange(n + 1) * step_cm
    y1g = np.interp(grid, x1, y1)
    y2g = np.interp(grid, x2, y2)
    return grid, y1g, y2g


def compute_rmse(y_ref: np.ndarray, y_eval: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_ref - y_eval) ** 2)))


def compute_gamma_pass(x_ref_cm: np.ndarray, y_ref_true: np.ndarray,
                       x_eval_cm: np.ndarray, y_eval_true: np.ndarray,
                       dd_percent: float, dta_mm: float, cutoff_percent: float) -> float:
    # ﾎｳ縺ｮ縺溘ａ縲∝渕貅悶ｒ%繧ｹ繧ｱ繝ｼ繝ｫ縺ｸ・域怙螟ｧ=100%・・
    if np.max(y_ref_true) <= 0:
        return 0.0
    ref_pct = (y_ref_true / np.max(y_ref_true)) * 100.0
    eval_pct = (y_eval_true / np.max(y_ref_true)) * 100.0  # 蝓ｺ貅匁ｭ｣隕丞喧縺ｫ蜷医ｏ縺帙ｋ
    # 霆ｸ繧知m縺ｸ
    x_ref_mm = x_ref_cm * 10.0
    x_eval_mm = x_eval_cm * 10.0
    gamma = pymedphys.gamma(
        axes_reference=(x_ref_mm,),
        dose_reference=ref_pct,
        axes_evaluation=(x_eval_mm,),
        dose_evaluation=eval_pct,
        dose_percent_threshold=dd_percent,
        distance_mm_threshold=dta_mm,
        lower_percent_dose_cutoff=cutoff_percent,
    )
    valid = gamma[~np.isnan(gamma)]
    if valid.size == 0:
        return 0.0
    return float(np.sum(valid <= 1.0) / valid.size * 100.0)


def main():
    parser = argparse.ArgumentParser(description='PDD驥阪∩莉倥￠逵溷､繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ縺ｧOCR繧呈ｯ碑ｼ・(ﾎｳ/RMSE)')
    # PDD 蜈･蜉・
    parser.add_argument('--ref-pdd-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--ref-pdd-file', required=True)
    parser.add_argument('--eval-pdd-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--eval-pdd-file', required=True)
    # OCR 蜈･蜉・
    parser.add_argument('--ref-ocr-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--ref-ocr-file', required=True)
    parser.add_argument('--eval-ocr-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--eval-ocr-file', required=True)
    # 豁｣隕丞喧
    parser.add_argument('--norm-mode', choices=['dmax', 'z_ref'], default='dmax')
    parser.add_argument('--z-ref', type=float, default=10.0)
    # 隧穂ｾ｡譚｡莉ｶ
    parser.add_argument('--dd1', type=float, default=2.0)
    parser.add_argument('--dta1', type=float, default=2.0)
    parser.add_argument('--dd2', type=float, default=3.0)
    parser.add_argument('--dta2', type=float, default=3.0)
    parser.add_argument('--cutoff', type=float, default=10.0)
    # 蟷ｳ貊大喧繝ｻ蜀阪し繝ｳ繝励Ν繝ｻ蜿ｯ隕門喧
    parser.add_argument('--smooth-window', type=int, default=5, help='Savitzky-Golay蟷ｳ貊代・繧ｦ繧｣繝ｳ繝峨え・亥･・焚, 繝・ヵ繧ｩ繝ｫ繝・・・)
    parser.add_argument('--smooth-order', type=int, default=2, help='Savitzky-Golay蟷ｳ貊代・谺｡謨ｰ・医ョ繝輔か繝ｫ繝・・・)
    parser.add_argument('--no-smooth', action='store_true', help='蟷ｳ貊大喧繧堤┌蜉ｹ蛹悶☆繧・)
    parser.add_argument('--grid', type=float, default=None, help='RMSE/蜿ｯ隕門喧縺ｮ蜈ｱ騾壹げ繝ｪ繝・ラ蛻ｻ縺ｿ[cm] (譛ｪ謖・ｮ壹・config.ini縺ｮProcessing.resample_grid_cm)')
    parser.add_argument('--ymin', type=float, default=None, help='繝励Ο繝・ヨ縺ｮY譛蟆丞､')
    parser.add_argument('--ymax', type=float, default=None, help='繝励Ο繝・ヨ縺ｮY譛螟ｧ蛟､')
    parser.add_argument('--export-csv', action='store_true', help='逵溷､邉ｻ蛻暦ｼ亥ｿ・ｦ√↓蠢懊§縺ｦ蜀阪し繝ｳ繝励Ν邉ｻ蛻励ｂ・峨ｒCSV縺ｫ菫晏ｭ倥☆繧・)
    parser.add_argument('--export-gamma', action='store_true', help='蝓ｺ貅也ｳｻ蛻礼せ縺斐→縺ｮﾎｳ繧辰SV縺ｫ菫晏ｭ倥☆繧具ｼ亥・騾壹げ繝ｪ繝・ラ菴ｿ逕ｨ譎ゅ・縺昴・繧ｰ繝ｪ繝・ラ縺ｧ・・)
    parser.add_argument('--xlim-symmetric', action='store_true', help='讓ｪ霆ｸ繧貞次轤ｹ蟇ｾ遘ｰ遽・峇縺ｫ險ｭ螳壹☆繧・)
    parser.add_argument('--legend-ref', type=str, default=None, help='蜃｡萓九・ref繝ｩ繝吶Ν繧呈欠螳・)
    parser.add_argument('--legend-eval', type=str, default=None, help='蜃｡萓九・eval繝ｩ繝吶Ν繧呈欠螳・)
    parser.add_argument('--center-tol-cm', type=float, default=0.05, help='荳ｭ蠢・ｭ｣隕丞喧縺ｧx=0霑大ｍ縺ｨ隕九↑縺呵ｨｱ螳ｹ遽・峇[cm]・域里螳・.05・・)
    parser.add_argument('--center-interp', action='store_true', help='x=0縺ｫ繧ｵ繝ｳ繝励Ν縺檎┌縺・ｴ蜷医∫ｷ壼ｽ｢陬憺俣縺ｧx=0縺ｮ蛟､繧呈耳螳壹＠縺ｦ荳ｭ蠢・ｭ｣隕丞喧縺ｫ菴ｿ逕ｨ縺吶ｋ')
    parser.add_argument('--fwhm-warn-cm', type=float, default=1.0, help='|ΔFWHM|がこの閾値[cm]を超えた場合に警告を出力（OCR相対プロファイルから算出）')

    # OCR 隱ｭ縺ｿ霎ｼ縺ｿ繝ｻ荳ｭ蠢・ｭ｣隕丞喧・・val・・
    if args.eval_ocr_type == 'csv':
        x_eval, ocr_eval = load_csv_profile(args.eval_ocr_file)
        depth_csv = _extract_depth_cm_from_csv_filename(args.eval_ocr_file)
        if depth_csv is not None:
            z_depth_eval = float(depth_csv)
        else:
            z_depth_eval = args.z_ref
            print(f"隴ｦ蜻・ OCR(CSV) 縺ｮ豺ｱ縺輔ｒ繝輔ぃ繧､繝ｫ蜷阪°繧牙叙蠕励〒縺阪∪縺帙ｓ縺ｧ縺励◆縲・_ref={args.z_ref} cm 繧剃ｽｿ逕ｨ縺励∪縺・, file=sys.stderr)
    else:
        axis, pos, dose, meta = parse_phits_out_profile(args.eval_ocr_file)
        z_depth_eval = meta.get('y_center_cm', None)
        if z_depth_eval is None:
            depth_from_name = _extract_depth_cm_from_phits_filename(args.eval_ocr_file)
            if depth_from_name is not None:
                z_depth_eval = float(depth_from_name)
            else:
                z_depth_eval = args.z_ref
                print(f"隴ｦ蜻・ OCR(PHITS) 縺ｮ豺ｱ縺輔ｒy繧ｹ繝ｩ繝・繝輔ぃ繧､繝ｫ蜷阪°繧牙叙蠕励〒縺阪∪縺帙ｓ縺ｧ縺励◆縲・_ref={args.z_ref} cm 繧剃ｽｿ逕ｨ縺励∪縺・, file=sys.stderr)
        x_eval, ocr_eval = pos, dose
    x_eval, ocr_eval_rel = ocr_center_normalize_with_options(x_eval, ocr_eval, tol_cm=args.center_tol_cm, interp=args.center_interp)

    # 霆ｽ縺・ｹｳ貊大喧・・avitzky窶敵olay・峨ゅョ繝ｼ繧ｿ轤ｹ謨ｰ縺御ｸ崎ｶｳ/譚｡莉ｶ荳堺ｸ閾ｴ縺ｪ繧峨せ繧ｭ繝・・
    if not args.no_smooth:
        try:
            w = args.smooth_window if args.smooth_window % 2 == 1 else args.smooth_window + 1
            o = args.smooth_order
            if w > o and len(ocr_ref_rel) >= w:
                ocr_ref_rel = savgol_filter(ocr_ref_rel, w, o)
            if w > o and len(ocr_eval_rel) >= w:
                ocr_eval_rel = savgol_filter(ocr_eval_rel, w, o)
            # 蟷ｳ貊大ｾ後ｂ譛螟ｧ蛟､縺・.00縺ｨ縺ｪ繧九ｈ縺・・豁｣隕丞喧
            ref_max = float(np.max(ocr_ref_rel)) if len(ocr_ref_rel) else 1.0
            eval_max = float(np.max(ocr_eval_rel)) if len(ocr_eval_rel) else 1.0
            if ref_max > 0:
                ocr_ref_rel = (ocr_ref_rel / ref_max)
            if eval_max > 0:
                ocr_eval_rel = (ocr_eval_rel / eval_max)
        except Exception:
            pass

    # True(x,z) 讒狗ｯ・
    s_axis_ref = float(np.interp(z_depth_ref, z_ref_pos, z_ref_norm))
    s_axis_eval = float(np.interp(z_depth_eval, z_eval_pos, z_eval_norm))
    # FWHM・育嶌蟇ｾOCR縺ｧ險育ｮ暦ｼ・
    def _compute_fwhm(pos_cm: np.ndarray, dose_norm: np.ndarray) -> Optional[float]:
        if pos_cm.size < 3 or dose_norm.size < 3:
            return None
        imax = int(np.argmax(dose_norm))
        peak = float(dose_norm[imax])
        if peak <= 0:
            return None
        half = peak * 0.5
        left = None
        for i in range(imax, 0, -1):
            y0, y1 = dose_norm[i - 1], dose_norm[i]
            if (y0 <= half <= y1) or (y1 <= half <= y0):
                x0, x1 = pos_cm[i - 1], pos_cm[i]
                left = float(x0) if (y1 == y0) else float(x0 + (half - y0) * (x1 - x0) / (y1 - y0))
                break
        right = None
        for i in range(imax, len(pos_cm) - 1):
            y0, y1 = dose_norm[i], dose_norm[i + 1]
            if (y0 <= half <= y1) or (y1 <= half <= y0):
                x0, x1 = pos_cm[i], pos_cm[i + 1]
                right = float(x1) if (y1 == y0) else float(x0 + (half - y0) * (x1 - x0) / (y1 - y0))
                break
        if left is None or right is None:
            return None
        return float(abs(right - left))

    fwhm_ref = _compute_fwhm(x_ref, ocr_ref_rel)
    fwhm_eval = _compute_fwhm(x_eval, ocr_eval_rel)
    fwhm_delta = None
    if fwhm_ref is not None and fwhm_eval is not None:
        fwhm_delta = fwhm_eval - fwhm_ref
        try:
            thr = float(args.fwhm_warn_cm)
        except Exception:
            thr = 1.0
        if abs(fwhm_delta) > thr:
            print(f"隴ｦ蜻・ FWHM繝溘せ繝槭ャ繝・|ﾎ培={abs(fwhm_delta):.3f} cm (> {thr:.3f} cm). ref={fwhm_ref:.3f} cm, eval={fwhm_eval:.3f} cm", file=sys.stderr)
            # 辣ｧ蟆・㍽縺ｮ蛟呵｣彝ev繧偵ヲ繝ｳ繝郁｡ｨ遉ｺ・育ｵ碁ｨ灘援・・            try:
                ref_name = os.path.basename(args.ref_ocr_file).lower()
                hint = None
                if '05x05m' in ref_name or '5x5' in ref_name:
                    hint = '5x5 竊・Rev80-5x5-...・医∪縺溘・ Rev60-5x5-...・・
                elif '10x10m' in ref_name or '10x10' in ref_name:
                    hint = '10x10 竊・Rev70-c8-0.49n'
                elif '30x30m' in ref_name or '30x30' in ref_name:
                    hint = '30x30 竊・Rev50-30x30--c8-0.49n'
                if hint:
                    print(f"繝偵Φ繝・ 豈碑ｼ・ｯｾ雎｡縺ｮPHITS繝・・繧ｿ縺ｮ辣ｧ蟆・㍽縺檎焚縺ｪ繧句庄閭ｽ諤ｧ縺後≠繧翫∪縺呻ｼ・hint}・峨・, file=sys.stderr)
            except Exception:
                pass

    y_true_ref = s_axis_ref * ocr_ref_rel
    y_true_eval = s_axis_eval * ocr_eval_rel

    # RMSE・亥・騾壹げ繝ｪ繝・ラ・・
    grid, y_ref_g, y_eval_g = resample_common_grid(x_ref, y_true_ref, x_eval, y_true_eval, grid_step)
    if grid is not None:
        rmse = compute_rmse(y_ref_g, y_eval_g)
        print(f"RMSE (蜈ｱ騾壹げ繝ｪ繝・ラ {grid_step:.3f} cm): {rmse:.6f}")
        x_for_gamma_ref = grid
        y_for_gamma_ref = y_ref_g
        x_for_gamma_eval = grid
        y_for_gamma_eval = y_eval_g
    else:
        rmse = compute_rmse(np.interp(x_ref, x_eval, y_true_eval), y_true_ref) if x_eval.size > 1 else compute_rmse(y_true_ref, y_true_eval)
        print(f"RMSE: {rmse:.6f}")
        x_for_gamma_ref = x_ref
        y_for_gamma_ref = y_true_ref
        x_for_gamma_eval = x_eval
        y_for_gamma_eval = y_true_eval

    # ﾎｳ・井ｸｻ隕・蜑ｯ谺｡・・
    g1 = compute_gamma_pass(x_for_gamma_ref, y_for_gamma_ref, x_for_gamma_eval, y_for_gamma_eval,
                            dd_percent=args.dd1, dta_mm=args.dta1, cutoff_percent=args.cutoff)
    g2 = compute_gamma_pass(x_for_gamma_ref, y_for_gamma_ref, x_for_gamma_eval, y_for_gamma_eval,
                            dd_percent=args.dd2, dta_mm=args.dta2, cutoff_percent=args.cutoff)
    print(f"Gamma pass (DD={args.dd1:.1f}%, DTA={args.dta1:.1f}mm, Cutoff={args.cutoff:.1f}%): {g1:.2f}%")
    print(f"Gamma pass (DD={args.dd2:.1f}%, DTA={args.dta2:.1f}mm, Cutoff={args.cutoff:.1f}%): {g2:.2f}%")

    # 蜃ｺ蜉帛・・・utput/plots, output/reports・・
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_root = None
    cfg_out = configparser.ConfigParser()
    cfg_path = os.path.join(project_root, 'config.ini')
    if os.path.exists(cfg_path):
        try:
            cfg_out.read(cfg_path, encoding='utf-8')
            out_root = cfg_out.get('Paths', 'output_dir', fallback=None)
        except Exception:
            out_root = None
    if not out_root:
        out_root = os.path.join(project_root, 'output')
    plot_dir = os.path.join(out_root, 'plots')
    report_dir = os.path.join(out_root, 'reports')
    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    # 蝗ｳ菫晏ｭ假ｼ・rue 繧ｹ繧ｱ繝ｼ繝ｫ縺ｮ豈碑ｼ・ｼ・
    ref_ocr_base = os.path.splitext(os.path.basename(args.ref_ocr_file))[0]
    eval_ocr_base = os.path.splitext(os.path.basename(args.eval_ocr_file))[0]
    title = (
        f"PDD驥阪∩莉倥￠ 逵溷､繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ\n"
        f"norm={args.norm_mode}, z_ref={args.z_ref} cm / ref_z={z_depth_ref:.3f} cm, eval_z={z_depth_eval:.3f} cm"
    )
    # 譌･譛ｬ隱槭ヵ繧ｩ繝ｳ繝医・險ｭ螳夲ｼ亥峙菫晏ｭ俶凾縺ｮ隴ｦ蜻頑椛豁｢・・
    try:
        import matplotlib as _mpl
        _mpl.rcParams['font.family'] = ['Yu Gothic', 'Meiryo', 'MS Gothic', 'Noto Sans CJK JP', 'Noto Sans JP', 'IPAexGothic', 'DejaVu Sans']
        _mpl.rcParams['axes.unicode_minus'] = False
    except Exception:
        pass
    plt.figure(figsize=(12, 8))
    ref_label = args.legend_ref if args.legend_ref else f'逵溷､(ref): {ref_ocr_base}'
    eval_label = args.legend_eval if args.legend_eval else f'逵溷､(eval): {eval_ocr_base}'
    plt.plot(x_for_gamma_ref, y_for_gamma_ref, label=ref_label, color='blue', lw=2.2)
    plt.plot(x_for_gamma_eval, y_for_gamma_eval, label=eval_label, color='red', lw=2.2, linestyle='--')
    plt.title(title, fontsize=14)
    plt.xlabel('讓ｪ譁ｹ蜷台ｽ咲ｽｮ (cm)')
    plt.ylabel('逵溷､邱夐㍼ (PDD驥阪∩莉倥￠, 莉ｻ諢丞腰菴・')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    # 讎りｦ√ユ繧ｭ繧ｹ繝茨ｼ・MSE/ﾎｳ・峨ｒ蝗ｳ蜀・↓陦ｨ遉ｺ
    summary = (
        f"RMSE: {rmse:.4f}\n"
        f"ﾎｳ1 ({args.dd1:.0f}%/{args.dta1:.0f}mm/{args.cutoff:.0f}%): {g1:.2f}%\n"
        f"ﾎｳ2 ({args.dd2:.0f}%/{args.dta2:.0f}mm/{args.cutoff:.0f}%): {g2:.2f}%\n"
        f"S_axis(ref)={s_axis_ref:.3f}, S_axis(eval)={s_axis_eval:.3f}\n"
        f"grid={grid_step:.3f} cm"
    )
    plt.gca().text(0.02, 0.98, summary, transform=plt.gca().transAxes,
                   va='top', ha='left', fontsize=11,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, lw=0.5))
    # 霆ｸ遽・峇
    if args.ymin is not None or args.ymax is not None:
        ymin = args.ymin if args.ymin is not None else plt.gca().get_ylim()[0]
        ymax = args.ymax if args.ymax is not None else plt.gca().get_ylim()[1]
        try:
            plt.ylim(ymin, ymax)
        except Exception:
            pass
    try:
        if args.xlim_symmetric:
            xmax = max(abs(np.min(x_for_gamma_ref)), abs(np.max(x_for_gamma_ref)),
                       abs(np.min(x_for_gamma_eval)), abs(np.max(x_for_gamma_eval)))
            plt.xlim(-xmax, xmax)
        else:
            x_min = min(np.min(x_for_gamma_ref), np.min(x_for_gamma_eval))
            x_max = max(np.max(x_for_gamma_ref), np.max(x_for_gamma_eval))
            plt.xlim(x_min - 0.5, x_max + 0.5)
    except Exception:
        pass
    plot_name = (
        f"TrueComp_{ref_ocr_base}_vs_{eval_ocr_base}"
        f"_norm-{args.norm_mode}_zref-{args.z_ref:g}_z-{z_depth_ref:g}-{z_depth_eval:g}.png"
    )
    plot_path = os.path.join(plot_dir, plot_name)
    plt.savefig(plot_path)
    print(f"Plot saved: {plot_path}")

    # 繝ｬ繝昴・繝井ｿ晏ｭ・
    report_name = (
        f"TrueReport_{ref_ocr_base}_vs_{eval_ocr_base}"
        f"_norm-{args.norm_mode}_zref-{args.z_ref:g}_z-{z_depth_ref:g}-{z_depth_eval:g}.txt"
    )
    report_path = os.path.join(report_dir, report_name)
    saved_files = [plot_path]
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# PDD驥阪∩莉倥￠ 逵溷､繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ 繝ｬ繝昴・繝・n")
            f.write("\n## 蜈･蜉媾n")
            f.write(f"ref PDD: {args.ref_pdd_type} 窶・{args.ref_pdd_file}\n")
            f.write(f"eval PDD: {args.eval_pdd_type} 窶・{args.eval_pdd_file}\n")
            f.write(f"ref OCR: {args.ref_ocr_type} 窶・{args.ref_ocr_file}\n")
            f.write(f"eval OCR: {args.eval_ocr_type} 窶・{args.eval_ocr_file}\n")
            f.write("\n## 隗｣譫舌ヱ繝ｩ繝｡繝ｼ繧ｿ\n")
            f.write(f"norm-mode: {args.norm_mode}, z_ref: {args.z_ref} cm\n")
            f.write(f"ref depth (cm): {z_depth_ref:.6f}, eval depth (cm): {z_depth_eval:.6f}\n")
            f.write(f"S_axis(ref): {s_axis_ref:.6f}, S_axis(eval): {s_axis_eval:.6f}\n")
            f.write(f"grid (cm): {grid_step:.6f}\n")
            try:
                if fwhm_ref is not None and fwhm_eval is not None:
                    f.write(f"FWHM(ref/eval) [cm]: {fwhm_ref:.4f} / {fwhm_eval:.4f} (ﾎ・{fwhm_delta:+.4f})\n")
            except Exception:
                pass
            f.write("\n## 邨先棡\n")
            f.write(f"RMSE: {rmse:.6f}\n")
            f.write(f"Gamma 1 (DD={args.dd1:.1f}%, DTA={args.dta1:.1f}mm, Cutoff={args.cutoff:.1f}%): {g1:.2f}%\n")
            f.write(f"Gamma 2 (DD={args.dd2:.1f}%, DTA={args.dta2:.1f}mm, Cutoff={args.cutoff:.1f}%): {g2:.2f}%\n")
        print(f"Report saved: {report_path}")
        saved_files.append(report_path)
    except Exception as e:
        print(f"繝ｬ繝昴・繝井ｿ晏ｭ倅ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ: {e}", file=sys.stderr)

    # CSV繧ｨ繧ｯ繧ｹ繝昴・繝・
    if args.export_csv:
        data_dir = os.path.join(out_root, 'data')
        os.makedirs(data_dir, exist_ok=True)
        try:
            ref_csv = os.path.join(data_dir, f"TrueRef_{ref_ocr_base}_z{z_depth_ref:g}.csv")
            eval_csv = os.path.join(data_dir, f"TrueEval_{eval_ocr_base}_z{z_depth_eval:g}.csv")
            pd.DataFrame({'x_cm': x_ref, 'true_dose': y_true_ref}).to_csv(ref_csv, index=False, encoding='utf-8')
            pd.DataFrame({'x_cm': x_eval, 'true_dose': y_true_eval}).to_csv(eval_csv, index=False, encoding='utf-8')
            print(f"CSV saved: {ref_csv}")
            print(f"CSV saved: {eval_csv}")
            saved_files.extend([ref_csv, eval_csv])
            if grid is not None:
                ref_g_csv = os.path.join(data_dir, f"TrueRefResampled_{ref_ocr_base}_z{z_depth_ref:g}_grid{grid_step:g}.csv")
                eval_g_csv = os.path.join(data_dir, f"TrueEvalResampled_{eval_ocr_base}_z{z_depth_eval:g}_grid{grid_step:g}.csv")
                pd.DataFrame({'x_cm': grid, 'true_dose': y_ref_g}).to_csv(ref_g_csv, index=False, encoding='utf-8')
                pd.DataFrame({'x_cm': grid, 'true_dose': y_eval_g}).to_csv(eval_g_csv, index=False, encoding='utf-8')
                print(f"CSV saved: {ref_g_csv}")
                print(f"CSV saved: {eval_g_csv}")
                saved_files.extend([ref_g_csv, eval_g_csv])
            if args.export_gamma:
                # 蝓ｺ貅也ｳｻ蛻礼せ縺斐→縺ｮﾎｳ繧定ｨ育ｮ励＠縺ｦ菫晏ｭ假ｼ・ymedphys.gamma縺ｮ謌ｻ繧企・蛻励ｒ蛻ｩ逕ｨ・・
                xref_mm = (x_for_gamma_ref * 10.0).astype(float)
                xeval_mm = (x_for_gamma_eval * 10.0).astype(float)
                # %繧ｹ繧ｱ繝ｼ繝ｫ螟画鋤・亥渕貅匁怙螟ｧ=100%・・
                ref_pct = (y_for_gamma_ref / np.max(y_for_gamma_ref)) * 100.0 if np.max(y_for_gamma_ref) > 0 else y_for_gamma_ref
                eval_pct = (y_for_gamma_eval / np.max(y_for_gamma_ref)) * 100.0 if np.max(y_for_gamma_ref) > 0 else y_for_gamma_eval
                gamma = pymedphys.gamma(
                    axes_reference=(xref_mm,), dose_reference=ref_pct,
                    axes_evaluation=(xeval_mm,), dose_evaluation=eval_pct,
                    dose_percent_threshold=args.dd1,
                    distance_mm_threshold=args.dta1,
                    lower_percent_dose_cutoff=args.cutoff,
                )
                gamma_csv = os.path.join(data_dir, f"Gamma_{ref_ocr_base}_vs_{eval_ocr_base}_z{z_depth_ref:g}-{z_depth_eval:g}.csv")
                pd.DataFrame({
                    'x_cm': x_for_gamma_ref,
                    'true_ref': y_for_gamma_ref,
                    'true_eval_interp': np.interp(x_for_gamma_ref, x_for_gamma_eval, y_for_gamma_eval),
                    'gamma': gamma,
                    'pass': np.where(np.isnan(gamma), '', np.where(gamma <= 1.0, 'PASS', 'FAIL')),
                }).to_csv(gamma_csv, index=False, encoding='utf-8')
                print(f"CSV saved: {gamma_csv}")
                saved_files.append(gamma_csv)
        except Exception as e:
            print(f"CSV蜃ｺ蜉帑ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ: {e}", file=sys.stderr)

    # 繝ｪ繝昴ず繝医Μ蜀・↓繧ゅΑ繝ｩ繝ｼ菫晏ｭ假ｼ・utput/<basename(output_dir)> 荳具ｼ・
    try:
        mirror_root = os.path.join(project_root, 'output', os.path.basename(out_root.rstrip('\\/')))
        for path in saved_files:
            if not path:
                continue
            rel = os.path.relpath(path, out_root)
            dst = os.path.join(mirror_root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(path, dst)
    except Exception as e:
        print(f"隴ｦ蜻・ 繝溘Λ繝ｼ菫晏ｭ倅ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()

