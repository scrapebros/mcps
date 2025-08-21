#!/bin/bash

# Playwright Test Runner Script
# This script provides various options for running Playwright tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
LANGUAGE="js"
BROWSER="all"
HEADLESS="true"
PARALLEL="true"
REPORT="true"

# Function to print colored output
print_color() {
    echo -e "${2}${1}${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -l, --language [js|python|both]   Language to run tests in (default: js)"
    echo "  -b, --browser [chromium|firefox|webkit|all]  Browser to test (default: all)"
    echo "  -h, --headed                      Run tests in headed mode"
    echo "  -s, --serial                      Run tests serially (not parallel)"
    echo "  -r, --no-report                   Don't generate HTML report"
    echo "  -t, --test <pattern>              Run specific test file or pattern"
    echo "  -g, --grep <pattern>              Run tests matching grep pattern"
    echo "  -d, --debug                       Run tests in debug mode"
    echo "  -u, --update-snapshots            Update snapshots"
    echo "  -w, --watch                       Run tests in watch mode"
    echo "  --help                            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                # Run all JS tests in all browsers"
    echo "  $0 -l python -b chromium          # Run Python tests in Chromium only"
    echo "  $0 -l both -h                     # Run all tests in headed mode"
    echo "  $0 -t example.spec.ts             # Run specific test file"
    echo "  $0 -g 'should load homepage'      # Run tests matching pattern"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--language)
            LANGUAGE="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -h|--headed)
            HEADLESS="false"
            shift
            ;;
        -s|--serial)
            PARALLEL="false"
            shift
            ;;
        -r|--no-report)
            REPORT="false"
            shift
            ;;
        -t|--test)
            TEST_FILE="$2"
            shift 2
            ;;
        -g|--grep)
            GREP_PATTERN="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG="true"
            shift
            ;;
        -u|--update-snapshots)
            UPDATE_SNAPSHOTS="true"
            shift
            ;;
        -w|--watch)
            WATCH="true"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to run JavaScript/TypeScript tests
run_js_tests() {
    print_color "Running JavaScript/TypeScript tests..." "$GREEN"
    
    # Build command
    CMD="npx playwright test"
    
    # Add browser option
    if [ "$BROWSER" != "all" ]; then
        CMD="$CMD --project=$BROWSER"
    fi
    
    # Add headed/headless option
    if [ "$HEADLESS" = "false" ]; then
        CMD="$CMD --headed"
    fi
    
    # Add parallel/serial option
    if [ "$PARALLEL" = "false" ]; then
        CMD="$CMD --workers=1"
    fi
    
    # Add specific test file
    if [ ! -z "$TEST_FILE" ]; then
        CMD="$CMD $TEST_FILE"
    fi
    
    # Add grep pattern
    if [ ! -z "$GREP_PATTERN" ]; then
        CMD="$CMD --grep \"$GREP_PATTERN\""
    fi
    
    # Add debug mode
    if [ "$DEBUG" = "true" ]; then
        CMD="$CMD --debug"
    fi
    
    # Add update snapshots
    if [ "$UPDATE_SNAPSHOTS" = "true" ]; then
        CMD="$CMD --update-snapshots"
    fi
    
    # Add watch mode
    if [ "$WATCH" = "true" ]; then
        CMD="$CMD --watch"
    fi
    
    # Run tests
    echo "Executing: $CMD"
    eval $CMD
    
    # Show report
    if [ "$REPORT" = "true" ] && [ "$WATCH" != "true" ]; then
        print_color "Opening test report..." "$YELLOW"
        npx playwright show-report
    fi
}

# Function to run Python tests
run_python_tests() {
    print_color "Running Python tests..." "$GREEN"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Build command
    CMD="pytest"
    
    # Add browser option
    if [ "$BROWSER" != "all" ]; then
        CMD="$CMD --browser $BROWSER"
    else
        CMD="$CMD --browser chromium --browser firefox --browser webkit"
    fi
    
    # Add headed/headless option
    if [ "$HEADLESS" = "false" ]; then
        CMD="$CMD --headed"
    fi
    
    # Add parallel/serial option
    if [ "$PARALLEL" = "true" ]; then
        CMD="$CMD -n auto"
    fi
    
    # Add specific test file
    if [ ! -z "$TEST_FILE" ]; then
        CMD="$CMD tests/e2e/python/$TEST_FILE"
    else
        CMD="$CMD tests/e2e/python"
    fi
    
    # Add grep pattern
    if [ ! -z "$GREP_PATTERN" ]; then
        CMD="$CMD -k \"$GREP_PATTERN\""
    fi
    
    # Add debug mode
    if [ "$DEBUG" = "true" ]; then
        CMD="$CMD --pdb"
    fi
    
    # Add verbose output
    CMD="$CMD -v"
    
    # Run tests
    echo "Executing: $CMD"
    eval $CMD
    
    # Deactivate virtual environment
    deactivate
    
    # Show report
    if [ "$REPORT" = "true" ]; then
        print_color "Test report generated at: reports/pytest-report.html" "$YELLOW"
    fi
}

# Main execution
print_color "=== Playwright Test Runner ===" "$GREEN"
echo ""

# Check if dependencies are installed
if [ "$LANGUAGE" = "js" ] || [ "$LANGUAGE" = "both" ]; then
    if [ ! -d "node_modules" ]; then
        print_color "Node modules not found. Installing dependencies..." "$YELLOW"
        npm install
        npx playwright install
    fi
fi

if [ "$LANGUAGE" = "python" ] || [ "$LANGUAGE" = "both" ]; then
    if [ ! -d "venv" ]; then
        print_color "Virtual environment not found. Creating and installing dependencies..." "$YELLOW"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        playwright install
        deactivate
    fi
fi

# Create reports directory if it doesn't exist
mkdir -p reports/screenshots

# Run tests based on language selection
case $LANGUAGE in
    js)
        run_js_tests
        ;;
    python)
        run_python_tests
        ;;
    both)
        run_js_tests
        echo ""
        run_python_tests
        ;;
    *)
        print_color "Invalid language option: $LANGUAGE" "$RED"
        show_usage
        exit 1
        ;;
esac

print_color "=== Test execution completed ===" "$GREEN"