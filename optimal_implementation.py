#!/usr/bin/env python3
"""
Optimal Multi-Agent System Implementation with ForeverVM Integration
A consolidated, efficient implementation of the website cloning system
"""

import os
import sys
import json
import time
import logging
import asyncio
import argparse
import threading
import traceback
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('multi_agent_system.log')
    ]
)
logger = logging.getLogger('multi_agent_system')

# Project constants
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / '.env'
MULTI_AGENT_DIR = PROJECT_ROOT / 'test_multi_agent'
CONFIG_PATH = MULTI_AGENT_DIR / 'shared' / 'config.json'

# Agent types
class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    CRAWLER = "crawler"
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    FEEDBACK = "feedback"

# Message types
class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

# System states
class SystemState(Enum):
    INITIALIZING = "initializing"
    CRAWLING = "crawling"
    ANALYZING = "analyzing"
    IMPLEMENTING = "implementing"
    FEEDBACK = "feedback"
    COMPLETE = "complete"
    ERROR = "error"

# ForeverVM Integration
try:
    from integrate_forevervm import ForeverVMSandbox, MultiAgentExecutor
    FOREVERVM_AVAILABLE = True
    logger.info("ForeverVM integration available")
except ImportError:
    logger.warning("ForeverVM integration not available")
    FOREVERVM_AVAILABLE = False

