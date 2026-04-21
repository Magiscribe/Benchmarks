# Broken API (Agent Task)

An agent task where the agent debugs a broken FastAPI service. Unlike the
LLM-endpoint benchmarks in `Tests/`, the unit of evaluation here is an
**agent + harness combination**. The harness spins up a Docker container with
a seeded SQLite-backed FastAPI app, isolates the scoring logic, and points
the agent at a workspace with a `task.md` brief. After the agent signals
done by creating `.done`, the harness runs a private `eval.py` to score it.

## Layout

```
Tasks/Broken_API/
├── task.md                 # Agent-visible brief (deliberately minimal)
├── setup/
│   ├── docker-compose.yml  # FastAPI container definition
│   ├── Dockerfile
│   └── app/                # The buggy source code (copied to workspace/)
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       └── routes/
│           ├── products.py
│           ├── orders.py
│           └── users.py
├── eval/
│   ├── eval.py             # PRIVATE — scoring logic
│   └── traffic.json        # PRIVATE — expected HTTP responses
├── harness.py              # start / score / run / cleanup CLI
├── workspace/              # created at runtime; the agent's CWD
└── leaderboard.csv         # appended once per scored run
```

## What the agent sees vs. doesn't

- **Sees:** `workspace/task.md`, a running API at `localhost:8080` (with
  hot-reload), and `workspace/app/` — the full source code to edit.
- **Does not see:** `eval/eval.py` and `eval/traffic.json` — the harness
  moves them to a temp dir outside the task tree during the agent's run.

## The bugs (SPOILERS)

There are 5 intentional bugs planted in `setup/app/routes/`:

1. **`products.py` — unpaginated listing:** `LEFT JOIN order_items` causes
   duplicate rows for products that appear in multiple orders.
2. **`products.py` — paginated listing:** `ORDER BY price ASC` instead of
   `ORDER BY id` returns wrong products for a given page offset.
3. **`orders.py` — status filter:** `status.strip().lower()[:8]` truncates
   `"completed"` → `"complete"`, matching no rows.
4. **`orders.py` — order total:** `int(total * 100) / 100` truncates instead
   of rounding, producing `34.33` instead of `34.34`.
5. **`users.py` — user orders:** `JOIN order_items ON oi.order_id = o.id`
   duplicates orders that have multiple line items.

## Operator workflow

One-time install:

```bash
pip install -r ../../requirements.txt
```

### One-command runs (recommended)

```bash
# Claude
python harness.py run --agent claude --model claude-opus-4-7

# Gemini
python harness.py run --agent gemini --model gemini-3.1-pro

# Codex
python harness.py run --agent codex --model gpt-5.4

# With timeout (kills agent after N seconds and scores partial result):
python harness.py run --agent claude --model claude-opus-4-7 --timeout 300

# Tear down automatically after scoring:
python harness.py run --agent claude --model claude-opus-4-7 --auto-cleanup
```

`run` does: `start` → invoke agent CLI (blocking) → `score` → append row to
`leaderboard.csv`.

### Manual runs

```bash
# 1. Stage the environment
python harness.py start --agent claude --model claude-opus-4-7

# 2. Run the agent yourself with CWD = ./workspace
cd workspace
claude --dangerously-skip-permissions

# 3. Score after agent exits
cd ..
python harness.py score

# 4. Tear down
python harness.py cleanup --sweep
```

## Scoring

Five binary checks, one point each:

| Check | What it tests |
|---|---|
| `products_list` | `GET /products` returns all 8 products (no duplicates) |
| `orders_completed` | `GET /orders?status=completed` returns 3 orders |
| `user_orders` | `GET /users/2/orders` returns 3 orders (no duplicates) |
| `products_paginated` | `GET /products?page=2&per_page=3` returns IDs `[4, 5, 6]` |
| `order_total` | `POST /orders` with known items returns `total = 34.34` |

Wall time from `start` to agent exit is also recorded.

## Leaderboard

`leaderboard.csv` is appended by every scored run. Columns:

```
timestamp, agent, model, score, max_score, elapsed_seconds,
done_flag, self_report, checks_passed, checks_failed, notes
```

## Caveats

- **Isolation is best-effort.** The staged `eval/` lives in an OS temp dir;
  a sufficiently motivated agent could still find it. Full enforcement is V2
  (sidecar eval container).
- Port `8080` must be free on the host. Pass `--sweep` to cleanup to forcibly
  remove any containers occupying it.
