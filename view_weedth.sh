#!/bin/bash
# Simple script to open the latest weed.th HTML file in a browser

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=== weed.th Viewer ===${NC}"
echo "This script opens the latest generated weed.th HTML file in your default browser."
echo

# Find the latest HTML file
CLONES_DIR="$HOME/weedth_claude/clones"

if [ ! -d "$CLONES_DIR" ]; then
    echo -e "${RED}❌ Clone directory not found at $CLONES_DIR${NC}"
    echo "Please run the weedth_clone_test.js script first to generate files."
    exit 1
fi

LATEST_HTML=$(ls -t "$CLONES_DIR"/*.html 2>/dev/null | head -1)

if [ -z "$LATEST_HTML" ]; then
    echo -e "${RED}❌ No HTML files found in $CLONES_DIR${NC}"
    echo "Please run the weedth_clone_test.js script first to generate files."
    exit 1
fi

# Open the file in the default browser
echo -e "${YELLOW}Opening ${LATEST_HTML} in browser...${NC}"

# Open command based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$LATEST_HTML"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$LATEST_HTML"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    start "$LATEST_HTML"
else
    echo -e "${RED}❌ Unsupported operating system${NC}"
    echo "Please open the file manually: $LATEST_HTML"
    exit 1
fi

echo -e "${GREEN}✅ HTML file opened in browser${NC}"
echo
echo -e "${YELLOW}View the complete outputs at:${NC}"
echo "$CLONES_DIR"