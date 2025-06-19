import asyncio
from orchestrator.orchestrator import Orchestrator

async def test_live_vulgarity():
    """Test the exact live scenario through the main orchestrator"""
    orchestrator = Orchestrator()
    
    print("🎯 Testing Live Vulgarity Scenario Through Main Orchestrator")
    print("=" * 70)
    
    # Simulate the exact live scenario
    message = "shit"
    conversation_history = []
    
    print(f"Input Message: '{message}'")
    print(f"Current Agent: {orchestrator.current_agent}")
    print()
    
    # Process through main orchestrator (same as live system)
    response, agent_type, analysis_data = await orchestrator.process_message(message, conversation_history)
    
    print("Results:")
    print(f"  Response: {response}")
    print(f"  Agent Type: {agent_type}")
    print()
    
    # Check orchestrator decision
    orchestrator_decision = analysis_data.get("orchestrator_decision", {})
    print("Orchestrator Decision:")
    print(f"  Current → Next: {orchestrator_decision.get('current_agent', 'unknown')} → {orchestrator_decision.get('next_agent', 'unknown')}")
    print(f"  Action: {orchestrator_decision.get('action', 'unknown')}")
    print(f"  Thinking: {orchestrator_decision.get('thinking', 'No thinking provided')}")
    print()
    
    # Check if it's using new AI system
    thinking = orchestrator_decision.get('thinking', '')
    if thinking.startswith('🧠 AI:'):
        print("✅ SUCCESS: Using new AI orchestrator with vulgarity detection!")
        if 'vulgarity' in thinking.lower():
            print("✅ VULGARITY: AI detected and handled vulgarity correctly!")
        else:
            print("⚠️  WARNING: AI system active but no vulgarity mention")
    else:
        print("❌ ISSUE: Still using old rule-based system")
        print(f"   Thinking format: {thinking[:50]}...")
    
    # Check sentiment analysis
    sentiment = analysis_data.get("sentiment_analysis", {})
    print(f"\nSentiment Analysis:")
    print(f"  Emotion: {sentiment.get('emotion', 'unknown')}")
    print(f"  Intensity: {sentiment.get('intensity', 0)}")
    print(f"  Confidence: {sentiment.get('confidence', 0)}")
    
    # Expected vs Actual
    print(f"\nExpected Behavior:")
    print(f"  Should detect vulgarity in 'shit'")
    print(f"  Should escalate to 'irritated' regardless of emotion")
    print(f"  Should show AI reasoning with vulgarity override")
    
    if agent_type == 'irritated' and 'vulgarity' in thinking.lower():
        print(f"\n🎉 PERFECT: System working as expected!")
    else:
        print(f"\n🚨 NEEDS FIX: System not working as expected")

if __name__ == "__main__":
    asyncio.run(test_live_vulgarity()) 