Param()

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Move to repo root and set PYTHONPATH
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $ROOT
$env:PYTHONPATH = $ROOT

# Load config defaults (JSON)
$cfgPath = Join-Path $ROOT 'config/true_gui_defaults.json'
$cfg = @{}
if (Test-Path $cfgPath) {
  try { $cfg = Get-Content -Raw -Path $cfgPath | ConvertFrom-Json } catch { $cfg = @{} }
}

function New-Label($text, $x, $y){ $o = New-Object System.Windows.Forms.Label; $o.Text=$text; $o.Location=New-Object System.Drawing.Point($x,$y); $o.AutoSize=$true; return $o }
function New-Button($text, $x, $y, $w=80, $h=26){ $o=New-Object System.Windows.Forms.Button; $o.Text=$text; $o.Location=New-Object System.Drawing.Point($x,$y); $o.Size=New-Object System.Drawing.Size($w,$h); return $o }
function New-TextBox($x, $y, $w=430){ $o=New-Object System.Windows.Forms.TextBox; $o.Location=New-Object System.Drawing.Point($x,$y); $o.Size=New-Object System.Drawing.Size($w,22); $o.ReadOnly=$true; return $o }
function New-Combo($x, $y, $items){ $o=New-Object System.Windows.Forms.ComboBox; $o.Location=New-Object System.Drawing.Point($x,$y); $o.Size=New-Object System.Drawing.Size(80,22); $o.DropDownStyle='DropDownList'; $o.Items.AddRange($items); $o.SelectedIndex=0; return $o }
function New-Num($x,$y,$min,$max,$val){ $o=New-Object System.Windows.Forms.NumericUpDown; $o.Location=New-Object System.Drawing.Point($x,$y); $o.Size=New-Object System.Drawing.Size(80,22); $o.Minimum=[decimal]$min; $o.Maximum=[decimal]$max; $o.DecimalPlaces=2; $o.Increment=0.10; $o.Value=[decimal]$val; return $o }

# Form
$form = New-Object System.Windows.Forms.Form
$form.Text = 'True Scaling OCR GUI'
$form.Size = New-Object System.Drawing.Size(860,680)
$form.StartPosition = 'CenterScreen'
$form.Font = New-Object System.Drawing.Font('Segoe UI',9)

# Ref PDD
$form.Controls.Add((New-Label 'Ref PDD' 20 20))
$cbRefPdd = New-Combo 90 18 @('csv','phits')
$tbRefPdd = New-TextBox 180 18 560
$btnRefPdd = New-Button 'Browse...' 750 16
$form.Controls.Add($cbRefPdd); $form.Controls.Add($tbRefPdd); $form.Controls.Add($btnRefPdd)

# Eval PDD
$form.Controls.Add((New-Label 'Eval PDD' 20 52))
$cbEvalPdd = New-Combo 90 50 @('csv','phits')
$tbEvalPdd = New-TextBox 180 50 560
$btnEvalPdd = New-Button 'Browse...' 750 48
$form.Controls.Add($cbEvalPdd); $form.Controls.Add($tbEvalPdd); $form.Controls.Add($btnEvalPdd)

# Ref OCR
$form.Controls.Add((New-Label 'Ref OCR' 20 84))
$cbRefOcr = New-Combo 90 82 @('csv','phits')
$tbRefOcr = New-TextBox 180 82 560
$btnRefOcr = New-Button 'Browse...' 750 80
$form.Controls.Add($cbRefOcr); $form.Controls.Add($tbRefOcr); $form.Controls.Add($btnRefOcr)

# Eval OCR
$form.Controls.Add((New-Label 'Eval OCR' 20 116))
$cbEvalOcr = New-Combo 90 114 @('csv','phits')
$tbEvalOcr = New-TextBox 180 114 560
$btnEvalOcr = New-Button 'Browse...' 750 112
$form.Controls.Add($cbEvalOcr); $form.Controls.Add($tbEvalOcr); $form.Controls.Add($btnEvalOcr)

