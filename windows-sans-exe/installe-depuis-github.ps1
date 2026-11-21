# ============================================================
#  Installation d'OpenWhisper depuis le code GitHub (Windows 10/11 64 bits)
#  Lance par INSTALLER-WINDOWS.bat, a la racine du dossier telecharge.
#
#  Prerequis : Python 3.12 installe depuis python.org (pour l'utilisateur,
#  sans droits admin). Tout le reste se fait ici, en mode utilisateur :
#   - copie le programme dans %LOCALAPPDATA%\OpenWhisper (le dossier
#     telecharge peut ensuite etre supprime) ;
#   - cree un environnement Python dedie (.venv) et y installe les
#     dependances (~200 Mo, une seule fois) ;
#   - regle l'appli en francais, transcription 100% locale, et telecharge
#     le modele de reconnaissance (~480 Mo, une seule fois) ;
#   - raccourci bureau + demarrage automatique a l'ouverture de session.
#  Aucun .exe compile, aucun droit admin. Relancable : il reprend et remet
#  tout d'aplomb. Fichier en ASCII pur (PowerShell 5.1).
# ============================================================
$ErrorActionPreference = "Stop"

$w       = Split-Path -Parent $MyInvocation.MyCommand.Path      # ...\windows-sans-exe
$src     = Split-Path -Parent $w                                 # racine du depot
$dest    = Join-Path $env:LOCALAPPDATA "OpenWhisper"
$venvPy  = Join-Path $dest ".venv\Scripts\python.exe"
$vbs     = Join-Path $dest "OpenWhisper.vbs"
$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$bureau  = [Environment]::GetFolderPath("Desktop")

if (-not (Test-Path (Join-Path $src "openwhisper\__main__.py"))) {
    throw "Dossier 'openwhisper' introuvable a cote de l'installeur : decompresser TOUT le ZIP, puis relancer INSTALLER-WINDOWS.bat."
}

# --- 1. Python 3.12 -------------------------------------------------------------
Write-Host "[1/7] Recherche de Python 3.12"
function Get-Python312([string]$exe, [string[]]$avant) {
    try {
        $out = & $exe @avant -c "import sys; print(sys.version_info[:2] == (3, 12)); print(sys.executable)" 2>$null
        $global:LASTEXITCODE = 0
        if ($out -and $out.Count -ge 2 -and $out[0] -eq "True") { return $out[1] }
    } catch { }
    $global:LASTEXITCODE = 0
    return $null
}
$pyBase = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $pyBase = Get-Python312 "py" @("-3.12") }
if (-not $pyBase) {
    $p = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path $p) { $pyBase = Get-Python312 $p @() }
}
if (-not $pyBase) {
    $c = Get-Command python -ErrorAction SilentlyContinue
    # L'alias "python" de WindowsApps ouvre le Microsoft Store : on l'ignore.
    if ($c -and $c.Source -notlike "*WindowsApps*") { $pyBase = Get-Python312 $c.Source @() }
}
if (-not $pyBase) {
    throw "Python 3.12 introuvable. Installer Python 3.12 depuis python.org (etape 1 du guide, cocher 'Add python.exe to PATH'), fermer cette fenetre et relancer INSTALLER-WINDOWS.bat."
}
Write-Host "      Python : $pyBase"

# --- 2. Arreter une version deja lancee -----------------------------------------
# Seulement NOTRE python (ligne de commande "-m openwhisper").
Write-Host "[2/7] Arret d'une version deja lancee"
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -like '*-m openwhisper*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Get-Process -Name OpenWhisper -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

# --- 3. Copier le programme -----------------------------------------------------
Write-Host "[3/7] Copie du programme dans $dest"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
# Une ancienne installation par cle USB (python embarque) passerait devant le .venv.
$embarque = Join-Path $dest "python"
if (Test-Path $embarque) { Remove-Item $embarque -Recurse -Force }
foreach ($d in @("openwhisper", "assets")) {
    robocopy (Join-Path $src $d) (Join-Path $dest $d) /MIR /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
    $code = $LASTEXITCODE
    $global:LASTEXITCODE = 0          # robocopy : 0-7 = succes, >= 8 = echec reel
    if ($code -ge 8) { throw "Copie de '$d' echouee (robocopy code $code)." }
}
foreach ($f in @("OpenWhisper.vbs", "preparer_poste.py", "requirements-windows.txt",
                 "Desinstalle-OpenWhisper.bat", "desinstalle-openwhisper.ps1", "DIAGNOSTIC-OpenWhisper.bat")) {
    Copy-Item (Join-Path $w $f) (Join-Path $dest $f) -Force
}
Copy-Item (Join-Path $src "LICENSE") (Join-Path $dest "LICENSE.txt") -Force

