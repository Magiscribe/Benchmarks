"""Harness entry point for the MySQL_to_Postgres task.

All lifecycle logic lives in the shared Harness/ module. This file is pure
configuration.
"""
import sys
from pathlib import Path

TASK_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(TASK_DIR.parent.parent))  # repo root → import Harness

from Harness import DockerHealth, TaskSpec, run_cli  # noqa: E402


SPEC = TaskSpec(
    name="MySQL_to_Postgres",
    container_name="benchmark-mysql-legacy",
    port=5433,
    readiness=DockerHealth(container="benchmark-mysql-legacy", timeout_seconds=180),
)


if __name__ == "__main__":
    run_cli(SPEC, task_dir=TASK_DIR)
