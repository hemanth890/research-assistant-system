from crewai import Agent
from communication import AgentMessage, MessageQueue
from config import config
import logging
from datetime import datetime

class Task:
    def __init__(self, text, agent_name="analysis_agent"):
        self.text = text
        self.output_json = None
        self.output_pydantic = None 
        self.human_input = None  
        self.description = None 
        self.metadata = {} 
        self.agent = agent_name 
        self.id = "task_" + str(id(self))

    def prompt(self):
        return self.text

class AnalysisAgent:
    def __init__(self, message_queue: MessageQueue):
        self.message_queue = message_queue
        self.agent_name = "analysis_agent"
        self.logger = logging.getLogger(__name__)
        
        self.agent = Agent(
            role="Data Analyst",
            goal="Analyze information and extract key insights from any content",
            backstory="You are an expert analyst who can find patterns and insights in any information.",
            allow_delegation=False,
            verbose=True,
            model=config.MODEL
        )
    
    def process_messages(self):
        """Process incoming messages from research agent"""
        while True:
            message = self.message_queue.receive_message(self.agent_name)
            if message:
                self._handle_message(message)
            else:
                break
    
    def _safe_execute_task(self, task):
        """Safely execute task with proper error handling"""
        try:
            # Use the agent's kickoff method instead of execute_task if available
            if hasattr(self.agent, 'kickoff'):
                result = self.agent.kickoff(task.prompt())
                return result
            else:
                # Fallback to execute_task but handle potential issues
                self.agent.execute_task(task)
                return getattr(task, "output_json", None) or getattr(task, "result", None)
        except Exception as e:
            self.logger.error(f"Task execution error: {str(e)}")
            return f"Analysis could not be completed due to: {str(e)}"
    
    def _handle_message(self, message: AgentMessage):
        """Handle different types of messages"""
        try:
            if message.message_type == "research_data":
                self.logger.info("Analysis Agent received research data")
                
                # Safely extract content with validation
                content = message.content
                if not isinstance(content, dict):
                    raise ValueError("Message content is not a dictionary")
                
                research_data = content.get("research_data", "")
                topic = content.get("topic", "Unknown topic")
                
                # Ensure research_data is a string for processing
                if not isinstance(research_data, str):
                    if hasattr(research_data, '__str__'):
                        research_text = str(research_data)
                    else:
                        research_text = f"Research data in format: {type(research_data)}"
                else:
                    research_text = research_data
                
                # Create a simpler task structure to avoid CrewAI issues
                task_text = f"""
                Analyze this research data about {topic} and extract key points, themes, and insights.
                Provide a comprehensive analysis with the most important information.
                
                RESEARCH DATA:
                {research_text}
                
                Please provide your analysis in a structured format with clear sections.
                """
                
                task = Task(task_text, agent_name="analysis_agent")
                
                # Use safe execution
                analysis_result = self._safe_execute_task(task)
                
                # If analysis failed, provide a basic analysis
                if analysis_result is None or "could not be completed" in str(analysis_result):
                    analysis_result = self._fallback_analysis(topic, research_text)
                
                # Send to summary agent
                response_message = AgentMessage(
                    sender=self.agent_name,
                    receiver="summary_agent",
                    content={
                        "topic": topic,
                        "research_data": research_text[:500] + "..." if len(research_text) > 500 else research_text,  # Truncate if too long
                        "analysis_data": analysis_result,
                        "status": "success"
                    },
                    message_type="analysis",
                    timestamp=datetime.now().isoformat()
                )
                self.message_queue.send_message(response_message)
                self.logger.info("Analysis completed and sent to summary agent")
                
            elif message.message_type == "error":
                self.logger.warning("Analysis Agent received error message")
                # Forward error to summary agent with proper structure
                error_message = AgentMessage(
                    sender=self.agent_name,
                    receiver="summary_agent",
                    content={
                        "topic": message.content.get("topic", "unknown"),
                        "error": f"Analysis failed: {message.content.get('error', 'Unknown error')}",
                        "status": "error"
                    },
                    message_type="error",
                    timestamp=datetime.now().isoformat()
                )
                self.message_queue.send_message(error_message)
                
        except Exception as e:
            self.logger.error(f"Analysis agent failed: {str(e)}")
            error_message = AgentMessage(
                sender=self.agent_name,
                receiver="summary_agent",
                content={
                    "topic": message.content.get("topic", "unknown") if 'message' in locals() else "unknown",
                    "error": f"Analysis failed: {str(e)}",
                    "status": "error"
                },
                message_type="error",
                timestamp=datetime.now().isoformat()
            )
            self.message_queue.send_message(error_message)
    
    def _fallback_analysis(self, topic, research_text):
        """Provide a fallback analysis when CrewAI fails"""
        self.logger.info("Using fallback analysis method")
        
        # Simple keyword-based analysis as fallback
        keywords = ["AI", "artificial intelligence", "healthcare", "medical", "diagnosis", "treatment"]
        found_keywords = [kw for kw in keywords if kw.lower() in research_text.lower()]
        
        return {
            "status": "fallback_analysis",
            "topic": topic,
            "key_themes": found_keywords,
            "summary": f"Based on research about {topic}, key areas discussed include: {', '.join(found_keywords) if found_keywords else 'general topics'}",
            "insights": "Analysis completed using fallback method due to technical constraints.",
            "data_length": len(research_text)
        }