# --- 4. Environnement Python + dependances ------------------------------------
Write-Host "[4/7] Environnement Python et composants (~200 Mo la premiere fois, quelques minutes)"
if (-not (Test-Path $venvPy)) {
    & $pyBase -m venv (Join-Path $dest ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Creation de l'environnement Python impossible (code $LASTEXITCODE)." }
}
& $venvPy -m pip install --disable-pip-version-check --no-input -r (Join-Path $dest "requirements-windows.txt")
if ($LASTEXITCODE -ne 0) {
    throw "L'installation des composants a echoue (pip, code $LASTEXITCODE) : voir le message au-dessus. Verifier internet et relancer INSTALLER-WINDOWS.bat (il reprend)."
}
$global:LASTEXITCODE = 0

# --- 5. Reglages francais + modele + verification ------------------------------
Write-Host "[5/7] Reglages (francais, transcription locale), modele et verification"
$env:OPENWHISPER_BUNDLE = "1"
$env:HF_HOME = Join-Path $dest "hf"
$env:HF_HUB_DISABLE_TELEMETRY = "1"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
Remove-Item Env:\HF_HUB_OFFLINE -ErrorAction SilentlyContinue
& $venvPy -s (Join-Path $dest "preparer_poste.py")
$verif = $LASTEXITCODE
$global:LASTEXITCODE = 0
if ($verif -ne 0) {
    throw "La verification a echoue (code $verif) : voir les lignes KO au-dessus (section Depannage du guide)."
}

# --- 6. Raccourci bureau + demarrage automatique ------------------------------
Write-Host "[6/7] Raccourci bureau et demarrage automatique"
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $bureau "OpenWhisper.lnk"))
$lnk.TargetPath       = "wscript.exe"
$lnk.Arguments        = '"' + $vbs + '"'
$lnk.WorkingDirectory = $dest
$lnk.IconLocation     = (Join-Path $dest "assets\icon.ico") + ",0"
$lnk.Description      = "OpenWhisper : dictee vocale (maintenir Alt + Espace)"
$lnk.Save()

# Jeton d'arret de parsing (--%) + variable d'environnement : PowerShell ne
# retouche pas les guillemets de /tr (idiome eprouve sur postes sans admin).
$env:OPENWHISPER_VBS_AUTOSTART = $vbs
schtasks --% /create /tn "OpenWhisper" /tr "wscript.exe \"%OPENWHISPER_VBS_AUTOSTART%\"" /sc ONLOGON /f
$codeTache = $LASTEXITCODE
$global:LASTEXITCODE = 0
Remove-Item Env:\OPENWHISPER_VBS_AUTOSTART -ErrorAction SilentlyContinue

$repliDemarrage = Join-Path $startup "OpenWhisper.vbs"
if ($codeTache -eq 0) {
    Remove-Item $repliDemarrage -Force -ErrorAction SilentlyContinue
    Write-Host "      OpenWhisper demarrera a chaque ouverture de session."
} else {
    Write-Host "      tache planifiee refusee (code $codeTache) : repli sur le dossier Demarrage."
    $repli = @'
' Repli d'autostart OpenWhisper (dossier Demarrage), pose quand la tache
' planifiee n'a pas pu etre creee. Resout %LOCALAPPDATA% au logon.
Dim sh, cible
Set sh = CreateObject("WScript.Shell")
cible = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\OpenWhisper\OpenWhisper.vbs")
sh.Run "wscript.exe """ & cible & """", 0, False
'@
    try {
        New-Item -ItemType Directory -Force -Path $startup -ErrorAction Stop | Out-Null
        Set-Content -Path $repliDemarrage -Value $repli -Encoding ASCII
        Write-Host "      demarrage automatique pose dans le dossier Demarrage."
    } catch {
        Write-Host "      demarrage automatique impossible ($_) : lancer OpenWhisper depuis le bureau."
    }
}

# --- 7. Lancer ------------------------------------------------------------------
Write-Host "[7/7] Lancement"
Start-Process -FilePath "wscript.exe" -ArgumentList ('"' + $vbs + '"') -WorkingDirectory $dest

Write-Host ""
Write-Host "  ============================================"
Write-Host "   OpenWhisper est installe."
Write-Host "  ============================================"
Write-Host "  - Il tourne en fond : un petit rond de couleur pres de l'horloge"
Write-Host "    (cliquer sur la fleche ^ s'il est cache). Clic droit : Settings / Quit."
Write-Host "  - Pour dicter : MAINTENIR Alt + Espace, parler, relacher."
Write-Host "    Le texte s'ecrit la ou se trouve le curseur."
Write-Host "  - Tout reste sur ce PC : la voix n'est envoyee nulle part."
Write-Host "  - Il redemarre tout seul a chaque ouverture de session."
Write-Host "  - Le dossier telecharge (et le ZIP) peuvent etre supprimes."
