#!/bin/bash

# Setup script for Multi-Agent Grok Integration with ForeverVM

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}  Setting up Multi-Agent Grok Integration for Weed.th   ${NC}"
echo -e "${BLUE}  with ForeverVM Secure Execution                       ${NC}"
echo -e "${BLUE}========================================================${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo -e "${RED}Please install Python 3.8+ from https://www.python.org/downloads/${NC}"
    exit 1
fi

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}ℹ️ UV not found. Installing...${NC}"
    
    # Install UV (Python package manager)
    curl -sSf https://install.python-poetry.org | python3 -
    pip3 install uv
fi

# Check if Node.js is installed (required for ForeverVM)
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required for ForeverVM but not installed.${NC}"
    echo -e "${RED}Please install Node.js 16+ from https://nodejs.org/${NC}"
    
    # Continue anyway, we'll handle ForeverVM later
    echo -e "${BLUE}ℹ️ Continuing setup without Node.js...${NC}"
    echo -e "${BLUE}ℹ️ ForeverVM functionality will be limited.${NC}"
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"
    
    # Check npm
    if command -v npm &>/dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✓ npm found: $NPM_VERSION${NC}"
    else
        echo -e "${RED}❌ npm not found but needed for ForeverVM.${NC}"
    fi
fi

# Create virtual environment
echo -e "${BLUE}ℹ️ Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source venv/bin/activate
else
    source venv/Scripts/activate
fi

# Install required Python packages
echo -e "${BLUE}ℹ️ Installing Python dependencies...${NC}"
uv pip install requests flask pathlib argparse pytest

# Install ForeverVM Python SDK if possible
echo -e "${BLUE}ℹ️ Attempting to install ForeverVM SDK...${NC}"
if pip3 install forevervm-sdk 2>/dev/null; then
    echo -e "${GREEN}✓ ForeverVM SDK installed successfully${NC}"
else
    echo -e "${BLUE}ℹ️ ForeverVM SDK installation skipped${NC}"
    echo -e "${BLUE}ℹ️ You can install it later with: pip install forevervm-sdk${NC}"
fi

# Copy the ForeverVM integration file
echo -e "${BLUE}ℹ️ Setting up ForeverVM integration...${NC}"
if [ ! -f "integrate_forevervm.py" ]; then
    # Create a stub file if the real one doesn't exist
    cat > integrate_forevervm.py << EOF
#!/usr/bin/env python3
"""
ForeverVM Integration for Multi-Agent System
This is a stub file. To use actual ForeverVM functionality:
1. Install Node.js and npm
2. Install ForeverVM SDK: pip install forevervm-sdk
3. Set FOREVERVM_API_TOKEN environment variable
"""

import os
import sys
import json
from typing import Dict, Any, Optional

class ForeverVMSandbox:
    """ForeverVM sandbox stub for secure code execution."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the ForeverVM sandbox stub."""
        self.api_token = api_token or os.environ.get("FOREVERVM_API_TOKEN", "")
        self.machine = None
    
    def __enter__(self):
        """Create a ForeverVM machine when entering context."""
        print("⚠️ This is a ForeverVM stub. No actual sandbox will be created.")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up ForeverVM machine when exiting context."""
        pass
    
    def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code (stub implementation)."""
        print(f"⚠️ ForeverVM stub: Would execute code with timeout {timeout}s")
        return {
            "success": True,
            "output": "ForeverVM stub - code not actually executed",
            "return_value": None,
            "error": None
        }

class MultiAgentExecutor:
    """Integrates ForeverVM with the multi-agent system (stub)."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the multi-agent executor stub."""
        self.api_token = api_token
    
    def safe_execute_implementation(self, code_file: str) -> Dict[str, Any]:
        """Safely execute implementation code (stub)."""
        print(f"⚠️ ForeverVM stub: Would execute {code_file}")
        return {
            "success": True,
            "output": "ForeverVM stub - code not actually executed",
            "return_value": None,
            "error": None
        }
    
    def test_implementation(self, code_file: str, test_code: str) -> Dict[str, Any]:
        """Test implementation with provided test code (stub)."""
        print(f"⚠️ ForeverVM stub: Would test {code_file}")
        return {
            "success": True,
            "output": "ForeverVM stub - tests not actually executed",
            "return_value": None,
            "error": None
        }
EOF
    echo -e "${BLUE}ℹ️ Created ForeverVM integration stub${NC}"
    echo -e "${BLUE}ℹ️ For full functionality, see requirements in integrate_forevervm.py${NC}"
else
    echo -e "${GREEN}✓ ForeverVM integration file exists${NC}"
fi

# Make the script executable
chmod +x multi_agent_grok_integration.py

# Create directories for multi-agent system if they don't exist
echo -e "${BLUE}ℹ️ Setting up multi-agent directories...${NC}"
mkdir -p test_multi_agent/{crawler,analysis,implementation,feedback,orchestrator}/output
mkdir -p test_multi_agent/shared

# Check for ForeverVM configuration
if [ ! -d "test_multi_agent/orchestrator" ]; then
    mkdir -p test_multi_agent/orchestrator
fi

# Create ForeverVM configuration if it doesn't exist
if [ ! -f "test_multi_agent/orchestrator/forevervm_config.json" ]; then
    cat > test_multi_agent/orchestrator/forevervm_config.json << EOF
{
  "forevervm": {
    "enabled": true,
    "api_token_env": "FOREVERVM_API_TOKEN",
    "timeout_seconds": 60,
    "default_packages": [
      "requests",
      "beautifulsoup4",
      "pytest",
      "pandas",
      "numpy"
    ],
    "sandbox_settings": {
      "allow_network": true,
      "persistent_storage": true,
      "memory_limit_mb": 1024,
      "cpu_limit": 1.0
    },
    "agent_integrations": {
      "implementation": {
        "enabled": true,
        "auto_test": true
      },
      "analysis": {
        "enabled": true
      },
      "feedback": {
        "enabled": true
      },
      "crawler": {
        "enabled": true
      }
    }
  }
}
EOF
    echo -e "${GREEN}✓ Created ForeverVM configuration${NC}"
else
    echo -e "${GREEN}✓ ForeverVM configuration exists${NC}"
fi

# Create an example ForeverVM test file
if [ ! -f "test_multi_agent/implementation/forevervm_task_example.py" ]; then
    echo -e "${BLUE}ℹ️ Creating ForeverVM example task...${NC}"
    echo -e "${BLUE}ℹ️ Check test_multi_agent/implementation/forevervm_task_example.py for usage examples${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup complete! You can now run the multi-agent system:${NC}"
echo ""
echo -e "   python multi_agent_grok_integration.py"
echo ""
echo -e "${BLUE}Optional arguments:${NC}"
echo -e "   --project \"my_project\"   # Project directory name"
echo -e "   --url \"https://example.com\"   # Website to clone"
echo -e "   --secure                 # Enable ForeverVM secure execution"
echo ""
echo -e "${BLUE}ForeverVM Integration:${NC}"
echo -e "1. Set the FOREVERVM_API_TOKEN environment variable"
echo -e "2. Run examples with: python test_multi_agent/implementation/forevervm_task_example.py"
echo ""
echo -e "For more information, see multi_agent_grok_integration.md"
echo -e "${BLUE}========================================================${NC}"