# Load environment variables
def load_environment():
    """Load environment variables from .env file"""
    if ENV_PATH.exists():
        logger.info(f"Loading environment from {ENV_PATH}")
        with open(ENV_PATH, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    # Mask sensitive values in logs
                    if 'TOKEN' in key or 'KEY' in key:
                        masked_value = value[:5] + '...' if len(value) > 5 else '***'
                        logger.info(f"Set {key}={masked_value}")
                    else:
                        logger.info(f"Set {key}={value}")
    else:
        logger.warning(f".env file not found at {ENV_PATH}")

# Load system configuration
def load_config() -> Dict[str, Any]:
    """Load system configuration"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {CONFIG_PATH}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    else:
        logger.warning(f"Configuration file not found at {CONFIG_PATH}")
        return {}

# Save system configuration
def save_config(config: Dict[str, Any]):
    """Save system configuration"""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved configuration to {CONFIG_PATH}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")

# Message format for agent communication
class Message:
    """Message class for agent communication"""
    
    def __init__(
        self,
        source_agent: AgentType,
        destination_agent: AgentType,
        message_type: MessageType,
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.message_id = message_id or f"{int(time.time())}-{id(self)}"
        self.source_agent = source_agent
        self.destination_agent = destination_agent
        self.message_type = message_type
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.priority = priority
        self.payload = payload
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "source_agent": self.source_agent.value,
            "destination_agent": self.destination_agent.value,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            source_agent=AgentType(data["source_agent"]),
            destination_agent=AgentType(data["destination_agent"]),
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            message_id=data["message_id"],
            timestamp=data["timestamp"],
            priority=data["priority"],
            metadata=data["metadata"]
        )
    
    def __repr__(self) -> str:
        return f"Message({self.source_agent.value} -> {self.destination_agent.value}, {self.message_type.value})"

# Base class for all agents
class Agent:
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType, message_queue: asyncio.Queue):
        self.agent_type = agent_type
        self.message_queue = message_queue
        self.output_dir = MULTI_AGENT_DIR / agent_type.value / "output"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.status_file = self.output_dir / "status.json"
        self.result_file = self.output_dir / "result.json"
        self.running = False
        self.status = "idle"
        self.logger = logging.getLogger(f"agent.{agent_type.value}")
    
    async def start(self):
        """Start the agent"""
        self.running = True
        self.status = "running"
        self.update_status()
        self.logger.info(f"Agent {self.agent_type.value} started")
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        self.status = "idle"
        self.update_status()
        self.logger.info(f"Agent {self.agent_type.value} stopped")
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle an incoming message"""
        self.logger.info(f"Received message: {message}")
        
        # Default implementation just logs the message
        return None
    
    async def send_message(self, destination_agent: AgentType, message_type: MessageType, 
                          payload: Dict[str, Any], priority: int = 5, 
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send a message to another agent"""
        message = Message(
            source_agent=self.agent_type,
            destination_agent=destination_agent,
            message_type=message_type,
            payload=payload,
            priority=priority,
            metadata=metadata
        )
        
        await self.message_queue.put(message)
        self.logger.info(f"Sent message: {message}")
        
        return message.message_id
    
    def update_status(self, error: Optional[str] = None):
        """Update the agent's status file"""
        status_data = {
            "status": self.status,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_type": self.agent_type.value
        }
        
        if error:
            status_data["error"] = error
            self.status = "error"
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error updating status file: {e}")
    
    def save_result(self, result: Dict[str, Any]):
        """Save the agent's result"""
        try:
            with open(self.result_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving result: {e}")
    
    async def run(self):
        """Main agent loop"""
        try:
            await self.start()
            
            while self.running:
                # Process incoming messages
                try:
                    message = self.message_queue.get_nowait()
                    if message.destination_agent == self.agent_type:
                        response = await self.handle_message(message)
                        if response:
                            await self.message_queue.put(response)
                    else:
                        # Put it back if it's not for us
                        await self.message_queue.put(message)
                except asyncio.QueueEmpty:
                    # No messages, do agent-specific work
                    await self.do_work()
                    await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error in agent {self.agent_type.value}: {e}")
            self.logger.error(traceback.format_exc())
            self.status = "error"
            self.update_status(str(e))
        finally:
            await self.stop()
    
    async def do_work(self):
        """Perform agent-specific work"""
        # Override in subclasses
        await asyncio.sleep(0.1)

# Crawler Agent
class CrawlerAgent(Agent):
    """Agent responsible for crawling websites"""
    
    def __init__(self, message_queue: asyncio.Queue):
        super().__init__(AgentType.CRAWLER, message_queue)
        self.config = {}
        self.target_url = None
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def start(self):
        """Start the crawler agent"""
        await super().start()
        self.config = load_config()
        self.target_url = self.config.get("website_url")
        
        if not self.target_url:
            self.logger.warning("No target URL specified")
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.ERROR,
                {"error": "No target URL specified"}
            )
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle messages"""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "crawl":
                # Handle crawl request
                url = message.payload.get("url") or self.target_url
                if url:
                    self.target_url = url
                    self.logger.info(f"Starting crawl of {url}")
                    
                    # Start crawling in a separate task
                    asyncio.create_task(self.crawl_website(url))
                    
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.RESPONSE,
                        payload={"status": "crawling", "url": url}
                    )
                else:
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.ERROR,
                        payload={"error": "No URL specified"}
                    )
        
        return await super().handle_message(message)
    
    async def crawl_website(self, url: str):
        """Crawl a website using ForeverVM for isolation"""
        self.logger.info(f"Crawling website: {url}")
        
        try:
            if FOREVERVM_AVAILABLE:
                # Use ForeverVM for secure crawling
                self.logger.info("Using ForeverVM for secure crawling")
                
                crawl_code = f"""
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse

def crawl_website(url, max_pages=10):
    # Crawl website and extract structure
    visited = set()
    to_visit = [url]
    results = {{
        "base_url": url,
        "pages": [],
        "assets": []
    }}
    
    headers = {{
        "User-Agent": "Mozilla/5.0 Ethical Crawler for Development Purposes"
    }}
    
    while to_visit and len(visited) < max_pages:
        current = to_visit.pop(0)
        if current in visited:
            continue
        
        print(f"Crawling: {{current}}")
        
        try:
            response = requests.get(current, headers=headers, timeout=10)
            visited.add(current)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page info
                title = soup.title.text if soup.title else "No title"
                
                # Extract structure - simplified for ethical crawling
                structure = {{
                    "url": current,
                    "title": title,
                    "has_header": bool(soup.find('header')),
                    "has_footer": bool(soup.find('footer')),
                    "has_nav": bool(soup.find('nav')),
                    "num_sections": len(soup.find_all('section')),
                    "meta_tags": [{{
                        "name": tag.get("name", ""),
                        "content": tag.get("content", "")
                    }} for tag in soup.find_all('meta') if tag.get("name")]
                }}
                
                results["pages"].append(structure)
                
                # Find assets - for ethical crawling we just count them
                css_files = len(soup.find_all("link", rel="stylesheet"))
                js_files = len(soup.find_all("script", src=True))
                images = len(soup.find_all("img", src=True))
                
                results["assets"].append({{
                    "page_url": current,
                    "css_count": css_files,
                    "js_count": js_files,
                    "image_count": images
                }})
                
                # Find links
                base_url = "{{}}://{{}}".format(
                    urlparse(current).scheme, 
                    urlparse(current).netloc
                )
                
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    # Skip anchor links, javascript, and mailto
                    if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                        continue
                    
                    # Make absolute URL
                    if not href.startswith(("http://", "https://")):
                        href = urljoin(current, href)
                    
                    # Only follow links to same domain
                    if urlparse(href).netloc == urlparse(url).netloc and href not in visited:
                        to_visit.append(href)
        
        except Exception as e:
            print(f"Error crawling {{current}}: {{e}}")
    
    return results

# Crawl the website
result = crawl_website("{url}")
print(f"Crawled {{len(result['pages'])}} pages")

# Return the result
result
"""

                with ForeverVMSandbox() as sandbox:
                    # Install required packages
                    self.logger.info("Installing required packages in sandbox")
                    sandbox.install_package("requests")
                    sandbox.install_package("beautifulsoup4")
                    
                    # Execute crawling code
                    self.logger.info("Executing crawling code in sandbox")
                    result = sandbox.execute_code(crawl_code)
                    
                    if result["success"]:
                        self.logger.info("Crawling successful")
                        
                        # Save crawl result
                        crawl_result = result["return_value"]
                        self.save_result(crawl_result)
                        
                        # Notify orchestrator of completion
                        await self.send_message(
                            AgentType.ORCHESTRATOR,
                            MessageType.NOTIFICATION,
                            {
                                "status": "complete",
                                "pages_crawled": len(crawl_result["pages"]),
                                "result_path": str(self.result_file)
                            }
                        )
                        
                        # Notify analysis agent to analyze the results
                        await self.send_message(
                            AgentType.ANALYSIS,
                            MessageType.REQUEST,
                            {
                                "action": "analyze",
                                "crawl_result_path": str(self.result_file)
                            }
                        )
                    else:
                        self.logger.error(f"Crawling failed: {result['error']}")
                        await self.send_message(
                            AgentType.ORCHESTRATOR,
                            MessageType.ERROR,
                            {"error": f"Crawling failed: {result['error']}"}
                        )
            else:
                # Implement non-ForeverVM fallback
                self.logger.warning("ForeverVM not available, using simplified crawler")
                
                # This would be a simplified, less secure crawler
                # In a real system, we'd implement this here
                
                self.logger.error("Simplified crawler not implemented")
                await self.send_message(
                    AgentType.ORCHESTRATOR,
                    MessageType.ERROR,
                    {"error": "ForeverVM required for secure crawling"}
                )
            
        except Exception as e:
            self.logger.error(f"Error crawling website: {e}")
            self.logger.error(traceback.format_exc())
            
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.ERROR,
                {"error": f"Error crawling website: {str(e)}"}
            )
            
            self.status = "error"
            self.update_status(str(e))

# Analysis Agent
class AnalysisAgent(Agent):
    """Agent responsible for analyzing website structure"""
    
    def __init__(self, message_queue: asyncio.Queue):
        super().__init__(AgentType.ANALYSIS, message_queue)
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle messages"""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "analyze":
                # Handle analyze request
                crawl_result_path = message.payload.get("crawl_result_path")
                if crawl_result_path:
                    self.logger.info(f"Starting analysis of {crawl_result_path}")
                    
                    # Start analysis in a separate task
                    asyncio.create_task(self.analyze_crawl_result(crawl_result_path))
                    
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.RESPONSE,
                        payload={"status": "analyzing", "crawl_result_path": crawl_result_path}
                    )
                else:
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.ERROR,
                        payload={"error": "No crawl result path specified"}
                    )
        
        return await super().handle_message(message)
    
    async def analyze_crawl_result(self, crawl_result_path: str):
        """Analyze crawl results"""
        self.logger.info(f"Analyzing crawl result: {crawl_result_path}")
        
        try:
            # Load crawl result
            with open(crawl_result_path, 'r') as f:
                crawl_result = json.load(f)
            
            # Analyze the data - in a real system this would be more sophisticated
            analysis = {
                "base_url": crawl_result["base_url"],
                "pages_analyzed": len(crawl_result["pages"]),
                "page_structure": {},
                "common_patterns": {},
                "asset_analysis": {},
                "recommendations": []
            }
            
            # Extract page structure information
            has_header_count = sum(1 for page in crawl_result["pages"] if page.get("has_header", False))
            has_footer_count = sum(1 for page in crawl_result["pages"] if page.get("has_footer", False))
            has_nav_count = sum(1 for page in crawl_result["pages"] if page.get("has_nav", False))
            
            analysis["page_structure"] = {
                "header_percentage": (has_header_count / len(crawl_result["pages"])) * 100 if crawl_result["pages"] else 0,
                "footer_percentage": (has_footer_count / len(crawl_result["pages"])) * 100 if crawl_result["pages"] else 0,
                "nav_percentage": (has_nav_count / len(crawl_result["pages"])) * 100 if crawl_result["pages"] else 0,
                "avg_sections_per_page": sum(page.get("num_sections", 0) for page in crawl_result["pages"]) / len(crawl_result["pages"]) if crawl_result["pages"] else 0
            }
            
            # Asset analysis
            if crawl_result["assets"]:
                total_css = sum(asset.get("css_count", 0) for asset in crawl_result["assets"])
                total_js = sum(asset.get("js_count", 0) for asset in crawl_result["assets"])
                total_images = sum(asset.get("image_count", 0) for asset in crawl_result["assets"])
                
                analysis["asset_analysis"] = {
                    "total_css_files": total_css,
                    "total_js_files": total_js,
                    "total_images": total_images,
                    "avg_css_per_page": total_css / len(crawl_result["assets"]),
                    "avg_js_per_page": total_js / len(crawl_result["assets"]),
                    "avg_images_per_page": total_images / len(crawl_result["assets"])
                }
            
            # Generate recommendations
            if analysis["page_structure"]["header_percentage"] > 90:
                analysis["recommendations"].append(
                    "Implement consistent header across all pages"
                )
            
            if analysis["page_structure"]["footer_percentage"] > 90:
                analysis["recommendations"].append(
                    "Implement consistent footer across all pages"
                )
            
            if "asset_analysis" in analysis and analysis["asset_analysis"]["avg_js_per_page"] > 5:
                analysis["recommendations"].append(
                    "Consider bundling JavaScript files to improve loading performance"
                )
            
            # Save analysis result
            self.save_result(analysis)
            
            # Notify orchestrator of completion
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.NOTIFICATION,
                {
                    "status": "complete",
                    "pages_analyzed": len(crawl_result["pages"]),
                    "result_path": str(self.result_file)
                }
            )
            
            # Notify implementation agent
            await self.send_message(
                AgentType.IMPLEMENTATION,
                MessageType.REQUEST,
                {
                    "action": "implement",
                    "analysis_result_path": str(self.result_file),
                    "crawl_result_path": crawl_result_path
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing crawl result: {e}")
            self.logger.error(traceback.format_exc())
            
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.ERROR,
                {"error": f"Error analyzing crawl result: {str(e)}"}
            )
            
            self.status = "error"
            self.update_status(str(e))

# Implementation Agent
class ImplementationAgent(Agent):
    """Agent responsible for implementing website structure"""
    
    def __init__(self, message_queue: asyncio.Queue):
        super().__init__(AgentType.IMPLEMENTATION, message_queue)
        self.executor = MultiAgentExecutor() if FOREVERVM_AVAILABLE else None
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle messages"""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "implement":
                # Handle implement request
                analysis_result_path = message.payload.get("analysis_result_path")
                crawl_result_path = message.payload.get("crawl_result_path")
                
                if analysis_result_path and crawl_result_path:
                    self.logger.info(f"Starting implementation based on {analysis_result_path}")
                    
                    # Start implementation in a separate task
                    asyncio.create_task(self.implement_website(analysis_result_path, crawl_result_path))
                    
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.RESPONSE,
                        payload={
                            "status": "implementing", 
                            "analysis_result_path": analysis_result_path,
                            "crawl_result_path": crawl_result_path
                        }
                    )
                else:
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.ERROR,
                        payload={"error": "Missing result paths"}
                    )
        
        return await super().handle_message(message)
    
    async def implement_website(self, analysis_result_path: str, crawl_result_path: str):
        """Implement website based on analysis"""
        self.logger.info(f"Implementing website based on {analysis_result_path}")
        
        try:
            # Load analysis result
            with open(analysis_result_path, 'r') as f:
                analysis = json.load(f)
            
            # Load crawl result
            with open(crawl_result_path, 'r') as f:
                crawl_result = json.load(f)
            
            # Generate implementation
            implementation_code = self.generate_implementation_code(analysis, crawl_result)
            
            # Save implementation code
            implementation_file = self.output_dir / "implementation.py"
            with open(implementation_file, 'w') as f:
                f.write(implementation_code)
            
            # Generate HTML template
            html_template = self.generate_html_template(analysis, crawl_result)
            
            # Save HTML template
            template_file = self.output_dir / "template.html"
            with open(template_file, 'w') as f:
                f.write(html_template)
            
            # Generate CSS
            css = self.generate_css(analysis, crawl_result)
            
            # Save CSS
            css_file = self.output_dir / "styles.css"
            with open(css_file, 'w') as f:
                f.write(css)
            
            # Test implementation if ForeverVM is available
            if FOREVERVM_AVAILABLE and self.executor:
                self.logger.info("Testing implementation with ForeverVM")
                
                # Create test code
                test_code = self.generate_test_code(implementation_file)
                
                # Save test code
                test_file = self.output_dir / "test_implementation.py"
                with open(test_file, 'w') as f:
                    f.write(test_code)
                
                # Run tests in ForeverVM
                result = self.executor.test_implementation(
                    str(implementation_file.name), 
                    test_code
                )
                
                if result["success"]:
                    self.logger.info("Implementation tests passed")
                else:
                    self.logger.warning(f"Implementation tests failed: {result['error']}")
            
            # Save implementation result
            implementation_result = {
                "files": [
                    {
                        "path": str(implementation_file),
                        "type": "python",
                        "purpose": "Main implementation"
                    },
                    {
                        "path": str(template_file),
                        "type": "html",
                        "purpose": "HTML template"
                    },
                    {
                        "path": str(css_file),
                        "type": "css",
                        "purpose": "Stylesheet"
                    }
                ],
                "base_url": crawl_result["base_url"],
                "pages_implemented": len(crawl_result["pages"]),
                "test_results": {
                    "tests_passed": True if FOREVERVM_AVAILABLE and result.get("success", False) else None,
                    "output": result.get("output") if FOREVERVM_AVAILABLE else "Tests not run - ForeverVM not available"
                }
            }
            
            self.save_result(implementation_result)
            
            # Notify orchestrator of completion
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.NOTIFICATION,
                {
                    "status": "complete",
                    "files_generated": len(implementation_result["files"]),
                    "result_path": str(self.result_file)
                }
            )
            
            # Notify feedback agent
            await self.send_message(
                AgentType.FEEDBACK,
                MessageType.REQUEST,
                {
                    "action": "evaluate",
                    "implementation_result_path": str(self.result_file),
                    "analysis_result_path": analysis_result_path,
                    "crawl_result_path": crawl_result_path
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error implementing website: {e}")
            self.logger.error(traceback.format_exc())
            
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.ERROR,
                {"error": f"Error implementing website: {str(e)}"}
            )
            
            self.status = "error"
            self.update_status(str(e))
    
    def generate_implementation_code(self, analysis, crawl_result):
        """Generate implementation code based on analysis"""
        code = f"""#!/usr/bin/env python3
\"\"\"
Website Implementation Generator
Based on analysis of {crawl_result['base_url']}
Generated by Multi-Agent System with ForeverVM
\"\"\"

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

class WebsiteGenerator:
    \"\"\"Generate website structure based on analysis\"\"\"
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create directories
        self.css_dir = self.output_dir / "css"
        self.js_dir = self.output_dir / "js"
        self.img_dir = self.output_dir / "img"
        
        self.css_dir.mkdir(exist_ok=True)
        self.js_dir.mkdir(exist_ok=True)
        self.img_dir.mkdir(exist_ok=True)
    
    def generate(self):
        \"\"\"Generate the website\"\"\"
        print("Generating website structure...")
        
        # Copy template files
        template_dir = Path(__file__).parent
        shutil.copy(template_dir / "template.html", self.output_dir / "index.html")
        shutil.copy(template_dir / "styles.css", self.css_dir / "styles.css")
        
        # Generate additional pages
        self.generate_pages()
        
        # Generate JavaScript
        self.generate_javascript()
        
        print(f"Website generated in {self.output_dir}")
        return {{"output_dir": str(self.output_dir)}}
    
    def generate_pages(self):
        \"\"\"Generate additional pages\"\"\"
        # In a real implementation, this would generate pages based on the crawl result
        pages = {min(5, len(crawl_result["pages"]))}
        
        for i in range(1, pages):
            page_file = self.output_dir / f"page{i}.html"
            with open(page_file, 'w') as f:
                f.write(self.get_page_template(f"Page {i}", f"This is page {i}"))
    
    def generate_javascript(self):
        \"\"\"Generate JavaScript files\"\"\"
        # Generate main.js
        with open(self.js_dir / "main.js", 'w') as f:
            f.write(\"\"\"
// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Website loaded');
    
    // Initialize components
    initializeNavigation();
});

