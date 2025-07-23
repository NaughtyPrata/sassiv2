import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def test_openai_orchestrator():
    """Test the fully agentic OpenAI GPT-4o-mini orchestrator"""
    orchestrator = OrchestratorAgent()
    
    print("🤖 Testing Fully Agentic OpenAI GPT-4o-mini Orchestrator")
    print("=" * 70)
    
    test_cases = [
        # (message, emotion, intensity, current_agent, description)
        ("damn it", "anger", 0.6, "normal", "Live scenario - should go to irritated, not agitated"),
        ("oh shit", "surprise", 0.6, "normal", "Surprise emotion - how does AI handle it?"),
        ("I'm so happy!", "joy", 0.7, "normal", "High happiness - should escalate appropriately"),
        ("I feel really sad", "sadness", 0.8, "normal", "High sadness - cross-emotional transition"),
        ("This is amazing!", "joy", 0.9, "irritated", "Cross-transition from anger to joy"),
        ("I'm sorry", "neutral", 0.2, "enraged", "Apology while enraged - counter test"),
        ("Still angry!", "anger", 0.8, "agitated", "Escalation to enraged from agitated"),
    ]
    
    for i, (message, emotion, intensity, current_agent, description) in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {description}")
        print(f"   Message: '{message}'")
        print(f"   Current: {current_agent} | Emotion: {emotion} ({intensity})")
        
        # Set up anger counter for enraged test
        if current_agent == "enraged":
            orchestrator.anger_counter = 2
        
        sentiment = {'emotion': emotion, 'intensity': intensity, 'confidence': 0.8}
        decision = await orchestrator.make_routing_decision(sentiment, current_agent, message)
        
        print(f"   ➡️  Next Agent: {decision['next_agent']}")
        print(f"   📋 Action: {decision['action']}")
        print(f"   💭 {decision['thinking']}")
        
        if decision.get('counter_info'):
            print(f"   🤬 Counter: {decision['counter_info']['display']}")
            print(f"   🙏 Apology: {decision['counter_info']['apology_detected']}")
        
        print()
    
    print("="*70)
    print("🎯 Key Test: Live Scenario Replication")
    print("   Testing: 'damn it' with anger 0.6 from normal")
    print("   Expected: Should go to 'irritated' (proper escalation)")
    print("   Previous: Went to 'agitated' (skipped irritated)")
    
    orchestrator_fresh = OrchestratorAgent()
    sentiment = {'emotion': 'anger', 'intensity': 0.6, 'confidence': 0.8}
    decision = await orchestrator_fresh.make_routing_decision(sentiment, 'normal', 'damn it')
    
    if decision['next_agent'] == 'irritated':
        print("   ✅ SUCCESS: Proper escalation to irritated!")
    elif decision['next_agent'] == 'agitated':
        print("   ❌ ISSUE: Still skipping to agitated")
    else:
        print(f"   🤔 UNEXPECTED: Went to {decision['next_agent']}")
    
    print(f"   Final Decision: normal → {decision['next_agent']}")
    print(f"   AI Reasoning: {decision['thinking']}")

if __name__ == "__main__":
    asyncio.run(test_openai_orchestrator()) 