# codex_inet_gitpy_v4.ps1
# シンプル即動作版：
# - サンドボックス無し（インターネット可）
# - PowerShell 側のパラメータ宣言なし → すべての引数はそのまま Codex へ渡す
# - 文字化け対策は既定で CP932 に寄せる（chcp があれば 932 に設定）

# === 文字コード調整（CP932 を既定） ===
$cmdChcp = Get-Command chcp -ErrorAction SilentlyContinue
if ($cmdChcp) { & $cmdChcp 932 | Out-Null }

$enc = [System.Text.Encoding]::GetEncoding(932)
$global:OutputEncoding = $enc
[Console]::OutputEncoding = $enc
[Console]::InputEncoding  = $enc

# === Codex 実行ファイルの検出（PATH → APPDATA → USERPROFILE） ===
$codex = $null

$cmd = Get-Command codex -ErrorAction SilentlyContinue
if ($cmd) {
    if ($cmd.Path) { $codex = $cmd.Path }
    elseif ($cmd.Source) { $codex = $cmd.Source }
}

if (-not $codex -and $env:APPDATA) {
    $cand = Join-Path $env:APPDATA 'npm\codex.cmd'
    if (Test-Path -LiteralPath $cand) { $codex = $cand }
}

if (-not $codex) {
    $home = $HOME
    if (-not $home -and $env:USERPROFILE) { $home = $env:USERPROFILE }
    if ($home) {
        $cand2 = Join-Path $home 'AppData\Roaming\npm\codex.cmd'
        if (Test-Path -LiteralPath $cand2) { $codex = $cand2 }
    }
}

if (-not $codex) { $codex = 'codex' }

# === そのまま引数を Codex にパススルー（インターネット可：--sandbox を付けない） ===
& $codex @args
$code = $LASTEXITCODE
if ($null -eq $code) { $code = 0 }
exit $code
