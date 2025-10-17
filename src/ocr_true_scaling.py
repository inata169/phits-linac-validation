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
    print(f"依存ライブラリが見つかりません: {e}. pip install pymedphys matplotlib scipy を実行してください。", file=sys.stderr)
    sys.exit(1)


def load_csv_profile(path: str) -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(path, encoding='utf-8-sig', header=None)
    # ヘッダ行がある場合を考慮: 先頭行に(cm)があればスキップ
    if df.shape[1] >= 2 and isinstance(df.iloc[0, 0], str) and '(cm)' in df.iloc[0, 0]:
        df = pd.read_csv(path, encoding='utf-8-sig')
        # 先頭2列に限定
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
    # 位置で昇順ソート（補間の安定化のため）
    order = np.argsort(pos)
    pos = pos[order]
    dose = dose[order]
    # 正規化 [0,1]
    if dose.size == 0:
        raise ValueError(f"CSVに有効な数値データがありません: {path}")
    dmax = np.max(dose)
    if dmax <= 0:
        raise ValueError(f"CSVの線量最大値が0以下です: {path}")
    dose_norm = dose / dmax
    return pos.astype(float), dose_norm.astype(float)


def parse_phits_out_profile(path: str) -> Tuple[str, np.ndarray, np.ndarray, dict]:
    """
    PHITS [T-Deposit] 出力から1Dプロファイルを抽出。
    戻り値: (axis, pos_cm, dose_norm, meta)
    - axis: 'x'/'y'/'z' のうち、出力軸（"axis =" に依存）
    - pos_cm: ビン中心位置（cm）
    - dose_norm: ビンの線量（最大=1で正規化）
    - meta: 追加情報（例: y-slab範囲など）
    """
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    axis = None
    y_slab = None
    # 軸・スラブ情報
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

    # データ部を探す: ヘッダ 'h:' の後、"#  y-lower      y-upper      all         r.err" 行に続く数表
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
        raise ValueError(f"PHITSデータ表の開始位置が見つかりません: {path}")

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
        raise ValueError(f"PHITSデータが空です: {path}")
    dmax = np.max(dose)
    if dmax <= 0:
        raise ValueError(f"PHITS線量最大値が0以下です: {path}")
    dose_norm = dose / dmax
    meta = {}
    if y_slab is not None:
        meta['y_center_cm'] = y_slab
    return (axis or ''), pos, dose_norm, meta


def normalize_pdd(pos_cm: np.ndarray, dose_norm: np.ndarray, mode: str, z_ref_cm: float) -> Tuple[np.ndarray, np.ndarray]:
    if mode == 'z_ref':
        # 参照深で1.0になるよう正規化
        ref = np.interp(z_ref_cm, pos_cm, dose_norm)
        if ref <= 0:
            raise ValueError(f"z_ref={z_ref_cm} cm のPDDが0以下のため正規化できません")
        return pos_cm, (dose_norm / ref)
    # 既定 dmax
    dmax = np.max(dose_norm)
    return pos_cm, (dose_norm / dmax)


