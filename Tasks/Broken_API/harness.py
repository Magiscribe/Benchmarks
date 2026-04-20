"""
Harness for the Broken API task.

Commands:
    start    - copy app source to workspace, spin up the API container,
               stash eval/ outside the task tree, start clock
    score    - stop clock, restore eval/, run eval.py (HTTP traffic replay),
               print score + write last_result.json
    run      - start + invoke a named agent (blocks until CLI exits) +
               score + append leaderboard row
    cleanup  - tear down container, remove workspace,
               restore eval/ if it's still staged.

The agent is invoked with CWD = ./workspace. It signals completion by
creating ./workspace/.done (optionally JSON with identity metadata).
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TASK_DIR = Path(__file__).parent.resolve()
TASK_NAME = TASK_DIR.name
SETUP_DIR = TASK_DIR / "setup"
EVAL_DIR = TASK_DIR / "eval"
WORKSPACE = TASK_DIR / "workspace"

# Auto-load .env from the repo root (two levels up from this task dir).
_ENV_FILE = TASK_DIR.parent.parent / ".env"
if _ENV_FILE.is_file():
    with open(_ENV_FILE) as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            k, v = _line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

TASK_MD_SRC = TASK_DIR / "task.md"
TASK_MD_DST = WORKSPACE / "task.md"
STATE_FILE = TASK_DIR / ".harness_state.json"
RESULT_FILE = TASK_DIR / "last_result.json"
LEADERBOARD_FILE = TASK_DIR / "leaderboard.csv"
COMPOSE_FILE = SETUP_DIR / "docker-compose.yml"

API_CONTAINER = "benchmark-broken-api"
API_PORT = 8080
API_URL = f"http://localhost:{API_PORT}"

LEADERBOARD_COLUMNS = [
    "timestamp",
    "agent",
    "model",
    "score",
    "max_score",
    "elapsed_seconds",
    "done_flag",
    "self_report",
    "checks_passed",
    "checks_failed",
    "notes",
]


def log(msg):
    print(f"[harness] {msg}", flush=True)


def compose(*args, capture=False):
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), *args]
    if capture:
        return subprocess.run(cmd, cwd=str(SETUP_DIR), capture_output=True, text=True)
    return subprocess.run(cmd, cwd=str(SETUP_DIR))


def wait_for_api_healthy(timeout=60):
    """Poll the API health endpoint until it responds 200."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(f"{API_URL}/health")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_state():
    if not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text())


def stage_eval():
    """Move eval/ out of the task tree so the agent can't peek at it."""
    if not EVAL_DIR.exists():
        raise RuntimeError(
            f"eval dir not found at {EVAL_DIR}. If a prior run was interrupted, "
            "check `.harness_state.json` for `eval_staged_at` and restore manually."
        )
    staging_parent = Path(tempfile.mkdtemp(prefix=f"benchmark-eval-{TASK_NAME}-"))
    staged_eval = staging_parent / "eval"
    shutil.move(str(EVAL_DIR), str(staged_eval))
    return str(staged_eval)


def restore_eval(staged_path_str):
    """Move the staged eval/ back into the task tree."""
    if not staged_path_str:
        return
    staged = Path(staged_path_str)
    if not staged.exists():
        log(f"WARNING: staged eval missing at {staged}. eval/ will not be restored.")
        return
    if EVAL_DIR.exists():
        log(f"WARNING: {EVAL_DIR} already exists; removing staged copy at {staged}.")
        shutil.rmtree(staged.parent)
        return
    shutil.move(str(staged), str(EVAL_DIR))
    try:
        staged.parent.rmdir()
    except OSError:
        pass


def find_containers_on_port(port):
    r = subprocess.run(
        ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.Names}}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return []
    return [n for n in r.stdout.strip().splitlines() if n]


def sweep_port(port):
    names = find_containers_on_port(port)
    if not names:
        log(f"No containers bound to port {port} to sweep.")
        return
    log(f"Sweeping containers on port {port}: {', '.join(names)}")
    subprocess.run(["docker", "rm", "-f", *names], capture_output=True, text=True)


def parse_done(workspace):
    """Return (present, self_report_dict_or_None)."""
    done = workspace / ".done"
    if not done.exists():
        return False, None
    try:
        text = done.read_text().strip()
    except Exception:
        return True, None
    if not text:
        return True, None
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return True, data
        return True, {"raw": text}
    except json.JSONDecodeError:
        return True, {"raw": text}


