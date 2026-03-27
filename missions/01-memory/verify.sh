#!/bin/bash
set -e

APP_URL="${APP_URL:-http://localhost:5001}"
PASS=0
FAIL=0

echo "=== Mission 01: Memory — Verification ==="
echo ""

echo -n "1. App is reachable... "
if curl -sf "$APP_URL/" > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (is 'docker compose up' running?)"
    exit 1
fi

echo -n "2. Documents are indexed... "
PAGE=$(curl -sf "$APP_URL/" 2>/dev/null)
if echo "$PAGE" | grep -q "chunks"; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (no indexed documents found)"
    FAIL=$((FAIL + 1))
fi

# Test semantic search — search for a concept NOT literally in the docs
echo -n "3. Semantic search works (concept match)... "
RESULT=$(curl -sf "$APP_URL/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "machine running out of memory", "top_k": 3}' \
    2>/dev/null)

if echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert len(data.get('results', [])) > 0
# At least one result should have >30% similarity
assert any(r['similarity'] > 0.3 for r in data['results'])
" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (no relevant results returned)"
    FAIL=$((FAIL + 1))
fi

# Test that results are ranked by similarity (semantic, not keyword)
echo -n "4. Results are semantically ranked... "
RESULT=$(curl -sf "$APP_URL/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "protecting against unauthorized access", "top_k": 3}' \
    2>/dev/null)

if echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
results = data.get('results', [])
assert len(results) >= 2
# Results should be in descending similarity order
sims = [r['similarity'] for r in results]
assert sims == sorted(sims, reverse=True), f'Not sorted: {sims}'
" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL (results not properly ranked)"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi

echo ""
echo "Mission 01 complete! Your AI has memory."
echo "Next: cd ../02-retrieval && docker compose up"
