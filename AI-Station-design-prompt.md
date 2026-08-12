# AI-Station Design Prompt

## Projet

IA Local Install M5

## Fichier cible

- `/Users/JOB/#AI/_Tools/ai-station-m5/AI-Station.html`
- Version design : `v4.1`

## Source design

- `/Users/JOB/#AI/_Tools/sources/_bootstrap.html`

## Intention

Appliquer a AI-Station le style du template "La Meute / Digital Athanor" :

- fond blanc papier avec grille laboratoire subtile
- texte noir, gris pierre, rouge rubedo unique
- typographie editoriale serif pour les titres
- mono espace pour labels, versions et commandes
- boutons rouges arrondis
- cartes sobres, bordures fines, accents rouges
- interface claire, dense, lisible, sans neon

## Contraintes fonctionnelles

Conserver les services et liens :

- ComfyUI : `http://127.0.0.1:8188/`
- Sorties images : `../../Images/outputs/`
- Open WebUI : `http://localhost:3000/`
- Ollama : `http://127.0.0.1:11434/api/tags`

Conserver les onglets :

- Accueil
- Images
- Erotique 18+
- Chat
- API
- Dossiers
- Commandes

## Regles de version

A chaque nouveau redesign :

1. Incrementer `<meta name="ai-station-design-version" content="x.x">`.
2. Mettre a jour le badge visible `DESIGN vx.x`.
3. Mettre a jour le footer.
4. Archiver ou copier les sources dans `/Users/JOB/#AI/_Tools/sources/`.
5. Mettre a jour ce fichier Markdown.

## Verification attendue

- HTML valide
- onglets actifs et panneaux correspondants
- pas d'overflow horizontal mobile
- liens locaux en `200`
- version visible dans la page

## Ajout v3.1

Ajout d'un pack BDSM 18+ consensuel :

- onglet Erotique transforme en section `BDSM 18+ consensuel`
- prompt principal adulte/editorial
- negative prompt strict anti-mineur, anti-coercition, anti-violence reelle
- reglages ComfyUI SDXL
- variantes latex, cuir, shibari artistique, rouge rubedo
- fichier dedie : `/Users/JOB/#AI/_Tools/ai-station-m5/BDSM-18-consensuel-prompt-pack.md`

## Ajout v4.0

Refonte dashboard dev IA :

- ajout onglet `Agents Dev`
- affichage des agents detectes : Codex, Claude Code, Aider, Hermes, Continue
- affichage des agents manquants utiles : Cline, Goose, OpenHands, OpenCode, TabbyML
- synthese services, modeles Ollama, dossiers et commandes
- recommandation Hermes : installer `qwen2.5-coder:14b`
- backup de la version precedente : `AI-Station.v3.1.backup.html`

## Ajout v4.1

Synchronisation apres installation outils dev :

- installation Cline CLI
- installation Goose CLI
- installation OpenHands CLI
- installation OpenCode CLI
- installation modele Ollama `qwen2.5-coder:14b`
- configuration Hermes sur `qwen2.5-coder:14b`
- TabbyML conserve en option lourd serveur autocomplete
