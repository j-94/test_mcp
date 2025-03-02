#!/usr/bin/env python3
"""
Simple UI for ForeverVM Sandbox Testing
A minimal interface to test ForeverVM sandbox functionality
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Try to import ForeverVM integration
try:
    from integrate_forevervm import ForeverVMSandbox
    FOREVERVM_AVAILABLE = True
    print("ForeverVM integration available")
except ImportError:
    FOREVERVM_AVAILABLE = False
    print("ForeverVM integration not available")

# Load environment variables from .env file
env_path = project_root / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    print(f"Loaded environment from .env file")
    print(f"ForeverVM API Token: {os.environ.get('FOREVERVM_API_TOKEN', '')[:5]}... (set)")

def execute_in_sandbox(code):
    """Execute Python code in a ForeverVM sandbox."""
    print(f"Executing code in ForeverVM sandbox:\n{code}\n")
    
    if not FOREVERVM_AVAILABLE:
        return {
            "success": False,
            "error": "ForeverVM integration not available"
        }
    
    try:
        with ForeverVMSandbox() as sandbox:
            result = sandbox.execute_code(code)
            return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_sandbox():
    """Run a simple test in the ForeverVM sandbox."""
    test_code = """
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print("ForeverVM sandbox is working!")

# Return a success message
"Sandbox test successful"
"""
    return execute_in_sandbox(test_code)

def show_menu():
    """Display the main menu."""
    print("\n========= ForeverVM Sandbox Tester =========")
    print("1. Test sandbox connection")
    print("2. Execute custom code")
    print("3. Show environment")
    print("4. Exit")
    print("===========================================")
    
    choice = input("Enter your choice (1-4): ")
    return choice

def handle_custom_code():
    """Handle custom code execution."""
    print("\n--- Enter Python code to execute (type 'done' on a new line to finish) ---")
    code_lines = []
    
    while True:
        line = input()
        if line.strip().lower() == 'done':
            break
        code_lines.append(line)
    
    code = "\n".join(code_lines)
    if not code.strip():
        print("No code provided.")
        return
    
    result = execute_in_sandbox(code)
    
    print("\n--- Execution Result ---")
    if result["success"]:
        print("✅ Code executed successfully")
        print("\nOutput:")
        print(result["output"])
        if result["return_value"]:
            print("\nReturn Value:")
            print(result["return_value"])
    else:
        print("❌ Execution failed")
        print("\nError:")
        print(result["error"])

def show_environment():
    """Show environment information."""
    print("\n--- Environment Information ---")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"ForeverVM available: {FOREVERVM_AVAILABLE}")
    print(f"ForeverVM API Token: {'Set' if 'FOREVERVM_API_TOKEN' in os.environ else 'Not set'}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check for required directories
    multi_agent_dir = project_root / "test_multi_agent"
    print(f"Multi-agent directory exists: {multi_agent_dir.exists()}")
    
    # Check for required files
    integrate_vm_path = project_root / "integrate_forevervm.py"
    print(f"ForeverVM integration exists: {integrate_vm_path.exists()}")

def main():
    """Main function."""
    print("Welcome to the ForeverVM Sandbox Tester")
    print(f"ForeverVM integration {'available' if FOREVERVM_AVAILABLE else 'not available'}")
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            print("\nTesting ForeverVM sandbox...")
            result = test_sandbox()
            
            print("\n--- Test Result ---")
            if result["success"]:
                print("✅ Sandbox test successful")
                print("\nOutput:")
                print(result["output"])
            else:
                print("❌ Sandbox test failed")
                print("\nError:")
                print(result["error"])
        
        elif choice == '2':
            handle_custom_code()
        
        elif choice == '3':
            show_environment()
        
        elif choice == '4':
            print("\nExiting ForeverVM Sandbox Tester. Goodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()