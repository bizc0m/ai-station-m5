# ai-station-m5

Station IA locale pour macOS Apple Silicon M5.

## Liens GitHub

- Dépôt AI-Station : <https://github.com/bizc0m/ai-station-m5>
- Dépôt Prompt Master : <https://github.com/bizc0m/prompt-master>
- CTxKNL : <https://github.com/bizc0m/prompt-master/blob/main/CTxKNL_v0.7.md>
- Versions : <https://github.com/bizc0m/prompt-master/blob/main/VERSIONS.md>
- Prompt à coller dans n'importe quel LLM : <https://github.com/bizc0m/prompt-master/blob/main/CTxKNL-launcher-prompt.txt>
- Générateur de Prompt Master : <https://bizc0m.github.io/prompt-master/>
- Prompt pure latest : <https://bizc0m.github.io/prompt-master/prompt.html>
- Prompt brut latest : <https://bizc0m.github.io/prompt-master/latest.md>
- Prompt Markdown latest : <https://bizc0m.github.io/prompt-master/prompt.md>
- Source officielle : <https://github.com/bizc0m/prompt-master/blob/main/assistant-dev-prompt.md>

## Contenu

- `AI-Station.html` : page routeur locale
- `V2/` : version propre courante
- `V2/CTxKNL_v0.7.md` : Prompt Master modulaire Context Kernel
- `CTxKNL_v0.1.md` : ancienne version / compat
- `VERSIONS.md` : numerotation et historique
- `CTxKNL-launcher-prompt.txt` : prompt court à coller dans n'importe quel LLM
- `index.html` : page publique avec simulateur projet, cartouches, générateur de modules et bookmarks/services
- `prompt.md` : prompt latest source, toujours mis à jour
- `latest.md` : alias brut latest, même contenu que `prompt.md`
- `prompt.html` : page pure latest stable qui lit `prompt.md`, même URL quelle que soit la version
- Deeplink macOS : `open "https://bizc0m.github.io/prompt-master/"`
- Bookmarklet : `javascript:(()=>{window.open('https://bizc0m.github.io/prompt-master/','_blank','noopener');})();`
- `archive/2026-08-10-ctxknl-v2/` : anciens brouillons et backups de la refonte
- `AI-Station-design-prompt.md` : brief design et historique versions
- `BDSM-18-consensuel-prompt-pack.md` : pack prompts image adulte consensuel
- `sources/_bootstrap.html` : source design de reference

## Services locaux

- ComfyUI : `http://127.0.0.1:8188/`
- Open WebUI : `http://localhost:3000/`
- Ollama : `http://127.0.0.1:11434/api/tags`

## Version

Design actuel : `v4.5`

## Git

- Dépôt local reconstitué le 2026-08-12.
- Archives conservées : `archive/`, `backups/`, `V2/`.
- Versions CTxKNL conservées : `v0.1`, `v0.4`, `v0.7`.
- Fichiers temporaires exclus : `__pycache__/`, `*.pyc`, `.DS_Store`, `tmp/`, `*.log`.

## Agents dev detectes

- Codex CLI
- Claude Code
- Aider
- Hermes
- Cursor
- ZCode
- Cline
- Goose
- OpenHands
- OpenCode
- ComfyUI

## Lanceurs iTerm

Scripts :

- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/codex.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/claude.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/claude-caveman.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/aider.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/hermes.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/cursor.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/zcode.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/cline.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/goose.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/openhands.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/opencode.command`
- `/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/launchers/comfyui.command`

## LLM local

- Racine Ollama : `/Users/JOB/.ollama/models`
- Manifests : `/Users/JOB/.ollama/models/manifests`
- Blobs/poids : `/Users/JOB/.ollama/models/blobs`
- Modele Hermes : `/Users/JOB/.ollama/models/manifests/registry.ollama.ai/library/qwen2.5-coder/14b`

## A completer

- Option lourd : TabbyML serveur autocomplete
