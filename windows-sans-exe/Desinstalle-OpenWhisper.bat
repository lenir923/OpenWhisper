@echo off
rem OpenWhisper - desinstallation complete du poste (ne touche a aucun autre programme).
echo.
echo   Desinstallation d'OpenWhisper...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0desinstalle-openwhisper.ps1"
echo.
pause
