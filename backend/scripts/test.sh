#!/bin/bash
# Backend test runner script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}${1}${NC}"
}

case "${1:-all}" in
    unit)
        print_status "Running unit tests..." "$YELLOW"
        pytest -m unit -v
        ;;
    integration)
        print_status "Running integration tests..." "$YELLOW"
        pytest -m integration -v
        ;;
    slow)
        print_status "Running slow tests..." "$YELLOW"
        pytest -m slow -v
        ;;
    coverage)
        print_status "Running tests with coverage..." "$YELLOW"
        pytest --cov=app --cov-report=html --cov-report=term
        print_status "Coverage report generated in htmlcov/" "$GREEN"
        ;;
    all)
        print_status "Running all tests..." "$YELLOW"
        pytest -v
        ;;
    watch)
        print_status "Running tests in watch mode..." "$YELLOW"
        pytest -v --watch
        ;;
    *)
        echo "Usage: ./scripts/test.sh {unit|integration|slow|coverage|all|watch}"
        exit 1
        ;;
esac

print_status "Tests completed!" "$GREEN"
