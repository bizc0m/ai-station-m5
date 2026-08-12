#!/bin/zsh
PROMPT_FILE="/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/prompt-master-systematique.txt"
HTML_FILE="/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/Prompt-Master.html"

clear
echo "Prompt Master"
echo "${PROMPT_FILE}"
echo
open "${HTML_FILE}"
exec less -R "${PROMPT_FILE}"
