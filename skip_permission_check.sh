#!/bin/bash
#
# Script to modify the --dangerously-skip-permission check for ForeverVM
# USE WITH CAUTION: This bypasses security checks which exist for a reason
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Warning message
echo -e "${YELLOW}⚠️  WARNING: This script modifies security checks${NC}"
echo -e "${YELLOW}⚠️  Only use in controlled development environments${NC}"
echo -e "${YELLOW}⚠️  NEVER use in production environments${NC}"
echo ""

# Confirm execution
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Operation cancelled.${NC}"
    exit 0
fi

# Find python packages directory
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "Detected Python version: ${GREEN}$PYTHON_VERSION${NC}"

# Determine package path based on environment
if [ -d "$HOME/.pyenv" ]; then
    # pyenv installation
    SITE_PACKAGES="$HOME/.pyenv/versions/$PYTHON_VERSION/lib/python$PYTHON_VERSION/site-packages"
    echo "Detected pyenv installation"
elif [ -d "$HOME/Library/Python/$PYTHON_VERSION" ]; then
    # macOS user installation
    SITE_PACKAGES="$HOME/Library/Python/$PYTHON_VERSION/lib/python/site-packages"
    echo "Detected macOS user installation"
elif [ -d "/usr/local/lib/python$PYTHON_VERSION" ]; then
    # System-wide installation
    SITE_PACKAGES="/usr/local/lib/python$PYTHON_VERSION/dist-packages"
    echo "Detected system-wide installation"
else
    # Try to find it using Python itself
    SITE_PACKAGES=$(python3 -c 'import site; print(site.getsitepackages()[0])')
    echo "Using Python-provided site-packages path"
fi

echo -e "Using site-packages path: ${GREEN}$SITE_PACKAGES${NC}"

# Check if the directory exists
if [ ! -d "$SITE_PACKAGES" ]; then
    echo -e "${RED}Error: Site packages directory not found at: $SITE_PACKAGES${NC}"
    echo -e "${YELLOW}Trying to detect path automatically...${NC}"
    
    # Try to detect it automatically
    SITE_PACKAGES=$(python3 -c 'import site; print(site.getsitepackages()[0])')
    
    if [ ! -d "$SITE_PACKAGES" ]; then
        echo -e "${RED}Could not automatically detect site-packages directory.${NC}"
        echo "Please install ForeverVM first with: pip install forevervm-sdk"
        exit 1
    else
        echo -e "Found site-packages at: ${GREEN}$SITE_PACKAGES${NC}"
    fi
fi

# Look for ForeverVM SDK
FOREVERVM_DIR="$SITE_PACKAGES/forevervm_sdk"

if [ ! -d "$FOREVERVM_DIR" ]; then
    echo -e "${RED}ForeverVM SDK not found at: $FOREVERVM_DIR${NC}"
    echo "Do you want to install it now? (y/n)"
    read -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing ForeverVM SDK..."
        pip3 install forevervm-sdk
        
        # Check if installation succeeded
        if [ ! -d "$FOREVERVM_DIR" ]; then
            echo -e "${RED}Installation failed or directory still not found.${NC}"
            echo "Please install manually with: pip install forevervm-sdk"
            exit 1
        fi
    else
        echo "Please install ForeverVM SDK first with: pip install forevervm-sdk"
        exit 1
    fi
fi

echo -e "ForeverVM SDK found at: ${GREEN}$FOREVERVM_DIR${NC}"

# Look for security check files
POSSIBLE_FILES=(
    "$FOREVERVM_DIR/repl.py"
    "$FOREVERVM_DIR/client.py"
    "$FOREVERVM_DIR/machine.py"
    "$FOREVERVM_DIR/auth.py"
)

MODIFIED_FILES=0

for FILE in "${POSSIBLE_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo -e "Checking file: ${GREEN}$FILE${NC}"
        
        # Create a backup
        BACKUP_FILE="${FILE}.bak"
        cp "$FILE" "$BACKUP_FILE"
        echo "Created backup: $BACKUP_FILE"
        
        # Check if file contains permission checks
        if grep -q "permission" "$FILE" || grep -q "dangerously-skip" "$FILE"; then
            echo -e "${YELLOW}Found permission checks in $FILE${NC}"
            
            # Modify the file to bypass permission checks
            sed -i.tmp 's/if not args\.dangerously_skip_permission_checks:/if False:/g' "$FILE"
            sed -i.tmp 's/--dangerously-skip-permission-checks/--dangerously-skip-permission-checks (enabled by default)/g' "$FILE"
            
            # Remove temporary files from sed
            rm -f "${FILE}.tmp"
            
            echo -e "${GREEN}Modified file to bypass permission checks${NC}"
            MODIFIED_FILES=$((MODIFIED_FILES + 1))
        else
            echo "No permission checks found in this file"
        fi
    fi
done

