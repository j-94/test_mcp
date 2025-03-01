# CLAUDE.md - Firecrawl MCP Server Setup for weed.th Website Cloning

## Overview
This guide sets up the Firecrawl MCP server with Claude Desktop to clone website structures ethically, inspired by an X post (Feb 21, 2025) about cloning websites using Cursor and Firecrawl MCP with Claude 3.5 Sonnet. Adapted for Claude Desktop, it supports the weed.th cannabis dispensary mapping application by extracting site structures for development.

## Automated Directory and Project Structure Validation

The system automatically checks project structure and validates the setup before proceeding:

```bash
check_project_structure() {
  echo "Verifying project structure..."
  
  # Required directories
  REQUIRED_DIRS=(
    "~/weedth_claude"
    "~/weedth_claude/clones"
    "~/weedth_claude/dev"
    "~/weedth_claude/snapshots"
    "~/MCP_Servers"
  )
  
  # Required files
  REQUIRED_FILES=(
    "~/MCP_Servers/mcp_servers.txt"
    "~/weedth_claude/dev_feedback.json"
  )
  
  # Check directories
  for dir in "${REQUIRED_DIRS[@]}"; do
    dir_path=$(eval echo "$dir")
    if [ ! -d "$dir_path" ]; then
      echo "❌ Missing directory: $dir"
      echo "Creating directory: $dir"
      mkdir -p "$dir_path"
    else
      echo "✅ Found directory: $dir"
    fi
  done
  
  # Check files
  for file in "${REQUIRED_FILES[@]}"; do
    file_path=$(eval echo "$file")
    if [ ! -f "$file_path" ]; then
      echo "❌ Missing file: $file"
      # Create basic file if missing
      if [[ "$file" == *"mcp_servers.txt" ]]; then
        echo "Creating basic mcp_servers.txt file..."
        echo "https://github.com/mendableai/firecrawl-mcp-server" > "$file_path"
        echo "https://github.com/anthropics/anthropic-tools" >> "$file_path"
        echo "https://github.com/appcypher/awesome-mcp-servers" >> "$file_path"
      elif [[ "$file" == *"dev_feedback.json" ]]; then
        echo "Creating empty dev_feedback.json file..."
        echo '{"feedback": [], "iterations": 0, "last_updated": "'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"}' > "$file_path"
      fi
    else
      echo "✅ Found file: $file"
    fi
  done
  
  echo "Project structure verification complete."
}
```

## Dev Server Feedback Integration

This system integrates the development server feedback with the website cloning process, creating a continuous improvement loop:

```bash
setup_dev_integration() {
  echo "Setting up development server integration..."
  
  DEV_DIR="$HOME/weedth_claude/dev"
  CLONE_DIR="$HOME/weedth_claude/clones"
  SNAPSHOT_DIR="$HOME/weedth_claude/snapshots"
  FEEDBACK_FILE="$HOME/weedth_claude/dev_feedback.json"
  
  # Create a dev environment using the latest clone
  LATEST_HTML=$(ls -t "$CLONE_DIR"/*.html 2>/dev/null | head -1)
  
  if [ -z "$LATEST_HTML" ]; then
    echo "❌ No HTML clones found. Please run the cloning process first."
    return 1
  fi
  
  # Copy the latest HTML to the dev directory
  cp "$LATEST_HTML" "$DEV_DIR/index.html"
  echo "✅ Copied latest clone to dev environment"
  
  # Extract CSS from the HTML file and save as separate file
  echo "Extracting CSS from HTML..."
  grep -o '<style>.*</style>' "$DEV_DIR/index.html" | sed 's/<style>//;s/<\/style>//' > "$DEV_DIR/styles.css"
  
  # Update HTML to reference external CSS
  sed -i '' 's/<style>.*<\/style>/<link rel="stylesheet" href="styles.css">/' "$DEV_DIR/index.html"
  
  # Set up basic dev server configuration
  echo '{
    "port": 8080,
    "hot": true,
    "watch": ["**/*.html", "**/*.css", "**/*.js"],
    "feedback": {
      "enabled": true,
      "captureInterval": 15000,
      "outputPath": "../snapshots/"
    }
  }' > "$DEV_DIR/server-config.json"
  
  echo "✅ Development environment configured"
  
  # Create initial feedback record if it doesn't exist
  if [ ! -s "$FEEDBACK_FILE" ]; then
    echo '{"feedback": [], "iterations": 0, "last_updated": "'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"}' > "$FEEDBACK_FILE"
  fi
  
  echo "Development server integration complete."
}
```