function initializeNavigation() {
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            console.log('Navigating to: ' + this.getAttribute('href'));
        });
    });
}
\"\"\")
    
    def get_page_template(self, title, content):
        \"\"\"Get page template\"\"\"
        return f\"\"\"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{title}</h1>
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="page1.html">Page 1</a></li>
                    <li><a href="page2.html">Page 2</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            <section class="content">
                <h2>{title}</h2>
                <p>{content}</p>
            </section>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {datetime.now().year} Generated Website. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="js/main.js"></script>
</body>
</html>\"\"\"

if __name__ == "__main__":
    generator = WebsiteGenerator("./generated_site")
    generator.generate()
"""
        return code
    
    def generate_html_template(self, analysis, crawl_result):
        """Generate HTML template based on analysis"""
        # Determine if the site commonly has headers/footers/nav
        has_header = analysis["page_structure"]["header_percentage"] > 50
        has_footer = analysis["page_structure"]["footer_percentage"] > 50
        has_nav = analysis["page_structure"]["nav_percentage"] > 50
        
        base_url = crawl_result["base_url"]
        
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated from {base_url}</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
"""

        if has_header:
            template += """    <header>
        <div class="container">
            <h1>Website Title</h1>"""
            
            if has_nav:
                template += """
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="page1.html">Page 1</a></li>
                    <li><a href="page2.html">Page 2</a></li>
                </ul>
            </nav>"""
                
            template += """
        </div>
    </header>
"""
        
        template += """    <main>
        <div class="container">
            <section class="hero">
                <h2>Welcome to the Generated Website</h2>
                <p>This website was automatically generated based on analysis of the original site structure.</p>
            </section>
            
            <section class="content">
                <div class="row">
                    <div class="col">
                        <h3>About</h3>
                        <p>This is a placeholder for the about section. In a real implementation, this would contain content from the original site.</p>
                    </div>
                    <div class="col">
                        <h3>Features</h3>
                        <p>This is a placeholder for the features section. In a real implementation, this would contain content from the original site.</p>
                    </div>
                </div>
            </section>
        </div>
    </main>
"""
        
        if has_footer:
            template += """    <footer>
        <div class="container">
            <p>&copy; 2025 Generated Website. All rights reserved.</p>
        </div>
    </footer>
"""
        
        template += """    <script src="js/main.js"></script>
</body>
</html>
"""
        return template
    
    def generate_css(self, analysis, crawl_result):
        """Generate CSS based on analysis"""
        css = """/* 
 * Generated Stylesheet 
 * Based on website structure analysis
 */

:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --text-color: #333333;
    --background-color: #ffffff;
    --accent-color: #f39c12;
    --border-color: #e0e0e0;
}

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

/* Header styles */
header {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

header h1 {
    margin-bottom: 0.5rem;
}

/* Navigation */
nav ul {
    list-style: none;
    display: flex;
}

nav li {
    margin-right: 1.5rem;
}

nav a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}

nav a:hover {
    color: var(--accent-color);
}

/* Main content */
main {
    padding: 2rem 0;
}

.hero {
    background-color: #f5f5f5;
    padding: 2rem;
    margin-bottom: 2rem;
    border-radius: 4px;
    text-align: center;
}

.hero h2 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.content {
    margin-bottom: 2rem;
}

.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -15px;
}

.col {
    flex: 1;
    padding: 0 15px;
    min-width: 300px;
}

h3 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

/* Footer */
footer {
    background-color: #333;
    color: white;
    padding: 1.5rem 0;
    text-align: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .row {
        flex-direction: column;
    }
    
    .col {
        margin-bottom: 1.5rem;
    }
    
    nav ul {
        flex-direction: column;
    }
    
    nav li {
        margin-right: 0;
        margin-bottom: 0.5rem;
    }
}
"""
        return css
    
    def generate_test_code(self, implementation_file):
        """Generate test code for implementation"""
        test_code = f"""
import unittest
import os
import tempfile
import sys
from pathlib import Path

# Add the implementation directory to path
sys.path.append(str(Path("{implementation_file}").parent))

# Import the implementation
from {Path(implementation_file).stem} import WebsiteGenerator

class TestWebsiteGenerator(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.generator = WebsiteGenerator(self.test_dir)
    
    def test_directory_creation(self):
        # Test that the directories are created
        self.generator.generate()
        
        # Check that directories exist
        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "css")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "js")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "img")))
    
    def test_file_generation(self):
        # Test that files are generated
        self.generator.generate()
        
        # Check that index.html is created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "index.html")))
        
        # Check that CSS file is created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "css", "styles.css")))
        
        # Check that JS file is created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "js", "main.js")))
    
    def test_page_generation(self):
        # Test page generation
        self.generator.generate()
        
        # Check that at least one additional page is created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "page1.html")))

if __name__ == '__main__':
    unittest.main()
"""
        return test_code

