"""Prepare le poste apres la copie : reglages francais + verification.

Lance par l'installeur (installe-openwhisper.ps1 depuis la cle, ou
installe-depuis-github.ps1 depuis le code GitHub), depuis
%LOCALAPPDATA%\\OpenWhisper. Trois choses :

1. Verifie que toutes les briques s'importent (Qt, transcription, micro,
   clavier, trousseau). Si une manque, l'installation est declaree ratee.
2. Pose les reglages : francais, transcription locale (modele "small"
   multilingue), sans toucher au reste (raccourci, dictionnaire, snippets)
   si un reglage existe deja.
3. Charge le modele une fois. Depuis la cle il est deja la (HF_HUB_OFFLINE=1
   pose par l'installeur) ; depuis GitHub il est telecharge ici (~480 Mo),
   une seule fois, dans %LOCALAPPDATA%\\OpenWhisper\\hf.

Code de sortie : 0 = poste pret ; 2 = brique manquante ; 3 = modele introuvable.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))


def verifier_imports() -> bool:
    briques = [
        ("Qt (fenetres)", "PySide6.QtWidgets"),
        ("transcription", "faster_whisper"),
        ("moteur du modele", "ctranslate2"),
        ("micro", "sounddevice"),
        ("raccourci clavier", "pynput.keyboard"),
        ("trousseau Windows", "keyring"),
        ("application", "openwhisper.app"),
    ]
    ok = True
    for nom, module in briques:
        try:
            __import__(module)
            print(f"      OK  {nom}")
        except Exception as exc:  # noqa: BLE001 - on veut tout afficher
            ok = False
            print(f"      KO  {nom} ({module}) : {type(exc).__name__}: {exc}")
    return ok


def poser_reglages() -> None:
    from openwhisper.config import settings_file_path
    from openwhisper.settings import AppSettings

    chemin = settings_file_path()
    brut: dict = {}
    if chemin.exists():
        try:
            brut = json.loads(chemin.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - reglage illisible : on repart propre
            brut = {}
    brut["languages"] = ["fr"]
    brut["stt_provider"] = "whisper"
    brut["whisper_model_size"] = "small"
    try:
        reglages = AppSettings.model_validate(brut)
    except Exception:  # noqa: BLE001
        reglages = AppSettings(languages=["fr"], stt_provider="whisper", whisper_model_size="small")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(reglages.model_dump_json(indent=2), encoding="utf-8")
    print(f"      reglages poses : francais, transcription locale ({chemin})")


def verifier_modele() -> bool:
    os.environ.setdefault("HF_HOME", str(RACINE / "hf"))
    hors_ligne = os.environ.get("HF_HUB_OFFLINE") == "1"
    if not hors_ligne:
        print("      telechargement du modele de reconnaissance vocale si besoin")
        print("      (environ 480 Mo, une seule fois : quelques minutes selon la connexion)")
    try:
        from faster_whisper import WhisperModel

        t0 = time.time()
        WhisperModel("small", device="cpu", compute_type="int8")
        mode = "hors ligne" if hors_ligne else "pret, il ne sera plus telecharge"
        print(f"      OK  modele local charge en {time.time() - t0:.1f} s ({mode})")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"      KO  modele local : {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    if not verifier_imports():
        return 2
    poser_reglages()
    if not verifier_modele():
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
