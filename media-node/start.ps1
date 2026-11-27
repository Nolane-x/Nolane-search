#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$envPath = Join-Path $root ".env"
if (-not (Test-Path $envPath)) { throw "Missing media-node\.env. Run install.ps1 first." }
$tokenLine = Get-Content $envPath | Where-Object { $_ -match '^NOLANE_INTERNAL_TOKEN=' } | Select-Object -First 1
if (-not $tokenLine) { throw "Missing NOLANE_INTERNAL_TOKEN in media-node\.env." }
$token = $tokenLine.Substring($tokenLine.IndexOf('=') + 1).Trim()
if ($token -notmatch '^[a-fA-F0-9]{64}$') { throw "Invalid local Media Node token." }
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Missing local Python environment. Run install.ps1." }
$env:NOLANE_INTERNAL_TOKEN = $token
$env:NOLANE_MEDIA_DATA_DIR = Join-Path $root "data"
$env:NOLANE_MEDIA_PORT = "8765"
New-Item -ItemType Directory -Force -Path $env:NOLANE_MEDIA_DATA_DIR | Out-Null
$log = Join-Path $env:NOLANE_MEDIA_DATA_DIR "media-node.log"
& $python (Join-Path $root "server.py") *>> $log
exit $LASTEXITCODE
