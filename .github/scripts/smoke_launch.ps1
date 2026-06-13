<#
.SYNOPSIS
    Generic GUI launch smoke test for packaged release executables.

.DESCRIPTION
    Launches the packaged executable with the Qt offscreen platform and isolated
    runtime directories, then waits a short grace window. The launch is considered
    healthy when the process is still running at the end of the window (it is then
    terminated) or has already exited cleanly with code 0. An early non-zero exit
    is treated as a startup failure.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,
    [int]$GraceSeconds = 12
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "Executable not found: $ExePath"
}

$tempRoot = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { [System.IO.Path]::GetTempPath() }
$profileRoot = Join-Path $tempRoot ("smoke-" + [System.IO.Path]::GetFileNameWithoutExtension($ExePath))
$configDir = Join-Path $profileRoot "config"
$dataDir = Join-Path $profileRoot "data"
$tempDir = Join-Path $profileRoot "temp"
New-Item -ItemType Directory -Force -Path $configDir, $dataDir, $tempDir | Out-Null

$env:QT_QPA_PLATFORM = "offscreen"
$env:CONFIG_DIR = $configDir
$env:DATA_DIR = $dataDir
$env:APPDATA = $dataDir
$env:LOCALAPPDATA = $dataDir
$env:TEMP = $tempDir
$env:TMP = $tempDir

Write-Host "Launching '$ExePath' (offscreen) with a ${GraceSeconds}s survival window..."
$process = Start-Process -FilePath $ExePath -PassThru

$deadline = (Get-Date).AddSeconds($GraceSeconds)
while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 250
}

if ($process.HasExited) {
    if ($process.ExitCode -ne 0) {
        throw "Executable exited early with non-zero code $($process.ExitCode)."
    }
    Write-Host "Executable exited cleanly with code 0."
    exit 0
}

Write-Host "Executable still running after grace window; launch is healthy. Terminating."
try {
    $process.Kill()
    $process.WaitForExit(10000) | Out-Null
}
catch {
    Write-Host "Note: failed to terminate process cleanly: $($_.Exception.Message)"
}
exit 0
