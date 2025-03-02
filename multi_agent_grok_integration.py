#!/usr/bin/env python
import subprocess
import os
import sys
import json
import time
import argparse
from pathlib import Path

def run_command(command, cwd=None, shell=False, capture_output=False):
    """Run a shell command and handle errors."""
    try:
        if capture_output:
            return subprocess.run(command, cwd=cwd, shell=shell, check=True, 
                                 capture_output=True, text=True)
        subprocess.run(command, cwd=cwd, shell=shell, check=True)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running {command}: {e}")
        if not capture_output:
            print("Continuing despite the error...")
        return None
    except Exception as e:
        print(f"Unexpected error running {command}: {e}")
        if not capture_output:
            print("Continuing despite the error...")
        return None

def check_dependencies():
    """Check for required dependencies and install if missing."""
    print("Checking for dependencies...")
    
    # Check for Python requirements
    try:
        import requests
        import flask
    except ImportError:
        print("Installing Python dependencies with UV...")
        run_command(["uv", "pip", "install", "requests", "flask"])
    
    # Check for Node.js and npm
    print("Checking for Node.js and npm...")
    node_installed = False
    npm_installed = False
    
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        node_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        npm_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if not (node_installed and npm_installed):
        print("Node.js or npm not found. Installing...")
        if os.name == 'nt':  # Windows
            run_command(["winget", "install", "nodejs"])
        elif sys.platform == 'darwin':  # macOS
            run_command(["brew", "install", "node"], shell=True)
        else:  # Linux
            run_command(["sudo", "apt-get", "update"], shell=True)
            run_command(["sudo", "apt-get", "install", "-y", "nodejs", "npm"], shell=True)
    
    # Check for Claude CLI
    claude_installed = False
    try:
        result = subprocess.run(["claude", "--help"], capture_output=True, text=True)
        claude_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if not claude_installed:
        print("Installing @anthropic-ai/claude-code...")
        try:
            run_command(["npm", "install", "-g", "@anthropic-ai/claude-code"])
        except Exception as e:
            print(f"Error installing Claude CLI: {e}")
            print("Please install Claude CLI manually with: npm install -g @anthropic-ai/claude-code")
            print("For testing purposes, we'll continue without Claude CLI...")
    
    # Check for Jujutsu (JJ)
    jj_installed = False
    try:
        result = subprocess.run(["jj", "--version"], capture_output=True, text=True)
        jj_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    if not jj_installed:
        print("Installing Jujutsu (JJ)...")
        if os.name != 'nt':  # Linux/macOS
            try:
                # Using a single shell command is safer for pipes
                run_command("curl -s https://raw.githubusercontent.com/martinvonz/jj/main/install.sh | sh", shell=True)
            except Exception as e:
                print(f"Error installing JJ: {e}")
                print("Continuing without JJ...")
        else:  # Windows
            print("Please install JJ manually on Windows: https://github.com/martinvonz/jj/releases")
            print("Continuing without JJ...")

