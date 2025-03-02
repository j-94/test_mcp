
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
            logToSandbox(`Execution result:
${data.output}`);
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
    