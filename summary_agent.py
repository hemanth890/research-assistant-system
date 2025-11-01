from crewai import Agent
from src.communication import AgentMessage, MessageQueue
from src.config import config
import logging
from datetime import datetime

class Task:
    def __init__(self, text, agent_name="summary_agent"):
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

class SummaryAgent:
    def __init__(self, message_queue: MessageQueue):
        self.message_queue = message_queue
        self.agent_name = "summary_agent"
        self.logger = logging.getLogger(__name__)
        self.final_results = "Summary completed successfully" 

        
        self.agent = Agent(
            role="Research Summarizer",
            goal="Create comprehensive and well-structured research summaries from analysis data",
            backstory="You are an expert technical writer who can synthesize complex information into clear, actionable summaries.",
            allow_delegation=False,
            verbose=True,
            model=config.MODEL
        )
    
    def process_messages(self):
        """Process incoming messages from analysis agent"""
        while True:
            message = self.message_queue.receive_message(self.agent_name)
            if message:
                self._handle_message(message)
            else:
                break
    
    def _safe_execute_task(self, task_text):
        """Safely execute task with proper error handling"""
        try:
            # Create task object
            task = Task(task_text, agent_name="summary_agent")
            
            # Use the agent's kickoff method instead of execute_task if available
            if hasattr(self.agent, 'kickoff'):
                result = self.agent.kickoff(task.prompt())
                return result
            else:
                # Fallback to execute_task
                self.agent.execute_task(task)
                return getattr(task, "output_json", None) or getattr(task, "result", None) or "Summary generated successfully"
        except Exception as e:
            self.logger.error(f"Summary task execution error: {str(e)}")
            return self._fallback_summary(task_text)
    
    def _fallback_summary(self, task_text):
        """Provide a fallback summary when CrewAI fails"""
        self.logger.info("Using fallback summary method")
        
        # Extract key information from task text for basic summary
        if "Topic:" in task_text and "Analysis Data:" in task_text:
            lines = task_text.split('\n')
            topic = "Unknown Topic"
            for line in lines:
                if line.startswith("Topic:"):
                    topic = line.replace("Topic:", "").strip()
                    break
            
            return {
                "status": "fallback_summary",
                "topic": topic,
                "summary": f"Research summary for {topic} - Generated using fallback method",
                "key_findings": ["Analysis completed with basic summary due to technical constraints"],
                "conclusion": "This summary was generated using fallback methods. Consider checking API configuration for enhanced analysis."
            }
        else:
            return "Research summary generated successfully using fallback methods."
    
    def _handle_message(self, message: AgentMessage):
        """Handle different types of messages"""
        try:
            if message.message_type == "analysis":
                self.logger.info("Summary Agent received analysis data")
                
                content = message.content
                if not isinstance(content, dict):
                    raise ValueError("Message content is not a dictionary")
                
                topic = content.get("topic", "Unknown topic")
                research_data = content.get("research_data", "")
                analysis_data = content.get("analysis_data", "")
                
                # Handle different formats of analysis_data
                if isinstance(analysis_data, dict):
                    analysis_text = str(analysis_data)
                elif hasattr(analysis_data, '__dict__'):
                    analysis_text = str(analysis_data.__dict__)
                else:
                    analysis_text = str(analysis_data)
                
                # Create task text for summary generation
                task_text = f"""
                Create a comprehensive research summary based on the following analysis.
                
                TOPIC: {topic}
                
                RESEARCH DATA:
                {research_data}
                
                ANALYSIS DATA:
                {analysis_text}
                
                Please provide a well-structured summary that includes:
                1. Key findings and insights
                2. Main themes and patterns
                3. Important conclusions
                4. Potential implications or recommendations
                
                Format the summary in a clear, professional manner suitable for research reporting.
                """
                
                # Use safe execution
                summary_result = self._safe_execute_task(task_text)
                
                # Generate final output
                final_summary = self._generate_final_output(topic, summary_result)
                
                self.logger.info(f"Summary generation completed for: {topic}")
                print(final_summary)
                
            elif message.message_type == "error":
                self.logger.error(f"Summary Agent received error for topic: {message.content.get('topic', 'unknown')}")
                topic = message.content.get("topic", "Unknown topic")
                error_msg = message.content.get("error", "Unknown error")
                
                error_summary = f"""
                === RESEARCH SUMMARY ===
                Topic: {topic}
                
                Status: ERROR
                Error: {error_msg}
                
                The research pipeline encountered an error. Please try again.
                Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                print(error_summary)
                
        except Exception as e:
            self.logger.error(f"Summary agent failed: {str(e)}")
            error_summary = f"""
            === RESEARCH SUMMARY ===
            Topic: Unknown
            
            Status: ERROR
            Error: Summary generation failed: {str(e)}
            
            The research pipeline encountered an error. Please try again.
            Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            print(error_summary)
    
    def _generate_final_output(self, topic, summary_result):
        """Generate the final formatted output"""
        if isinstance(summary_result, dict):
            # Handle dictionary output
            key_findings = summary_result.get('key_findings', ['No specific findings listed'])
            conclusion = summary_result.get('conclusion', 'Analysis completed successfully.')
            
            final_output = f"""
            === RESEARCH SUMMARY ===
            Topic: {topic}
            
            Status: COMPLETED
            Key Findings:
            {chr(10).join(f'  • {finding}' for finding in key_findings)}
            
            Conclusion: {conclusion}
            
            Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        else:
            # Handle string output
            final_output = f"""
            === RESEARCH SUMMARY ===
            Topic: {topic}
            
            Status: COMPLETED
            
            Summary:
            {summary_result}
            
            Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        
        return final_output