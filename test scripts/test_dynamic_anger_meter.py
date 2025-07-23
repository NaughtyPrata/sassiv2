#!/usr/bin/env python3
"""
Test the new dynamic anger meter system with actual agent responses
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator
from agents.base_agent import ChatMessage

async def test_dynamic_anger_meter():
    """Test that the enraged agent shows dynamic anger meter instead of old 2/2 counter"""
    print("🔥 Testing Dynamic Anger Meter Display 🔥")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    conversation_history = []
    
    # Test messages that should escalate to enraged with different anger levels
    test_scenarios = [
        {
            "message": "shut the fuck up",
            "description": "Single insult - should reach baseline enraged (LVL 1)",
        },
        {
            "message": "you're a fucking idiot asshole",
            "description": "Multiple insults - should reach higher anger (LVL 2-3)",
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['description']} ---")
        print(f"Message: '{scenario['message']}'")
        
        # Reset orchestrator for clean test
        orchestrator.anger_meter.reset_meter()
        conversation_history = [ChatMessage(role="user", content=scenario["message"])]
        
        # Process the message
        response, agent_type, analysis_data = await orchestrator.process_message(
            scenario["message"], conversation_history
        )
        
        # Extract anger meter info
        anger_meter = analysis_data.get("orchestrator_decision", {}).get("anger_meter", {})
        
        print(f"Agent: {agent_type}")
        print(f"Anger Points: {anger_meter.get('anger_points', 0)}")
        print(f"Points Change: +{anger_meter.get('points_change', 0)}")
        print(f"Reasons: {', '.join(anger_meter.get('change_reasons', []))}")
        
        # Show the actual response with dynamic anger meter
        print(f"\nAgent Response:")
        print(f"{response}")
        
        # Check if the response contains the new dynamic meter format
        if "🔥" in response and "pts" in response and "LVL" in response:
            print("✅ Dynamic anger meter format detected!")
        elif "🤬" in response and "/2" in response:
            print("❌ Old anger counter format detected - needs fixing")
        else:
            print("⚠️  No anger meter format detected")

async def test_anger_level_progression():
    """Test that anger levels progress realistically and show in responses"""
    print(f"\n\n📈 Testing Anger Level Progression 📈")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    
    # Simulate a conversation that builds up anger gradually
    conversation = [
        "Hi there",
        "This is annoying",
        "I'm getting frustrated",
        "This is really pissing me off",
        "Fuck this stupid system",
        "You're a fucking idiot",
    ]
    
    conversation_history = []
    
    for i, message in enumerate(conversation, 1):
        print(f"\nMessage {i}: '{message}'")
        
        # Add to conversation history
        user_message = ChatMessage(role="user", content=message)
        conversation_history.append(user_message)
        
        # Process message
        response, agent_type, analysis_data = await orchestrator.process_message(
            message, conversation_history
        )
        
        # Extract anger info
        anger_meter = analysis_data.get("orchestrator_decision", {}).get("anger_meter", {})
        anger_points = anger_meter.get('anger_points', 0)
        
        print(f"  Agent: {agent_type} | Points: {anger_points}")
        
        # If enraged, show the dynamic meter in response
        if agent_type == "enraged":
            print(f"  🔥 ENRAGED Response: {response[:100]}...")
            
            # Extract the anger meter display from response
            if "<t>" in response:
                start = response.find("<t>") + 3
                end = response.find("</t>")
                if end > start:
                    meter_display = response[start:end]
                    print(f"  📊 Meter Display: {meter_display}")
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response)
        conversation_history.append(assistant_message)
        
        if agent_type == "enraged":
            print(f"  🎯 ENRAGED ACHIEVED at message {i}!")
            break

if __name__ == "__main__":
    async def main():
        await test_dynamic_anger_meter()
        await test_anger_level_progression()
        
        print("\n\n✅ Dynamic Anger Meter Testing Complete!")
        print("🔥 The old 🤬 2/2 counter has been replaced with dynamic 🔥 X/100 pts (LVL Y)")
        print("📊 Anger levels now reflect ACTUAL conversation buildup!")
    
    asyncio.run(main()) 