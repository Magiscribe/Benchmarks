import os
import json
import time
import base64
import argparse
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import config
from vision_providers import PROVIDER_REGISTRY, VisionProvider

# Load environment variables
load_dotenv()

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
            model_name: Name of the model to use (e.g., "claude-3-sonnet-20240229", "gpt-4-vision-preview")
            api_key: API key. If None, will look for appropriate environment variable
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        self.model_name = model_name
        self.provider_name = self._get_provider(model_name)
        self.provider_class = PROVIDER_REGISTRY[self.provider_name]
        self.api_key = api_key or self._get_api_key()
        
        if not self.api_key:
            raise ValueError(f"API key must be provided or set as {self.provider_class(None, None).get_env_var_name()} environment variable")
        
        self.provider = self.provider_class(model_name, self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _get_provider(self, model_name: str) -> str:
        """
        Determine the provider based on the model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Provider name ("anthropic", "openai", "gemini", or "groq")
        """
        if model_name.startswith(("claude")):
            return "anthropic"
        elif model_name.startswith(("gpt", "o")):
            return "openai"
        elif model_name.startswith("gemini"):
            return "gemini"
        elif model_name.startswith(("meta-llama", "llama")):
            return "groq"
        else:
            # Default to anthropic for backward compatibility
            return "anthropic"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get the API key from environment variables.
        
        Returns:
            API key if found, None otherwise
        """
        env_var_name = self.provider_class.get_env_var_name()
        return os.environ.get(env_var_name)
    
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
            f"There are {config.CHARS_PER_ROW} characters per row, and the font sizes are standardized. There is only capitalized and lower case English letters in the image. "
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
                response = self.provider.run_model_on_image(encoded_image, system_prompt, user_prompt)
                break
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise Exception(f"Failed after {self.max_retries} retries: {str(e)}")
                print(f"API call failed, retrying ({retries}/{self.max_retries}): {str(e)}")
                time.sleep(self.retry_delay)
        
        if not response:
            raise Exception("Failed to get a response from the API")
        
        # Parse the response text
        return self._parse_response(response, image_path)
    
    def _parse_response(self, response_text, image_path):
        """
        Extract and parse the response text to JSON.
        
        Args:
            response_text: Text response from the model
            image_path: Path to the image file (for error reporting)
            
        Returns:
            Parsed JSON as a list of dictionaries
        """
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
            results.append({
                "image_path": item['image_path'],
                "responses": response
            })
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
    
    parser.add_argument("--model", type=str, choices=config.AVAILABLE_MODELS,
                      default=os.getenv('DEFAULT_MODEL', 'claude-3-7-sonnet'),
                      help="Model name to evaluate")
    parser.add_argument("--dataset", type=str, default=os.getenv('DATASET_FILE', 'dataset.json'), 
                      help="Path to dataset file (default: dataset.json)")
    parser.add_argument("--output", type=str, default=None, 
                      help="Path to save model responses (default: model_name_responses.json)")
    parser.add_argument("--api-key", type=str, default=None, 
                      help="API key (default: uses appropriate environment variable)")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Set default output path if not provided
    if not args.output:
        args.output = f"{args.model}_responses.json"
    
    # Get the actual model ID from config
    model_id = config.MODELS[args.model]
    
    runner = ModelRunner(model_name=model_id, api_key=args.api_key)
    
    print(f"Running model {args.model} (API: {model_id}) on dataset {args.dataset}")
    responses = runner.run_on_dataset(args.dataset)
    
    runner.save_responses(responses, args.output)
    print(f"Saved responses to {args.output}")