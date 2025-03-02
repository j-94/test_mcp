#!/bin/bash
#
# Multi-Agent System Launcher with Visual Monitor
#

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Gather terminal size for better UI
TERM_WIDTH=$(tput cols)
TERM_HEIGHT=$(tput lines)

# Base directories
BASE_DIR="$(pwd)"
MULTI_AGENT_DIR="${BASE_DIR}/test_multi_agent"
SHARED_DIR="${MULTI_AGENT_DIR}/shared"

# Print centered header
print_header() {
  local text="$1"
  local padding=$(( (TERM_WIDTH - ${#text}) / 2 ))
  printf "%${padding}s" ""
  echo -e "${BLUE}${text}${NC}"
}

# Print agent status
print_agent_status() {
  local agent="$1"
  local status="$2"
  local agent_color
  
  case "$agent" in
    "orchestrator") agent_color="${PURPLE}" ;;
    "crawler") agent_color="${GREEN}" ;;
    "analysis") agent_color="${BLUE}" ;;
    "implementation") agent_color="${YELLOW}" ;;
    "feedback") agent_color="${CYAN}" ;;
    *) agent_color="${NC}" ;;
  esac
  
  local status_color
  case "$status" in
    "active") status_color="${GREEN}" ;;
    "idle") status_color="${BLUE}" ;;
    "error") status_color="${RED}" ;;
    "complete") status_color="${CYAN}" ;;
    *) status_color="${NC}" ;;
  esac
  
  printf "${agent_color}%-15s${NC} : ${status_color}%-10s${NC}\n" "${agent^}" "$status"
}

# Print progress bar
print_progress() {
  local percent=$1
  local width=$(( TERM_WIDTH - 10 ))
  local num_chars=$(( width * percent / 100 ))
  
  printf "["
  for ((i=0; i<num_chars; i++)); do
    printf "#"
  done
  for ((i=num_chars; i<width; i++)); do
    printf " "
  done
  printf "] %3d%%\n" $percent
}

# Clear screen and print header
clear_and_print_header() {
  clear
  echo -e "${BLUE}=========================================================${NC}"
  print_header "MULTI-AGENT SYSTEM WITH FOREVERVM"
  echo -e "${BLUE}=========================================================${NC}"
  echo ""
}

# Initialize the system
initialize_system() {
  echo -e "${YELLOW}Initializing the multi-agent system...${NC}"
  
  # Ensure the shared directory exists
  mkdir -p "${SHARED_DIR}"
  
  # Initialize or update the config.json
  if [ ! -f "${SHARED_DIR}/config.json" ]; then
    echo '{
  "website_url": "https://example.com"
}' > "${SHARED_DIR}/config.json"
  fi
  
  # Initialize or update the communication protocol
  if [ ! -f "${SHARED_DIR}/communication_protocol.json" ]; then
    echo '{
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
}' > "${SHARED_DIR}/communication_protocol.json"
  else
    # Reset the protocol for a fresh run
    python3 -c 'import json, time; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "r"); data = json.load(f); f.close(); for agent in data["agent_states"]: data["agent_states"][agent] = "idle"; data["project_state"] = "initializing"; data["current_iteration"] = 0; data["completion_percentage"] = 0; data["error_states"] = {}; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "w"); json.dump(data, f, indent=2); f.close()'
  fi
  
  # Ensure output directories exist for all agents
  for agent in orchestrator crawler analysis implementation feedback; do
    mkdir -p "${MULTI_AGENT_DIR}/${agent}/output"
  done
  
  echo -e "${GREEN}System initialized successfully.${NC}"
}

# Update agent status (simulated for demo)
update_agent_status() {
  local agent="$1"
  local status="$2"
  
  python3 -c 'import json; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "r"); data = json.load(f); f.close(); data["agent_states"]["'"$agent"'"] = "'"$status"'"; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "w"); json.dump(data, f, indent=2); f.close()'
}