def append_leaderboard_row(result, state):
    new_file = not LEADERBOARD_FILE.exists()
    checks = result.get("checks", [])
    passed = [c["name"] for c in checks if c.get("passed")]
    failed = [c["name"] for c in checks if not c.get("passed")]
    self_report = result.get("self_report") or {}
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agent": state.get("agent") or self_report.get("agent") or "unknown",
        "model": state.get("model") or self_report.get("model") or "unknown",
        "score": result.get("score"),
        "max_score": result.get("max_score"),
        "elapsed_seconds": f"{result.get('elapsed_seconds', 0):.1f}",
        "done_flag": result.get("done_flag"),
        "self_report": json.dumps(self_report) if self_report else "",
        "checks_passed": ",".join(passed),
        "checks_failed": ",".join(failed),
        "notes": self_report.get("notes", "") if isinstance(self_report, dict) else "",
    }
    with LEADERBOARD_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEADERBOARD_COLUMNS)
        if new_file:
            w.writeheader()
        w.writerow(row)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_start(args):
    if STATE_FILE.exists():
        log("Harness already started. Run `cleanup` first.")
        sys.exit(1)

    log("Preparing workspace...")
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    WORKSPACE.mkdir()

    # Copy app source into workspace (this is what the agent will edit)
    src_app = SETUP_DIR / "app"
    dst_app = WORKSPACE / "app"
    shutil.copytree(str(src_app), str(dst_app))

    # Copy task brief
    shutil.copy(TASK_MD_SRC, TASK_MD_DST)

    log("Clearing any prior compose state...")
    compose("down", "-v", capture=True)

    log("Building and starting API container...")
    r = compose("up", "-d", "--build")
    if r.returncode != 0:
        log("docker compose up failed.")
        sys.exit(1)

    log("Waiting for API to be healthy...")
    if not wait_for_api_healthy(timeout=60):
        log("API did not become healthy in time. Container logs:")
        compose("logs", "api")
        # Don't exit — the API might be crashing due to bugs, which is expected.
        # The agent's job is to fix those. Just warn.
        log("WARNING: API not healthy (expected — it has bugs). Continuing.")

    log("Staging eval/ outside the task tree...")
    staged = stage_eval()

    start_time = time.time()
    save_state({
        "start_time": start_time,
        "api_container": API_CONTAINER,
        "eval_staged_at": staged,
        "agent": getattr(args, "agent", None),
        "model": getattr(args, "model", None),
    })
    log(f"Ready. Workspace: {WORKSPACE}")
    log(f"Task brief: {TASK_MD_DST}")
    if getattr(args, "agent", None) or getattr(args, "model", None):
        log(f"Recorded identity: agent={args.agent or '?'} model={args.model or '?'}")
    log("Point your agent at the workspace directory. Score when done.")


