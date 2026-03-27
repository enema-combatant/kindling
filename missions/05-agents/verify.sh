#!/bin/bash
set -e

APP_URL="${APP_URL:-http://localhost:5005}"
PASS=0
FAIL=0

echo "=== Mission 05: Agents — Verification ==="
echo ""

echo -n "1. App is reachable... "
if curl -sf "$APP_URL/" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (is 'docker compose up' running?)"
    exit 1
fi

echo -n "2. Agent endpoint accepts a query... "
RESULT=$(curl -sf "$APP_URL/agent" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is 25 * 4?"}' \
    --max-time 120 2>/dev/null)

if echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert 'answer' in data, 'No answer field'
assert 'steps' in data, 'No steps field'
assert 'iterations' in data, 'No iterations field'
" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (agent response missing required fields)"
    FAIL=$((FAIL + 1))
fi

echo -n "3. Agent uses tools (multi-step query)... "
RESULT=$(curl -sf "$APP_URL/agent" \
    -H "Content-Type: application/json" \
    -d '{"query": "Search the knowledge base for container operations and tell me the key points."}' \
    --max-time 120 2>/dev/null)

if echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
steps = data.get('steps', [])
assert len(steps) > 0, 'No tool calls were made'
# At least one step should be a search
tool_names = [s['tool'] for s in steps]
assert 'search_knowledge' in tool_names, f'Expected search_knowledge in {tool_names}'
" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (agent did not use search tool)"
    FAIL=$((FAIL + 1))
fi

echo -n "4. Agent returns reasonable answer... "
if echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
answer = data.get('answer', '')
assert len(answer) > 20, f'Answer too short: {len(answer)} chars'
" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (answer too short or empty)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi

echo ""
echo "Mission 05 complete! Your AI has hands — it can use tools autonomously."
echo "Review the reasoning trace in the UI to see every decision."
