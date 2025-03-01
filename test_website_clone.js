#!/usr/bin/env node
/**
 * Website Clone Test Script
 * ------------------------
 * This script tests the Firecrawl MCP server's website cloning capabilities
 * using standard Node.js APIs to simulate Claude Desktop's interaction.
 * 
 * Created for the weed.th website structure extraction project.
 * Date: March 1, 2025
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ANSI color codes for terminal output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
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
 * Check if the Firecrawl MCP server is running
 * @returns {Promise<boolean>} - Whether the server is running
 */
async function checkServerStatus() {
  printInfo('Checking if Firecrawl MCP server is running...');

  return new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: 3456,
      path: '/status',
      method: 'GET',
      timeout: 3000
    }, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const statusData = JSON.parse(data);
            if (statusData.status === 'ok') {
              printSuccess('Firecrawl MCP server is running');
              resolve(true);
            } else {
              printWarning(`Server returned unexpected status: ${data}`);
              resolve(false);
            }
          } catch (e) {
            printWarning(`Failed to parse server response: ${e.message}`);
            resolve(false);
          }
        } else {
          printWarning(`Server returned status code ${res.statusCode}`);
          resolve(false);
        }
      });
    });
    
    req.on('error', (e) => {
      printError(`Server connection error: ${e.message}`);
      printInfo('Make sure the Firecrawl MCP server is running (run "npx firecrawl-mcp" in another terminal)');
      resolve(false);
    });
    
    req.on('timeout', () => {
      req.destroy();
      printError('Request timed out');
      resolve(false);
    });
    
    req.end();
  });
}

/**
 * Simulate sending a prompt to Claude Desktop to clone a website
 * @param {string} url - The URL to clone
 * @returns {Promise<string>} - The cloned website structure
 */
async function simulateClaudePrompt(url) {
  printInfo(`Simulating Claude Desktop prompt to clone ${url}...`);

  return new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: 3456,
      path: '/api/v1/scrape',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000
    }, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const responseData = JSON.parse(data);
            printSuccess('Successfully received website structure');
            resolve(responseData);
          } catch (e) {
            printWarning(`Failed to parse server response: ${e.message}`);
            resolve(null);
          }
        } else {
          printWarning(`Server returned status code ${res.statusCode}: ${data}`);
          resolve(null);
        }
      });
    });
    
    req.on('error', (e) => {
      printError(`Request error: ${e.message}`);
      resolve(null);
    });
    
    req.on('timeout', () => {
      req.destroy();
      printError('Request timed out');
      resolve(null);
    });
    
    const requestData = {
      url: url,
      options: {
        includeStyles: true,
        extractStructure: true,
        depth: 1
      }
    };
    
    req.write(JSON.stringify(requestData));
    req.end();
  });
}

/**
 * Save the cloned website structure to a file
 * @param {Object} data - The cloned website structure
 * @param {string} url - The URL that was cloned
 * @returns {string} - The path to the saved file
 */
