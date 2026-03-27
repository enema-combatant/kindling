#!/bin/bash
set -e

APP_URL="${APP_URL:-http://localhost:5002}"
PASS=0
FAIL=0

echo "=== Mission 02: Retrieval — Verification ==="
echo ""

echo -n "1. App is reachable... "
if curl -sf "$APP_URL/" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    exit 1
fi

echo -n "2. RAG endpoint responds with answer and sources... "
RESULT=$(curl -sf "$APP_URL/ask" \
    -H "Content-Type: application/json" \
    -d '{"query": "How do I prevent a service from consuming too much memory?"}' \
    --max-time 60 2>/dev/null)

if echo "$RESULT" | grep -q "sources"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "3. Answer includes citation... "
if echo "$RESULT" | grep -q ".txt"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (no source citation in response)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -gt 0 ] && exit 1

echo ""
echo "Mission 02 complete! Your AI can answer questions from your documents."
echo "Next: cd ../03-voice && docker compose up"
