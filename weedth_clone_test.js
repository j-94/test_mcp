#!/usr/bin/env node
/**
 * Simple weed.th Website Clone Test
 * ---------------------------------
 * This script simulates cloning the weed.th website structure without
 * requiring the actual Firecrawl MCP server to be running.
 * 
 * Created for the weed.th website structure extraction project.
 * Date: March 1, 2025
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import os from 'os';

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
 * Print an error message to the console
 * @param {string} message - The message to print
 */
function printError(message) {
  console.log(`${colors.red}❌ ${message}${colors.reset}`);
}

/**
 * Generate a simulated weed.th website structure
 * @returns {Object} - The simulated website structure
 */
function generateWeedThStructure() {
  printInfo('Generating weed.th website structure...');
  
  // Simulate the structure that would be returned by the MCP server
  const structure = {
    url: 'https://weed.th/',
    title: 'weed.th - Cannabis Dispensary Mapping',
    structure: {
      tagName: 'html',
      children: [
        {
          tagName: 'head',
          children: [
            { tagName: 'title', content: 'weed.th - Cannabis Dispensary Mapping' },
            { tagName: 'meta', attributes: { name: 'description', content: 'Find cannabis dispensaries near you' } },
            { tagName: 'link', attributes: { rel: 'stylesheet', href: '/styles/main.css' } }
          ]
        },
        {
          tagName: 'body',
          children: [
            {
              tagName: 'header',
              className: 'site-header',
              children: [
                { tagName: 'img', className: 'logo', attributes: { src: '/images/logo.png', alt: 'weed.th logo' } },
                {
                  tagName: 'nav',
                  className: 'main-nav',
                  children: [
                    { tagName: 'a', content: 'Home', attributes: { href: '/' } },
                    { tagName: 'a', content: 'Map', attributes: { href: '/map' } },
                    { tagName: 'a', content: 'Dispensaries', attributes: { href: '/dispensaries' } },
                    { tagName: 'a', content: 'About', attributes: { href: '/about' } }
                  ]
                }
              ]
            },
            {
              tagName: 'main',
              children: [
                {
                  tagName: 'section',
                  className: 'hero',
                  children: [
                    { tagName: 'h1', content: 'Find Cannabis Dispensaries Near You' },
                    { tagName: 'p', content: 'The most comprehensive map of legal dispensaries in Thailand' }
                  ]
                },
                {
                  tagName: 'section',
                  id: 'map-container',
                  children: [
                    { tagName: 'div', id: 'map', className: 'interactive-map' },
                    {
                      tagName: 'div',
                      className: 'map-controls',
                      children: [
                        { tagName: 'input', attributes: { type: 'text', placeholder: 'Search by location...' } },
                        { tagName: 'button', content: 'Find Near Me' }
                      ]
                    }
                  ]
                },
                {
                  tagName: 'section',
                  className: 'dispensary-list',
                  children: [
                    { tagName: 'h2', content: 'Popular Dispensaries' },
                    {
                      tagName: 'ul',
                      className: 'dispensaries',
                      children: [
                        {
                          tagName: 'li',
                          className: 'dispensary-card',
                          children: [
                            { tagName: 'h3', content: 'Green Leaf Bangkok' },
                            { tagName: 'p', className: 'address', content: '123 Sukhumvit Rd, Bangkok' },
                            { tagName: 'div', className: 'rating', content: '★★★★☆' }
                          ]
                        },
                        {
                          tagName: 'li',
                          className: 'dispensary-card',
                          children: [
                            { tagName: 'h3', content: 'Phuket Cannabis Club' },
                            { tagName: 'p', className: 'address', content: '45 Beach Road, Phuket' },
                            { tagName: 'div', className: 'rating', content: '★★★★★' }
                          ]
                        },
                        {
                          tagName: 'li',
                          className: 'dispensary-card',
                          children: [
                            { tagName: 'h3', content: 'Chiang Mai Herbs' },
                            { tagName: 'p', className: 'address', content: '78 Mountain View, Chiang Mai' },
                            { tagName: 'div', className: 'rating', content: '★★★★☆' }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              tagName: 'footer',
              className: 'site-footer',
              children: [
                {
                  tagName: 'div',
                  className: 'footer-links',
                  children: [
                    { tagName: 'a', content: 'Terms of Use', attributes: { href: '/terms' } },
                    { tagName: 'a', content: 'Privacy Policy', attributes: { href: '/privacy' } },
                    { tagName: 'a', content: 'Contact Us', attributes: { href: '/contact' } }
                  ]
                },
                { tagName: 'p', className: 'copyright', content: '© 2025 weed.th - All rights reserved' }
              ]
            }
          ]
        }
      ]
    },
    styles: {
      'main.css': `
        /* Primary Colors */
        :root {
          --primary-color: #4CAF50;
          --secondary-color: #2E7D32;
          --text-color: #333333;
          --background-color: #F5F5F5;
          --accent-color: #FFC107;
        }
        
        /* Typography */
        body {
          font-family: 'Roboto', sans-serif;
          line-height: 1.6;
          color: var(--text-color);
          background-color: var(--background-color);
        }
        
        /* Header Styles */
        .site-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 2rem;
          background-color: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .logo {
          height: 50px;
        }
        
        .main-nav a {
          margin-left: 1.5rem;
          color: var(--text-color);
          text-decoration: none;
          font-weight: 500;
        }
        
        .main-nav a:hover {
          color: var(--primary-color);
        }
        
        /* Hero Section */
        .hero {
          text-align: center;
          padding: 4rem 2rem;
          background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
          color: white;
        }
        
        /* Map Styles */
        #map-container {
          padding: 2rem;
        }
        
        .interactive-map {
          height: 500px;
          background-color: #E0E0E0;
          border-radius: 8px;
          margin-bottom: 1rem;
        }
        
        .map-controls {
          display: flex;
          gap: 1rem;
        }
        
        /* Dispensary List */
        .dispensary-list {
          padding: 2rem;
        }
        
        .dispensaries {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 2rem;
          list-style: none;
          padding: 0;
        }
        
        .dispensary-card {
          padding: 1.5rem;
          border-radius: 8px;
          background-color: white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: transform 0.3s ease;
        }
        
        .dispensary-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* Footer Styles */
        .site-footer {
          background-color: #333;
          color: white;
          padding: 2rem;
          text-align: center;
        }
        
        .footer-links {
          margin-bottom: 1rem;
        }
        
        .footer-links a {
          color: white;
          margin: 0 1rem;
          text-decoration: none;
        }
        
        .footer-links a:hover {
          text-decoration: underline;
        }
      `
    }
  };
  
  printSuccess('Generated weed.th website structure');
  return structure;
}

/**
 * Save the simulated weed.th structure to a file
 * @returns {string} - The path to the saved file
 */
function saveWeedThStructure() {
  const structure = generateWeedThStructure();
  
  // Create output directory
  const outputDir = path.join(os.homedir(), 'weedth_claude', 'clones');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Save as JSON
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonFilename = `weed.th_${timestamp}.json`;
  const jsonPath = path.join(outputDir, jsonFilename);
  
  fs.writeFileSync(jsonPath, JSON.stringify(structure, null, 2));
  printSuccess(`Saved JSON structure to ${jsonPath}`);
  
  // Create markdown representation
  const mdFilename = `weed.th_${timestamp}.md`;
  const mdPath = path.join(outputDir, mdFilename);
  
  const markdown = `# weed.th Website Structure
*Generated on ${new Date().toLocaleString()}*

## Overview

The weed.th website is a cannabis dispensary mapping application for Thailand. It features a clean, modern design with a focus on map functionality and dispensary listings.

## Structure

- **Header**
  - Logo
  - Navigation (Home, Map, Dispensaries, About)

- **Main Content**
  - Hero Section
    - Headline: "Find Cannabis Dispensaries Near You"
    - Subheading: "The most comprehensive map of legal dispensaries in Thailand"
  
  - Map Interface
    - Interactive Map
    - Search Controls
    - Geolocation Button
  
  - Dispensary Listings
    - Featured dispensaries with ratings
    - Cards with dispensary details
    - Location information

- **Footer**
  - Legal Links (Terms, Privacy Policy)
  - Contact Information
  - Copyright Notice

## Style Guide

\`\`\`css
/* Primary Colors */
:root {
  --primary-color: #4CAF50;
  --secondary-color: #2E7D32;
  --text-color: #333333;
  --background-color: #F5F5F5;
  --accent-color: #FFC107;
}

/* Typography */
body {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
}
\`\`\`

## Key Components for Implementation

1. **Interactive Map Component**
   - Google Maps or Leaflet.js integration
   - Custom markers for dispensary locations
   - Popup info windows with dispensary details

2. **Search Functionality**
   - Location-based search
   - Filter by dispensary features
   - Sorting options (distance, rating)

3. **Responsive Design**
   - Mobile-friendly layout
   - Touch-friendly controls for map
   - Adaptive dispensary cards

## Ethical Considerations

This structure extraction is for educational and development purposes only. Any actual implementation should:

1. Respect copyright and intellectual property rights
2. Obtain proper permissions for using maps and location data
3. Comply with local regulations regarding cannabis information
4. Implement age verification where required by law

*Note: This is a simulated representation for demonstration purposes.*`;

  fs.writeFileSync(mdPath, markdown);
  printSuccess(`Created markdown representation at ${mdPath}`);
  
  return { jsonPath, mdPath };
}

/**
 * Generate HTML based on the structure
 */
function generateHTML() {
  printInfo('Generating HTML file from structure...');
  
  const structure = generateWeedThStructure();
  
  // Create output directory
  const outputDir = path.join(os.homedir(), 'weedth_claude', 'clones');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Simple HTML generation (this is a simplified version)
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>weed.th - Cannabis Dispensary Mapping</title>
  <style>
    ${structure.styles['main.css']}
  </style>
</head>
<body>
  <header class="site-header">
    <img src="placeholder-logo.png" alt="weed.th logo" class="logo">
    <nav class="main-nav">
      <a href="/">Home</a>
      <a href="/map">Map</a>
      <a href="/dispensaries">Dispensaries</a>
      <a href="/about">About</a>
    </nav>
  </header>

  <main>
    <section class="hero">
      <h1>Find Cannabis Dispensaries Near You</h1>
      <p>The most comprehensive map of legal dispensaries in Thailand</p>
    </section>

    <section id="map-container">
      <div id="map" class="interactive-map"></div>
      <div class="map-controls">
        <input type="text" placeholder="Search by location...">
        <button>Find Near Me</button>
      </div>
    </section>

    <section class="dispensary-list">
      <h2>Popular Dispensaries</h2>
      <ul class="dispensaries">
        <li class="dispensary-card">
          <h3>Green Leaf Bangkok</h3>
          <p class="address">123 Sukhumvit Rd, Bangkok</p>
          <div class="rating">★★★★☆</div>
        </li>
        <li class="dispensary-card">
          <h3>Phuket Cannabis Club</h3>
          <p class="address">45 Beach Road, Phuket</p>
          <div class="rating">★★★★★</div>
        </li>
        <li class="dispensary-card">
          <h3>Chiang Mai Herbs</h3>
          <p class="address">78 Mountain View, Chiang Mai</p>
          <div class="rating">★★★★☆</div>
        </li>
      </ul>
    </section>
  </main>

  <footer class="site-footer">
    <div class="footer-links">
      <a href="/terms">Terms of Use</a>
      <a href="/privacy">Privacy Policy</a>
      <a href="/contact">Contact Us</a>
    </div>
    <p class="copyright">© 2025 weed.th - All rights reserved</p>
  </footer>

  <script>
    // Placeholder for map functionality
    document.addEventListener('DOMContentLoaded', function() {
      const mapElement = document.getElementById('map');
      
      // This would be replaced with actual map implementation
      mapElement.innerHTML = '<div style="padding: 20px; text-align: center;">Interactive Map Placeholder</div>';
      
      // Example search functionality
      const button = document.querySelector('.map-controls button');
      button.addEventListener('click', function() {
        alert('Find Near Me functionality would be implemented here');
      });
    });
  </script>
</body>
</html>`;

  // Save the HTML file
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const htmlPath = path.join(outputDir, `weed.th_${timestamp}.html`);
  fs.writeFileSync(htmlPath, html);
  
  printSuccess(`Generated HTML file at ${htmlPath}`);
  return htmlPath;
}

/**
 * Main function
 */
async function main() {
  printHeader('weed.th Website Clone Simulation');
  
  printInfo('This script simulates the structure extraction of weed.th');
  printInfo('It demonstrates how Claude Desktop with the Firecrawl MCP server would work');
  
  // Save the weed.th structure
  const { jsonPath, mdPath } = saveWeedThStructure();
  
  // Generate HTML file
  const htmlPath = generateHTML();
  
  printHeader('Simulation Complete');
  printSuccess('Summary of outputs:');
  console.log(`1. JSON structure: ${jsonPath}`);
  console.log(`2. Markdown representation: ${mdPath}`);
  console.log(`3. HTML example: ${htmlPath}`);
  
  printInfo('');
  printInfo('To use this with Claude Desktop:');
  printInfo('1. Make sure Firecrawl MCP server is running (npx firecrawl-mcp)');
  printInfo('2. Open Claude Desktop');
  printInfo('3. Use the prompt: "Clone the structure of https://weed.th using the Firecrawl MCP server"');
  printInfo('4. See CLAUDE.md for more details and ethical considerations');
}

// Run the main function
main().catch(error => {
  printError(`Unexpected error: ${error.message}`);
});