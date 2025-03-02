#!/usr/bin/env python3
import sys
import time
import json
from pathlib import Path

COLOR = "35"
AGENT_NAME = "orchestrator"
AGENT_TITLE = "Orchestrator Agent"
AGENT_ROLE = "Coordinates all agents and manages workflow"

def print_colored(text):
    """Print colored text."""
    print(f"\033[{COLOR}m{text}\033[0m")

def main():
    print_colored(f"=== {AGENT_TITLE} ===")
    print_colored(f"Role: {AGENT_ROLE}")
    
    while True:
        try:
            # Read from shared state file
            try:
                with open('shared_state.json', 'r') as f:
                    state = json.load(f)
            except FileNotFoundError:
                state = {'messages': []}
            
            # Process any new messages
            for msg in state.get('messages', []):
                if msg.get('to') == AGENT_NAME and not msg.get('processed'):
                    print_colored(f"Received: {msg['content']}")
                    msg['processed'] = True
            
            # Get user input
            user_input = input(f"\033[{COLOR}m{AGENT_NAME}> \033[0m")
            
            if user_input.lower() == 'exit':
                break
            
            # Add message to shared state
            state['messages'].append({
                'from': AGENT_NAME,
                'to': 'all',
                'content': user_input,
                'timestamp': time.time(),
                'processed': False
            })
            
            # Write back to shared state
            with open('shared_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            time.sleep(0.1)  # Prevent busy waiting
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print_colored(f"Error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
