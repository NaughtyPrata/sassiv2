import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def test_ai_orchestrator():
    """Test the upgraded orchestrator with DeepSeek R1 model"""
    orchestrator = OrchestratorAgent()
    
    print("🧠 Testing AI-Enhanced Orchestrator with DeepSeek R1")
    print("=" * 60)
    
    # Test case 1: Mild frustration
    print("Test 1: Mild frustration")
    sentiment = {'emotion': 'frustration', 'intensity': 0.6, 'confidence': 0.8}
    decision = await orchestrator.make_routing_decision(sentiment, 'normal', 'This is really annoying!')
    print(f'  Next agent: {decision["next_agent"]}')
    print(f'  Action: {decision["action"]}')
    print(f'  Thinking: {decision["thinking"]}')
    print()
    
    # Test case 2: High anger from agitated state
    print("Test 2: High anger from agitated state")
    sentiment = {'emotion': 'anger', 'intensity': 0.9, 'confidence': 0.9}
    decision = await orchestrator.make_routing_decision(sentiment, 'agitated', 'I am absolutely furious!')
    print(f'  Next agent: {decision["next_agent"]}')
    print(f'  Action: {decision["action"]}')
    print(f'  Thinking: {decision["thinking"]}')
    if decision.get('counter_info'):
        print(f'  Counter: {decision["counter_info"]["display"]}')
    print()
    
    # Test case 3: Happy emotion
    print("Test 3: Happy emotion")
    sentiment = {'emotion': 'joy', 'intensity': 0.7, 'confidence': 0.8}
    decision = await orchestrator.make_routing_decision(sentiment, 'normal', 'This is wonderful!')
    print(f'  Next agent: {decision["next_agent"]}')
    print(f'  Action: {decision["action"]}')
    print(f'  Thinking: {decision["thinking"]}')
    print()
    
    # Test case 4: Apology while enraged
    print("Test 4: Apology while enraged (counter test)")
    # First get to enraged state
    orchestrator.anger_counter = 2
    sentiment = {'emotion': 'neutral', 'intensity': 0.2, 'confidence': 0.7}
    decision = await orchestrator.make_routing_decision(sentiment, 'enraged', 'I am sorry for my behavior')
    print(f'  Next agent: {decision["next_agent"]}')
    print(f'  Action: {decision["action"]}')
    print(f'  Thinking: {decision["thinking"]}')
    if decision.get('counter_info'):
        print(f'  Counter: {decision["counter_info"]["display"]}')
        print(f'  Apology detected: {decision["counter_info"]["apology_detected"]}')
    print()
    
    # Test case 5: Complex emotional transition
    print("Test 5: Complex emotional transition")
    sentiment = {'emotion': 'sadness', 'intensity': 0.8, 'confidence': 0.9}
    decision = await orchestrator.make_routing_decision(sentiment, 'irritated', 'I feel so sad and disappointed')
    print(f'  Next agent: {decision["next_agent"]}')
    print(f'  Action: {decision["action"]}')
    print(f'  Thinking: {decision["thinking"]}')
    print()

if __name__ == "__main__":
    asyncio.run(test_ai_orchestrator()) 