## VLM-Powered Image Comparison and Analysis

The system uses Claude's Vision Language Model capabilities to compare snapshots of the website and provide intelligent feedback for improvements:

```javascript
// VLM comparison and analysis script
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const fetch = require('node-fetch');

// Configuration
const SNAPSHOT_DIR = path.join(process.env.HOME, 'weedth_claude', 'snapshots');
const FEEDBACK_FILE = path.join(process.env.HOME, 'weedth_claude', 'dev_feedback.json');
const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY;

// Validate required environment variables
if (!CLAUDE_API_KEY) {
  console.error('❌ CLAUDE_API_KEY environment variable not set');
  process.exit(1);
}

/**
 * Get the two most recent snapshots for comparison
 * @returns {Array} Array of two snapshot paths [newer, older]
 */
async function getRecentSnapshots() {
  try {
    const files = fs.readdirSync(SNAPSHOT_DIR)
      .filter(file => file.endsWith('.png'))
      .map(file => ({
        name: file,
        path: path.join(SNAPSHOT_DIR, file),
        time: fs.statSync(path.join(SNAPSHOT_DIR, file)).mtime.getTime()
      }))
      .sort((a, b) => b.time - a.time);
    
    if (files.length < 2) {
      console.error('❌ Need at least 2 snapshots for comparison');
      return null;
    }
    
    return [files[0].path, files[1].path];
  } catch (error) {
    console.error('❌ Error getting snapshots:', error.message);
    return null;
  }
}

/**
 * Convert images to base64 for API submission
 * @param {string} imagePath - Path to image
 * @returns {string} Base64-encoded image
 */
function imageToBase64(imagePath) {
  const image = fs.readFileSync(imagePath);
  return Buffer.from(image).toString('base64');
}

/**
 * Submit snapshot comparison to Claude VLM
 * @param {Array} snapshots - Array of [newer, older] snapshot paths
 * @returns {Object} Claude's analysis
 */
async function analyzeWithClaudeVLM(snapshots) {
  try {
    const [newerSnapshot, olderSnapshot] = snapshots;
    
    const newerBase64 = imageToBase64(newerSnapshot);
    const olderBase64 = imageToBase64(olderSnapshot);
    
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-opus-20240229',
        max_tokens: 2000,
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: 'I have two screenshots of a website for a cannabis dispensary mapping application called weed.th. The first image is an older version, and the second is the newer version after some development iterations. Please analyze both images and provide the following:\n\n1. Visual differences between the two versions\n2. Improvements made in the newer version\n3. Specific suggestions for further improvements to the design and user experience\n4. Any issues or inconsistencies that should be addressed\n5. A JSON object with structured feedback that can be used programmatically\n\nFocus particularly on the map interface, dispensary listings, and overall user experience.'
              },
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/png',
                  data: olderBase64
                }
              },
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/png',
                  data: newerBase64
                }
              }
            ]
          }
        ]
      })
    });
    
    const result = await response.json();
    
    if (!result.content || result.error) {
      throw new Error(result.error?.message || 'Unknown API error');
    }
    
    return result;
  } catch (error) {
    console.error('❌ Error analyzing with Claude VLM:', error.message);
    return null;
  }
}

/**
 * Extract structured feedback from Claude's response
 * @param {Object} claudeResponse - Claude API response
 * @returns {Object} Structured feedback object
 */
function extractStructuredFeedback(claudeResponse) {
  try {
    const content = claudeResponse.content[0].text;
    
    // Look for JSON block in the response
    const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/);
    
    if (jsonMatch && jsonMatch[1]) {
      return JSON.parse(jsonMatch[1]);
    }
    
    // If no JSON block found, create a simplified structure
    return {
      differences: "Could not extract structured differences",
      improvements: "Could not extract structured improvements",
      suggestions: ["Could not extract structured suggestions"],
      issues: ["Could not extract structured issues"],
      raw_feedback: content
    };
  } catch (error) {
    console.error('❌ Error extracting feedback:', error.message);
    return {
      error: error.message,
      raw_feedback: claudeResponse.content[0].text
    };
  }
}

/**
 * Save feedback to the feedback file
 * @param {Object} feedback - Structured feedback
 */
async function saveFeedback(feedback) {
  try {
    let feedbackData = { feedback: [], iterations: 0, last_updated: '' };
    
    if (fs.existsSync(FEEDBACK_FILE)) {
      const fileContent = fs.readFileSync(FEEDBACK_FILE, 'utf8');
      feedbackData = JSON.parse(fileContent);
    }
    
    // Add new feedback
    feedbackData.feedback.push({
      timestamp: new Date().toISOString(),
      analysis: feedback
    });
    
    // Update metadata
    feedbackData.iterations += 1;
    feedbackData.last_updated = new Date().toISOString();
    
    // Save updated feedback
    fs.writeFileSync(FEEDBACK_FILE, JSON.stringify(feedbackData, null, 2));
    
    console.log(`✅ Feedback saved to ${FEEDBACK_FILE}`);
    console.log(`Total iterations: ${feedbackData.iterations}`);
  } catch (error) {
    console.error('❌ Error saving feedback:', error.message);
  }
}

/**
 * Main function to run the analysis
 */
async function main() {
  console.log('🔄 Starting VLM snapshot comparison...');
  
  // Get snapshots
  const snapshots = await getRecentSnapshots();
  if (!snapshots) {
    return;
  }
  
  console.log(`📸 Comparing: \n  Newer: ${path.basename(snapshots[0])}\n  Older: ${path.basename(snapshots[1])}`);
  
  // Analyze with Claude VLM
  const analysis = await analyzeWithClaudeVLM(snapshots);
  if (!analysis) {
    return;
  }
  
  // Extract structured feedback
  const feedback = extractStructuredFeedback(analysis);
  
  // Save feedback
  await saveFeedback(feedback);
  
  console.log('✅ VLM analysis complete. Feedback saved to development cycle.');
}

// Run the main function
main().catch(error => {
  console.error('❌ Unexpected error:', error);
});
```

