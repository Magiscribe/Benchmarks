import os
import json
import time
import base64
import argparse
from typing import List, Dict, Any, Optional
import anthropic
import config

class ModelRunner:
    """Handles running vision models on eye chart test images."""
    
    def __init__(
        self, 
        model_name: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize the model runner.
        
        Args:
            model_name: Name of the model to use (e.g., "claude-3-sonnet-20240229", "claude-3-haiku-20240307")
            api_key: Anthropic API key. If None, will look for ANTHROPIC_API_KEY environment variable
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key must be provided or set as ANTHROPIC_API_KEY environment variable")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode an image as base64 for the API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64-encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _create_system_prompt(self) -> str:
        """
        Create a system prompt for the vision model.
        
        Returns:
            System prompt string
        """
        return (
            "You are an expert at reading text from eye chart images. You will be shown an eye chart image with "
            "multiple rows of text of decreasing size from top to bottom."
            f"There are ${config.CHARS_PER_ROW} characters per row, and the font sizes are standardized. There is only capitalized and lower case English letters in the image. "
            "\n\n"
            "Your task is to read each row of text and report what you see, starting from row 0 (top row) to the last row. "
            "Be extremely precise in your reading, attempting to identify each character correctly. "
            "If you cannot read a row clearly, make your best guess."
            "\n\n"
            "Format your response as a JSON array of objects, where each object has two fields:"
            "\n- row: The row number (starting from 0 for the top row)"
            "\n- text: The text content you read on that row"
            "\n\n"
            "Example response format:\n"
            "```json\n"
            "[\n"
            "  {\"row\": 0, \"text\": \"ABCadgeDEF\"},\n"
            "  {\"row\": 1, \"text\": \"GHIdsvvJKL\"},\n"
            "  {\"row\": 2, \"text\": \"MNOewvPQR\"}\n"
            "]\n"
            "```"
            "\n\n"
            "Only output the JSON array. Do not include any explanations or additional text outside the JSON array."
        )
    
    def run_model_on_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Run the model on a single image and return the parsed response.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dict with format [{row: int, text: str}]
        """
        # Encode the image
        encoded_image = self.encode_image(image_path)
        
        # Create the prompt
        system_prompt = self._create_system_prompt()
        user_prompt = "Read all the text in this eye chart image, row by row, starting from the top (row 0)."
        
        # Make the API call with retries
        response = None
        retries = 0
        
        while retries <= self.max_retries:
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                            ]
                        }
                    ],
                    temperature=0,
                    max_tokens=1000
                )
                break
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise Exception(f"Failed after {self.max_retries} retries: {str(e)}")
                print(f"API call failed, retrying ({retries}/{self.max_retries}): {str(e)}")
                time.sleep(self.retry_delay)
        
        if not response:
            raise Exception("Failed to get a response from the API")
        
        # Extract and parse the response
        response_text = response.content[0].text
        
        # Try to extract JSON array
        try:
            # Look for JSON array in the response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}. Attempting to fix malformed JSON...")
                    # Manual fix for common JSON errors in model responses
                    import re
                    
                    # Fix for unescaped quotes within strings
                    fixed_json = json_str
                    
                    # Fix unescaped quotes in text field values
                    pattern = r'("text": ".*?)(")(.*?")'
                    fixed_json = re.sub(pattern, r'\1\\\2\3', fixed_json)
                    
                    # Fix other common issues (add more patterns as needed)
                    # Replace non-standard quotes
                    fixed_json = fixed_json.replace('"', '"').replace('"', '"')
                    
                    print(f"Attempting to parse fixed JSON: {fixed_json[:100]}...")
                    try:
                        return json.loads(fixed_json)
                    except json.JSONDecodeError:
                        print("Still unable to parse JSON after fixes. Creating manual structure...")
                        
                        # Create a structure manually
                        results = []
                        row_pattern = r'"row"\s*:\s*(\d+)\s*,\s*"text"\s*:\s*"([^"]*?)"'
                        matches = re.findall(row_pattern, json_str)
                        
                        if matches:
                            for row_num, text in matches:
                                results.append({"row": int(row_num), "text": text})
                            return results
                        else:
                            # Last resort: create mock structure from lines
                            lines = json_str.strip().split('\n')
                            results = []
                            for i, line in enumerate(lines):
                                if line.strip() and not line.strip().startswith('{') and not line.strip().startswith('}'):
                                    # Extract any text content
                                    text_content = re.sub(r'[^a-zA-Z0-9]', '', line)
                                    if text_content:
                                        results.append({"row": i, "text": text_content})
                            return results
            else:
                # If no JSON array is found, try to parse the whole response
                return json.loads(response_text)
        except json.JSONDecodeError:
            print(f"Could not parse JSON from response. Creating fallback response.")
            print(f"Response text: {response_text[:200]}...")
            
            # Create a fallback response
            fallback = []
            lines = response_text.strip().split('\n')
            
            for i, line in enumerate(lines):
                if line.strip():
                    # Try to extract anything that looks like text
                    text_match = re.search(r'"text"\s*:\s*"([^"]*)"', line)
                    if text_match:
                        text = text_match.group(1)
                        fallback.append({"row": i, "text": text})
                    else:
                        # Just use the line as is, removing non-alphanumeric chars
                        text = re.sub(r'[^a-zA-Z0-9]', '', line)
                        if text:
                            fallback.append({"row": i, "text": text})
            
            if fallback:
                print(f"Created fallback response with {len(fallback)} rows")
                return fallback
            else:
                print(f"WARNING: Returning empty result for {image_path}")
                return []
    
    def run_on_dataset(self, dataset_path: str) -> List[List[Dict[str, Any]]]:
        """
        Run the model on all images in a dataset.
        
        Args:
            dataset_path: Path to the dataset JSON file
            
        Returns:
            List of model responses, one per image
        """
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        results = []
        for i, item in enumerate(dataset):
            print(f"Processing image {i+1}/{len(dataset)}: {item['image_path']}")
            response = self.run_model_on_image(item['image_path'])
            results.append(response)
            # Add a small delay between requests
            if i < len(dataset) - 1:
                time.sleep(1)
        
        return results
    
    def save_responses(self, responses: List[List[Dict[str, Any]]], output_path: str) -> None:
        """
        Save model responses to a JSON file.
        
        Args:
            responses: List of model responses
            output_path: Path to save the responses
        """
        with open(output_path, 'w') as f:
            json.dump(responses, f, indent=2)

def parse_args():
    parser = argparse.ArgumentParser(description="Run AI models on the eye chart dataset")
    
    parser.add_argument("--model", type=str, default="claude-3-sonnet-20240229", 
                      help="Model name (default: claude-3-sonnet-20240229)")
    parser.add_argument("--dataset", type=str, default="dataset.json", 
                      help="Path to dataset file (default: dataset.json)")
    parser.add_argument("--output", type=str, default=None, 
                      help="Path to save model responses (default: model_name_responses.json)")
    parser.add_argument("--api-key", type=str, default=None, 
                      help="API key (default: uses ANTHROPIC_API_KEY environment variable)")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Set default output path if not provided
    if not args.output:
        model_short_name = args.model.split("-")[-1] if "-" in args.model else args.model
        args.output = f"{model_short_name}_responses.json"
    
    runner = ModelRunner(model_name=args.model, api_key=args.api_key)
    
    print(f"Running model {args.model} on dataset {args.dataset}")
    responses = runner.run_on_dataset(args.dataset)
    
    runner.save_responses(responses, args.output)
    print(f"Saved responses to {args.output}")