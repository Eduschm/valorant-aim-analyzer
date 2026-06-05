#!/usr/bin/env bash
# smoke.sh — launch backend + frontend, run API smoke test, report all route statuses
# Run from repo root: bash .claude/skills/run-valorant-aim-analyzer/smoke.sh
set -e

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"

PYTHON=".venv/Scripts/python.exe"
if [ ! -f "$PYTHON" ]; then
  PYTHON="python3"
fi

# --- Backend ---
echo "[backend] starting on :8000"
cd "$ROOT/services/api"
DEV_MODE=true \
  ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-dummy}" \
  RIOT_API_KEY="${RIOT_API_KEY:-dummy}" \
  "$ROOT/$PYTHON" -m uvicorn main:app --port 8000 2>&1 | sed 's/^/[api] /' &
BACKEND_PID=$!
cd "$ROOT"

# Wait for backend ready
for i in $(seq 1 20); do
  sleep 1
  python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>/dev/null && break
  echo "[backend] waiting... ($i)"
done

echo ""
echo "=== API smoke ==="

python3 - <<'PYEOF'
import urllib.request, json, time

BASE = "http://localhost:8000"

def get(path):
    r = urllib.request.urlopen(BASE + path)
    return r.status, json.loads(r.read())

def post(path, body):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req)
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# 1. Health
status, body = get("/health")
assert status == 200 and body["status"] == "ok", f"health failed: {body}"
print(f"  PASS  GET /health  ->  {body}")

# 2. Dev account creation
status, body = post("/api/v1/dev/create-account", {"email": "smoke@test.local"})
assert status == 200 and "token" in body, f"dev account failed: {body}"
token = body["token"]
print(f"  PASS  POST /api/v1/dev/create-account  ->  token={token[:16]}...")

# 3. Submit analysis (will error at Riot step without real key — expected)
status, body = post("/api/v1/analyze", {"riot_id": "Smoke#TEST"})
assert status == 200 and "report_id" in body, f"analyze failed: {body}"
report_id = body["report_id"]
print(f"  PASS  POST /api/v1/analyze  ->  report_id={report_id}")

# 4. Poll report
time.sleep(4)
status, body = get(f"/api/v1/report/{report_id}")
assert status == 200 and body["status"] in ("queued","processing","done","error"), f"report poll failed: {body}"
print(f"  PASS  GET /api/v1/report/{{id}}  ->  status={body['status']}  (error expected without real RIOT_API_KEY)")

# 5. Auth stub returns 501
status, body = post("/api/v1/auth/magic-link", {"email": "smoke@test.local"})
assert status == 501, f"expected 501, got {status}: {body}"
print(f"  PASS  POST /api/v1/auth/magic-link  ->  501 (not implemented, expected)")

print("\nAll API smoke checks passed.")
PYEOF

# --- Frontend ---
echo ""
echo "=== Frontend routes ==="
cd "$ROOT/frontend"
NEXT_PUBLIC_MOCK_MODE=true NEXT_PUBLIC_API_URL=http://localhost:8000 \
  node_modules/.bin/next dev --port 3000 2>&1 | sed 's/^/[next] /' &
FRONTEND_PID=$!
cd "$ROOT"

# Wait for frontend ready
for i in $(seq 1 30); do
  sleep 1
  python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:3000')" 2>/dev/null && break
  echo "[frontend] waiting... ($i)"
done

python3 - <<'PYEOF'
import urllib.request

routes = ["/", "/analysis/new", "/auth/signin", "/dashboard", "/profile", "/tracker", "/settings"]
all_ok = True
for r in routes:
    try:
        resp = urllib.request.urlopen("http://localhost:3000" + r)
        code = resp.status
    except Exception as e:
        code = str(e)
        all_ok = False
    ok = "PASS" if code == 200 else "FAIL"
    print(f"  {ok}  {r}  ->  {code}")

if all_ok:
    print("\nAll frontend routes returned 200.")
else:
    print("\nSome routes failed.")
    raise SystemExit(1)
PYEOF

# Cleanup
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
echo ""
echo "Smoke complete. Both servers stopped."
