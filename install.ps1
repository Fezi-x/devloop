Param(
  [string]$DevloopHome = $env:DEVLOOP_HOME
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSource = Join-Path $repoRoot "skill.md"
if (-not (Test-Path $skillSource)) {
  Write-Error "skill.md not found in repo root: $repoRoot"
  exit 1
}

$binDir = Join-Path $env:USERPROFILE ".local\bin"
if (-not (Test-Path $binDir)) {
  New-Item -ItemType Directory -Path $binDir | Out-Null
}

$devloopCmd = Join-Path $binDir "devloop.cmd"
$devloopPs1 = Join-Path $binDir "devloop.ps1"

$cmdContent = @"
@echo off
setlocal

rem 1) Use DEVLOOP_HOME if set
if not "%DEVLOOP_HOME%"=="" (
  python "%DEVLOOP_HOME%\cli.py" %*
  exit /b %ERRORLEVEL%
)

rem 2) Walk up from current dir looking for cli.py
set "CUR=%CD%"
:findloop
if exist "%CUR%\cli.py" (
  python "%CUR%\cli.py" %*
  exit /b %ERRORLEVEL%
)
if "%CUR%"=="%CUR:~0,3%" goto notfound
cd ..
set "CUR=%CD%"
goto findloop

:notfound
@echo devloop not found. Set DEVLOOP_HOME or run inside the devloop repo.
exit /b 1
"@

$ps1Content = @"
param([Parameter(ValueFromRemainingArguments=`$true)] [string[]] `$Args)

if (`$env:DEVLOOP_HOME -and (Test-Path (Join-Path `$env:DEVLOOP_HOME "cli.py"))) {
  python (Join-Path `$env:DEVLOOP_HOME "cli.py") `$Args
  exit `$LASTEXITCODE
}

`$cur = Get-Location
while (`$true) {
  `$cli = Join-Path `$cur "cli.py"
  if (Test-Path `$cli) {
    python `$cli `$Args
    exit `$LASTEXITCODE
  }
  `$parent = Split-Path -Parent `$cur
  if (`$parent -eq `$cur) { break }
  `$cur = `$parent
}

Write-Error "devloop not found. Set DEVLOOP_HOME or run inside the devloop repo."
exit 1
"@

Set-Content -Encoding ASCII -Path $devloopCmd -Value $cmdContent
Set-Content -Encoding UTF8 -Path $devloopPs1 -Value $ps1Content

$skillDir = Join-Path $env:USERPROFILE ".codex\skills\devloop"
if (-not (Test-Path $skillDir)) {
  New-Item -ItemType Directory -Path $skillDir | Out-Null
}
Copy-Item -Force $skillSource (Join-Path $skillDir "skill.md")

Write-Output "Installed devloop launcher to: $devloopCmd"
Write-Output "Installed devloop PowerShell launcher to: $devloopPs1"
Write-Output "Installed Codex skill to: $skillDir\skill.md"
