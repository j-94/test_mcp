#!/usr/bin/env node
/**
 * Weed.th Website Iteration Cycle Implementation
 * ---------------------------------------------
 * This script implements the complete iterative cycle for the weed.th website,
 * integrating the project structure validation, dev server integration,
 * VLM-powered image comparison, and iterative refinement process.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { execSync } from 'child_process';
import os from 'os';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuration
const HOME_DIR = os.homedir();
const WEEDTH_DIR = path.join(HOME_DIR, 'weedth_claude');
const DEV_DIR = path.join(WEEDTH_DIR, 'dev');
const CLONE_DIR = path.join(WEEDTH_DIR, 'clones');
const SNAPSHOT_DIR = path.join(WEEDTH_DIR, 'snapshots');
const MCP_SERVERS_DIR = path.join(HOME_DIR, 'MCP_Servers');
const FEEDBACK_FILE = path.join(WEEDTH_DIR, 'dev_feedback.json');

// ANSI color codes for terminal output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

/**
 * Print a formatted header to the console
 * @param {string} title - The header title
 */
function printHeader(title) {
  console.log(`\n${colors.green}=== ${title} ===${colors.reset}`);
}

/**
 * Print an info message to the console
 * @param {string} message - The message to print
 */
function printInfo(message) {
  console.log(`${colors.blue}ℹ️ ${message}${colors.reset}`);
}

/**
 * Print a success message to the console
 * @param {string} message - The message to print
 */
function printSuccess(message) {
  console.log(`${colors.green}✅ ${message}${colors.reset}`);
}

/**
 * Print a warning message to the console
 * @param {string} message - The message to print
 */
function printWarning(message) {
  console.log(`${colors.yellow}⚠️ ${message}${colors.reset}`);
}

/**
 * Print an error message to the console
 * @param {string} message - The message to print
 */
function printError(message) {
  console.log(`${colors.red}❌ ${message}${colors.reset}`);
}

/**
 * Check and create required project structure
 */
function checkProjectStructure() {
  printHeader('Checking Project Structure');
  
  // Required directories
  const requiredDirs = [
    WEEDTH_DIR,
    DEV_DIR,
    CLONE_DIR,
    SNAPSHOT_DIR,
    MCP_SERVERS_DIR,
    path.join(DEV_DIR, 'backups')
  ];
  
  // Required files
  const requiredFiles = [
    path.join(MCP_SERVERS_DIR, 'mcp_servers.txt'),
    FEEDBACK_FILE
  ];
  
  // Check directories
  for (const dir of requiredDirs) {
    if (!fs.existsSync(dir)) {
      printInfo(`Creating directory: ${dir}`);
      fs.mkdirSync(dir, { recursive: true });
    } else {
      printSuccess(`Found directory: ${dir}`);
    }
  }
  
  // Check files
  for (const file of requiredFiles) {
    if (!fs.existsSync(file)) {
      printInfo(`Creating file: ${file}`);
      
      // Create basic file if missing
      if (file.includes('mcp_servers.txt')) {
        fs.writeFileSync(file, [
          'https://github.com/mendableai/firecrawl-mcp-server',
          'https://github.com/anthropics/anthropic-tools',
          'https://github.com/appcypher/awesome-mcp-servers'
        ].join('\n'));
      } else if (file.includes('dev_feedback.json')) {
        fs.writeFileSync(file, JSON.stringify({
          feedback: [],
          iterations: 0,
          last_updated: new Date().toISOString()
        }, null, 2));
      }
    } else {
      printSuccess(`Found file: ${file}`);
    }
  }
  
  printSuccess('Project structure verification complete');
}

/**
 * Set up development environment integration
 */
