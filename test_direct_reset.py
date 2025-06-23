#!/usr/bin/env python3
"""
Test the reset functionality directly
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator.orchestrator import Orchestrator

def test_direct_reset():
    """Test reset functionality directly on orchestrator instance"""
    print("🔧 Testing Direct Reset Functionality 🔧")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Check initial state
    print("Initial state:")
    print(f"  Anger points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current level: {orchestrator.anger_meter.current_level}")
    print(f"  Current agent: {orchestrator.current_agent}")
    
    # Build up anger
    print(f"\nBuilding anger...")
    orchestrator.anger_meter.process_message("fuck you", {'emotion': 'anger', 'intensity': 0.8})
    orchestrator.current_agent = "enraged"
    
    print("After building anger:")
    print(f"  Anger points: {orchestrator.anger_meter.anger_points}")
    print(f"  Current level: {orchestrator.anger_meter.current_level}")
    print(f"  Current agent: {orchestrator.current_agent}")
    
    # Test anger meter reset directly
    print(f"\nTesting anger meter reset directly...")
    print(f"  Before: {orchestrator.anger_meter.anger_points} points")
    orchestrator.anger_meter.reset_meter()
    print(f"  After: {orchestrator.anger_meter.anger_points} points")
    
    # Test full orchestrator reset
    print(f"\nTesting full orchestrator reset...")
    # Build anger again
    orchestrator.anger_meter.process_message("damn it", {'emotion': 'anger', 'intensity': 0.7})
    orchestrator.current_agent = "agitated"
    
    print(f"  Before full reset:")
    print(f"    Anger points: {orchestrator.anger_meter.anger_points}")
    print(f"    Current agent: {orchestrator.current_agent}")
    print(f"    Emotional history: {len(orchestrator.emotional_history)} items")
    
    orchestrator.reset_state()
    
    print(f"  After full reset:")
    print(f"    Anger points: {orchestrator.anger_meter.anger_points}")
    print(f"    Current agent: {orchestrator.current_agent}")
    print(f"    Emotional history: {len(orchestrator.emotional_history)} items")
    
    # Verify reset worked
    if (orchestrator.anger_meter.anger_points == 0.0 and 
        orchestrator.current_agent == "normal" and
        len(orchestrator.emotional_history) == 0):
        print("\n✅ Direct reset test PASSED!")
    else:
        print("\n❌ Direct reset test FAILED!")

def test_server_instance():
    """Test if there might be a different server instance"""
    print(f"\n🌐 Testing Server Instance Issue 🌐")
    print("=" * 50)
    
    # Import the same way the server does
    from orchestrator.orchestrator import Orchestrator
    
    # Create orchestrator same way as main.py
    test_orchestrator = Orchestrator()
    
    print("Test orchestrator initial state:")
    print(f"  Anger points: {test_orchestrator.anger_meter.anger_points}")
    print(f"  Current agent: {test_orchestrator.current_agent}")
    
    # Build anger
    test_orchestrator.anger_meter.process_message("test anger", {'emotion': 'anger', 'intensity': 0.8})
    print(f"After building anger: {test_orchestrator.anger_meter.anger_points} points")
    
    # Reset
    test_orchestrator.reset_state()
    print(f"After reset: {test_orchestrator.anger_meter.anger_points} points")
    
    if test_orchestrator.anger_meter.anger_points == 0.0:
        print("✅ Test orchestrator reset works correctly")
        print("❓ Issue might be with server instance persistence")
    else:
        print("❌ Test orchestrator reset also failing")

if __name__ == "__main__":
    test_direct_reset()
    test_server_instance()
    
    print("\n🔍 Diagnosis:")
    print("If direct reset works but server doesn't, the issue is:")
    print("1. Server instance not being reset properly")
    print("2. Multiple orchestrator instances")
    print("3. Caching or persistence layer")
    print("4. Race condition in reset timing") 