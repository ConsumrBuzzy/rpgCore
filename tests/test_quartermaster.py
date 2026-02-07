"""
Test script for Quartermaster Logic (v1.1 - Stats Integration)
"""
import sys
import os

# Add src to path
sys.path.append(r"c:\Github\rpgCore\src")

from quartermaster import Quartermaster

def test_sticky_floors():
    """Verify Sticky Floors logic."""
    print("Testing 'Sticky Floors' logic...")
    qm = Quartermaster()
    
    # Test case: Finesse with Sticky Floors
    outcome = qm.calculate_outcome(
        intent_id="finesse",
        room_tags=["Sticky Floors"],
        base_difficulty=10
    )
    
    if "Sticky floors hindered movement" in outcome.narrative_context:
        print("PASS: Sticky floors noticed for Finesse.")
    else:
        print(f"FAIL: Sticky floors ignored. Context: {outcome.narrative_context}")

def test_attribute_mapping():
    """Verify Attribute logic."""
    print("\nTesting Attribute Integration...")
    qm = Quartermaster()
    
    # 1. Strength Bonus for Force
    outcome = qm.calculate_outcome(
        intent_id="force",
        room_tags=[],
        player_stats={"strength": 5, "dexterity": 0, "intelligence": 0, "charisma": 0}
    )
    
    if "Strength (+5)" in outcome.narrative_context:
        print("PASS: Strength bonus applied correctly.")
    else:
        print(f"FAIL: Strength bonus missing. Context: {outcome.narrative_context}")

    # 2. Charisma Penalty for Charm (-2 Charisma)
    outcome_neg = qm.calculate_outcome(
        intent_id="charm",
        room_tags=[],
        player_stats={"strength": 0, "dexterity": 0, "intelligence": 0, "charisma": -2}
    )
    
    if "Charisma (-2)" in outcome_neg.narrative_context:
        print("PASS: Negative Charisma applied correctly.")
    else:
        print(f"FAIL: Negative Charisma missing. Context: {outcome_neg.narrative_context}")

def test_combined_difficulty():
    """Verify Stacked Penalties (Rowdy Crowd + Low Charisma)."""
    print("\nTesting Combined Difficulty (The 'Rowdy Charm' Case)...")
    qm = Quartermaster()
    
    # Charm (-2 Crowd) + (-2 Charisma) = -4 Total Modifier
    outcome = qm.calculate_outcome(
        intent_id="charm",
        room_tags=["Rowdy Crowd"],
        player_stats={"strength": 0, "dexterity": 0, "intelligence": 0, "charisma": -2}
    )
    
    context = outcome.narrative_context
    if "Crowd noise" in context and "Charisma (-2)" in context:
        print("PASS: Both Crowd and Charisma penalties applied.")
        print(f"Narrative Context: {context}")
    else:
        print(f"FAIL: Missing context modifiers. Context: {context}")

def main():
    test_sticky_floors()
    test_attribute_mapping()
    test_combined_difficulty()

if __name__ == "__main__":
    main()
