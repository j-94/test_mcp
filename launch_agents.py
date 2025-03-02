#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json
from pathlib import Path

# Configuration
AGENTS = {
    'crawler': {
        'color': '32',  # Green
        'title': 'Crawler Agent',
        'role': 'Handles website crawling and data extraction'
    },
    'analyzer': {
        'color': '34',  # Blue
        'title': 'Analyzer Agent',
        'role': 'Analyzes website structure and patterns'
    },
    'orchestrator': {
        'color': '35',  # Purple
        'title': 'Orchestrator Agent',
        'role': 'Coordinates all agents and manages workflow'
    }
}

def create_agent_script(agent_name, config):
    """Create the individual agent script."""
    script_path = Path(f'agent_{agent_name}.py')
    
    with open(script_path, 'w') as f:
        f.write(f'''#!/usr/bin/env python3
import sys
import time
import json
from pathlib import Path

COLOR = "{config['color']}"
AGENT_NAME = "{agent_name}"
AGENT_TITLE = "{config['title']}"
AGENT_ROLE = "{config['role']}"

def print_colored(text):
    """Print colored text."""
    print(f"\\033[{{COLOR}}m{{text}}\\033[0m")

def main():
    print_colored(f"=== {{AGENT_TITLE}} ===")
    print_colored(f"Role: {{AGENT_ROLE}}")
    
    while True:
        try:
            # Read from shared state file
            try:
                with open('shared_state.json', 'r') as f:
                    state = json.load(f)
            except FileNotFoundError:
                state = {{'messages': []}}
            
            # Process any new messages
            for msg in state.get('messages', []):
                if msg.get('to') == AGENT_NAME and not msg.get('processed'):
                    print_colored(f"Received: {{msg['content']}}")
                    msg['processed'] = True
            
            # Get user input
            user_input = input(f"\\033[{{COLOR}}m{{AGENT_NAME}}> \\033[0m")
            
            if user_input.lower() == 'exit':
                break
            
            # Add message to shared state
            state['messages'].append({{
                'from': AGENT_NAME,
                'to': 'all',
                'content': user_input,
                'timestamp': time.time(),
                'processed': False
            }})
            
            # Write back to shared state
            with open('shared_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            time.sleep(0.1)  # Prevent busy waiting
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print_colored(f"Error: {{e}}")
            time.sleep(1)

if __name__ == '__main__':
    main()
''')
    
    # Make the script executable
    script_path.chmod(0o755)
    return script_path

def create_shared_state():
    """Create the initial shared state file."""
    if not Path('shared_state.json').exists():
        with open('shared_state.json', 'w') as f:
            json.dump({
                'messages': [],
                'status': 'running',
                'last_update': time.time()
            }, f, indent=2)

def launch_agent_terminal(agent_name, script_path):
    """Launch a new terminal window running the agent script."""
    if sys.platform == 'darwin':  # macOS
        cmd = [
            'osascript',
            '-e',
            f'''tell application "Terminal"
                do script "cd {os.getcwd()} && python3 {script_path}"
                set custom title of front window to "{AGENTS[agent_name]['title']}"
            end tell'''
        ]
    elif sys.platform.startswith('linux'):
        cmd = [
            'gnome-terminal',
            '--title',
            AGENTS[agent_name]['title'],
            '--',
            'python3',
            str(script_path)
        ]
    else:
        print(f"Unsupported platform: {sys.platform}")
        return
    
    subprocess.Popen(cmd)

def main():
    # Create shared state file
    create_shared_state()
    
    # Create and launch each agent
    for agent_name, config in AGENTS.items():
        script_path = create_agent_script(agent_name, config)
        launch_agent_terminal(agent_name, script_path)
        time.sleep(0.5)  # Small delay between launching terminals
    
    print("All agents launched. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Update shared state to signal shutdown
        with open('shared_state.json', 'w') as f:
            json.dump({
                'messages': [],
                'status': 'shutdown',
                'last_update': time.time()
            }, f, indent=2)
        print("\nShutting down agents...")

if __name__ == '__main__':
    main() 