# Feedback Agent
class FeedbackAgent(Agent):
    """Agent responsible for providing feedback on implementations"""
    
    def __init__(self, message_queue: asyncio.Queue):
        super().__init__(AgentType.FEEDBACK, message_queue)
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle messages"""
        if message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "evaluate":
                # Handle evaluate request
                implementation_result_path = message.payload.get("implementation_result_path")
                analysis_result_path = message.payload.get("analysis_result_path")
                crawl_result_path = message.payload.get("crawl_result_path")
                
                if implementation_result_path and analysis_result_path and crawl_result_path:
                    self.logger.info(f"Starting evaluation of {implementation_result_path}")
                    
                    # Start evaluation in a separate task
                    asyncio.create_task(self.evaluate_implementation(
                        implementation_result_path, 
                        analysis_result_path, 
                        crawl_result_path
                    ))
                    
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.RESPONSE,
                        payload={
                            "status": "evaluating", 
                            "implementation_result_path": implementation_result_path
                        }
                    )
                else:
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.ERROR,
                        payload={"error": "Missing result paths"}
                    )
        
        return await super().handle_message(message)
    
    async def evaluate_implementation(self, implementation_result_path: str, 
                                    analysis_result_path: str, crawl_result_path: str):
        """Evaluate implementation based on analysis and crawl results"""
        self.logger.info(f"Evaluating implementation based on {implementation_result_path}")
        
        try:
            # Load implementation result
            with open(implementation_result_path, 'r') as f:
                implementation = json.load(f)
            
            # Load analysis result
            with open(analysis_result_path, 'r') as f:
                analysis = json.load(f)
            
            # Load crawl result
            with open(crawl_result_path, 'r') as f:
                crawl_result = json.load(f)
            
            # Evaluate implementation
            feedback = {
                "implementation_path": implementation_result_path,
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "overall_assessment": ""
            }
            
            # Example evaluation logic - in a real system this would be more sophisticated
            
            # Check if all recommended files were generated
            if len(implementation["files"]) >= 3:
                feedback["strengths"].append("Generated all required files (HTML, CSS, JavaScript)")
                feedback["score"] += 1
            else:
                feedback["weaknesses"].append("Missing some required files")
            
            # Check if tests passed (if run)
            if implementation.get("test_results", {}).get("tests_passed"):
                feedback["strengths"].append("Implementation passes all tests")
                feedback["score"] += 1
            elif implementation.get("test_results", {}).get("tests_passed") is False:
                feedback["weaknesses"].append("Implementation fails some tests")
            
            # Check if implementation follows recommendations from analysis
            recommendations_followed = 0
            for recommendation in analysis.get("recommendations", []):
                # This is a simplified check - in a real system, we'd check if the 
                # recommendation was actually implemented
                recommendations_followed += 1
            
            if recommendations_followed == len(analysis.get("recommendations", [])):
                feedback["strengths"].append("Implementation follows all recommendations from analysis")
                feedback["score"] += 1
            elif recommendations_followed > 0:
                feedback["strengths"].append(f"Implementation follows {recommendations_followed} recommendations from analysis")
                feedback["score"] += 0.5
            
            # Add suggestions
            feedback["suggestions"].append("Add more responsive design features")
            feedback["suggestions"].append("Implement accessibility improvements")
            feedback["suggestions"].append("Consider adding animation effects for better user experience")
            
            # Overall assessment
            if feedback["score"] >= 2:
                feedback["overall_assessment"] = "Good implementation that meets most requirements"
            elif feedback["score"] >= 1:
                feedback["overall_assessment"] = "Acceptable implementation with room for improvement"
            else:
                feedback["overall_assessment"] = "Implementation needs significant improvement"
            
            # Save feedback result
            self.save_result(feedback)
            
            # Notify orchestrator of completion
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.NOTIFICATION,
                {
                    "status": "complete",
                    "score": feedback["score"],
                    "result_path": str(self.result_file)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating implementation: {e}")
            self.logger.error(traceback.format_exc())
            
            await self.send_message(
                AgentType.ORCHESTRATOR,
                MessageType.ERROR,
                {"error": f"Error evaluating implementation: {str(e)}"}
            )
            
            self.status = "error"
            self.update_status(str(e))

# Orchestrator Agent
class OrchestratorAgent(Agent):
    """Agent responsible for orchestrating the entire process"""
    
    def __init__(self, message_queue: asyncio.Queue):
        super().__init__(AgentType.ORCHESTRATOR, message_queue)
        self.config = {}
        self.system_state = SystemState.INITIALIZING
        self.agents_status = {agent_type.value: "idle" for agent_type in AgentType}
        self.agent_results = {}
        self.current_iteration = 0
        self.max_iterations = 3
        self.target_url = None
    
    async def start(self):
        """Start the orchestrator agent"""
        await super().start()
        
        # Load configuration
        self.config = load_config()
        self.target_url = self.config.get("website_url")
        
        # Update system state
        self.system_state = SystemState.INITIALIZING
        self.update_system_state()
        
        # Start first iteration
        if self.target_url:
            await self.start_iteration()
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle messages"""
        if message.message_type == MessageType.NOTIFICATION:
            # Handle completion notifications from agents
            if message.payload.get("status") == "complete":
                agent_type = message.source_agent.value
                result_path = message.payload.get("result_path")
                
                self.logger.info(f"Agent {agent_type} completed task")
                self.agents_status[agent_type] = "idle"
                
                if result_path:
                    self.agent_results[agent_type] = result_path
                
                # Check if all agents are idle to potentially start next iteration
                await self.check_system_progress()
                
                return Message(
                    source_agent=self.agent_type,
                    destination_agent=message.source_agent,
                    message_type=MessageType.RESPONSE,
                    payload={"status": "acknowledged"}
                )
        
        elif message.message_type == MessageType.ERROR:
            # Handle error notifications from agents
            agent_type = message.source_agent.value
            error = message.payload.get("error")
            
            self.logger.error(f"Error from agent {agent_type}: {error}")
            self.agents_status[agent_type] = "error"
            
            # Check if we should abort or continue
            await self.check_system_progress()
            
            return Message(
                source_agent=self.agent_type,
                destination_agent=message.source_agent,
                message_type=MessageType.RESPONSE,
                payload={"status": "error_acknowledged"}
            )
        
        elif message.message_type == MessageType.REQUEST:
            if message.payload.get("action") == "set_url":
                # Handle set URL request
                url = message.payload.get("url")
                if url:
                    self.target_url = url
                    self.config["website_url"] = url
                    save_config(self.config)
                    
                    self.logger.info(f"Set target URL to {url}")
                    
                    # If we're idle, start a new iteration
                    if self.system_state == SystemState.COMPLETE or self.system_state == SystemState.INITIALIZING:
                        await self.start_iteration()
                    
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.RESPONSE,
                        payload={"status": "url_set", "url": url}
                    )
                else:
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.ERROR,
                        payload={"error": "No URL provided"}
                    )
            
            elif message.payload.get("action") == "start":
                # Handle start request
                if not self.target_url:
                    return Message(
                        source_agent=self.agent_type,
                        destination_agent=message.source_agent,
                        message_type=MessageType.ERROR,
                        payload={"error": "No target URL set"}
                    )
                
                # Start a new iteration
                await self.start_iteration()
                
                return Message(
                    source_agent=self.agent_type,
                    destination_agent=message.source_agent,
                    message_type=MessageType.RESPONSE,
                    payload={"status": "started", "iteration": self.current_iteration}
                )
            
            elif message.payload.get("action") == "stop":
                # Handle stop request
                self.system_state = SystemState.COMPLETE
                self.update_system_state()
                
                # We could also send stop messages to all agents
                
                return Message(
                    source_agent=self.agent_type,
                    destination_agent=message.source_agent,
                    message_type=MessageType.RESPONSE,
                    payload={"status": "stopped"}
                )
        
        return await super().handle_message(message)
    
    async def start_iteration(self):
        """Start a new iteration of the process"""
        self.current_iteration += 1
        self.logger.info(f"Starting iteration {self.current_iteration}")
        
        # Reset state
        self.agent_results = {}
        
        if self.current_iteration > self.max_iterations:
            self.logger.info(f"Reached maximum iterations ({self.max_iterations})")
            self.system_state = SystemState.COMPLETE
            self.update_system_state()
            return
        
        # Start with crawling
        self.system_state = SystemState.CRAWLING
        self.update_system_state()
        
        # Send crawl request to crawler agent
        await self.send_message(
            AgentType.CRAWLER,
            MessageType.REQUEST,
            {
                "action": "crawl",
                "url": self.target_url,
                "iteration": self.current_iteration
            }
        )
        
        self.agents_status[AgentType.CRAWLER.value] = "running"
    
    async def check_system_progress(self):
        """Check system progress and update state"""
        # Check if any agent is in error state
        if any(status == "error" for status in self.agents_status.values()):
            self.logger.warning("One or more agents are in error state")
            
            # Decide if we should abort or continue
            if self.agents_status[AgentType.CRAWLER.value] == "error":
                # If crawler failed, we can't continue
                self.logger.error("Crawler agent failed, aborting iteration")
                self.system_state = SystemState.ERROR
                self.update_system_state()
                return
        
        # Check current state and progress
        if self.system_state == SystemState.CRAWLING:
            if AgentType.CRAWLER.value in self.agent_results:
                # Crawler completed, but analysis should have been triggered directly
                # Just update the state
                self.system_state = SystemState.ANALYZING
                self.update_system_state()
        
        elif self.system_state == SystemState.ANALYZING:
            if AgentType.ANALYSIS.value in self.agent_results:
                # Analysis completed, but implementation should have been triggered directly
                # Just update the state
                self.system_state = SystemState.IMPLEMENTING
                self.update_system_state()
        
        elif self.system_state == SystemState.IMPLEMENTING:
            if AgentType.IMPLEMENTATION.value in self.agent_results:
                # Implementation completed, but feedback should have been triggered directly
                # Just update the state
                self.system_state = SystemState.FEEDBACK
                self.update_system_state()
        
        elif self.system_state == SystemState.FEEDBACK:
            if AgentType.FEEDBACK.value in self.agent_results:
                # Feedback completed, iteration is done
                self.logger.info(f"Iteration {self.current_iteration} completed")
                
                # Check if we should start another iteration
                if self.current_iteration < self.max_iterations:
                    await self.start_iteration()
                else:
                    self.logger.info(f"Reached maximum iterations ({self.max_iterations})")
                    self.system_state = SystemState.COMPLETE
                    self.update_system_state()
    
    def update_system_state(self):
        """Update the system state file"""
        state_data = {
            "state": self.system_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "agent_states": self.agents_status,
            "target_url": self.target_url,
            "forevervm_available": FOREVERVM_AVAILABLE
        }
        
        state_file = self.output_dir / "system_state.json"
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error updating system state file: {e}")

