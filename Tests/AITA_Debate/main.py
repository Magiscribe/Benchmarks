"""
AITA Debate - Lincoln-Douglas Style Debate Benchmark

Run structured debates on AITA scenarios with explicit role assignment.
"""

import argparse
import os
import sys
import json
import random
from pathlib import Path
from dotenv import load_dotenv

# Add the Inference directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Inference'))

from available_models import AVAILABLE_MODELS, MODELS
from model_runner import ModelRunner

# Load environment variables from .env file in root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

from utils.debate_manager import DebateManager
from utils.dataset_creator import DatasetCreator
from utils.debate_evaluator import DebateEvaluator
from test_config import (
    DEFAULT_PRO_MODEL, DEFAULT_CON_MODEL, DEFAULT_JUDGE_MODEL,
    NUM_SCENARIOS, DATASET_FILE, DEBATES_DIR, SCENARIOS_FILE
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="AITA Debate - Lincoln-Douglas Style Debate Benchmark"
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
    
    # Debate execution arguments
    parser.add_argument(
        "--run-debate",
        action="store_true",
        help="Run a debate on a specific scenario"
    )
    parser.add_argument(
        "--scenario-id",
        type=str,
        help="Scenario ID to run debate on (e.g., 'aita_001')"
    )
    
    # Model assignment - explicit role assignment
    parser.add_argument(
        "--pro-model",
        type=str,
        choices=AVAILABLE_MODELS,
        default=DEFAULT_PRO_MODEL,
        help=f"Model for PRO role (argues NTA). Default: {DEFAULT_PRO_MODEL}"
    )
    parser.add_argument(
        "--con-model",
        type=str,
        choices=AVAILABLE_MODELS,
        default=DEFAULT_CON_MODEL,
        help=f"Model for CON role (argues YTA). Default: {DEFAULT_CON_MODEL}"
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        choices=AVAILABLE_MODELS,
        default=DEFAULT_JUDGE_MODEL,
        help=f"Model for JUDGE role. Default: {DEFAULT_JUDGE_MODEL}"
    )
    
    # Random model selection
    parser.add_argument(
        "--random-models",
        action="store_true",
        help="Randomly select 3 models and assign to roles"
    )
    parser.add_argument(
        "--model-pool",
        type=str,
        nargs="+",
        choices=AVAILABLE_MODELS,
        help="Pool of models to randomly select from (requires --random-models)"
    )
    
    # Evaluation arguments
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate all existing debates and generate results CSV"
    )
    parser.add_argument(
        "--debates-dir",
        type=str,
        default=DEBATES_DIR,
        help=f"Directory containing debate logs (default: {DEBATES_DIR})"
    )
    
    # Batch processing
    parser.add_argument(
        "--run-all",
        action="store_true",
        help="Run debates for all scenarios in dataset"
    )
    
    return parser.parse_args()


def select_random_models(pool=None):
    """
    Randomly select 3 models and assign to PRO, CON, JUDGE roles.
    
    Args:
        pool: Optional list of models to select from. If None, uses all available.
        
    Returns:
        Tuple of (pro_model, con_model, judge_model)
    """
    if pool is None:
        pool = AVAILABLE_MODELS
    
    if len(pool) < 3:
        raise ValueError(f"Model pool must have at least 3 models, got {len(pool)}")
    
    selected = random.sample(pool, 3)
    return selected[0], selected[1], selected[2]


def print_dataset_summary(dataset):
    """Print a summary of the dataset."""
    print("\n" + "="*60)
    print("AITA DEBATE - DATASET SUMMARY")
    print("="*60)
    
    print(f"\nTotal scenarios: {len(dataset)}")
    
    print("\nScenarios:")
    for scenario in dataset:
        print(f"  {scenario['scenario_id']}: {scenario.get('title', scenario['scenario_id'])}")
    
    print("\n" + "="*60)


