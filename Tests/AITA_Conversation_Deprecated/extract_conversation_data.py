"""
Extract conversation data into separate JSON files for analysis:
- scenarios.json: Just scenario_id and text
- conversations.json: Full conversations with initial positions but NO final positions or current_position tracking
- final_positions.json: Just the final verdicts
- example.json: One complete example showing the format
"""

import json
import os
from pathlib import Path

def load_dataset():
    """Load the original dataset with scenario texts"""
    with open('dataset.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_all_conversations():
    """Load all conversation JSON files from the conversations directory"""
    conversations = []
    conv_dir = Path('conversations')
    
    for conv_file in conv_dir.glob('*.json'):
        with open(conv_file, 'r', encoding='utf-8') as f:
            conv_data = json.load(f)
            conversations.append(conv_data)
    
    return conversations

def extract_scenarios(dataset):
    """Extract just scenario_id and text"""
    scenarios = []
    for scenario in dataset:
        scenarios.append({
            "scenario_id": scenario["scenario_id"],
            "text": scenario["text"]
        })
    return scenarios

def extract_conversations(conversations_data):
    """Extract conversations WITHOUT final positions or current_position tracking"""
    cleaned_conversations = []
    
    for conv in conversations_data:
        # Strip out current_position from all turns, keep timestamp
        cleaned_turns = []
        for turn in conv.get('turns', []):
            cleaned_turn = {
                "speaker": turn["speaker"],
                "message": turn["message"],
                "timestamp": turn["timestamp"]
            }
            cleaned_turns.append(cleaned_turn)
        
        cleaned_conv = {
            "conversation_id": conv["conversation_id"],
            "turns": cleaned_turns
        }
        cleaned_conversations.append(cleaned_conv)
    
    return cleaned_conversations

def extract_final_positions(conversations_data):
    """Extract just the final positions for each conversation"""
    final_positions = []
    
    for conv in conversations_data:
        final_pos = {
            "conversation_id": conv["conversation_id"],
            "final_positions": conv.get("final_positions", {})
        }
        final_positions.append(final_pos)
    
    return final_positions

def create_example(conversations_data):
    """Create one complete example with all data"""
    if not conversations_data:
        return None
    
    # Use the first conversation as the example
    example = conversations_data[0]
    return example

def main():
    print("Loading dataset...")
    dataset = load_dataset()
    
    print("Loading all conversations...")
    conversations_data = load_all_conversations()
    print(f"Found {len(conversations_data)} conversations")
    
    # Extract different views of the data
    print("\nExtracting scenarios...")
    scenarios = extract_scenarios(dataset)
    
    print("Extracting conversations (without final positions)...")
    conversations = extract_conversations(conversations_data)
    
    print("Extracting final positions...")
    final_positions = extract_final_positions(conversations_data)
    
    print("Creating example...")
    example = create_example(conversations_data)
    
    # Save all files
    print("\nSaving files...")
    
    with open('scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    print(f"✓ scenarios.json - {len(scenarios)} scenarios")
    
    with open('conversations.json', 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    print(f"✓ conversations.json - {len(conversations)} conversations")
    
    with open('final_positions.json', 'w', encoding='utf-8') as f:
        json.dump(final_positions, f, indent=2, ensure_ascii=False)
    print(f"✓ final_positions.json - {len(final_positions)} conversations")
    
    if example:
        with open('example.json', 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2, ensure_ascii=False)
        print(f"✓ example.json - conversation_id: {example['conversation_id']}")
    
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE!")
    print("="*60)
    print("\nFiles created:")
    print("  - scenarios.json: Scenario texts only")
    print("  - conversations.json: Full debates WITHOUT final positions")
    print("  - final_positions.json: Final verdicts only")
    print("  - example.json: One complete example with everything")
    print("\nUse Case:")
    print("  Give a model scenarios.json + conversations.json")
    print("  Ask it to predict what's in final_positions.json")
    print("  Use example.json to show the format")

if __name__ == "__main__":
    main()
