import json
import csv
import os
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file in root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

def load_dataset():
    # Go up one level from utils/ to get to the test directory
    test_dir = os.path.dirname(os.path.dirname(__file__))
    dataset_file = os.path.join(test_dir, os.getenv('DATASET_FILE', 'dataset.json'))
    with open(dataset_file, 'r') as f:
        return json.load(f)

def process_responses():
    results = defaultdict(lambda: {"correct": 0, "total": 0})
    # Go up one level from utils/ to get to the test directory  
    test_dir = os.path.dirname(os.path.dirname(__file__))
    responses_dir = Path(os.path.join(test_dir, os.getenv('RESPONSES_DIR', 'responses')))
    dataset = load_dataset()

    # Process each response file
    for response_file in responses_dir.glob('*.json'):
        model = response_file.stem.replace('_responses', '')
        
        with open(response_file, 'r') as f:
            model_responses = json.load(f)        # Process each image's responses
        for image_results in model_responses:            # Find matching dataset entry by image path            # Normalize both paths for comparison by:
            # 1. Converting backslashes to forward slashes
            # 2. Removing any leading assets/ or assets\
            resp_path = image_results['image_path'].replace('\\', '/').replace('assets/', '')
            
            # Try to find exact match by normalizing both paths
            matching_data = next((img for img in dataset 
                                if img['image_path'].replace('\\', '/').replace('assets/', '') == resp_path), None)
            
            if not matching_data:
                print(f"ERROR: Could not find matching image for {resp_path}")
                continue
                
            font = matching_data['metadata']['font']
            
            # Compare ground truth with responses
            for gt_row, resp_row in zip(matching_data['ground_truth'], image_results['responses']):
                size = gt_row['size']
                gt_text = gt_row['text']
                resp_text = resp_row['text']
                
                # Compare character by character
                for gt_char, resp_char in zip(gt_text, resp_text):
                    key = (model, font, size, gt_char)
                    results[key]["total"] += 1
                    if gt_char == resp_char:
                        results[key]["correct"] += 1

    return results

def write_results(results, output_file=None):
    if output_file is None:
        # Export to centralized Results folder with benchmark name prefix
        # Go up from utils/ -> LLM_Eye_Test/ -> Tests/ -> Benchmarks/ -> Results/
        results_dir = os.path.join('..', '..', '..', 'Results')
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, 'LLM_Eye_Test_model_results.csv')
    
    headers = ["model", "font", "size", "character", "correct", "total"]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        # Sort results for consistent output
        sorted_results = sorted(results.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3]))
        for (model, font, size, char), stats in sorted_results:
            writer.writerow([
                model, font, size, char,
                stats["correct"], stats["total"]
            ])

def main():
    results = process_responses()
    write_results(results)
    print("Results written to ../../../Results/LLM_Eye_Test_model_results.csv")

if __name__ == "__main__":
    main()
