#!/bin/bash
#
# Run Multi-Agent System with ForeverVM Integration
#

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  Multi-Agent System Launcher    ${NC}"
echo -e "${BLUE}=================================${NC}"

# Default values
URL=""
SECURE_MODE=false
MAX_ITERATIONS=1
BYPASS_PERMISSIONS=false
SANDBOX_TEST_ONLY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --url=*)
      URL="${1#*=}"
      shift
      ;;
    --url)
      URL="$2"
      shift 2
      ;;
    --iterations=*)
      MAX_ITERATIONS="${1#*=}"
      shift
      ;;
    --iterations)
      MAX_ITERATIONS="$2"
      shift 2
      ;;
    --secure)
      SECURE_MODE=true
      shift
      ;;
    --bypass-permissions)
      BYPASS_PERMISSIONS=true
      shift
      ;;
    --test-sandbox)
      SANDBOX_TEST_ONLY=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --url=URL                Website URL to clone"
      echo "  --iterations=N           Number of improvement iterations (default: 1)"
      echo "  --secure                 Enable secure mode"
      echo "  --bypass-permissions     Bypass ForeverVM permission checks"
      echo "  --test-sandbox          Only test the ForeverVM sandbox"
      echo "  --help                   Show this help message"
      echo ""
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check URL
if [ -z "$URL" ] && [ "$SANDBOX_TEST_ONLY" = false ]; then
  echo -e "${YELLOW}No URL specified. Using default example.com${NC}"
  URL="https://example.com"
fi

# Display configuration
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Website URL:      ${GREEN}$URL${NC}"
echo -e "  Max iterations:   ${GREEN}$MAX_ITERATIONS${NC}"
echo -e "  Secure mode:      ${GREEN}$SECURE_MODE${NC}"
echo -e "  Bypass perms:     ${GREEN}$BYPASS_PERMISSIONS${NC}"
echo -e "  Test sandbox:     ${GREEN}$SANDBOX_TEST_ONLY${NC}"
echo ""

# Load environment from .env file if it exists
if [ -f ".env" ]; then
  echo -e "${BLUE}Loading environment from .env file...${NC}"
  export $(grep -v '^#' .env | xargs)
  MASKED_TOKEN="${FOREVERVM_API_TOKEN:0:5}..."
  echo -e "ForeverVM API Token: ${GREEN}$MASKED_TOKEN${NC}"
else
  echo -e "${YELLOW}No .env file found. ForeverVM features may be limited.${NC}"
fi

# Check if we need to bypass permissions
if [ "$BYPASS_PERMISSIONS" = true ]; then
  echo -e "${YELLOW}Bypassing ForeverVM permission checks...${NC}"
  
  # Execute bypass script non-interactively
  echo "y" | ./skip_permission_check.sh
fi

# Test sandbox only if requested
if [ "$SANDBOX_TEST_ONLY" = true ]; then
  echo -e "${BLUE}Testing ForeverVM sandbox...${NC}"
  python3 forevervm_simple_test.py
  echo -e "${GREEN}Sandbox test complete.${NC}"
  exit 0
fi

# Select which implementation to use
if [ -f "forevervm_bypass.py" ] && [ "$BYPASS_PERMISSIONS" = true ]; then
  IMPLEMENTATION="forevervm_bypass.py"
elif [ -f "optimal_implementation.py" ]; then
  IMPLEMENTATION="optimal_implementation.py"
else
  IMPLEMENTATION="forevervm_simple_test.py"
fi

echo -e "${BLUE}Using implementation: ${GREEN}$IMPLEMENTATION${NC}"

# Build command
CMD="python3 $IMPLEMENTATION"

if [ "$IMPLEMENTATION" = "optimal_implementation.py" ]; then
  # Add optimal implementation arguments
  CMD="$CMD --url $URL --iterations $MAX_ITERATIONS"
  
  if [ "$SECURE_MODE" = true ]; then
    # Check for python version to determine if ForeverVM is viable
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
    PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
    
    if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
      echo -e "${YELLOW}Warning: ForeverVM requires Python 3.10+, but you have Python ${PY_VERSION}${NC}"
      echo -e "${YELLOW}Using simulated sandbox instead${NC}"
    else
      CMD="$CMD --secure"
    fi
  fi
elif [ "$IMPLEMENTATION" = "forevervm_bypass.py" ]; then
  # Add bypass arguments
  CMD="$CMD --dangerously-skip-permission-checks --code \"import requests; print('Testing sandbox with URL: $URL')\""
fi

# Execute the command
echo -e "${BLUE}Executing:${NC} $CMD"
echo ""
eval $CMD