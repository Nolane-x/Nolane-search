#Requires -Version 5.1
[CmdletBinding()]
param([switch]$RemoveData)
$ErrorActionPreference = "Stop"
$taskName = "Nolane Media Node"
Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Get-NetFirewallRule -Name "NolaneMediaNode-*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
if ($RemoveData) {
    $dataPath = Join-Path $PSScriptRoot "data"
    if (Test-Path $dataPath) { Remove-Item -LiteralPath $dataPath -Recurse -Force }
}
Write-Host "Nolane Media Node scheduled task and network rules removed."
if ($RemoveData) { Write-Host "Local job database and temporary media files removed." }
else { Write-Host "Local media data was kept. Remove media-node\data manually only when no longer needed." }
Write-Host "The local .env secret is retained. Delete it manually after removing MEDIA_NODE_URL and MEDIA_NODE_TOKEN from GitHub Actions secrets."
