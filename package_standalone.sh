#!/bin/bash

# Package Multi-Agent Grok Integration as a standalone executable

set -e  # Exit on error

echo "========================================================"
echo "  Packaging Multi-Agent Grok as standalone executable   "
echo "========================================================"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is required but not installed."
    echo "Please run ./setup_multi_agent_grok.sh first."
    exit 1
fi

# Check if the Python script exists
if [ ! -f "multi_agent_grok_integration.py" ]; then
    echo "❌ multi_agent_grok_integration.py not found."
    exit 1
fi

# Create a build directory
echo "ℹ️ Creating build directory..."
mkdir -p build

# Package the script using UV
echo "ℹ️ Packaging with UV..."
uv pip install pyinstaller
pyinstaller --onefile multi_agent_grok_integration.py --distpath ./build

# Copy documentation
echo "ℹ️ Copying documentation..."
cp multi_agent_grok_integration.md build/

echo ""
echo "✅ Packaging complete! You can find the standalone executable at:"
echo ""
echo "   build/multi_agent_grok_integration"
echo ""
echo "Run it with:"
echo ""
echo "   ./build/multi_agent_grok_integration --project \"my_project\" --url \"https://example.com\""
echo ""
echo "For more information, see build/multi_agent_grok_integration.md"
echo "========================================================"