## Iterative Refinement Process

The final component is an automated iterative refinement process that uses the VLM feedback to improve the website:

```javascript
// Iterative refinement process
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const DEV_DIR = path.join(process.env.HOME, 'weedth_claude', 'dev');
const FEEDBACK_FILE = path.join(process.env.HOME, 'weedth_claude', 'dev_feedback.json');
const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY;

/**
 * Read the latest feedback and apply improvements
 */
async function applyFeedbackImprovements() {
  console.log('🔄 Starting iterative refinement process...');
  
  // Read feedback file
  if (!fs.existsSync(FEEDBACK_FILE)) {
    console.error('❌ Feedback file not found');
    return;
  }
  
  try {
    const feedbackData = JSON.parse(fs.readFileSync(FEEDBACK_FILE, 'utf8'));
    
    if (!feedbackData.feedback || feedbackData.feedback.length === 0) {
      console.error('❌ No feedback found');
      return;
    }
    
    // Get latest feedback
    const latestFeedback = feedbackData.feedback[feedbackData.feedback.length - 1];
    console.log(`📝 Processing feedback from: ${latestFeedback.timestamp}`);
    
    // Extract improvement suggestions
    const suggestions = latestFeedback.analysis.suggestions || [];
    if (suggestions.length === 0) {
      console.log('ℹ️ No specific suggestions found in feedback');
      return;
    }
    
    // Apply improvements based on suggestions
    console.log(`🛠️ Applying ${suggestions.length} improvements...`);
    
    // Create a plan for implementing improvements
    const implementationPlan = await createImplementationPlan(latestFeedback.analysis);
    
    // Apply the implementation plan
    await applyImplementationPlan(implementationPlan);
    
    console.log('✅ Improvements applied successfully');
    
    // Increment iteration count
    feedbackData.iterations += 1;
    feedbackData.last_updated = new Date().toISOString();
    fs.writeFileSync(FEEDBACK_FILE, JSON.stringify(feedbackData, null, 2));
    
    console.log(`🔄 Completed iteration #${feedbackData.iterations}`);
  } catch (error) {
    console.error('❌ Error applying improvements:', error.message);
  }
}

