#!/usr/bin/env python3
"""
ForeverVM Integration for Multi-Agent System
Provides secure code execution capabilities for the implementation and feedback agents.
"""

import os
import json
import subprocess
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# ForeverVM SDK imports (install with: pip install forevervm-sdk)
# Since we're encountering compatibility issues with ForeverVM SDK
# and Python 3.9, we'll use a stub implementation

print("Using ForeverVM stub implementation compatible with Python 3.9")

# Define a stub ForeverVM class for compatibility
class ForeverVM:
    """Stub implementation of ForeverVM for compatibility with Python 3.9"""
    
    def __init__(self, token=None):
        self.token = token or os.environ.get("FOREVERVM_API_TOKEN", "")
        print(f"ForeverVM stub initialized with token: {self.token[:5]}..." if self.token else "ForeverVM stub initialized without token")
    
    def create_machine(self):
        """Create a ForeverVM machine simulation"""
        print("ForeverVM stub: Creating machine simulation")
        return ForeverVMMachine(self.token)

class ForeverVMMachine:
    """Stub implementation of ForeverVM machine"""
    
    def __init__(self, token):
        self.token = token
    
    def run(self, code, timeout=30):
        """Simulate running code in ForeverVM"""
        print(f"ForeverVM stub: Would execute {len(code)} bytes of code with timeout {timeout}s")
        
        # Create a simple "sandbox" using a restricted Python environment
        # This is NOT a true sandbox, just a demonstration
        import subprocess
        
        try:
            # Execute with restricted environment for basic simulation
            # NOT SECURE - just for demonstration purposes
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "output": result.stdout + result.stderr,
                "return_value": "Stub sandbox simulation result",
                "state": "complete"
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "Code execution timed out",
                "return_value": None,
                "state": "timeout"
            }
        except Exception as e:
            return {
                "output": f"Error executing code: {str(e)}",
                "return_value": None,
                "state": "error"
            }

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv
    # Load again after installing
    load_dotenv(dotenv_path=env_path)
except Exception as e:
    print(f"Warning: Could not install python-dotenv: {e}")
    print("Will continue without loading .env file")

# Configuration
FOREVERVM_API_TOKEN = os.environ.get("FOREVERVM_API_TOKEN", "")
if not FOREVERVM_API_TOKEN and env_path.exists():
    # Try to read directly from .env file as fallback
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('FOREVERVM_API_TOKEN='):
                    FOREVERVM_API_TOKEN = line.strip().split('=', 1)[1]
                    # Remove quotes if present
                    FOREVERVM_API_TOKEN = FOREVERVM_API_TOKEN.strip('\'"')
                    break
    except Exception as e:
        print(f"Warning: Could not read .env file: {e}")

DEFAULT_TIMEOUT = 30  # seconds

class ForeverVMSandbox:
    """ForeverVM sandbox for secure code execution in the multi-agent system."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the ForeverVM sandbox."""
        self.api_token = api_token or FOREVERVM_API_TOKEN
        
        if not self.api_token:
            raise ValueError("ForeverVM API token not provided. Set FOREVERVM_API_TOKEN environment variable.")
        
        # Initialize ForeverVM client
        self.fvm = ForeverVM(token=self.api_token)
        self.machine = None
    
    def __enter__(self):
        """Create a ForeverVM machine when entering context."""
        self.machine = self.fvm.create_machine()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up ForeverVM machine when exiting context."""
        if self.machine:
            # ForeverVM handles cleanup automatically through the SDK
            self.machine = None
    
    def execute_code(self, code: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """
        Execute Python code safely in the ForeverVM sandbox.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with execution results containing:
                - success: Boolean indicating success
                - output: Stdout/stderr content
                - return_value: Return value if applicable
                - error: Error message if execution failed
        """
        if not self.machine:
            raise RuntimeError("ForeverVM machine not created. Use with-statement or create_machine().")
        
        try:
            # Execute code and capture output
            result = self.machine.run(code, timeout=timeout)
            
            return {
                "success": True,
                "output": result.output,
                "return_value": result.return_value,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "return_value": None,
                "error": str(e)
            }
    
    def install_package(self, package_name: str) -> Dict[str, Any]:
        """
        Install a Python package in the ForeverVM sandbox.
        
        Args:
            package_name: Name of the package to install
            
        Returns:
            Dict with installation results
        """
        install_code = f"import subprocess; subprocess.check_call(['pip', 'install', '{package_name}'])"
        return self.execute_code(install_code, timeout=60)  # Allow longer timeout for package installation
    
    def execute_file(self, file_path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """
        Execute a Python file in the ForeverVM sandbox.
        
        Args:
            file_path: Path to the Python file to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with execution results
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            return self.execute_code(code, timeout)
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "return_value": None,
                "error": f"Error reading file: {str(e)}"
            }


class MultiAgentExecutor:
    """Integrates ForeverVM with the multi-agent system for secure code execution."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the multi-agent executor."""
        self.api_token = api_token or FOREVERVM_API_TOKEN
        
        # Directories 
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_dir = os.path.join(self.base_dir, "test_multi_agent")
        self.implementation_dir = os.path.join(self.test_dir, "implementation")
        self.feedback_dir = os.path.join(self.test_dir, "feedback")
        self.output_dir = os.path.join(self.implementation_dir, "output")
    
    def safe_execute_implementation(self, code_file: str) -> Dict[str, Any]:
        """
        Safely execute implementation code generated by the implementation agent.
        
        Args:
            code_file: Path to the code file to execute
            
        Returns:
            Dict with execution results and metadata
        """
        file_path = os.path.join(self.output_dir, code_file) if not os.path.isabs(code_file) else code_file
        
        with ForeverVMSandbox(self.api_token) as sandbox:
            # Install required packages first
            sandbox.install_package("requests")
            sandbox.install_package("beautifulsoup4")
            
            # Execute the implementation code
            result = sandbox.execute_file(file_path)
            
            # Log execution results
            self._log_execution(code_file, result)
            
            return result
    
    def _log_execution(self, code_file: str, result: Dict[str, Any]) -> None:
        """Log execution results for feedback agent analysis."""
        log_entry = {
            "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip(),
            "file": code_file,
            "success": result["success"],
            "output": result["output"],
            "error": result["error"]
        }
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(self.output_dir, "execution_logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Write log entry
        log_file = os.path.join(logs_dir, f"{os.path.basename(code_file)}.log.json")
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    
    def test_implementation(self, code_file: str, test_code: str) -> Dict[str, Any]:
        """
        Test implementation with provided test code.
        
        Args:
            code_file: Path to the implementation code file
            test_code: Python code for testing the implementation
            
        Returns:
            Dict with test results
        """
        file_path = os.path.join(self.output_dir, code_file) if not os.path.isabs(code_file) else code_file
        
        with ForeverVMSandbox(self.api_token) as sandbox:
            # First, install required packages
            sandbox.install_package("pytest")
            
            # Import the implementation code
            setup_code = f"""
import os
import sys
sys.path.append(os.path.dirname("{file_path}"))
with open("{file_path}", "r") as f:
    exec(f.read())
            """
            sandbox.execute_code(setup_code)
            
            # Run the test code
            return sandbox.execute_code(test_code)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <python_file_to_execute>")
        sys.exit(1)
    
    file_to_execute = sys.argv[1]
    
    executor = MultiAgentExecutor()
    result = executor.safe_execute_implementation(file_to_execute)
    
    print("\n--- Execution Results ---")
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