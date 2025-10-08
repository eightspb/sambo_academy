#!/bin/bash

# Sambo Academy - Comprehensive Test Runner
# This script runs all tests with coverage reporting

set -e

echo "🧪 Sambo Academy - Running Comprehensive Tests"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing...${NC}"
    pip install pytest pytest-asyncio pytest-cov httpx
fi

# Check if coverage is installed
if ! command -v coverage &> /dev/null; then
    echo -e "${YELLOW}⚠️  coverage not found. Installing...${NC}"
    pip install coverage
fi

echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install -q pytest pytest-asyncio pytest-cov httpx sqlalchemy[asyncio] asyncpg

echo ""
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Run tests with coverage
echo -e "${YELLOW}🔬 Running tests with coverage...${NC}"
echo ""

pytest tests/ \
    -v \
    --tb=short \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml \
    -W ignore::DeprecationWarning \
    || TEST_EXIT_CODE=$?

echo ""
echo "=============================================="

if [ ${TEST_EXIT_CODE:-0} -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}📊 Coverage report generated:${NC}"
    echo "   - Terminal: See above"
    echo "   - HTML: htmlcov/index.html"
    echo "   - XML: coverage.xml"
    echo ""
    echo -e "${GREEN}🎉 Test suite completed successfully!${NC}"
else
    echo -e "${RED}❌ Some tests failed. Exit code: ${TEST_EXIT_CODE}${NC}"
    echo ""
    echo "Please review the test output above for details."
    exit ${TEST_EXIT_CODE}
fi

# Show summary
echo ""
echo "=============================================="
echo -e "${YELLOW}📈 Test Summary:${NC}"
pytest tests/ --collect-only -q 2>/dev/null | tail -1 || echo "Run pytest to see test count"
echo "=============================================="
