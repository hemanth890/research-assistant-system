from crewai import Agent
from mcp_tools import MCPToolServer
from communication import AgentMessage, MessageQueue
from config import config
import logging
from datetime import datetime

class MCPResearchAgent:
    """Research Agent enhanced with MCP tools"""
    
    def __init__(self, message_queue: MessageQueue):
        self.message_queue = message_queue
        self.agent_name = "mcp_research_agent"
        self.logger = logging.getLogger(__name__)
        self.mcp_server = MCPToolServer()
        
        # Initialize MCP tools
        self.mcp_tools_available = False
        self._init_mcp_tools()
        
        self.agent = Agent(
            role="MCP-Enhanced Research Specialist",
            goal="Use MCP tools to gather comprehensive information from external resources",
            backstory="""You are an expert researcher with access to MCP tools for 
            enhanced web search, data analysis, and fact verification.""",
            allow_delegation=False,
            verbose=True,
            model=config.MODEL
        )
    
    def _init_mcp_tools(self):
        """Initialize MCP tools"""
        try:
            self.mcp_tools_available = self.mcp_server.start_server()
            if self.mcp_tools_available:
                self.logger.info("MCP tools initialized successfully")
            else:
                self.logger.warning("MCP tools not available, falling back to basic search")
        except Exception as e:
            self.logger.error(f"MCP tools initialization failed: {e}")
    
    def execute(self, topic: str):
        """Execute research using MCP tools"""
        try:
            self.logger.info(f"MCP Research Agent starting work on: {topic}")
            
            if self.mcp_tools_available:
                # Use MCP tools for enhanced research
                search_results = self.mcp_server.execute_tool(
                    "web_search", 
                    {"query": f"latest developments in {topic}"}
                )
                
                analysis_results = self.mcp_server.execute_tool(
                    "data_analysis",
                    {"data": f"Research data about {topic}"}
                )
                
                research_result = f"""
                MCP-ENHANCED RESEARCH:
                {search_results}
                
                MCP ANALYSIS:
                {analysis_results}
                """
            else:
                # Fallback to basic research
                research_result = f"Basic research results for: {topic}"
            
            # Send message to analysis agent
            message = AgentMessage(
                sender=self.agent_name,
                receiver="analysis_agent",
                content={
                    "topic": topic,
                    "research_data": research_result,
                    "status": "success",
                    "mcp_enhanced": self.mcp_tools_available
                },
                message_type="research_data",
                timestamp=datetime.now().isoformat(),
                metadata={"mcp_tools_used": self.mcp_tools_available}
            )
            self.message_queue.send_message(message)
            self.logger.info("MCP Research completed and sent to analysis agent")
            
        except Exception as e:
            self.logger.error(f"MCP Research agent failed: {str(e)}")
            error_message = AgentMessage(
                sender=self.agent_name,
                receiver="summary_agent",
                content={
                    "topic": topic,
                    "error": f"MCP Research failed: {str(e)}",
                    "status": "error"
                },
                message_type="error",
                timestamp=datetime.now().isoformat()
            )
            self.message_queue.send_message(error_message)