#!/bin/bash
#
# Multi-Agent Iteration Script
# Runs another iteration to refine the weed.th website clone
#

set -e  # Exit on error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}  Multi-Agent System Iteration Launcher       ${NC}"
echo -e "${BLUE}===============================================${NC}"

# Get last demo file
CLONES_DIR="$HOME/weedth_claude/clones"
ANALYSIS_DIR="$HOME/weedth_claude/analysis"
FEEDBACK_DIR="$HOME/weedth_claude/feedback"
ITERATIONS_DIR="$HOME/weedth_claude/iterations"

# Create directories if they don't exist
mkdir -p "$CLONES_DIR"
mkdir -p "$ANALYSIS_DIR"
mkdir -p "$FEEDBACK_DIR"
mkdir -p "$ITERATIONS_DIR"

# Find latest demo file
LATEST_DEMO=$(ls -t "$CLONES_DIR"/weedth_demo_*.html 2>/dev/null | head -1)

if [ -z "$LATEST_DEMO" ]; then
  echo -e "${YELLOW}No previous demo found. Running initial demo...${NC}"
  python weedth_simple_demo.py
  LATEST_DEMO=$(ls -t "$CLONES_DIR"/weedth_demo_*.html 2>/dev/null | head -1)
fi

echo -e "${GREEN}Using latest demo: ${LATEST_DEMO}${NC}"

# Get timestamp for this iteration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ITERATION_DIR="$ITERATIONS_DIR/iteration_$TIMESTAMP"
mkdir -p "$ITERATION_DIR"

# Define the improvements we want to make
echo -e "${BLUE}Creating feedback for iteration...${NC}"
FEEDBACK_FILE="$FEEDBACK_DIR/feedback_$TIMESTAMP.json"

cat > "$FEEDBACK_FILE" << EOL
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "base_file": "$(basename "$LATEST_DEMO")",
  "improvements": [
    {
      "type": "layout",
      "description": "Move the filter sidebar to the top as a collapsible filter bar for better mobile experience"
    },
    {
      "type": "feature",
      "description": "Add a 'Verify Age' modal that appears when the site first loads"
    },
    {
      "type": "design",
      "description": "Update the dispensary listings to include product categories like 'Flower', 'Edibles', 'Concentrates'"
    },
    {
      "type": "accessibility",
      "description": "Improve accessibility by adding proper ARIA labels and focus states"
    },
    {
      "type": "seo",
      "description": "Add metadata for better search engine optimization"
    }
  ],
  "priority": "high",
  "notes": "Make sure to keep the site functioning as a cannabis dispensary mapping service, but with a cleaner, more modern interface. Focus on mobile responsiveness."
}
EOL

echo -e "${GREEN}Feedback created at: ${FEEDBACK_FILE}${NC}"

# Create the new iteration
echo -e "${BLUE}Generating new iteration based on feedback...${NC}"
NEW_DEMO="$ITERATION_DIR/weedth_improved_$TIMESTAMP.html"

# Python code to apply the improvements
python3 - << EOL
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
import random

# Load the latest demo
with open("$LATEST_DEMO", 'r') as f:
    html = f.read()

# Load the feedback
with open("$FEEDBACK_FILE", 'r') as f:
    feedback = json.load(f)

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# 1. Move filters to top bar
print("Applying improvement: Convert sidebar filters to top bar...")
filters_div = soup.select_one('.filters')
if filters_div:
    # Create new filter bar
    filter_bar = soup.new_tag('div', attrs={'class': 'filter-bar'})
    filter_bar['style'] = 'background-color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; flex-wrap: wrap; gap: 1rem; position: relative;'
    
    # Add toggle button
    toggle_button = soup.new_tag('button', attrs={'class': 'filter-toggle', 'onclick': 'toggleFilters()'})
    toggle_button.string = 'Filters ▼'
    toggle_button['style'] = 'background-color: #1b5e20; color: white; border: none; border-radius: 4px; padding: 0.5rem 1rem; cursor: pointer; margin-bottom: 1rem;'
    filter_bar.append(toggle_button)
    
    # Create collapsible div
    filter_content = soup.new_tag('div', attrs={'class': 'filter-content', 'id': 'filterContent'})
    filter_content['style'] = 'display: none; width: 100%;'
    
    # Move filter groups
    for group in filters_div.select('.filter-group'):
        # Create a new group div with horizontal layout
        new_group = soup.new_tag('div', attrs={'class': 'filter-group-horizontal'})
        new_group['style'] = 'margin-right: 2rem; margin-bottom: 1rem;'
        
        # Add the title
        title = group.select_one('h3')
        if title:
            new_group.append(title)
        
        # Add the options with horizontal layout
        options_div = soup.new_tag('div', attrs={'class': 'filter-options-horizontal'})
        options_div['style'] = 'display: flex; gap: 1rem;'
        
        for option in group.select('.filter-option'):
            options_div.append(option)
        
        new_group.append(options_div)
        filter_content.append(new_group)
    
    # Add filter content to filter bar
    filter_bar.append(filter_content)
    
    # Add filter bar to container, before map-container
    container = soup.select_one('.container')
    map_container = soup.select_one('.map-container')
    if container and map_container:
        container.insert_before(filter_bar)
    
    # Remove the old filters div
    filters_div.decompose()
    
    # Make the map container full width
    if map_container:
        map_container['style'] = 'width: 100%;'
    
    # Add JavaScript for toggling filters
    script = soup.new_tag('script')
    script.string = '''
function toggleFilters() {
    var content = document.getElementById('filterContent');
    var button = document.querySelector('.filter-toggle');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        button.innerHTML = 'Filters ▲';
    } else {
        content.style.display = 'none';
        button.innerHTML = 'Filters ▼';
    }
}
'''
    soup.body.append(script)

