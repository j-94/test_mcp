#!/bin/bash
#
# Simple Multi-Agent System Monitor
#

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Base directories
BASE_DIR="$(pwd)"
MULTI_AGENT_DIR="${BASE_DIR}/test_multi_agent"
SHARED_DIR="${MULTI_AGENT_DIR}/shared"

# Clear screen and print header
clear
echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}         MULTI-AGENT SYSTEM MONITOR             ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check if the communication protocol file exists
if [ ! -f "${SHARED_DIR}/communication_protocol.json" ]; then
  echo -e "${RED}Error: Communication protocol file not found.${NC}"
  echo -e "${YELLOW}Creating default protocol file...${NC}"
  
  # Create shared directory if it doesn't exist
  mkdir -p "${SHARED_DIR}"
  
  # Create default protocol file
  cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
EOL
  echo -e "${GREEN}Default protocol file created.${NC}"
fi

# Initialize the system with a website URL
URL="$1"
if [ -z "$URL" ]; then
  URL="https://example.com"
fi

# Update config.json with the URL
mkdir -p "${SHARED_DIR}"
cat > "${SHARED_DIR}/config.json" << EOL
{
  "website_url": "${URL}"
}
EOL
echo -e "${GREEN}Config updated with URL: ${URL}${NC}"

# Simulate running the multi-agent system
simulate_multi_agent_process() {
  echo -e "${YELLOW}Starting multi-agent simulation...${NC}"
  
  # Ensure output directories exist
  for agent in orchestrator crawler analysis implementation feedback; do
    mkdir -p "${MULTI_AGENT_DIR}/${agent}/output"
  done
  
  # Simulate two iterations
  for iter in 1 2; do
    echo -e "\n${YELLOW}Starting iteration ${iter}...${NC}"
    
    # Update current iteration in protocol
    cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "orchestrator": "active"
  },
  "project_state": "planning",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 5
}
EOL
    
    # Orchestrator active
    echo -e "${PURPLE}Orchestrator: Planning iteration ${iter}${NC}"
    sleep 1
    
    # Crawler phase
    cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "crawler": "active",
    "analysis": "idle",
    "implementation": "idle",
    "feedback": "idle",
    "orchestrator": "active"
  },
  "project_state": "crawling",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 10
}
EOL
    echo -e "${GREEN}Crawler: Extracting structure from ${URL}${NC}"
    
    # Create sample crawler output
    cat > "${MULTI_AGENT_DIR}/crawler/output/extracted_site_iter${iter}.html" << EOL
<html>
  <head>
    <title>Extracted from ${URL} (Iteration ${iter})</title>
  </head>
  <body>
    <h1>${URL}</h1>
    <p>This is a demonstration of the Crawler Agent - Iteration ${iter}.</p>
  </body>
</html>
EOL
    sleep 2
    
    # Analysis phase
    cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "crawler": "complete",
    "analysis": "active",
    "implementation": "idle",
    "feedback": "idle",
    "orchestrator": "active"
  },
  "project_state": "analyzing",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 30
}
EOL
    echo -e "${BLUE}Analysis: Analyzing website structure${NC}"
    
    # Create sample analysis output
    cat > "${MULTI_AGENT_DIR}/analysis/output/analysis_report_iter${iter}.md" << EOL
# Website Analysis Report - Iteration ${iter}

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
EOL
    sleep 2
    
    # Implementation phase
    cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "crawler": "complete",
    "analysis": "complete",
    "implementation": "active",
    "feedback": "idle",
    "orchestrator": "active"
  },
  "project_state": "implementing",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 60
}
EOL
    echo -e "${YELLOW}Implementation: Generating clone of ${URL}${NC}"
    
    # Create sample implementation output
    cat > "${MULTI_AGENT_DIR}/implementation/output/clone_site_iter${iter}.html" << EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clone of ${URL} (Iteration ${iter})</title>
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
        <div class="logo">LOGO</div>
        <nav>
            <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#">Products</a></li>
                <li><a href="#">Services</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <div class="content">
            <h1>Welcome to ${URL}</h1>
            <p>This is a demonstration of the Implementation Agent - Iteration ${iter}.</p>
            <div class="products">
                <div class="product">Product 1</div>
                <div class="product">Product 2</div>
                <div class="product">Product 3</div>
                <div class="product">Product 4</div>
            </div>
        </div>
        <div class="sidebar">
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
                    <input type="range" min="0" max="100">
                </div>
            </form>
        </div>
    </main>
    <footer>
        <p>© 2025 Clone Site - Iteration ${iter}</p>
    </footer>
</body>
</html>
EOL
    sleep 3
    
    # Feedback phase
    cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "crawler": "complete",
    "analysis": "complete",
    "implementation": "complete",
    "feedback": "active",
    "orchestrator": "active"
  },
  "project_state": "evaluating",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 80
}
EOL
    echo -e "${CYAN}Feedback: Evaluating implementation${NC}"
    
    # Create sample feedback output
    cat > "${MULTI_AGENT_DIR}/feedback/output/feedback_report_iter${iter}.md" << EOL
# Implementation Feedback - Iteration ${iter}

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
EOL
    sleep 2
    
    # Finish iteration
    cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "crawler": "complete",
    "analysis": "complete",
    "implementation": "complete",
    "feedback": "complete",
    "orchestrator": "active"
  },
  "project_state": "finalizing",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 90
}
EOL
    
    # Create final status report
    cat > "${MULTI_AGENT_DIR}/orchestrator/output/status_report_iter${iter}.md" << EOL
# Multi-Agent System Status Report - Iteration ${iter}

All agents have completed their tasks for iteration ${iter}.

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
$(if [ $iter -lt 2 ]; then echo "Proceeding to iteration $(($iter+1))"; else echo "All iterations complete"; fi)
EOL
    
    echo -e "${PURPLE}Orchestrator: Completed iteration ${iter}${NC}"
    
    if [ $iter -eq 2 ]; then
      # Final completion
      cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "crawler": "complete",
    "analysis": "complete",
    "implementation": "complete",
    "feedback": "complete",
    "orchestrator": "complete"
  },
  "project_state": "complete",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": 100
}
EOL
    else
      # Prepare for next iteration
      cat > "${SHARED_DIR}/communication_protocol.json" << EOL
{
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
    "orchestrator": "active"
  },
  "project_state": "iterating",
  "current_iteration": ${iter},
  "error_states": {},
  "completion_percentage": $(( 90 + (iter * 5) ))
}
EOL
    fi
    
    echo -e "${GREEN}Iteration ${iter} completed${NC}"
    sleep 1
  done
  
  echo -e "\n${GREEN}All iterations completed successfully.${NC}"
  echo -e "You can view the outputs in: ${YELLOW}${MULTI_AGENT_DIR}/*/output/${NC}"
}

# Run the simulation with the provided URL
simulate_multi_agent_process

# Print final status
echo -e "\n${BLUE}Final System Status${NC}"
echo -e "${GREEN}✓ Process completed successfully${NC}"
echo -e "  Cloned website: ${YELLOW}${URL}${NC}"
echo -e "  Outputs available in: ${YELLOW}${MULTI_AGENT_DIR}/*/output/${NC}"
echo ""
echo -e "${BLUE}Most recent outputs:${NC}"
ls -la ${MULTI_AGENT_DIR}/*/output/ | grep -v "^d" | tail -10