# Output folder
$form.Controls.Add((New-Label 'Output' 20 148))
$tbOut = New-TextBox 90 146 650
$btnOut = New-Button 'Select...' 750 144
$form.Controls.Add($tbOut); $form.Controls.Add($btnOut)

# Norm / z_ref
$form.Controls.Add((New-Label 'Norm' 20 180))
$cbNorm = New-Combo 60 178 @('dmax','z_ref')
$form.Controls.Add($cbNorm)
$form.Controls.Add((New-Label 'z_ref(cm)' 150 180))
$numZref = New-Num 220 178 0 100 10
$form.Controls.Add($numZref)

# Criteria
$form.Controls.Add((New-Label 'DD1(%)' 320 180)); $numDD1 = New-Num 370 178 0 10 2; $numDD1.DecimalPlaces=1; $numDD1.Increment=0.1
$form.Controls.Add($numDD1)
$form.Controls.Add((New-Label 'DTA1(mm)' 460 180)); $numDTA1 = New-Num 530 178 0 10 2; $numDTA1.DecimalPlaces=1; $numDTA1.Increment=0.5
$form.Controls.Add($numDTA1)
$form.Controls.Add((New-Label 'DD2(%)' 620 180)); $numDD2 = New-Num 670 178 0 10 3; $numDD2.DecimalPlaces=1; $numDD2.Increment=0.1
$form.Controls.Add($numDD2)
$form.Controls.Add((New-Label 'DTA2(mm)' 20 212)); $numDTA2 = New-Num 90 210 0 10 3; $numDTA2.DecimalPlaces=1; $numDTA2.Increment=0.5
$form.Controls.Add($numDTA2)
$form.Controls.Add((New-Label 'Cutoff(%)' 180 212)); $numCut = New-Num 250 210 0 50 10; $numCut.DecimalPlaces=1; $numCut.Increment=1
$form.Controls.Add($numCut)
$form.Controls.Add((New-Label 'Grid(cm)' 340 212)); $numGrid = New-Num 400 210 0 5 0.1; $numGrid.DecimalPlaces=2; $numGrid.Increment=0.1
$form.Controls.Add($numGrid)

# Smoothing / center / FWHM
$form.Controls.Add((New-Label 'Smooth win' 470 212)); $numWin = New-Num 540 210 1 99 5; $numWin.DecimalPlaces=0; $numWin.Increment=2
$form.Controls.Add($numWin)
$form.Controls.Add((New-Label 'order' 600 212)); $numOrd = New-Num 650 210 1 9 2; $numOrd.DecimalPlaces=0; $numOrd.Increment=1
$form.Controls.Add($numOrd)
$cbNoSmooth = New-Object System.Windows.Forms.CheckBox; $cbNoSmooth.Text='No smooth'; $cbNoSmooth.Location=New-Object System.Drawing.Point(720,212); $cbNoSmooth.AutoSize=$true; $form.Controls.Add($cbNoSmooth)

$form.Controls.Add((New-Label 'Center tol(cm)' 20 244)); $numCTol = New-Num 110 242 0 1 0.05; $numCTol.DecimalPlaces=3; $numCTol.Increment=0.01; $form.Controls.Add($numCTol)
$cbCInterp = New-Object System.Windows.Forms.CheckBox; $cbCInterp.Text='Center interp'; $cbCInterp.Location=New-Object System.Drawing.Point(200,244); $cbCInterp.AutoSize=$true; $form.Controls.Add($cbCInterp)

$form.Controls.Add((New-Label 'FWHM warn(cm)' 320 244)); $numFwhm = New-Num 410 242 0 5 1.0; $numFwhm.DecimalPlaces=2; $numFwhm.Increment=0.1; $form.Controls.Add($numFwhm)

