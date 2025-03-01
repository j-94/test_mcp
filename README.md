# Self-Improving Website Cloner with Claude VLM

This repository demonstrates a self-improving website cloning system built using Claude. It features an automated iterative refinement loop powered by VLM (Vision Language Model) image comparison.

![Website Cloning System](docs/system-diagram.png)

## What We've Built

We've created a comprehensive system that can:

1. **Clone website structures** - Extract layouts, styles and content patterns from websites
2. **Set up development environments** - Create working development copies with proper separation of HTML/CSS/JS
3. **Automate visual comparison** - Use Claude's VLM capabilities to analyze visual differences between versions
4. **Implement iterative feedback loops** - Automatically refine and improve websites based on AI suggestions
5. **Self-maintain project structures** - Handle directory creation, configuration, and dependency management

## Components

- **CLAUDE.md** - Comprehensive documentation with code snippets for integration
- **setup_firecrawl_mcp.sh** - MCP server setup for website cloning
- **update_mcp_servers.py** - Self-updating repository of MCP tools
- **test_website_clone.js** - Website structure extraction tool
- **weedth_clone_test.js** - Domain-specific example implementation
- **implement_iteration_cycle.js** - Complete iterative refinement system

## Key Features

### 1. Self-Improving Feedback Loop

The system captures screenshots of the website at different stages, compares them using Claude's VLM capabilities, and automatically implements suggested improvements:

```javascript
// Extract structured feedback from Claude's VLM analysis
function extractStructuredFeedback(claudeResponse) {
  // Process visual differences between website versions
  // Generate actionable improvements
  // Format as structured data for automated implementation
}

// Apply feedback through automated code changes
async function applyImplementationPlan(plan) {
  // Backup current files
  // Implement suggested CSS improvements
  // Update HTML structure
  // Document changes in iteration log
}
```

### 2. Automated Project Structure Management

```javascript
function checkProjectStructure() {
  // Verify required directories exist
  // Create missing components
  // Set up configuration files
  // Initialize development environment
}
```

### 3. Cross-Domain Adaptability

The system is designed to be easily adapted to different domains:

- **E-commerce** - Product listings, cart systems, checkout flows
- **Education** - Course catalogs, learning modules, assessment systems
- **Healthcare** - Provider directories, appointment booking, patient portals
- **Real Estate** - Property listings, map integration, filtering systems

## Getting Started

1. Clone this repository
2. Run the initial setup:
   ```bash
   ./setup_firecrawl_mcp.sh
   ```
3. Launch the iterative cycle implementation:
   ```bash
   node implement_iteration_cycle.js
   ```
4. Select option 4 to run the complete cycle

## Potential Next Steps

### 1. True Vision API Integration

Connect to Claude's Vision API for real-time screenshot analysis:

```javascript
async function analyzeScreenshotWithAPI(imagePath) {
  // Send screenshot to Claude Vision API
  // Process visual feedback
  // Generate structured improvement plan
}
```

### 2. Research API Integration

Add capability to research domain-specific best practices:

```javascript
async function researchDomainPatterns(domain) {
  // Query design pattern databases
  // Research competitive sites
  // Analyze successful implementations
  // Generate domain-specific recommendations
}
```

### 3. Multi-Tool Orchestration

Coordinate multiple AI tools for specialized functions:

```javascript
async function orchestrateTools(task) {
  // Delegate visual analysis to Claude VLM
  // Use code generation models for implementation
  // Leverage specialized domain models for content
  // Coordinate through central workflow
}
```

### 4. Self-Modifying Capabilities

Allow the system to improve its own code:

```javascript
async function selfOptimize() {
  // Analyze own performance metrics
  // Identify optimization opportunities
  // Implement code improvements
  // Test and validate changes
}
```

## Ethical Considerations

This project is designed for ethical website structure extraction. Always:

- Respect website terms of service and robots.txt
- Obtain proper permissions before cloning commercial sites
- Use for educational, development, or authorized purposes only
- Respect copyright and intellectual property

## License

MIT

## Acknowledgments

- Inspired by a February 21, 2025 X post about website cloning with Claude
- Built with [Claude](https://anthropic.com/claude) from Anthropic
- Uses MCP server architecture for Claude desktop integration