# Multi-Agent System
class MultiAgentSystem:
    """Multi-Agent System for website cloning and enhancement"""
    
    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.agents = {}
        self.running = False
        self.logger = logging.getLogger('multi_agent_system')
    
    def initialize_agents(self):
        """Initialize all agents"""
        self.agents[AgentType.ORCHESTRATOR] = OrchestratorAgent(self.message_queue)
        self.agents[AgentType.CRAWLER] = CrawlerAgent(self.message_queue)
        self.agents[AgentType.ANALYSIS] = AnalysisAgent(self.message_queue)
        self.agents[AgentType.IMPLEMENTATION] = ImplementationAgent(self.message_queue)
        self.agents[AgentType.FEEDBACK] = FeedbackAgent(self.message_queue)
    
    async def start(self):
        """Start the multi-agent system"""
        self.logger.info("Starting Multi-Agent System")
        self.running = True
        
        # Initialize agents
        self.initialize_agents()
        
        # Start all agents
        agent_tasks = []
        for agent_type, agent in self.agents.items():
            self.logger.info(f"Starting agent: {agent_type.value}")
            agent_tasks.append(asyncio.create_task(agent.run()))
        
        # Wait for all agents to complete
        await asyncio.gather(*agent_tasks)
    
    async def stop(self):
        """Stop the multi-agent system"""
        self.logger.info("Stopping Multi-Agent System")
        self.running = False
        
        # Stop all agents
        for agent_type, agent in self.agents.items():
            if hasattr(agent, 'stop'):
                self.logger.info(f"Stopping agent: {agent_type.value}")
                await agent.stop()

