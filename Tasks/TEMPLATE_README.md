# Creating a New Agent Task

Unlike the LLM-endpoint benchmarks in `Tests/`, tasks in `Tasks/` evaluate an
**agent + harness** combination. The harness pre-stages a Docker world, points
the agent at a workspace with a `task.md` brief, and after the agent signals
done it runs a private `eval.py` against the resulting world state.

All lifecycle logic lives in the shared `Harness/` module (peer to `Inference/`).
Each task's `harness.py` is a small declarative config — no subprocess,
Docker, or leaderboard logic in the task itself.

## Directory structure

```
Tasks/YourTaskName/
├── task.md                 # Agent-visible brief
├── setup/
│   ├── docker-compose.yml  # Initial-state container(s)
│   └── …                   # Dockerfile / seed.sql / source trees as needed
├── eval/
│   └── eval.py             # PRIVATE — scoring logic
├── harness.py              # ~20-line TaskSpec config
├── workspace/              # created at runtime; agent's CWD
└── README.md               # operator docs (not for the agent)
```

## `harness.py` contract

Tasks only declare a `TaskSpec` and hand it to `run_cli`. Example:

```python
import sys
from pathlib import Path

TASK_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(TASK_DIR.parent.parent))  # repo root → import Harness

from Harness import TaskSpec, HttpHealth, run_cli

SPEC = TaskSpec(
    name="YourTaskName",
    container_name="benchmark-your-task",
    port=8080,
    readiness=HttpHealth(url="http://localhost:8080/health"),
    workspace_copies=[("app", "app")],   # copy setup/app → workspace/app
    tolerate_unready=False,              # True if the world starts broken
    build=True,                          # docker compose up --build
    bootstrap_prompt=None,               # None → generic default
)

if __name__ == "__main__":
    run_cli(SPEC, task_dir=TASK_DIR)
```

### `TaskSpec` fields

| Field | Purpose |
|---|---|
| `name` | Task identifier (shown in logs, tempdir prefix) |
| `container_name` | Primary container for state tracking |
| `port` | Port used by the task (for `cleanup --sweep`) |
| `readiness` | `HttpHealth(url=…)` or `DockerHealth(container=…)` |
| `workspace_copies` | `[(src_rel_to_setup, dst_rel_to_workspace), …]`; `task.md` is copied automatically |
| `tolerate_unready` | If the initial world is expected to be broken (e.g. Broken_API), warn instead of abort when readiness fails |
| `build` | Use `docker compose up --build` if the compose file defines a build context |
| `bootstrap_prompt` | Override the generic "read task.md, do the work, create .done" prompt if the task needs extra hints |

## CLI surface (unchanged per task)

- `python harness.py start [--agent X --model Y]` — bring up the world, start the clock.
- `python harness.py score` — run eval, print + persist score.
- `python harness.py run --agent claude --model sonnet [--timeout N] [--auto-cleanup]`
  — start + invoke the agent CLI + score, all in one.
- `python harness.py cleanup [--sweep]` — tear down.

## Adding a new agent CLI

Edit `Harness/agents.py` once — add an entry to `AGENT_COMMANDS`. All tasks
get the new agent automatically.

## `task.md` guidelines

The agent only sees `task.md` and what it can discover by shell. Be explicit
about:

- Initial state: what's running, where, with what credentials.
- Terminal state: what makes this "done".
- Done signal: the `.done` file convention.
- Scoring rubric (at a summary level — not the exact queries).
- What the agent is and is not free to modify.

## What NOT to put in `task.md`

- The exact eval queries (those live in `eval/eval.py`).
- Implementation hints (the agent's approach is part of what you're testing).

## Hybrid initial state

Prefer the **hybrid** model: the harness starts the "source of truth" container
that the agent inherits (already running, seeded, at a fixed address). The
agent is responsible for spinning up anything new the task requires (e.g., the
target of a migration). This keeps the signal clean on the source side while
still testing infrastructure competence.

## `eval/eval.py` contract

Printed JSON on stdout:

```json
{
  "score": 4,
  "max_score": 5,
  "checks": [
    {"name": "…", "passed": true},
    {"name": "…", "passed": false, "expected": "…", "actual": "…", "error": "…"}
  ]
}
```

The harness reads this, merges in `elapsed_seconds` / `done_flag` /
`self_report` / `agent` / `model`, writes `last_result.json`, and appends a row
to `leaderboard.csv`.