# Update project state (simulated for demo)
update_project_state() {
  local state="$1"
  local percentage="$2"
  
  python3 -c 'import json; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "r"); data = json.load(f); f.close(); data["project_state"] = "'"$state"'"; data["completion_percentage"] = '"$percentage"'; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "w"); json.dump(data, f, indent=2); f.close()'
}

# Simulated process for demonstration
run_simulated_process() {
  local url="$1"
  local iterations="${2:-1}"
  
  # Initialize system
  initialize_system
  
  # Update the config with the URL
  python3 -c 'import json; f = open("'"${SHARED_DIR}"'/config.json", "r"); data = json.load(f); f.close(); data["website_url"] = "'"$url"'"; f = open("'"${SHARED_DIR}"'/config.json", "w"); json.dump(data, f, indent=2); f.close()'
  
  # Start the orchestrator
  update_agent_status "orchestrator" "active"
  update_project_state "planning" 5
  sleep 2
  
  # Run the specified number of iterations
  for (( iter=1; iter<=iterations; iter++ )); do
    echo -e "\n${YELLOW}Starting iteration $iter of $iterations...${NC}"
    
    # Update project state to reflect the current iteration
    python3 -c 'import json; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "r"); data = json.load(f); f.close(); data["current_iteration"] = '"$iter"'; f = open("'"${SHARED_DIR}"'/communication_protocol.json", "w"); json.dump(data, f, indent=2); f.close()'
    
    # Crawler phase
    update_agent_status "crawler" "active"
    update_project_state "crawling" 10
    sleep 2
    
    # Create sample crawler output
    echo "<html><head><title>Extracted from $url (Iteration $iter)</title></head><body><h1>$url</h1><p>This is a demonstration of the Crawler Agent - Iteration $iter.</p></body></html>" > "${MULTI_AGENT_DIR}/crawler/output/extracted_site_iter${iter}.html"
    echo -e "${GREEN}Crawler extracted site structure${NC}"
    update_agent_status "crawler" "complete"
    
    # Analysis phase
    update_agent_status "analysis" "active"
    update_project_state "analyzing" 30
    sleep 3
    
    # Create sample analysis output
    echo "# Website Analysis Report - Iteration $iter
    
## Structure
- Header with logo and navigation
- Main content area
- Sidebar with filters
- Footer with links

## Components
- Navigation menu: 5 items
- Search box
- Product cards: 8 items
- Filter panel
- Footer links: 4 sections

## Styling
- Primary color: #336699
- Secondary color: #993366
- Font: Arial, sans-serif
- Responsive layout
" > "${MULTI_AGENT_DIR}/analysis/output/analysis_report_iter${iter}.md"
    echo -e "${GREEN}Analysis completed site structure analysis${NC}"
    update_agent_status "analysis" "complete"
    
    # Implementation phase
    update_agent_status "implementation" "active"
    update_project_state "implementing" 60
    sleep 4
    
    # Create sample implementation output
    echo "<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Clone of $url (Iteration $iter)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }
        header {
            background-color: #336699;
            color: white;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
        }
        nav ul {
            display: flex;
            list-style: none;
            gap: 1rem;
        }
        main {
            display: flex;
            padding: 1rem;
        }
        .content {
            flex: 3;
        }
        .sidebar {
            flex: 1;
            background-color: #f0f0f0;
            padding: 1rem;
        }
        footer {
            background-color: #333;
            color: white;
            padding: 1rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <header>
        <div class=\"logo\">LOGO</div>
        <nav>
            <ul>
                <li><a href=\"#\">Home</a></li>
                <li><a href=\"#\">Products</a></li>
                <li><a href=\"#\">Services</a></li>
                <li><a href=\"#\">About</a></li>
                <li><a href=\"#\">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <div class=\"content\">
            <h1>Welcome to the Clone Site</h1>
            <p>This is a demonstration of the Implementation Agent - Iteration $iter.</p>
            <div class=\"products\">
                <div class=\"product\">Product 1</div>
                <div class=\"product\">Product 2</div>
                <div class=\"product\">Product 3</div>
                <div class=\"product\">Product 4</div>
            </div>
        </div>
        <div class=\"sidebar\">
            <h2>Filters</h2>
            <form>
                <div>
                    <label>Category</label>
                    <select>
                        <option>All</option>
                        <option>Category 1</option>
                        <option>Category 2</option>
                    </select>
                </div>
                <div>
                    <label>Price Range</label>
                    <input type=\"range\" min=\"0\" max=\"100\">
                </div>
            </form>
        </div>
    </main>
    <footer>
        <p>© 2025 Clone Site - Iteration $iter</p>
    </footer>
</body>
</html>" > "${MULTI_AGENT_DIR}/implementation/output/clone_site_iter${iter}.html"
    echo -e "${GREEN}Implementation created site clone${NC}"
    update_agent_status "implementation" "complete"
    
    # Feedback phase
    update_agent_status "feedback" "active"
    update_project_state "evaluating" 80
    sleep 2
    
    # Create sample feedback output
    echo "# Implementation Feedback - Iteration $iter

## Strengths
- Clean structure following the original design
- Responsive layout implemented
- Core functionality in place

## Areas for Improvement
- Add more interactive elements
- Improve color contrast for accessibility
- Optimize mobile layout
- Add missing form validation

## Recommendations for Next Iteration
- Implement search functionality
- Add product detail pages
- Improve sidebar filter UI
- Update footer with social media links

## Overall Score: 7/10
" > "${MULTI_AGENT_DIR}/feedback/output/feedback_report_iter${iter}.md"
    echo -e "${GREEN}Feedback generated improvement suggestions${NC}"
    update_agent_status "feedback" "complete"
    
    # Update orchestrator status
    update_project_state "finalizing" 90
    sleep 1
    
    # Create final status report
    echo "# Multi-Agent System Status Report - Iteration $iter

All agents have completed their tasks for iteration $iter.

## Agent Status
- Crawler: Complete
- Analysis: Complete
- Implementation: Complete
- Feedback: Complete

## Outputs
- Extracted HTML: ../crawler/output/extracted_site_iter${iter}.html
- Analysis Report: ../analysis/output/analysis_report_iter${iter}.md
- Implemented Clone: ../implementation/output/clone_site_iter${iter}.html
- Feedback: ../feedback/output/feedback_report_iter${iter}.md

## Next Steps
$(if [ $iter -lt $iterations ]; then echo "Proceeding to iteration $(($iter+1))"; else echo "All iterations complete"; fi)
" > "${MULTI_AGENT_DIR}/orchestrator/output/status_report_iter${iter}.md"
    
    # Mark iteration as complete
    if [ $iter -eq $iterations ]; then
      update_project_state "complete" 100
      update_agent_status "orchestrator" "complete"
    else
      update_project_state "iterating" $(( 90 + (iter * 10 / iterations) ))
    fi
    
    echo -e "${GREEN}Iteration $iter completed${NC}"
    sleep 1
  done
  
  echo -e "\n${GREEN}All iterations completed successfully.${NC}"
}

# Display the current status of the multi-agent system
display_status() {
  # Read the current status
  local protocol_file="${SHARED_DIR}/communication_protocol.json"
  if [ ! -f "$protocol_file" ]; then
    echo -e "${RED}Error: Communication protocol file not found.${NC}"
    return 1
  fi
  
  # Parse the JSON using Python
  local states=$(python3 -c 'import json; f = open("'"$protocol_file"'", "r"); data = json.load(f); f.close(); print(" ".join([f"{agent}:{state}" for agent, state in data["agent_states"].items()]))' 2>/dev/null)
  local project_state=$(python3 -c 'import json; f = open("'"$protocol_file"'", "r"); data = json.load(f); f.close(); print(data["project_state"])' 2>/dev/null)
  local completion=$(python3 -c 'import json; f = open("'"$protocol_file"'", "r"); data = json.load(f); f.close(); print(data["completion_percentage"])' 2>/dev/null)
  local iteration=$(python3 -c 'import json; f = open("'"$protocol_file"'", "r"); data = json.load(f); f.close(); print(data["current_iteration"])' 2>/dev/null)
  
  # Display status
  clear_and_print_header
  
  echo -e "${YELLOW}Current Status:${NC} $project_state"
  echo -e "${YELLOW}Current Iteration:${NC} $iteration"
  echo ""
  
  echo -e "${YELLOW}Agent Status:${NC}"
  for state in $states; do
    agent=${state%%:*}
    status=${state#*:}
    print_agent_status "$agent" "$status"
  done
  
  echo ""
  echo -e "${YELLOW}Progress:${NC}"
  print_progress "$completion"
  
  # Display last few lines of logs from each agent if available
  echo ""
  echo -e "${YELLOW}Recent Activity:${NC}"
  for agent in orchestrator crawler analysis implementation feedback; do
    local log_file="${MULTI_AGENT_DIR}/${agent}/output/latest.log"
    local report_file=""
    
    case "$agent" in
      "orchestrator") report_file="${MULTI_AGENT_DIR}/${agent}/output/status_report_iter${iteration}.md" ;;
      "crawler") report_file="${MULTI_AGENT_DIR}/${agent}/output/extracted_site_iter${iteration}.html" ;;
      "analysis") report_file="${MULTI_AGENT_DIR}/${agent}/output/analysis_report_iter${iteration}.md" ;;
      "implementation") report_file="${MULTI_AGENT_DIR}/${agent}/output/clone_site_iter${iteration}.html" ;;
      "feedback") report_file="${MULTI_AGENT_DIR}/${agent}/output/feedback_report_iter${iteration}.md" ;;
    esac
    
    if [ -f "$report_file" ]; then
      case "$agent" in
        "orchestrator") 
          echo -e "${PURPLE}${agent^}:${NC} Created status report for iteration $iteration"
          ;;
        "crawler") 
          echo -e "${GREEN}${agent^}:${NC} Extracted site structure for iteration $iteration"
          ;;
        "analysis") 
          echo -e "${BLUE}${agent^}:${NC} Completed analysis for iteration $iteration"
          ;;
        "implementation") 
          echo -e "${YELLOW}${agent^}:${NC} Created site clone for iteration $iteration"
          ;;
        "feedback") 
          echo -e "${CYAN}${agent^}:${NC} Generated feedback for iteration $iteration"
          ;;
      esac
    fi
  done
}

