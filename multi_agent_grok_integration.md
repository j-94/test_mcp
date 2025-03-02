# Multi-Agent Grok Integration for Website Cloning

This document explains how to use the `multi_agent_grok_integration.py` script to deploy a complete multi-agent system for website cloning and improvement.

## Overview

This integration combines:

1. **Multi-Agent Architecture** - Specialized agents working together for website cloning
2. **UV Python Packaging** - Self-contained deployment with automated dependency management
3. **Claude Desktop Integration** - Leveraging Claude's capabilities across multiple agents
4. **Jujutsu (JJ) Workspaces** - Version control with isolated workspaces for each agent

## System Components

The system consists of five specialized agents:

1. **Crawler Agent** - Extracts website structure and creates initial representation
2. **Analysis Agent** - Identifies design patterns and component structures
3. **Implementation Agent** - Converts analysis into working code
4. **Feedback Agent** - Evaluates implementation and suggests improvements
5. **Orchestrator Agent** - Coordinates the workflow between all agents

## How It Works

1. **Dependency Management**
   - The script checks for required dependencies (Python, Node.js, etc.)
   - Missing dependencies are automatically installed
   - Claude CLI is set up for agent communication

2. **Workspace Setup**
   - Creates a directory structure for all agents
   - Sets up JJ workspaces for version control
   - Generates agent-specific instruction files
   - Establishes a shared communication protocol

3. **Agent Execution**
   - Launches each agent in a separate terminal window
   - Agents communicate through a structured JSON protocol
   - The orchestrator manages workflow and dependencies

## How to Run

Run the script with the following command:

```bash
python multi_agent_grok_integration.py --project "my_project" --url "https://example.com"
```

Optional arguments:
- `--project`: Name of the project directory (default: "weedth_claude")
- `--url`: URL of the website to clone (default: "https://example.com")

## System Requirements

- Python 3.8+
- Node.js and npm (auto-installed if missing)
- Claude CLI (@anthropic-ai/claude-code)
- Jujutsu (JJ) for workspace management (auto-installed)

## Communication Protocol

Agents communicate using a standardized message format:

```json
{
  "message_id": "uuid-string",
  "source_agent": "agent-name",
  "destination_agent": "agent-name",
  "message_type": "request|response|notification|error",
  "timestamp": "ISO-8601-timestamp",
  "priority": 0-10,
  "payload": {
    // Message-specific data
  },
  "metadata": {
    // Additional context information
  }
}
```

## Directory Structure

The system creates the following directory structure:

```
project_name/
├── crawler/
│   ├── CLAUDE.md
│   ├── crawler_tasks.sh
│   └── output/
├── analysis/
│   ├── CLAUDE.md
│   ├── analysis_tasks.sh
│   └── output/
├── implementation/
│   ├── CLAUDE.md
│   ├── implementation_tasks.sh
│   └── output/
├── feedback/
│   ├── CLAUDE.md
│   ├── feedback_tasks.sh
│   └── output/
├── orchestrator/
│   ├── CLAUDE.md
│   ├── orchestrator_tasks.sh
│   └── output/
└── shared/
    └── communication_protocol.json
```

## Customization

To customize agent behavior:
1. Edit the CLAUDE.md file in each agent directory
2. Modify the agent_tasks.sh scripts with specific instructions
3. Adjust the communication protocol for custom message types

## Troubleshooting

- If the script fails to install dependencies, try running it with administrator privileges
- If agents fail to start, check the Claude CLI installation with `claude --version`
- If agents can't communicate, verify the shared/communication_protocol.json file exists and is properly formatted

## Future Enhancements

1. **Self-Modifying Capabilities**
   - Allowing agents to improve their own code
   - Implementing performance monitoring
   - Enabling automated optimization

2. **True VLM Integration**
   - Direct Claude Vision API integration
   - Real-time screenshot analysis
   - Visual feedback loop

3. **Multi-Tool Orchestration**
   - Integration with specialized AI models
   - Task delegation framework
   - Cross-model consensus mechanisms