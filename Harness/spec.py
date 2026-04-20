"""Declarative task configuration for the agent-task harness."""
from dataclasses import dataclass, field
from typing import Union


@dataclass
class HttpHealth:
    url: str
    timeout_seconds: int = 60


@dataclass
class DockerHealth:
    container: str
    timeout_seconds: int = 180


ReadinessCheck = Union[HttpHealth, DockerHealth]


@dataclass
class TaskSpec:
    name: str
    container_name: str
    port: int
    readiness: ReadinessCheck
    workspace_copies: list = field(default_factory=list)
    tolerate_unready: bool = False
    build: bool = False
    bootstrap_prompt: str = None
