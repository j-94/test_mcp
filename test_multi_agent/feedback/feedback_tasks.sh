#!/bin/bash

echo "==== FEEDBACK AGENT ===="

if command -v claude &> /dev/null; then
  claude "As the Feedback Agent, compare the implementation in ../implementation/output with the original site structure in ../crawler/output. Generate structured improvement suggestions and save them to the ./output directory. Update ../shared/communication_protocol.json when complete."
else
  echo "Claude CLI not available. Would have provided feedback comparing ../implementation/output with ../crawler/output"
  # Create a sample feedback file as a demonstration
  echo "# Improvement Suggestions

1. Add more semantic HTML elements
2. Improve color contrast for accessibility
3. Add responsive design breakpoints" > ./output/feedback.md
  echo "Created sample feedback in ./output/feedback.md"
fi
