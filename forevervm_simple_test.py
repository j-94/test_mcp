#!/usr/bin/env python3
"""
Very simple ForeverVM test
"""

import os
import sys

# Load environment from .env file
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    print(f"Loaded API token: {os.environ.get('FOREVERVM_API_TOKEN', '')[:5]}...")

# Test a simple ForeverVM-like sandbox
def run_in_sandbox(code):
    """Run code in a simulated sandbox"""
    print(f"\nRunning code in simulated sandbox:")
    print("-" * 40)
    print(code)
    print("-" * 40)
    
    try:
        # This is NOT a true sandbox but a simple demonstration
        result = {}
        exec(code, {'result': result, 'print': print})
        print(f"Execution successful")
        return True
    except Exception as e:
        print(f"Execution failed: {e}")
        return False

# Main function
def main():
    print("ForeverVM Simulation Test")
    
    # Test code in sandbox
    test_code = """
import sys
import platform
import os

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current directory: {os.getcwd()}")
print("Sandbox test running!")
    
# Set some result value
result['success'] = True
result['message'] = "Code executed successfully"
"""
    
    success = run_in_sandbox(test_code)
    
    if success:
        print("\nTest complete! The system is working with a simulated ForeverVM sandbox.")
        print("In a real implementation, this would use the actual ForeverVM service.")
    else:
        print("\nTest failed. There may be an issue with the simulated sandbox.")

if __name__ == "__main__":
    main()