# Task: Migrate a MySQL Database to Postgres

## Objective

Migrate all data from a running MySQL database into a new Postgres database
you stand up yourself. When you are done, the Postgres database must contain
the same data as the original MySQL database, and the original MySQL database
must be shut down and unreachable.

## Environment

You have full shell access on the host and can install any tools you need.
Docker is available.

### Source: MySQL (already running)

A MySQL 8 container is running on the host, seeded with a small e-commerce
schema (a handful of tables with foreign key relationships between them).

- Host: `localhost` (also reachable as `127.0.0.1`)
- Port: `3306`
- User: `root`
- Password: `rootpass`
- Database: `legacy`

Use standard MySQL tooling to inspect the schema and data. For example:

```
mysql -h 127.0.0.1 -P 3306 -u root -prootpass legacy -e "SHOW TABLES;"
mysql -h 127.0.0.1 -P 3306 -u root -prootpass legacy -e "DESCRIBE users;"
```

### Target: Postgres (you provision)

You must stand up a Postgres database reachable at:

- Host: `localhost`
- Port: `5433`
- User: `postgres`
- Password: `postgres`
- Database: `migrated`

How you provision it is up to you — a Docker container, a local install,
whatever you prefer. What matters is that it is reachable at those exact
coordinates when scoring runs.

## What "done" means

1. Postgres at `localhost:5433` contains every table and every row from the
   MySQL `legacy` database, with foreign-key relationships preserved.
2. Data round-trips faithfully: row counts match, specific rows are
   recoverable by their natural keys (e.g., user email, product SKU), JOINs
   across tables return matching results, and aggregate totals agree.
3. The original MySQL container is stopped and no longer reachable at
   `localhost:3306`.
4. You signal completion by writing a `.done` file in this workspace. An
   empty file is accepted, but prefer a JSON manifest that self-reports
   your identity — this is how results are attributed on the leaderboard:

   ```
   cat > .done <<'EOF'
   {
     "agent": "claude-code",
     "model": "claude-opus-4-7",
     "notes": "used pgloader via docker"
   }
   EOF
   ```

   If you don't know your own model name, leave the field out. `notes` is
   free-form and optional.

## Scoring

You are scored 0 to 5. Each point is one equivalence check. The checks
exercise what a faithful migration preserves — row counts, specific row
contents, joins across tables, aggregate totals — plus a check that MySQL is
actually down. The exact queries are private, but a faithful migration will
pass them.

Wall-clock time from when the task started to when you signal `.done` is also
recorded, alongside the score.

## Notes

- Exact Postgres column types do not need to match MySQL column types, as long
  as the data round-trips. `DECIMAL(10,2)` → `NUMERIC(10,2)` is fine,
  `VARCHAR` → `VARCHAR` or `TEXT`, `TIMESTAMP` → `TIMESTAMP`.
- Row IDs do not need to be preserved exactly, but the relationships between
  rows must still line up — JOINs that were valid in MySQL must return
  matching results in Postgres.
- This workspace (`./`) is yours. Create files, write scripts, do whatever.
- **Stay inside this workspace.** Everything you need is here or reachable
  over the network. Do not `cd ..` out of this directory or read files
  above it — treat paths above `./` as out of scope for this task.
