#!/bin/zsh
cd "/Users/JOB/#DEV" || exit 1
exec /Users/JOB/.local/bin/hermes --ignore-rules -t terminal -m qwen2.5-coder:14b
