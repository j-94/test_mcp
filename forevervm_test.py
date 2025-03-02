#!/usr/bin/env python3
"""
Simple ForeverVM Test Script
Tests the ForeverVM integration with a basic sandbox test
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('forevervm_test')

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / '.env'

# Load environment variables
def load_environment():
    """Load environment variables from .env file"""
    if ENV_PATH.exists():
        logger.info(f"Loading environment from {ENV_PATH}")
        with open(ENV_PATH, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    # Mask sensitive values in logs
                    if 'TOKEN' in key or 'KEY' in key:
                        masked_value = value[:5] + '...' if len(value) > 5 else '***'
                        logger.info(f"Set {key}={masked_value}")
                    else:
                        logger.info(f"Set {key}={value}")
    else:
        logger.warning(f".env file not found at {ENV_PATH}")

# Main function
def main():
    """Test ForeverVM sandbox"""
    # Load environment variables
    load_environment()
    
    # Try to import ForeverVM integration
    try:
        from integrate_forevervm import ForeverVMSandbox
        logger.info("ForeverVM integration available")
        
        # Test sandbox
        logger.info("Testing ForeverVM sandbox...")
        
        with ForeverVMSandbox() as sandbox:
            # Simple test code
            test_code = """
import sys
import platform
import os

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current directory: {os.getcwd()}")
print("ForeverVM sandbox is working!")

# Return a success message
"Sandbox test successful"
"""
            logger.info("Executing test code in ForeverVM sandbox...")
            result = sandbox.execute_code(test_code)
            
            if result["success"]:
                logger.info("ForeverVM sandbox test successful")
                logger.info(f"Output: {result['output']}")
                if result["return_value"]:
                    logger.info(f"Return value: {result['return_value']}")
            else:
                logger.error(f"ForeverVM sandbox test failed: {result['error']}")
                
            # Test installing a package
            logger.info("Testing package installation in ForeverVM sandbox...")
            install_result = sandbox.install_package("requests")
            
            if install_result["success"]:
                logger.info("Package installation successful")
                
                # Test using the installed package
                test_requests = """
import requests

response = requests.get("https://example.com")
print(f"Status code: {response.status_code}")
print(f"Content length: {len(response.text)} bytes")

# Return response info
{"status_code": response.status_code, "content_length": len(response.text)}
"""
                logger.info("Testing installed package...")
                req_result = sandbox.execute_code(test_requests)
                
                if req_result["success"]:
                    logger.info("Package test successful")
                    logger.info(f"Output: {req_result['output']}")
                    logger.info(f"Return value: {req_result['return_value']}")
                else:
                    logger.error(f"Package test failed: {req_result['error']}")
            else:
                logger.error(f"Package installation failed: {install_result['error']}")
    
    except ImportError:
        logger.error("ForeverVM integration not available")
        logger.error("Please check that the ForeverVM SDK is installed and the integrate_forevervm.py file exists")
    except Exception as e:
        logger.error(f"Error testing ForeverVM sandbox: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()