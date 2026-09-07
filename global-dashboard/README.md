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

## V1.1 — Tâches et résultats (2026-09-07)

L’onglet **Tâches & résultats** appelle les actions natives LoopX `todo.create` avec `start_execution=true`. Il ne simule pas une exécution par ouverture de Terminal. Codex doit être rattaché au Goal choisi via `agent.bind` ; ce rattachement a été appliqué à `station-tasks`.

Parcours : lecture seule des tâches NotePlan ou saisie → aperçu du projet et de la demande → création/exécution → suivi durable de la session et du tour → réponse dans l’interface → fiche dans le clone Unification et index local régénéré. Le bouton de validation demande une preuve puis utilise la clôture native LoopX. Aucune validation métier n’est déduite de la seule réponse du modèle.

Les demandes et reçus privés sont dans `task-data/`, ignoré par Git. Le suivi reprend au démarrage ; il ne renvoie pas une action d’exécution après une réponse réseau incertaine. Un identifiant persistant évite le double envoi. Les anciennes tâches ne sont jamais relancées. La source NotePlan n’est ni modifiée ni cochée. Lecture limitée à 200 tâches/8 secondes, avec signalement des résultats partiels ; archives, dossiers cachés et pièces jointes exclus.

Configuration : `STATION_LOOPX_REGISTRY` sélectionne le registre, `STATION_NOTEPLAN_ROOT` le dossier contenant `Notes` et `Calendar`. Seuls les projets actifs du registre sont proposés, avec leur dossier affiché. Le Goal actuel vise le workspace LoopX ; il ne donne pas automatiquement accès en écriture à tous les projets ou à l’autre Mac. Les lanceurs des autres agents restent distincts.

Vérifications : `python3 global-dashboard/test_task_bridge.py` couvre non-duplication, envoi incertain, corrélation du tour, distinction réponse/validation, lecture NotePlan et rejet des chemins invalides. Test réel du formulaire : tâche dédiée, fichier `dashboard-execution-proof.txt` créé par Codex, relu indépendamment et conforme à `STATION_EXECUTION_OK`, réponse récupérée, fiche/index générés, import NotePlan dans le formulaire sans envoi, état conservé après redémarrage.

Les commits et push des projets exécutés, la publication distante des fiches et le déploiement sur M2 ne sont pas automatiques. Une tâche peut encore rencontrer une permission manquante ou une erreur d’agent ; le dashboard doit alors afficher ce blocage.

### Blocage découvert pendant le test réel

L’API native LoopX renvoie parfois `Typed action preview could not be created` lors de la préparation et de la clôture. L’exécution de preuve a nécessité de créer sa prévisualisation avec le service canonique Python, puis a été lancée depuis le formulaire. Ce test prouve l’exécution et le retour/archivage, mais ne valide donc PAS encore un nouvel envoi autonome entièrement par HTTP. Le redémarrage de LoopX n’a pas corrigé l’erreur. La clôture du test n’est pas encore confirmée.

Le diagnostic temporaire du serveur installé (trace d’exception et redémarrage) a été refusé par le contrôle automatique ; accord utilisateur explicite demandé. Tant que cette cause n’est pas corrigée, conserver les demandes en préparation et leurs identifiants, ne pas contourner le problème en recréant des tâches ni annoncer le parcours entièrement opérationnel.

## Présentation Nyx — 2026-09-07

Palette sombre issue de la référence Nyx fournie, barre compacte, treize onglets conservés, navigation latérale groupée et repliable. Les panneaux de synthèse se replient ; les préférences sont conservées localement. Le formulaire tâches utilise la même palette. Les pages intégrées de même origine reçoivent un thème visuel ; les applications externes conservent leur interface.

Vérifications : syntaxe JavaScript, navigation des onglets, repli des menus/panneaux, rendu desktop et largeur mobile 390 px sans débordement du dashboard ni du formulaire. Aucun envoi de tâche ni démarrage d’agent déclenché pour tester ce design. Le blocage de prévisualisation LoopX décrit ci-dessus reste distinct de cette modification visuelle. Le fractionnement libre et le déplacement des panneaux du mockup ne sont pas implémentés.

## Chat compact — 2026-09-07

Chat placé en premier et ouvert par défaut sans fragment URL. Navigation latérale fermée par défaut, texte de conversation 15 px (saisie 16 px sur mobile), messages et saisie fixe en bas. Les treize sections précédentes restent disponibles. La session est conservée dans le navigateur après ouverture et les messages restent stockés par LoopX.

Le serveur expose uniquement ouverture, lecture et envoi de conversation via les API natives LoopX. Le chat utilise Codex en contexte goal station-tasks, distinct du lancement de tâches. Test réel dans le navigateur : demande sans outils, réponse CHAT_OK reçue. Largeur mobile vérifiée à 390 px sans débordement. Le problème de prévisualisation des tâches est inchangé.
