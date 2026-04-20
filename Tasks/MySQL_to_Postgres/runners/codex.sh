#!/usr/bin/env bash
# Runner for OpenAI Codex CLI. CWD is set by harness.py to ./workspace/.
# NOTE: Codex flag names shift; verify locally and edit if needed.
set -u

# RUNNERS_DIR is set by harness.py; fall back to dirname $0 for manual runs.
RUNNERS_DIR="${RUNNERS_DIR:-$(dirname "$0")}"
PROMPT="$(cat "$RUNNERS_DIR/bootstrap_prompt.txt")"

# `codex exec` runs a single non-interactive session with the given prompt.
# --dangerously-bypass-approvals-and-sandbox (or --full-auto depending on
# version): approve tool calls automatically.
codex exec --dangerously-bypass-approvals-and-sandbox "$PROMPT"
