import json
import os
from image_generator import EyeChartGenerator

class DatasetCreator:
    def __init__(self, output_file="dataset.json"):
        self.output_file = output_file
        self.image_generator = EyeChartGenerator()
    
    def create_dataset(self, num_fonts=None, num_images_per_font=1):
        """
        Creates a dataset of eye chart images with ground truth text.
        
        Args:
            num_fonts: Number of fonts to use. If None, uses all available fonts.
            num_images_per_font: Number of images to generate per font.
            
        Returns:
            List of dataset entries.
        """
        # Generate test images
        if num_fonts is None:
            fonts = list(self.image_generator.fonts.keys())
        else:
            fonts = list(self.image_generator.fonts.keys())[:num_fonts]
        
        test_set = self.image_generator.generate_test_set(fonts, num_images_per_font)
        
        # Format the dataset with ground truth
        dataset = []
        for item in test_set:
            # Extract row-by-row ground truth from metadata
            ground_truth = []
            for row_data in item['metadata']['row_data']:
                ground_truth.append({
                    "row": row_data['row'],  # Already 0-indexed
                    "text": row_data['text'],
                    "size": row_data['size']
                })
            
            # Create dataset entry
            entry = {
                "image_path": item['image_path'],
                "metadata": {
                    "font": item['metadata']['font'],
                    "font_sizes": item['metadata']['font_sizes'],
                    "num_rows": item['metadata']['num_rows'],
                    "chars_per_row": item['metadata']['chars_per_row']
                },
                "ground_truth": ground_truth
            }
            
            dataset.append(entry)
        
        # Print a summary before saving
        font_counts = {}
        for entry in dataset:
            font = entry["metadata"]["font"]
            font_counts[font] = font_counts.get(font, 0) + 1
            
        print(f"\nDataset summary:")
        for font, count in font_counts.items():
            print(f"  {font}: {count} images")
        
        # Save dataset to JSON file
        with open(self.output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return dataset
    
    def load_dataset(self):
        """
        Loads a previously created dataset.
        
        Returns:
            List of dataset entries if file exists, empty list otherwise.
        """
        if not os.path.exists(self.output_file):
            return []
        
        with open(self.output_file, 'r') as f:
            return json.load(f)


if __name__ == "__main__":
    creator = DatasetCreator()
    dataset = creator.create_dataset(num_images_per_font=1)
    print(f"Created dataset with {len(dataset)} entries")
    print(f"Dataset saved to {creator.output_file}")
    
    # Example of how to access dataset entries
    if dataset:
        sample = dataset[0]
        print(f"\nSample entry:")
        print(f"Image: {sample['image_path']}")
        print(f"Font: {sample['metadata']['font']}")
        print(f"Font sizes: {sample['metadata']['font_sizes']}")
        print(f"Number of rows: {sample['metadata']['num_rows']}")
        print(f"Characters per row: {sample['metadata']['chars_per_row']}")
        print(f"Ground truth for first row (row 0): {sample['ground_truth'][0]['text']} (size: {sample['ground_truth'][0]['size']})")
        print(f"Ground truth for last row (row {sample['metadata']['num_rows']-1}): {sample['ground_truth'][-1]['text']} (size: {sample['ground_truth'][-1]['size']})")