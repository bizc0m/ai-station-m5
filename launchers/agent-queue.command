#!/bin/zsh
QUEUE="/Users/JOB/#DEV/_Agents/task-queue"
cd "${QUEUE}" || exit 1
/Users/JOB/#DEV/_Agents/task-queue/scripts/agent-queue init
open "/Users/JOB/#DEV/01-projets/Tools/ai-station-m5/Agent-Queue.html"
echo
echo "Commandes rapides:"
echo "  scripts/agent-queue add \"Titre\" --agent codex --project \"/Users/JOB/#DEV\" --priority 4"
echo "  scripts/agent-queue next --agent codex"
echo "  scripts/agent-queue start TASK-0001 --agent codex"
echo "  scripts/agent-queue done TASK-0001 --note \"Termine\""
echo
exec zsh
