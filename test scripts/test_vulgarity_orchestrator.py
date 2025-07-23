import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def test_vulgarity_orchestrator():
    """Test the vulgarity detection and escalation in orchestrator"""
    orchestrator = OrchestratorAgent()
    
    print("🤬 Testing Vulgarity Detection & Escalation")
    print("=" * 60)
    print("Sassi HATES vulgar language and should escalate regardless of emotion!")
    print()
    
    test_cases = [
        # (message, emotion, intensity, current_agent, description)
        ("oh shit", "surprise", 0.7, "normal", "Vulgarity in surprise - should escalate to irritated"),
        ("damn it", "anger", 0.6, "normal", "Vulgarity in anger - should escalate to irritated/agitated"),
        ("this is fucking amazing", "joy", 0.9, "normal", "Vulgarity in joy - should override happiness"),
        ("I'm so happy!", "joy", 0.8, "normal", "No vulgarity in joy - should go to cheerful"),
        ("what the hell", "neutral", 0.3, "normal", "Mild vulgarity - should trigger escalation"),
        ("oh crap", "frustration", 0.4, "normal", "Mild vulgarity - should escalate"),
        ("this is great", "joy", 0.6, "normal", "Clean language - normal routing"),
        ("bloody hell", "anger", 0.5, "irritated", "Vulgarity from irritated - should escalate further"),
    ]
    
    for i, (message, emotion, intensity, current_agent, description) in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {description}")
        print(f"   Message: '{message}'")
        print(f"   Current: {current_agent} | Emotion: {emotion} ({intensity})")
        
        # Test vulgarity detection first
        vulgarity = orchestrator._detect_vulgarity(message)
        print(f"   🤬 Vulgarity Detected: {vulgarity}")
        
        sentiment = {'emotion': emotion, 'intensity': intensity, 'confidence': 0.8}
        decision = await orchestrator.make_routing_decision(sentiment, current_agent, message)
        
        print(f"   ➡️  Next Agent: {decision['next_agent']}")
        print(f"   📋 Action: {decision['action']}")
        print(f"   💭 {decision['thinking'][:100]}...")
        
        # Check if vulgarity triggered escalation
        if vulgarity:
            if decision['next_agent'] in ['irritated', 'agitated', 'enraged']:
                print("   ✅ SUCCESS: Vulgarity triggered anger escalation!")
            else:
                print(f"   ❌ ISSUE: Vulgarity detected but went to {decision['next_agent']}")
        else:
            print("   ℹ️  No vulgarity - normal routing applied")
        
        print()
    
    print("="*60)
    print("🎯 Live Scenario Tests")
    
    # Test the exact live scenarios
    live_tests = [
        ("oh shit", "surprise", 0.7, "normal", "Live Test 1"),
        ("damn it", "anger", 0.7, "normal", "Live Test 2"),
    ]
    
    for message, emotion, intensity, current_agent, test_name in live_tests:
        print(f"\n{test_name}: '{message}' with {emotion} ({intensity})")
        
        orchestrator_fresh = OrchestratorAgent()
        sentiment = {'emotion': emotion, 'intensity': intensity, 'confidence': 0.9}
        decision = await orchestrator_fresh.make_routing_decision(sentiment, current_agent, message)
        
        vulgarity = orchestrator_fresh._detect_vulgarity(message)
        
        print(f"   Vulgarity: {vulgarity}")
        print(f"   Decision: {current_agent} → {decision['next_agent']}")
        print(f"   Expected: Should escalate to irritated/agitated due to vulgarity")
        
        if decision['next_agent'] in ['irritated', 'agitated']:
            print("   ✅ SUCCESS: Proper vulgarity escalation!")
        else:
            print(f"   ❌ ISSUE: Went to {decision['next_agent']} instead")

if __name__ == "__main__":
    asyncio.run(test_vulgarity_orchestrator()) 