if [ $MODIFIED_FILES -eq 0 ]; then
    echo -e "${YELLOW}No files were modified. Permission checks might be in different files.${NC}"
    
    # Ask if user wants to search for permission checks in all files
    echo "Do you want to search for permission checks in all ForeverVM files? (y/n)"
    read -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Searching for permission checks in all files..."
        PERM_FILES=$(grep -r "permission" "$FOREVERVM_DIR" | grep -v ".bak" | cut -d ":" -f 1 | sort | uniq)
        
        if [ -z "$PERM_FILES" ]; then
            echo "No files with permission checks found."
        else
            echo -e "${YELLOW}Files containing permission checks:${NC}"
            echo "$PERM_FILES"
            
            # Ask if user wants to modify these files
            echo "Do you want to modify these files to bypass permission checks? (y/n)"
            read -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                for FILE in $PERM_FILES; do
                    echo -e "Modifying file: ${GREEN}$FILE${NC}"
                    
                    # Create a backup
                    BACKUP_FILE="${FILE}.bak"
                    cp "$FILE" "$BACKUP_FILE"
                    echo "Created backup: $BACKUP_FILE"
                    
                    # Modify the file to bypass permission checks
                    sed -i.tmp 's/if not args\.dangerously_skip_permission_checks:/if False:/g' "$FILE"
                    sed -i.tmp 's/--dangerously-skip-permission-checks/--dangerously-skip-permission-checks (enabled by default)/g' "$FILE"
                    
                    # Remove temporary files from sed
                    rm -f "${FILE}.tmp"
                    
                    MODIFIED_FILES=$((MODIFIED_FILES + 1))
                done
            fi
        fi
    fi
fi

# Create a custom stub implementation if no files were modified
if [ $MODIFIED_FILES -eq 0 ]; then
    echo -e "${YELLOW}No ForeverVM files were modified. Creating a custom stub implementation...${NC}"
    
    # Create stub implementation
    STUB_FILE="$PWD/forevervm_bypass.py"
    cat > "$STUB_FILE" << 'EOF'
#!/usr/bin/env python3
"""
ForeverVM Stub Implementation with Permission Checks Bypassed
WARNING: For development environments only
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Constants
DEFAULT_TIMEOUT = 30  # seconds

class ForeverVMMachine:
    """Stub implementation of ForeverVM machine with permission checks bypassed"""
    
    def __init__(self, token=None):
        self.token = token
        self.env = {}  # Environment for code execution
        print(f"🔒 ForeverVM machine created with permissions bypassed")
    
    def run(self, code, timeout=DEFAULT_TIMEOUT):
        """Run code in a simulated sandbox (NOT A TRUE SANDBOX)"""
        print(f"⚙️ Running code in simulated sandbox: {len(code)} bytes")
        
        # This is NOT a true sandbox - it's just for demonstration
        try:
            # Setup a temporary execution environment
            self.env = {"__result": None}
            
            # Execute code
            exec(code, self.env)
            
            # Get any printed output
            output = "Execution successful (no output captured in stub mode)"
            
            # Get return value if any
            return_value = self.env.get("__result", None)
            
            return {
                "output": output,
                "return_value": return_value,
                "state": "complete"
            }
        except Exception as e:
            return {
                "output": f"Error executing code: {str(e)}",
                "return_value": None,
                "state": "error"
            }

class ForeverVM:
    """Stub ForeverVM client with permission checks bypassed"""
    
    def __init__(self, token=None):
        """Initialize ForeverVM client"""
        self.token = token or os.environ.get("FOREVERVM_API_TOKEN", "")
        print(f"🔑 ForeverVM initialized with token: {self.token[:5]}..." if self.token else "⚠️ No token provided")
    
    def create_machine(self):
        """Create a ForeverVM machine with permission checks bypassed"""
        return ForeverVMMachine(self.token)

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description="ForeverVM Stub with Permission Checks Bypassed")
    parser.add_argument("--dangerously-skip-permission-checks", action="store_true", 
                        help="Permission checks are already bypassed in this stub", default=True)
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--code", type=str, help="Python code to execute", default=None)
    
    args = parser.parse_args()
    
    if args.version:
        print("ForeverVM Stub 0.1.0 (Permission Checks Bypassed)")
        return
    
    if args.code:
        client = ForeverVM()
        machine = client.create_machine()
        result = machine.run(args.code)
        print("Output:", result["output"])
        print("Return value:", result["return_value"])
        print("State:", result["state"])
    else:
        print("No code provided to execute.")

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$STUB_FILE"
    echo -e "${GREEN}Created stub implementation at: $STUB_FILE${NC}"
    echo "You can use this file to import a version of ForeverVM with permission checks bypassed."
    echo "Example:"
    echo "  from forevervm_bypass import ForeverVM"
    echo "  client = ForeverVM()"
    echo "  machine = client.create_machine()"
    echo "  result = machine.run('print(\"Hello World\")')"
fi

echo ""
if [ $MODIFIED_FILES -gt 0 ]; then
    echo -e "${GREEN}Successfully modified $MODIFIED_FILES files to bypass permission checks${NC}"
    echo -e "${YELLOW}To restore original files, copy the .bak files back to their original names${NC}"
else
    echo -e "${YELLOW}No existing ForeverVM files were modified${NC}"
    echo -e "${GREEN}A stub implementation has been created instead${NC}"
fi

echo ""
echo -e "${YELLOW}⚠️  SECURITY WARNING:${NC}"
echo "The permission checks in ForeverVM exist to protect your system."
echo "Only use this modified version in controlled development environments."
echo "NEVER use in production environments."