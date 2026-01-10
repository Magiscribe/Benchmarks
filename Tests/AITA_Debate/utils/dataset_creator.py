"""
DatasetCreator - Creates AITA scenario datasets for debate testing.
"""

import json
import os
from typing import List, Dict


class DatasetCreator:
    """Creates AITA scenario datasets."""
    
    def __init__(self, output_file: str = "dataset.json"):
        """
        Initialize the dataset creator.
        
        Args:
            output_file: Path to output JSON file
        """
        self.output_file = output_file
    
    def create_dataset(self, num_scenarios: int = 10) -> List[Dict]:
        """
        Create a dataset with placeholder scenarios.
        
        For real benchmarks, replace these with actual AITA scenarios.
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            List of scenario dictionaries
        """
        # Check if scenarios.json exists (real scenarios)
        scenarios_path = os.path.join(os.path.dirname(__file__), "..", "scenarios.json")
        if os.path.exists(scenarios_path):
            print(f"Loading existing scenarios from {scenarios_path}")
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                scenarios = json.load(f)
            
            # Save to output file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(scenarios, f, indent=2, ensure_ascii=False)
            
            return scenarios
        
        # Generate placeholder scenarios
        scenarios = []
        for i in range(1, num_scenarios + 1):
            scenario = {
                "scenario_id": f"aita_{i:03d}",
                "title": f"Placeholder Scenario {i}",
                "text": f"This is a placeholder scenario {i}. Replace with actual AITA content from Reddit.",
                "category": "placeholder"
            }
            scenarios.append(scenario)
        
        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(scenarios, f, indent=2, ensure_ascii=False)
        
        print(f"Created {num_scenarios} placeholder scenarios in {self.output_file}")
        print("Replace with actual AITA scenarios from Reddit for real benchmarking.")
        
        return scenarios


if __name__ == "__main__":
    creator = DatasetCreator()
    creator.create_dataset()
