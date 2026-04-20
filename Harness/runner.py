"""Task lifecycle: start / score / run / cleanup.

All commands take (spec, task_dir, args). This module owns every file path
derived from task_dir — tasks themselves never compute these.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import agents
from .docker_utils import (
    compose,
    find_containers_on_port,
    sweep_port,
    wait_for_ready,
)
from .eval_staging import restore_eval, stage_eval
from .leaderboard import append_leaderboard_row
from .spec import TaskSpec
from .state import load_state, parse_done, save_state


def _paths(task_dir: Path):
    return {
        "setup": task_dir / "setup",
        "eval": task_dir / "eval",
        "workspace": task_dir / "workspace",
        "task_md_src": task_dir / "task.md",
        "state_file": task_dir / ".harness_state.json",
        "result_file": task_dir / "last_result.json",
        "leaderboard_file": task_dir / "leaderboard.csv",
        "compose_file": task_dir / "setup" / "docker-compose.yml",
    }


def _make_log(spec: TaskSpec):
    def log(msg):
        print(f"[harness] {msg}", flush=True)
    return log


def cmd_start(spec: TaskSpec, task_dir: Path, args):
    p = _paths(task_dir)
    log = _make_log(spec)

    if p["state_file"].exists():
        log("Harness already started. Run `cleanup` first.")
        sys.exit(1)

    log("Preparing workspace...")
    if p["workspace"].exists():
        shutil.rmtree(p["workspace"])
    p["workspace"].mkdir()

    for src_rel, dst_rel in spec.workspace_copies:
        src = p["setup"] / src_rel
        dst = p["workspace"] / dst_rel
        if src.is_dir():
            shutil.copytree(str(src), str(dst))
        else:
            shutil.copy(str(src), str(dst))

    shutil.copy(p["task_md_src"], p["workspace"] / "task.md")

    log("Clearing any prior compose state...")
    compose(p["compose_file"], "down", "-v", capture=True)

    up_args = ["up", "-d"]
    if spec.build:
        up_args.append("--build")
    log(f"Starting {spec.container_name}...")
    r = compose(p["compose_file"], *up_args)
    if r.returncode != 0:
        log("docker compose up failed.")
        sys.exit(1)

    log("Waiting for readiness...")
    ready = wait_for_ready(spec.readiness)
    if not ready:
        if spec.tolerate_unready:
            log("WARNING: not healthy (expected — task world may start broken). Continuing.")
        else:
            log("Service did not become ready in time. Container logs:")
            compose(p["compose_file"], "logs")
            sys.exit(1)

    log("Staging eval/ outside the task tree...")
    staged = stage_eval(p["eval"], spec.name)

    start_time = time.time()
    save_state(p["state_file"], {
        "start_time": start_time,
        "container_name": spec.container_name,
        "eval_staged_at": staged,
        "agent": getattr(args, "agent", None),
        "model": getattr(args, "model", None),
    })
    log(f"Ready. Workspace: {p['workspace']}")
    log(f"Task brief: {p['workspace'] / 'task.md'}")
    if getattr(args, "agent", None) or getattr(args, "model", None):
        log(f"Recorded identity: agent={args.agent or '?'} model={args.model or '?'}")
    log("Point your agent at the workspace directory. Score when done.")


def _score_core(spec: TaskSpec, task_dir: Path):
    p = _paths(task_dir)
    log = _make_log(spec)

    state = load_state(p["state_file"])
    if state is None:
        log("Harness not started. Run `start` first.")
        sys.exit(1)

    elapsed = time.time() - state["start_time"]
    done_seen, self_report = parse_done(p["workspace"])

    log(f"Elapsed: {elapsed:.1f}s")
    log(f".done present: {done_seen}")
    if self_report:
        log(f"Agent self-report: {json.dumps(self_report)}")

    log("Restoring eval/ for scoring...")
    restore_eval(p["eval"], state.get("eval_staged_at"), log)
    state["eval_staged_at"] = None
    save_state(p["state_file"], state)

    log("Running eval...")
    r = subprocess.run(
        [sys.executable, str(p["eval"] / "eval.py")],
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
    p["result_file"].write_text(json.dumps(result, indent=2))
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


def cmd_score(spec: TaskSpec, task_dir: Path, args):
    p = _paths(task_dir)
    log = _make_log(spec)
    result, state = _score_core(spec, task_dir)
    _print_result(result, result["done_flag"], result["elapsed_seconds"])
    append_leaderboard_row(p["leaderboard_file"], result, state)
    log(f"Full result: {p['result_file']}")
    log(f"Leaderboard: {p['leaderboard_file']}")


def cmd_run(spec: TaskSpec, task_dir: Path, args):
    p = _paths(task_dir)
    log = _make_log(spec)

    if p["state_file"].exists():
        log("Harness already started. Run `cleanup` first.")
        sys.exit(1)

    agent = args.agent
    if agent not in agents.AGENT_COMMANDS:
        log(f"Unknown agent '{agent}'. Available: {agents.available_agents()}")
        sys.exit(1)

    cmd_start(spec, task_dir, args)

    prompt = (spec.bootstrap_prompt or agents.DEFAULT_BOOTSTRAP_PROMPT).strip()
    rc = agents.invoke_agent(
        agent=agent,
        model=args.model,
        prompt=prompt,
        cwd=str(p["workspace"]),
        timeout=getattr(args, "timeout", None),
        log=log,
    )
    log(f"Runner exited with code {rc}")

    result, state = _score_core(spec, task_dir)
    _print_result(result, result["done_flag"], result["elapsed_seconds"])
    append_leaderboard_row(p["leaderboard_file"], result, state)
    log(f"Full result: {p['result_file']}")
    log(f"Leaderboard row appended: {p['leaderboard_file']}")

    if args.auto_cleanup:
        log("Auto-cleanup enabled; tearing down.")
        cmd_cleanup(spec, task_dir, argparse.Namespace(sweep=True))


def cmd_cleanup(spec: TaskSpec, task_dir: Path, args):
    p = _paths(task_dir)
    log = _make_log(spec)

    state = load_state(p["state_file"])
    if state and state.get("eval_staged_at"):
        log("Restoring staged eval/ before cleanup...")
        restore_eval(p["eval"], state["eval_staged_at"], log)

    log("Stopping container(s)...")
    compose(p["compose_file"], "down", "-v", capture=True)

    if args.sweep:
        log(f"Sweeping any containers on port {spec.port} (--sweep)...")
        sweep_port(spec.port, log)
    else:
        leftover = find_containers_on_port(spec.port)
        if leftover:
            log(f"Containers still bound to port {spec.port}: "
                f"{', '.join(leftover)} (pass --sweep to remove).")

    if p["workspace"].exists():
        log("Removing workspace...")
        shutil.rmtree(p["workspace"])
    if p["state_file"].exists():
        p["state_file"].unlink()
    log("Done.")
