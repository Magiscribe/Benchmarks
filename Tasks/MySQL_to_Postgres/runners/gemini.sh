#!/usr/bin/env bash
# Runner for Gemini CLI. CWD is set by harness.py to ./workspace/.
# NOTE: Gemini CLI flag names have shifted across versions; verify locally.
# If this doesn't run headlessly, edit the command below.
set -u

PROMPT="$(cat "$(dirname "$0")/bootstrap_prompt.txt")"

# -p / --prompt: run non-interactively, act on the given prompt, exit.
# --yolo (or --auto-approve depending on version): approve tool calls.
gemini --yolo -p "$PROMPT"
