#!/bin/bash
# Launch script for Multi-Agent UI with ForeverVM

# Export the ForeverVM API token from .env file if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Loaded environment from .env file"
  echo "ForeverVM API Token: ${FOREVERVM_API_TOKEN:0:5}... (set)"
else
  echo "No .env file found. ForeverVM features may be limited."
fi

# Check for Python
if command -v python3 &> /dev/null; then
  PYTHON=python3
elif command -v python &> /dev/null; then
  PYTHON=python
else
  echo "❌ Python not found. Please install Python 3.8+"
  exit 1
fi

# Launch the UI
echo "🚀 Launching Multi-Agent System UI..."
echo "📋 Press Ctrl+C to stop the UI"
$PYTHON agent_ui.py

# This script should be executable with: chmod +x launch_ui.sh