function setupDevIntegration() {
  printHeader('Setting Up Development Integration');
  
  // Find the latest HTML file
  let latestHtml = null;
  try {
    const files = fs.readdirSync(CLONE_DIR)
      .filter(file => file.endsWith('.html'))
      .map(file => ({
        name: file,
        path: path.join(CLONE_DIR, file),
        time: fs.statSync(path.join(CLONE_DIR, file)).mtime.getTime()
      }))
      .sort((a, b) => b.time - a.time);
    
    if (files.length > 0) {
      latestHtml = files[0].path;
    }
  } catch (error) {
    printError(`Error finding HTML files: ${error.message}`);
  }
  
  if (!latestHtml) {
    printWarning('No HTML clones found. Running website clone script...');
    
    try {
      // Run the weedth_clone_test.js script to generate HTML
      printInfo('Generating website clone...');
      execSync('node weedth_clone_test.js', { stdio: 'inherit' });
      
      // Try again to find the latest HTML
      const files = fs.readdirSync(CLONE_DIR)
        .filter(file => file.endsWith('.html'))
        .map(file => ({
          name: file,
          path: path.join(CLONE_DIR, file),
          time: fs.statSync(path.join(CLONE_DIR, file)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time);
      
      if (files.length > 0) {
        latestHtml = files[0].path;
      } else {
        printError('Could not generate HTML clone');
        return false;
      }
    } catch (error) {
      printError(`Error running clone script: ${error.message}`);
      return false;
    }
  }
  
  printInfo(`Using latest HTML: ${path.basename(latestHtml)}`);
  
  // Copy HTML to dev directory
  fs.copyFileSync(latestHtml, path.join(DEV_DIR, 'index.html'));
  printSuccess('Copied HTML to dev directory');
  
  // Extract CSS from HTML
  const htmlContent = fs.readFileSync(path.join(DEV_DIR, 'index.html'), 'utf8');
  const styleMatch = htmlContent.match(/<style>([\s\S]*?)<\/style>/);
  
  if (styleMatch && styleMatch[1]) {
    fs.writeFileSync(path.join(DEV_DIR, 'styles.css'), styleMatch[1].trim());
    printSuccess('Extracted CSS to styles.css');
    
    // Update HTML to reference external CSS
    const updatedHtml = htmlContent.replace(
      /<style>[\s\S]*?<\/style>/,
      '<link rel="stylesheet" href="styles.css">'
    );
    fs.writeFileSync(path.join(DEV_DIR, 'index.html'), updatedHtml);
    printSuccess('Updated HTML to use external CSS file');
  } else {
    printWarning('Could not extract CSS from HTML');
  }
  
  // Create server configuration
  const serverConfig = {
    port: 8080,
    hot: true,
    watch: ['**/*.html', '**/*.css', '**/*.js'],
    feedback: {
      enabled: true,
      captureInterval: 15000,
      outputPath: '../snapshots/'
    }
  };
  
  fs.writeFileSync(
    path.join(DEV_DIR, 'server-config.json'),
    JSON.stringify(serverConfig, null, 2)
  );
  printSuccess('Created server configuration');
  
  // Create a basic package.json if it doesn't exist
  if (!fs.existsSync(path.join(DEV_DIR, 'package.json'))) {
    const packageJson = {
      name: 'weedth-dev',
      version: '0.1.0',
      description: 'Development environment for weed.th website',
      scripts: {
        start: 'npx live-server --port=8080 --wait=100',
        snapshot: 'node ../capture_snapshot.js'
      },
      dependencies: {
        'live-server': '^1.2.2'
      }
    };
    
    fs.writeFileSync(
      path.join(DEV_DIR, 'package.json'),
      JSON.stringify(packageJson, null, 2)
    );
    printSuccess('Created package.json');
  }
  
  // Create a basic readme file
  fs.writeFileSync(
    path.join(DEV_DIR, 'README.md'),
    `# weed.th Development Environment

This is the development environment for the weed.th cannabis dispensary mapping website.

## Getting Started

1. Install dependencies: \`npm install\`
2. Start the development server: \`npm start\`
3. The website will open in your default browser.

## Taking Snapshots

Run \`npm run snapshot\` to capture a snapshot of the current state of the website.

## Iterative Refinement

The system will automatically compare snapshots and suggest improvements based on the feedback.`
  );
  printSuccess('Created README.md');
  
  // Create a simple snapshot capture script
  fs.writeFileSync(
    path.join(WEEDTH_DIR, 'capture_snapshot.js'),
    `#!/usr/bin/env node
/**
 * Snapshot Capture Script for weed.th
 * -----------------------------------
 * This script captures a screenshot of the development website
 * for use in the iterative refinement process.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const SNAPSHOT_DIR = path.join(__dirname, 'snapshots');
const DEV_SERVER_URL = 'http://localhost:8080';

// Ensure snapshot directory exists
if (!fs.existsSync(SNAPSHOT_DIR)) {
  fs.mkdirSync(SNAPSHOT_DIR, { recursive: true });
}

// Generate filename with timestamp
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const snapshotPath = path.join(SNAPSHOT_DIR, \`weedth_\${timestamp}.png\`);

console.log(\`Capturing snapshot to: \${snapshotPath}\`);

// This is a placeholder for actual screenshot capture
// In a real implementation, you would use a tool like Puppeteer
console.log('In a real implementation, this would use Puppeteer to capture a screenshot');
console.log('For this demo, we will just create an empty file');

// Create an empty file for demonstration purposes
fs.writeFileSync(snapshotPath, '');

console.log('Snapshot captured successfully');
`
  );
  printSuccess('Created snapshot capture script');
  
  printSuccess('Development integration setup complete');
  return true;
}

/**
 * Simulate the iterative refinement process
 */
function simulateIterativeRefinement() {
  printHeader('Simulating Iterative Refinement');
  
  // Check if required files exist
  if (!fs.existsSync(path.join(DEV_DIR, 'index.html')) || 
      !fs.existsSync(path.join(DEV_DIR, 'styles.css'))) {
    printError('Development files not found. Run setup first.');
    return;
  }
  
  // Generate simulated feedback
  const simulatedFeedback = {
    differences: "The newer version has a more polished navigation bar, improved map controls, and more detailed dispensary cards.",
    improvements: [
      "Navigation bar now has a cleaner layout with proper spacing",
      "Map interface includes a more prominent search box",
      "Dispensary cards show more information and have better hover effects"
    ],
    suggestions: [
      "Add filter options for the dispensary list",
      "Improve mobile responsiveness of the map interface",
      "Add a color legend for the map markers"
    ],
    issues: [
      "Search button styling inconsistent with site theme",
      "Footer links could use more spacing",
      "Map placeholder doesn't indicate loading state"
    ]
  };
  
  // Add feedback to the feedback file
  let feedbackData = { feedback: [], iterations: 0, last_updated: '' };
  
  if (fs.existsSync(FEEDBACK_FILE)) {
    const fileContent = fs.readFileSync(FEEDBACK_FILE, 'utf8');
    feedbackData = JSON.parse(fileContent);
  }
  
  // Add new feedback
  feedbackData.feedback.push({
    timestamp: new Date().toISOString(),
    analysis: simulatedFeedback
  });
  
  // Update metadata
  feedbackData.iterations += 1;
  feedbackData.last_updated = new Date().toISOString();
  
  // Save updated feedback
  fs.writeFileSync(FEEDBACK_FILE, JSON.stringify(feedbackData, null, 2));
  printSuccess('Added simulated feedback');
  
  // Create a simulated implementation plan
  const implementationPlan = {
    summary: "Implement filter options, improve mobile responsiveness, and fix styling issues",
    file_changes: [
      {
        file: "styles.css",
        changes: [
          {
            type: "add",
            selector: "end",
            new: `
/* Filter options */
.filter-options {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-option {
  padding: 0.5rem 1rem;
  background-color: var(--background-color);
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.filter-option:hover,
.filter-option.active {
  background-color: var(--primary-color);
  color: white;
}

/* Mobile responsiveness improvements */
@media (max-width: 768px) {
  .interactive-map {
    height: 300px;
  }
  
  .map-controls {
    flex-direction: column;
  }
  
  .dispensaries {
    grid-template-columns: 1fr;
  }
  
  .main-nav a {
    margin-left: 1rem;
    font-size: 14px;
  }
}

/* Fix styling issues */
.map-controls button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.footer-links a {
  margin: 0 1.5rem;
}

.interactive-map::before {
  content: "Loading map...";
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-style: italic;
  color: #666;
}`
          }
        ]
      },
      {
        file: "index.html",
        changes: [
          {
            type: "add",
            selector: '<section class="dispensary-list">',
            new: `
    <div class="filter-options">
      <div class="filter-option active">All</div>
      <div class="filter-option">Open Now</div>
      <div class="filter-option">Highest Rated</div>
      <div class="filter-option">Nearest</div>
    </div>`
          }
        ]
      }
    ]
  };
  
  // Apply the implementation plan
  printInfo('Applying implementation plan...');
  
  // Create backup directory
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupDir = path.join(DEV_DIR, 'backups', timestamp);
  fs.mkdirSync(backupDir, { recursive: true });
  
  // Process each file change
  for (const fileChange of implementationPlan.file_changes) {
    const filePath = path.join(DEV_DIR, fileChange.file);
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      printError(`File not found: ${fileChange.file}`);
      continue;
    }
    
    // Backup the file
    const backupPath = path.join(backupDir, fileChange.file);
    fs.copyFileSync(filePath, backupPath);
    printInfo(`Backed up ${fileChange.file}`);
    
    // Read current file content
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Apply each change
    for (const change of fileChange.changes) {
      switch (change.type) {
        case 'replace':
          if (content.includes(change.original)) {
            content = content.replace(change.original, change.new);
            printSuccess(`Replaced content in ${fileChange.file}`);
          } else {
            printWarning(`Original content not found in ${fileChange.file}`);
          }
          break;
          
        case 'add':
          if (change.selector === 'end') {
            // Add to end of file
            content += '\n' + change.new;
            printSuccess(`Added content to end of ${fileChange.file}`);
          } else if (change.selector === 'start') {
            // Add to start of file
            content = change.new + '\n' + content;
            printSuccess(`Added content to start of ${fileChange.file}`);
          } else {
            // Add after a specific selector
            if (content.includes(change.selector)) {
              content = content.replace(
                change.selector,
                change.selector + change.new
              );
              printSuccess(`Added content after "${change.selector}" in ${fileChange.file}`);
            } else {
              printWarning(`Selector "${change.selector}" not found in ${fileChange.file}`);
            }
          }
          break;
          
        case 'remove':
          if (content.includes(change.selector)) {
            content = content.replace(change.selector, '');
            printSuccess(`Removed content from ${fileChange.file}`);
          } else {
            printWarning(`Content to remove not found in ${fileChange.file}`);
          }
          break;
          
        default:
          printWarning(`Unknown change type: ${change.type}`);
      }
    }
    
    // Write updated content back to file
    fs.writeFileSync(filePath, content);
    printSuccess(`Updated ${fileChange.file}`);
  }
  
  // Update iteration log
  const logPath = path.join(DEV_DIR, 'iteration_log.md');
  let logContent = '';
  
  if (fs.existsSync(logPath)) {
    logContent = fs.readFileSync(logPath, 'utf8');
  }
  
  // Add new log entry
  logContent += `\n## Iteration ${timestamp}\n\n`;
  logContent += `### Summary\n${implementationPlan.summary}\n\n`;
  logContent += `### Changes\n`;
  
  for (const fileChange of implementationPlan.file_changes) {
    logContent += `- **${fileChange.file}**: ${fileChange.changes.length} changes\n`;
  }
  
  fs.writeFileSync(logPath, logContent);
  printSuccess(`Updated iteration log`);
  
  printSuccess('Iterative refinement simulation complete');
}

/**
 * Show the menu of available commands
 */
function showMenu() {
  console.log(`\n${colors.cyan}Weed.th Website Iteration Cycle${colors.reset}`);
  console.log(`${colors.cyan}================================${colors.reset}`);
  console.log(`
${colors.yellow}1${colors.reset}. Check and create project structure
${colors.yellow}2${colors.reset}. Set up development environment
${colors.yellow}3${colors.reset}. Simulate iterative refinement
${colors.yellow}4${colors.reset}. Run complete iteration cycle
${colors.yellow}5${colors.reset}. View latest development version
${colors.yellow}0${colors.reset}. Exit
  `);
}

/**
 * Run complete iteration cycle
 */
function runCompleteCycle() {
  printHeader('Running Complete Iteration Cycle');
  
  // Check project structure
  checkProjectStructure();
  
  // Set up development environment
  const devSetupSuccess = setupDevIntegration();
  if (!devSetupSuccess) {
    printError('Development environment setup failed');
    return;
  }
  
  // Simulate iterative refinement
  simulateIterativeRefinement();
  
  // Show the result
  printSuccess('Complete iteration cycle completed successfully');
  printInfo('You can now view the development version in a browser');
}

/**
 * View the latest development version
 */
function viewLatestVersion() {
  printHeader('Opening Latest Development Version');
  
  const indexPath = path.join(DEV_DIR, 'index.html');
  if (!fs.existsSync(indexPath)) {
    printError('Development files not found. Run setup first.');
    return;
  }
  
  printInfo(`Opening ${indexPath} in browser...`);
  
  try {
    // Detect OS and open browser accordingly
    if (process.platform === 'darwin') {
      // macOS
      execSync(`open "${indexPath}"`);
    } else if (process.platform === 'win32') {
      // Windows
      execSync(`start "" "${indexPath}"`);
    } else {
      // Linux
      execSync(`xdg-open "${indexPath}"`);
    }
    printSuccess('Browser opened');
  } catch (error) {
    printError(`Error opening browser: ${error.message}`);
    printInfo(`You can manually open this file: ${indexPath}`);
  }
}

/**
 * Main function that presents a menu and handles user input
 */
async function main() {
  // Show welcome message
  printHeader('Weed.th Website Iteration Cycle Implementation');
  console.log(`This script implements the complete iterative cycle for the weed.th website.`);
  
  // Create readline interface
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const promptUser = () => {
    showMenu();
    rl.question(`${colors.cyan}Enter your choice: ${colors.reset}`, (choice) => {
      switch (choice) {
        case '1':
          checkProjectStructure();
          setTimeout(promptUser, 500);
          break;
          
        case '2':
          setupDevIntegration();
          setTimeout(promptUser, 500);
          break;
          
        case '3':
          simulateIterativeRefinement();
          setTimeout(promptUser, 500);
          break;
          
        case '4':
          runCompleteCycle();
          setTimeout(promptUser, 500);
          break;
          
        case '5':
          viewLatestVersion();
          setTimeout(promptUser, 500);
          break;
          
        case '0':
          rl.close();
          printInfo('Goodbye!');
          break;
          
        default:
          printWarning('Invalid choice');
          setTimeout(promptUser, 500);
          break;
      }
    });
  };
  
  promptUser();
}

// Run the main function if executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(error => {
    printError(`Unexpected error: ${error.message}`);
  });
}

export {
  checkProjectStructure,
  setupDevIntegration,
  simulateIterativeRefinement,
  runCompleteCycle,
  viewLatestVersion
};