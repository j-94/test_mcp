#!/bin/bash
# Start the agent UI on any available port between 8000 and 9000

echo "Finding an available port and starting Multi-Agent System UI..."

# Try ports 8000-9000
for port in $(seq 8000 9000); do
  if ! lsof -i :$port >/dev/null 2>&1; then
    echo "Found available port: $port"
    export FLASK_APP=agent_ui
    export FLASK_DEBUG=1
    
    echo "Starting UI server on port $port..."
    echo "UI will be accessible at: http://localhost:$port"
    
    python3 -c "
import os
import sys
from agent_ui import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=$port, debug=True, use_reloader=False)
" "$@"
    
    break
  fi
done