def main():
    args = parse_args()
    
    # Generate dataset if requested
    if args.generate:
        print("Generating AITA debate dataset...")
        creator = DatasetCreator(output_file=args.dataset)
        dataset = creator.create_dataset(num_scenarios=args.num_scenarios)
        print_dataset_summary(dataset)
        return
    
    # Evaluate if requested
    if args.evaluate:
        print("Evaluating debate results...")
        evaluator = DebateEvaluator(debates_dir=args.debates_dir)
        results = evaluator.evaluate_all_debates()
        evaluator.save_results_csv(results)
        return
    
    # Run debate(s)
    if args.run_debate or args.run_all:
        # Check if dataset exists
        if not os.path.exists(args.dataset):
            # Try to use scenarios.json if it exists
            if os.path.exists(SCENARIOS_FILE):
                args.dataset = SCENARIOS_FILE
            else:
                print(f"Error: Dataset file {args.dataset} does not exist.")
                print("Run with --generate first or provide scenarios.json")
                sys.exit(1)
        
        # Load dataset
        with open(args.dataset, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Determine model assignments
        if args.random_models:
            pro_model, con_model, judge_model = select_random_models(args.model_pool)
            print(f"\nRandomly assigned models:")
            print(f"  PRO:   {pro_model}")
            print(f"  CON:   {con_model}")
            print(f"  JUDGE: {judge_model}")
        else:
            pro_model = args.pro_model
            con_model = args.con_model
            judge_model = args.judge_model
        
        # Initialize model runner (we'll switch models as needed)
        model_runner = ModelRunner(model_name=pro_model)
        
        # Initialize debate manager
        manager = DebateManager(
            pro_model=pro_model,
            con_model=con_model,
            judge_model=judge_model,
            debates_dir=args.debates_dir
        )
        
        # Determine which scenarios to run
        if args.run_all:
            scenarios_to_run = dataset
            print(f"\nRunning debates for ALL {len(scenarios_to_run)} scenarios")
        else:
            if not args.scenario_id:
                print("Error: --scenario-id required when using --run-debate")
                print("Use --run-all to run all scenarios")
                sys.exit(1)
            
            # Find the specific scenario
            scenario = next(
                (s for s in dataset if s['scenario_id'] == args.scenario_id),
                None
            )
            if scenario is None:
                print(f"Error: Scenario {args.scenario_id} not found in dataset")
                print("Available scenarios:")
                for s in dataset:
                    print(f"  {s['scenario_id']}")
                sys.exit(1)
            
            scenarios_to_run = [scenario]
        
        # Run debates
        results = []
        for i, scenario in enumerate(scenarios_to_run):
            print(f"\n[{i+1}/{len(scenarios_to_run)}] Running debate for {scenario['scenario_id']}...")
            
            try:
                result = manager.run_full_debate(scenario, model_runner)
                results.append({
                    "scenario_id": scenario['scenario_id'],
                    "debate_id": result['debate_id'],
                    "decision": result['decision'],
                    "status": "success"
                })
            except Exception as e:
                print(f"Error running debate for {scenario['scenario_id']}: {e}")
                results.append({
                    "scenario_id": scenario['scenario_id'],
                    "status": "error",
                    "error": str(e)
                })
        
        # Print summary
        print("\n" + "="*60)
        print("DEBATE RUN SUMMARY")
        print("="*60)
        
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        print(f"\nSuccessful: {len(successful)}/{len(results)}")
        if successful:
            pro_wins = sum(1 for r in successful if r['decision'] == 'PRO')
            con_wins = sum(1 for r in successful if r['decision'] == 'CON')
            print(f"  PRO wins: {pro_wins}")
            print(f"  CON wins: {con_wins}")
        
        if failed:
            print(f"\nFailed: {len(failed)}")
            for r in failed:
                print(f"  {r['scenario_id']}: {r['error']}")
        
        print("\n" + "="*60)
        return
    
    # If no action specified, print help
    parser = argparse.ArgumentParser()
    parse_args()
    print("No action specified. Use --help for usage information.")


if __name__ == "__main__":
    main()