# Flags / labels
$cbXSym = New-Object System.Windows.Forms.CheckBox; $cbXSym.Text='Xlim symmetric'; $cbXSym.Location=New-Object System.Drawing.Point(520,244); $cbXSym.AutoSize=$true; $form.Controls.Add($cbXSym)
$cbCSV = New-Object System.Windows.Forms.CheckBox; $cbCSV.Text='Export CSV'; $cbCSV.Location=New-Object System.Drawing.Point(640,244); $cbCSV.AutoSize=$true; $form.Controls.Add($cbCSV)
$cbGAM = New-Object System.Windows.Forms.CheckBox; $cbGAM.Text='Export Gamma CSV'; $cbGAM.Location=New-Object System.Drawing.Point(740,244); $cbGAM.AutoSize=$true; $form.Controls.Add($cbGAM)

$form.Controls.Add((New-Label 'Legend ref' 20 276)); $tbLRef = New-Object System.Windows.Forms.TextBox; $tbLRef.Location=New-Object System.Drawing.Point(100,274); $tbLRef.Size=New-Object System.Drawing.Size(300,22); $form.Controls.Add($tbLRef)
$form.Controls.Add((New-Label 'Legend eval' 420 276)); $tbLEval = New-Object System.Windows.Forms.TextBox; $tbLEval.Location=New-Object System.Drawing.Point(500,274); $tbLEval.Size=New-Object System.Drawing.Size(300,22); $form.Controls.Add($tbLEval)

# Run / Open / Log
$btnRun = New-Button 'Run' 20 310 120 32
$btnPrev = New-Button 'Preview Depths' 150 310 150 32
$btnOpen = New-Button 'Open Output' 310 310 160 32
$lblStatus = New-Label 'Status: Idle' 480 316
$pb = New-Object System.Windows.Forms.ProgressBar; $pb.Location=New-Object System.Drawing.Point(20, 348); $pb.Size=New-Object System.Drawing.Size(800, 10); $pb.Style='Marquee'; $pb.MarqueeAnimationSpeed=25; $pb.Visible=$false
$form.Controls.Add($btnRun); $form.Controls.Add($btnPrev); $form.Controls.Add($btnOpen); $form.Controls.Add($lblStatus); $form.Controls.Add($pb)

$tbLog = New-Object System.Windows.Forms.TextBox; $tbLog.Location=New-Object System.Drawing.Point(20,368); $tbLog.Size=New-Object System.Drawing.Size(800,260); $tbLog.Multiline=$true; $tbLog.ScrollBars='Vertical'; $tbLog.ReadOnly=$true; $form.Controls.Add($tbLog)

function Append-Log($text){ $tbLog.AppendText("$text`r`n") }
function Browse-AnyFile([ref]$tb, [string]$initialDir){
  $dlg = New-Object System.Windows.Forms.OpenFileDialog
  $dlg.Filter='All files (*.*)|*.*'
  if($initialDir -and (Test-Path $initialDir)) { $dlg.InitialDirectory = $initialDir }
  if($dlg.ShowDialog() -eq 'OK'){ $tb.Value.Text=$dlg.FileName; return (Split-Path -Parent $dlg.FileName) }
  return $null
}
function Browse-Folder([ref]$tb){ $dlg = New-Object System.Windows.Forms.FolderBrowserDialog; if($dlg.ShowDialog() -eq 'OK'){ $tb.Value.Text=$dlg.SelectedPath } }

$script:lastRefPddDir  = if($cfg.last_ref_pdd_dir){ [string]$cfg.last_ref_pdd_dir } else { '' }
$script:lastEvalPddDir = if($cfg.last_eval_pdd_dir){ [string]$cfg.last_eval_pdd_dir } else { '' }
$script:lastRefOcrDir  = if($cfg.last_ref_ocr_dir){ [string]$cfg.last_ref_ocr_dir } else { '' }
$script:lastEvalOcrDir = if($cfg.last_eval_ocr_dir){ [string]$cfg.last_eval_ocr_dir } else { '' }

