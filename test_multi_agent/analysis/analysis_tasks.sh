#!/bin/bash

echo "==== ANALYSIS AGENT ===="

if command -v claude &> /dev/null; then
  claude "As the Analysis Agent, examine the website structure in ../crawler/output. Identify key components, design patterns, and create a design system document. Save all outputs to the ./output directory and update the ../shared/communication_protocol.json when complete."
else
  echo "Claude CLI not available. Would have analyzed from ../crawler/output"
  # Create a sample analysis file as a demonstration
  echo "# Design Analysis

- Simple heading structure
- Basic paragraph text
- No complex components identified" > ./output/analysis.md
  echo "Created sample analysis in ./output/analysis.md"
fi
