#!/usr/bin/env bash
# Build Windows "classique" : .exe PyInstaller + installeur .bat, zippe.
# A lancer sous Windows (Git Bash) depuis la racine du depot.
# Attention : le .exe n'est pas signe ; sur un poste protege par un antivirus
# EDR, preferer l'installation sans .exe (INSTALLER-WINDOWS.bat, ou
# build-windows-sans-exe.sh pour une cle USB).
set -e
cd "$(dirname "$0")"
PY=".venv-build/Scripts/python.exe"

echo "[1/4] pip install des dependances (long, ~1 Go)..."
"$PY" -m pip install -r requirements.txt pyinstaller

echo "[2/4] Build PyInstaller..."
"$PY" -m PyInstaller --noconfirm OpenWhisper.spec

echo "[3/4] Copie du script d'installation dans le dossier de l'app..."
cp "windows-exe/Installe-OpenWhisper.bat" "dist/OpenWhisper/Installe-OpenWhisper.bat"

echo "[4/4] Compression du livrable ZIP..."
powershell.exe -NoProfile -Command "Compress-Archive -Path 'dist/OpenWhisper/*' -DestinationPath 'dist/OpenWhisper-portable.zip' -Force"

echo "BUILD_OK -> dist/OpenWhisper-portable.zip"
ls -lh dist/OpenWhisper-portable.zip
