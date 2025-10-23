# Build Windows executable (CLI) for ocr_true_scaling using PyInstaller
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1 [-OneFile]

param(
  [switch]$OneFile
)

$ErrorActionPreference = 'Stop'

Write-Host '[build] Checking Python...'
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error 'python command not found. Activate venv (.venv\Scripts\Activate)'
  exit 1
}

Write-Host '[build] Checking PyInstaller...'
try {
  python -c "import PyInstaller" | Out-Null
} catch {
  Write-Warning 'PyInstaller not found. Install with:'
  Write-Host   '  pip install pyinstaller'
  exit 1
}

$opts = @()
if ($OneFile) { $opts += '--onefile' }

Write-Host '[build] Running PyInstaller...'
# Build directly from script (no .spec file required)
pyinstaller @opts --name ocr_true_scaling --clean --noconfirm .\src\ocr_true_scaling.py

Write-Host '[build] Done. Executable output under .\dist\ or .\dist\ocr_true_scaling\ depending on mode.'
Write-Host '[run] Example: .\dist\ocr_true_scaling.exe --help  (onefile)'

