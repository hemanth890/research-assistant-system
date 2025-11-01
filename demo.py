import sys
sys.stdout.reconfigure(encoding='utf-8')

from enhanced_orchestrator import EnhancedResearchOrchestrator



def demo():
    print("RESEARCH ASSISTANT MULTI-AGENT SYSTEM DEMO")
    print("=" * 60)
    
    orchestrator = EnhancedResearchOrchestrator(use_mcp=True)
    
    # Sample query as specified in requirements
    topic = "Artificial intelligence in healthcare"
    print(f"Topic: {topic}")
    print("=" * 60)
    
    result = orchestrator.process_topic(topic)
    print(result)

if __name__ == "__main__":
    demo()