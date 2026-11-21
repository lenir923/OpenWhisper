@echo off
rem ============================================================
rem  OpenWhisper - installation sur ce PC Windows (dictee vocale)
rem  Double-clic. Prerequis : Python 3.12 (python.org).
rem  Aucun droit admin requis. Guide : INSTALLATION-WINDOWS.md
rem ============================================================
echo.
echo   Installation d'OpenWhisper sur ce PC...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows-sans-exe\installe-depuis-github.ps1"
echo.
pause
