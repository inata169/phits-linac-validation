import os
import sys
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEAS_ROOT = os.path.join(REPO_ROOT, 'data', 'measured_csv')
PY = sys.executable
CLI = os.path.join(REPO_ROOT, 'src', 'ocr_true_scaling.py')

SCENARIOS = [
    { 'folder': r'C:\phits\work\Elekta\6MV\Rev60-5x5-c8-0.49n',  'size': '05x05m' },
    { 'folder': r'C:\phits\work\Elekta\6MV\Rev47-c8-0.49n',       'size': '10x10m' },
    { 'folder': r'C:\phits\work\Elekta\6MV\Rev50-30x30--c8-0.49n','size': '30x30m' },
]
DEPTHS = [5, 10, 20]
AXES   = ['x', 'z']

def run_case(rev_folder, size_prefix, depth, axis):
    # Output to repo-only path
    out_root = os.path.join(REPO_ROOT, 'output', os.path.basename(rev_folder))
    os.makedirs(os.path.join(out_root, 'plots'), exist_ok=True)
    os.makedirs(os.path.join(out_root, 'reports'), exist_ok=True)
    os.makedirs(os.path.join(out_root, 'data'), exist_ok=True)

    # Build inputs
    pdd_csv = os.path.join(MEAS_ROOT, f'{size_prefix}PDD-zZver.csv')
    meas_depth = f'{depth:02d}'
    phits_tag  = {5:'050', 10:'100', 20:'200'}.get(depth, f'{depth:03d}')
    meas_ocr = os.path.join(MEAS_ROOT, f'{size_prefix}{meas_depth}cm-{"xXlat" if axis=="x" else "zYlng"}.csv')
    phits_ocr = os.path.join(rev_folder, f'deposit-y-water-{phits_tag}{axis}.out')

    if not os.path.exists(pdd_csv) or not os.path.exists(meas_ocr) or not os.path.exists(phits_ocr):
        print(f'[SKIP] missing inputs: pdd={os.path.exists(pdd_csv)} meas={os.path.exists(meas_ocr)} phits={os.path.exists(phits_ocr)}')
        return

    # Ensure config.ini points output_dir to repo output
    cfg_path = os.path.join(REPO_ROOT, 'config.ini')
    with open(cfg_path, 'w', encoding='utf-8') as f:
        f.write('[Paths]\n')
        f.write(f'phits_data_dir = {rev_folder}\n')
        f.write(f'measured_data_dir = {MEAS_ROOT}\n')
        f.write(f'output_dir = {out_root}\n\n')
        f.write('[Processing]\nresample_grid_cm = 0.1\n')

    cmd = [PY, CLI,
           '--ref-pdd-type','csv','--ref-pdd-file', pdd_csv,
           '--eval-pdd-type','phits','--eval-pdd-file', os.path.join(rev_folder, 'deposit-z-water.out'),
           '--ref-ocr-type','csv','--ref-ocr-file', meas_ocr,
           '--eval-ocr-type','phits','--eval-ocr-file', phits_ocr,
           '--norm-mode','dmax','--cutoff','10','--xlim-symmetric',
           '--smooth-window','5','--smooth-order','2','--export-csv','--export-gamma']
    print(f'RUN {size_prefix} d={depth} ax={axis}')
    subprocess.run(cmd, check=False)

def main():
    for sc in SCENARIOS:
        for d in DEPTHS:
            for ax in AXES:
                run_case(sc['folder'], sc['size'], d, ax)
    print('\nCompleted. Check outputs under:')
    for sc in SCENARIOS:
        print('  ' + os.path.join('output', os.path.basename(sc['folder']), '{plots,reports,data}'))

if __name__ == '__main__':
    main()