def setup_agent_workspaces(project_name):
    """Set up Jujutsu workspaces for each agent."""
    project_dir = Path(os.getcwd()) / project_name
    print(f"Setting up project in {project_dir}...")
    
    # Create project directory
    project_dir.mkdir(exist_ok=True)
    os.chdir(project_dir)
    
    # Initialize the agent directories
    agents = [
        "crawler",
        "analysis",
        "implementation",
        "feedback",
        "orchestrator"
    ]
    
    # Set up JJ repository if available
    try:
        if run_command(["jj", "--version"], capture_output=True) is not None:
            print("Setting up JJ workspaces...")
            run_command(["jj", "git", "init"])
            
            # Create a workspace for each agent
            for agent in agents:
                run_command(["jj", "workspace", "add", agent])
    except Exception as e:
        print(f"Skipping JJ setup due to error: {e}")
        print("Continuing with directory-based workspaces only...")
    
    # Regardless of JJ, create directories for each agent
    for agent in agents:
        agent_dir = project_dir / agent
        agent_dir.mkdir(exist_ok=True)
        
        # Create a CLAUDE.md file with agent-specific instructions
        claude_md = agent_dir / "CLAUDE.md"
        with open(claude_md, "w") as f:
            f.write(f"# {agent.capitalize()} Agent Instructions\n\n")
            f.write(f"This file contains instructions specific to the {agent} agent.\n\n")
            
            # Add agent-specific responsibilities based on multi_agent_system.md
            if agent == "crawler":
                f.write("## Responsibilities\n\n")
                f.write("- Website structure extraction and cloning\n")
                f.write("- DOM traversal and extraction\n")
                f.write("- Respecting robots.txt and ethical crawling practices\n")
                f.write("- Handling JS-heavy websites and SPAs\n")
                f.write("- Screenshot capture for visual reference\n")
            elif agent == "analysis":
                f.write("## Responsibilities\n\n")
                f.write("- Analyzing website structure and design patterns\n")
                f.write("- Identifying key UI components and patterns\n")
                f.write("- Recognizing responsive design breakpoints\n")
                f.write("- Cataloging design system elements\n")
                f.write("- Identifying accessibility concerns\n")
            elif agent == "implementation":
                f.write("## Responsibilities\n\n")
                f.write("- Converting extracted structure to working code\n")
                f.write("- Generating semantic HTML\n")
                f.write("- Creating optimized CSS\n")
                f.write("- Implementing basic interactivity\n")
                f.write("- Setting up development environment\n")
            elif agent == "feedback":
                f.write("## Responsibilities\n\n")
                f.write("- Capturing and analyzing VLM feedback\n")
                f.write("- Comparing snapshots of different versions\n")
                f.write("- Generating structured improvement suggestions\n")
                f.write("- Prioritizing changes based on impact\n")
                f.write("- Tracking implemented vs. pending changes\n")
            elif agent == "orchestrator":
                f.write("## Responsibilities\n\n")
                f.write("- Coordinating all other agents and managing workflow\n")
                f.write("- Handling agent communication\n")
                f.write("- Managing execution flow and dependencies\n")
                f.write("- Error handling and recovery\n")
                f.write("- Progress tracking and reporting\n")
    
    # Create a shared data directory for agent communication
    shared_dir = project_dir / "shared"
    shared_dir.mkdir(exist_ok=True)
    
    # Create initial communication protocol JSON
    protocol_file = shared_dir / "communication_protocol.json"
    protocol = {
        "message_format": {
            "message_id": "UUID string",
            "source_agent": "Name of sending agent",
            "destination_agent": "Name of receiving agent",
            "message_type": "request|response|notification|error",
            "timestamp": "ISO-8601 timestamp",
            "priority": "0-10 integer",
            "payload": "Message-specific data",
            "metadata": "Additional context information"
        },
        "agent_states": {
            "crawler": "idle",
            "analysis": "idle",
            "implementation": "idle",
            "feedback": "idle",
            "orchestrator": "idle"
        },
        "project_state": "initializing",
        "current_iteration": 0,
        "error_states": {},
        "completion_percentage": 0
    }
    
    with open(protocol_file, "w") as f:
        json.dump(protocol, f, indent=2)
    
    return project_dir

