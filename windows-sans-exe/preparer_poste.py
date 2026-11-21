"""Prepare le poste apres la copie : reglages francais + verification.

Lance par l'installeur depuis %LOCALAPPDATA%\\OpenWhisper :
- installe-depuis-github.ps1 -> mode Groq (`--groq`) : transcription par
  l'API Groq, rapide et precise. La cle arrive par la variable
  d'environnement OPENWHISPER_GROQ_KEY (jamais en argument : elle serait
  visible dans la liste des processus), est testee aupres de Groq, puis
  rangee dans le Gestionnaire d'identification Windows (keyring), la ou
  l'application la lit.
- installe-openwhisper.ps1 (cle USB) -> mode local : modele "small" livre
  sur la cle, charge hors ligne (HF_HUB_OFFLINE=1 pose par l'installeur).

Dans les deux cas : verifie que toutes les briques s'importent, puis pose
les reglages (francais + mode choisi) sans toucher au reste (raccourci,
dictionnaire, snippets) si un reglage existe deja.

Code de sortie : 0 = poste pret ; 2 = brique manquante ; 3 = modele local
introuvable ; 4 = cle Groq absente ou refusee ; 5 = Groq injoignable.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))

GROQ_TEST_URL = "https://api.groq.com/openai/v1/models"


def verifier_imports(groq: bool) -> bool:
    briques = [
        ("Qt (fenetres)", "PySide6.QtWidgets"),
        ("micro", "sounddevice"),
        ("raccourci clavier", "pynput.keyboard"),
        ("trousseau Windows", "keyring"),
        ("application", "openwhisper.app"),
    ]
    if groq:
        briques.insert(1, ("connexion a Groq", "httpx"))
    else:
        briques[1:1] = [("transcription", "faster_whisper"), ("moteur du modele", "ctranslate2")]
    ok = True
    for nom, module in briques:
        try:
            __import__(module)
            print(f"      OK  {nom}")
        except Exception as exc:  # noqa: BLE001 - on veut tout afficher
            ok = False
            print(f"      KO  {nom} ({module}) : {type(exc).__name__}: {exc}")
    return ok


def poser_reglages(groq: bool) -> None:
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
    brut["stt_provider"] = "groq" if groq else "whisper"
    brut["whisper_model_size"] = "small"
    try:
        reglages = AppSettings.model_validate(brut)
    except Exception:  # noqa: BLE001
        reglages = AppSettings(languages=["fr"], stt_provider=brut["stt_provider"], whisper_model_size="small")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(reglages.model_dump_json(indent=2), encoding="utf-8")
    mode = "transcription par Groq" if groq else "transcription locale"
    print(f"      reglages poses : francais, {mode}")


def tester_cle_groq(cle: str) -> int:
    """0 = cle acceptee ; 4 = refusee ; 5 = Groq injoignable."""
    import httpx

    try:
        r = httpx.get(GROQ_TEST_URL, headers={"Authorization": f"Bearer {cle}"}, timeout=20)
    except Exception as exc:  # noqa: BLE001
        print(f"      KO  Groq injoignable ({type(exc).__name__}) : verifier internet, proxy ou pare-feu.")
        return 5
    if r.status_code == 200:
        return 0
    if r.status_code in (401, 403):
        print("      KO  cle Groq refusee : elle est mal copiee, ou a ete supprimee dans la console Groq.")
        return 4
    print(f"      KO  Groq a repondu {r.status_code} : reessayer dans une minute.")
    return 5


def preparer_groq() -> int:
    from openwhisper.keyring_store import SecretStore

    store = SecretStore()
    collee = "".join(os.environ.get("OPENWHISPER_GROQ_KEY", "").split())
    if collee:
        if not collee.startswith("gsk_"):
            print("      KO  ce n'est pas une cle Groq : elle doit commencer par gsk_")
            return 4
        code = tester_cle_groq(collee)
        if code != 0:
            return code
        store.set_groq_key(collee)
        if store.get_groq_key() != collee:
            print("      KO  impossible d'enregistrer la cle dans le Gestionnaire d'identification Windows.")
            return 4
        print("      OK  cle Groq acceptee et enregistree (Gestionnaire d'identification Windows)")
        return 0
    existante = store.get_groq_key()
    if not existante:
        print("      KO  aucune cle Groq collee, et aucune deja enregistree sur ce PC.")
        return 4
    code = tester_cle_groq(existante)
    if code == 0:
        print("      OK  cle Groq deja enregistree, toujours valide")
    return code


def verifier_modele_local() -> bool:
    os.environ.setdefault("HF_HOME", str(RACINE / "hf"))
    try:
        from faster_whisper import WhisperModel

        t0 = time.time()
        WhisperModel("small", device="cpu", compute_type="int8")
        print(f"      OK  modele local charge en {time.time() - t0:.1f} s")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"      KO  modele local : {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    groq = "--groq" in sys.argv[1:]
    if not verifier_imports(groq):
        return 2
    if groq:
        code = preparer_groq()
        if code != 0:
            return code
        poser_reglages(groq=True)
        return 0
    poser_reglages(groq=False)
    return 0 if verifier_modele_local() else 3


if __name__ == "__main__":
    sys.exit(main())
