@echo off
setlocal enableextensions
title Installation OpenWhisper
chcp 65001 >nul

echo ============================================
echo    Installation d'OpenWhisper
echo ============================================
echo.
echo Patientez, copie des fichiers en cours...

set "SRC=%~dp0"
set "DEST=%LOCALAPPDATA%\Programs\OpenWhisper"
set "EXE=%DEST%\OpenWhisper.exe"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM --- Copie de l'application vers un emplacement permanent ---
if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%" 2>nul
xcopy "%SRC%*" "%DEST%\" /e /i /h /y >nul

if not exist "%EXE%" (
  echo.
  echo ERREUR : le fichier OpenWhisper.exe est introuvable apres copie.
  echo Verifiez que le dossier a bien ete decompresse en entier.
  pause
  exit /b 1
)

REM --- Raccourci de demarrage automatique (a chaque allumage) + raccourci bureau ---
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$w = New-Object -ComObject WScript.Shell;" ^
 "$s = $w.CreateShortcut(\"%STARTUP%\OpenWhisper.lnk\"); $s.TargetPath = \"%EXE%\"; $s.WorkingDirectory = \"%DEST%\"; $s.Save();" ^
 "$d = $w.CreateShortcut(($w.SpecialFolders('Desktop')) + '\OpenWhisper.lnk'); $d.TargetPath = \"%EXE%\"; $d.WorkingDirectory = \"%DEST%\"; $d.Save()"

REM --- Lancement immediat ---
start "" /d "%DEST%" "%EXE%"

echo.
echo ============================================
echo    Termine.
echo ============================================
echo.
echo OpenWhisper est installe.
echo Il se lancera tout seul a chaque demarrage de Windows.
echo Un raccourci a ete ajoute sur le bureau.
echo.
timeout /t 4 >nul
endlocal
