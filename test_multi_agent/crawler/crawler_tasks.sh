#!/bin/bash

echo "==== CRAWLER AGENT ===="
echo "Processing https://example.com..."

if command -v claude &> /dev/null; then
  claude "As the Crawler Agent, extract the structure of https://example.com. Create HTML, CSS, and component files that represent the site's structure. Save all outputs to the ./output directory and update the ../shared/communication_protocol.json when complete."
else
  echo "Claude CLI not available. Would have extracted https://example.com"
  # Create a sample HTML file as a demonstration
  echo "<html><head><title>Sample Extracted from https://example.com</title></head><body><h1>Sample Extraction</h1><p>This is a demonstration of the Crawler Agent.</p></body></html>" > ./output/sample.html
  echo "Created sample output in ./output/sample.html"
fi
