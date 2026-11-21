#!/usr/bin/env bash
# ============================================================
#  Build Windows d'OpenWhisper SANS .exe compile, depuis le Mac.
#
#  Pourquoi : le .exe PyInstaller (build-windows-exe.sh) n est pas signe ; sur les
#  postes proteges par un antivirus EDR, il est ferme. Un outil passe s il livre
#  le python officiel signe + le code source. On fait pareil.
#
#  Sortie : dist/windows-sans-exe/OpenWhisper/
#      Installe-OpenWhisper.bat   <- le seul fichier a lancer sur le poste
#      installe-openwhisper.ps1, Desinstalle-*.bat/.ps1, DIAGNOSTIC-*.bat
#      bundle/  python/ (embarque 3.12 + Lib/site-packages win_amd64)
#               openwhisper/ assets/ hf/ (modele small multilingue)
#               OpenWhisper.vbs preparer_poste.py VERSION.txt
#
#  Usage :
#    PYBASE=<python embarque 3.12 Windows> MODEL_CACHE=<cache HF> ./build-windows-sans-exe.sh
#    PYBASE : ex. un python-3.12.x-embed-amd64 de python.org (on n en prend que le noyau).
#    MODEL_CACHE : dossier --cache-dir de
#      uvx --from huggingface_hub hf download Systran/faster-whisper-small \
#          config.json model.bin tokenizer.json vocabulary.txt --cache-dir <MODEL_CACHE>
#    SKIP_DEPS=1 : garde les site-packages deja installes (rebuild rapide).
# ============================================================
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/dist/windows-sans-exe/OpenWhisper"
B="$OUT/bundle"
SP="$B/python/Lib/site-packages"
W="$ROOT/windows-sans-exe"
: "${PYBASE:?PYBASE = dossier du python embarque 3.12 Windows}"
: "${MODEL_CACHE:?MODEL_CACHE = cache HF contenant Systran/faster-whisper-small}"

if [ "${SKIP_DEPS:-0}" != "1" ]; then
  echo "[1/7] Dependances Windows (win_amd64, cp312)"
  rm -rf "$OUT"; mkdir -p "$SP"
  uv pip install --target "$SP" --python-platform x86_64-pc-windows-msvc --python-version 3.12 \
    --only-binary :all: \
    faster-whisper==1.2.1 ctranslate2==4.7.2 onnxruntime==1.26.0 av==17.0.1 tokenizers==0.23.1 \
    numpy==2.4.6 pydantic==2.13.4 keyring==25.7.0 PySide6-Essentials==6.11.1 tqdm==4.67.3 \
    sounddevice pynput httpx
  # pyperclip n'a pas de wheel : pur python, installe sans build natif
  uv pip install --target "$SP" --python-platform x86_64-pc-windows-msvc --python-version 3.12 --no-deps pyperclip
else
  echo "[1/7] Dependances : gardees (SKIP_DEPS=1)"
  rm -rf "$B/openwhisper" "$B/assets" "$B/hf" "$OUT"/*.bat "$OUT"/*.ps1
fi

echo "[2/7] Aucun .exe non signe dans les dependances (lanceurs de scripts, outils)"
find "$SP" -iname "*.exe" -print -delete | sed 's/^/      retire : /'
rm -rf "$SP/bin" "$SP/Scripts"
# Le .pth de setuptools (shim distutils) est inutile a l execution et casse
# au demarrage si _distutils_hack est incomplet : on le retire.
rm -f "$SP/distutils-precedence.pth"

echo "[3/7] Noyau du python embarque (signe PSF) + runtime MSVC"
find "$PYBASE" -maxdepth 1 -type f -exec cp {} "$B/python/" \;
# Les .pyd de ctranslate2 / onnxruntime cherchent msvcp140.dll a cote de python.exe
for dll in "$SP"/PySide6/msvcp140*.dll "$SP"/PySide6/concrt140.dll; do
  [ -f "$dll" ] && cp "$dll" "$B/python/"
done
[ -f "$B/python/msvcp140.dll" ] || cp "$W/runtime/msvcp140.dll" "$B/python/"

echo "[4/7] Code de l'application"
rsync -a --exclude "__pycache__" --exclude "*.pyc" "$ROOT/openwhisper" "$B/"
rsync -a "$ROOT/assets" "$B/"
cp "$ROOT/LICENSE" "$B/LICENSE.txt"
cp "$W/OpenWhisper.vbs" "$W/preparer_poste.py" "$B/"

echo "[5/7] Modele local (faster-whisper small, multilingue)"
M="models--Systran--faster-whisper-small"
mkdir -p "$B/hf/hub/$M"
cp -R "$MODEL_CACHE/$M/refs" "$B/hf/hub/$M/"
cp -RL "$MODEL_CACHE/$M/snapshots" "$B/hf/hub/$M/"   # vrais fichiers, pas de liens

echo "[6/7] Installeurs (CRLF ; .ps1 en UTF-8 avec BOM)"
for f in Installe-OpenWhisper.bat Desinstalle-OpenWhisper.bat DIAGNOSTIC-OpenWhisper.bat \
         installe-openwhisper.ps1 desinstalle-openwhisper.ps1; do
  cp "$W/$f" "$OUT/$f"
done
for f in "$OUT"/*.bat "$OUT"/*.ps1 "$B/OpenWhisper.vbs"; do
  perl -pi -e 's/\r?\n/\r\n/' "$f"
done
for f in "$OUT"/*.ps1; do
  printf '\xEF\xBB\xBF' | cat - "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done

echo "[7/7] Trace de version"
{
  echo "OpenWhisper - build Windows sans .exe (python embarque signe)"
  echo "Construit le : $(date '+%Y-%m-%d %H:%M')"
  echo "Code         : $(git -C "$ROOT" rev-parse --short HEAD)$(git -C "$ROOT" diff --quiet || echo ' + modifs locales')"
  echo "Python       : embarque 3.12 (noyau de $PYBASE)"
  echo "Modele       : Systran/faster-whisper-small (hors ligne)"
} > "$B/VERSION.txt"
find "$OUT" -name "__pycache__" -type d -prune -exec rm -rf {} +
du -sh "$OUT"
echo "BUILD_OK -> $OUT"
