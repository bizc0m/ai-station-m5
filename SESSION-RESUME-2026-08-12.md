# Session Resume - AI-Station / Prompt Master

Date: 2026-08-12
Thread: codex://threads/019fef4f-66a3-7243-8560-dc2291660163
Mode: Dev
Etat: reprise conseillee avant suite longue

## Objectif

Stabiliser AI-Station, Prompt Master / CTxKNL, le composeur Bash et les regles de livraison Git/Bash/iTerm.

## Etat actuel

- AI-Station locale: http://127.0.0.1:8765/AI-Station.html
- Repo AI-Station: https://github.com/bizc0m/ai-station-m5
- Repo Prompt Master: https://github.com/bizc0m/prompt-master
- Prompt Master officiel pousse.
- AI-Station reconstitue en depot Git local et pousse sur GitHub.
- Page locale verifiee en HTTP 200.

## Decisions

- Ne pas pousser sans demande explicite, sauf demande directe de push.
- Compteur prompt systematique des que Prompt Master / CTxKNL est charge.
- A 30 prompts: STOP, resume de reprise, nouveau chat conseille.
- Bash necessaire: fournir bloc bash copiable + lien iTerm automatique si possible.
- Lien iTerm: uniquement via `.command` ou route locale controlee, jamais bash arbitraire encode dans URL.
- UI AI-Station: compacte, operationnelle, pas landing page.
- AI-Station doit garder `archive/`, `backups/`, `V2/`.

## Commits

- prompt-master: `a8fb8ff prompt: require bash launch links`
- prompt-master: `e602805 prompt: make counter footer systematic`
- ai-station-m5: `d38ea8a prompt: add bash launch link rule`
- ai-station-m5: `db7901f chore: reconstruct ai station git history`

## Tags AI-Station

- `ctxknl-v0.1`
- `ctxknl-v0.4`
- `ctxknl-v0.7`

## Fichiers importants

- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/AI-Station.html`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/server.py`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/CTxKNL_v0.7.md`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/latest.md`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/V2/`
- `/Users/JOB/#DEV/01-projets/Tools/prompt-master/assistant-dev-prompt.md`
- `/Users/JOB/#DEV/01-projets/Tools/prompt-master/CTxKNL_v0.7.md`
- `/Users/JOB/#DEV/01-projets/Tools/prompt-master/latest.md`

## A verifier au prochain demarrage

- `files-nav.html` est non suivi dans `ai-station-m5`; decider garder, archiver ou ignorer.
- Verifier visuellement que `BASH GO` apparait tout en haut.
- Tester `/llm-launch` avec un chemin autorise et un chemin refuse.
- Verifier que V2 reste synchronise avec les fichiers actifs utiles.
- Mettre a jour README/VERSIONS si nouvelle modification fonctionnelle.

## Tests faits

- AI-Station locale: HTTP 200.
- GitHub AI-Station: HTTP 200.
- GitHub Prompt Master: HTTP 200.
- Git push Prompt Master OK.
- Git push AI-Station OK.

## Prompt de reprise conseille

Charge CTxKNL depuis:
https://raw.githubusercontent.com/bizc0m/prompt-master/main/CTxKNL_v0.7.md

Travaille dans:
`/Users/JOB/#DEV/01-projets/Tools/ai-station-m5`

Repo:
`https://github.com/bizc0m/ai-station-m5`

Reprends depuis:
`/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/SESSION-RESUME-2026-08-12.md`

Mission:
1. Lire le resume.
2. Verifier l'etat Git.
3. Verifier AI-Station locale.
4. Traiter `files-nav.html`.
5. Continuer uniquement le prochain objectif demande.

Contraintes:
- Ne pas supprimer sans archiver.
- Ne pas push sans demande explicite.
- Bash necessaire = bloc copiable + lien iTerm si possible.
- Reponse courte ACT / RES / NEXT.
