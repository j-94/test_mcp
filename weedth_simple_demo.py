#!/usr/bin/env python3
"""
Weed.th Simple Demo Generator
Creates a demonstration HTML showing what the weed.th cannabis mapping site would look like
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def generate_demo():
    """Generate a demo HTML for weed.th cannabis mapping site"""
    
    # Create output directory
    output_dir = os.path.expanduser("~/weedth_claude/clones")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"weedth_demo_{timestamp}.html")
    
    # Sample dispensary data
    dispensaries = [
        {
            "name": "Green Leaf Dispensary",
            "address": "123 Main Street, Bangkok",
            "rating": "4.8/5",
            "specialty": "Organic strains",
            "hours": "9AM-10PM"
        },
        {
            "name": "Bangkok Cannabis Co.",
            "address": "456 High Street, Bangkok",
            "rating": "4.5/5",
            "specialty": "Edibles",
            "hours": "10AM-8PM"
        },
        {
            "name": "Thai Medical Marijuana Clinic",
            "address": "789 Health Ave, Chiang Mai",
            "rating": "4.9/5",
            "specialty": "Medical strains",
            "hours": "8AM-6PM"
        },
        {
            "name": "Phuket Green Dispensary",
            "address": "101 Beach Road, Phuket",
            "rating": "4.3/5",
            "specialty": "Concentrates",
            "hours": "11AM-11PM"
        },
        {
            "name": "Weed Express Bangkok",
            "address": "202 Fast Lane, Bangkok",
            "rating": "4.0/5",
            "specialty": "Delivery service",
            "hours": "24 hours"
        }
    ]
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>weed.th - Thailand Cannabis Dispensary Map</title>
    <style>
        :root {{
            --primary: #1b5e20;
            --primary-light: #4c8c4a;
            --primary-dark: #003300;
            --secondary: #fdd835;
            --text-on-primary: #ffffff;
            --text-on-secondary: #000000;
            --background: #f5f5f5;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--background);
            color: #333;
        }}
        
        header {{
            background-color: var(--primary);
            color: var(--text-on-primary);
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .logo h1 {{
            margin: 0;
            font-size: 1.8rem;
        }}
        
        .logo-icon {{
            width: 40px;
            height: 40px;
            background-color: var(--secondary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: var(--primary-dark);
        }}
        
        nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 1rem;
            background-color: var(--primary-dark);
        }}
        
        nav ul {{
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
            gap: 1.5rem;
        }}
        
        nav a {{
            color: var(--text-on-primary);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .search-bar {{
            padding: 1rem;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .search-bar input {{
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 0.5rem;
            width: 60%;
            max-width: 400px;
        }}
        
        .search-bar button {{
            padding: 0.5rem 1rem;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        
        .container {{
            display: flex;
            max-width: 1200px;
            margin: 1rem auto;
            gap: 1rem;
            padding: 0 1rem;
        }}
        
        .filters {{
            width: 250px;
            background-color: white;
            padding: 1rem;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex-shrink: 0;
        }}
        
        .filters h2 {{
            margin-top: 0;
            font-size: 1.2rem;
            color: var(--primary);
        }}
        
        .filter-group {{
            margin-bottom: 1.5rem;
        }}
        
        .filter-group h3 {{
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
        }}
        
        .filter-options {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .filter-option {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .filter-option label {{
            flex: 1;
        }}
        
        .map-container {{
            flex: 1;
            position: relative;
        }}
        
        .map {{
            width: 100%;
            height: 400px;
            background-color: #e0e0e0;
            border-radius: 4px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .map-marker {{
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: var(--primary);
            border-radius: 50%;
            border: 3px solid white;
            transform: translate(-50%, -50%);
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            cursor: pointer;
        }}
        
        .map-marker:hover {{
            background-color: var(--secondary);
        }}
        
        .listings {{
            margin-top: 2rem;
        }}
        
        .listings h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            margin-top: 0;
        }}
        
        .listing-card {{
            background-color: white;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            gap: 1rem;
        }}
        
        .listing-image {{
            width: 100px;
            height: 100px;
            background-color: #e0e0e0;
            border-radius: 4px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
        }}
        
        .listing-content {{
            flex: 1;
        }}
        
        .listing-content h3 {{
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: var(--primary-dark);
        }}
        
        .listing-content p {{
            margin: 0.25rem 0;
        }}
        
        .rating {{
            color: var(--secondary);
            font-weight: bold;
        }}
        
        .footer {{
            background-color: var(--primary-dark);
            color: var(--text-on-primary);
            padding: 2rem 1rem;
            margin-top: 2rem;
        }}
        
        .footer-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
        }}
        
        .footer-section {{
            flex: 1;
            min-width: 200px;
        }}
        
        .footer-section h3 {{
            margin-top: 0;
            color: var(--secondary);
        }}
        
        .footer-section ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .footer-section li {{
            margin-bottom: 0.5rem;
        }}
        
        .footer-section a {{
            color: var(--text-on-primary);
            text-decoration: none;
        }}
        
        .footer-section a:hover {{
            text-decoration: underline;
        }}
        
        .copyright {{
            text-align: center;
            margin-top: 2rem;
            color: rgba(255,255,255,0.7);
            font-size: 0.9rem;
        }}
        
        .note {{
            background-color: #f8f9fa;
            border-left: 4px solid var(--primary);
            padding: 1rem;
            margin: 2rem auto;
            max-width: 1200px;
            border-radius: 0 4px 4px 0;
        }}
        
        .note h4 {{
            margin-top: 0;
            color: var(--primary);
        }}
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <div class="logo-icon">W</div>
            <h1>weed.th</h1>
        </div>
    </header>
    
    <nav>
        <ul>
            <li><a href="#">Home</a></li>
            <li><a href="#">Map</a></li>
            <li><a href="#">Dispensaries</a></li>
            <li><a href="#">About</a></li>
            <li><a href="#">Help</a></li>
        </ul>
        <div>
            <a href="#">Login</a>
        </div>
    </nav>
    
    <div class="search-bar">
        <input type="text" placeholder="Search for dispensaries...">
        <button>Search</button>
    </div>
    
    <div class="container">
        <div class="filters">
            <h2>Filters</h2>
            
            <div class="filter-group">
                <h3>Type</h3>
                <div class="filter-options">
                    <div class="filter-option">
                        <input type="checkbox" id="type-recreational" checked>
                        <label for="type-recreational">Recreational</label>
                    </div>
                    <div class="filter-option">
                        <input type="checkbox" id="type-medical" checked>
                        <label for="type-medical">Medical</label>
                    </div>
                    <div class="filter-option">
                        <input type="checkbox" id="type-cbd" checked>
                        <label for="type-cbd">CBD Only</label>
                    </div>
                </div>
            </div>
            
            <div class="filter-group">
                <h3>Rating</h3>
                <div class="filter-options">
                    <div class="filter-option">
                        <input type="checkbox" id="rating-5" checked>
                        <label for="rating-5">5 Stars</label>
                    </div>
                    <div class="filter-option">
                        <input type="checkbox" id="rating-4" checked>
                        <label for="rating-4">4+ Stars</label>
                    </div>
                    <div class="filter-option">
                        <input type="checkbox" id="rating-3" checked>
                        <label for="rating-3">3+ Stars</label>
                    </div>
                </div>
            </div>
            
            <div class="filter-group">
                <h3>Features</h3>
                <div class="filter-options">
                    <div class="filter-option">
                        <input type="checkbox" id="feature-delivery">
                        <label for="feature-delivery">Delivery</label>
                    </div>
                    <div class="filter-option">
                        <input type="checkbox" id="feature-open-now" checked>
                        <label for="feature-open-now">Open Now</label>
                    </div>
                    <div class="filter-option">
                        <input type="checkbox" id="feature-lab-tested">
                        <label for="feature-lab-tested">Lab Tested</label>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="map-container">
            <div class="map">
                <!-- Map markers positioned randomly -->
                <div class="map-marker" style="top: 30%; left: 40%;"></div>
                <div class="map-marker" style="top: 50%; left: 60%;"></div>
                <div class="map-marker" style="top: 70%; left: 30%;"></div>
                <div class="map-marker" style="top: 35%; left: 70%;"></div>
                <div class="map-marker" style="top: 65%; left: 50%;"></div>
                
                <p>[Interactive map would display here in the actual implementation]</p>
            </div>
            
            <div class="listings">
                <h2>Dispensaries Near You</h2>
                
                <!-- Dispensary listings -->
"""

    # Add dispensary listings
    for dispensary in dispensaries:
        html += f"""
                <div class="listing-card">
                    <div class="listing-image">
                        [Logo]
                    </div>
                    <div class="listing-content">
                        <h3>{dispensary['name']}</h3>
                        <p>{dispensary['address']}</p>
                        <p class="rating">★ {dispensary['rating']}</p>
                        <p>Specialty: {dispensary['specialty']}</p>
                        <p>Hours: {dispensary['hours']}</p>
                    </div>
                </div>"""

    # Close the main container and add footer
    html += """
            </div>
        </div>
    </div>
    
    <div class="note">
        <h4>Demonstration Note</h4>
        <p>This is a structural demonstration of what the weed.th website might look like. The site would function as a map-based directory of legal cannabis dispensaries in Thailand, similar to how other mapping applications work for businesses.</p>
        <p>No actual dispensary data is shown here. This demonstration is created for development and educational purposes only.</p>
    </div>
    
    <footer class="footer">
        <div class="footer-container">
            <div class="footer-section">
                <h3>weed.th</h3>
                <p>The trusted guide to legal cannabis dispensaries in Thailand.</p>
            </div>
            
            <div class="footer-section">
                <h3>Information</h3>
                <ul>
                    <li><a href="#">About Us</a></li>
                    <li><a href="#">Cannabis Laws</a></li>
                    <li><a href="#">FAQ</a></li>
                    <li><a href="#">Privacy Policy</a></li>
                    <li><a href="#">Terms of Service</a></li>
                </ul>
            </div>
            
            <div class="footer-section">
                <h3>For Dispensaries</h3>
                <ul>
                    <li><a href="#">List Your Business</a></li>
                    <li><a href="#">Business Portal</a></li>
                    <li><a href="#">Advertising</a></li>
                </ul>
            </div>
            
            <div class="footer-section">
                <h3>Contact</h3>
                <ul>
                    <li><a href="#">Support</a></li>
                    <li><a href="#">Feedback</a></li>
                    <li><a href="#">Report an Issue</a></li>
                </ul>
            </div>
        </div>
        
        <div class="copyright">
            <p>© 2025 weed.th - For demonstration purposes only</p>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </footer>
</body>
</html>
"""
    
    # Save to file
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"Demo generated and saved to: {output_file}")
    
    # Also create analysis file
    analysis_dir = os.path.expanduser("~/weedth_claude/analysis")
    os.makedirs(analysis_dir, exist_ok=True)
    
    analysis_file = os.path.join(analysis_dir, f"weedth_analysis_{timestamp}.json")
    
    analysis = {
        "generated_at": datetime.now().isoformat(),
        "demo_file": output_file,
        "features": [
            "Interactive map interface",
            "Dispensary listings",
            "Search functionality",
            "Filtering system",
            "Rating display",
            "Business details"
        ],
        "dispensaries": len(dispensaries),
        "map_markers": 5,
        "filters": {
            "type": ["Recreational", "Medical", "CBD Only"],
            "rating": ["5 Stars", "4+ Stars", "3+ Stars"],
            "features": ["Delivery", "Open Now", "Lab Tested"]
        },
        "site_sections": [
            "Header with logo",
            "Navigation menu",
            "Search bar",
            "Filter sidebar",
            "Map display",
            "Dispensary listings",
            "Footer with links"
        ]
    }
    
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"Analysis saved to: {analysis_file}")
    
    return output_file

if __name__ == "__main__":
    output_file = generate_demo()
    
    # Try opening in browser
    if sys.platform == "darwin":  # macOS
        os.system(f"open {output_file}")
    elif sys.platform == "win32":  # Windows
        os.system(f"start {output_file}")
    elif sys.platform.startswith("linux"):  # Linux
        os.system(f"xdg-open {output_file}")
    else:
        print(f"File saved to: {output_file}")
        print("Please open it manually in your browser.")