$btnRefPdd.Add_Click({ $d = Browse-AnyFile ([ref]$tbRefPdd) $script:lastRefPddDir; if($d){ $script:lastRefPddDir = $d } })
$btnEvalPdd.Add_Click({ $d = Browse-AnyFile ([ref]$tbEvalPdd) $script:lastEvalPddDir; if($d){ $script:lastEvalPddDir = $d } })
$btnRefOcr.Add_Click({ $d = Browse-AnyFile ([ref]$tbRefOcr) $script:lastRefOcrDir; if($d){ $script:lastRefOcrDir = $d } })
$btnEvalOcr.Add_Click({ $d = Browse-AnyFile ([ref]$tbEvalOcr) $script:lastEvalOcrDir; if($d){ $script:lastEvalOcrDir = $d } })
$btnOut.Add_Click({ Browse-Folder ([ref]$tbOut) })
$btnOpen.Add_Click({ if([string]::IsNullOrWhiteSpace($tbOut.Text)){return}else{ Start-Process explorer.exe $tbOut.Text } })
$btnPrev.Add_Click({ Preview-Depths })

# Depth preview helpers
function Get-DepthFromCsvPath([string]$p){
  try {
    $name = [System.IO.Path]::GetFileName($p)
    $m = [regex]::Match($name, '([0-9]+(?:\.[0-9]+)?)\s*cm', 'IgnoreCase')
    if ($m.Success) { return [double]$m.Groups[1].Value }
  } catch {}
  return $null
}
function Get-DepthFromPhitsPath([string]$p){
  try {
    $name = [System.IO.Path]::GetFileName($p)
    $m = [regex]::Match($name, '-(\d+)([a-z])?\.out$', 'IgnoreCase')
    if ($m.Success) { return ([double]$m.Groups[1].Value) / 10.0 }
  } catch {}
  return $null
}
function Preview-Depths(){
  $refType = [string]$cbRefOcr.SelectedItem
  $evalType = [string]$cbEvalOcr.SelectedItem
  $refPath = [string]$tbRefOcr.Text
  $evalPath = [string]$tbEvalOcr.Text
  if ([string]::IsNullOrWhiteSpace($refPath) -or [string]::IsNullOrWhiteSpace($evalPath)){
    [System.Windows.Forms.MessageBox]::Show('Please select both Ref/Eval OCR files first.')
    return
  }
  $zr = $null; $ze = $null
  if ($refType -eq 'csv') { $zr = Get-DepthFromCsvPath $refPath } else { $zr = Get-DepthFromPhitsPath $refPath }
  if ($evalType -eq 'csv') { $ze = Get-DepthFromCsvPath $evalPath } else { $ze = Get-DepthFromPhitsPath $evalPath }
  $msg = "Ref depth: " + ([string]::Format('{0}', $(if($zr -ne $null){ '{0:0.###} cm' -f $zr } else { 'N/A' }))) +
         "  |  Eval depth: " + ([string]::Format('{0}', $(if($ze -ne $null){ '{0:0.###} cm' -f $ze } else { 'N/A' }))) +
         "`r`n(Depth is estimated from filenames. Final value may use PHITS header y-slab if available.)"
  [System.Windows.Forms.MessageBox]::Show($msg, 'Depth Preview') | Out-Null
}

