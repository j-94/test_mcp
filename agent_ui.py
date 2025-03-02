#!/usr/bin/env python3
"""
Web UI for Multi-Agent System with ForeverVM Integration
Provides a simple interface to control and monitor the multi-agent system.
"""

import os
import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Try to import required dependencies
try:
    # Try to install Flask if not available
    try:
        from flask import Flask, render_template, request, jsonify, redirect, url_for
    except ImportError:
        print("Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        from flask import Flask, render_template, request, jsonify, redirect, url_for
    
    # Try to install python-dotenv if not available
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Installing python-dotenv...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
        from dotenv import load_dotenv
    
    # Try to import ForeverVM integration
    try:
        from integrate_forevervm import MultiAgentExecutor, ForeverVMSandbox
        FOREVERVM_AVAILABLE = True
    except ImportError:
        print("Warning: ForeverVM integration not available")
        FOREVERVM_AVAILABLE = False
except Exception as e:
    print(f"Error setting up dependencies: {str(e)}")
    FOREVERVM_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)

# Configuration
CONFIG = {
    "agents": ["orchestrator", "crawler", "analysis", "implementation", "feedback"],
    "base_dir": str(project_root),
    "multi_agent_dir": str(project_root / "test_multi_agent"),
    "forevervm_available": FOREVERVM_AVAILABLE,
    "log_file": str(project_root / "agent_ui.log")
}

# Agent process tracking
agent_processes = {}
agent_status = {agent: "idle" for agent in CONFIG["agents"]}

# Create HTML templates directory if it doesn't exist
templates_dir = project_root / "templates"
templates_dir.mkdir(exist_ok=True)

# Create static directory if it doesn't exist
static_dir = project_root / "static"
static_dir.mkdir(exist_ok=True)

# Create templates
def create_templates():
    """Create HTML templates for the UI."""
    
    # Index template
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent System UI</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <h1>Multi-Agent System Control Panel</h1>
        <div class="status">
            <span>System Status: </span>
            <span id="system-status" class="status-badge idle">Idle</span>
            {% if config.forevervm_available %}
            <span class="forevervm-badge">ForeverVM Enabled</span>
            {% else %}
            <span class="forevervm-badge disabled">ForeverVM Disabled</span>
            {% endif %}
        </div>
    </header>
    
    <div class="container">
        <div class="sidebar">
            <div class="control-panel">
                <h2>Controls</h2>
                <div class="control-buttons">
                    <button id="start-all" class="btn primary">Start All Agents</button>
                    <button id="stop-all" class="btn danger">Stop All Agents</button>
                </div>
                
                <h3>Website URL</h3>
                <div class="url-input">
                    <input type="text" id="website-url" placeholder="https://example.com">
                    <button id="set-url" class="btn secondary">Set</button>
                </div>
                
                <h3>ForeverVM Sandbox</h3>
                <div class="sandbox-controls">
                    <button id="test-sandbox" class="btn secondary" {% if not config.forevervm_available %}disabled{% endif %}>
                        Test Sandbox
                    </button>
                    <div class="sandbox-status">
                        <span>Status: </span>
                        <span id="sandbox-status" class="status-badge idle">Not Running</span>
                    </div>
                </div>
                
                <h3>Code Execution</h3>
                <div class="code-input">
                    <textarea id="code-to-execute" placeholder="# Python code to execute in sandbox
