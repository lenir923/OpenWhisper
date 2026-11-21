' OpenWhisper : lanceur silencieux (aucune fenetre noire). Pas de .exe
' compile : le python officiel signe (pythonw.exe) + le code source.
' Resout son propre dossier au clic, et marche pour les deux installations :
'   - depuis la cle : python embarque dans  <dossier>\python\
'   - depuis GitHub : environnement Python dans <dossier>\.venv\
' Le modele vit dans <dossier>\hf ; HF_HUB_OFFLINE : rien ne sort du poste.
Option Explicit
Dim sh, fso, racine, env, pyw
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
racine = fso.GetParentFolderName(WScript.ScriptFullName)
pyw = racine & "\python\pythonw.exe"
If Not fso.FileExists(pyw) Then pyw = racine & "\.venv\Scripts\pythonw.exe"
If Not fso.FileExists(pyw) Then
  MsgBox "OpenWhisper n'est pas installe correctement (Python introuvable dans " & racine & "). Relancez l'installation.", 16, "OpenWhisper"
  WScript.Quit 1
End If
Set env = sh.Environment("PROCESS")
env("OPENWHISPER_BUNDLE") = "1"
env("HF_HOME") = racine & "\hf"
env("HF_HUB_OFFLINE") = "1"
env("HF_HUB_DISABLE_TELEMETRY") = "1"
sh.CurrentDirectory = racine
sh.Run """" & pyw & """ -s -m openwhisper", 0, False
