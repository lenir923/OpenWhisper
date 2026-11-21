# Installer OpenWhisper sur Windows

> **Pour l'assistant IA (Claude ou autre) qui lit ce guide.**
> Vous aidez une personne qui n'est pas informaticienne à installer OpenWhisper sur son PC Windows.
> - Guidez-la **une étape à la fois**, en français et avec des mots simples. Attendez qu'elle confirme (ou qu'elle envoie une capture d'écran) avant de passer à l'étape suivante.
> - Si un message d'erreur apparaît, demandez-lui le texte exact ou une photo de l'écran, puis appuyez-vous sur la section **Dépannage**.
> - Ne lui demandez jamais de mot de passe. L'installation n'a besoin d'aucun droit administrateur.
> - Si vous avez la main sur son ordinateur (Claude Code, Cowork, etc.), vous pouvez lancer les commandes vous-même, en lui expliquant d'abord ce que vous faites.
> - Commencez par lui résumer en deux phrases ce qu'on va faire et combien de temps ça prend (environ 20 minutes).

## Ce qu'est OpenWhisper

Une dictée vocale pour Windows. On **maintient Alt + Espace**, on parle, on **relâche** : le texte s'écrit là où se trouve le curseur (mail, Word, Excel, navigateur, logiciel métier...).

Cette version est réglée **en français**, et la reconnaissance vocale tourne **entièrement sur le PC** : la voix n'est jamais envoyée sur internet. Gratuit et open source (licence MIT).

## Ce qu'il faut

- Un PC sous **Windows 10 ou 11** (64 bits).
- **3 Go** d'espace disque libre.
- **Internet pendant l'installation** : environ 700 Mo à télécharger, une seule fois. Ensuite, OpenWhisper fonctionne sans internet.
- Un **micro** (celui du PC portable, d'un casque ou d'une webcam).
- Environ **20 minutes**.

## Étape 1 : installer Python 3.12

OpenWhisper est écrit en Python. On installe le Python officiel (gratuit, signé par la Python Software Foundation).

1. Télécharger l'installeur : https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
2. Lancer le fichier téléchargé. Dans la première fenêtre :
   - **cocher « Add python.exe to PATH »** (case en bas de la fenêtre) ;
   - **décocher « Use admin privileges when installing py.exe »** si elle est cochée ;
   - cliquer sur **« Install Now »**.
3. Attendre « Setup was successful », puis cliquer sur « Close ».

Déjà installé ? Pour vérifier : ouvrir **PowerShell** (touche Windows, taper « PowerShell », Entrée) et taper `py -3.12 --version`. Si la réponse est `Python 3.12.x`, passer à l'étape 2.

## Étape 2 : télécharger OpenWhisper

1. Télécharger le ZIP : https://github.com/lenir923/OpenWhisper/archive/refs/heads/main.zip
2. Dans le dossier **Téléchargements**, faire un clic droit sur `OpenWhisper-main.zip`, puis **Propriétés**. Si une case **« Débloquer »** apparaît en bas, la cocher, puis OK. (Ça évite des avertissements de Windows.)
3. Clic droit sur le ZIP, puis **« Extraire tout... »**, puis **« Extraire »**. On obtient un dossier `OpenWhisper-main`.

## Étape 3 : lancer l'installation

1. Ouvrir le dossier `OpenWhisper-main`. S'il contient un deuxième dossier `OpenWhisper-main`, l'ouvrir aussi : il faut voir le fichier **`INSTALLER-WINDOWS.bat`**.
2. Double-cliquer sur **`INSTALLER-WINDOWS.bat`**.
   - Si Windows affiche « Windows a protégé votre ordinateur » : cliquer sur **« Informations complémentaires »**, puis **« Exécuter quand même »**.
   - Si Windows demande « Voulez-vous ouvrir ce fichier ? » : **« Exécuter »**.
3. Une fenêtre noire déroule 7 étapes. Compter **5 à 15 minutes** selon la connexion : elle télécharge d'abord les composants, puis le modèle de reconnaissance vocale (environ 480 Mo). **Ne pas la fermer** tant que ce n'est pas fini.
4. C'est réussi quand toutes les lignes de vérification sont en **OK** et que le message **« OpenWhisper est installé »** s'affiche. Appuyer sur une touche pour fermer la fenêtre.

Le dossier `OpenWhisper-main` et le ZIP peuvent ensuite être supprimés : le programme est installé dans `%LOCALAPPDATA%\OpenWhisper`.

## Étape 4 : premier essai

