#!/usr/bin/env python3
"""
Test script specifically for insult detection and anger meter response
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.anger_meter import AngerMeter

def test_insult_detection():
    """Test that insults are properly detected and trigger anger escalation"""
    print("🎯 Testing Insult Detection & Anger Escalation 🎯")
    print("=" * 60)
    
    meter = AngerMeter()
    
    # Test cases that should trigger anger escalation
    test_cases = [
        {
            "message": "suck my balls",
            "sentiment": {"emotion": "neutral", "intensity": 0.5},
            "expected_agent": "agitated",  # Should force anger detection
            "should_detect": ["direct_insults", "vulgar_language"]
        },
        {
            "message": "fuck you",
            "sentiment": {"emotion": "neutral", "intensity": 0.3},
            "expected_agent": "agitated",
            "should_detect": ["direct_insults", "vulgar_language"]
        },
        {
            "message": "you're a fucking idiot",
            "sentiment": {"emotion": "anger", "intensity": 0.6},
            "expected_agent": "enraged",  # Should get massive bonuses
            "should_detect": ["vulgar_language", "direct_insults"]
        },
        {
            "message": "shut the fuck up",
            "sentiment": {"emotion": "frustration", "intensity": 0.7},
            "expected_agent": "enraged",
            "should_detect": ["direct_insults", "vulgar_language"]
        },
        {
            "message": "this is annoying",
            "sentiment": {"emotion": "frustration", "intensity": 0.4},
            "expected_agent": "normal",  # No insults, should be mild
            "should_detect": []
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: '{test['message']}' ---")
        
        # Reset meter for each test
        meter.reset_meter()
        
        # Process the message
        agent, info = meter.process_message(test["message"], test["sentiment"])
        
        print(f"Sentiment: {test['sentiment']['emotion']} ({test['sentiment']['intensity']})")
        print(f"Agent: {agent} (expected: {test['expected_agent']})")
        print(f"Points: {info['anger_points']}")
        print(f"Change: +{info['points_change']}")
        print(f"Reasons: {info['change_reasons']}")
        
        # Check if expected detections occurred
        reasons_str = ", ".join(info['change_reasons'])
        detected = []
        for detection in test['should_detect']:
            if detection in reasons_str:
                detected.append(f"✅ {detection}")
            else:
                detected.append(f"❌ {detection}")
        
        if detected:
            print(f"Detections: {', '.join(detected)}")
        
        # Check if agent matches expectation
        if agent == test['expected_agent']:
            print(f"✅ Agent routing correct")
        else:
            print(f"❌ Agent routing wrong (got {agent}, expected {test['expected_agent']})")
    
    print(f"\n🔧 Current Configuration:")
    print(f"Anger Multiplier: {meter.config['anger_multiplier']}")
    print(f"Thresholds: {meter.config['thresholds']}")
    print(f"Vulgar Bonus: {meter.config['bonuses']['vulgar_language']}")
    print(f"Insult Bonus: {meter.config['bonuses']['direct_insults']}")

def test_escalation_scenario():
    """Test a realistic escalation scenario"""
    print(f"\n\n🔥 Testing Realistic Escalation Scenario 🔥")
    print("=" * 60)
    
    meter = AngerMeter()
    
    # Realistic conversation that should escalate to enraged
    conversation = [
        ("Hi there", {"emotion": "neutral", "intensity": 0.1}),
        ("This is frustrating", {"emotion": "frustration", "intensity": 0.4}),
        ("I'm getting really annoyed", {"emotion": "anger", "intensity": 0.6}),
        ("This is fucking stupid", {"emotion": "anger", "intensity": 0.7}),
        ("suck my balls", {"emotion": "neutral", "intensity": 0.5}),  # The problem message
    ]
    
    for i, (message, sentiment) in enumerate(conversation, 1):
        agent, info = meter.process_message(message, sentiment)
        print(f"\nMessage {i}: '{message}'")
        print(f"  Agent: {agent} | Points: {info['anger_points']} | Change: +{info['points_change']}")
        print(f"  Reasons: {', '.join(info['change_reasons'])}")
        
        if agent == "enraged":
            print(f"  🎯 ENRAGED ACHIEVED at message {i}!")
            break
    
    final_status = meter.get_meter_status()
    print(f"\nFinal Status: {final_status}")

if __name__ == "__main__":
    test_insult_detection()
    test_escalation_scenario()
    
    print("\n\n✅ Insult Detection Testing Complete!")
    print("💡 If 'suck my balls' still doesn't trigger enraged, try:")
    print("   - Lower enraged threshold in anger_config.yaml")
    print("   - Increase direct_insults bonus")
    print("   - Increase anger_multiplier") 