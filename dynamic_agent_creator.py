#!/usr/bin/env python3
"""
Dynamic Agent Creator
Creates agent instances based on schema definition and requirements
"""

import os
import sys
import json
import time
import uuid
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Colors for terminal output
COLORS = {
    "blue": "\033[0;34m",
    "green": "\033[0;32m",
    "yellow": "\033[1;33m",
    "red": "\033[0;31m",
    "purple": "\033[0;35m",
    "cyan": "\033[0;36m",
    "reset": "\033[0m"
}

class DynamicAgentCreator:
    """Creates and manages dynamic agents based on schema definition"""
    
    def __init__(self, schema_path: str, base_dir: Optional[str] = None):
        """Initialize with schema path and optional base directory"""
        self.schema_path = schema_path
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.schema = self._load_schema()
        self.agents_created = []
        self.cost_log = []
        
    def _load_schema(self) -> Dict[str, Any]:
        """Load and validate the agent schema"""
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)
            
            # Basic validation
            required_keys = ["system_name", "agent_types", "communication_protocol"]
            for key in required_keys:
                if key not in schema:
                    raise ValueError(f"Schema is missing required key: {key}")
            
            print(f"{COLORS['green']}Schema loaded successfully: {schema['system_name']} v{schema['version']}{COLORS['reset']}")
            return schema
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"{COLORS['red']}Error loading schema: {str(e)}{COLORS['reset']}")
            sys.exit(1)
    
    def initialize_system(self) -> None:
        """Initialize the multi-agent system directories and shared state"""
        print(f"{COLORS['blue']}Initializing multi-agent system...{COLORS['reset']}")
        
        # Create multi-agent base directory if needed
        multi_agent_dir = self.base_dir / "test_multi_agent"
        multi_agent_dir.mkdir(exist_ok=True)
        
        # Create shared directory
        shared_dir = multi_agent_dir / "shared"
        shared_dir.mkdir(exist_ok=True)
        
        # Create or reset communication protocol
        protocol_file = shared_dir / "communication_protocol.json"
        protocol_data = {
            "message_format": self.schema["communication_protocol"]["message_format"],
            "agent_states": {agent_type: "idle" for agent_type in self.schema["agent_types"]},
            "project_state": "initializing",
            "current_iteration": 0,
            "error_states": {},
            "completion_percentage": 0
        }
        
        with open(protocol_file, 'w') as f:
            json.dump(protocol_data, f, indent=2)
        
        # Create default config
        config_file = shared_dir / "config.json"
        if not config_file.exists():
            config_data = {
                "website_url": "https://example.com"
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        
        # Create cost monitoring file if enabled
        if self.schema.get("cost_monitoring", {}).get("enabled", False):
            cost_file = self.base_dir / self.schema["cost_monitoring"].get("log_file", "cost_monitor.log")
            with open(cost_file, 'w') as f:
                f.write(f"# Cost Monitoring Log\nSystem: {self.schema['system_name']}\nStarted: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        print(f"{COLORS['green']}System initialized successfully.{COLORS['reset']}")
    
    def create_agent(self, agent_type: str) -> bool:
        """Create a specific agent based on the schema definition"""
        if agent_type not in self.schema["agent_types"]:
            print(f"{COLORS['red']}Unknown agent type: {agent_type}{COLORS['reset']}")
            return False
        
        agent_info = self.schema["agent_types"][agent_type]
        print(f"{COLORS['yellow']}Creating {agent_type} agent...{COLORS['reset']}")
        
        # Create agent directory
        agent_dir = self.base_dir / "test_multi_agent" / agent_type
        agent_dir.mkdir(exist_ok=True)
        output_dir = agent_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Create agent Python script
        if self.schema.get("dynamic_agent_creation", {}).get("enabled", False):
            template = self.schema["dynamic_agent_creation"]["agent_template"]
            
            script_content = template["script_header"].format(
                color=agent_info.get("color", "37"),  # Default to white
                agent_name=agent_type,
                agent_title=f"{agent_type.capitalize()} Agent",
                agent_role=agent_info["description"]
            )
            
            script_content += template["main_function"]
            
            script_path = self.base_dir / f"agent_{agent_type}.py"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable
            script_path.chmod(0o755)
            
            # Create bash task script
            bash_template = self.schema["dynamic_agent_creation"]["bash_task_template"]
            bash_content = bash_template.format(
                AGENT_TITLE=f"{agent_type.capitalize()} Agent",
                AGENT_DESCRIPTION=agent_info["description"],
                TASK_DESCRIPTION=f"process data related to the website and update the shared state",
                SAMPLE_OUTPUT=f"Sample output from {agent_type} agent",
                OUTPUT_FILENAME=f"{agent_type}_output.txt"
            )
            
            bash_path = agent_dir / f"{agent_type}_tasks.sh"
            with open(bash_path, 'w') as f:
                f.write(bash_content)
            
            # Make executable
            bash_path.chmod(0o755)
            
            # Create agent CLAUDE.md file with instructions
            claude_md = f"""# {agent_type.capitalize()} Agent Instructions

## Overview
You are the {agent_type.capitalize()} Agent in the Multi-Agent Website Cloning System.

## Role
{agent_info["description"]}

## Capabilities
{", ".join(agent_info.get("capabilities", []))}

## Dependencies
{", ".join(agent_info.get("dependencies", []))}

## Communication Protocol
Use the ../shared/communication_protocol.json file to communicate with other agents.

## Output
Place all outputs in the ./output directory.
"""
            
            claude_path = agent_dir / "CLAUDE.md"
            with open(claude_path, 'w') as f:
                f.write(claude_md)
            
            self.agents_created.append(agent_type)
            print(f"{COLORS['green']}✓ Created {agent_type} agent successfully{COLORS['reset']}")
            return True
        else:
            print(f"{COLORS['yellow']}Dynamic agent creation is disabled in schema.{COLORS['reset']}")
            return False
    
    def create_all_agents(self) -> None:
        """Create all agents defined in the schema"""
        print(f"{COLORS['blue']}Creating all agents...{COLORS['reset']}")
        
        for agent_type in self.schema["agent_types"]:
            self.create_agent(agent_type)
        
        print(f"{COLORS['green']}✓ All agents created successfully{COLORS['reset']}")
    
    def update_agent_status(self, agent_type: str, status: str) -> None:
        """Update the status of an agent in the communication protocol"""
        if agent_type not in self.schema["agent_types"]:
            print(f"{COLORS['red']}Unknown agent type: {agent_type}{COLORS['reset']}")
            return
        
        protocol_file = self.base_dir / "test_multi_agent" / "shared" / "communication_protocol.json"
        try:
            with open(protocol_file, 'r') as f:
                protocol_data = json.load(f)
            
            protocol_data["agent_states"][agent_type] = status
            
            with open(protocol_file, 'w') as f:
                json.dump(protocol_data, f, indent=2)
            
            print(f"{COLORS['green']}Updated {agent_type} status to {status}{COLORS['reset']}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"{COLORS['red']}Error updating agent status: {str(e)}{COLORS['reset']}")
    
    def log_cost(self, agent_type: str, tokens: int, cost: float, description: str) -> None:
        """Log API call cost for monitoring"""
        if not self.schema.get("cost_monitoring", {}).get("enabled", False):
            return
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "agent": agent_type,
            "tokens": tokens,
            "cost": cost,
            "description": description
        }
        
        self.cost_log.append(entry)
        
        # Write to log file
        cost_file = self.base_dir / self.schema["cost_monitoring"].get("log_file", "cost_monitor.log")
        with open(cost_file, 'a') as f:
            f.write(f"[{timestamp}] {agent_type}: {tokens} tokens, ${cost:.6f} - {description}\n")
        
        # Check if over threshold
        total_cost = sum(entry["cost"] for entry in self.cost_log)
        budget_limit = self.schema["cost_monitoring"].get("budget_limit", float('inf'))
        alert_threshold = self.schema["cost_monitoring"].get("alert_threshold", budget_limit * 0.8)
        
        if total_cost >= budget_limit:
            print(f"{COLORS['red']}⚠️ BUDGET LIMIT REACHED: ${total_cost:.2f} / ${budget_limit:.2f}{COLORS['reset']}")
            # Could potentially shut down the system here
        elif total_cost >= alert_threshold:
            print(f"{COLORS['yellow']}⚠️ BUDGET ALERT: ${total_cost:.2f} / ${budget_limit:.2f}{COLORS['reset']}")
    
    def generate_meta_prompt(self, agent_type: str, website_url: str, iteration: int, task: str) -> str:
        """Generate a meta-prompt for the agent based on the schema template"""
        if not self.schema.get("meta_prompting", {}).get("enabled", False):
            return ""
        
        agent_info = self.schema["agent_types"].get(agent_type, {})
        template = self.schema["meta_prompting"]["template"]
        
        prompt = template.format(
            AGENT_TITLE=f"{agent_type.capitalize()} Agent",
            AGENT_DESCRIPTION=agent_info.get("description", "perform tasks in the multi-agent system"),
            WEBSITE_URL=website_url,
            ITERATION_NUMBER=iteration,
            TASK_DESCRIPTION=task
        )
        
        # Log the cost estimate based on prompt length
        tokens = len(prompt.split()) + 50  # Rough estimate
        cost = tokens * 0.000001  # Assuming $0.001 per 1000 tokens
        self.log_cost(agent_type, tokens, cost, "Meta-prompt generation")
        
        return prompt
    
    def launch_agent(self, agent_type: str) -> Optional[subprocess.Popen]:
        """Launch an agent script in a new terminal window"""
        if agent_type not in self.schema["agent_types"]:
            print(f"{COLORS['red']}Unknown agent type: {agent_type}{COLORS['reset']}")
            return None
        
        script_path = self.base_dir / f"agent_{agent_type}.py"
        if not script_path.exists():
            print(f"{COLORS['red']}Agent script not found: {script_path}{COLORS['reset']}")
            return None
        
        try:
            # Update agent status
            self.update_agent_status(agent_type, "active")
            
            # Determine platform and launch terminal
            if sys.platform == 'darwin':  # macOS
                cmd = [
                    'osascript',
                    '-e',
                    f'''tell application "Terminal"
                        do script "cd {self.base_dir} && python3 {script_path}"
                        set custom title of front window to "{agent_type.capitalize()} Agent"
                    end tell'''
                ]
            elif sys.platform.startswith('linux'):
                cmd = [
                    'gnome-terminal',
                    '--title',
                    f"{agent_type.capitalize()} Agent",
                    '--',
                    'python3',
                    str(script_path)
                ]
            else:
                print(f"{COLORS['red']}Unsupported platform: {sys.platform}{COLORS['reset']}")
                return None
            
            process = subprocess.Popen(cmd)
            print(f"{COLORS['green']}Launched {agent_type} agent{COLORS['reset']}")
            return process
        except Exception as e:
            print(f"{COLORS['red']}Error launching agent: {str(e)}{COLORS['reset']}")
            self.update_agent_status(agent_type, "error")
            return None
    
    def launch_all_agents(self) -> Dict[str, subprocess.Popen]:
        """Launch all created agents in new terminal windows"""
        print(f"{COLORS['blue']}Launching all agents...{COLORS['reset']}")
        
        processes = {}
        for agent_type in self.agents_created:
            process = self.launch_agent(agent_type)
            if process:
                processes[agent_type] = process
            time.sleep(0.5)  # Small delay between launches
        
        print(f"{COLORS['green']}✓ Launched {len(processes)} agents{COLORS['reset']}")
        return processes


def main():
    """Main function for the dynamic agent creator"""
    parser = argparse.ArgumentParser(description="Create and manage dynamic agents based on schema")
    parser.add_argument("--schema", default="agent_schema.json", help="Path to the agent schema JSON file")
    parser.add_argument("--create-all", action="store_true", help="Create all agents defined in the schema")
    parser.add_argument("--create", type=str, help="Create a specific agent type")
    parser.add_argument("--launch-all", action="store_true", help="Launch all created agents")
    parser.add_argument("--launch", type=str, help="Launch a specific agent type")
    parser.add_argument("--init", action="store_true", help="Initialize the multi-agent system")
    args = parser.parse_args()
    
    creator = DynamicAgentCreator(args.schema)
    
    if args.init:
        creator.initialize_system()
    
    if args.create_all:
        creator.create_all_agents()
    elif args.create:
        creator.create_agent(args.create)
    
    if args.launch_all:
        creator.launch_all_agents()
    elif args.launch:
        creator.launch_agent(args.launch)

if __name__ == "__main__":
    main()