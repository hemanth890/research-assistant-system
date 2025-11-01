import logging
from research_agent import ResearchAgent
from mcp_research_agent import MCPResearchAgent
from analysis_agent import AnalysisAgent
from summary_agent import SummaryAgent
from communication import MessageQueue
from config import config
import time
import sys

class EnhancedResearchOrchestrator:
    """
    Enhanced orchestrator that demonstrates ALL THREE integration requirements:
    1. Agent Framework: CrewAI
    2. Communication Protocol: Message Queue  
    3. MCP: Model Context Protocol for external tools
    """
    
    def __init__(self, use_mcp: bool = True):
        self.config = config
        self.message_queue = MessageQueue()
        self.use_mcp = use_mcp
        
        # Validate configuration
        if not self.config.GROQ_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents with chosen configuration
        if self.use_mcp:
            self.research_agent = MCPResearchAgent(self.message_queue)
            self.logger.info("Using MCP-Enhanced Research Agent")
        else:
            self.research_agent = ResearchAgent(self.message_queue)
            self.logger.info("Using Standard Research Agent")
            
        self.analysis_agent = AnalysisAgent(self.message_queue)
        self.summary_agent = SummaryAgent(self.message_queue)
        
        self.logger.info("Enhanced Multi-Agent System Initialized")
        self.logger.info(f"Integration Methods: CrewAI + Message Queue + {'MCP' if use_mcp else 'Basic Tools'}")
    
    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('enhanced_agent_system.log')
            ]
        )
    
    def demonstrate_integration_methods(self):
        """Demonstrate all three integration methods in use"""
        integration_info = """
        INTEGRATION METHODS DEMONSTRATED:
        
        1. AGENT FRAMEWORK (CrewAI):
           - Using CrewAI Agent class for all agents
           - Agent roles, goals, and backstories defined
           - Built-in task execution and delegation
        
        2. COMMUNICATION PROTOCOL (Message Queue):
           - Custom MessageQueue class for inter-agent communication
           - Structured AgentMessage format
           - Async message passing with logging
        
        3. MCP (Model Context Protocol):
           - MCPToolServer for external tool integration
           - Standardized tool execution interface
           - External resource access via MCP
        """
        self.logger.info(integration_info)
        return integration_info
    
    def process_topic(self, topic: str) -> str:
        """Orchestrate research pipeline using all integration methods"""
        self.logger.info(f"Starting enhanced pipeline for: '{topic}'")
        
        # Demonstrate integration methods
        self.demonstrate_integration_methods()
        
        try:
            # Start the research agent (uses MCP if enabled)
            self.research_agent.execute(topic)
            
            # Process the message chain (Communication Protocol)
            max_wait_time = 60
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # Agent Framework handles internal processing
                self.analysis_agent.process_messages()
                self.summary_agent.process_messages()
                
                if topic in self.summary_agent.final_results:
                    result = self.summary_agent.final_results.pop(topic)
                    
                    # Add integration method info to result
                    enhanced_result = f"""
{result}

---
INTEGRATION METHODS USED:
• Agent Framework: CrewAI
• Communication: Message Queue Protocol  
• External Tools: {'MCP (Model Context Protocol)' if self.use_mcp else 'Basic Tools'}
"""
                    self.logger.info("Enhanced pipeline completed successfully")
                    return enhanced_result
                
                time.sleep(1)
            
            timeout_msg = f"Pipeline timeout after {max_wait_time} seconds"
            self.logger.error(timeout_msg)
            return f"ERROR: {timeout_msg}"
            
        except Exception as e:
            error_msg = f"Enhanced orchestrator failed: {str(e)}"
            self.logger.error(error_msg)
            return f"ERROR: {error_msg}"