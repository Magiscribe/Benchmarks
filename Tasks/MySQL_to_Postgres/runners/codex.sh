#!/usr/bin/env bash
# Runner for OpenAI Codex CLI. CWD is set by harness.py to ./workspace/.
# NOTE: Codex flag names shift; verify locally and edit if needed.
set -u

PROMPT="$(cat "$(dirname "$0")/bootstrap_prompt.txt")"

# `codex exec` runs a single non-interactive session with the given prompt.
# --dangerously-bypass-approvals-and-sandbox (or --full-auto depending on
# version): approve tool calls automatically.
codex exec --dangerously-bypass-approvals-and-sandbox "$PROMPT"
