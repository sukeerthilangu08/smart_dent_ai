#!/bin/bash
# Mac Verification Script for Smart Dent AI

echo "🦷 Smart Dent AI - Mac Verification"
echo "===================================="
echo ""

# Check if server is running
echo "1. Checking if server is running..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "   ✅ Server is running!"
else
    echo "   ❌ Server is NOT running!"
    echo "   Start it with: python3 backend/app.py"
    exit 1
fi

# Test health endpoint
echo ""
echo "2. Testing health endpoint..."
curl -s http://localhost:8000/api/health | python3 -m json.tool

# Test analysis with sample data
echo ""
echo "3. Testing analysis endpoint..."
echo "   Creating sample image..."

# Create a simple base64 test image (1x1 white pixel)
TEST_IMAGE="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$TEST_IMAGE\"}" | python3 -m json.tool | head -50

echo ""
echo "===================================="
echo "✅ Verification complete!"
echo ""
echo "Next steps:"
echo "1. Open browser: open http://localhost:8000"
echo "2. Or test page: open http://localhost:8000/test.html"
echo "3. Press Cmd+Option+J to open console"
echo "===================================="
