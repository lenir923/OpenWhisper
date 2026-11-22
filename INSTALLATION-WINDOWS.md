# Installer OpenWhisper sur Windows

> **Pour l'assistant IA (Claude ou autre) qui lit ce guide.**
> Vous aidez une personne qui n'est pas informaticienne à installer OpenWhisper sur son PC Windows.
> - Guidez-la **une étape à la fois**, en français et avec des mots simples. Attendez qu'elle confirme (ou qu'elle envoie une capture d'écran) avant de passer à l'étape suivante.
> - Si un message d'erreur apparaît, demandez-lui le texte exact ou une photo de l'écran, puis appuyez-vous sur la section **Dépannage**.
> - **Ne lui demandez jamais sa clé Groq, ni aucun mot de passe.** La clé se colle uniquement dans la fenêtre noire de l'installeur, jamais dans votre conversation. Si elle vous la colle quand même, dites-lui de la supprimer dans la console Groq et d'en créer une nouvelle.
> - L'installation n'a besoin d'aucun droit administrateur.
> - Si vous avez la main sur son ordinateur (Claude Code, Cowork, etc.), vous pouvez lancer les commandes vous-même, en lui expliquant d'abord ce que vous faites. L'étape de la clé Groq reste à faire par elle.
> - Commencez par lui résumer en deux phrases ce qu'on va faire et combien de temps ça prend (environ 20 minutes).

## Ce qu'est OpenWhisper

Une dictée vocale pour Windows. On **maintient Alt + Espace**, on parle, on **relâche** : le texte s'écrit là où se trouve le curseur (mail, Word, Excel, navigateur, logiciel métier...).

Cette version est réglée **en français**. La transcription est faite par **Groq**, un service en ligne très rapide et très précis : la voix lui est envoyée à chaque dictée (Groq est une société américaine), et le texte revient en une seconde environ. OpenWhisper est gratuit et open source (licence MIT).

## Ce qu'il faut

- Un PC sous **Windows 10 ou 11** (64 bits).
- **2 Go** d'espace disque libre.
- **Internet**, pendant l'installation (environ 200 Mo à télécharger) et ensuite pour dicter.
- Un **compte Groq** (inscription gratuite), créé à l'étape 2.
- Un **micro** (celui du PC portable, d'un casque ou d'une webcam).
- Environ **20 minutes**.

## Étape 1 : installer Python 3.12

OpenWhisper est écrit en Python. On installe le Python officiel (gratuit, signé par la Python Software Foundation).

Cette étape peut être sautée : si Python 3.12 manque, l'installeur de l'étape 4 l'installe tout seul (pour cet utilisateur, sans droits administrateur). La faire à la main reste utile si l'installation automatique échoue.

1. Télécharger l'installeur : https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
2. Lancer le fichier téléchargé. Dans la première fenêtre :
   - **cocher « Add python.exe to PATH »** (case en bas de la fenêtre) ;
   - **décocher « Use admin privileges when installing py.exe »** si elle est cochée ;
   - cliquer sur **« Install Now »**.
3. Attendre « Setup was successful », puis cliquer sur « Close ».

Déjà installé ? Pour vérifier : ouvrir **PowerShell** (touche Windows, taper « PowerShell », Entrée) et taper `py -3.12 --version`. Si la réponse est `Python 3.12.x`, passer à l'étape 2.

## Étape 2 : créer une clé Groq

La clé Groq est le « badge » qui autorise OpenWhisper à utiliser le service de transcription.

1. Aller sur https://console.groq.com et créer un compte (le plus simple : « Continuer avec Google »), ou se connecter.
2. Dans le menu, ouvrir **API Keys**, puis cliquer sur **Create API Key**.
3. Lui donner un nom, par exemple `OpenWhisper`, et valider.
4. **Copier la clé** avec le bouton de copie. Elle commence par `gsk_`. Groq ne la montre **qu'une seule fois** : la garder sous la main (par exemple dans le Bloc-notes, le temps de l'installation) jusqu'à l'étape 4.

La clé est personnelle : ne pas la partager, ne pas l'envoyer par mail ni dans une conversation.

## Étape 3 : télécharger OpenWhisper

1. Télécharger le ZIP : https://github.com/lenir923/OpenWhisper/archive/refs/heads/main.zip
2. Dans le dossier **Téléchargements**, faire un clic droit sur `OpenWhisper-main.zip`, puis **Propriétés**. Si une case **« Débloquer »** apparaît en bas, la cocher, puis OK. (Ça évite des avertissements de Windows.)
3. Clic droit sur le ZIP, puis **« Extraire tout... »**, puis **« Extraire »**. On obtient un dossier `OpenWhisper-main`.