def _score_core():
    """Shared logic for score. Returns (result_dict, state_dict)."""
    state = load_state()
    if state is None:
        log("Harness not started. Run `start` first.")
        sys.exit(1)

    elapsed = time.time() - state["start_time"]
    done_seen, self_report = parse_done(WORKSPACE)

    log(f"Elapsed: {elapsed:.1f}s")
    log(f".done present: {done_seen}")
    if self_report:
        log(f"Agent self-report: {json.dumps(self_report)}")

    log("Restoring eval/ for scoring...")
    restore_eval(state.get("eval_staged_at"))
    state["eval_staged_at"] = None
    save_state(state)

    log("Running eval...")
    r = subprocess.run(
        [sys.executable, str(EVAL_DIR / "eval.py")],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        log(f"Eval exited {r.returncode}")
        if r.stderr:
            sys.stderr.write(r.stderr)
        sys.exit(1)

    try:
        result = json.loads(r.stdout)
    except json.JSONDecodeError:
        log("Eval did not return valid JSON:")
        print(r.stdout)
        sys.exit(1)

    result["elapsed_seconds"] = elapsed
    result["done_flag"] = done_seen
    result["self_report"] = self_report
    result["agent"] = state.get("agent")
    result["model"] = state.get("model")
    RESULT_FILE.write_text(json.dumps(result, indent=2))
    return result, state


def _print_result(result, done_seen, elapsed):
    print()
    print("=" * 60)
    print(f"SCORE: {result['score']} / {result['max_score']}")
    print(f"TIME:  {elapsed:.1f}s")
    print(f"DONE:  {'yes' if done_seen else 'no (agent did not signal)'}")
    if result.get("agent") or result.get("model"):
        print(f"AGENT: {result.get('agent') or '?'} / {result.get('model') or '?'}")
    print("=" * 60)
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        line = f"  [{status}] {check['name']}"
        if not check["passed"]:
            if check.get("error"):
                err = " ".join(check["error"].split())
                if len(err) > 200:
                    err = err[:200] + "..."
                line += f"  - {err}"
            else:
                line += (f"  - expected {check.get('expected')}, "
                         f"got {check.get('actual')}")
        print(line)
    print()


def cmd_score(args):
    result, state = _score_core()
    _print_result(result, result["done_flag"], result["elapsed_seconds"])
    append_leaderboard_row(result, state)
    log(f"Full result: {RESULT_FILE}")
    log(f"Leaderboard: {LEADERBOARD_FILE}")


# ---------------------------------------------------------------------------
# Agent invocation (run command)
# ---------------------------------------------------------------------------

BOOTSTRAP_PROMPT = """Your current working directory contains:
- task.md — your full task brief
- app/ — the source code of a running FastAPI service (mounted into a Docker container with hot-reload)

Read task.md for complete instructions. In short: the API at http://localhost:8080 has bugs causing wrong responses. Fix them by editing files in app/. The server auto-reloads on save. When all bugs are fixed, create a .done file.
"""

# Agent CLI commands keyed by agent name.
# Each factory receives (prompt, model) where model may be None.
AGENT_COMMANDS = {
    "gemini": lambda prompt, model: ([
        "gemini", "--yolo",
        "-m", model or os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
        "-p", prompt,
    ], None),
    "claude": lambda prompt, model: ([
        "claude", "--dangerously-skip-permissions",
        "--model", model or os.environ.get("CLAUDE_MODEL", "sonnet"),
        "-p",
    ], prompt),
    "codex": lambda prompt, model: ([
        "codex", "exec",
        "-m", model or os.environ.get("CODEX_MODEL", "gpt-5.4"),
        "--dangerously-bypass-approvals-and-sandbox", "-",
    ], prompt),
}


def cmd_run(args):
    if STATE_FILE.exists():
        log("Harness already started. Run `cleanup` first.")
        sys.exit(1)

    agent = args.agent
    if agent not in AGENT_COMMANDS:
        log(f"Unknown agent '{agent}'. Available: {sorted(AGENT_COMMANDS.keys())}")
        sys.exit(1)

    # Start the environment
    start_args = argparse.Namespace(agent=args.agent, model=args.model)
    cmd_start(start_args)

    # Build the prompt and CLI command
    prompt = BOOTSTRAP_PROMPT.strip()
    cmd, stdin_input = AGENT_COMMANDS[agent](prompt, args.model)

    # Ensure agent-specific API key env vars are set.
    env = os.environ.copy()
    if agent == "gemini" and "GEMINI_API_KEY" not in env:
        gkey = env.get("GOOGLE_API_KEY")
        if gkey:
            env["GEMINI_API_KEY"] = gkey
            log("Set GEMINI_API_KEY from GOOGLE_API_KEY.")
        else:
            log("WARNING: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set.")

    timeout = getattr(args, "timeout", None)
    log(f"Invoking agent: {' '.join(cmd[:3])}...")
    if timeout:
        log(f"(Timeout: {timeout}s. Will score on expiry.)")
    log("(Blocking until the agent CLI exits. Hit Ctrl+C to abort.)")
    popen_kwargs = dict(
        cwd=str(WORKSPACE),
        env=env,
        shell=(sys.platform == "win32"),
    )
    if stdin_input:
        popen_kwargs["stdin"] = subprocess.PIPE
    try:
        proc = subprocess.Popen(cmd, **popen_kwargs)
        if stdin_input:
            proc.stdin.write(stdin_input.encode("utf-8"))
            proc.stdin.close()
        rc = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"Timeout of {timeout}s reached. Killing agent process...")
        proc.kill()
        proc.wait()
        rc = 124  # standard timeout exit code
    log(f"Runner exited with code {rc}")

    result, state = _score_core()
    _print_result(result, result["done_flag"], result["elapsed_seconds"])
    append_leaderboard_row(result, state)
    log(f"Full result: {RESULT_FILE}")
    log(f"Leaderboard row appended: {LEADERBOARD_FILE}")

    if args.auto_cleanup:
        log("Auto-cleanup enabled; tearing down.")
        cleanup_args = argparse.Namespace(sweep=True)
        cmd_cleanup(cleanup_args)


def cmd_cleanup(args):
    state = load_state()

    # If we staged eval but never scored, restore it now
    if state and state.get("eval_staged_at"):
        log("Restoring staged eval/ before cleanup...")
        restore_eval(state["eval_staged_at"])

    log("Stopping API container...")
    compose("down", "-v", capture=True)

    if args.sweep:
        log(f"Sweeping any containers on port {API_PORT} (--sweep)...")
        sweep_port(API_PORT)
    else:
        leftover = find_containers_on_port(API_PORT)
        if leftover:
            log(f"Containers still bound to port {API_PORT}: "
                f"{', '.join(leftover)} (pass --sweep to remove).")

    if WORKSPACE.exists():
        log("Removing workspace...")
        shutil.rmtree(WORKSPACE)
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    log("Done.")


def main():
    parser = argparse.ArgumentParser(
        description="Broken API task harness"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Start API and prepare workspace")
    p_start.add_argument("--agent", help="Agent identifier")
    p_start.add_argument("--model", help="Model identifier")

    sub.add_parser("score", help="Run eval and print score")

    p_run = sub.add_parser("run", help="start + invoke agent + score")
    p_run.add_argument("--agent", required=True,
                       help="Agent name (gemini, claude, codex)")
    p_run.add_argument("--model", help="Model identifier for the leaderboard")
    p_run.add_argument("--timeout", type=int, default=None, metavar="SECONDS",
                       help="Kill the agent and score after this many seconds")
    p_run.add_argument("--auto-cleanup", action="store_true",
                       help="Tear down after scoring (implies --sweep)")

    p_cleanup = sub.add_parser("cleanup",
                               help="Tear down container and workspace")
    p_cleanup.add_argument("--sweep", action="store_true",
                           help=f"Also remove containers on port {API_PORT}")

    args = parser.parse_args()
    {
        "start": cmd_start,
        "score": cmd_score,
        "run": cmd_run,
        "cleanup": cmd_cleanup,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
