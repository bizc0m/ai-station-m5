#!/bin/zsh
cd "/Users/JOB/#DEV" || exit 1
exec /Users/JOB/.local/bin/aider --model ollama/qwen2.5-coder:14b
