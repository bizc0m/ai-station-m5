# Audit — ai-station-m5 v1.0.1, build 1

Date : 2026-09-08. Machine : M5.lan. Dépôt : `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5`. Branche : `main`. Remote : `https://github.com/bizc0m/ai-station-m5.git`. État initial : trois commits locaux en avance, nombreuses modifications hors périmètre conservées.

## Corrections de cette itération

- Contraste : fonds sombres explicites dans station.html et control.html.
- Navigation : quatorze onglets conservés et répartis sur plusieurs lignes.
- Chat : métadonnées repliables, espacement réduit, saisie fixe.
- Réponses : ajout des mesures horodatées du dashboard à chaque envoi.
- Export : contexte technique masqué, texte utilisateur et métadonnées conservés.
- Version : SemVer 1.0.1, premier build déclaré 1.

## Preuves actuelles

- Six tests du pont de tâches exécutés avec succès.
- Syntaxe de tous les fichiers Python et scripts HTML vérifiée.
- Navigateur : cartes Agents Dev sombres observées ; chat observé à 390 × 844, menus repliables et saisie accessibles.
- Conversation réelle : 14 modèles Ollama sur M5.lan, mesure du 08/09/2026 à 05:42:22 +02:00, réponse reçue à 05:42:30. Nombre concordant avec l’API du dashboard.
- Détails de message ouverts : date, lien, priorité accessibles.
- Export téléchargé et relu : `station-ad41851644894eeca44e6c3cc9a4dba7-2026-09-08T03-43-57-762Z.md`. Dates, liens, réponse présents ; données techniques injectées absentes. Export privé exclu du dépôt.

## Limites et corrections suivantes

Cette version reste partielle. Le chat natif répond mais `/status.json` LoopX renvoie HTTP 500. Ollama répond HTTP 200 ; ComfyUI et M2 sont inaccessibles lors du relevé. Ces états sont ponctuels.

1. Diagnostiquer l’erreur de statut et l’erreur de prévisualisation LoopX décrite dans README. Un nouvel envoi de tâche entièrement par HTTP n’est pas validé. Aucun ancien travail n’a été relancé pour cet audit.
2. Ajouter le choix modèle et destination au chat, actuellement fixé sur Codex et `station-tasks`.
3. Vérifier réellement chaque agent et le routage M2 ; présence d’un binaire ne prouve pas son fonctionnement.
4. Actualiser les informations statiques des fiches Agents Dev.
5. Les priorités restent locales au navigateur. NotePlan charge un brouillon ; cela ne prouve pas l’exécution d’une tâche. Aucun coffre NotePlan n’a été modifié.
6. Git des projets exécutés et publication des fiches ne sont pas automatiques.

## Sauvegarde

Périmètre : README.md, AUDIT-1.0.1.md, release.json, index.html, station.html, control.html, conversation.html et server.py dans global-dashboard.

Le commit et les tags sont identifiables dans Git par `ai-station-m5-v1.0.1` et `ai-station-m5-v1.0.1-build1`. La vérification distante doit être réalisée après publication ; ce document ne la présume pas. Livrable : code du dashboard servi localement, aucun installateur.
