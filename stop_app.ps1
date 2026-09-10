$ErrorActionPreference = 'Stop'
$stateFile = Join-Path $PSScriptRoot '.local\server.json'
if (Test-Path -LiteralPath $stateFile) {
    $state = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
    $appProcess = Get-CimInstance Win32_Process -Filter ("ProcessId = " + [int]$state.pid)
    $appPath = Join-Path $PSScriptRoot 'app.py'
    if ($state.root -eq $PSScriptRoot -and $appProcess -and $appProcess.CommandLine.Contains($appPath) -and $appProcess.CommandLine.Contains('streamlit')) {
        Stop-Process -Id $appProcess.ProcessId
        Write-Host 'Campus assistant stopped.'
    } else {
        Write-Host 'No matching app process. Nothing stopped.'
    }
}

