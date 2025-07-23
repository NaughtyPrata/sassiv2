import asyncio
from agents.orchestrator_agent import OrchestratorAgent

async def test_ai_debug():
    """Debug why AI routing is failing"""
    orchestrator = OrchestratorAgent()
    
    print("🔍 Debugging AI Routing Failure")
    print("=" * 50)
    
    # Test the AI routing method directly
    sentiment_analysis = {
        'emotion': 'anger', 
        'intensity': 0.6, 
        'confidence': 0.8
    }
    current_agent = 'normal'
    user_message = 'damn it'
    
    print("Testing AI routing method directly...")
    try:
        ai_decision = await orchestrator._get_ai_routing_decision(sentiment_analysis, current_agent, user_message)
        
        if ai_decision:
            print("✅ AI routing succeeded:")
            print(f"  Next Agent: {ai_decision['next_agent']}")
            print(f"  Action: {ai_decision['action']}")
            print(f"  Thinking: {ai_decision['thinking']}")
        else:
            print("❌ AI routing returned None (failed)")
            
    except Exception as e:
        print(f"❌ AI routing threw exception: {e}")
        print(f"   Exception type: {type(e)}")
    
    print("\nTesting fallback method...")
    try:
        rule_decision = await orchestrator._make_rule_based_routing_decision(sentiment_analysis, current_agent, user_message)
        print("✅ Rule-based routing succeeded:")
        print(f"  Next Agent: {rule_decision['next_agent']}")
        print(f"  Action: {rule_decision['action']}")
        print(f"  Thinking: {rule_decision['thinking']}")
    except Exception as e:
        print(f"❌ Rule-based routing failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_debug()) 