function Build-Command(){
  if([string]::IsNullOrWhiteSpace($tbRefPdd.Text) -or [string]::IsNullOrWhiteSpace($tbEvalPdd.Text) -or [string]::IsNullOrWhiteSpace($tbRefOcr.Text) -or [string]::IsNullOrWhiteSpace($tbEvalOcr.Text) -or [string]::IsNullOrWhiteSpace($tbOut.Text)){
    [System.Windows.Forms.MessageBox]::Show('Please select all required files and output folder.'); return $null }
  New-Item -ItemType Directory -Force -Path $tbOut.Text | Out-Null
  $cmd = @('python','-u','src/ocr_true_scaling_ascii.py',
    '--ref-pdd-type',$cbRefPdd.SelectedItem,'--ref-pdd-file',$tbRefPdd.Text,
    '--eval-pdd-type',$cbEvalPdd.SelectedItem,'--eval-pdd-file',$tbEvalPdd.Text,
    '--ref-ocr-type',$cbRefOcr.SelectedItem,'--ref-ocr-file',$tbRefOcr.Text,
    '--eval-ocr-type',$cbEvalOcr.SelectedItem,'--eval-ocr-file',$tbEvalOcr.Text,
    '--norm-mode',$cbNorm.SelectedItem,
    '--dd1',[string]$numDD1.Value,'--dta1',[string]$numDTA1.Value,
    '--dd2',[string]$numDD2.Value,'--dta2',[string]$numDTA2.Value,
    '--cutoff',[string]$numCut.Value,'--grid',[string]$numGrid.Value,
    '--smooth-window',[string]$numWin.Value,'--smooth-order',[string]$numOrd.Value,
    '--center-tol-cm',[string]$numCTol.Value,'--fwhm-warn-cm',[string]$numFwhm.Value,'--output-dir',$tbOut.Text)
  if ($cbNorm.SelectedItem -eq 'z_ref') { $cmd += @('--z-ref',[string]$numZref.Value) }
  if ($cbNoSmooth.Checked) { $cmd += '--no-smooth' }
  if ($cbCInterp.Checked) { $cmd += '--center-interp' }
  if ($cbXSym.Checked) { $cmd += '--xlim-symmetric' }
  if ($cbCSV.Checked) { $cmd += '--export-csv' }
  if ($cbGAM.Checked) { $cmd += '--export-gamma' }
  return $cmd
}

function Run-Cmd([string[]]$cmd){
  Append-Log ("> " + ($cmd -join ' '))
  $btnRun.Enabled=$false; $btnRun.Text='Running...'; $lblStatus.Text='Status: Running'; $pb.Visible=$true
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $cmd[0]
  $psi.Arguments = ($cmd[1..($cmd.Length-1)] -join ' ')
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $psi.WorkingDirectory = $ROOT
  $psi.EnvironmentVariables['PYTHONUNBUFFERED'] = '1'
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  $p.EnableRaisingEvents = $true
  $p.SynchronizingObject = $form
  $null = $p.add_OutputDataReceived({ param($s,$e) if ($e.Data){ $tbLog.AppendText($e.Data+"`r`n") } })
  $null = $p.add_ErrorDataReceived({ param($s,$e) if ($e.Data){ $tbLog.AppendText($e.Data+"`r`n") } })
  $null = $p.add_Exited({ param($s,$e)
      $btnRun.Enabled=$true; $btnRun.Text='Run'; $lblStatus.Text = ("Status: Done (Exit {0})" -f $s.ExitCode); $pb.Visible=$false
      try {
        if (-not [string]::IsNullOrWhiteSpace($tbOut.Text)) {
          $logPath = Join-Path $tbOut.Text 'log.txt'
          $tbLog.Text | Out-File -FilePath $logPath -Encoding utf8
        }
      } catch {}
    })
  [void]$p.Start(); $p.BeginOutputReadLine(); $p.BeginErrorReadLine()
}

