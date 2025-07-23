import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def test_live_scenario():
    """Test the exact live scenario: 'damn it' with anger 0.6"""
    orchestrator = OrchestratorAgent()
    
    print("🎯 Testing Live Scenario: 'damn it' with anger 0.6")
    print("=" * 60)
    
    # Exact scenario from live conversation
    sentiment_analysis = {
        'emotion': 'anger', 
        'intensity': 0.6, 
        'confidence': 0.8
    }
    current_agent = 'normal'
    user_message = 'damn it'
    
    print(f"Input:")
    print(f"  Message: '{user_message}'")
    print(f"  Current Agent: {current_agent}")
    print(f"  Emotion: {sentiment_analysis['emotion']}")
    print(f"  Intensity: {sentiment_analysis['intensity']}")
    print(f"  Confidence: {sentiment_analysis['confidence']}")
    print()
    
    # Test the routing decision
    decision = await orchestrator.make_routing_decision(sentiment_analysis, current_agent, user_message)
    
    print(f"Result:")
    print(f"  Next Agent: {decision['next_agent']}")
    print(f"  Action: {decision['action']}")
    print(f"  Thinking: {decision['thinking']}")
    print()
    
    # Determine which system was used
    if decision['thinking'].startswith('AI:'):
        print("🧠 AI Routing (DeepSeek R1) was used")
        print("   → AI made intelligent decision based on context")
    else:
        print("⚙️  Rule-based Routing was used")
        print("   → Fallback system with strict thresholds")
    
    print()
    print("Expected behavior:")
    print("  With fixed thresholds (0.6 → agitated):")
    print("  normal → agitated (skipping irritated)")
    print()
    print("  With AI routing:")
    print("  normal → irritated (gradual escalation)")

if __name__ == "__main__":
    asyncio.run(test_live_scenario()) 