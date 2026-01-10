import json
import os
from collections import defaultdict
from typing import List, Dict


class ConversationEvaluator:
    """Evaluates AITA conversation outcomes and model performance."""
    
    def __init__(self, conversations_dir: str = "conversations"):
        """
        Initialize the evaluator.
        
        Args:
            conversations_dir: Directory containing conversation log JSON files
        """
        self.conversations_dir = conversations_dir
    
    def load_conversation(self, conversation_path: str) -> Dict:
        """Load a conversation log from JSON file."""
        with open(conversation_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_winner(self, final_positions: Dict[str, str]) -> Dict[str, bool]:
        """
        Determine winner(s) based on final positions.
        
        A model wins if it's the ONLY one with its position.
        
        Args:
            final_positions: Dict mapping model names to final positions
            
        Returns:
            Dict mapping model names to winner status (True/False)
        """
        # Count how many models have each position
        position_counts = defaultdict(int)
        for position in final_positions.values():
            position_counts[position] += 1
        
        # A model wins if its position is unique (count == 1)
        winners = {}
        for model, position in final_positions.items():
            winners[model] = (position_counts[position] == 1)
        
        return winners
    
    def count_messages_sent(self, turns: List[Dict], model: str) -> int:
        """
        Count how many messages a specific model sent.
        
        Args:
            turns: List of conversation turns
            model: Model name
            
        Returns:
            Count of messages sent by this model
        """
        return sum(1 for turn in turns if turn['speaker'] == model)
    
    def evaluate_conversation(self, conversation: Dict) -> List[Dict]:
        """
        Evaluate a single conversation and return results for each model.
        
        Args:
            conversation: Conversation log dictionary
            
        Returns:
            List of result dictionaries, one per model
        """
        conversation_id = conversation['conversation_id']
        scenario_id = conversation['scenario_id']
        initial_positions = conversation['initial_positions']
        final_positions = conversation['final_positions']
        turns = conversation['turns']
        models = conversation['models']
        
        # Calculate winners
        winners = self.calculate_winner(final_positions)
        
        # Build results for each model
        results = []
        for model in models:
            result = {
                'model': model,
                'conversation_id': conversation_id,
                'scenario_id': scenario_id,
                'initial_answer': initial_positions[model],
                'final_answer': final_positions[model],
                'winner': 1 if winners[model] else 0,
                'messages_sent': self.count_messages_sent(turns, model)
            }
            results.append(result)
        
        return results
    
    def evaluate_all_conversations(self) -> List[Dict]:
        """
        Evaluate all conversations in the conversations directory.
        
        Returns:
            List of all evaluation results (flattened)
        """
        all_results = []
        
        # Find all conversation JSON files
        conversation_files = []
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                conversation_files.append(
                    os.path.join(self.conversations_dir, filename)
                )
        
        if not conversation_files:
            print(f"No conversation files found in {self.conversations_dir}")
            return []
        
        print(f"Found {len(conversation_files)} conversation(s) to evaluate")
        
        # Evaluate each conversation
        for conv_path in conversation_files:
            conversation = self.load_conversation(conv_path)
            results = self.evaluate_conversation(conversation)
            all_results.extend(results)
        
        return all_results
    
    def get_summary_stats(self, results: List[Dict]) -> Dict:
        """
        Calculate summary statistics across all results.
        
        Args:
            results: List of evaluation result dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {}
        
        # Group by model
        by_model = defaultdict(list)
        for result in results:
            by_model[result['model']].append(result)
        
        stats = {}
        for model, model_results in by_model.items():
            total = len(model_results)
            wins = sum(r['winner'] for r in model_results)
            position_changes = sum(
                1 for r in model_results 
                if r['initial_answer'] != r['final_answer']
            )
            total_messages = sum(r['messages_sent'] for r in model_results)
            
            stats[model] = {
                'total_conversations': total,
                'wins': wins,
                'win_rate': wins / total if total > 0 else 0,
                'position_changes': position_changes,
                'change_rate': position_changes / total if total > 0 else 0,
                'avg_messages_sent': total_messages / total if total > 0 else 0
            }
        
        return stats


if __name__ == "__main__":
    evaluator = ConversationEvaluator()
    print("ConversationEvaluator initialized and ready to use.")
    print("\nUsage:")
    print("  evaluator = ConversationEvaluator('conversations')")
    print("  results = evaluator.evaluate_all_conversations()")
    print("  stats = evaluator.get_summary_stats(results)")
