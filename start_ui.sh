#!/bin/bash
# Start the agent UI on port 8080

echo "Starting Multi-Agent System UI on port 8080..."
export FLASK_APP=agent_ui
export FLASK_DEBUG=1
python3 -c "
import os
import sys
from agent_ui import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True, use_reloader=False)
" "$@"

echo "UI should be accessible at: http://localhost:8080"