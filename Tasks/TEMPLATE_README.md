# Creating a New Agent Task

Unlike the LLM-endpoint benchmarks in `Tests/`, tasks in `Tasks/` evaluate an
**agent + harness** combination. The harness pre-stages a Docker world, points
the agent at a workspace with a `task.md` brief, and after the agent signals
done it runs a private `eval.py` against the resulting world state.

## Directory structure

```
Tasks/YourTaskName/
├── task.md                 # Agent-visible brief
├── setup/
│   ├── docker-compose.yml  # Initial-state container(s)
│   └── seed.sql            # (or equivalent) initial data
├── eval/
│   └── eval.py             # PRIVATE — scoring logic
├── harness.py              # start / score / cleanup CLI
├── workspace/              # created at runtime; agent's CWD
└── README.md               # operator docs (not for the agent)
```

## The contract

- `python harness.py start` — bring up the initial world, copy `task.md` into
  `workspace/`, start the clock.
- Orchestrator runs the agent (Claude Code, Codex, Gemini CLI, …) with
  `./workspace/` as CWD.
- Agent does work, then creates `./workspace/.done` (empty file) to signal
  completion.
- `python harness.py score` — stop clock, run `eval.py`, print score + time.
- `python harness.py cleanup` — tear down containers the harness started,
  remove workspace.

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
