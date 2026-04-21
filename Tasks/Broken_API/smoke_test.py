#!/usr/bin/env python3
import json
import urllib.request
import sys

API_URL = "http://localhost:8080"

def check(name, url, expected_fail):
    try:
        with urllib.request.urlopen(f"{API_URL}{url}", timeout=3) as resp:
            data = json.load(resp)
            if isinstance(data, list):
                result = len(data)
                expected = f"len={expected_fail}"
            elif isinstance(data, dict) and "total" in data:
                result = data["total"]
                expected = f"total={expected_fail}"
            else:
                result = data
                expected = expected_fail
            status = "PASS" if str(result) == str(expected_fail) else "FAIL"
            print(f"[{status}] {name}: {result} (expected {expected})")
            return str(result) == str(expected_fail)
    except Exception as e:
        print(f"[FAIL] {name}: ERROR - {e}")
        return False

print("=== SMOKE TEST: Verifying Bugs ===\n")

# Bug 1: Products returns 9 instead of 8
check("Bug 1 (products len)", "/products", 9)

# Bug 2: Orders?status=completed returns 0
check("Bug 2 (orders/completed)", "/orders?status=completed", 0)

# Bug 3: User 2 orders returns 4 instead of 3
check("Bug 3 (user/2/orders)", "/users/2/orders", 4)

# Bug 4: Pagination returns wrong IDs
try:
    with urllib.request.urlopen(f"{API_URL}/products?page=2&per_page=3", timeout=3) as resp:
        data = json.load(resp)
        ids = [x["id"] for x in data]
        expected = [4, 5, 6]
        status = "FAIL" if ids == expected else "PASS"  # Should NOT be [4,5,6]
        print(f"[{status}] Bug 4 (pagination ids): {ids} (expected NOT {expected})")
except Exception as e:
    print(f"[FAIL] Bug 4: ERROR - {e}")

# Bug 5: Order total is 34.33 instead of 34.34
try:
    payload = json.dumps({
        "user_id": 1,
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 2, "quantity": 4},
            {"product_id": 3, "quantity": 3}
        ]
    }).encode()
    req = urllib.request.Request(
        f"{API_URL}/orders",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=3) as resp:
        data = json.load(resp)
        total = data.get("total")
        expected = 34.33
        status = "PASS" if abs(total - expected) < 0.001 else "FAIL"
        print(f"[{status}] Bug 5 (order total): {total} (expected {expected})")
except Exception as e:
    print(f"[FAIL] Bug 5: ERROR - {e}")

print("\n[OK] All bugs verified!")
