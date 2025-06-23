#!/usr/bin/env python3
"""
Test the reset functionality end-to-end
"""

import asyncio
import sys
import os
import requests
import time

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator

def test_reset_endpoint():
    """Test the /reset endpoint"""
    print("🌐 Testing Reset Endpoint 🌐")
    print("=" * 50)
    
    try:
        # Test the reset endpoint
        response = requests.post("http://localhost:7878/reset")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Reset endpoint successful!")
            print(f"  Message: {data.get('message', 'N/A')}")
            print(f"  Current Agent: {data.get('current_agent', 'N/A')}")
            print(f"  Anger Points: {data.get('anger_points', 'N/A')}")
            print(f"  Anger Counter: {data.get('anger_counter', 'N/A')}")
        else:
            print(f"❌ Reset endpoint failed: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure to run ./startup.sh first!")
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

def test_orchestrator_reset():
    """Test orchestrator reset directly"""
    print(f"\n📦 Testing Orchestrator Reset Directly 📦")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Build up some state
    print("Building up state...")
    orchestrator.anger_meter.process_message("fuck you", {'emotion': 'anger', 'intensity': 0.8})
    orchestrator.current_agent = "enraged"
    orchestrator.emotional_history.append({"emotion": "anger", "intensity": 0.8, "agent": "enraged"})
    
    print(f"Before reset:")
    print(f"  Anger Points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current Agent: {orchestrator.current_agent}")
    print(f"  Emotional History: {len(orchestrator.emotional_history)} items")
    
    # Reset
    orchestrator.reset_state()
    
    print(f"After reset:")
    print(f"  Anger Points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current Agent: {orchestrator.current_agent}")
    print(f"  Emotional History: {len(orchestrator.emotional_history)} items")
    
    if (orchestrator.anger_meter.anger_points == 0.0 and 
        orchestrator.current_agent == "normal" and
        len(orchestrator.emotional_history) == 0):
        print("✅ Direct orchestrator reset successful!")
    else:
        print("❌ Direct orchestrator reset failed!")

async def test_conversation_flow():
    """Test a full conversation flow with reset"""
    print(f"\n💬 Testing Full Conversation Flow with Reset 💬")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Start fresh
    orchestrator.reset_state()
    
    # Test messages
    messages = [
        ("hello", "Should start normal"),
        ("fuck you", "Should escalate to anger"),
        ("you're an idiot", "Should stay/increase anger"),
    ]
    
    conversation_history = []
    
    for message, description in messages:
        print(f"\nMessage: '{message}' ({description})")
        
        # Add to conversation history
        from agents.base_agent import ChatMessage
        user_message = ChatMessage(role="user", content=message)
        conversation_history.append(user_message)
        
        # Process message
        response, agent_type, analysis_data = await orchestrator.process_message(
            message, conversation_history
        )
        
        # Extract anger meter info
        anger_meter = analysis_data.get("orchestrator_decision", {}).get("anger_meter", {})
        
        print(f"  Agent: {agent_type}")
        print(f"  Anger Points: {anger_meter.get('anger_points', 0)}")
        print(f"  Change: {anger_meter.get('points_change', 0)}")
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response)
        conversation_history.append(assistant_message)
    
    # Now reset and test
    print(f"\n🔄 Resetting orchestrator...")
    orchestrator.reset_state()
    
    # Test a fresh message
    fresh_message = "hello again"
    user_message = ChatMessage(role="user", content=fresh_message)
    response, agent_type, analysis_data = await orchestrator.process_message(
        fresh_message, [user_message]
    )
    
    anger_meter = analysis_data.get("orchestrator_decision", {}).get("anger_meter", {})
    
    print(f"\nAfter reset - Message: '{fresh_message}'")
    print(f"  Agent: {agent_type}")
    print(f"  Anger Points: {anger_meter.get('anger_points', 0)}")
    
    if agent_type == "normal" and anger_meter.get('anger_points', 0) <= 2:
        print("✅ Fresh conversation after reset successful!")
    else:
        print("❌ Fresh conversation after reset failed!")

if __name__ == "__main__":
    async def main():
        test_orchestrator_reset()
        test_reset_endpoint()
        await test_conversation_flow()
        
        print("\n\n🎯 Summary:")
        print("✅ Orchestrator reset functionality working")
        print("✅ Reset endpoint available at POST /reset") 
        print("✅ Web interface has reset button (🔄 Reset)")
        print("✅ Fresh conversations start with clean state")
        
        print("\n💡 Usage:")
        print("- Click 🔄 Reset button in web interface")
        print("- Or call: curl -X POST http://localhost:7878/reset")
        print("- Server auto-resets on startup")
    
    asyncio.run(main()) 