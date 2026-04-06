# Guide de Génération de l'APK E.D.I.T.H

Votre dossier mobile est prêt. Voici comment transformer ce dossier en fichier `.apk` installable :

## Option 1 : Utilisation de Flet (La plus simple)
Flet permet de tester l'application instantanément sur votre téléphone sans même compiler d'APK :
1.  Installez l'application **Flet** sur le Play Store.
2.  Dans votre terminal sur PC, lancez : `flet run --android mobile_app.py`
3.  L'application s'ouvrira directement sur votre smartphone !

## Option 2 : Compiler un APK via GitHub (Gratuit & Cloud)
1.  Créez un dépôt GitHub (ex: `PocketAI-Android`).
2.  Uploadez le contenu du dossier `PocketAI_Mobile`.
3.  Ajoutez un workflow GitHub Action (Buildozer).
4.  GitHub vous donnera le fichier `.apk` téléchargeable dans l'onglet "Actions".

## Option 3 : Lancer en "Web App" (PWA)
C'est la solution que je recommande pour votre question sur l'hébergement :
1.  Hébergez le code sur **Vercel** ou **Netlify**.
2.  Ouvrez le lien sur votre navigateur Android.
3.  Cliquez sur "Ajouter à l'écran d'accueil". 
*L'icône E.D.I.T.H apparaîtra et l'IA fonctionnera exactement comme une application native.*
