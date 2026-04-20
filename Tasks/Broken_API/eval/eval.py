"""
PRIVATE evaluation script for the Broken API task.

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
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "http://localhost:8080"
TRAFFIC_FILE = Path(__file__).parent / "traffic.json"


def send_request(method: str, path: str, body=None):
    """Send an HTTP request and return (status_code, parsed_json | None)."""
    url = f"{API_BASE}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8") if e.fp else ""
        try:
            body_json = json.loads(raw)
        except Exception:
            body_json = {"raw": raw[:200]}
        return e.code, body_json
    except Exception as e:
        return None, str(e)


def check_response(spec: dict) -> dict:
    """Run one traffic spec and return a check result."""
    name = spec["name"]
    try:
        status, body = send_request(spec["method"], spec["path"], spec.get("body"))

        if status is None:
            return {
                "name": name,
                "passed": False,
                "expected": f"status {spec['expect_status']}",
                "actual": f"connection error: {body}",
            }

        expect = spec["expect_body"]

        # Check status first
        if status != spec["expect_status"]:
            return {
                "name": name,
                "passed": False,
                "expected": f"status {spec['expect_status']}",
                "actual": f"status {status}",
                "error": f"response: {json.dumps(body)[:200]}",
            }

        # Check body based on type
        if expect["type"] == "length":
            actual_len = len(body) if isinstance(body, list) else -1
            passed = actual_len == expect["value"]
            return {
                "name": name,
                "passed": passed,
                "expected": f"length {expect['value']}",
                "actual": f"length {actual_len}",
            }

        elif expect["type"] == "ids":
            actual_ids = [item["id"] for item in body] if isinstance(body, list) else []
            passed = actual_ids == expect["value"]
            return {
                "name": name,
                "passed": passed,
                "expected": f"ids {expect['value']}",
                "actual": f"ids {actual_ids}",
            }

        elif expect["type"] == "field_equals":
            field = expect["field"]
            actual_val = body.get(field) if isinstance(body, dict) else None
            expected_val = expect["value"]
            tolerance = expect.get("tolerance", 0)
            if actual_val is not None and tolerance > 0:
                passed = abs(float(actual_val) - float(expected_val)) < tolerance
            else:
                passed = actual_val == expected_val
            return {
                "name": name,
                "passed": passed,
                "expected": f"{field} = {expected_val}",
                "actual": f"{field} = {actual_val}",
            }

        else:
            return {
                "name": name,
                "passed": False,
                "expected": "unknown check type",
                "actual": str(expect["type"]),
            }

    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "expected": None,
            "actual": None,
            "error": str(e),
        }


def main():
    traffic = json.loads(TRAFFIC_FILE.read_text())
    checks = [check_response(spec) for spec in traffic]

    score = sum(1 for c in checks if c["passed"])
    result = {
        "score": score,
        "max_score": len(checks),
        "checks": checks,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
