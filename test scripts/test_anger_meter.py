#!/usr/bin/env python3
"""
Test script for the Anger Meter system
Tests escalation, de-escalation, and configuration-driven behavior
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator
from agents.base_agent import ChatMessage

async def test_anger_escalation():
    """Test anger meter escalation through different levels"""
    print("🔥 Testing Anger Meter System 🔥")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    conversation_history = []
    
    # Test messages with increasing anger
    test_messages = [
        "Hello, how are you?",  # Normal - should decay any existing anger
        "This is annoying me",  # Mild anger - should start building points
        "I'm getting frustrated with this",  # More anger
        "This is really pissing me off!",  # Vulgar language bonus
        "I'm so damn angry right now!",  # More vulgar + consecutive anger
        "FUCK THIS STUPID SYSTEM!!!",  # All caps + multiple vulgar words
        "Sorry, I didn't mean to get so angry",  # Apology - should reduce points
        "Thank you for your patience",  # Calm language - further reduction
        "Actually, I'm still pretty irritated",  # Back to anger
        "This is absolutely infuriating!",  # High intensity anger
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Message {i}: '{message}' ---")
        
        # Add user message to history
        user_message = ChatMessage(role="user", content=message)
        conversation_history.append(user_message)
        
        # Process message
        response, agent_type, analysis_data = await orchestrator.process_message(
            message, conversation_history
        )
        
        # Extract anger meter info
        anger_meter = analysis_data.get("orchestrator_decision", {}).get("anger_meter", {})
        
        print(f"Agent: {agent_type}")
        print(f"Anger Points: {anger_meter.get('anger_points', 0)}")
        print(f"Points Change: {anger_meter.get('points_change', 0)}")
        print(f"Reasons: {', '.join(anger_meter.get('change_reasons', []))}")
        print(f"Consecutive Anger: {anger_meter.get('consecutive_anger', 0)}")
        
        # Show thresholds for context
        thresholds = anger_meter.get('thresholds', {})
        print(f"Thresholds: Irritated={thresholds.get('irritated', 20)}, Agitated={thresholds.get('agitated', 50)}, Enraged={thresholds.get('enraged', 80)}")
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response)
        conversation_history.append(assistant_message)
        
        print(f"Response: {response[:100]}{'...' if len(response) > 100 else ''}")

async def test_meter_config():
    """Test that configuration changes affect behavior"""
    print("\n\n🔧 Testing Configuration Changes 🔧")
    print("=" * 50)
    
    # Test direct anger meter functionality
    from utils.anger_meter import AngerMeter
    
    meter = AngerMeter()
    print(f"Default config loaded: {meter.config['anger_multiplier']} multiplier")
    print(f"Thresholds: {meter.config['thresholds']}")
    
    # Simulate angry message
    test_sentiment = {
        'emotion': 'anger',
        'intensity': 0.8
    }
    
    agent, info = meter.process_message("I'm really angry!", test_sentiment)
    print(f"\nAfter angry message:")
    print(f"Agent: {agent}")
    print(f"Points: {info['anger_points']}")
    print(f"Change: +{info['points_change']}")
    
    # Test vulgar language detection
    agent2, info2 = meter.process_message("This is fucking stupid!", test_sentiment)
    print(f"\nAfter vulgar message:")
    print(f"Agent: {agent2}")
    print(f"Points: {info2['anger_points']}")
    print(f"Change: +{info2['points_change']}")
    print(f"Reasons: {info2['change_reasons']}")
    
    # Test apology
    apology_sentiment = {'emotion': 'neutral', 'intensity': 0.1}
    agent3, info3 = meter.process_message("Sorry about that", apology_sentiment)
    print(f"\nAfter apology:")
    print(f"Agent: {agent3}")
    print(f"Points: {info3['anger_points']}")
    print(f"Change: {info3['points_change']}")
    print(f"Reasons: {info3['change_reasons']}")

async def test_agent_responses():
    """Test that different anger levels produce different agent responses"""
    print("\n\n🤖 Testing Agent Response Differences 🤖")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Force different anger levels and get responses
    test_cases = [
        ("normal", "What's your favorite color?"),
        ("irritated", "This is mildly annoying"),
        ("agitated", "I'm getting really frustrated"),
        ("enraged", "I'M FUCKING FURIOUS!")
    ]
    
    for target_level, message in test_cases:
        print(f"\n--- Testing {target_level.upper()} agent ---")
        
        # Manually set anger meter to target level
        if target_level == "irritated":
            orchestrator.anger_meter.anger_points = 25
        elif target_level == "agitated":
            orchestrator.anger_meter.anger_points = 55
        elif target_level == "enraged":
            orchestrator.anger_meter.anger_points = 85
        else:
            orchestrator.anger_meter.anger_points = 0
        
        conversation_history = [ChatMessage(role="user", content=message)]
        
        response, agent_type, analysis_data = await orchestrator.process_message(
            message, conversation_history
        )
        
        print(f"Target Level: {target_level}")
        print(f"Actual Agent: {agent_type}")
        print(f"Response: {response}")

if __name__ == "__main__":
    async def main():
        await test_anger_escalation()
        await test_meter_config()
        await test_agent_responses()
        
        print("\n\n✅ Anger Meter Testing Complete!")
        print("🔧 To fine-tune behavior, edit anger_config.yaml")
    
    asyncio.run(main()) 