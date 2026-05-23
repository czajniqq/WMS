#Requires -RunAsAdministrator

$ServiceName = "MonitoringAgent"
$AgentDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
$PythonExe = if ($PythonCmd) { $PythonCmd.Source } else { $null }

if (-not $PythonExe) {
    Write-Error "Python not found in PATH."
    exit 1
}

Write-Host "Python found at: $PythonExe"
Write-Host "Installing dependencies..."
& $PythonExe -m pip install -r "$AgentDir\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements."
    exit 1
}

$NssmCmd = Get-Command nssm -ErrorAction SilentlyContinue
$NssmPath = if ($NssmCmd) { $NssmCmd.Source } else { $null }

# NOWA SEKCJA: Zatrzymywanie i usuwanie usługi, jeśli już istnieje
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "[INFO] Usługa $ServiceName już istnieje. Następuje jej aktualizacja..."
    Stop-Service -Name $ServiceName -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    if ($NssmPath) {
        & nssm remove $ServiceName confirm
    } else {
        sc.exe delete $ServiceName > $null
    }
    Write-Host "[INFO] Stara usługa została usunięta."
    Start-Sleep -Seconds 2
}

if ($NssmPath) {
    Write-Host "Using NSSM to install service..."
    & nssm install $ServiceName $PythonExe "$AgentDir\main.py"
    & nssm set $ServiceName AppDirectory $AgentDir
    & nssm set $ServiceName Start SERVICE_AUTO_START
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

Write-Host "Done. Monitor agent installed and started successfully."