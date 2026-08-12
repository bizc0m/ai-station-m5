#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/llm-work-pack.sh --agent <nom> --source <chemin> --title <titre> [--move] [--commit]

Exemples:
  scripts/llm-work-pack.sh --agent claude --source /Users/JOB/Downloads/resultat --title "audit ai station"
  scripts/llm-work-pack.sh --agent opencode --source ./tmp/llm-output --title "bugfix launch" --move
  scripts/llm-work-pack.sh --agent codex --source ./files-nav.html --title "navigation fichiers" --commit

Effet:
  - cree llm-work/<agent>/<YYYYMMDD-HHMMSS>-<titre>/
  - copie par defaut le fichier/dossier source dans incoming/
  - --move deplace la source au lieu de copier
  - cree README.md + MANIFEST.txt
  - fait git add du dossier cree
  - --commit cree un commit local
USAGE
}

die() {
  echo "ERREUR: $*" >&2
  exit 1
}

slugify() {
  printf "%s" "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | iconv -f UTF-8 -t ASCII//TRANSLIT 2>/dev/null \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' \
    | cut -c1-60
}

agent=""
source_path=""
title=""
mode="copy"
commit="no"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      agent="${2:-}"
      shift 2
      ;;
    --source)
      source_path="${2:-}"
      shift 2
      ;;
    --title)
      title="${2:-}"
      shift 2
      ;;
    --move)
      mode="move"
      shift
      ;;
    --commit)
      commit="yes"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "option inconnue: $1"
      ;;
  esac
done

[[ -n "$agent" ]] || die "--agent manquant"
[[ -n "$source_path" ]] || die "--source manquant"
[[ -n "$title" ]] || die "--title manquant"
[[ -e "$source_path" ]] || die "source introuvable: $source_path"

git_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "pas dans un depot Git"
cd "$git_root"

agent_slug="$(slugify "$agent")"
title_slug="$(slugify "$title")"
[[ -n "$agent_slug" ]] || die "agent invalide"
[[ -n "$title_slug" ]] || title_slug="travail-llm"

stamp="$(date +%Y%m%d-%H%M%S)"
dest_dir="llm-work/${agent_slug}/${stamp}-${title_slug}"
incoming_dir="${dest_dir}/incoming"
mkdir -p "$incoming_dir"

base_name="$(basename "$source_path")"
target="${incoming_dir}/${base_name}"

if [[ "$mode" == "move" ]]; then
  mv "$source_path" "$target"
else
  cp -R "$source_path" "$target"
fi

{
  echo "# LLM Work - ${title}"
  echo
  echo "- Date: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "- Agent/CLI: ${agent}"
  echo "- Mode: ${mode}"
  echo "- Source: ${source_path}"
  echo "- Dossier Git: ${dest_dir}"
  echo
  echo "## Contenu"
  echo
  echo "- incoming/${base_name}"
  echo
  echo "## Suite"
  echo
  echo "- [ ] Verifier le contenu"
  echo "- [ ] Integrer ce qui est utile"
  echo "- [ ] Supprimer ou archiver le reste"
} > "${dest_dir}/README.md"

find "$dest_dir" -maxdepth 3 -type f | sort > "${dest_dir}/MANIFEST.txt"

git add "$dest_dir"

if [[ "$commit" == "yes" ]]; then
  git commit -m "llm-work: add ${agent_slug} ${title_slug}"
fi

echo "OK: ${dest_dir}"
echo "Git: dossier ajoute a l'index"
if [[ "$commit" == "no" ]]; then
  echo "Commit: non cree (--commit absent)"
fi