# Apply defaults
try {
  if ($cfg.output_dir) { $tbOut.Text = [string]$cfg.output_dir }
  if ($cfg.norm_mode) { $i = $cbNorm.Items.IndexOf([string]$cfg.norm_mode); if($i -ge 0){ $cbNorm.SelectedIndex=$i } }
  if ($cfg.z_ref) { $numZref.Value = [decimal]$cfg.z_ref }
  if ($cfg.dd1) { $numDD1.Value = [decimal]$cfg.dd1 }
  if ($cfg.dta1) { $numDTA1.Value = [decimal]$cfg.dta1 }
  if ($cfg.dd2) { $numDD2.Value = [decimal]$cfg.dd2 }
  if ($cfg.dta2) { $numDTA2.Value = [decimal]$cfg.dta2 }
  if ($cfg.cutoff) { $numCut.Value = [decimal]$cfg.cutoff }
  if ($cfg.grid) { $numGrid.Value = [decimal]$cfg.grid }
  if ($cfg.smooth_window) { $numWin.Value = [decimal]$cfg.smooth_window }
  if ($cfg.smooth_order) { $numOrd.Value = [decimal]$cfg.smooth_order }
  if ($cfg.no_smooth) { $cbNoSmooth.Checked = [bool]$cfg.no_smooth }
  if ($cfg.center_tol_cm) { $numCTol.Value = [decimal]$cfg.center_tol_cm }
  if ($cfg.center_interp) { $cbCInterp.Checked = [bool]$cfg.center_interp }
  if ($cfg.fwhm_warn_cm) { $numFwhm.Value = [decimal]$cfg.fwhm_warn_cm }
  if ($cfg.xlim_symmetric) { $cbXSym.Checked = [bool]$cfg.xlim_symmetric }
  if ($cfg.export_csv) { $cbCSV.Checked = [bool]$cfg.export_csv }
  if ($cfg.export_gamma) { $cbGAM.Checked = [bool]$cfg.export_gamma }
  if ($cfg.legend_ref) { $tbLRef.Text = [string]$cfg.legend_ref }
  if ($cfg.legend_eval) { $tbLEval.Text = [string]$cfg.legend_eval }
} catch {}

# Save Settings
$btnSave = New-Button 'Save Settings' 660 310 160 32
$form.Controls.Add($btnSave)
$btnSave.Add_Click({
  $new = [ordered]@{
    output_dir = $tbOut.Text
    norm_mode = [string]$cbNorm.SelectedItem
    z_ref = [double]$numZref.Value
    dd1 = [double]$numDD1.Value
    dta1 = [double]$numDTA1.Value
    dd2 = [double]$numDD2.Value
    dta2 = [double]$numDTA2.Value
    cutoff = [double]$numCut.Value
    grid = [double]$numGrid.Value
    smooth_window = [int]$numWin.Value
    smooth_order = [int]$numOrd.Value
    no_smooth = [bool]$cbNoSmooth.Checked
    center_tol_cm = [double]$numCTol.Value
    center_interp = [bool]$cbCInterp.Checked
    fwhm_warn_cm = [double]$numFwhm.Value
    xlim_symmetric = [bool]$cbXSym.Checked
    export_csv = [bool]$cbCSV.Checked
    export_gamma = [bool]$cbGAM.Checked
    legend_ref = [string]$tbLRef.Text
    legend_eval = [string]$tbLEval.Text
    last_ref_pdd_dir  = [string]$script:lastRefPddDir
    last_eval_pdd_dir = [string]$script:lastEvalPddDir
    last_ref_ocr_dir  = [string]$script:lastRefOcrDir
    last_eval_ocr_dir = [string]$script:lastEvalOcrDir
  }
  try { ($new | ConvertTo-Json -Depth 3) | Out-File -FilePath $cfgPath -Encoding utf8; [System.Windows.Forms.MessageBox]::Show('Saved.') } catch {}
})

$btnRun.Add_Click({ $cmd = Build-Command; if($null -ne $cmd){ Run-Cmd $cmd } })

# Enable z_ref input only when norm=z_ref
$cbNorm.add_SelectedIndexChanged({
  if ([string]$cbNorm.SelectedItem -eq 'z_ref') { $numZref.Enabled = $true } else { $numZref.Enabled = $false }
})
# Set initial enabled state
if ([string]$cbNorm.SelectedItem -eq 'z_ref') { $numZref.Enabled = $true } else { $numZref.Enabled = $false }

[void]$form.ShowDialog()




