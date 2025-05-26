
import json
import os
import pandas as pd


def process_responses():
    """
    Process all model responses and generate a results CSV file with directional errors
    """
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset.json")
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    print(f"Dataset loaded with {len(dataset)} items")    # Create ground truth lookup by filename
    ground_truth = {}
    for item in dataset:
        # Extract filename from image_path (e.g., "assets\\coordinate_grid_1748135594214.png" -> "coordinate_grid_1748135594214.png")
        image_path = item['image_path']
        filename = os.path.basename(image_path)
        ground_truth[filename] = item['ground_truth']
    
    # Get response files
    responses_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "responses")
    
    results = []
    for response_file in os.listdir(responses_dir):
        if response_file.endswith("_responses.json"):
            model_name = response_file.replace("_responses.json", "")
            
            # Load responses
            response_path = os.path.join(responses_dir, response_file)
            with open(response_path, 'r') as f:
                responses = json.load(f)
            
            # Process each response
            for response in responses:
                image_path = response['image_path']
                filename = os.path.basename(image_path)
                
                # Extract grid_id from filename (timestamp)
                # e.g., coordinate_grid_1748135594214.png -> 1748135594214
                grid_id = filename.replace('coordinate_grid_', '').replace('.png', '')
                
                if filename not in ground_truth:
                    print(f"Warning: No ground truth found for {filename}")
                    continue
                gt_squares = ground_truth[filename]
                predicted_squares = response['responses']                # Process each square (0-4)
                for square_id in range(5):
                    if square_id < len(gt_squares) and square_id < len(predicted_squares):
                        gt_square = gt_squares[square_id]
                        pred_square = predicted_squares[square_id]
                        
                        # Check if the predicted square has the expected format
                        if 'x' in pred_square and 'y' in pred_square:
                            # Calculate directional errors (predicted - actual)
                            error_X = pred_square['x'] - gt_square['x']
                            error_Y = pred_square['y'] - gt_square['y']
                            results.append({
                                'model': model_name,
                                'grid_id': grid_id,
                                'square_id': square_id,
                                'error_X': error_X,
                                'error_Y': error_Y
                            })
                        else:
                            # Handle malformed predictions (e.g., error messages)
                            print(f"Warning: Malformed prediction for {model_name}, {filename}, square {square_id}: {pred_square}")
                            results.append({
                                'model': model_name,
                                'grid_id': grid_id,
                                'square_id': square_id,
                                'error_X': 999,  # Use a large error value to indicate malformed data
                                'error_Y': 999
                            })
                    else:
                        # Handle missing predictions or ground truth
                        results.append({                            'model': model_name,
                            'grid_id': grid_id,
                            'square_id': square_id,
                            'error_X': 999,  # Use a large error value to indicate missing data
                            'error_Y': 999
                        })
    
    print(f"\nGenerated {len(results)} result rows")
    
    # Save results - go up to Benchmarks directory, then into Results
    # Current path: Benchmarks/Tests/Coordinate_Grid/utils/synthesize_model_results.py
    # Target path: Benchmarks/Results/Coordinate_Grid_model_results.csv
    benchmarks_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    output_path = os.path.join(benchmarks_dir, "Results", "Coordinate_Grid_model_results.csv")
    
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    
    print(f"Results saved to {output_path}")
    print(f"CSV shape: {df.shape}")
    print("First few rows:")
    print(df.head(10))


def main():
    """
    Main function to process responses and generate results CSV
    """
    process_responses()
    print("Model results synthesized with directional errors to Benchmarks/Results/Coordinate_Grid_model_results.csv")


if __name__ == "__main__":
    main()
