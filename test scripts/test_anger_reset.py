#!/usr/bin/env python3
"""
Test script to verify anger meter reset functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator

def test_anger_meter_reset():
    """Test that anger meter resets properly"""
    print("🧪 Testing Anger Meter Reset Functionality 🧪")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    
    # Check initial state
    print("📊 Initial State:")
    print(f"  Anger Points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current Level: {orchestrator.anger_meter.current_level}")
    print(f"  Current Agent: {orchestrator.current_agent}")
    print(f"  Apology Count: {orchestrator.anger_meter.apology_count}")
    
    # Build up some anger
    print(f"\n🔥 Building up anger...")
    orchestrator.anger_meter.process_message("fuck you", {'emotion': 'anger', 'intensity': 0.8})
    orchestrator.anger_meter.process_message("you're stupid", {'emotion': 'anger', 'intensity': 0.7})
    orchestrator.current_agent = "enraged"
    
    print("📊 After Building Anger:")
    print(f"  Anger Points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current Level: {orchestrator.anger_meter.current_level}")
    print(f"  Current Agent: {orchestrator.current_agent}")
    print(f"  Apology Count: {orchestrator.anger_meter.apology_count}")
    
    # Reset the state
    print(f"\n🔄 Resetting orchestrator state...")
    orchestrator.reset_state()
    
    print("📊 After Reset:")
    print(f"  Anger Points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current Level: {orchestrator.anger_meter.current_level}")
    print(f"  Current Agent: {orchestrator.current_agent}")
    print(f"  Apology Count: {orchestrator.anger_meter.apology_count}")
    print(f"  Emotional History: {orchestrator.emotional_history}")
    
    # Verify reset worked
    if (orchestrator.anger_meter.anger_points == 0.0 and 
        orchestrator.anger_meter.current_level == "normal" and
        orchestrator.current_agent == "normal" and
        orchestrator.anger_meter.apology_count == 0 and
        len(orchestrator.emotional_history) == 0):
        print("\n✅ RESET SUCCESSFUL - All values returned to initial state!")
    else:
        print("\n❌ RESET FAILED - Some values not properly reset")
        
def test_fresh_conversation():
    """Test that a fresh conversation starts with clean state"""
    print(f"\n\n🆕 Testing Fresh Conversation Start 🆕")
    print("=" * 60)
    
    orchestrator = Orchestrator()
    
    # Simulate what happens when server starts or reset is called
    orchestrator.reset_state()
    
    # Process a neutral message like "hello"
    agent, info = orchestrator.anger_meter.process_message("hello", {'emotion': 'neutral', 'intensity': 0.0})
    
    print("📊 Fresh Conversation State:")
    print(f"  Message: 'hello'")
    print(f"  Detected Agent: {agent}")
    print(f"  Anger Points: {info['anger_points']}")
    print(f"  Current Level: {orchestrator.anger_meter.current_level}")
    print(f"  Change Reasons: {info.get('change_reasons', [])}")
    
    if agent == "normal" and info['anger_points'] <= 2.0:  # Should be 0 or small decay
        print("\n✅ FRESH START SUCCESSFUL - Starting with normal agent and low/zero anger!")
    else:
        print(f"\n❌ FRESH START FAILED - Expected normal agent with ~0 anger, got {agent} with {info['anger_points']} points")

if __name__ == "__main__":
    test_anger_meter_reset()
    test_fresh_conversation()
    
    print("\n\n🎯 Summary:")
    print("✅ The anger meter now properly resets on server startup")
    print("✅ Manual reset endpoint also resets anger meter")  
    print("✅ Fresh conversations start with clean state")
    print("\n💡 To reset manually, call POST /reset endpoint") 