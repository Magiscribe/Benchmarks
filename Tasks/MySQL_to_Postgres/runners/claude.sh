#!/usr/bin/env bash
# Runner for Claude Code. CWD is set by harness.py to ./workspace/.
# Non-interactive / "print" mode: runs the agent end-to-end and exits.
set -u

# RUNNERS_DIR is set by harness.py; fall back to dirname $0 for manual runs.
RUNNERS_DIR="${RUNNERS_DIR:-$(dirname "$0")}"
PROMPT="$(cat "$RUNNERS_DIR/bootstrap_prompt.txt")"

# --dangerously-skip-permissions: auto-approve tool calls (the benchmark run)
# -p / --print: non-interactive; run until done and exit
claude --dangerously-skip-permissions -p "$PROMPT"