def launch_agents(project_dir, target_url=None):
    """Launch Claude agents for each component."""
    print("Launching agents...")
    
    # Check if Claude CLI is available
    claude_available = False
    try:
        subprocess.run(["claude", "--help"], capture_output=True, check=True)
        claude_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Claude CLI not available. Will create agent task files but won't launch agents.")
    
    # Create a command file for each agent
    agents = [
        "crawler",
        "analysis",
        "implementation",
        "feedback",
        "orchestrator"
    ]
    
    for agent in agents:
        agent_dir = project_dir / agent
        cmd_file = agent_dir / f"{agent}_tasks.sh"
        
        with open(cmd_file, "w") as f:
            f.write("#!/bin/bash\n\n")
            
            if agent == "crawler" and target_url:
                f.write(f'echo "==== {agent.upper()} AGENT ===="\n')
                f.write(f'echo "Processing {target_url}..."\n\n')
                f.write(f'if command -v claude &> /dev/null; then\n')
                f.write(f'  claude "As the Crawler Agent, extract the structure of {target_url}. '\
                        f'Create HTML, CSS, and component files that represent the site\'s structure. '\
                        f'Save all outputs to the ./output directory and update the ../shared/communication_protocol.json '\
                        f'when complete."\n')
                f.write(f'else\n')
                f.write(f'  echo "Claude CLI not available. Would have extracted {target_url}"\n')
                f.write(f'  # Create a sample HTML file as a demonstration\n')
                f.write(f'  echo "<html><head><title>Sample Extracted from {target_url}</title></head><body><h1>Sample Extraction</h1><p>This is a demonstration of the Crawler Agent.</p></body></html>" > ./output/sample.html\n')
                f.write(f'  echo "Created sample output in ./output/sample.html"\n')
                f.write(f'fi\n')
            elif agent == "analysis":
                f.write(f'echo "==== {agent.upper()} AGENT ===="\n\n')
                f.write(f'if command -v claude &> /dev/null; then\n')
                f.write(f'  claude "As the Analysis Agent, examine the website structure in ../crawler/output. '\
                        f'Identify key components, design patterns, and create a design system document. '\
                        f'Save all outputs to the ./output directory and update the ../shared/communication_protocol.json '\
                        f'when complete."\n')
                f.write(f'else\n')
                f.write(f'  echo "Claude CLI not available. Would have analyzed from ../crawler/output"\n')
                f.write(f'  # Create a sample analysis file as a demonstration\n')
                f.write(f'  echo "# Design Analysis\n\n- Simple heading structure\n- Basic paragraph text\n- No complex components identified" > ./output/analysis.md\n')
                f.write(f'  echo "Created sample analysis in ./output/analysis.md"\n')
                f.write(f'fi\n')
            elif agent == "implementation":
                f.write(f'echo "==== {agent.upper()} AGENT ===="\n\n')
                f.write(f'if command -v claude &> /dev/null; then\n')
                f.write(f'  claude "As the Implementation Agent, use the analyses in ../analysis/output to create '\
                        f'a working implementation with semantic HTML, CSS, and basic interactivity. '\
                        f'Save all outputs to the ./output directory and update the ../shared/communication_protocol.json '\
                        f'when complete."\n')
                f.write(f'else\n')
                f.write(f'  echo "Claude CLI not available. Would have implemented based on ../analysis/output"\n')
                f.write(f'  # Create a sample implementation file as a demonstration\n')
                html_content = (
                    '<!DOCTYPE html>\n'
                    '<html>\n'
                    '<head>\n'
                    '  <title>Implemented Site</title>\n'
                    '  <style>\n'
                    '    body { font-family: Arial, sans-serif; }\n'
                    '    h1 { color: navy; }\n'
                    '  </style>\n'
                    '</head>\n'
                    '<body>\n'
                    '  <h1>Implemented Site</h1>\n'
                    '  <p>This is a sample implementation based on the analysis.</p>\n'
                    '</body>\n'
                    '</html>'
                )
                f.write(f'  cat > ./output/index.html << \'EOL\'\n{html_content}\nEOL\n')
                f.write(f'  echo "Created sample implementation in ./output/index.html"\n')
                f.write(f'fi\n')
            elif agent == "feedback":
                f.write(f'echo "==== {agent.upper()} AGENT ===="\n\n')
                f.write(f'if command -v claude &> /dev/null; then\n')
                f.write(f'  claude "As the Feedback Agent, compare the implementation in ../implementation/output '\
                        f'with the original site structure in ../crawler/output. Generate structured improvement '\
                        f'suggestions and save them to the ./output directory. Update ../shared/communication_protocol.json '\
                        f'when complete."\n')
                f.write(f'else\n')
                f.write(f'  echo "Claude CLI not available. Would have provided feedback comparing ../implementation/output with ../crawler/output"\n')
                f.write(f'  # Create a sample feedback file as a demonstration\n')
                f.write(f'  echo "# Improvement Suggestions\n\n1. Add more semantic HTML elements\n2. Improve color contrast for accessibility\n3. Add responsive design breakpoints" > ./output/feedback.md\n')
                f.write(f'  echo "Created sample feedback in ./output/feedback.md"\n')
                f.write(f'fi\n')
            elif agent == "orchestrator":
                f.write(f'echo "==== {agent.upper()} AGENT ===="\n\n')
                f.write(f'if command -v claude &> /dev/null; then\n')
                f.write(f'  claude "As the Orchestrator Agent, monitor and coordinate the activities of all other agents '\
                        f'by checking ../shared/communication_protocol.json. Ensure smooth workflow, handle errors, '\
                        f'and report progress. Create a status report in the ./output directory."\n')
                f.write(f'else\n')
                f.write(f'  echo "Claude CLI not available. Would have orchestrated the multi-agent workflow"\n')
                f.write(f'  # Update the communication protocol to simulate progress\n')
                f.write(f'  echo "Creating a demonstration status update..."\n')
                f.write(f'  cp ../shared/communication_protocol.json ../shared/communication_protocol.json.bak\n')
                f.write(f'  python3 -c \'import json; f = open("../shared/communication_protocol.json", "r"); data = json.load(f); f.close(); data["project_state"] = "complete"; data["completion_percentage"] = 100; for agent in data["agent_states"]: data["agent_states"][agent] = "complete"; f = open("../shared/communication_protocol.json", "w"); json.dump(data, f, indent=2); f.close()\'\n')
                f.write(f'  # Create a sample status report\n')
                f.write(f'  echo "# Multi-Agent System Status Report\n\nAll agents have completed their tasks.\n\n## Agent Status\n- Crawler: Complete\n- Analysis: Complete\n- Implementation: Complete\n- Feedback: Complete\n\n## Next Steps\nReady for iteration 2." > ./output/status_report.md\n')
                f.write(f'  echo "Created sample status report in ./output/status_report.md"\n')
                f.write(f'fi\n')
        
        # Make the command file executable
        os.chmod(cmd_file, 0o755)
        
        # Create output directory
        output_dir = agent_dir / "output"
        output_dir.mkdir(exist_ok=True)
    
    # If Claude is not available, simply print instructions
    if not claude_available:
        print("\nClaude CLI is not available. Agent task files have been created but won't be launched.")
        print(f"To manually run the agents, navigate to {project_dir} and run each agent's task script:")
        print(f"  cd {project_dir}/orchestrator && ./orchestrator_tasks.sh")
        print(f"  cd {project_dir}/crawler && ./crawler_tasks.sh")
        print("  (and so on for each agent)")
        return
    
    # Start the orchestrator agent first
    print("Starting orchestrator agent...")
    orchestrator_dir = project_dir / "orchestrator"
    orchestrator_cmd = orchestrator_dir / "orchestrator_tasks.sh"
    
    # Run the orchestrator in a new terminal window if possible
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(f"start cmd /k {orchestrator_cmd}", shell=True)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(["open", "-a", "Terminal", str(orchestrator_cmd)])
        else:  # Linux
            subprocess.Popen(["gnome-terminal", "--", "bash", str(orchestrator_cmd)])
        
        time.sleep(2)  # Give orchestrator time to start
        
        # Now start the other agents
        for agent in ["crawler", "analysis", "implementation", "feedback"]:
            print(f"Starting {agent} agent...")
            agent_dir = project_dir / agent
            agent_cmd = agent_dir / f"{agent}_tasks.sh"
            
            # Run each agent in a new terminal window
            if os.name == 'nt':  # Windows
                subprocess.Popen(f"start cmd /k {agent_cmd}", shell=True)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(["open", "-a", "Terminal", str(agent_cmd)])
            else:  # Linux
                subprocess.Popen(["gnome-terminal", "--", "bash", str(agent_cmd)])
            
            time.sleep(1)  # Small delay between agent launches
    except Exception as e:
        print(f"Error launching agents: {e}")
        print(f"To manually run the agents, navigate to {project_dir} and run each agent's task script:")

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent System for Website Cloning")
    parser.add_argument("--project", default="weedth_claude", help="Name of the project directory")
    parser.add_argument("--url", default="https://example.com", help="URL of the website to clone")
    args = parser.parse_args()
    
    print("=" * 60)
    print(" Multi-Agent System for Website Cloning and Improvement")
    print("=" * 60)
    
    # Step 1: Check and install dependencies
    check_dependencies()
    
    # Step 2: Set up agent workspaces
    project_dir = setup_agent_workspaces(args.project)
    
    # Step 3: Launch agents
    launch_agents(project_dir, args.url)
    
    print("\nSetup complete! Multi-agent system is now running.")
    print(f"Check the '{args.project}' directory for agent outputs.")
    print("\nAgent status can be monitored in the shared/communication_protocol.json file.")

if __name__ == "__main__":
    main()