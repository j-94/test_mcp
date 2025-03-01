#!/bin/bash
# Firecrawl MCP Server Setup Script
# Created for weed.th website structure extraction
# Date: March 1, 2025

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=== Firecrawl MCP Server Setup ===${NC}"
echo "This script sets up the Firecrawl MCP server for website structure extraction."
echo "Inspired by X post from February 21, 2025 about website cloning with Claude."
echo

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Node.js and npm
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "✅ Node.js ${GREEN}$NODE_VERSION${NC} is installed"
else
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js v16+ from https://nodejs.org${NC}"
    exit 1
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    echo -e "✅ npm ${GREEN}$NPM_VERSION${NC} is installed"
else
    echo -e "${RED}❌ npm is not installed. Please install npm.${NC}"
    exit 1
fi

# Create working directory
echo -e "\n${YELLOW}Creating working directory...${NC}"
WORK_DIR="$HOME/weedth_claude"
mkdir -p "$WORK_DIR"
echo -e "✅ Created ${GREEN}$WORK_DIR${NC}"

# Install Firecrawl MCP
echo -e "\n${YELLOW}Installing Firecrawl MCP...${NC}"
npm install -g firecrawl-mcp

# Verify installation
if command -v npx firecrawl-mcp --version &> /dev/null; then
    FIRECRAWL_VERSION=$(npx firecrawl-mcp --version)
    echo -e "✅ Firecrawl MCP ${GREEN}$FIRECRAWL_VERSION${NC} installed successfully"
else
    echo -e "${RED}❌ Failed to install Firecrawl MCP. Please check npm for errors.${NC}"
    exit 1
fi

# Set up environment variables
echo -e "\n${YELLOW}Setting up environment variables...${NC}"
read -p "Enter your Firecrawl API key (press Enter to skip): " FIRECRAWL_API_KEY

if [ -n "$FIRECRAWL_API_KEY" ]; then
    # Add to current session
    export FIRECRAWL_API_KEY="$FIRECRAWL_API_KEY"
    
    # Add to shell profile
    if [[ "$SHELL" == *"zsh"* ]]; then
        PROFILE="$HOME/.zshrc"
    else
        PROFILE="$HOME/.bashrc"
    fi
    
    if grep -q "FIRECRAWL_API_KEY" "$PROFILE"; then
        sed -i '' "s/export FIRECRAWL_API_KEY=.*/export FIRECRAWL_API_KEY=\"$FIRECRAWL_API_KEY\"/" "$PROFILE"
    else
        echo "export FIRECRAWL_API_KEY=\"$FIRECRAWL_API_KEY\"" >> "$PROFILE"
    fi
    
    echo -e "✅ API key added to ${GREEN}$PROFILE${NC}"
else
    echo -e "${YELLOW}⚠️ Skipped API key setup. You'll need to set FIRECRAWL_API_KEY manually.${NC}"
fi

# Configure Claude Desktop integration
echo -e "\n${YELLOW}Configuring Claude Desktop integration...${NC}"
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Anthropic/Claude"

if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    
    # Create config file if it doesn't exist
    if [ ! -f "$CONFIG_FILE" ]; then
        echo '{
  "api_key": "",
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "'"$FIRECRAWL_API_KEY"'"
      }
    }
  }
}' > "$CONFIG_FILE"
        echo -e "✅ Created ${GREEN}$CONFIG_FILE${NC}"
    else
        # Backup existing config
        cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
        echo -e "ℹ️ Backed up existing config to ${CONFIG_FILE}.bak"
        
        # Update config to include MCP server
        # This is a simplified approach; a real script should use jq for proper JSON manipulation
        if grep -q "mcpServers" "$CONFIG_FILE"; then
            echo -e "${YELLOW}⚠️ MCP servers already configured in $CONFIG_FILE${NC}"
            echo -e "${YELLOW}⚠️ Please manually add Firecrawl MCP server to your config${NC}"
        else
            # Simple approach, assumes a basic config structure
            sed -i '' 's/\(.*"api_key".*\)/\1,\n  "mcpServers": {\n    "firecrawl-mcp": {\n      "command": "npx",\n      "args": ["firecrawl-mcp"],\n      "env": {\n        "FIRECRAWL_API_KEY": "'"$FIRECRAWL_API_KEY"'"\n      }\n    }\n  }/' "$CONFIG_FILE"
            echo -e "✅ Updated ${GREEN}$CONFIG_FILE${NC} with Firecrawl MCP server configuration"
        fi
    fi
else
    echo -e "${YELLOW}⚠️ Claude Desktop config directory not found at $CLAUDE_CONFIG_DIR${NC}"
    echo -e "${YELLOW}⚠️ Please install Claude Desktop or manually configure the MCP server${NC}"
fi

# Create directory for MCP server resources
echo -e "\n${YELLOW}Setting up MCP server resources...${NC}"
MCP_DIR="$HOME/MCP_Servers"
mkdir -p "$MCP_DIR"

# Create mcp_servers.txt with initial repositories
echo "https://github.com/mendableai/firecrawl-mcp-server" > "$MCP_DIR/mcp_servers.txt"
echo "https://github.com/anthropics/anthropic-tools" >> "$MCP_DIR/mcp_servers.txt" 
echo "https://github.com/appcypher/awesome-mcp-servers" >> "$MCP_DIR/mcp_servers.txt"
echo -e "✅ Created ${GREEN}$MCP_DIR/mcp_servers.txt${NC} with initial repositories"

# Final instructions
echo -e "\n${GREEN}=== Setup Complete ===${NC}"
echo -e "To start the Firecrawl MCP server, run: ${YELLOW}npx firecrawl-mcp${NC}"
echo -e "To verify the server is running, run: ${YELLOW}curl http://localhost:3456/status${NC}"
echo -e "Remember to restart Claude Desktop to apply the configuration changes."
echo
echo -e "${GREEN}=== Usage Instructions ===${NC}"
echo "1. Start the Firecrawl MCP server in a terminal"
echo "2. In Claude Desktop, use the prompt:"
echo -e "   ${YELLOW}Clone the structure of https://example.com using the Firecrawl MCP server${NC}"
echo "3. For the weed.th mapping application, replace example.com with weed.th"
echo
echo -e "${GREEN}=== Ethical Note ===${NC}"
echo "Ensure you have permission to clone website structures."
echo "For development, prefer to use owned, test, or public domain sites."
echo
echo -e "${GREEN}Happy cloning!${NC}"