#!/bin/bash
# Quick test script to validate ContextGrid API + CLI + Web UI setup

set -e

echo "========================================="
echo "ContextGrid System Test"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if API server is running
echo "1. Checking API server..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}✓ API server is running${NC}"
else
    echo -e "${RED}✗ API server is not running${NC}"
    echo "Start it with: python -m api.server"
    exit 1
fi

# Test API health endpoint
echo ""
echo "2. Testing API health endpoint..."
HEALTH=$(curl -s http://localhost:8000/api/health | python -c "import sys, json; print(json.load(sys.stdin)['status'])")
if [ "$HEALTH" = "ok" ]; then
    echo -e "${GREEN}✓ API health check passed${NC}"
else
    echo -e "${RED}✗ API health check failed${NC}"
    exit 1
fi

# Test CLI list command
echo ""
echo "3. Testing CLI list command..."
if python src/main.py list > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CLI list command works${NC}"
else
    echo -e "${RED}✗ CLI list command failed${NC}"
    exit 1
fi

# Count projects
PROJECT_COUNT=$(curl -s http://localhost:8000/api/projects | python -c "import sys, json; print(json.load(sys.stdin)['total'])")
echo ""
echo "4. Current project count: $PROJECT_COUNT"

# Test creating a project via API
echo ""
echo "5. Creating test project via API..."
NEW_PROJECT=$(curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Project '$(date +%s)'","status":"idea","description":"Automated test project"}' | \
  python -c "import sys, json; print(json.load(sys.stdin)['id'])")

if [ -n "$NEW_PROJECT" ]; then
    echo -e "${GREEN}✓ Created project with ID: $NEW_PROJECT${NC}"
else
    echo -e "${RED}✗ Failed to create project${NC}"
    exit 1
fi

# Test CLI show command
echo ""
echo "6. Testing CLI show command..."
if python src/main.py show $NEW_PROJECT > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CLI show command works${NC}"
else
    echo -e "${RED}✗ CLI show command failed${NC}"
    exit 1
fi

# Test adding tag
echo ""
echo "7. Testing tag operations..."
if python src/main.py tag add $NEW_PROJECT test-tag > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Added tag to project${NC}"
else
    echo -e "${RED}✗ Failed to add tag${NC}"
    exit 1
fi

# Test touch
echo ""
echo "8. Testing touch command..."
if python src/main.py touch $NEW_PROJECT > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Touch command works${NC}"
else
    echo -e "${RED}✗ Touch command failed${NC}"
    exit 1
fi

# Clean up test project
echo ""
echo "9. Cleaning up test project..."
if curl -s -X DELETE http://localhost:8000/api/projects/$NEW_PROJECT > /dev/null; then
    echo -e "${GREEN}✓ Test project deleted${NC}"
else
    echo -e "${RED}✗ Failed to delete test project${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "========================================="
echo ""
echo "System is working correctly!"
echo ""
echo "Quick commands:"
echo "  - List projects: python src/main.py list"
echo "  - Add project: python src/main.py add 'Project Name'"
echo "  - API docs: http://localhost:8000/docs"
echo "  - Web UI: http://localhost:8080 (if running)"