def ocr_center_normalize(pos_cm: np.ndarray, dose_norm: np.ndarray, tol_cm: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """中心(ビーム中心)の位置と振幅を正規化。
    - 位置: 中心候補の座標を0 cmに平行移動（座標再中心化）
    - 振幅: 中心点の線量を1.00にスケーリング（近傍±tolに点が無ければ最大値）
    """
    # 中心候補のインデックス（x=0に最も近い）
    idx_center = int(np.argmin(np.abs(pos_cm))) if pos_cm.size else 0
    x_center = pos_cm[idx_center] if pos_cm.size else 0.0
    # 座標を中心が0になるように平行移動
    pos_centered = pos_cm - x_center
    # 振幅スケーリング参照値
    if abs(x_center) <= tol_cm:
        c = dose_norm[idx_center]
    else:
        # 近傍に中心サンプルが無い場合は最大値を基準とする
        c = float(np.max(dose_norm)) if dose_norm.size else 1.0
    if c <= 0:
        raise ValueError("OCR中心正規化の基準が0以下です")
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
    # γのため、基準を%スケールへ（最大=100%）
    if np.max(y_ref_true) <= 0:
        return 0.0
    ref_pct = (y_ref_true / np.max(y_ref_true)) * 100.0
    eval_pct = (y_eval_true / np.max(y_ref_true)) * 100.0  # 基準正規化に合わせる
    # 軸をmmへ
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
    parser = argparse.ArgumentParser(description='PDD重み付け真値スケーリングでOCRを比較 (γ/RMSE)')
    # PDD 入力
    parser.add_argument('--ref-pdd-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--ref-pdd-file', required=True)
    parser.add_argument('--eval-pdd-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--eval-pdd-file', required=True)
    # OCR 入力
    parser.add_argument('--ref-ocr-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--ref-ocr-file', required=True)
    parser.add_argument('--eval-ocr-type', choices=['csv', 'phits'], required=True)
    parser.add_argument('--eval-ocr-file', required=True)
    # 正規化
    parser.add_argument('--norm-mode', choices=['dmax', 'z_ref'], default='dmax')
    parser.add_argument('--z-ref', type=float, default=10.0)
    # 評価条件
    parser.add_argument('--dd1', type=float, default=2.0)
    parser.add_argument('--dta1', type=float, default=2.0)
    parser.add_argument('--dd2', type=float, default=3.0)
    parser.add_argument('--dta2', type=float, default=3.0)
    parser.add_argument('--cutoff', type=float, default=10.0)
    # 平滑化・再サンプル・可視化
    parser.add_argument('--smooth-window', type=int, default=5, help='Savitzky-Golay平滑のウィンドウ（奇数, デフォルト5）')
    parser.add_argument('--smooth-order', type=int, default=2, help='Savitzky-Golay平滑の次数（デフォルト2）')
    parser.add_argument('--no-smooth', action='store_true', help='平滑化を無効化する')
    parser.add_argument('--grid', type=float, default=None, help='RMSE/可視化の共通グリッド刻み[cm] (未指定はconfig.iniのProcessing.resample_grid_cm)')
    parser.add_argument('--ymin', type=float, default=None, help='プロットのY最小値')
    parser.add_argument('--ymax', type=float, default=None, help='プロットのY最大値')
    parser.add_argument('--export-csv', action='store_true', help='真値系列（必要に応じて再サンプル系列も）をCSVに保存する')
    parser.add_argument('--export-gamma', action='store_true', help='基準系列点ごとのγをCSVに保存する（共通グリッド使用時はそのグリッドで）')
    parser.add_argument('--xlim-symmetric', action='store_true', help='横軸を原点対称範囲に設定する')
    parser.add_argument('--legend-ref', type=str, default=None, help='凡例のrefラベルを指定')
    parser.add_argument('--legend-eval', type=str, default=None, help='凡例のevalラベルを指定')
    args = parser.parse_args()

    # config から grid 既定値
    grid_step = args.grid
    if grid_step is None:
        cfg = configparser.ConfigParser()
        project_root = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(project_root)
        cfg_path = os.path.join(project_root, 'config.ini')
        if os.path.exists(cfg_path):
            try:
                cfg.read(cfg_path, encoding='utf-8')
                grid_step = float(cfg.get('Processing', 'resample_grid_cm', fallback='0.1'))
            except Exception:
                grid_step = 0.1
        else:
            grid_step = 0.1

    # PDD 読み込み・正規化（reference）
    if args.ref_pdd_type == 'csv':
        z_ref_pos, z_ref_dose = load_csv_profile(args.ref_pdd_file)
    else:
        axis, pos, dose, _ = parse_phits_out_profile(args.ref_pdd_file)
        if axis.lower() not in ('y',):
            print(f"警告: PDDは通常y軸です。axis={axis}", file=sys.stderr)
        z_ref_pos, z_ref_dose = pos, dose
    z_ref_pos, z_ref_norm = normalize_pdd(z_ref_pos, z_ref_dose, args.norm_mode, args.z_ref)

    # PDD 読み込み・正規化（eval）
    if args.eval_pdd_type == 'csv':
        z_eval_pos, z_eval_dose = load_csv_profile(args.eval_pdd_file)
    else:
        axis, pos, dose, _ = parse_phits_out_profile(args.eval_pdd_file)
        if axis.lower() not in ('y',):
            print(f"警告: PDDは通常y軸です。axis={axis}", file=sys.stderr)
        z_eval_pos, z_eval_dose = pos, dose
    z_eval_pos, z_eval_norm = normalize_pdd(z_eval_pos, z_eval_dose, args.norm_mode, args.z_ref)

    # OCR 読み込み・中心正規化（reference）
    if args.ref_ocr_type == 'csv':
        x_ref, ocr_ref = load_csv_profile(args.ref_ocr_file)
        # 深さはファイル名から推定 (..10cm.. → 10.0)
        m = re.search(r'([0-9]+)\s*cm', os.path.basename(args.ref_ocr_file), re.IGNORECASE)
        z_depth_ref = float(m.group(1)) if m else args.z_ref
    else:
        axis, pos, dose, meta = parse_phits_out_profile(args.ref_ocr_file)
        # PHITS OCR は lateral 軸 (xやz) のはず。深さは y_slab 中心を採用
        z_depth_ref = meta.get('y_center_cm', args.z_ref)
        x_ref, ocr_ref = pos, dose
    x_ref, ocr_ref_rel = ocr_center_normalize(x_ref, ocr_ref, tol_cm=0.05)

    # OCR 読み込み・中心正規化（eval）
    if args.eval_ocr_type == 'csv':
        x_eval, ocr_eval = load_csv_profile(args.eval_ocr_file)
        m = re.search(r'([0-9]+)\s*cm', os.path.basename(args.eval_ocr_file), re.IGNORECASE)
        z_depth_eval = float(m.group(1)) if m else args.z_ref
    else:
        axis, pos, dose, meta = parse_phits_out_profile(args.eval_ocr_file)
        z_depth_eval = meta.get('y_center_cm', args.z_ref)
        x_eval, ocr_eval = pos, dose
    x_eval, ocr_eval_rel = ocr_center_normalize(x_eval, ocr_eval, tol_cm=0.05)

    # 軽い平滑化（Savitzky–Golay）。データ点数が不足/条件不一致ならスキップ
    if not args.no_smooth:
        try:
            w = args.smooth_window if args.smooth_window % 2 == 1 else args.smooth_window + 1
            o = args.smooth_order
            if w > o and len(ocr_ref_rel) >= w:
                ocr_ref_rel = savgol_filter(ocr_ref_rel, w, o)
            if w > o and len(ocr_eval_rel) >= w:
                ocr_eval_rel = savgol_filter(ocr_eval_rel, w, o)
            # 平滑後も最大値が1.00となるよう再正規化
            ref_max = float(np.max(ocr_ref_rel)) if len(ocr_ref_rel) else 1.0
            eval_max = float(np.max(ocr_eval_rel)) if len(ocr_eval_rel) else 1.0
            if ref_max > 0:
                ocr_ref_rel = (ocr_ref_rel / ref_max)
            if eval_max > 0:
                ocr_eval_rel = (ocr_eval_rel / eval_max)
        except Exception:
            pass

    # True(x,z) 構築
    s_axis_ref = float(np.interp(z_depth_ref, z_ref_pos, z_ref_norm))
    s_axis_eval = float(np.interp(z_depth_eval, z_eval_pos, z_eval_norm))
    y_true_ref = s_axis_ref * ocr_ref_rel
    y_true_eval = s_axis_eval * ocr_eval_rel

    # RMSE（共通グリッド）
    grid, y_ref_g, y_eval_g = resample_common_grid(x_ref, y_true_ref, x_eval, y_true_eval, grid_step)
    if grid is not None:
        rmse = compute_rmse(y_ref_g, y_eval_g)
        print(f"RMSE (共通グリッド {grid_step:.3f} cm): {rmse:.6f}")
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

    # γ（主要/副次）
    g1 = compute_gamma_pass(x_for_gamma_ref, y_for_gamma_ref, x_for_gamma_eval, y_for_gamma_eval,
                            dd_percent=args.dd1, dta_mm=args.dta1, cutoff_percent=args.cutoff)
    g2 = compute_gamma_pass(x_for_gamma_ref, y_for_gamma_ref, x_for_gamma_eval, y_for_gamma_eval,
                            dd_percent=args.dd2, dta_mm=args.dta2, cutoff_percent=args.cutoff)
    print(f"Gamma pass (DD={args.dd1:.1f}%, DTA={args.dta1:.1f}mm, Cutoff={args.cutoff:.1f}%): {g1:.2f}%")
    print(f"Gamma pass (DD={args.dd2:.1f}%, DTA={args.dta2:.1f}mm, Cutoff={args.cutoff:.1f}%): {g2:.2f}%")

    # 出力先（output/plots, output/reports）
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

    # 図保存（True スケールの比較）
    ref_ocr_base = os.path.splitext(os.path.basename(args.ref_ocr_file))[0]
    eval_ocr_base = os.path.splitext(os.path.basename(args.eval_ocr_file))[0]
    title = (
        f"PDD重み付け 真値スケーリング\n"
        f"norm={args.norm_mode}, z_ref={args.z_ref} cm / ref_z={z_depth_ref:.3f} cm, eval_z={z_depth_eval:.3f} cm"
    )
    # 日本語フォントの設定（図保存時の警告抑止）
    try:
        import matplotlib as _mpl
        _mpl.rcParams['font.family'] = ['Yu Gothic', 'Meiryo', 'MS Gothic', 'Noto Sans CJK JP', 'Noto Sans JP', 'IPAexGothic', 'DejaVu Sans']
        _mpl.rcParams['axes.unicode_minus'] = False
    except Exception:
        pass
    plt.figure(figsize=(12, 8))
    ref_label = args.legend_ref if args.legend_ref else f'真値(ref): {ref_ocr_base}'
    eval_label = args.legend_eval if args.legend_eval else f'真値(eval): {eval_ocr_base}'
    plt.plot(x_for_gamma_ref, y_for_gamma_ref, label=ref_label, color='blue', lw=2.2)
    plt.plot(x_for_gamma_eval, y_for_gamma_eval, label=eval_label, color='red', lw=2.2, linestyle='--')
    plt.title(title, fontsize=14)
    plt.xlabel('横方向位置 (cm)')
    plt.ylabel('真値線量 (PDD重み付け, 任意単位)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    # 概要テキスト（RMSE/γ）を図内に表示
    summary = (
        f"RMSE: {rmse:.4f}\n"
        f"γ1 ({args.dd1:.0f}%/{args.dta1:.0f}mm/{args.cutoff:.0f}%): {g1:.2f}%\n"
        f"γ2 ({args.dd2:.0f}%/{args.dta2:.0f}mm/{args.cutoff:.0f}%): {g2:.2f}%\n"
        f"S_axis(ref)={s_axis_ref:.3f}, S_axis(eval)={s_axis_eval:.3f}\n"
        f"grid={grid_step:.3f} cm"
    )
    plt.gca().text(0.02, 0.98, summary, transform=plt.gca().transAxes,
                   va='top', ha='left', fontsize=11,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, lw=0.5))
    # 軸範囲
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

    # レポート保存
    report_name = (
        f"TrueReport_{ref_ocr_base}_vs_{eval_ocr_base}"
        f"_norm-{args.norm_mode}_zref-{args.z_ref:g}_z-{z_depth_ref:g}-{z_depth_eval:g}.txt"
    )
    report_path = os.path.join(report_dir, report_name)
    saved_files = [plot_path]
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# PDD重み付け 真値スケーリング レポート\n")
            f.write("\n## 入力\n")
            f.write(f"ref PDD: {args.ref_pdd_type} — {args.ref_pdd_file}\n")
            f.write(f"eval PDD: {args.eval_pdd_type} — {args.eval_pdd_file}\n")
            f.write(f"ref OCR: {args.ref_ocr_type} — {args.ref_ocr_file}\n")
            f.write(f"eval OCR: {args.eval_ocr_type} — {args.eval_ocr_file}\n")
            f.write("\n## 解析パラメータ\n")
            f.write(f"norm-mode: {args.norm_mode}, z_ref: {args.z_ref} cm\n")
            f.write(f"ref depth (cm): {z_depth_ref:.6f}, eval depth (cm): {z_depth_eval:.6f}\n")
            f.write(f"S_axis(ref): {s_axis_ref:.6f}, S_axis(eval): {s_axis_eval:.6f}\n")
            f.write(f"grid (cm): {grid_step:.6f}\n")
            f.write("\n## 結果\n")
            f.write(f"RMSE: {rmse:.6f}\n")
            f.write(f"Gamma 1 (DD={args.dd1:.1f}%, DTA={args.dta1:.1f}mm, Cutoff={args.cutoff:.1f}%): {g1:.2f}%\n")
            f.write(f"Gamma 2 (DD={args.dd2:.1f}%, DTA={args.dta2:.1f}mm, Cutoff={args.cutoff:.1f}%): {g2:.2f}%\n")
        print(f"Report saved: {report_path}")
        saved_files.append(report_path)
    except Exception as e:
        print(f"レポート保存中にエラー: {e}", file=sys.stderr)

    # CSVエクスポート
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
                # 基準系列点ごとのγを計算して保存（pymedphys.gammaの戻り配列を利用）
                xref_mm = (x_for_gamma_ref * 10.0).astype(float)
                xeval_mm = (x_for_gamma_eval * 10.0).astype(float)
                # %スケール変換（基準最大=100%）
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
            print(f"CSV出力中にエラー: {e}", file=sys.stderr)

    # リポジトリ内にもミラー保存（output/<basename(output_dir)> 下）
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
        print(f"警告: ミラー保存中にエラー: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
