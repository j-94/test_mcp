#!/bin/bash
#
# Multi-Agent System Runner
#

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  Multi-Agent System Runner      ${NC}"
echo -e "${BLUE}=================================${NC}"

# Default values
URL="https://example.com"
MODE="visual"
ITERATIONS=2
DYNAMIC=false
SECURE=false

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
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --iterations=*)
      ITERATIONS="${1#*=}"
      shift
      ;;
    --iterations)
      ITERATIONS="$2"
      shift 2
      ;;
    --dynamic)
      DYNAMIC=true
      shift
      ;;
    --secure)
      SECURE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --url=URL             Website URL to clone (default: https://example.com)"
      echo "  --mode=MODE           Running mode: visual, ui, or basic (default: visual)"
      echo "  --iterations=N        Number of improvement iterations (default: 2)"
      echo "  --dynamic             Use dynamic agent creation"
      echo "  --secure              Enable secure sandbox mode"
      echo "  --help                Show this help message"
      echo ""
      echo "Modes:"
      echo "  visual: Run simulation with visual status display"
      echo "  ui:     Launch the web-based UI"
      echo "  basic:  Run the simple multi-agent script"
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

# Display configuration
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Website URL:     ${GREEN}$URL${NC}"
echo -e "  Running mode:    ${GREEN}$MODE${NC}"
echo -e "  Iterations:      ${GREEN}$ITERATIONS${NC}"
echo -e "  Dynamic agents:  ${GREEN}$DYNAMIC${NC}"
echo -e "  Secure sandbox:  ${GREEN}$SECURE${NC}"
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

# Execute based on mode
case "$MODE" in
  "visual")
    echo -e "${BLUE}Launching visual mode...${NC}"
    ./launch_system_monitor.sh --url="$URL" --iterations="$ITERATIONS"
    ;;
  "ui")
    echo -e "${BLUE}Launching web UI...${NC}"
    python3 agent_ui.py
    ;;
  "basic")
    echo -e "${BLUE}Running basic multi-agent system...${NC}"
    SECURE_OPTION=""
    if [ "$SECURE" = true ]; then
      SECURE_OPTION="--secure"
    fi
    ./run_multi_agent.sh --url="$URL" --iterations="$ITERATIONS" $SECURE_OPTION
    ;;
  *)
    echo -e "${RED}Unknown mode: $MODE${NC}"
    echo "Use --help for usage information"
    exit 1
    ;;
esac

# Dynamic agent creation handling
if [ "$DYNAMIC" = true ]; then
  echo -e "${BLUE}Setting up dynamic agent creation...${NC}"
  
  # Initialize the system
  python3 dynamic_agent_creator.py --init
  
  # Create all agents
  python3 dynamic_agent_creator.py --create-all
  
  # Launch all agents if in basic mode
  if [ "$MODE" = "basic" ]; then
    python3 dynamic_agent_creator.py --launch-all
  fi
fi