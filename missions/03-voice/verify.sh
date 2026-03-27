#!/bin/bash
set -e

APP_URL="${APP_URL:-http://localhost:5003}"
WHISPER_URL="${WHISPER_URL:-http://localhost:8100}"
PASS=0
FAIL=0

echo "=== Mission 03: Voice — Verification ==="
echo ""

echo -n "1. App is reachable... "
if curl -sf "$APP_URL/" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    exit 1
fi

echo -n "2. Whisper STT service is healthy... "
if curl -sf "$WHISPER_URL/health" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (Whisper not ready — may still be loading model)"
    FAIL=$((FAIL + 1))
fi

echo -n "3. TTS endpoint responds... "
RESULT=$(curl -sf "$APP_URL/speak" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello, this is a test."}' \
    --max-time 15 \
    -o /dev/null -w "%{http_code}" 2>/dev/null)

if [ "$RESULT" = "200" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (HTTP $RESULT — Piper may not be ready)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -gt 0 ] && exit 1

echo ""
echo "Mission 03 complete! Your AI can hear and speak."
echo "Next: cd ../04-specialization && docker compose up"
