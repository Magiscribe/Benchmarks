# MySQL → Postgres Migration (Agent Task)

A proof-of-concept **agent task**: unlike the LLM-endpoint benchmarks in
`Tests/`, the unit of evaluation here is an **agent + harness combination**.
The harness stages a Docker world (a seeded MySQL container), isolates the
scoring logic, points the agent at a workspace with a `task.md`, and after
the agent signals done it runs a private `eval.py` to score the result.

## Layout

- `task.md` — agent-visible brief (copied into `workspace/` on start)
- `setup/docker-compose.yml` — defines the initial MySQL container
- `setup/seed.sql` — schema + seed data (runs on first boot via init-dir)
- `eval/eval.py` — **private** scoring script. Moved out of the task tree
  while the agent is running and restored for scoring.
- `runners/*.sh` — per-agent launch scripts (Claude Code, Gemini, Codex)
- `runners/bootstrap_prompt.txt` — the uniform prompt handed to every agent
- `harness.py` — `start` / `score` / `run` / `cleanup` CLI
- `workspace/` — created at runtime; the agent's CWD
- `leaderboard.csv` — appended once per scored run

## What the agent sees vs. doesn't

- Sees: `workspace/task.md`, a running MySQL at `localhost:3306`, an empty
  workspace it can write to.
- Does not see: `eval/eval.py` — the harness moves it to a temp directory
  outside the task tree during the agent's run. `../eval/` from the
  workspace simply doesn't exist until `score` restores it.
- Does see (acceptable): `setup/seed.sql`. The agent can already read the
  same data via `mysql` queries; the seed file leaks no extra signal.

## Operator workflow

One-time install:

```bash
pip install -r ../../requirements.txt
```

### One-command runs (recommended)

```bash
# Claude Code
python harness.py run --agent claude --model claude-opus-4-7

# Gemini CLI
python harness.py run --agent gemini --model gemini-2.5-pro

# Codex CLI
python harness.py run --agent codex --model gpt-5.1-codex

# Add --auto-cleanup to tear everything down after scoring:
python harness.py run --agent claude --model claude-opus-4-7 --auto-cleanup
```

`run` does: `start` → invoke `runners/<agent>.sh` (blocking) → `score` →
append a row to `leaderboard.csv`.

### Manual runs (e.g., debugging an agent interactively)

```bash
# 1. Stage the world and record identity
python harness.py start --agent claude-code --model claude-opus-4-7

# 2. Run the agent yourself, CWD must be ./workspace
cd workspace
claude --dangerously-skip-permissions   # or: gemini, or: codex

# 3. After the agent exits (having touched .done), go back up and score
cd ..
python harness.py score

# 4. Tear down
python harness.py cleanup --sweep   # --sweep also kills agent-spun Postgres
```

## Runner scripts

Each script in `runners/` is ~10 lines: `cd workspace` is handled by the
harness, the script just invokes the CLI with non-interactive flags and
feeds it `runners/bootstrap_prompt.txt`. The bootstrap prompt is
**deliberately minimal** — every agent gets the same seed, and the test
is whether the agent can read `task.md` and execute it.

Flag names shift across CLI versions. If a runner doesn't launch
headlessly, edit the script — all three are meant to be tweaked.

## Scoring

Five binary checks, one point each:

1. `user_count` — row count in `users` matches
2. `specific_user` — a named user is recoverable by email
3. `user_join` — JOIN across `users` ↔ `orders` returns the expected count
4. `completed_total` — `SUM(total)` with a status filter agrees (tolerance 0.01)
5. `mysql_down` — original MySQL port is unreachable

Wall time from `start` to `score` is also captured in `last_result.json`
and `leaderboard.csv`.

## Leaderboard

`leaderboard.csv` is appended by every `score` (or `run`). Columns:

```
timestamp, agent, model, score, max_score, elapsed_seconds,
done_flag, self_report, checks_passed, checks_failed, notes
```

`agent` and `model` come from the operator-provided flags; if the agent
also self-reported via a JSON `.done` manifest, that's stored in
`self_report` for cross-check.

## Caveats

- **Isolation is best-effort, not enforced.** The staged `eval/` lives in
  an OS temp dir outside the task tree; a sufficiently motivated agent
  could still find it. `task.md` explicitly tells the agent to stay in
  the workspace. Full enforcement is V2 (sidecar eval container).
- **Agent-spun containers** survive `cleanup` unless you pass `--sweep`,
  which removes anything bound to port `5433`. The built-in MySQL
  container is always cleaned up via compose.
- Ports `3306` and `5433` must be free on the host.