# 2. Add age verification modal
print("Applying improvement: Adding age verification modal...")
age_verify_style = '''
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
.modal-content {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
    text-align: center;
}
.modal-title {
    color: #1b5e20;
    margin-top: 0;
}
.modal-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
}
.modal-button {
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    border: none;
    font-weight: bold;
    cursor: pointer;
}
.modal-confirm {
    background-color: #1b5e20;
    color: white;
}
.modal-deny {
    background-color: #e0e0e0;
    color: #333;
}
'''

# Add style to head
style_tag = soup.new_tag('style')
style_tag.string = age_verify_style
soup.head.append(style_tag)

# Create modal HTML
modal_html = '''
<div id="ageVerifyModal" class="modal-overlay">
    <div class="modal-content">
        <h2 class="modal-title">Age Verification</h2>
        <p>Welcome to weed.th. You must be 21 years or older to enter this site.</p>
        <p>By clicking "I am 21 or older", you confirm that you are of legal age to view cannabis content in your jurisdiction.</p>
        <div class="modal-buttons">
            <button class="modal-button modal-confirm" onclick="confirmAge()">I am 21 or older</button>
            <button class="modal-button modal-deny" onclick="denyAge()">I am under 21</button>
        </div>
    </div>
</div>
'''

# Add modal to body
modal_div = BeautifulSoup(modal_html, 'html.parser')
soup.body.insert(0, modal_div)

# Add scripts for modal functionality
modal_script = soup.new_tag('script')
modal_script.string = '''
function confirmAge() {
    document.getElementById('ageVerifyModal').style.display = 'none';
    // Set cookie to remember verification
    document.cookie = "ageVerified=true; max-age=86400; path=/";
}

function denyAge() {
    window.location.href = "https://www.google.com";
}

// Check if already verified
function checkAgeVerification() {
    if (document.cookie.indexOf("ageVerified=true") === -1) {
        document.getElementById('ageVerifyModal').style.display = 'flex';
    } else {
        document.getElementById('ageVerifyModal').style.display = 'none';
    }
}

// Run when page loads
window.onload = checkAgeVerification;
'''
soup.body.append(modal_script)

# 3. Update dispensary listings with product categories
print("Applying improvement: Adding product categories to listings...")
listing_cards = soup.select('.listing-card')
for card in listing_cards:
    content_div = card.select_one('.listing-content')
    if content_div:
        # Add product categories
        products_div = soup.new_tag('div', attrs={'class': 'product-categories'})
        products_div['style'] = 'display: flex; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap;'
        
        # List of possible products
        products = ['Flower', 'Edibles', 'Concentrates', 'Topicals', 'Pre-rolls', 'CBD', 'Vapes']
        
        # Randomly select 2-4 products for each dispensary
        num_products = random.randint(2, 4)
        selected = random.sample(products, num_products)
        
        for product in selected:
            product_tag = soup.new_tag('span', attrs={'class': 'product-tag'})
            product_tag['style'] = 'background-color: #e0f2e9; color: #1b5e20; padding: 0.25rem 0.5rem; border-radius: 20px; font-size: 0.8rem;'
            product_tag.string = product
            products_div.append(product_tag)
        
        content_div.append(products_div)

# 4. Add accessibility improvements
print("Applying improvement: Adding accessibility features...")
# Add ARIA labels to interactive elements
for button in soup.find_all('button'):
    if not button.get('aria-label'):
        if button.string:
            button['aria-label'] = button.string
        else:
            button['aria-label'] = 'Button'

# Add lang attribute to html tag if not present
html_tag = soup.html
if not html_tag.get('lang'):
    html_tag['lang'] = 'en'

# Add focus styles
focus_style = '''
/* Accessibility focus styles */
a:focus, button:focus, input:focus, [tabindex]:focus {
    outline: 3px solid #fdd835;
    outline-offset: 2px;
}
'''
# Add to existing style
style_tags = soup.select('style')
if style_tags:
    style_tags[0].string += focus_style

