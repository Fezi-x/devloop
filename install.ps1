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

# Ensure DEVLOOP_HOME is set for future sessions and current session.
if (-not $DevloopHome) {
  $DevloopHome = $repoRoot
}
$env:DEVLOOP_HOME = $DevloopHome
try {
  setx DEVLOOP_HOME $DevloopHome | Out-Null
} catch {
  Write-Warning "Failed to persist DEVLOOP_HOME with setx. You can set it manually to: $DevloopHome"
}

# Ensure DEVLOOP_CONFIG is set for global config (.env, token).
if (-not $env:DEVLOOP_CONFIG) {
  $env:DEVLOOP_CONFIG = Join-Path $env:USERPROFILE ".devloop"
}
try {
  setx DEVLOOP_CONFIG $env:DEVLOOP_CONFIG | Out-Null
} catch {
  Write-Warning "Failed to persist DEVLOOP_CONFIG with setx. You can set it manually to: $env:DEVLOOP_CONFIG"
}

if (-not (Test-Path $env:DEVLOOP_CONFIG)) {
  New-Item -ItemType Directory -Path $env:DEVLOOP_CONFIG | Out-Null
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

$skillsRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $env:USERPROFILE ".codex\skills" }
$skillName = "devloop"
$skillDir = Join-Path $skillsRoot $skillName

if (-not (Test-Path $skillsRoot)) {
  New-Item -ItemType Directory -Path $skillsRoot | Out-Null
}

if (-not (Test-Path $skillDir)) {
  $initSkill = "C:\Users\Lenovo\.codex\skills\.system\skill-creator\scripts\init_skill.py"
  python $initSkill $skillName --path $skillsRoot
}

$skillBody = Get-Content -Raw -LiteralPath $skillSource
$skillFrontmatter = @"
---
name: devloop
description: Compact Devloop issue protocol and CLI launcher usage for creating, listing, getting, and editing GitHub issues via the devloop tool; use when interacting with devloop or its compact `/d` commands.
---

"@
$skillContent = $skillFrontmatter + $skillBody
$skillPath = Join-Path $skillDir "SKILL.md"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($skillPath, $skillContent, $utf8NoBom)

$genYaml = "C:\Users\Lenovo\.codex\skills\.system\skill-creator\scripts\generate_openai_yaml.py"
python $genYaml $skillDir `
  --interface display_name="Devloop" `
  --interface short_description="Run the Devloop compact issue workflow" `
  --interface default_prompt="Enter devloop mode: use the compact /d commands and map them to devloop CLI calls."

$validateSkill = "C:\Users\Lenovo\.codex\skills\.system\skill-creator\scripts\quick_validate.py"
python $validateSkill $skillDir

# Migrate existing local config to global config (one-time best effort).
$localEnv = Join-Path $repoRoot ".env"
$globalEnv = Join-Path $env:DEVLOOP_CONFIG ".env"
if ((Test-Path $localEnv) -and (-not (Test-Path $globalEnv))) {
  Copy-Item -LiteralPath $localEnv -Destination $globalEnv
}

$localToken = Join-Path $repoRoot "token.json"
$globalToken = Join-Path $env:DEVLOOP_CONFIG "token.json"
if ((Test-Path $localToken) -and (-not (Test-Path $globalToken))) {
  Copy-Item -LiteralPath $localToken -Destination $globalToken
}

if (-not (Test-Path $globalToken)) {
  Write-Output "Starting GitHub device authorization..."
  python (Join-Path $repoRoot "auth.py")
} else {
  Write-Output "token.json already exists; skipping GitHub authorization."
}

Write-Output "Installed devloop launcher to: $devloopCmd"
Write-Output "Installed devloop PowerShell launcher to: $devloopPs1"
Write-Output "Installed Codex skill to: $skillDir\SKILL.md"
