#!/bin/bash
#
# Quick test script for Tide v2
#

echo "🌊 Testing Tide v2..."
echo ""

# Test 1: Import
echo -n "✓ Testing imports... "
python3 -c "from tide_v2 import TideAgent" 2>/dev/null && echo "OK" || echo "FAILED"

# Test 2: Tool count
echo -n "✓ Testing tool count... "
COUNT=$(python3 -c "from tide_v2 import TideAgent; a=TideAgent(); print(len(a.get_available_tools()))" 2>/dev/null)
if [ "$COUNT" -eq 10 ]; then
    echo "OK (10 tools)"
else
    echo "FAILED (found $COUNT tools)"
fi

# Test 3: CLI help
echo -n "✓ Testing CLI... "
python3 tide-v2.py --help > /dev/null 2>&1 && echo "OK" || echo "FAILED"

# Test 4: Check files
echo -n "✓ Checking files... "
if [ -f "tide-v2.py" ] && [ -d "tide_v2" ] && [ -f "Dockerfile" ]; then
    echo "OK"
else
    echo "FAILED"
fi

echo ""
echo "Test complete!"
