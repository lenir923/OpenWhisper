@echo off
rem ============================================================
rem  OpenWhisper - Installation sur le poste (dictee vocale)
rem  Double-clic depuis la cle USB. Tout en mode utilisateur,
rem  aucun droit admin requis. Pas de .exe compile :
rem  python officiel signe + code source.
rem ============================================================
echo.
echo   Installation d'OpenWhisper sur ce poste...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installe-openwhisper.ps1"
echo.
pause
