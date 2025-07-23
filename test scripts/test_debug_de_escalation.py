#!/usr/bin/env python3
"""
Debug test to see exactly what's happening in the de-escalation logic
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.anger_meter import AngerMeter

def debug_de_escalation():
    """Debug the de-escalation logic step by step"""
    print("🔍 Debugging De-escalation Logic 🔍")
    print("=" * 60)
    
    meter = AngerMeter()
    
    # Get to enraged state
    print("Getting to enraged state...")
    meter.process_message("fuck you asshole", {'emotion': 'anger', 'intensity': 0.9})
    meter.process_message("you're stupid", {'emotion': 'anger', 'intensity': 0.8})
    agent, info = meter.process_message("shut up", {'emotion': 'anger', 'intensity': 0.7})
    
    print(f"Enraged state: {agent} agent, {info['anger_points']} points")
    print(f"Current level in meter: {meter.current_level}")
    print(f"Apology count: {meter.apology_count}")
    
    # First apology
    print(f"\n--- First Apology Debug ---")
    print(f"Before apology:")
    print(f"  Current level: {meter.current_level}")
    print(f"  Anger points: {meter.anger_points}")
    print(f"  Apology count: {meter.apology_count}")
    
    agent, info = meter.process_message("I'm sorry", {'emotion': 'neutral', 'intensity': 0.1})
    
    print(f"After apology:")
    print(f"  Returned agent: {agent}")
    print(f"  Current level: {meter.current_level}")
    print(f"  Anger points: {meter.anger_points}")
    print(f"  Apology count: {meter.apology_count}")
    print(f"  Can de-escalate: {meter._can_de_escalate_from_enraged()}")
    print(f"  Apologies needed: {meter._get_apologies_needed()}")
    
    # Second apology
    print(f"\n--- Second Apology Debug ---")
    print(f"Before second apology:")
    print(f"  Current level: {meter.current_level}")
    print(f"  Anger points: {meter.anger_points}")
    print(f"  Apology count: {meter.apology_count}")
    print(f"  Can de-escalate: {meter._can_de_escalate_from_enraged()}")
    
    agent, info = meter.process_message("I really apologize", {'emotion': 'neutral', 'intensity': 0.1})
    
    print(f"After second apology:")
    print(f"  Returned agent: {agent}")
    print(f"  Current level: {meter.current_level}")
    print(f"  Anger points: {meter.anger_points}")
    print(f"  Apology count: {meter.apology_count}")
    print(f"  Can de-escalate: {meter._can_de_escalate_from_enraged()}")
    print(f"  Apologies needed: {meter._get_apologies_needed()}")
    
    # Check thresholds
    print(f"\n--- Threshold Analysis ---")
    thresholds = meter.config['thresholds']
    points = meter.anger_points
    print(f"Current points: {points}")
    print(f"Enraged threshold: {thresholds['enraged']}")
    print(f"Agitated threshold: {thresholds['agitated']}")
    print(f"Irritated threshold: {thresholds['irritated']}")
    
    # What would agent be based on points alone?
    if points >= thresholds['enraged']:
        expected_agent = "enraged"
    elif points >= thresholds['agitated']:
        expected_agent = "agitated"
    elif points >= thresholds['irritated']:
        expected_agent = "irritated"
    else:
        expected_agent = "normal"
    
    print(f"Expected agent based on points: {expected_agent}")
    print(f"Actual agent returned: {agent}")
    
    if expected_agent != agent and meter.apology_count >= 2:
        print("❌ BUG: Should have de-escalated but didn't!")
    elif expected_agent == agent and meter.apology_count < 2:
        print("✅ Correctly blocked de-escalation")
    elif expected_agent != agent and meter.apology_count >= 2:
        print("✅ Correctly allowed de-escalation")

if __name__ == "__main__":
    debug_de_escalation() 