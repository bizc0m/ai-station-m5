# Dashboard global — V1.0.0

Interface locale macOS : état des services, tâches LoopX, modèles Ollama, lanceurs des agents installés et onglet Prompt Master.

## Démarrage

Depuis la racine du dépôt :

```sh
python3 global-dashboard/server.py
```

Ouvrir <http://127.0.0.1:8871/>. Le serveur utilise uniquement la bibliothèque standard Python. Le serveur historique à la racine requiert Python 3.9 à 3.12 (module `cgi`), comme le service macOS existant. Le `server.py` à la racine démarre aussi ce dashboard et le LoopX installé, et redirige les anciennes entrées de la station vers le dashboard.

## Installation existante requise

Cette V1 reprend les chemins du Mac JOB, définis dans les deux serveurs. Adapter les chemins des exécutables et des dossiers avant utilisation sur une autre machine. Les outils, leurs identifiants et leurs données ne sont pas inclus.

- LoopX 0.5.4 installé dans `/Users/JOB/#DEV/_Agents/loopx`, commande `/Users/JOB/.local/bin/loopx`, interface sur le port 8870.
- L’installation locale LoopX contient des correctifs de sérialisation JSON et de liste complète des tâches. Ces correctifs du paquet installé ne sont pas fournis par ce dépôt ; une installation standard peut afficher une liste partielle.
- Ollama sur 11434 ; ComfyUI sur 8188 ; service M2 configuré dans `SERVICES`.
- Codex et Claude utilisent les adaptateurs LoopX existants. Les autres boutons ouvrent les outils dans Terminal ; ils ne lancent pas les tâches LoopX.

Le dashboard indique les services inaccessibles. Aucun lancement automatique de toutes les tâches n’est activé. Le code retour d’ouverture de Terminal ne prouve pas qu’une tâche a été exécutée.

## Vérifications de cette version

Syntaxe Python et JavaScript vérifiée, API locale testée, onglets et rendu desktop/mobile observés. LoopX et Ollama ont répondu ; ComfyUI et M2 étaient inaccessibles lors de la vérification. Tous les lanceurs externes n’ont pas été retestés de bout en bout.

Les journaux, scripts de lancement générés, sauvegardes et données privées des tâches sont exclus de cette publication.
