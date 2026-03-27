#!/bin/bash
set -e

APP_URL="${APP_URL:-http://localhost:5004}"
PASS=0
FAIL=0

echo "=== Mission 04: Specialization — Verification ==="
echo ""

echo -n "1. App is reachable... "
if curl -sf "$APP_URL/" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    exit 1
fi

echo -n "2. Chat endpoint responds with answer and sources... "
RESULT=$(curl -sf "$APP_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{"query": "A host cannot reach the gateway. What should I check?"}' \
    --max-time 60 2>/dev/null)

if echo "$RESULT" | grep -q "sources"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "3. Test suite endpoint responds... "
EVAL_RESULT=$(curl -sf "$APP_URL/evaluate" --max-time 120 2>/dev/null)

if echo "$EVAL_RESULT" | grep -q "pass_rate"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (test endpoint did not return results)"
    FAIL=$((FAIL + 1))
fi

echo -n "4. Domain name is present in response... "
if echo "$EVAL_RESULT" | grep -qi "network"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -gt 0 ] && exit 1

echo ""
echo "Mission 04 complete! Your domain expert is operational."
echo "Next: cd ../05-agents && docker compose up"