/**
 * Create an implementation plan based on Claude's feedback
 * @param {Object} analysis - Analysis object from feedback
 * @returns {Object} Implementation plan with specific file changes
 */
async function createImplementationPlan(analysis) {
  console.log('🧠 Creating implementation plan from feedback...');
  
  try {
    // Use Claude to generate specific code changes
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-opus-20240229',
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'text',
                text: `I need to improve a cannabis dispensary mapping website called weed.th based on the following feedback:
                
${JSON.stringify(analysis, null, 2)}

Here are the current files in the development directory:

HTML: ${fs.readFileSync(path.join(DEV_DIR, 'index.html'), 'utf8')}

CSS: ${fs.readFileSync(path.join(DEV_DIR, 'styles.css'), 'utf8')}

Please create a detailed implementation plan with specific code changes to address the feedback. Format your response as a JSON object with the following structure:

{
  "summary": "Brief summary of changes",
  "file_changes": [
    {
      "file": "filename.ext",
      "changes": [
        {
          "type": "replace" or "add" or "remove",
          "selector": "CSS selector or line identifier",
          "original": "original code to replace (if type is replace)",
          "new": "new code (if type is replace or add)"
        }
      ]
    }
  ]
}

Focus on making changes that address the specific issues mentioned in the feedback.`
              }
            ]
          }
        ]
      })
    });
    
    const result = await response.json();
    
    if (!result.content || result.error) {
      throw new Error(result.error?.message || 'Unknown API error');
    }
    
    // Extract the JSON implementation plan
    const content = result.content[0].text;
    const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/) || content.match(/\{[\s\S]*\}/);
    
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch (e) {
        console.error('❌ Error parsing implementation plan JSON');
        return {
          summary: "Could not parse implementation plan",
          file_changes: []
        };
      }
    }
    
    return {
      summary: "Could not extract implementation plan",
      file_changes: []
    };
  } catch (error) {
    console.error('❌ Error creating implementation plan:', error.message);
    return {
      summary: "Error creating implementation plan",
      file_changes: []
    };
  }
}

/**
 * Apply the implementation plan to the development files
 * @param {Object} plan - Implementation plan
 */
