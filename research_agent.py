from crewai import Agent
from duckduckgo_search import DDGS
from langchain.tools import Tool
from communication import AgentMessage, MessageQueue
from config import config
import logging
from datetime import datetime
import time

class ResearchAgent:
    def __init__(self, message_queue: MessageQueue):
        self.message_queue = message_queue
        self.agent_name = "research_agent"
        self.logger = logging.getLogger(__name__)
        
        self.search_tool = Tool(
            name="WebSearch",
            func=self._search_web_with_retry,
            description="Search the web for current information"
        )
        
        self.agent = Agent(
            role="Research Specialist",
            goal="Find comprehensive and accurate information about any topic",
            backstory="You are an expert researcher who can find information about anything.",
            tools=[self.search_tool],
            allow_delegation=False,
            verbose=True,
            model=config.MODEL
        )
    
    def _search_web_with_retry(self, query: str) -> str:
        """Search with retry logic and error handling"""
        for attempt in range(config.MAX_RETRIES):
            try:
                self.logger.info(f"Search attempt {attempt + 1} for: {query}")
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                
                if results:
                    self.logger.info(f"Search successful, found {len(results)} results")
                    formatted_results = "\n\n".join([
                        f"Source {i+1}:\nTitle: {r['title']}\nURL: {r['href']}\nContent: {r['body'][:200]}..."
                        for i, r in enumerate(results)
                    ])
                    return formatted_results
                else:
                    self.logger.warning(f"No results found on attempt {attempt + 1}")
                    
            except Exception as e:
                self.logger.error(f"Search failed on attempt {attempt + 1}: {str(e)}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(2)  # Wait before retry
                    continue
            
        error_msg = f"All {config.MAX_RETRIES} search attempts failed for: {query}"
        self.logger.error(error_msg)
        return error_msg
    
    def execute(self, topic: str):
        """Execute research and send results to analysis agent"""
        try:
            self.logger.info(f"Research Agent starting work on: {topic}")
            
            prompt = f"Research this topic and gather comprehensive information: {topic}"
            research_result = self.agent.execute_task(prompt)
            
            # Send message to analysis agent
            message = AgentMessage(
                sender=self.agent_name,
                receiver="analysis_agent",
                content={
                    "topic": topic,
                    "research_data": research_result,
                    "status": "success"
                },
                message_type="research_data",
                timestamp=datetime.now().isoformat()
            )
            self.message_queue.send_message(message)
            self.logger.info("Research completed and sent to analysis agent")
            
        except Exception as e:
            self.logger.error(f"Research agent failed: {str(e)}")
            error_message = AgentMessage(
                sender=self.agent_name,
                receiver="summary_agent",
                content={
                    "topic": topic,
                    "error": f"Research failed: {str(e)}",
                    "status": "error"
                },
                message_type="error",
                timestamp=datetime.now().isoformat()
            )
            self.message_queue.send_message(error_message)