# 5. Add SEO metadata
print("Applying improvement: Adding SEO metadata...")
# Add meta description
description = soup.find('meta', attrs={'name': 'description'})
if not description:
    description = soup.new_tag('meta', attrs={'name': 'description'})
    description['content'] = 'weed.th is Thailand\'s premier cannabis dispensary mapping service. Find legal dispensaries near you, browse menus, and get directions.'
    soup.head.append(description)

# Add meta keywords
keywords = soup.find('meta', attrs={'name': 'keywords'})
if not keywords:
    keywords = soup.new_tag('meta', attrs={'name': 'keywords'})
    keywords['content'] = 'cannabis, dispensary, thailand, weed, marijuana, legal cannabis, medical marijuana, recreational cannabis, cannabis map, dispensary finder'
    soup.head.append(keywords)

# Add Open Graph tags
og_title = soup.new_tag('meta', attrs={'property': 'og:title'})
og_title['content'] = 'weed.th - Thailand Cannabis Dispensary Map'
soup.head.append(og_title)

og_desc = soup.new_tag('meta', attrs={'property': 'og:description'})
og_desc['content'] = 'Find legal cannabis dispensaries in Thailand with weed.th\'s interactive map.'
soup.head.append(og_desc)

og_type = soup.new_tag('meta', attrs={'property': 'og:type'})
og_type['content'] = 'website'
soup.head.append(og_type)

# Add mobile responsive meta tag if not present
viewport = soup.find('meta', attrs={'name': 'viewport'})
if not viewport:
    viewport = soup.new_tag('meta', attrs={'name': 'viewport'})
    viewport['content'] = 'width=device-width, initial-scale=1.0'
    soup.head.append(viewport)

# Add canonical URL
canonical = soup.new_tag('link', attrs={'rel': 'canonical'})
canonical['href'] = 'https://weed.th/'
soup.head.append(canonical)

# Update the iteration note to show this is an improved version
note_div = soup.select_one('.note')
if note_div:
    note_title = note_div.select_one('h4')
    if note_title:
        note_title.string = 'Improved Demonstration (Iteration {})'.format(datetime.now().strftime("%Y-%m-%d"))
    
    note_p = note_div.select_one('p')
    if note_p:
        note_p.string = 'This is an improved iteration of the weed.th website demonstration, with enhanced mobile responsiveness, age verification, product categories, accessibility features, and SEO optimization.'

# Add timestamp for this iteration
timestamp_div = soup.new_tag('div', attrs={'class': 'iteration-info'})
timestamp_div['style'] = 'text-align: center; font-size: 0.8rem; color: #666; margin-top: 2rem;'
timestamp_div.string = 'Iteration generated on: {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
soup.body.append(timestamp_div)

# Save the new version
with open("$NEW_DEMO", 'w') as f:
    f.write(str(soup))

print("Improvements applied successfully!")

# Create analysis file
analysis_file = "$ITERATION_DIR/analysis_$TIMESTAMP.json"
analysis = {
    "iteration_timestamp": datetime.now().isoformat(),
    "based_on": "$LATEST_DEMO",
    "improvements_applied": [imp["description"] for imp in feedback["improvements"]],
    "improvements_analysis": [
        {
            "type": "layout",
            "description": "Filters moved from sidebar to collapsible top bar",
            "impact": "Improves mobile responsiveness and saves vertical space"
        },
        {
            "type": "feature",
            "description": "Added age verification modal",
            "impact": "Ensures legal compliance and prevents underage access"
        },
        {
            "type": "design",
            "description": "Product categories added to listings",
            "impact": "Provides more information about dispensary offerings"
        },
        {
            "type": "accessibility",
            "description": "Added ARIA labels and focus styles",
            "impact": "Improves usability for screen readers and keyboard navigation"
        },
        {
            "type": "seo",
            "description": "Added meta tags and Open Graph data",
            "impact": "Improves search engine visibility and social sharing appearance"
        }
    ],
    "next_iteration_suggestions": [
        "Add dispensary details page",
        "Implement click functionality for map markers",
        "Add user reviews section",
        "Implement geolocation to show nearest dispensaries",
        "Add language toggle for Thai/English"
    ]
}

with open(analysis_file, 'w') as f:
    json.dump(analysis, f, indent=2)

print("Analysis saved to:", analysis_file)
EOL

echo -e "${GREEN}New iteration generated at: ${NEW_DEMO}${NC}"
echo -e "${GREEN}Analysis saved to: ${ITERATION_DIR}/analysis_${TIMESTAMP}.json${NC}"

# Open the new iteration in the browser
echo -e "${BLUE}Opening new iteration in browser...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
  open "$NEW_DEMO"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  if command -v xdg-open > /dev/null; then
    xdg-open "$NEW_DEMO"
  else
    echo -e "${YELLOW}Cannot open browser automatically. View file at: ${NEW_DEMO}${NC}"
  fi
else
  echo -e "${YELLOW}Cannot open browser automatically. View file at: ${NEW_DEMO}${NC}"
fi

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Iteration complete!${NC}"
echo -e "${BLUE}===============================================${NC}"