## Étape 4 : lancer l'installation

1. Ouvrir le dossier `OpenWhisper-main`. S'il contient un deuxième dossier `OpenWhisper-main`, l'ouvrir aussi : il faut voir le fichier **`INSTALLER-WINDOWS.bat`**.
2. Double-cliquer sur **`INSTALLER-WINDOWS.bat`**.
   - Si Windows affiche « Windows a protégé votre ordinateur » : cliquer sur **« Informations complémentaires »**, puis **« Exécuter quand même »**.
   - Si Windows demande « Voulez-vous ouvrir ce fichier ? » : **« Exécuter »**.
3. Une fenêtre noire déroule 7 étapes. Les composants se téléchargent d'abord (quelques minutes). **Ne pas la fermer.**
4. À l'étape **[5/7]**, la fenêtre demande la **clé Groq** : la coller **dans cette fenêtre noire** (Ctrl + V, ou clic droit), puis appuyer sur **Entrée**. Elle s'affiche en étoiles, c'est normal. L'installeur la teste auprès de Groq et l'enregistre dans le coffre-fort de Windows (Gestionnaire d'identification).
5. C'est réussi quand les lignes de vérification sont en **OK**, dont « clé Groq acceptée », et que le message **« OpenWhisper est installé »** s'affiche. Appuyer sur une touche pour fermer la fenêtre.

Le dossier `OpenWhisper-main` et le ZIP peuvent ensuite être supprimés : le programme est installé dans `%LOCALAPPDATA%\OpenWhisper`. Le Bloc-notes où la clé a été collée peut être fermé sans l'enregistrer.

## Étape 5 : premier essai