import os
print('Hello from ForeverVM sandbox!')
print(f'Current directory: {os.getcwd()}')"></textarea>
                    <button id="execute-code" class="btn primary" {% if not config.forevervm_available %}disabled{% endif %}>
                        Execute in Sandbox
                    </button>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="agents-panel">
                <h2>Agent Status</h2>
                <div class="agent-grid">
                    {% for agent in config.agents %}
                    <div class="agent-card" id="agent-{{ agent }}">
                        <div class="agent-header">
                            <h3>{{ agent|capitalize }} Agent</h3>
                            <span class="agent-status idle">Idle</span>
                        </div>
                        <div class="agent-controls">
                            <button class="btn secondary start-agent" data-agent="{{ agent }}">Start</button>
                            <button class="btn danger stop-agent" data-agent="{{ agent }}">Stop</button>
                        </div>
                        <div class="agent-output">
                            <div class="output-header">
                                <h4>Output</h4>
                                <button class="btn mini clear-output" data-agent="{{ agent }}">Clear</button>
                            </div>
                            <pre class="output-text"></pre>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="output-panel">
                <div class="output-header">
                    <h2>System Output</h2>
                    <button id="clear-system-output" class="btn mini">Clear</button>
                </div>
                <pre id="system-output" class="system-output"></pre>
            </div>
            
            <div class="sandbox-panel">
                <h2>ForeverVM Sandbox Output</h2>
                <pre id="sandbox-output" class="sandbox-output"></pre>
            </div>
            
            <div class="metrics-panel">
                <h2>System Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Agent Activity</h3>
                        <canvas id="agent-activity-chart"></canvas>
                    </div>
                    <div class="metric-card">
                        <h3>Sandbox Executions</h3>
                        <canvas id="sandbox-executions-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>Multi-Agent System with ForeverVM Integration | <a href="https://github.com/anthropics/claude-code" target="_blank">Powered by Claude</a></p>
    </footer>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
    """
    
    with open(templates_dir / "index.html", "w") as f:
        f.write(index_html)
    
    # Create CSS
    css = """
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --danger-color: #e74c3c;
    --background-color: #f5f7fa;
    --card-color: #ffffff;
    --text-color: #2c3e50;
    --border-color: #dce0e6;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --error-color: #c0392b;
    --idle-color: #7f8c8d;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    display: flex;
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: var(--text-color);
    color: white;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 {
    font-size: 1.5rem;
    font-weight: 500;
}

