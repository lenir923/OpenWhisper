# ============================================================
#  Desinstalleur OpenWhisper - lance par Desinstalle-OpenWhisper.bat
#  Retire tout ce que installe-openwhisper.ps1 a pose, y compris les
#  reglages et l'historique des dictees (%APPDATA%\OpenWhisper).
#  Ne touche a aucun autre programme Python du poste.
# ============================================================
$ErrorActionPreference = "Continue"
$dest    = Join-Path $env:LOCALAPPDATA "OpenWhisper"
$donnees = Join-Path $env:APPDATA "OpenWhisper"
$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$bureau  = [Environment]::GetFolderPath("Desktop")

Write-Host "[1/3] Arret d'OpenWhisper"
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -like '*-m openwhisper*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Get-Process -Name OpenWhisper -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

Write-Host "[2/3] Demarrage automatique et raccourcis"
cmd /c "schtasks /delete /tn OpenWhisper /f >nul 2>nul"
$global:LASTEXITCODE = 0
Remove-Item (Join-Path $startup "OpenWhisper.vbs") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $startup "OpenWhisper.lnk") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $bureau "OpenWhisper.lnk") -Force -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "OpenWhisper" -ErrorAction SilentlyContinue

Write-Host "[3/3] Cle Groq, fichiers de l'application, reglages et historique"
# La cle Groq vit dans le Gestionnaire d'identification Windows : on la retire
# avec le meme module (keyring) que l'application, tant que son Python existe.
foreach ($py in @((Join-Path $dest ".venv\Scripts\python.exe"), (Join-Path $dest "python\python.exe"))) {
    if (Test-Path $py) {
        & $py -s -c "import keyring`ntry: keyring.delete_password('OpenWhisper', 'groq_api_key')`nexcept Exception: pass" 2>$null
        break
    }
}
$global:LASTEXITCODE = 0
foreach ($d in @($dest, $donnees, (Join-Path $env:LOCALAPPDATA "Programs\OpenWhisper"))) {
    if (Test-Path $d) { Remove-Item $d -Recurse -Force -ErrorAction SilentlyContinue }
}
cmd /c "cmdkey /delete:OpenWhisper >nul 2>nul & cmdkey /delete:LegacyGeneric:target=OpenWhisper >nul 2>nul"
$global:LASTEXITCODE = 0

Write-Host ""
Write-Host "  OpenWhisper est desinstalle de ce poste."
