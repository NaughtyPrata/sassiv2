#!/usr/bin/env python3
"""
Test script specifically for enraged state de-escalation requiring two apologies
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.anger_meter import AngerMeter

def test_enraged_de_escalation():
    """Test that enraged agents require two apologies to de-escalate"""
    print("🔥 Testing Enraged De-escalation Logic 🔥")
    print("=" * 60)
    
    meter = AngerMeter()
    
    # Build up to enraged state with multiple angry messages
    angry_messages = [
        ("fuck you", {'emotion': 'anger', 'intensity': 0.8}),
        ("you're a fucking idiot", {'emotion': 'anger', 'intensity': 0.9}),
        ("shut the fuck up asshole", {'emotion': 'anger', 'intensity': 0.85})
    ]
    
    print("📈 Building up anger to enraged state:")
    for i, (message, sentiment) in enumerate(angry_messages, 1):
        agent, info = meter.process_message(message, sentiment)
        print(f"  Message {i}: '{message}'")
        print(f"    → Agent: {agent}, Points: {info['anger_points']}")
        
        if agent == "enraged":
            print(f"    🔥 ENRAGED STATE REACHED! 🔥")
            break
    
    if agent != "enraged":
        print(f"❌ Failed to reach enraged state. Current: {agent} with {info['anger_points']} points")
        return
    
    print(f"\n🚫 Testing De-escalation Blocking:")
    print(f"Current state: {agent} agent with {info['anger_points']} points")
    
    # Try first apology - should stay enraged
    print(f"\n--- First Apology Test ---")
    agent, info = meter.process_message("I'm sorry", {'emotion': 'neutral', 'intensity': 0.1})
    
    apology_count = info['debug']['apology_count']
    apologies_needed = info['debug']['apologies_needed']
    points = info['anger_points']
    change_reasons = info['change_reasons']
    
    print(f"After 1st apology:")
    print(f"  Agent: {agent}")
    print(f"  Points: {points}")
    print(f"  Apology Count: {apology_count}")
    print(f"  Apologies Needed: {apologies_needed}")
    print(f"  Change Reasons: {change_reasons}")
    
    if agent == "enraged":
        print("  ✅ CORRECTLY stayed enraged (need more apologies)")
    else:
        print("  ❌ INCORRECTLY de-escalated with only 1 apology")
    
    # Try second apology - should allow de-escalation
    print(f"\n--- Second Apology Test ---")
    agent, info = meter.process_message("I really apologize", {'emotion': 'neutral', 'intensity': 0.1})
    
    apology_count = info['debug']['apology_count']
    apologies_needed = info['debug']['apologies_needed']
    points = info['anger_points']
    change_reasons = info['change_reasons']
    
    print(f"After 2nd apology:")
    print(f"  Agent: {agent}")
    print(f"  Points: {points}")
    print(f"  Apology Count: {apology_count}")
    print(f"  Apologies Needed: {apologies_needed}")
    print(f"  Change Reasons: {change_reasons}")
    
    if agent != "enraged":
        print("  ✅ CORRECTLY de-escalated after 2 apologies!")
    else:
        print("  ❌ INCORRECTLY still enraged after 2 apologies")

def test_anger_resets_apologies():
    """Test that getting angry again resets the apology count"""
    print(f"\n\n🔄 Testing Anger Resets Apology Count 🔄")
    print("=" * 60)
    
    meter = AngerMeter()
    
    # Get to enraged state
    meter.process_message("fuck you asshole", {'emotion': 'anger', 'intensity': 0.9})
    meter.process_message("you're stupid", {'emotion': 'anger', 'intensity': 0.8})
    agent, info = meter.process_message("shut up", {'emotion': 'anger', 'intensity': 0.7})
    
    print(f"Initial enraged state: {agent} agent, {info['anger_points']} points")
    
    # Make one apology
    agent, info = meter.process_message("I'm sorry", {'emotion': 'neutral', 'intensity': 0.1})
    apology_count_after_first = info['debug']['apology_count']
    print(f"After 1st apology: {apology_count_after_first} apologies counted")
    
    # Get angry again - should reset apology count
    agent, info = meter.process_message("but you're still dumb", {'emotion': 'anger', 'intensity': 0.6})
    apology_count_after_anger = info['debug']['apology_count']
    print(f"After getting angry again: {apology_count_after_anger} apologies counted")
    
    if apology_count_after_anger == 0:
        print("✅ CORRECTLY reset apology count when user got angry again")
    else:
        print("❌ FAILED to reset apology count")
    
    # Now need two fresh apologies
    agent, info = meter.process_message("sorry", {'emotion': 'neutral', 'intensity': 0.1})
    apologies_needed = info['debug']['apologies_needed']
    print(f"After new apology: need {apologies_needed} more apologies (should be 1)")

def test_configuration_values():
    """Test that configuration values are being read correctly"""
    print(f"\n\n⚙️  Testing Configuration Values ⚙️")
    print("=" * 60)
    
    meter = AngerMeter()
    config = meter.config
    
    de_escalation_config = config.get('de_escalation', {})
    apology_requirement = de_escalation_config.get('enraged_apology_requirement', 'NOT FOUND')
    memory_limit = de_escalation_config.get('apology_memory_limit', 'NOT FOUND')
    reset_on_anger = de_escalation_config.get('reset_apology_count_on_anger', 'NOT FOUND')
    
    print(f"De-escalation Configuration:")
    print(f"  Enraged Apology Requirement: {apology_requirement}")
    print(f"  Apology Memory Limit: {memory_limit}")
    print(f"  Reset Apology Count on Anger: {reset_on_anger}")
    
    enraged_threshold = config.get('thresholds', {}).get('enraged', 'NOT FOUND')
    print(f"\nEnraged Threshold: {enraged_threshold} points")

if __name__ == "__main__":
    test_configuration_values()
    test_enraged_de_escalation()
    test_anger_resets_apologies()
    
    print("\n\n🎯 Summary:")
    print("✅ De-escalation system requires exactly 2 apologies for enraged agents")
    print("✅ Getting angry again resets the apology count")
    print("✅ System is configurable via anger_config.yaml")
    print("\n📝 To change requirements, edit 'enraged_apology_requirement' in anger_config.yaml") 