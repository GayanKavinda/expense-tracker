"""
Middleware & Rate Limit Verification Script
=========================================
Tests:
  1. GET /health → Logs appear in terminal in structured format
  2. POST /auth/login x11 → 11th should return 429
  3. Every response has X-Request-ID and X-Response-Time headers
"""

import json
import urllib.request
import urllib.error
import time

BASE_URL = "http://127.0.0.1:8000"
PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode()), dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body), dict(e.headers)
        except Exception:
            return e.code, body, dict(e.headers)
    except Exception as ex:
        return 500, str(ex), {}


# ─── TEST 1: Structured logging ───────────────────────────────────────────────
print()
print("=" * 60)
print("  TEST 1 — Structured log on GET /health")
print("=" * 60)
print(f"{INFO} Sending GET /health ... watch terminal/uvicorn output above for log line")
status, body, headers = make_request("/health")
print(f"  Status : {status}")
print(f"  Body   : {body}")
print(f"{PASS if status == 200 else FAIL} Expected 200, got {status}")


# ─── TEST 2: Check headers ────────────────────────────────────────────────────
print()
print("=" * 60)
print("  TEST 2 — Response Headers (X-Request-ID, X-Response-Time)")
print("=" * 60)
req_id = headers.get("X-Request-ID") or headers.get("x-request-id")
resp_time = headers.get("X-Response-Time") or headers.get("x-response-time")

if req_id:
    print(f"{PASS} X-Request-ID      : {req_id}")
else:
    print(f"{FAIL} X-Request-ID missing!")

if resp_time:
    print(f"{PASS} X-Response-Time   : {resp_time}")
else:
    print(f"{FAIL} X-Response-Time missing!")


# ─── TEST 3: Rate limiting on POST /auth/login ────────────────────────────────
print()
print("=" * 60)
print("  TEST 3 — Rate Limit: POST /auth/login x11 (limit=10/minute)")
print("=" * 60)

payload = {"email": "ratelimit_test@example.com", "password": "wrongpassword"}
statuses = []
headers_ok = []

for i in range(1, 12):
    status, body, resp_headers = make_request("/auth/login", "POST", payload)
    statuses.append(status)
    
    rid = resp_headers.get("X-Request-ID") or resp_headers.get("x-request-id")
    rt  = resp_headers.get("X-Response-Time") or resp_headers.get("x-response-time")
    has_headers = bool(rid and rt)
    headers_ok.append(has_headers)
    
    marker = "← 429 expected here" if i == 11 else ""
    hdr_ok = "✓ headers" if has_headers else "✗ NO HEADERS"
    print(f"  Request {i:>2}: status={status}  {hdr_ok}  {marker}")

print()
# Did request 11 return 429?
if statuses[10] == 429:
    print(f"{PASS} Request #11 returned 429 Too Many Requests")
else:
    print(f"{FAIL} Request #11 returned {statuses[10]} — expected 429")
    print("       → Make sure @limiter.limit('10/minute') is on the login endpoint")
    print("         and the server was restarted after the change.\n")

# Did ALL responses have headers?
if all(headers_ok):
    print(f"{PASS} All 11 responses had X-Request-ID and X-Response-Time")
else:
    missing = [i+1 for i, ok in enumerate(headers_ok) if not ok]
    print(f"{FAIL} Requests missing headers: {missing}")

print()
print("=" * 60)
print("  DONE — Check uvicorn terminal output for structured log lines")
print("  Expected format:")
print("  2026-06-07T... [info] request method=GET path=/health status_code=200 duration_ms=1.2 request_id=01J...")
print("=" * 60)
print()
