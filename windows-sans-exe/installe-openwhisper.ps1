# ============================================================
#  Installeur OpenWhisper (dictee vocale) depuis une cle USB preparee par
#  build-windows-sans-exe.sh - lance par Installe-OpenWhisper.bat.
#  (Depuis le code GitHub : INSTALLER-WINDOWS.bat a la racine du depot.)
#
#  Concu pour les postes proteges par un antivirus de type EDR :
#   - PAS de .exe compile (un binaire non signe est la cible n.1 de
#     l'antivirus) : le python officiel signe + le code source ;
#   - 100% mode utilisateur : %LOCALAPPDATA%\OpenWhisper, aucun admin ;
#   - lanceur .vbs silencieux (pythonw, aucune fenetre noire), raccourci
#     bureau vers wscript.exe ;
#   - demarrage auto par tache utilisateur ONLOGON, repli dossier Demarrage ;
#   - transcription 100% locale : le modele est sur la cle, la voix ne
#     quitte jamais le poste (HF_HUB_OFFLINE).
#
#  Idempotent : on peut le relancer, il remet tout d'aplomb.
#  Fichier en ASCII pur, enregistre en UTF-8 avec BOM (PowerShell 5.1).
# ============================================================
$ErrorActionPreference = "Stop"

$src    = Split-Path -Parent $MyInvocation.MyCommand.Path
$bundle = Join-Path $src "bundle"
$dest   = Join-Path $env:LOCALAPPDATA "OpenWhisper"
$vbs    = Join-Path $dest "OpenWhisper.vbs"
$py     = Join-Path $dest "python\python.exe"
$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$bureau  = [Environment]::GetFolderPath("Desktop")

if (-not (Test-Path (Join-Path $bundle "python\pythonw.exe"))) {
    throw "bundle\python introuvable a cote de l'installeur : la cle est incomplete, previens Leni."
}

# --- 1. Arreter ce qui tourne ------------------------------------------------
# Seulement NOTRE python (ligne de commande "-m openwhisper") : d'autres
# outils peuvent tourner en pythonw sur le poste, on n'y touche pas.
Write-Host "[1/6] Arret d'une version deja lancee"
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -like '*-m openwhisper*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Get-Process -Name OpenWhisper -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

# --- 2. Retirer l'ancienne version (.exe PyInstaller de juin) ----------------
Write-Host "[2/6] Retrait de l'ancienne version (.exe) si elle est la"
$ancien = Join-Path $env:LOCALAPPDATA "Programs\OpenWhisper"
if (Test-Path $ancien) { Remove-Item $ancien -Recurse -Force -ErrorAction SilentlyContinue }
Remove-Item (Join-Path $startup "OpenWhisper.lnk") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $bureau "OpenWhisper.lnk") -Force -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "OpenWhisper" -ErrorAction SilentlyContinue

# --- 3. Copier l'application ---------------------------------------------------
Write-Host "[3/6] Copie de l'application (environ 1 Go, 1 a 3 minutes)"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
robocopy $bundle $dest /MIR /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
$code = $LASTEXITCODE
$global:LASTEXITCODE = 0          # robocopy : 0-7 = succes, >= 8 = echec reel
if ($code -ge 8) { throw "robocopy a echoue (code $code) : copie incomplete, relance l'installeur." }

# --- 4. Reglages + verification sur le poste ----------------------------------
Write-Host "[4/6] Reglages (francais, transcription locale) et verification du poste"
$env:OPENWHISPER_BUNDLE = "1"
$env:HF_HOME = Join-Path $dest "hf"
$env:HF_HUB_OFFLINE = "1"
$env:HF_HUB_DISABLE_TELEMETRY = "1"
& $py -s (Join-Path $dest "preparer_poste.py")
$verif = $LASTEXITCODE
$global:LASTEXITCODE = 0
if ($verif -ne 0) {
    throw "La verification a echoue (code $verif), voir le message au-dessus. Ne pas utiliser ce poste, previens Leni."
}

# --- 5. Raccourci bureau + demarrage automatique ------------------------------
Write-Host "[5/6] Raccourci bureau et demarrage automatique"
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
    Write-Host "      tache creee : OpenWhisper demarrera a chaque ouverture de session."
} else {
    Write-Warning "      schtasks a refuse la tache (code $codeTache) : repli sur le dossier Demarrage."
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
        Write-Host "      repli d'autostart pose dans le dossier Demarrage."
    } catch {
        Write-Warning "      repli Demarrage impossible ($_) : lancer OpenWhisper a la main depuis le bureau."
    }
}

# --- 6. Lancer ------------------------------------------------------------------
Write-Host "[6/6] Lancement"
Start-Process -FilePath "wscript.exe" -ArgumentList ('"' + $vbs + '"') -WorkingDirectory $dest

Write-Host ""
Write-Host "  ============================================"
Write-Host "   OpenWhisper est installe."
Write-Host "  ============================================"
Write-Host "  - Il tourne en fond : un petit rond de couleur pres de l'horloge"
Write-Host "    (cliquer sur la fleche ^ s'il est cache). Clic droit : Settings / Quit."
Write-Host "  - Pour dicter : MAINTENIR Alt + Espace, parler, relacher."
Write-Host "    Le texte s'ecrit la ou se trouve le curseur."
Write-Host "  - Tout reste sur ce poste : la voix n'est envoyee nulle part."
Write-Host "  - Il redemarre tout seul a chaque ouverture de session."
Write-Host "  - S'il ne se lance pas : DIAGNOSTIC-OpenWhisper.bat sur la cle."
