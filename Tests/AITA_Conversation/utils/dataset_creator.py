import json
import os
from typing import List, Dict


class DatasetCreator:
    """Creates AITA conversation test dataset with placeholder scenarios."""
    
    def __init__(self, output_file: str = "dataset.json"):
        """
        Initialize dataset creator.
        
        Args:
            output_file: Path to save the dataset JSON file
        """
        self.output_file = output_file
    
    def create_dataset(self, num_scenarios: int = 10) -> List[Dict]:
        """
        Create a dataset of AITA scenarios with placeholder text.
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            List of scenario dictionaries
        """
        dataset = []
        
        for i in range(1, num_scenarios + 1):
            scenario = {
                "scenario_id": f"aita_{i:03d}",
                "title": f"Placeholder Title {i}",
                "text": f"Placeholder scenario text {i}. Replace this with actual AITA scenario from Reddit.",
                "category": "placeholder"
            }
            dataset.append(scenario)
        
        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"Created dataset with {len(dataset)} placeholder scenarios")
        print(f"Dataset saved to {self.output_file}")
        print("\nNOTE: Replace placeholder text with actual AITA scenarios from Reddit")
        
        return dataset
    
    def get_dataset_stats(self, dataset: List[Dict]) -> Dict:
        """
        Get statistics about the dataset.
        
        Args:
            dataset: List of scenario dictionaries
            
        Returns:
            Dictionary with dataset statistics
        """
        return {
            "total_scenarios": len(dataset),
            "categories": list(set(s["category"] for s in dataset))
        }


if __name__ == "__main__":
    creator = DatasetCreator()
    dataset = creator.create_dataset(num_scenarios=10)
    stats = creator.get_dataset_stats(dataset)
    print(f"\nDataset stats: {stats}")
