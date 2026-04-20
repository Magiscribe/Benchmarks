#!/usr/bin/env bash
# Runner for Gemini CLI. CWD is set by harness.py to ./workspace/.
# NOTE: Gemini CLI flag names have shifted across versions; verify locally.
# If this doesn't run headlessly, edit the command below.
set -u

# RUNNERS_DIR is set by harness.py; fall back to dirname $0 for manual runs.
RUNNERS_DIR="${RUNNERS_DIR:-$(dirname "$0")}"
PROMPT="$(cat "$RUNNERS_DIR/bootstrap_prompt.txt")"

# -p / --prompt: run non-interactively, act on the given prompt, exit.
# --yolo (or --auto-approve depending on version): approve tool calls.
gemini --yolo -m "${GEMINI_MODEL:-gemini-3-flash-preview}" -p "$PROMPT"
