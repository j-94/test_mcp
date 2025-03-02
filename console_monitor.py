#!/usr/bin/env python3
"""
Simple console-based monitor for the multi-agent system.
This provides real-time visibility into agent activities.
"""

import os
import sys
import json
import time
import curses
from pathlib import Path
from datetime import datetime

# Colors for different agents
COLORS = {
    "orchestrator": 5,  # Magenta
    "crawler": 2,      # Green
    "analysis": 4,      # Blue
    "implementation": 3, # Yellow
    "feedback": 6       # Cyan
}

# Base paths
BASE_DIR = Path.cwd()
MULTI_AGENT_DIR = BASE_DIR / "test_multi_agent"
SHARED_DIR = MULTI_AGENT_DIR / "shared"
PROTOCOL_FILE = SHARED_DIR / "communication_protocol.json"
CONFIG_FILE = SHARED_DIR / "config.json"

def load_agent_status():
    """Load the current agent status from the protocol file."""
    try:
        if not PROTOCOL_FILE.exists():
            return {
                "agent_states": {
                    "orchestrator": "unknown",
                    "crawler": "unknown",
                    "analysis": "unknown",
                    "implementation": "unknown",
                    "feedback": "unknown"
                },
                "project_state": "unknown",
                "current_iteration": 0,
                "completion_percentage": 0
            }
        
        with open(PROTOCOL_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {
            "agent_states": {
                "orchestrator": f"error: {e}",
                "crawler": "unknown",
                "analysis": "unknown",
                "implementation": "unknown",
                "feedback": "unknown"
            },
            "project_state": "error",
            "current_iteration": 0,
            "completion_percentage": 0
        }

def get_latest_agent_outputs():
    """Get the most recent outputs from each agent."""
    outputs = {}
    for agent in ["orchestrator", "crawler", "analysis", "implementation", "feedback"]:
        output_dir = MULTI_AGENT_DIR / agent / "output"
        if output_dir.exists():
            files = list(output_dir.glob("*"))
            if files:
                latest_file = max(files, key=os.path.getmtime)
                try:
                    with open(latest_file, 'r') as f:
                        content = f.read()
                    outputs[agent] = {
                        "file": latest_file.name,
                        "time": datetime.fromtimestamp(latest_file.stat().st_mtime).strftime("%H:%M:%S"),
                        "content": content[:500] + "..." if len(content) > 500 else content
                    }
                except Exception as e:
                    outputs[agent] = {
                        "file": latest_file.name,
                        "time": "unknown",
                        "content": f"Error reading file: {e}"
                    }
    return outputs

def draw_ui(stdscr):
    """Draw the curses UI."""
    # Setup colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, 8):
        curses.init_pair(i, i, -1)
    
    # Hide cursor
    curses.curs_set(0)
    
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    while True:
        try:
            # Clear screen
            stdscr.clear()
            
            # Get current status
            status = load_agent_status()
            outputs = get_latest_agent_outputs()
            
            # Draw header
            header = "MULTI-AGENT SYSTEM MONITOR"
            stdscr.addstr(0, (max_x - len(header)) // 2, header, curses.A_BOLD)
            
            # Draw system status
            stdscr.addstr(2, 2, f"System Status: ", curses.A_BOLD)
            state_color = curses.color_pair(2) if status["project_state"] == "complete" else curses.color_pair(3)
            stdscr.addstr(2, 17, status["project_state"].upper(), state_color | curses.A_BOLD)
            
            stdscr.addstr(3, 2, f"Current Iteration: {status['current_iteration']}")
            stdscr.addstr(4, 2, f"Completion: {status['completion_percentage']}%")
            
            # Draw website URL
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                url = config.get("website_url", "unknown")
            except:
                url = "unknown"
            
            stdscr.addstr(5, 2, f"Target Website: {url}")
            
            # Draw progress bar
            bar_width = max_x - 16
            progress = int(bar_width * status["completion_percentage"] / 100)
            stdscr.addstr(6, 2, "Progress: [")
            for i in range(bar_width):
                if i < progress:
                    stdscr.addstr("#", curses.color_pair(2))
                else:
                    stdscr.addstr(" ")
            stdscr.addstr("]")
            
            # Draw agent status table
            stdscr.addstr(8, 2, "Agent Status:", curses.A_BOLD)
            for i, (agent, state) in enumerate(status["agent_states"].items()):
                color = curses.color_pair(COLORS.get(agent, 7))
                stdscr.addstr(9 + i, 4, f"{agent.capitalize():15}", color | curses.A_BOLD)
                
                state_color = curses.color_pair(2) if state in ["complete", "active"] else curses.color_pair(7)
                stdscr.addstr(9 + i, 20, f"{state.upper():10}", state_color)
                
                # Show latest output file if available
                if agent in outputs:
                    output = outputs[agent]
                    stdscr.addstr(9 + i, 32, f"Last output: {output['file']} at {output['time']}")
            
            # Draw latest outputs
            row = 15
            stdscr.addstr(row, 2, "Latest Agent Outputs:", curses.A_BOLD)
            row += 1
            
            for agent, output in outputs.items():
                if row + 5 >= max_y:
                    break
                
                color = curses.color_pair(COLORS.get(agent, 7))
                stdscr.addstr(row, 2, f"{agent.capitalize()} Output:", color | curses.A_BOLD)
                row += 1
                
                # Draw a box for the output
                stdscr.addstr(row, 2, "┌" + "─" * (max_x - 6) + "┐")
                row += 1
                
                # Show content with word wrap
                content = output["content"]
                lines = content.split("\n")
                for line in lines[:3]:  # Show up to 3 lines
                    if row >= max_y - 3:
                        break
                    # Truncate long lines
                    if len(line) > max_x - 8:
                        line = line[:max_x - 11] + "..."
                    stdscr.addstr(row, 2, "│ " + line + " " * (max_x - 6 - len(line)) + "│")
                    row += 1
                
                stdscr.addstr(row, 2, "└" + "─" * (max_x - 6) + "┘")
                row += 2
            
            # Add instructions at bottom
            stdscr.addstr(max_y - 2, 2, "Press 'q' to quit, 'r' to refresh, 'c' to run crawler, 'i' to run implementation", curses.A_BOLD)
            
            # Refresh the screen
            stdscr.refresh()
            
            # Check for user input with timeout
            stdscr.timeout(1000)  # 1 second timeout
            key = stdscr.getch()
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Just refresh, which happens on the next loop
                pass
            elif key == ord('c'):
                # Run crawler agent
                stdscr.addstr(max_y - 3, 2, "Running crawler agent...", curses.color_pair(2) | curses.A_BOLD)
                stdscr.refresh()
                os.system(f"cd {BASE_DIR} && bash {MULTI_AGENT_DIR}/crawler/crawler_tasks.sh > /dev/null 2>&1 &")
            elif key == ord('i'):
                # Run implementation agent
                stdscr.addstr(max_y - 3, 2, "Running implementation agent...", curses.color_pair(3) | curses.A_BOLD)
                stdscr.refresh()
                os.system(f"cd {BASE_DIR} && bash {MULTI_AGENT_DIR}/implementation/implementation_tasks.sh > /dev/null 2>&1 &")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            # Show error and continue
            stdscr.clear()
            stdscr.addstr(0, 0, f"Error: {str(e)}", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(1, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()

def main():
    """Main function to start the monitor."""
    # Ensure communication protocol exists
    os.makedirs(SHARED_DIR, exist_ok=True)
    if not PROTOCOL_FILE.exists():
        # Create default protocol
        default_protocol = {
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
        
        with open(PROTOCOL_FILE, 'w') as f:
            json.dump(default_protocol, f, indent=2)
    
    # Start curses application
    curses.wrapper(draw_ui)

if __name__ == "__main__":
    main()