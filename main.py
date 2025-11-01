from enhanced_orchestrator import EnhancedResearchOrchestrator
import os

def main():
    try:
        print("RESEARCH ASSISTANT MULTI-AGENT SYSTEM")
        print("=" * 60)
        
        # Test with MCP enabled
        orchestrator = EnhancedResearchOrchestrator(use_mcp=True)
        
        test_topics = [
            
            "Artificial intelligence in healthcare",

        ]
        
        for i, topic in enumerate(test_topics):
            print(f"\n" + "="*60)
            print(f"RESEARCH {i+1}: {topic}")
            print("="*60)
            
            result = orchestrator.process_topic(topic)
            print(f"\n{result}")
            
    except Exception as e:
        print(f"System initialization failed: {e}")
        print("Please check your OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    main()