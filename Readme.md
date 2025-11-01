# Research Assistant Multi-Agent System

A sophisticated multi-agent research system built with CrewAI that autonomously researches, analyzes, and summarizes topics using advanced AI agents and external tools.

## Features

- **Multi-Agent Architecture**: Three specialized AI agents working in coordination
- **MCP Integration**: Model Context Protocol for external tool access
- **Message Queue Communication**: Robust inter-agent communication system
- **Automated Research Pipeline**: End-to-end research and analysis workflow
- **Real-time Processing**: Live agent interaction and task execution

## System Architecture

### Agents
1. **MCP Research Agent** - Gathers research data using external tools
2. **Analysis Agent** - Analyzes and extracts insights from research data  
3. **Summary Agent** - Creates comprehensive research summaries

### Integration Methods
- **CrewAI Framework**: Agent management and task execution
- **Message Queue Protocol**: Inter-agent communication
- **MCP (Model Context Protocol)**: External tool integration

##  Quick Start

### Prerequisites
- Python 3.8+
- Groq API account (free at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/research-assistant-system.git
cd research-assistant-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env
```

4. **Configure API keys**
Edit `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL=groq/llama-3.3-70b-versatile
MAX_RETRIES=3
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

### Usage

Run the demo:
```bash
python demo.py
```

The system will automatically:
1. Research "Artificial Intelligence in Healthcare"
2. Analyze the gathered data
3. Generate a comprehensive summary
4. Display the final research report

## 🔧 Configuration

### Agent Configuration
Each agent is configured with specific roles, goals, and backstories:

- **Research Agent**: Specializes in data gathering using MCP tools
- **Analysis Agent**: Expert in pattern recognition and insight extraction  
- **Summary Agent**: Technical writer for creating structured summaries

### MCP Tools
The system integrates with external tools via MCP:
- Web Search
- Data Analysis
- Content Summarization
- Fact Verification



## 🛠️ Technical Details

### Communication Protocol
- Custom MessageQueue class for agent communication
- Structured AgentMessage format with type safety
- Async message passing with comprehensive logging

### Error Handling
- Robust error recovery mechanisms
- Fallback analysis methods
- Comprehensive logging at all levels

### Performance Features
- Concurrent agent processing
- Configurable timeouts and retries
- Efficient memory management


## Example Output

The system generates structured research summaries and you can find the sample output execution doc -> results_analysis.docx

```
=== RESEARCH SUMMARY ===
Topic: Artificial Intelligence in Healthcare

Status: COMPLETED

Key Findings:
• AI-powered diagnostic systems improving accuracy
• Personalized treatment plans through data analysis
• Predictive analytics for patient outcomes
• Virtual nursing assistants for remote care

Conclusion: AI is transforming healthcare through improved diagnostics...
Generated at: 2025-11-01 16:21:53
```