.status {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-badge {
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: 500;
    font-size: 0.8rem;
}

.status-badge.idle {
    background-color: var(--idle-color);
    color: white;
}

.status-badge.running {
    background-color: var(--success-color);
    color: white;
}

.status-badge.error {
    background-color: var(--error-color);
    color: white;
}

.forevervm-badge {
    background-color: var(--primary-color);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
}

.forevervm-badge.disabled {
    background-color: var(--idle-color);
}

.sidebar {
    width: 300px;
    margin-right: 20px;
}

.control-panel {
    background-color: var(--card-color);
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.control-panel h2, .control-panel h3 {
    margin-bottom: 15px;
    font-weight: 500;
}

.control-panel h3 {
    margin-top: 20px;
    font-size: 1rem;
    color: #555;
}

.control-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn.primary {
    background-color: var(--primary-color);
    color: white;
}

.btn.secondary {
    background-color: var(--secondary-color);
    color: white;
}

.btn.danger {
    background-color: var(--danger-color);
    color: white;
}

.btn.mini {
    padding: 4px 8px;
    font-size: 0.8rem;
}

.url-input {
    display: flex;
    gap: 5px;
}

.url-input input {
    flex: 1;
    padding: 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

.sandbox-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.sandbox-status {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.9rem;
}

.code-input {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.code-input textarea {
    height: 120px;
    padding: 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-family: monospace;
    resize: vertical;
}

.main-content {
    flex: 1;
}

.agents-panel, .output-panel, .sandbox-panel, .metrics-panel {
    background-color: var(--card-color);
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
}

.agent-card {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
}

.agent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background-color: #f8f9fa;
    border-bottom: 1px solid var(--border-color);
}

.agent-header h3 {
    font-size: 1rem;
    font-weight: 500;
}

.agent-status {
    font-size: 0.8rem;
    padding: 3px 8px;
    border-radius: 12px;
}

.agent-status.idle {
    background-color: var(--idle-color);
    color: white;
}

.agent-status.running {
    background-color: var(--success-color);
    color: white;
}

.agent-status.error {
    background-color: var(--error-color);
    color: white;
}

.agent-controls {
    display: flex;
    gap: 10px;
    padding: 10px 15px;
    border-bottom: 1px solid var(--border-color);
}

.agent-output {
    padding: 10px 15px;
}

.output-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.output-header h4 {
    font-size: 0.9rem;
    font-weight: 500;
}

.output-text, .system-output, .sandbox-output {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9rem;
    max-height: 150px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

.system-output, .sandbox-output {
    max-height: 300px;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 15px;
}

.metric-card {
    padding: 10px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
}

footer {
    text-align: center;
    padding: 20px;
    background-color: var(--text-color);
    color: white;
    font-size: 0.9rem;
}

footer a {
    color: var(--primary-color);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}
    """
    
    with open(static_dir / "style.css", "w") as f:
        f.write(css)
    
    # Create JavaScript
    js = """
// DOM Elements
const systemStatus = document.getElementById('system-status');
const systemOutput = document.getElementById('system-output');
const sandboxOutput = document.getElementById('sandbox-output');
const sandboxStatus = document.getElementById('sandbox-status');
const codeToExecute = document.getElementById('code-to-execute');
const websiteUrl = document.getElementById('website-url');

// Button event listeners
document.getElementById('start-all').addEventListener('click', startAllAgents);
document.getElementById('stop-all').addEventListener('click', stopAllAgents);
document.getElementById('set-url').addEventListener('click', setWebsiteUrl);
document.getElementById('test-sandbox').addEventListener('click', testSandbox);
document.getElementById('execute-code').addEventListener('click', executeCode);
document.getElementById('clear-system-output').addEventListener('click', () => { systemOutput.textContent = ''; });

// Agent-specific buttons
document.querySelectorAll('.start-agent').forEach(button => {
    button.addEventListener('click', () => startAgent(button.dataset.agent));
});

document.querySelectorAll('.stop-agent').forEach(button => {
    button.addEventListener('click', () => stopAgent(button.dataset.agent));
});

document.querySelectorAll('.clear-output').forEach(button => {
    button.addEventListener('click', () => {
        const agentCard = document.getElementById(`agent-${button.dataset.agent}`);
        const outputText = agentCard.querySelector('.output-text');
        outputText.textContent = '';
    });
});

// Initialize charts
let agentActivityChart, sandboxExecutionsChart;

function initCharts() {
    // Agent Activity Chart
    const activityCtx = document.getElementById('agent-activity-chart').getContext('2d');
    agentActivityChart = new Chart(activityCtx, {
        type: 'bar',
        data: {
            labels: ['Orchestrator', 'Crawler', 'Analysis', 'Implementation', 'Feedback'],
            datasets: [{
                label: 'Activity (seconds)',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#3498db',
                    '#2ecc71',
                    '#9b59b6',
                    '#e67e22',
                    '#f1c40f'
                ]
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Sandbox Executions Chart
    const sandboxCtx = document.getElementById('sandbox-executions-chart').getContext('2d');
    sandboxExecutionsChart = new Chart(sandboxCtx, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Failed'],
            datasets: [{
                label: 'Sandbox Executions',
                data: [0, 0],
                backgroundColor: [
                    '#27ae60',
                    '#c0392b'
                ]
            }]
        }
    });
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initCharts();
    updateAgentStatus();
    updateSystemStatus();
    logToSystem('System UI initialized');
});

// API Calls
async function startAllAgents() {
    logToSystem('Starting all agents...');
    try {
        const response = await fetch('/api/agents/start-all', { method: 'POST' });
        const data = await response.json();
        logToSystem(`Start all agents response: ${data.message}`);
        updateAgentStatus();
    } catch (error) {
        logToSystem(`Error starting agents: ${error.message}`, true);
    }
}

async function stopAllAgents() {
    logToSystem('Stopping all agents...');
    try {
        const response = await fetch('/api/agents/stop-all', { method: 'POST' });
        const data = await response.json();
        logToSystem(`Stop all agents response: ${data.message}`);
        updateAgentStatus();
    } catch (error) {
        logToSystem(`Error stopping agents: ${error.message}`, true);
    }
}

async function startAgent(agent) {
    logToSystem(`Starting ${agent} agent...`);
    try {
        const response = await fetch(`/api/agents/${agent}/start`, { method: 'POST' });
        const data = await response.json();
        logToSystem(`Start ${agent} agent response: ${data.message}`);
        updateAgentStatus();
    } catch (error) {
        logToSystem(`Error starting ${agent} agent: ${error.message}`, true);
    }
}

async function stopAgent(agent) {
    logToSystem(`Stopping ${agent} agent...`);
    try {
        const response = await fetch(`/api/agents/${agent}/stop`, { method: 'POST' });
        const data = await response.json();
        logToSystem(`Stop ${agent} agent response: ${data.message}`);
        updateAgentStatus();
    } catch (error) {
        logToSystem(`Error stopping ${agent} agent: ${error.message}`, true);
    }
}

async function setWebsiteUrl() {
    const url = websiteUrl.value.trim();
    if (!url) {
        logToSystem('Error: Please enter a valid URL', true);
        return;
    }
    
    logToSystem(`Setting website URL to: ${url}`);
    try {
        const response = await fetch('/api/config/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();
        logToSystem(`Set URL response: ${data.message}`);
    } catch (error) {
        logToSystem(`Error setting URL: ${error.message}`, true);
    }
}

async function testSandbox() {
    logToSystem('Testing ForeverVM sandbox...');
    sandboxStatus.textContent = 'Testing';
    sandboxStatus.className = 'status-badge running';
    
    try {
        const response = await fetch('/api/sandbox/test', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            logToSandbox(`Test successful: ${data.output}`);
            sandboxStatus.textContent = 'Ready';
            sandboxStatus.className = 'status-badge running';
            
            // Update chart
            sandboxExecutionsChart.data.datasets[0].data[0] += 1;
            sandboxExecutionsChart.update();
        } else {
            logToSandbox(`Test failed: ${data.error}`, true);
            sandboxStatus.textContent = 'Error';
            sandboxStatus.className = 'status-badge error';
            
            // Update chart
            sandboxExecutionsChart.data.datasets[0].data[1] += 1;
            sandboxExecutionsChart.update();
        }
    } catch (error) {
        logToSystem(`Error testing sandbox: ${error.message}`, true);
        logToSandbox(`Error: ${error.message}`, true);
        sandboxStatus.textContent = 'Error';
        sandboxStatus.className = 'status-badge error';
        
        // Update chart
        sandboxExecutionsChart.data.datasets[0].data[1] += 1;
        sandboxExecutionsChart.update();
    }
}

async function executeCode() {
    const code = codeToExecute.value.trim();
    if (!code) {
        logToSystem('Error: Please enter code to execute', true);
        return;
    }
    
    logToSystem('Executing code in ForeverVM sandbox...');
    sandboxStatus.textContent = 'Running';
    sandboxStatus.className = 'status-badge running';
    
    try {
        const response = await fetch('/api/sandbox/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        const data = await response.json();
        
        if (data.success) {
            logToSandbox(`Execution result:\n${data.output}`);
            if (data.return_value) {
                logToSandbox(`Return value: ${data.return_value}`);
            }
            sandboxStatus.textContent = 'Ready';
            sandboxStatus.className = 'status-badge running';
            
            // Update chart
            sandboxExecutionsChart.data.datasets[0].data[0] += 1;
            sandboxExecutionsChart.update();
        } else {
            logToSandbox(`Execution failed: ${data.error}`, true);
            sandboxStatus.textContent = 'Error';
            sandboxStatus.className = 'status-badge error';
            
            // Update chart
            sandboxExecutionsChart.data.datasets[0].data[1] += 1;
            sandboxExecutionsChart.update();
        }
    } catch (error) {
        logToSystem(`Error executing code: ${error.message}`, true);
        logToSandbox(`Error: ${error.message}`, true);
        sandboxStatus.textContent = 'Error';
        sandboxStatus.className = 'status-badge error';
        
        // Update chart
        sandboxExecutionsChart.data.datasets[0].data[1] += 1;
        sandboxExecutionsChart.update();
    }
}

async function updateAgentStatus() {
    try {
        const response = await fetch('/api/agents/status');
        const data = await response.json();
        
        for (const [agent, status] of Object.entries(data.agents)) {
            updateAgentCard(agent, status);
        }
        
        // Update activity chart
        const activityData = data.activity || [0, 0, 0, 0, 0];
        agentActivityChart.data.datasets[0].data = activityData;
        agentActivityChart.update();
    } catch (error) {
        logToSystem(`Error updating agent status: ${error.message}`, true);
    }
}

function updateAgentCard(agent, status) {
    const agentCard = document.getElementById(`agent-${agent}`);
    if (!agentCard) return;
    
    const statusElement = agentCard.querySelector('.agent-status');
    statusElement.textContent = status;
    
    // Update status class
    statusElement.className = 'agent-status';
    if (status === 'running') {
        statusElement.classList.add('running');
    } else if (status === 'error') {
        statusElement.classList.add('error');
    } else {
        statusElement.classList.add('idle');
    }
    
    // Update output if available
    if (status.output) {
        const outputElement = agentCard.querySelector('.output-text');
        outputElement.textContent = status.output;
    }
}

async function updateSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const data = await response.json();
        
        systemStatus.textContent = data.status;
        systemStatus.className = 'status-badge';
        
        if (data.status === 'running') {
            systemStatus.classList.add('running');
        } else if (data.status === 'error') {
            systemStatus.classList.add('error');
        } else {
            systemStatus.classList.add('idle');
        }
    } catch (error) {
        logToSystem(`Error updating system status: ${error.message}`, true);
    }
}

// Utility functions
function logToSystem(message, isError = false) {
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${message}`;
    
    const logElement = document.createElement('div');
    logElement.textContent = logMessage;
    if (isError) {
        logElement.style.color = 'var(--error-color)';
    }
    
    systemOutput.appendChild(logElement);
    systemOutput.scrollTop = systemOutput.scrollHeight;
}

function logToSandbox(message, isError = false) {
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${message}`;
    
    const logElement = document.createElement('div');
    logElement.textContent = logMessage;
    if (isError) {
        logElement.style.color = 'var(--error-color)';
    }
    
    sandboxOutput.appendChild(logElement);
    sandboxOutput.scrollTop = sandboxOutput.scrollHeight;
}

// Poll for updates every 5 seconds
setInterval(() => {
    updateAgentStatus();
    updateSystemStatus();
}, 5000);
    """
    
    with open(static_dir / "script.js", "w") as f:
        f.write(js)

# Routes for the web UI
@app.route('/')
def index():
    """Render the main UI page."""
    return render_template('index.html', config=CONFIG)

# API Routes
@app.route('/api/agents/status')
def get_agent_status():
    """Get the status of all agents."""
    # Read status from files if available
    agent_activity = []
    
    for agent in CONFIG["agents"]:
        try:
            status_file = os.path.join(CONFIG["multi_agent_dir"], agent, "output", "status.json")
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                agent_status[agent] = status_data.get("status", "idle")
                
                # Calculate activity for charts (mock data for now)
                if agent == "orchestrator":
                    agent_activity.append(10)
                elif agent == "crawler":
                    agent_activity.append(25)
                elif agent == "analysis":
                    agent_activity.append(15)
                elif agent == "implementation":
                    agent_activity.append(30)
                elif agent == "feedback":
                    agent_activity.append(20)
            else:
                agent_status[agent] = "idle"
                agent_activity.append(0)
        except Exception as e:
            agent_status[agent] = "error"
            log_message(f"Error getting {agent} status: {str(e)}")
            agent_activity.append(0)
    
    return jsonify({
        "agents": agent_status,
        "activity": agent_activity
    })

@app.route('/api/agents/start-all', methods=['POST'])
def start_all_agents():
    """Start all agents."""
    log_message("Starting all agents")
    
    # Start the orchestrator agent, which will start the others
    try:
        script_path = os.path.join(CONFIG["multi_agent_dir"], "orchestrator", "orchestrator_tasks.sh")
        
        if os.path.exists(script_path):
            process = subprocess.Popen(
                ['bash', script_path, 'start'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            agent_processes["orchestrator"] = process
            
            # Read initial output
            for i in range(3):  # Read a few lines for immediate feedback
                line = process.stdout.readline()
                if not line:
                    break
                log_message(f"Orchestrator: {line.strip()}")
            
            # Start output reader thread
            threading.Thread(
                target=read_process_output,
                args=(process, "orchestrator"),
                daemon=True
            ).start()
            
            return jsonify({"success": True, "message": "All agents starting"})
        else:
            log_message(f"Orchestrator script not found: {script_path}")
            return jsonify({"success": False, "message": "Orchestrator script not found"})
    except Exception as e:
        log_message(f"Error starting all agents: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/api/agents/stop-all', methods=['POST'])
def stop_all_agents():
    """Stop all agents."""
    log_message("Stopping all agents")
    
    for agent, process in agent_processes.items():
        try:
            if process and process.poll() is None:
                process.terminate()
                log_message(f"Terminated {agent} agent")
        except Exception as e:
            log_message(f"Error terminating {agent} agent: {str(e)}")
    
    agent_processes.clear()
    
    # Update status files
    for agent in CONFIG["agents"]:
        try:
            status_file = os.path.join(CONFIG["multi_agent_dir"], agent, "output", "status.json")
            status_data = {
                "status": "idle",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
            os.makedirs(os.path.dirname(status_file), exist_ok=True)
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            log_message(f"Error updating {agent} status file: {str(e)}")
    
    return jsonify({"success": True, "message": "All agents stopped"})

@app.route('/api/agents/<agent>/start', methods=['POST'])
def start_agent(agent):
    """Start a specific agent."""
    if agent not in CONFIG["agents"]:
        return jsonify({"success": False, "message": f"Unknown agent: {agent}"})
    
    log_message(f"Starting {agent} agent")
    
    try:
        script_path = os.path.join(CONFIG["multi_agent_dir"], agent, f"{agent}_tasks.sh")
        
        if os.path.exists(script_path):
            process = subprocess.Popen(
                ['bash', script_path, 'start'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            agent_processes[agent] = process
            
            # Read initial output
            for i in range(3):  # Read a few lines for immediate feedback
                line = process.stdout.readline()
                if not line:
                    break
                log_message(f"{agent}: {line.strip()}")
            
            # Start output reader thread
            threading.Thread(
                target=read_process_output,
                args=(process, agent),
                daemon=True
            ).start()
            
            return jsonify({"success": True, "message": f"{agent} agent started"})
        else:
            log_message(f"{agent} script not found: {script_path}")
            return jsonify({"success": False, "message": f"{agent} script not found"})
    except Exception as e:
        log_message(f"Error starting {agent} agent: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/api/agents/<agent>/stop', methods=['POST'])
def stop_agent(agent):
    """Stop a specific agent."""
    if agent not in CONFIG["agents"]:
        return jsonify({"success": False, "message": f"Unknown agent: {agent}"})
    
    log_message(f"Stopping {agent} agent")
    
    try:
        if agent in agent_processes and agent_processes[agent].poll() is None:
            agent_processes[agent].terminate()
            del agent_processes[agent]
            
            # Update status file
            status_file = os.path.join(CONFIG["multi_agent_dir"], agent, "output", "status.json")
            status_data = {
                "status": "idle",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
            os.makedirs(os.path.dirname(status_file), exist_ok=True)
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            return jsonify({"success": True, "message": f"{agent} agent stopped"})
        else:
            script_path = os.path.join(CONFIG["multi_agent_dir"], agent, f"{agent}_tasks.sh")
            
            if os.path.exists(script_path):
                subprocess.run(['bash', script_path, 'stop'], check=True)
                return jsonify({"success": True, "message": f"{agent} agent stopped"})
            else:
                log_message(f"{agent} stop script not found")
                return jsonify({"success": False, "message": f"{agent} script not found"})
    except Exception as e:
        log_message(f"Error stopping {agent} agent: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/api/system/status')
def get_system_status():
    """Get the overall system status."""
    # Check if any agent is running
    any_running = any(status == "running" for status in agent_status.values())
    any_error = any(status == "error" for status in agent_status.values())
    
    if any_error:
        status = "error"
    elif any_running:
        status = "running"
    else:
        status = "idle"
    
    return jsonify({
        "status": status,
        "agents_running": list(agent for agent, status in agent_status.items() if status == "running"),
        "agents_error": list(agent for agent, status in agent_status.items() if status == "error")
    })

@app.route('/api/config/url', methods=['POST'])
def set_website_url():
    """Set the website URL to clone."""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"success": False, "message": "No URL provided"})
    
    log_message(f"Setting website URL to: {url}")
    
    # Save URL to a configuration file
    config_file = os.path.join(CONFIG["multi_agent_dir"], "shared", "config.json")
    
    try:
        config_data = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        
        config_data["website_url"] = url
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return jsonify({"success": True, "message": "URL set successfully"})
    except Exception as e:
        log_message(f"Error setting URL: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

@app.route('/api/sandbox/test', methods=['POST'])
def test_sandbox():
    """Test the ForeverVM sandbox."""
    if not FOREVERVM_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "ForeverVM integration not available"
        })
    
    log_message("Testing ForeverVM sandbox")
    
    try:
        with ForeverVMSandbox() as sandbox:
            # Simple test code
            test_code = """
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print("ForeverVM sandbox is working!")

# Return a success message
"Sandbox test successful"
"""
            result = sandbox.execute_code(test_code)
            return jsonify(result)
    except Exception as e:
        log_message(f"Error testing sandbox: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/sandbox/execute', methods=['POST'])
def execute_in_sandbox():
    """Execute code in the ForeverVM sandbox."""
    if not FOREVERVM_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "ForeverVM integration not available"
        })
    
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({
            "success": False,
            "error": "No code provided"
        })
    
    log_message("Executing code in ForeverVM sandbox")
    
    try:
        with ForeverVMSandbox() as sandbox:
            result = sandbox.execute_code(code)
            return jsonify(result)
    except Exception as e:
        log_message(f"Error executing code: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

# Helper functions
def read_process_output(process, agent):
    """Read and log output from a subprocess."""
    try:
        for line in process.stdout:
            log_message(f"{agent}: {line.strip()}")
        
        # Check for errors
        for line in process.stderr:
            log_message(f"{agent} ERROR: {line.strip()}")
    except Exception as e:
        log_message(f"Error reading {agent} output: {str(e)}")
    
    # Process ended
    exit_code = process.wait()
    log_message(f"{agent} process ended with exit code {exit_code}")
    
    # Update status based on exit code
    status = "idle" if exit_code == 0 else "error"
    agent_status[agent] = status
    
    # Update status file
    try:
        status_file = os.path.join(CONFIG["multi_agent_dir"], agent, "output", "status.json")
        status_data = {
            "status": status,
            "exit_code": exit_code,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        os.makedirs(os.path.dirname(status_file), exist_ok=True)
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        log_message(f"Error updating {agent} status file: {str(e)}")

def log_message(message):
    """Log a message to the log file and console."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    try:
        with open(CONFIG["log_file"], 'a') as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")

# Main entry point
if __name__ == "__main__":
    # Create templates and static files
    create_templates()
    
    # Log startup information
    log_message("Starting Multi-Agent System UI")
    log_message(f"ForeverVM available: {FOREVERVM_AVAILABLE}")
    
    # Run Flask app
    print(f"UI is running at: http://127.0.0.1:5000")
    print(f"You can also access it at: http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)