async function applyImplementationPlan(plan) {
  console.log(`🛠️ Applying implementation plan: ${plan.summary}`);
  
  if (!plan.file_changes || plan.file_changes.length === 0) {
    console.log('ℹ️ No file changes specified in plan');
    return;
  }
  
  // Create backup of current files
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupDir = path.join(DEV_DIR, 'backups', timestamp);
  fs.mkdirSync(backupDir, { recursive: true });
  
  // Process each file change
  for (const fileChange of plan.file_changes) {
    const filePath = path.join(DEV_DIR, fileChange.file);
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      console.error(`❌ File not found: ${fileChange.file}`);
      continue;
    }
    
    // Backup the file
    const backupPath = path.join(backupDir, fileChange.file);
    fs.copyFileSync(filePath, backupPath);
    console.log(`📦 Backed up ${fileChange.file} to ${backupPath}`);
    
    // Read current file content
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Apply each change
    for (const change of fileChange.changes) {
      switch (change.type) {
        case 'replace':
          if (content.includes(change.original)) {
            content = content.replace(change.original, change.new);
            console.log(`✅ Replaced content in ${fileChange.file}`);
          } else {
            console.warn(`⚠️ Original content not found in ${fileChange.file}`);
          }
          break;
          
        case 'add':
          if (change.selector === 'end') {
            // Add to end of file
            content += '\n' + change.new;
            console.log(`✅ Added content to end of ${fileChange.file}`);
          } else if (change.selector === 'start') {
            // Add to start of file
            content = change.new + '\n' + content;
            console.log(`✅ Added content to start of ${fileChange.file}`);
          } else {
            // Add after a specific selector
            const parts = content.split(change.selector);
            if (parts.length > 1) {
              content = parts[0] + change.selector + change.new + parts.slice(1).join(change.selector);
              console.log(`✅ Added content after "${change.selector}" in ${fileChange.file}`);
            } else {
              console.warn(`⚠️ Selector "${change.selector}" not found in ${fileChange.file}`);
            }
          }
          break;
          
        case 'remove':
          if (content.includes(change.selector)) {
            content = content.replace(change.selector, '');
            console.log(`✅ Removed content from ${fileChange.file}`);
          } else {
            console.warn(`⚠️ Content to remove not found in ${fileChange.file}`);
          }
          break;
          
        default:
          console.warn(`⚠️ Unknown change type: ${change.type}`);
      }
    }
    
    // Write updated content back to file
    fs.writeFileSync(filePath, content);
    console.log(`✅ Updated ${fileChange.file}`);
  }
  
  console.log('✅ All file changes applied successfully');
  
  // Update iteration log
  const logPath = path.join(DEV_DIR, 'iteration_log.md');
  let logContent = '';
  
  if (fs.existsSync(logPath)) {
    logContent = fs.readFileSync(logPath, 'utf8');
  }
  
  // Add new log entry
  logContent += `\n## Iteration ${timestamp}\n\n`;
  logContent += `### Summary\n${plan.summary}\n\n`;
  logContent += `### Changes\n`;
  
  for (const fileChange of plan.file_changes) {
    logContent += `- **${fileChange.file}**: ${fileChange.changes.length} changes\n`;
  }
  
  fs.writeFileSync(logPath, logContent);
  console.log(`📝 Updated iteration log at ${logPath}`);
}

// Run the main function if executed directly
if (require.main === module) {
  applyFeedbackImprovements().catch(error => {
    console.error('❌ Unexpected error:', error);
  });
}

