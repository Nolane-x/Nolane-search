#Requires -Version 5.1
[CmdletBinding()]
param()
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$taskName = "Nolane Media Node"
$rulePrefix = "NolaneMediaNode-"
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this installer from an elevated PowerShell window. No service will be exposed until firewall rules are installed."
}
if (-not $env:OS -or $env:OS -ne "Windows_NT") { throw "Nolane Media Node setup requires Windows 10 or Windows 11." }
$profiles = Get-NetFirewallProfile
if (($profiles | Where-Object { $_.Enabled -ne $true }).Count -gt 0) {
    throw "Windows Defender Firewall must be enabled for Domain, Private and Public profiles."
}
$pythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $pythonLauncher) { throw "Python 3.12 and the py launcher are required." }
$pythonVersion = & $pythonLauncher.Source -3.12 -c "import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor))"
if ($LASTEXITCODE -ne 0 -or $pythonVersion.Trim() -ne "3.12") { throw "Python 3.12 is required. Detected: $pythonVersion" }
$node = Get-Command node.exe -ErrorAction SilentlyContinue
if (-not $node) { throw "Node.js 22 or newer is required for yt-dlp challenge support." }
$nodeMajor = (& $node.Source --version).Trim() -replace '^v','' -replace '\..*$',''
if ([int]$nodeMajor -lt 22) { throw "Node.js 22 or newer is required." }
$ffmpeg = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
if (-not $ffmpeg) { throw "FFmpeg is required and must be available on PATH." }
& $ffmpeg.Source -version *> $null
if ($LASTEXITCODE -ne 0) { throw "The detected FFmpeg executable did not run." }
$tailscale = Get-Command tailscale.exe -ErrorAction SilentlyContinue
if (-not $tailscale) { throw "Install Tailscale and sign in before configuring Funnel." }

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & $pythonLauncher.Source -3.12 -m venv (Join-Path $root ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Unable to create the Python virtual environment." }
}
& $venvPython -m pip install --disable-pip-version-check --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Unable to update pip." }
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $root "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Unable to install the pinned yt-dlp dependencies." }

$envPath = Join-Path $root ".env"
if (Test-Path $envPath) {
    $tokenLine = Get-Content $envPath | Where-Object { $_ -match '^NOLANE_INTERNAL_TOKEN=' } | Select-Object -First 1
    $token = if ($tokenLine) { $tokenLine.Substring($tokenLine.IndexOf('=') + 1).Trim() } else { "" }
} else { $token = "" }
if ($token -notmatch '^[a-fA-F0-9]{64}$') {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $token = ([BitConverter]::ToString($bytes)).Replace("-", "").ToLowerInvariant()
}
Set-Content -Path $envPath -Value ("NOLANE_INTERNAL_TOKEN=" + $token) -Encoding ASCII
& icacls.exe $envPath /inheritance:r /grant:r ("{0}:(R,W)" -f $identity.Name) | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Unable to restrict access to the local secret file." }

$blockedRanges = @(
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8",
    "169.254.0.0/16", "172.16.0.0/12", "192.0.0.0/24", "192.0.2.0/24",
    "192.88.99.0/24", "192.168.0.0/16", "198.18.0.0/15", "198.51.100.0/24",
    "203.0.113.0/24", "224.0.0.0/4", "240.0.0.0/4", "255.255.255.255/32",
    "::/128", "::1/128", "::ffff:0:0/96", "64:ff9b::/96", "64:ff9b:1::/48", "2001:20::/28", "fc00::/7",
    "fe80::/10", "ff00::/8", "2001:db8::/32", "2001::/23", "2002::/16"
)
$programs = @(
    @{ Name = "python"; Path = $venvPython },
    @{ Name = "ffmpeg"; Path = $ffmpeg.Source },
    @{ Name = "node"; Path = $node.Source }
)
foreach ($program in $programs) {
    if (-not (Test-Path $program.Path)) { throw "Missing executable for outbound isolation: $($program.Path)" }
    $ruleName = $rulePrefix + $program.Name
    Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule -Name $ruleName -DisplayName ("Nolane Media Node outbound private-network block (" + $program.Name + ")") -Direction Outbound -Action Block -Enabled True -Profile Any -Program $program.Path -RemoteAddress $blockedRanges | Out-Null
}
foreach ($program in $programs) {
    $rule = Get-NetFirewallRule -Name ($rulePrefix + $program.Name) -ErrorAction Stop
    if ($rule.Enabled -ne "True" -or $rule.Direction -ne "Outbound" -or $rule.Action -ne "Block") {
        throw "Firewall isolation could not be verified for $($program.Name). Do not enable Tailscale Funnel."
    }
}

$startScript = Join-Path $root "start.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $startScript + '"')
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principalTask = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 0) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principalTask -Settings $settings -Description "Owner-only local media download and temporary playback service." -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

Write-Host ""
Write-Host "Nolane Media Node installed. The service listens only on 127.0.0.1:8765."
Write-Host "The local token is stored in media-node\.env. Do not publish or send this file."
Write-Host "Read media-node\README.md, verify Funnel manually, then add MEDIA_NODE_URL and MEDIA_NODE_TOKEN to GitHub Actions secrets."
Write-Host "No Cloudflare Paid plan, R2 bucket or cloud media host is required."
