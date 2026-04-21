"""Append a scored run to the per-task leaderboard.csv."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

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


def append_leaderboard_row(leaderboard_file: Path, result: dict, state: dict):
    new_file = not leaderboard_file.exists()
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
    with leaderboard_file.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEADERBOARD_COLUMNS)
        if new_file:
            w.writeheader()
        w.writerow(row)
