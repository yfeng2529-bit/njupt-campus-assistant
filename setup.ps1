param([switch]$NoShortcut)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
try {
    if (Test-Path -LiteralPath '.venv\Scripts\python.exe') {
        $appPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
        Write-Host 'Using the existing environment (no deletion or recreation).'
    } else {
        $appPython = Join-Path $PSScriptRoot '.runtime\tools\python.exe'
        if (-not (Test-Path -LiteralPath $appPython)) {
            Write-Host 'Downloading private Python runtime. Your system Python will not change.'
            New-Item -ItemType Directory -Force '.local' | Out-Null
            $archive = Join-Path $PSScriptRoot '.local\python.zip'
            Invoke-WebRequest -UseBasicParsing -Uri 'https://api.nuget.org/v3-flatcontainer/python/3.12.10/python.3.12.10.nupkg' -OutFile $archive
            Expand-Archive -LiteralPath $archive -DestinationPath (Join-Path $PSScriptRoot '.runtime') -Force
        }
    }
    & $appPython -m pip --version
    if ($LASTEXITCODE -ne 0) {
        & $appPython -m ensurepip
        if ($LASTEXITCODE -ne 0) { throw 'Could not prepare pip.' }
    }
    Write-Host 'Installing app dependencies. First setup may take several minutes.'
    & $appPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependencies could not be installed. Check your network and retry.' }
    & $appPython -c 'import streamlit,openai,sentence_transformers,numpy,pypdf,dotenv'
    if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
    if (-not $NoShortcut) {
        $shell = New-Object -ComObject WScript.Shell
        $desktop = [Environment]::GetFolderPath('Desktop')
        $shortcut = $shell.CreateShortcut((Join-Path $desktop 'NJUPT Campus Assistant.lnk'))
        $shortcut.TargetPath = Join-Path $PSScriptRoot 'run_app.bat'
        $shortcut.WorkingDirectory = $PSScriptRoot
        $shortcut.Description = 'Local campus assistant - use your own API'
        $shortcut.WindowStyle = 7
        $shortcut.Save()
    }
    Write-Host 'Ready. Open NJUPT Campus Assistant from your desktop.'
} catch {
    Write-Host ('Setup failed: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}