1. Un **petit rond de couleur** apparaît près de l'horloge, en bas à droite de l'écran (cliquer sur la petite flèche **^** s'il est caché). C'est OpenWhisper qui tourne en fond.
2. Ouvrir le **Bloc-notes** et cliquer dedans.
3. **Maintenir Alt + Espace**, dire une phrase, puis **relâcher**. Le texte s'écrit après une ou deux secondes.
4. Ça marche partout où l'on peut écrire : mails, Word, Excel, navigateur, logiciels métier.

OpenWhisper se relance **tout seul à chaque démarrage** du PC. Si on l'a quitté, le raccourci **OpenWhisper** du bureau le relance.

**Réglages** : clic droit sur le rond, puis **Settings** (l'interface est en anglais).
- **Microphone** : choisir le micro à utiliser, et tester.
- **Hotkey** : changer le raccourci clavier.
- **Dictionary** : apprendre à OpenWhisper l'orthographe de mots particuliers (noms propres, marques, jargon).
- Ne pas changer **« Speech-to-Text Provider »** pour Groq : ce mode envoie la voix sur internet et demande une clé payante. Le mode local (Whisper) est celui qui est réglé.

## Dépannage (pour l'assistant)

- **« Python 3.12 introuvable »** : Python n'est pas installé, ou ce n'est pas la version 3.12. Refaire l'étape 1 en cochant bien « Add python.exe to PATH ». Fermer la fenêtre noire, puis relancer `INSTALLER-WINDOWS.bat`. Pour vérifier, `py -0` dans PowerShell doit afficher une ligne 3.12.
- **Erreur pendant l'étape 4/7 (composants, pip)** : c'est presque toujours le réseau (coupure, proxy ou filtrage d'entreprise). Relancer `INSTALLER-WINDOWS.bat` : il reprend là où il s'est arrêté. Si le message parle de SSL, de certificat ou de proxy, essayer depuis une autre connexion (par exemple le partage de connexion du téléphone).
- **« KO modèle local » à l'étape 5/7** : le téléchargement du modèle a échoué. Le modèle vient de huggingface.co, que certains réseaux d'entreprise bloquent. Vérifier internet, ou passer par une autre connexion, puis relancer l'installeur.
- **« KO micro » ou « KO Qt » à l'étape 5/7** : il manque probablement un composant Microsoft. Installer le « Microsoft Visual C++ Redistributable » (x64) : https://aka.ms/vs/17/release/vc_redist.x64.exe (il peut demander les droits administrateur), puis relancer l'installeur. Si ça ne suffit pas, noter le message exact de la ligne KO.
- **Rien ne s'écrit quand on dicte** :
  - vérifier que le rond est bien près de l'horloge (sinon, relancer avec le raccourci du bureau) ;
  - Paramètres Windows, puis Confidentialité et sécurité, puis Microphone : « Accès au microphone » et « Autoriser les applications de bureau à accéder à votre microphone » doivent être activés ;
  - dans Settings, puis Microphone, choisir le bon micro et tester ;
  - bien **maintenir** Alt + Espace pendant toute la phrase, et relâcher seulement à la fin.
- **Alt + Espace ouvre un petit menu de fenêtre** : changer le raccourci dans Settings, puis Hotkey (par exemple Ctrl + Alt + Espace).
- **L'application se ferme toute seule** : ouvrir l'Explorateur, taper `%LOCALAPPDATA%\OpenWhisper` dans la barre d'adresse, puis double-cliquer sur `DIAGNOSTIC-OpenWhisper.bat`. L'erreur reste affichée dans la fenêtre. Le journal complet est dans `%APPDATA%\OpenWhisper\openwhisper.log`.
- **Un antivirus bloque ou supprime un fichier** : OpenWhisper surveille le clavier (pour le raccourci) et colle du texte, ce qu'un antivirus peut prendre pour un comportement suspect. Sur un PC géré par un service informatique, demander leur accord. Ne jamais désactiver l'antivirus.

### Les mêmes étapes à la main (si `INSTALLER-WINDOWS.bat` ne passe pas)

Dans PowerShell, depuis le dossier `OpenWhisper-main` qui contient `INSTALLER-WINDOWS.bat` :

```powershell
$dest = "$env:LOCALAPPDATA\OpenWhisper"
robocopy openwhisper "$dest\openwhisper" /MIR
robocopy assets "$dest\assets" /MIR
Copy-Item windows-sans-exe\OpenWhisper.vbs, windows-sans-exe\preparer_poste.py, windows-sans-exe\requirements-windows.txt, windows-sans-exe\DIAGNOSTIC-OpenWhisper.bat, windows-sans-exe\Desinstalle-OpenWhisper.bat, windows-sans-exe\desinstalle-openwhisper.ps1 $dest
py -3.12 -m venv "$dest\.venv"
& "$dest\.venv\Scripts\python.exe" -m pip install -r "$dest\requirements-windows.txt"
$env:HF_HOME = "$dest\hf"
& "$dest\.venv\Scripts\python.exe" "$dest\preparer_poste.py"
wscript.exe "$dest\OpenWhisper.vbs"
```

Pour le démarrage automatique : touches **Windows + R**, taper `shell:startup`, Entrée. Dans ce dossier, créer un raccourci dont la cible est :
`wscript.exe "%LOCALAPPDATA%\OpenWhisper\OpenWhisper.vbs"`

## Désinstaller

Ouvrir `%LOCALAPPDATA%\OpenWhisper` dans l'Explorateur et double-cliquer sur `Desinstalle-OpenWhisper.bat`. Il retire le programme, le démarrage automatique, le raccourci du bureau, les réglages et l'historique des dictées. Python peut rester installé, ou se désinstaller depuis Paramètres, puis Applications.

## Une question

Contacter la personne qui vous a transmis ce guide.

---

Version d'[OpenWhisper](https://github.com/fsouza-dot/OpenWhisper) (licence MIT), adaptée pour une installation simple en français sur Windows.
