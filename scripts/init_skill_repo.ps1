#Requires -Version 5.1
<#
.SYNOPSIS
    Thin PowerShell wrapper around init_skill_repo.py.
.DESCRIPTION
    Locates a Python interpreter and invokes init_skill_repo.py from this
    script's directory, forwarding all arguments unchanged. No logic is
    duplicated here; see init_skill_repo.py for behavior and flags.
.EXAMPLE
    .\init_skill_repo.ps1 --repo-name keystone --owner my-org --dry-run
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = 'Stop'

# Resolve this script's directory.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PyScript = Join-Path $ScriptDir 'init_skill_repo.py'

# Find a Python interpreter: prefer the `py` launcher, then `python`, then `python3`.
$PythonExe = $null
foreach ($candidate in @('py', 'python', 'python3')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { $PythonExe = $cmd.Source; break }
}

if (-not $PythonExe) {
    Write-Error "Python was not found on PATH. Install Python 3.9+ (https://www.python.org/downloads/) and retry."
    exit 2
}

# The `py` launcher needs an explicit version selector to prefer Python 3.
if ((Split-Path -Leaf $PythonExe) -ieq 'py.exe') {
    & $PythonExe -3 $PyScript @Args
} else {
    & $PythonExe $PyScript @Args
}

exit $LASTEXITCODE
