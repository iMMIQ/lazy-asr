#!/bin/bash
# Test runner script for lazy-asr project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: ./scripts/test.sh [OPTION] [TARGET]

Run tests for the lazy-asr project.

OPTIONS:
    backend, -b, --backend     Run backend tests only
    frontend, -f, --frontend   Run frontend tests only
    e2e, -e, --e2e            Run E2E tests only
    all, -a, --all            Run all tests (default)
    coverage, -c, --coverage  Run tests with coverage report
    unit, -u, --unit          Run unit tests only
    integration, -i, --integration Run integration tests only
    help, -h, --help          Show this help message

TARGETS:
    Backend tests: pytest markers (unit, integration, slow)
    Frontend tests: vitest patterns

EXAMPLES:
    ./scripts/test.sh                    # Run all tests
    ./scripts/test.sh backend unit       # Run backend unit tests
    ./scripts/test.sh frontend coverage  # Run frontend tests with coverage
    ./scripts/test.sh -e                 # Run E2E tests

EOF
}

# Default values
RUN_BACKEND=false
RUN_FRONTEND=false
RUN_E2E=false
RUN_COVERAGE=false
PYTEST_MARKER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        backend|-b|--backend)
            RUN_BACKEND=true
            shift
            ;;
        frontend|-f|--frontend)
            RUN_FRONTEND=true
            shift
            ;;
        e2e|-e|--e2e)
            RUN_E2E=true
            shift
            ;;
        all|-a|--all)
            RUN_BACKEND=true
            RUN_FRONTEND=true
            RUN_E2E=true
            shift
            ;;
        coverage|-c|--coverage)
            RUN_COVERAGE=true
            shift
            ;;
        unit|-u|--unit)
            PYTEST_MARKER="-m unit"
            shift
            ;;
        integration|-i|--integration)
            PYTEST_MARKER="-m integration"
            shift
            ;;
        help|-h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_status "Unknown option: $1" "$RED"
            show_usage
            exit 1
            ;;
    esac
done

# If no specific test type selected, run all
if [ "$RUN_BACKEND" = false ] && [ "$RUN_FRONTEND" = false ] && [ "$RUN_E2E" = false ]; then
    RUN_BACKEND=true
    RUN_FRONTEND=true
    RUN_E2E=false  # E2E tests are slower, don't run by default
fi

# Track overall status
ALL_TESTS_PASSED=true

# Run backend tests
if [ "$RUN_BACKEND" = true ]; then
    print_status "Running backend tests..." "$YELLOW"
    cd backend

    if [ "$RUN_COVERAGE" = true ]; then
        pytest $PYTEST_MARKER -v --cov=app --cov-report=html --cov-report=term || ALL_TESTS_PASSED=false
    else
        pytest $PYTEST_MARKER -v || ALL_TESTS_PASSED=false
    fi

    cd ..
fi

# Run frontend tests
if [ "$RUN_FRONTEND" = true ]; then
    print_status "Running frontend tests..." "$YELLOW"
    cd frontend

    if [ "$RUN_COVERAGE" = true ]; then
        npm run test:coverage || ALL_TESTS_PASSED=false
    else
        npm run test:run || ALL_TESTS_PASSED=false
    fi

    cd ..
fi

# Run E2E tests
if [ "$RUN_E2E" = true ]; then
    print_status "Running E2E tests..." "$YELLOW"
    cd frontend
    npm run test:e2e || ALL_TESTS_PASSED=false
    cd ..
fi

# Final status
if [ "$ALL_TESTS_PASSED" = true ]; then
    print_status "All tests passed!" "$GREEN"
    exit 0
else
    print_status "Some tests failed!" "$RED"
    exit 1
fi
