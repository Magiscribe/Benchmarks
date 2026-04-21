"""Shared agent-task harness.

Each task's harness.py is a one-liner:

    from Harness import TaskSpec, HttpHealth, run_cli
    run_cli(TaskSpec(...), task_dir=Path(__file__).parent)
"""
from .cli import run_cli
from .spec import DockerHealth, HttpHealth, ReadinessCheck, TaskSpec

__all__ = ["TaskSpec", "HttpHealth", "DockerHealth", "ReadinessCheck", "run_cli"]
