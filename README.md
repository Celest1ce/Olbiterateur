# Olbiterateur

> **Le doigt de la vengeance informatique.**


## Fonctionnalites
- Detection de la main en temps reel grace a MediaPipe
- Extinction automatique apres maintien du majeur leve
- Affichage des FPS et du nombre de mains detectees

## Installation
1. Creez un environnement virtuel (optionnel)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Installez les dependances
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation
Lancez simplement :
```bash
python non.py
```
Si le script detecte uniquement votre majeur leve pendant quelques secondes,
un compte a rebours s'affiche avant l'extinction du PC.

## Prerequis
- Webcam fonctionnelle
- Droits administrateur pour l'arret de la machine
