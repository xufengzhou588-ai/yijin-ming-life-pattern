$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$dist = Join-Path $root "dist"
$staging = Join-Path $dist "MING-mac-handoff-$timestamp"
$zipPath = "$staging.zip"

New-Item -ItemType Directory -Force $dist | Out-Null
if (Test-Path $staging) {
  Remove-Item $staging -Recurse -Force
}
New-Item -ItemType Directory -Force $staging | Out-Null

$include = @(
  "README.md",
  "requirements.txt",
  "server.py",
  "start-yijin-server.bat",
  "bazi_core",
  "schemas",
  "samples",
  "tests",
  "tools",
  "web",
  "docs",
  "ios"
)

foreach ($item in $include) {
  $source = Join-Path $root $item
  if (Test-Path $source) {
    Copy-Item $source -Destination $staging -Recurse -Force
  }
}

$removePatterns = @(
  "__pycache__",
  ".pytest_cache"
)

foreach ($pattern in $removePatterns) {
  Get-ChildItem $staging -Recurse -Force -Directory -Filter $pattern -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force
}

Get-ChildItem $staging -Recurse -Force -Include "*.pyc","*.pyo","*.log" -ErrorAction SilentlyContinue |
  Remove-Item -Force

if (Test-Path $zipPath) {
  Remove-Item $zipPath -Force
}

Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath -Force

Write-Output $zipPath
