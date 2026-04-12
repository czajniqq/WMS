#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Installs the Monitoring Agent as a Windows service.
.DESCRIPTION
    Checks for Python, installs dependencies, then creates and starts
    the MonitoringAgent service using sc.exe or NSSM if available.
#>

$ServiceName = "MonitoringAgent"
$AgentDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source

if (-not $PythonExe) {
    Write-Error "Python not found in PATH. Please install Python 3.11+ and try again."
    exit 1
}

Write-Host "Python found at: $PythonExe"

Write-Host "Installing dependencies..."
& $PythonExe -m pip install -r "$AgentDir\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements."
    exit 1
}

$NssmPath = (Get-Command nssm -ErrorAction SilentlyContinue)?.Source

if ($NssmPath) {
    Write-Host "Using NSSM to install service..."
    & nssm install $ServiceName $PythonExe "$AgentDir\main.py"
    & nssm set $ServiceName AppDirectory $AgentDir
    & nssm set $ServiceName Start SERVICE_AUTO_START
    & nssm set $ServiceName AppStdout "$AgentDir\service_stdout.log"
    & nssm set $ServiceName AppStderr "$AgentDir\service_stderr.log"
} else {
    Write-Host "NSSM not found. Using sc.exe (basic service wrapper)..."
    $BinPath = "`"$PythonExe`" `"$AgentDir\main.py`""
    sc.exe create $ServiceName binPath= $BinPath start= auto DisplayName= "LAN Monitoring Agent"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create service with sc.exe."
        exit 1
    }
}

Write-Host "Starting service $ServiceName..."
Start-Service -Name $ServiceName -ErrorAction SilentlyContinue

$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($svc) {
    Write-Host "Service status: $($svc.Status)"
} else {
    Write-Warning "Service created but could not query status."
}

Write-Host "Done. Monitor agent installed as '$ServiceName'."
