#!/usr/bin/env python3
"""
MCP Servers Update Script
-------------------------
This script maintains the self-serving feedback loop for MCP servers.
It updates the list of MCP servers from GitHub repositories and allows
searching for specific types of servers.

Created for the weed.th website cloning project.
Date: March 1, 2025
"""

import os
import sys
import requests
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.GREEN}=== {title} ==={Colors.NC}")

def print_info(message: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.NC}")

def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.NC}")

def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def get_mcp_servers_path() -> Path:
    """Get the path to the MCP Servers directory and ensure it exists."""
    mcp_dir = Path.home() / "MCP_Servers"
    mcp_dir.mkdir(exist_ok=True)
    return mcp_dir

def get_server_list_path() -> Path:
    """Get the path to the MCP servers list file."""
    return get_mcp_servers_path() / "mcp_servers.txt"

def read_server_list() -> List[str]:
    """Read the list of MCP servers from the file."""
    server_list_path = get_server_list_path()
    
    if not server_list_path.exists():
        # Create initial server list if it doesn't exist
        initial_repos = [
            "https://github.com/mendableai/firecrawl-mcp-server",
            "https://github.com/anthropics/anthropic-tools",
            "https://github.com/appcypher/awesome-mcp-servers"
        ]
        write_server_list(initial_repos)
        return initial_repos
    
    with open(server_list_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def write_server_list(servers: List[str]) -> None:
    """Write the list of MCP servers to the file."""
    server_list_path = get_server_list_path()
    
    with open(server_list_path, 'w') as f:
        for server in servers:
            f.write(f"{server}\n")

def fetch_awesome_mcp_servers() -> List[str]:
    """Fetch MCP server repositories from awesome-mcp-servers."""
    print_info("Fetching repositories from awesome-mcp-servers...")
    
    try:
        # GitHub API rate limits anonymous requests, so this might need authentication in production
        response = requests.get(
            "https://api.github.com/repos/appcypher/awesome-mcp-servers/contents/README.md",
            headers={"Accept": "application/vnd.github.v3.raw"}
        )
        response.raise_for_status()
        content = response.text
        
        # Extract GitHub repository links 
        # This is a simplified parser - a real one would use a proper markdown parser
        repos = []
        lines = content.split("\n")
        for line in lines:
            if "github.com" in line and "http" in line:
                # Extract URL using simple string operations
                start = line.find("http")
                end = line.find(")", start)
                if end == -1:
                    end = line.find(" ", start)
                if end == -1:
                    end = len(line)
                
                url = line[start:end]
                if url and "github.com" in url:
                    repos.append(url)
        
        print_success(f"Found {len(repos)} repositories")
        return repos
    
    except Exception as e:
        print_error(f"Failed to fetch repositories: {str(e)}")
        return []

def update_server_list() -> None:
    """Update the MCP servers list from awesome-mcp-servers."""
    print_header("Updating MCP Servers List")
    
    current_servers = read_server_list()
    print_info(f"Current list contains {len(current_servers)} repositories")
    
    # Fetch new servers from awesome-mcp-servers
    new_servers = fetch_awesome_mcp_servers()
    
    if not new_servers:
        print_warning("No new repositories found. Using backup method.")
        # Fallback to a static list for demonstration purposes
        # In a real implementation, this would use alternative sources
        fallback_repos = [
            "https://github.com/mendableai/firecrawl-mcp-server",
            "https://github.com/anthropics/anthropic-tools",
            "https://github.com/appcypher/awesome-mcp-servers",
            "https://github.com/modelcontextprotocol/sdk",
            "https://github.com/modelcontextprotocol/inspector"
        ]
        new_servers = fallback_repos
    
    # Merge lists and remove duplicates
    all_servers = list(set(current_servers + new_servers))
    all_servers.sort()
    
    # Write updated list
    write_server_list(all_servers)
    
    new_count = len(all_servers) - len(current_servers)
    if new_count > 0:
        print_success(f"Added {new_count} new repositories")
    else:
        print_info("No new repositories added")
    
    print_success(f"Updated server list saved to {get_server_list_path()}")

def search_servers(keyword: str) -> None:
    """Search for MCP servers containing the keyword."""
    print_header(f"Searching for MCP Servers: '{keyword}'")
    
    servers = read_server_list()
    results = [server for server in servers if keyword.lower() in server.lower()]
    
    if results:
        print_success(f"Found {len(results)} matches:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result}")
    else:
        print_warning(f"No repositories found matching '{keyword}'")

def list_servers() -> None:
    """List all MCP servers."""
    print_header("All MCP Servers")
    
    servers = read_server_list()
    for i, server in enumerate(servers, 1):
        print(f"{i}. {server}")
    
    print_success(f"Total: {len(servers)} repositories")

def update_metadata() -> None:
    """Update metadata about the MCP server list."""
    metadata_path = get_mcp_servers_path() / "metadata.txt"
    
    with open(metadata_path, 'w') as f:
        f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total repositories: {len(read_server_list())}\n")
        f.write("Maintained by: Claude Desktop for weed.th mapping project\n")
    
    print_success(f"Updated metadata at {metadata_path}")

def main() -> None:
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description="MCP Servers List Management")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update the list of MCP servers")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for MCP servers")
    search_parser.add_argument("keyword", help="Keyword to search for")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all MCP servers")
    
    args = parser.parse_args()
    
    if args.command == "update":
        update_server_list()
        update_metadata()
    elif args.command == "search":
        search_servers(args.keyword)
    elif args.command == "list":
        list_servers()
    else:
        # Default to listing servers if no command is provided
        parser.print_help()

if __name__ == "__main__":
    main()