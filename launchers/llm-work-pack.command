#!/bin/zsh
set -euo pipefail

cd "/Users/JOB/#DEV/01-projets/Tools/ai-station-m5"

echo "LLM Work Pack"
echo "Repo: $(pwd)"
echo

printf "Agent/CLI (codex, claude, opencode, aider, hermes): "
read agent
printf "Chemin source fichier/dossier: "
read source_path
printf "Titre court: "
read title
printf "Deplacer vraiment ? (no par defaut, yes pour move): "
read move_answer

args=(--agent "$agent" --source "$source_path" --title "$title")
if [[ "$move_answer" == "yes" || "$move_answer" == "y" || "$move_answer" == "oui" ]]; then
  args+=(--move)
fi

scripts/llm-work-pack.sh "${args[@]}"

echo
echo "Termine. Appuie sur Entree pour fermer."
read _
