"""Harness entry point for the Broken_API task.

All lifecycle logic lives in the shared Harness/ module. This file is pure
configuration.
"""
import sys
from pathlib import Path

TASK_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(TASK_DIR.parent.parent))  # repo root → import Harness

from Harness import HttpHealth, TaskSpec, run_cli  # noqa: E402


BOOTSTRAP_PROMPT = """Your current working directory contains:
- task.md — your full task brief
- app/ — the source code of a running FastAPI service (mounted into a Docker container with hot-reload)

Read task.md for complete instructions. In short: the API at http://localhost:8080 has bugs causing wrong responses. Fix them by editing files in app/. The server auto-reloads on save. When all bugs are fixed, create a .done file.
"""


SPEC = TaskSpec(
    name="Broken_API",
    container_name="benchmark-broken-api",
    port=8080,
    readiness=HttpHealth(url="http://localhost:8080/health", timeout_seconds=60),
    workspace_copies=[("app", "app")],
    tolerate_unready=True,
    build=True,
    bootstrap_prompt=BOOTSTRAP_PROMPT,
)


if __name__ == "__main__":
    run_cli(SPEC, task_dir=TASK_DIR)
