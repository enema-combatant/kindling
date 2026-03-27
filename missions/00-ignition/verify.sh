#!/bin/bash
# Mission 00 — Ignition: Smoke test
# Verifies the chat endpoint responds coherently.

set -e

APP_URL="${APP_URL:-http://localhost:5000}"
PASS=0
FAIL=0

echo "=== Mission 00: Ignition — Verification ==="
echo ""

# Check if the app is running
echo -n "1. App is reachable... "
if curl -sf "$APP_URL/" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (is 'docker compose up' running?)"
    FAIL=$((FAIL + 1))
    echo ""
    echo "Start the mission first: docker compose up"
    exit 1
fi

# Send a chat request and check for a non-empty response
echo -n "2. Chat endpoint responds... "
RESPONSE=$(curl -sf "$APP_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{"message": "What is 2 + 2? Reply with just the number."}' \
    2>/dev/null)

if [ -z "$RESPONSE" ]; then
    echo "FAIL (empty response)"
    FAIL=$((FAIL + 1))
else
    # Check that response contains JSON with a "response" field
    if echo "$RESPONSE" | python3 -c "import sys,json; r=json.load(sys.stdin); assert 'response' in r and len(r['response']) > 0" 2>/dev/null; then
        echo "PASS"
        PASS=$((PASS + 1))
    else
        echo "FAIL (unexpected response format)"
        FAIL=$((FAIL + 1))
    fi
fi

# Check streaming endpoint
echo -n "3. Streaming endpoint works... "
STREAM_OUTPUT=$(curl -sf "$APP_URL/stream" \
    -H "Content-Type: application/json" \
    -d '{"message": "Say hello in one word."}' \
    --max-time 30 2>/dev/null)

if echo "$STREAM_OUTPUT" | grep -q "data:"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (no streaming data received)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi

echo ""
echo "Mission 00 complete! Your AI is operational."
echo "Next: cd ../01-memory && docker compose up"
