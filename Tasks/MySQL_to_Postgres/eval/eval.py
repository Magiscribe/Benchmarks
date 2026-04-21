"""
PRIVATE evaluation script for the MySQL → Postgres migration task.

Do NOT reveal the contents of this file or its expected values in task.md.
It is invoked by ../harness.py score after the agent signals .done.

Output: a single JSON document on stdout:
    {
        "score": <int 0..5>,
        "max_score": 5,
        "checks": [
            {"name": str, "passed": bool, "expected": str, "actual": str,
             "error": <optional str>},
            ...
        ]
    }
"""
import json
import socket
import sys
from decimal import Decimal

try:
    import psycopg2
except ImportError:
    print(
        "ERROR: psycopg2 not installed in harness env. "
        "pip install psycopg2-binary",
        file=sys.stderr,
    )
    sys.exit(2)


PG_HOST = "localhost"
PG_PORT = 5433
PG_USER = "postgres"
PG_PASSWORD = "postgres"
PG_DB = "migrated"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306


def pg_connect():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB,
        connect_timeout=5,
    )


def run_check(name, fn):
    try:
        passed, expected, actual = fn()
        return {
            "name": name,
            "passed": bool(passed),
            "expected": repr(expected),
            "actual": repr(actual),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "expected": None,
            "actual": None,
            "error": str(e),
        }


def check_user_count(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        actual = cur.fetchone()[0]
    expected = 5
    return actual == expected, expected, actual


def check_specific_user(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT name FROM users WHERE email = %s",
            ("carol@example.com",),
        )
        row = cur.fetchone()
    actual = row[0] if row else None
    expected = "Carol Davis"
    return actual == expected, expected, actual


def check_user_join(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM orders o "
            "JOIN users u ON u.id = o.user_id "
            "WHERE u.email = %s",
            ("bob@example.com",),
        )
        actual = cur.fetchone()[0]
    expected = 2
    return actual == expected, expected, actual


def check_completed_total(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT SUM(total) FROM orders WHERE status = 'completed'"
        )
        actual = cur.fetchone()[0]
    expected = Decimal("369.94")
    if actual is None:
        return False, expected, None
    diff = abs(Decimal(actual) - expected)
    return diff < Decimal("0.01"), expected, actual


def check_mysql_down():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((MYSQL_HOST, MYSQL_PORT))
        s.close()
        return False, "unreachable", "reachable"
    except (ConnectionRefusedError, socket.timeout, OSError):
        return True, "unreachable", "unreachable"


def main():
    results = []

    try:
        conn = pg_connect()
    except Exception as e:
        for name in (
            "user_count",
            "specific_user",
            "user_join",
            "completed_total",
        ):
            results.append({
                "name": name,
                "passed": False,
                "expected": None,
                "actual": None,
                "error": f"could not connect to Postgres: {e}",
            })
        results.append(run_check("mysql_down", check_mysql_down))
        score = sum(1 for r in results if r["passed"])
        print(json.dumps(
            {"score": score, "max_score": 5, "checks": results}, indent=2
        ))
        return

    try:
        results.append(run_check("user_count", lambda: check_user_count(conn)))
        results.append(run_check("specific_user", lambda: check_specific_user(conn)))
        results.append(run_check("user_join", lambda: check_user_join(conn)))
        results.append(run_check("completed_total", lambda: check_completed_total(conn)))
    finally:
        conn.close()

    results.append(run_check("mysql_down", check_mysql_down))

    score = sum(1 for r in results if r["passed"])
    print(json.dumps(
        {"score": score, "max_score": 5, "checks": results}, indent=2
    ))


if __name__ == "__main__":
    main()
