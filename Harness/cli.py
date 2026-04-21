"""argparse wiring for task harnesses. Called from each Tasks/*/harness.py."""
import argparse
from pathlib import Path

from . import agents
from .env import load_dotenv
from .runner import cmd_cleanup, cmd_run, cmd_score, cmd_start
from .spec import TaskSpec


def run_cli(spec: TaskSpec, task_dir: Path):
    load_dotenv()

    parser = argparse.ArgumentParser(description=f"{spec.name} task harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Bring up the world and prepare workspace")
    p_start.add_argument("--agent", help="Agent identifier (recorded for leaderboard)")
    p_start.add_argument("--model", help="Model identifier (recorded for leaderboard)")

    sub.add_parser("score", help="Run eval and print score")

    p_run = sub.add_parser("run", help="start + invoke agent + score")
    p_run.add_argument("--agent", required=True,
                       help=f"Agent name. Available: {', '.join(agents.available_agents())}")
    p_run.add_argument("--model", help="Model identifier (passed to agent + recorded)")
    p_run.add_argument("--timeout", type=int, default=None, metavar="SECONDS",
                       help="Kill the agent and score after this many seconds")
    p_run.add_argument("--auto-cleanup", action="store_true",
                       help="Tear down after scoring (implies --sweep)")

    p_cleanup = sub.add_parser("cleanup", help="Tear down container(s) and workspace")
    p_cleanup.add_argument("--sweep", action="store_true",
                           help=f"Also remove containers on port {spec.port}")

    args = parser.parse_args()
    dispatch = {
        "start": cmd_start,
        "score": cmd_score,
        "run": cmd_run,
        "cleanup": cmd_cleanup,
    }
    dispatch[args.cmd](spec, task_dir, args)