1. Un **petit rond de couleur** apparaît près de l'horloge, en bas à droite de l'écran (cliquer sur la petite flèche **^** s'il est caché). C'est OpenWhisper qui tourne en fond.
2. Ouvrir le **Bloc-notes** et cliquer dedans.
3. **Maintenir Alt + Espace**, dire une phrase, puis **relâcher**. Le texte s'écrit après une seconde environ.
4. Ça marche partout où l'on peut écrire : mails, Word, Excel, navigateur, logiciels métier.

OpenWhisper se relance **tout seul à chaque démarrage** du PC. Si on l'a quitté, le raccourci **OpenWhisper** du bureau le relance.

**Réglages** : clic droit sur le rond, puis **Settings** (l'interface est en anglais).
- **General** : la clé Groq (champ « Groq API Key ») et le service de transcription (« Speech-to-Text Provider », réglé sur Groq).
- **Microphone** : choisir le micro à utiliser, et tester.
- **Hotkey** : changer le raccourci clavier.
- **Dictionary** : apprendre à OpenWhisper l'orthographe de mots particuliers (noms propres, marques, jargon).

**Pour une équipe** : on refait l'installation sur chaque PC. Chaque personne peut créer sa propre clé (compte Groq gratuit), ou utiliser la clé d'un compte commun. Avec une clé commune, les limites de l'offre gratuite sont partagées entre tous.

## Dépannage (pour l'assistant)

- **« Python 3.12 introuvable »** : Python n'est pas installé, ou ce n'est pas la version 3.12. Refaire l'étape 1 en cochant bien « Add python.exe to PATH ». Fermer la fenêtre noire, puis relancer `INSTALLER-WINDOWS.bat`. Pour vérifier, `py -0` dans PowerShell doit afficher une ligne 3.12.
- **Erreur pendant l'étape 4/7 (composants, pip)** : c'est presque toujours le réseau (coupure, proxy ou filtrage d'entreprise). Relancer `INSTALLER-WINDOWS.bat` : il reprend là où il s'est arrêté. Si le message parle de SSL, de certificat ou de proxy, essayer depuis une autre connexion (par exemple le partage de connexion du téléphone).
- **« clé Groq refusée »** : la clé est mal copiée (il manque un bout) ou a été supprimée. Retourner sur https://console.groq.com, dans API Keys, créer une nouvelle clé, la copier avec le bouton de copie et la recoller. L'installeur laisse 3 essais, puis il suffit de le relancer.
- **« ce n'est pas une clé Groq »** : ce qui a été collé ne commence pas par `gsk_`. Recopier la clé depuis la console Groq.
- **« Groq injoignable »** : pas d'internet, ou le réseau bloque api.groq.com (proxy, pare-feu d'entreprise). Tester une autre connexion. Sur un réseau d'entreprise, il faut que le service informatique autorise api.groq.com.
- **« KO micro » ou « KO Qt » à l'étape 5/7** : il manque probablement un composant Microsoft. Installer le « Microsoft Visual C++ Redistributable » (x64) : https://aka.ms/vs/17/release/vc_redist.x64.exe (il peut demander les droits administrateur), puis relancer l'installeur. Si ça ne suffit pas, noter le message exact de la ligne KO.
- **Rien ne s'écrit quand on dicte** :
  - vérifier que le rond est bien près de l'horloge (sinon, relancer avec le raccourci du bureau) ;
  - vérifier internet : sans connexion, Groq ne répond pas ;
  - Paramètres Windows, puis Confidentialité et sécurité, puis Microphone : « Accès au microphone » et « Autoriser les applications de bureau à accéder à votre microphone » doivent être activés ;
  - dans Settings, puis Microphone, choisir le bon micro et tester ;
  - bien **maintenir** Alt + Espace pendant toute la phrase, et relâcher seulement à la fin.
- **La dictée marche, puis s'arrête un moment** : la limite de l'offre gratuite de Groq est peut-être atteinte (beaucoup de dictées en peu de temps, ou une clé partagée par plusieurs personnes). Attendre un peu. Pour un usage intensif, passer à l'offre payante dans la console Groq (rubrique Billing), ou donner une clé par personne.
- **Alt + Espace ouvre un petit menu de fenêtre** : changer le raccourci dans Settings, puis Hotkey (par exemple Ctrl + Alt + Espace).
- **L'application se ferme toute seule** : ouvrir l'Explorateur, taper `%LOCALAPPDATA%\OpenWhisper` dans la barre d'adresse, puis double-cliquer sur `DIAGNOSTIC-OpenWhisper.bat`. L'erreur reste affichée dans la fenêtre. Le journal complet est dans `%APPDATA%\OpenWhisper\openwhisper.log`.
- **Un antivirus bloque ou supprime un fichier** : OpenWhisper surveille le clavier (pour le raccourci) et colle du texte, ce qu'un antivirus peut prendre pour un comportement suspect. Sur un PC géré par un service informatique, demander leur accord. Ne jamais désactiver l'antivirus.
- **Changer de clé Groq plus tard** : clic droit sur le rond, Settings, General, champ « Groq API Key ». Ou relancer `INSTALLER-WINDOWS.bat` et coller la nouvelle clé.

### Les mêmes étapes à la main (si `INSTALLER-WINDOWS.bat` ne passe pas)

Dans PowerShell, depuis le dossier `OpenWhisper-main` qui contient `INSTALLER-WINDOWS.bat` :

```powershell
$dest = "$env:LOCALAPPDATA\OpenWhisper"
robocopy openwhisper "$dest\openwhisper" /MIR
robocopy assets "$dest\assets" /MIR
Copy-Item windows-sans-exe\OpenWhisper.vbs, windows-sans-exe\preparer_poste.py, windows-sans-exe\requirements-windows.txt, windows-sans-exe\DIAGNOSTIC-OpenWhisper.bat, windows-sans-exe\Desinstalle-OpenWhisper.bat, windows-sans-exe\desinstalle-openwhisper.ps1 $dest
py -3.12 -m venv "$dest\.venv"
& "$dest\.venv\Scripts\python.exe" -m pip install -r "$dest\requirements-windows.txt"
# La personne colle elle-meme sa cle quand la ligne "Cle Groq" s'affiche (rien ne s'affiche en tapant) :
& "$dest\.venv\Scripts\python.exe" -c "import getpass, keyring; keyring.set_password('OpenWhisper', 'groq_api_key', getpass.getpass('Cle Groq : ').strip())"
& "$dest\.venv\Scripts\python.exe" "$dest\preparer_poste.py" --groq
wscript.exe "$dest\OpenWhisper.vbs"
```

Pour le démarrage automatique : touches **Windows + R**, taper `shell:startup`, Entrée. Dans ce dossier, créer un raccourci dont la cible est :
`wscript.exe "%LOCALAPPDATA%\OpenWhisper\OpenWhisper.vbs"`

## Désinstaller

Ouvrir `%LOCALAPPDATA%\OpenWhisper` dans l'Explorateur et double-cliquer sur `Desinstalle-OpenWhisper.bat`. Il retire le programme, le démarrage automatique, le raccourci du bureau, les réglages, l'historique des dictées et la clé Groq enregistrée sur le PC. Python peut rester installé, ou se désinstaller depuis Paramètres, puis Applications. La clé peut aussi être supprimée dans la console Groq.

## Une question

Contacter la personne qui vous a transmis ce guide.

---

Version d'[OpenWhisper](https://github.com/fsouza-dot/OpenWhisper) (licence MIT), adaptée pour une installation simple en français sur Windows.