function saveClonedStructure(data, url) {
  // Create output directory
  const outputDir = path.join(process.env.HOME, 'weedth_claude', 'clones');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Extract domain name from URL for the filename
  const domain = new URL(url).hostname;
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${domain}_${timestamp}.json`;
  const outputPath = path.join(outputDir, filename);
  
  // Save the data
  fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
  
  printSuccess(`Saved cloned structure to ${outputPath}`);
  return outputPath;
}

/**
 * Create a markdown representation of the website structure
 * @param {Object} data - The cloned website structure
 * @param {string} url - The URL that was cloned
 * @returns {string} - The path to the saved markdown file
 */
function createMarkdownRepresentation(data, url) {
  // Create output directory
  const outputDir = path.join(process.env.HOME, 'weedth_claude', 'clones');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Extract domain name from URL for the filename
  const domain = new URL(url).hostname;
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${domain}_${timestamp}.md`;
  const outputPath = path.join(outputDir, filename);
  
  // Generate markdown content
  let markdown = `# Cloned Structure: ${url}\n\n`;
  markdown += `*Generated on ${new Date().toLocaleString()}*\n\n`;
  
  // Add structure section
  markdown += `## Structure\n\n`;
  
  // This is a simplified example - in reality, you would parse the HTML structure
  // and create a proper markdown representation
  if (data.structure) {
    // Real implementation would parse the structure object
    markdown += `- Header\n`;
    markdown += `  - Logo\n`;
    markdown += `  - Navigation\n`;
    markdown += `- Main Content\n`;
    markdown += `  - ${domain === 'weed.th' ? 'Map Interface' : 'Content Area'}\n`;
    markdown += `  - ${domain === 'weed.th' ? 'Dispensary Listings' : 'Sidebar'}\n`;
    markdown += `- Footer\n`;
    markdown += `  - Links\n`;
    markdown += `  - Copyright\n`;
  } else {
    markdown += `*Structure data not available*\n`;
  }
  
  // Add styles section
  markdown += `\n## Styles\n\n`;
  if (data.styles) {
    // Real implementation would format the CSS styles
    markdown += `\`\`\`css\n`;
    markdown += `/* Primary colors */\n`;
    markdown += `--primary-color: #somecolor;\n`;
    markdown += `--secondary-color: #somecolor;\n\n`;
    markdown += `/* Typography */\n`;
    markdown += `--font-family: 'Some Font', sans-serif;\n`;
    markdown += `--heading-size: 24px;\n`;
    markdown += `\`\`\`\n`;
  } else {
    markdown += `*Style data not available*\n`;
  }
  
  // Save the markdown
  fs.writeFileSync(outputPath, markdown);
  
  printSuccess(`Created markdown representation at ${outputPath}`);
  return outputPath;
}

/**
 * Test the website cloning process
 * @param {string} url - The URL to clone
 */
async function testWebsiteClone(url) {
  printHeader(`Testing Website Cloning: ${url}`);
  
  // Check if server is running
  const isServerRunning = await checkServerStatus();
  if (!isServerRunning) {
    return;
  }
  
  // Simulate Claude Desktop prompt
  const clonedData = await simulateClaudePrompt(url);
  if (!clonedData) {
    printError('Failed to clone website structure');
    
    // Create a fallback response for demonstration purposes
    printInfo('Creating fallback response for demonstration...');
    const fallbackData = {
      structure: {
        tagName: 'html',
        children: [
          {
            tagName: 'head',
            children: []
          },
          {
            tagName: 'body',
            children: [
              {
                tagName: 'header',
                children: []
              },
              {
                tagName: 'main',
                children: []
              },
              {
                tagName: 'footer',
                children: []
              }
            ]
          }
        ]
      },
      styles: '/* Fallback styles */'
    };
    
    // Save fallback data and create markdown representation
    saveClonedStructure(fallbackData, url);
    createMarkdownRepresentation(fallbackData, url);
    return;
  }
  
  // Save the cloned structure
  saveClonedStructure(clonedData, url);
  
  // Create a markdown representation
  createMarkdownRepresentation(clonedData, url);
  
  printSuccess('Website cloning test completed successfully');
}

/**
 * Main function
 */
async function main() {
  printHeader('Firecrawl MCP Website Clone Test');
  
  // Create a readline interface for user input
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  // Ask the user which URL to clone
  rl.question(`${colors.yellow}Enter URL to clone (default: https://example.com): ${colors.reset}`, async (answer) => {
    // Use default URL if none provided
    const url = answer.trim() || 'https://example.com';
    
    // Test cloning the website
    await testWebsiteClone(url);
    
    // Close the readline interface
    rl.close();
    
    // Print final message
    printHeader('Test Complete');
    printInfo('To use this with Claude Desktop:');
    printInfo('1. Make sure Firecrawl MCP server is running (npx firecrawl-mcp)');
    printInfo('2. Open Claude Desktop');
    printInfo(`3. Use the prompt: "Clone the structure of ${url} using the Firecrawl MCP server"`);
    printInfo('4. See CLAUDE.md for more details and ethical considerations');
  });
}

// Run the main function
main().catch(error => {
  printError(`Unexpected error: ${error.message}`);
});