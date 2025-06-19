import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def test_escalation_thresholds():
    """Test the fixed escalation thresholds"""
    orchestrator = OrchestratorAgent()
    
    print("🔧 Testing Fixed Escalation Thresholds")
    print("=" * 50)
    
    test_cases = [
        # (intensity, expected_agent, description)
        (0.3, "normal", "Low anger - should stay normal"),
        (0.4, "irritated", "Mild anger - should go to irritated"),
        (0.5, "irritated", "Medium-low anger - should stay irritated"),
        (0.6, "agitated", "Medium anger - should go to agitated"),
        (0.7, "agitated", "Medium-high anger - should stay agitated"),
        (0.8, "agitated", "High anger from normal - should go to agitated (not enraged)"),
    ]
    
    for intensity, expected_agent, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Intensity: {intensity}")
        
        sentiment = {'emotion': 'anger', 'intensity': intensity, 'confidence': 0.8}
        decision = await orchestrator.make_routing_decision(sentiment, 'normal', f'I am angry at level {intensity}!')
        
        actual_agent = decision["next_agent"]
        status = "✅" if actual_agent == expected_agent else "❌"
        
        print(f"{status} Expected: {expected_agent} | Actual: {actual_agent}")
        print(f"   Action: {decision['action']}")
        print(f"   Thinking: {decision['thinking']}")
        
        if actual_agent != expected_agent:
            print(f"   🚨 MISMATCH! Expected {expected_agent} but got {actual_agent}")
    
    print("\n" + "="*50)
    print("🎯 Testing Proper Escalation Path")
    
    # Test proper escalation: normal → irritated → agitated → enraged
    orchestrator2 = OrchestratorAgent()
    
    # Step 1: normal → irritated (0.4 intensity)
    sentiment = {'emotion': 'anger', 'intensity': 0.4, 'confidence': 0.8}
    decision = await orchestrator2.make_routing_decision(sentiment, 'normal', 'Getting annoyed')
    print(f"Step 1: normal → {decision['next_agent']} (intensity 0.4)")
    
    # Step 2: irritated → agitated (0.6 intensity)  
    sentiment = {'emotion': 'anger', 'intensity': 0.6, 'confidence': 0.8}
    decision = await orchestrator2.make_routing_decision(sentiment, 'irritated', 'Getting more angry')
    print(f"Step 2: irritated → {decision['next_agent']} (intensity 0.6)")
    
    # Step 3: agitated → enraged (0.8 intensity)
    sentiment = {'emotion': 'anger', 'intensity': 0.8, 'confidence': 0.8}
    decision = await orchestrator2.make_routing_decision(sentiment, 'agitated', 'Absolutely furious!')
    print(f"Step 3: agitated → {decision['next_agent']} (intensity 0.8)")
    if decision.get('counter_info'):
        print(f"        Counter: {decision['counter_info']['display']}")

if __name__ == "__main__":
    asyncio.run(test_escalation_thresholds()) 