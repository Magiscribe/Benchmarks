"""Docker Compose, health probing, and port sweeping helpers."""
import subprocess
import time
import urllib.request
from pathlib import Path

from .spec import DockerHealth, HttpHealth, ReadinessCheck


def compose(compose_file: Path, *args, capture=False):
    cmd = ["docker", "compose", "-f", str(compose_file), *args]
    cwd = str(compose_file.parent)
    if capture:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return subprocess.run(cmd, cwd=cwd)


def find_containers_on_port(port: int):
    r = subprocess.run(
        ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.Names}}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return []
    return [n for n in r.stdout.strip().splitlines() if n]


def sweep_port(port: int, log):
    names = find_containers_on_port(port)
    if not names:
        log(f"No containers bound to port {port} to sweep.")
        return
    log(f"Sweeping containers on port {port}: {', '.join(names)}")
    subprocess.run(["docker", "rm", "-f", *names], capture_output=True, text=True)


def _wait_http(url: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def _wait_docker_health(container: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "inspect", "-f",
             "{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}",
             container],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and r.stdout.strip() == "healthy":
            return True
        time.sleep(2)
    return False


def wait_for_ready(check: ReadinessCheck) -> bool:
    if isinstance(check, HttpHealth):
        return _wait_http(check.url, check.timeout_seconds)
    if isinstance(check, DockerHealth):
        return _wait_docker_health(check.container, check.timeout_seconds)
    raise TypeError(f"Unknown readiness check type: {type(check)!r}")