# Main function
main() {
  local url="https://example.com"
  local iterations=2
  
  # Parse command-line arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --url=*)
        url="${1#*=}"
        shift
        ;;
      --iterations=*)
        iterations="${1#*=}"
        shift
        ;;
      --help)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --url=URL                Website URL to clone (default: https://example.com)"
        echo "  --iterations=N           Number of improvement iterations (default: 2)"
        echo "  --help                   Show this help message"
        echo ""
        exit 0
        ;;
      *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information"
        exit 1
        ;;
    esac
  done
  
  clear_and_print_header
  
  echo -e "${YELLOW}Configuration:${NC}"
  echo -e "  Website URL:      ${GREEN}$url${NC}"
  echo -e "  Iterations:       ${GREEN}$iterations${NC}"
  echo ""
  
  # Run the simulation in the background
  run_simulated_process "$url" "$iterations" &
  local sim_pid=$!
  
  # Continuously update status until simulation is done
  while kill -0 $sim_pid 2>/dev/null; do
    display_status
    sleep 1
  done
  
  # Final status update
  display_status
  
  echo ""
  echo -e "${GREEN}✓ Process completed successfully${NC}"
  echo -e "  You can view the outputs in: ${YELLOW}${MULTI_AGENT_DIR}/*/output/${NC}"
}

# Execute main function with all arguments
main "$@"