module.exports = {
  applyFeedbackImprovements
};
```

## Prerequisites
- **Node.js v16+ and npm**: Download from [nodejs.org](https://nodejs.org).
  - Verify: `node -v` (e.g., v16.20.0), `npm -v` (e.g., 8.19.2).
- **Claude Desktop**: Install from [anthropic.com/desktop](https://www.anthropic.com/desktop).
  - Requires an Anthropic account and API key.
- **Firecrawl API Key**: Sign up at [firecrawl.dev](https://www.firecrawl.dev) (hypothetical).
- **Python 3.9+ (Optional)**: For weed.th integration, from [python.org](https://www.python.org).

## Setup Commands
1. **Install Node.js and npm**:
   - Run installer, restart terminal, verify versions.
2. **Install Claude Desktop**:
   - Download, install, add API key in Settings > API.
3. **Create Working Directory**:
   ```bash
   mkdir ~/weedth_claude
   cd ~/weedth_claude
   ```
4. **Install Firecrawl MCP**:
   ```bash
   npm install -g firecrawl-mcp
   # Verify: 
   npx firecrawl-mcp --version
   ```
5. **Start Server**:
   ```bash
   npx firecrawl-mcp
   ```
   Look for `[INFO] Server running` in terminal.
6. **Test Server**:
   ```bash
   curl http://localhost:3456/status
   ```
   Expected: `{"status": "ok"}` or similar.

## Environment Variables
Set these in your terminal:
- **FIRECRAWL_API_KEY**: Your Firecrawl API key.
  - macOS/Linux: 
    ```bash
    export FIRECRAWL_API_KEY="your-key"
    echo 'export FIRECRAWL_API_KEY="your-key"' >> ~/.zshrc
    source ~/.zshrc
    ```
  - Windows: 
    ```bash
    setx FIRECRAWL_API_KEY "your-key"
    ```
- **MCP_SERVER_PORT**: Custom port (default 3456).
  - Example: `export MCP_SERVER_PORT=4000`.

## Claude Desktop Integration
Edit `claude_desktop_config.json` in your Claude directory (e.g., `~/Library/Application Support/Anthropic/Claude` on macOS):
```json
{
  "api_key": "your-anthropic-api-key",
  "mcpServers": {
    "firecrawl-mcp": {
      "command": "npx",
      "args": ["firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-firecrawl-key"
      }
    }
  }
}
```
Restart Claude Desktop to apply.

## Test Website Cloning
1. **Start Firecrawl MCP Server**:
   - Run `npx firecrawl-mcp` in a terminal.
2. **Clone a Website**:
   - In Claude Desktop, prompt:
     ```
     Clone the structure of https://weed.th using the Firecrawl MCP server for ethical development of the weed.th mapping app.
     ```
   - Alternative test: Use https://example.com if weed.th isn't live.
3. **Expected Output**:
   - Files (e.g., `weedth_clone/index.html`, `styles.css`) or markdown:
     ```markdown
     # weed.th Structure
     - Header: Dispensary logo, navigation
     - Body: Map placeholder, store list
     - Footer: Legal info
     ```

**Ethical Note**: Ensure permission to clone live sites. For development, use owned or public domain sites.

## Self-Serving Feedback Loop
1. **Directory**: 
   ```bash
   mkdir ~/MCP_Servers
   echo "https://github.com/mendableai/firecrawl-mcp-server" > ~/MCP_Servers/mcp_servers.txt
   echo "https://github.com/anthropics/anthropic-tools" >> ~/MCP_Servers/mcp_servers.txt
   echo "https://github.com/appcypher/awesome-mcp-servers" >> ~/MCP_Servers/mcp_servers.txt
   ```
2. **Search**: 
   - Use `grep "web" ~/MCP_Servers/mcp_servers.txt` (macOS/Linux) or `findstr "web" ~/MCP_Servers/mcp_servers.txt` (Windows) to find cloning tools.
3. **Update**: Monthly, visit awesome-mcp-servers and append new repos.

## weed.th Integration
1. **Post-Cloning**:
   - Extract map-related elements (e.g., `<div id="map">`) from cloned output.
   - Integrate into a Python Flask app (example below):
     ```python
     from flask import Flask, render_template
     app = Flask(__name__)

     @app.route('/')
     def home():
         return render_template('index.html')  # Cloned weed.th structure

     if __name__ == '__main__':
         app.run(debug=True)
     ```

## Test Results (March 1, 2025)
- Cloned https://example.com: Generated index.html and styles.css.
- Next: Test with https://weed.th when live.

## Action Items
- [ ] Install Node.js, Claude Desktop, and Firecrawl MCP.
- [ ] Configure environment variables and claude_desktop_config.json.
- [ ] Test cloning with https://example.com.
- [ ] Clone https://weed.th (with permission).
- [ ] Integrate cloned structure into weed.th app.
- [ ] Update mcp_servers.txt monthly.

## Troubleshooting
- **Server Fails**: Check API key, reinstall with `npm install -g`.
- **No Output**: Verify server is running and URL is accessible.

## Alternative Approach (If Firecrawl MCP isn't available)
If Firecrawl MCP isn't natively supported, use this Claude prompt for ethical extraction:

```
Please analyze the structure of the website at [URL]. Create a markdown representation of:
1. The main layout sections (header, navigation, content areas, footer)
2. UI components and their relationships
3. The CSS styling patterns (colors, typography, spacing)

Focus on the structural elements rather than copying exact content, for ethical development purposes.
```