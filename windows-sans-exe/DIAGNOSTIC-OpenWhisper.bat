@echo off
rem ============================================================
rem  OpenWhisper - lancement AVEC fenetre, pour voir l'erreur
rem  si l'appli se ferme toute seule. Quitter d'abord celle qui
rem  tourne (clic droit sur le rond pres de l'horloge, Quit).
rem ============================================================
set "OW=%LOCALAPPDATA%\OpenWhisper"
set "PY=%OW%\python\python.exe"
if not exist "%PY%" set "PY=%OW%\.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo.
  echo   OpenWhisper n'est pas installe sur ce PC : lancer d'abord l'installation.
  echo.
  pause
  exit /b 1
)
set "OPENWHISPER_BUNDLE=1"
set "HF_HOME=%OW%\hf"
set "HF_HUB_OFFLINE=1"
set "HF_HUB_DISABLE_TELEMETRY=1"
cd /d "%OW%"
echo.
echo   OpenWhisper tourne dans cette fenetre. Ferme-la pour l'arreter.
echo.
"%PY%" -s -m openwhisper
echo.
echo   OpenWhisper s'est arrete (code %errorlevel%).
echo   Journal complet : %APPDATA%\OpenWhisper\openwhisper.log
echo.
pause
