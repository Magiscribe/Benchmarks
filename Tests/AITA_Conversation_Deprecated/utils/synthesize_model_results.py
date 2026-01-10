import csv
import os
from pathlib import Path
from dotenv import load_dotenv
from model_evaluator import ConversationEvaluator

# Load environment variables from .env file in root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)


def synthesize_results(conversations_dir: str = None, output_file: str = None):
    """
    Synthesize conversation results into a centralized CSV file.
    
    Args:
        conversations_dir: Directory containing conversation JSON files
        output_file: Path to output CSV file
    """
    # Default paths
    if conversations_dir is None:
        test_dir = os.path.dirname(os.path.dirname(__file__))
        conversations_dir = os.path.join(test_dir, "conversations")
    
    if output_file is None:
        # Export to centralized Results folder
        results_dir = os.path.join('..', '..', '..', 'Results')
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, 'AITA_Conversation_model_results.csv')
    
    print(f"Synthesizing results from {conversations_dir}")
    
    # Evaluate all conversations
    evaluator = ConversationEvaluator(conversations_dir)
    results = evaluator.evaluate_all_conversations()
    
    if not results:
        print("No results to synthesize!")
        return
    
    # Write to CSV
    headers = [
        "model",
        "conversation_id", 
        "scenario_id",
        "initial_answer",
        "final_answer",
        "winner",
        "messages_sent"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults written to {output_file}")
    print(f"Total rows: {len(results)}")
    
    # Print summary stats
    stats = evaluator.get_summary_stats(results)
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    for model, model_stats in stats.items():
        print(f"\n{model}:")
        print(f"  Conversations: {model_stats['total_conversations']}")
        print(f"  Wins: {model_stats['wins']} ({model_stats['win_rate']:.1%})")
        print(f"  Position changes: {model_stats['position_changes']} ({model_stats['change_rate']:.1%})")
        print(f"  Avg messages sent: {model_stats['avg_messages_sent']:.1f}")


def main():
    """Main function to run synthesis."""
    synthesize_results()


if __name__ == "__main__":
    main()
