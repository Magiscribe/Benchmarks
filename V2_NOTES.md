# V2 Notes — Agent Task Framework

Parking lot for ideas deferred from the V1 proof of concept
(`Tasks/MySQL_to_Postgres/`). V1 is deliberately minimal — just enough to run a
real agent end-to-end against a real container and get a score. Everything
below is an "if this becomes a thing, here's what to fix" note.

## Isolation & locking

- **Lock state for scoring**: once the agent signals `.done`, freeze the world
  before eval runs. Right now nothing stops the agent from continuing to touch
  Postgres while eval is scoring it. `docker pause` or `docker commit` + spin
  up a clean scoring copy.
- **Sidecar eval container**: move `eval/eval.py` into its own container that
  talks to the agent's Postgres over the network. Enforces the privacy
  convention at the filesystem level instead of by polite convention
  ("agents shouldn't peek at `../eval/`").
- **Multi-container initial state**: V1 locks to one seed container. V2 could
  declare N (microservice + DB + message queue, etc.).
- **Container registry / canonical base images**: tasks currently ship their
  own image choice. A shared registry could reduce task boilerplate and pin
  versions so `mysql:8` doesn't drift between tasks.

## Harness-agnosticism & orchestration

- **Unified agent invoker**: a thin wrapper that knows how to launch Claude
  Code, Codex, Gemini CLI with the right non-interactive flags (auto-accept
  permissions, feed in `task.md`, detect exit), so `harness.py` can go
  end-to-end without a human driving each step.
- **Agent-spun cleanup**: `harness.py cleanup` only stops containers the
  harness started. If the agent spins up a Postgres container with an
  arbitrary name, the operator has to sweep `docker ps` manually between
  runs. V2 could run the agent inside a docker-in-docker context we fully
  control, so anything it creates is cleaned with the outer container.
- **Budgets**: no max turns / max wall time right now. V2 should let a task
  declare a budget and fail the run if exceeded.

## Telemetry

- **Cost & tokens**: inferred today from wall time + public pricing. Per-harness
  session logs (`~/.claude/projects/...`, Codex logs, Gemini CLI logs) could be
  parsed and normalized.
- **Turn count**: same story — per-harness log parsing.
- **Per-check timing**: eval records total elapsed, not time per check.

## Scoring

- **Weighted checks**: V1 has 5 checks × 1 point. Some checks (e.g., MySQL-
  down) probably matter more than others (e.g., one user row's name).
- **Partial credit inside a check**: "migrated 4 of 5 users" currently fails
  `user_count` binary. V2 could score gracefully.
- **Must-pass vs. nice-to-pass**: distinguish acceptance checks from optional
  ones.

## Task-definition ergonomics

- **Parameterized `task.md`**: render from `task_config.py` so ports,
  credentials, and seed counts live in one place instead of being duplicated
  between `task.md` and `docker-compose.yml`.
- **Difficulty tiers**: same underlying world with progressively sparser
  `task.md` — test how much the agent can infer vs. how much it needs spelled
  out.
