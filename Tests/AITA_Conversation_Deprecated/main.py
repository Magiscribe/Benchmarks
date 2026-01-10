import argparse
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the Inference directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Inference'))

# Import shared model configuration from Inference
from available_models import AVAILABLE_MODELS, MODELS
from model_runner import ModelRunner

# Load environment variables from .env file in root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

from utils.dataset_creator import DatasetCreator
from utils.conversation_manager import ConversationManager
from utils.model_evaluator import ConversationEvaluator
from test_config import (
    MAX_TURNS, MODELS_PER_CONVERSATION, DEFAULT_MODELS, 
    NUM_SCENARIOS, DATASET_FILE, CONVERSATIONS_DIR, RESPONSES_DIR
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="AITA Conversation Test - Multi-agent debate benchmark"
    )
    
    # Dataset generation arguments
    parser.add_argument(
        "--generate", 
        action="store_true", 
        help="Generate new dataset with placeholder scenarios"
    )
    parser.add_argument(
        "--num-scenarios", 
        type=int, 
        default=NUM_SCENARIOS,
        help=f"Number of scenarios to generate (default: {NUM_SCENARIOS})"
    )
    parser.add_argument(
        "--dataset", 
        type=str, 
        default=DATASET_FILE,
        help=f"Path to dataset file (default: {DATASET_FILE})"
    )
    
    # Conversation execution arguments
    parser.add_argument(
        "--run-conversation",
        action="store_true",
        help="Run a conversation on a specific scenario"
    )
    parser.add_argument(
        "--scenario-id",
        type=str,
        help="Scenario ID to run conversation on (e.g., 'aita_001')"
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs=3,
        choices=AVAILABLE_MODELS,
        default=DEFAULT_MODELS,
        help=f"Three models to participate in conversation (default: {' '.join(DEFAULT_MODELS)})"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=MAX_TURNS,
        help=f"Maximum conversation turns (default: {MAX_TURNS})"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for models (if not in environment)"
    )
    
    # Evaluation arguments
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate all existing conversations and generate results CSV"
    )
    parser.add_argument(
        "--conversations-dir",
        type=str,
        default=CONVERSATIONS_DIR,
        help=f"Directory containing conversation logs (default: {CONVERSATIONS_DIR})"
    )
    
    # Batch processing
    parser.add_argument(
        "--run-all",
        action="store_true",
        help="Run conversations for all scenarios in dataset with specified models"
    )
    
    return parser.parse_args()


def print_dataset_summary(dataset):
    """Print a summary of the dataset."""
    print("\n" + "="*60)
    print("AITA CONVERSATION TEST - DATASET SUMMARY")
    print("="*60)
    
    print(f"\nTotal scenarios: {len(dataset)}")
    
    print("\nScenarios:")
    for scenario in dataset:
        print(f"  {scenario['scenario_id']}: {scenario['title']}")
    
    print("\n" + "="*60)


def main():
    args = parse_args()
    
    # Generate dataset if requested
    if args.generate:
        print("Generating AITA conversation dataset...")
        creator = DatasetCreator(output_file=args.dataset)
        dataset = creator.create_dataset(num_scenarios=args.num_scenarios)
        print_dataset_summary(dataset)
        return
    
    # Run conversation if requested
    if args.run_conversation or args.run_all:
        # Check if dataset exists
        if not os.path.exists(args.dataset):
            print(f"Error: Dataset file {args.dataset} does not exist.")
            print("Run with --generate first to create a dataset.")
            sys.exit(1)
        
        # Load dataset
        with open(args.dataset, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Determine which scenarios to run
        if args.run_all:
            scenarios_to_run = dataset
            print(f"\nRunning conversations for ALL {len(scenarios_to_run)} scenarios")
        else:
            if not args.scenario_id:
                print("Error: --scenario-id required when using --run-conversation")
                sys.exit(1)
            
            # Find the specific scenario
            scenario = next(
                (s for s in dataset if s['scenario_id'] == args.scenario_id), 
                None
            )
            if not scenario:
                print(f"Error: Scenario '{args.scenario_id}' not found in dataset")
                sys.exit(1)
            
            scenarios_to_run = [scenario]
        
        # Get model IDs
        model_ids = [MODELS[m] for m in args.models]
        print(f"\nModels: {', '.join(args.models)}")
        print(f"Max turns: {args.max_turns}")
        
        # Create model runner (we'll swap models as needed)
        model_runner = ModelRunner(
            model_name=model_ids[0],
            api_key=args.api_key,
            system_messages_dir=os.path.join(os.path.dirname(__file__), "system_messages")
        )
        
        # Create conversation manager
        manager = ConversationManager(
            models=args.models,
            max_turns=args.max_turns,
            conversations_dir=args.conversations_dir
        )
        
        # Run conversations
        for scenario in scenarios_to_run:
            try:
                result = manager.run_full_conversation(scenario, model_runner)
                print(f"✓ Completed: {scenario['scenario_id']}")
            except Exception as e:
                print(f"✗ Failed: {scenario['scenario_id']}")
                print(f"  Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("All conversations completed!")
        print("="*60)
    
    # Evaluate conversations if requested
    if args.evaluate:
        print("\nEvaluating conversations...")
        from utils.synthesize_model_results import synthesize_results
        
        try:
            synthesize_results(
                conversations_dir=args.conversations_dir
            )
        except Exception as e:
            print(f"Error during evaluation: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
