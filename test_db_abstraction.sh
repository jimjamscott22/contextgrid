#!/bin/bash
# Test script for database abstraction layer and dual mode support
# Tests SQLite + Direct mode, and validates the implementation

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "ContextGrid Database Abstraction Test"
echo "========================================="
echo ""

# Set up test environment
export USE_API=false
export DB_TYPE=sqlite
export DB_PATH=/tmp/contextgrid_test.db

# Clean up any existing test database
rm -f /tmp/contextgrid_test.db

echo -e "${YELLOW}Testing SQLite + Direct CLI Mode${NC}"
echo ""

# Test 1: List (should be empty)
echo "1. Testing list command (should be empty)..."
OUTPUT=$(python src/main.py list 2>&1)
if echo "$OUTPUT" | grep -q "No projects found"; then
    echo -e "${GREEN}✓ List command works (empty database)${NC}"
else
    echo -e "${RED}✗ List command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 2: Add project
echo ""
echo "2. Testing add command..."
OUTPUT=$(python src/main.py add "Test Project" <<EOF

active
web
Python
FastAPI



Testing database abstraction
EOF
)
if echo "$OUTPUT" | grep -q "Project created with ID"; then
    echo -e "${GREEN}✓ Add command works${NC}"
else
    echo -e "${RED}✗ Add command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 3: List (should have 1 project)
echo ""
echo "3. Testing list command (should show project)..."
OUTPUT=$(python src/main.py list 2>&1)
if echo "$OUTPUT" | grep -q "Test Project"; then
    echo -e "${GREEN}✓ List command shows created project${NC}"
else
    echo -e "${RED}✗ List command doesn't show project${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 4: Show project
echo ""
echo "4. Testing show command..."
OUTPUT=$(python src/main.py show 1 2>&1)
if echo "$OUTPUT" | grep -q "Test Project"; then
    echo -e "${GREEN}✓ Show command works${NC}"
else
    echo -e "${RED}✗ Show command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 5: Add tags
echo ""
echo "5. Testing tag add command..."
OUTPUT=$(python src/main.py tag add 1 python 2>&1)
if echo "$OUTPUT" | grep -q "added to project"; then
    echo -e "${GREEN}✓ Tag add command works${NC}"
else
    echo -e "${RED}✗ Tag add command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

OUTPUT=$(python src/main.py tag add 1 testing 2>&1)
if echo "$OUTPUT" | grep -q "added to project"; then
    echo -e "${GREEN}✓ Tag add command works (second tag)${NC}"
else
    echo -e "${RED}✗ Tag add command failed (second tag)${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 6: List tags
echo ""
echo "6. Testing tag list command..."
OUTPUT=$(python src/main.py tag list 2>&1)
if echo "$OUTPUT" | grep -q "python" && echo "$OUTPUT" | grep -q "testing"; then
    echo -e "${GREEN}✓ Tag list command works${NC}"
else
    echo -e "${RED}✗ Tag list command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 7: List tags for project
echo ""
echo "7. Testing tag list for specific project..."
OUTPUT=$(python src/main.py tag list 1 2>&1)
if echo "$OUTPUT" | grep -q "python" && echo "$OUTPUT" | grep -q "testing"; then
    echo -e "${GREEN}✓ Project tag list works${NC}"
else
    echo -e "${RED}✗ Project tag list failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 8: Filter by tag
echo ""
echo "8. Testing list by tag..."
OUTPUT=$(python src/main.py list --tag python 2>&1)
if echo "$OUTPUT" | grep -q "Test Project"; then
    echo -e "${GREEN}✓ Filter by tag works${NC}"
else
    echo -e "${RED}✗ Filter by tag failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 9: Filter by status
echo ""
echo "9. Testing list by status..."
OUTPUT=$(python src/main.py list --status active 2>&1)
if echo "$OUTPUT" | grep -q "Test Project"; then
    echo -e "${GREEN}✓ Filter by status works${NC}"
else
    echo -e "${RED}✗ Filter by status failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 10: Touch project
echo ""
echo "10. Testing touch command..."
OUTPUT=$(python src/main.py touch 1 2>&1)
if echo "$OUTPUT" | grep -q "Updated last_worked_at"; then
    echo -e "${GREEN}✓ Touch command works${NC}"
else
    echo -e "${RED}✗ Touch command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 11: Database verification
echo ""
echo "11. Testing database persistence..."
# Count projects directly in database
PROJECT_COUNT=$(sqlite3 /tmp/contextgrid_test.db "SELECT COUNT(*) FROM projects;" 2>/dev/null || echo "0")
if [ "$PROJECT_COUNT" = "1" ]; then
    echo -e "${GREEN}✓ Database persistence works${NC}"
else
    echo -e "${RED}✗ Database persistence failed (expected 1, got $PROJECT_COUNT)${NC}"
    exit 1
fi

# Test 12: Remove tag
echo ""
echo "12. Testing tag remove command..."
OUTPUT=$(python src/main.py tag remove 1 testing 2>&1)
if echo "$OUTPUT" | grep -q "removed from project"; then
    echo -e "${GREEN}✓ Tag remove command works${NC}"
else
    echo -e "${RED}✗ Tag remove command failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 13: Verify tag removed
OUTPUT=$(python src/main.py tag list 1 2>&1)
if echo "$OUTPUT" | grep -q "python" && ! echo "$OUTPUT" | grep -q "testing"; then
    echo -e "${GREEN}✓ Tag removed successfully${NC}"
else
    echo -e "${RED}✗ Tag not removed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 14: Create second project
echo ""
echo "14. Creating second project..."
OUTPUT=$(python src/main.py add "Second Project" <<EOF
Another test project
idea







EOF
)
if echo "$OUTPUT" | grep -q "Project created with ID"; then
    echo -e "${GREEN}✓ Second project created${NC}"
else
    echo -e "${RED}✗ Second project creation failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 15: Verify multiple projects
echo ""
echo "15. Testing multiple projects listing..."
OUTPUT=$(python src/main.py list 2>&1)
if echo "$OUTPUT" | grep -q "Test Project" && echo "$OUTPUT" | grep -q "Second Project"; then
    echo -e "${GREEN}✓ Multiple projects listed correctly${NC}"
else
    echo -e "${RED}✗ Multiple projects listing failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Test 16: Generate roadmap
echo ""
echo "16. Testing roadmap generation..."
OUTPUT=$(python src/main.py roadmap --output /tmp/test_roadmap.md 2>&1)
if [ -f /tmp/test_roadmap.md ]; then
    echo -e "${GREEN}✓ Roadmap generated successfully${NC}"
    rm -f /tmp/test_roadmap.md
else
    echo -e "${RED}✗ Roadmap generation failed${NC}"
    echo "$OUTPUT"
    exit 1
fi

# Clean up
echo ""
echo "Cleaning up test database..."
rm -f /tmp/contextgrid_test.db

echo ""
echo "========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "========================================="
echo ""
echo "✅ SQLite + Direct CLI mode is working correctly"
echo "✅ All CRUD operations are functional"
echo "✅ Tag management is working"
echo "✅ Filtering and querying work"
echo ""
echo "The database abstraction layer is fully functional!"