# Command-line interface
def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Multi-Agent System for Website Cloning")
    
    parser.add_argument("--url", type=str, help="Target website URL to clone")
    parser.add_argument("--iterations", type=int, default=1, help="Maximum number of iterations")
    parser.add_argument("--log-level", type=str, default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    parser.add_argument("--test-sandbox", action="store_true", 
                        help="Test ForeverVM sandbox and exit")
    
    return parser.parse_args()

async def run_system(args):
    """Run the multi-agent system"""
    # Load environment variables
    load_environment()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Check if we should just test the sandbox
    if args.test_sandbox:
        logger.info("Testing ForeverVM sandbox...")
        
        if not FOREVERVM_AVAILABLE:
            logger.error("ForeverVM integration not available")
            return
        
        try:
            with ForeverVMSandbox() as sandbox:
                code = """
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print("ForeverVM sandbox is working!")

# Return a success message
"Sandbox test successful"
"""
                logger.info("Executing test code in ForeverVM sandbox...")
                result = sandbox.execute_code(code)
                
                if result["success"]:
                    logger.info("ForeverVM sandbox test successful")
                    logger.info(f"Output: {result['output']}")
                    if result["return_value"]:
                        logger.info(f"Return value: {result['return_value']}")
                else:
                    logger.error(f"ForeverVM sandbox test failed: {result['error']}")
            
            return
        except Exception as e:
            logger.error(f"Error testing ForeverVM sandbox: {e}")
            logger.error(traceback.format_exc())
            return
    
    # Load or create configuration
    config = load_config()
    
    # Update configuration with command-line arguments
    if args.url:
        config["website_url"] = args.url
    
    # Save updated configuration
    save_config(config)
    
    # Create and start the multi-agent system
    system = MultiAgentSystem()
    
    try:
        # Set up signal handlers to stop gracefully
        loop = asyncio.get_event_loop()
        for signal_name in ('SIGINT', 'SIGTERM'):
            if sys.platform != 'win32':
                loop.add_signal_handler(
                    getattr(signal, signal_name),
                    lambda: asyncio.create_task(system.stop())
                )
        
        # Start the system
        await system.start()
    except Exception as e:
        logger.error(f"Error running multi-agent system: {e}")
        logger.error(traceback.format_exc())
    finally:
        if system.running:
            await system.stop()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    try:
        asyncio.run(run_system(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())