"""
DebateEvaluator - Evaluates debate outcomes and generates results.
"""

import json
import os
import csv
from typing import List, Dict
from pathlib import Path


class DebateEvaluator:
    """Evaluates AITA debate outcomes."""
    
    def __init__(self, debates_dir: str = "debates"):
        """
        Initialize the evaluator.
        
        Args:
            debates_dir: Directory containing debate log JSON files
        """
        self.debates_dir = debates_dir
    
    def load_debate(self, debate_path: str) -> Dict:
        """Load a debate log from JSON file."""
        with open(debate_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_debate(self, debate: Dict) -> List[Dict]:
        """
        Evaluate a single debate and return results for each model.
        
        Args:
            debate: Debate log dictionary
            
        Returns:
            List of result dictionaries, one per model/role (3 rows per debate)
        """
        debate_id = debate['debate_id']
        scenario_id = debate['scenario_id']
        models = debate['models']
        decision = debate.get('decision', 'UNKNOWN')
        token_usage = debate.get('token_usage', {})
        
        results = []
        
        # PRO model result
        pro_model = models['pro']
        pro_won = 1 if decision == 'PRO' else 0
        results.append({
            'model': pro_model,
            'role': 'PRO',
            'debate_id': debate_id,
            'scenario_id': scenario_id,
            'decision': decision,
            'won': pro_won,
            'token_usage': token_usage.get(pro_model, 0)
        })
        
        # CON model result
        con_model = models['con']
        con_won = 1 if decision == 'CON' else 0
        results.append({
            'model': con_model,
            'role': 'CON',
            'debate_id': debate_id,
            'scenario_id': scenario_id,
            'decision': decision,
            'won': con_won,
            'token_usage': token_usage.get(con_model, 0)
        })
        
        # JUDGE model result
        judge_model = models['judge']
        results.append({
            'model': judge_model,
            'role': 'JUDGE',
            'debate_id': debate_id,
            'scenario_id': scenario_id,
            'decision': decision,
            'won': None,
            'token_usage': token_usage.get(judge_model, 0)
        })
        
        return results
    
    def evaluate_all_debates(self) -> List[Dict]:
        """
        Evaluate all debates in the debates directory.
        
        Returns:
            List of all result dictionaries
        """
        all_results = []
        
        if not os.path.exists(self.debates_dir):
            print(f"Debates directory {self.debates_dir} does not exist")
            return all_results
        
        debate_files = list(Path(self.debates_dir).glob("*.json"))
        
        if not debate_files:
            print(f"No debate files found in {self.debates_dir}")
            return all_results
        
        print(f"Evaluating {len(debate_files)} debate(s)...")
        
        for debate_path in debate_files:
            try:
                debate = self.load_debate(str(debate_path))
                results = self.evaluate_debate(debate)
                all_results.extend(results)
            except Exception as e:
                print(f"Error evaluating {debate_path}: {e}")
        
        return all_results
    
    def save_results_csv(
        self, 
        results: List[Dict], 
        output_path: str = None
    ) -> str:
        """
        Save results to CSV file.
        
        Args:
            results: List of result dictionaries
            output_path: Path for output CSV. If None, uses default.
            
        Returns:
            Path to saved CSV file
        """
        if output_path is None:
            # Save to Results directory at project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            results_dir = os.path.join(project_root, "Results")
            os.makedirs(results_dir, exist_ok=True)
            output_path = os.path.join(results_dir, "AITA_Debate_model_results.csv")
        
        if not results:
            print("No results to save")
            return output_path
        
        # Define column order to match csv_format.json
        fieldnames = ['model', 'role', 'debate_id', 'scenario_id', 'decision', 'won', 'token_usage']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Results saved to {output_path}")
        return output_path
    
    def print_summary(self, results: List[Dict]):
        """Print a summary of debate results."""
        if not results:
            print("No results to summarize")
            return
        
        # Filter to just debater results (not judge entries)
        debater_results = [r for r in results if r['role'] in ['PRO', 'CON']]
        
        # Count wins by model
        model_wins = {}
        model_debates = {}
        model_tokens = {}
        
        for result in debater_results:
            model = result['model']
            won = result.get('won', 0) or 0
            tokens = result.get('token_usage', 0) or 0
            
            if model not in model_wins:
                model_wins[model] = 0
                model_debates[model] = 0
                model_tokens[model] = 0
            
            model_wins[model] += won
            model_debates[model] += 1
            model_tokens[model] += tokens
        
        print("\n" + "="*60)
        print("DEBATE RESULTS SUMMARY")
        print("="*60)
        
        print("\nWins by Model:")
        for model in sorted(model_wins.keys()):
            wins = model_wins[model]
            debates = model_debates[model]
            tokens = model_tokens[model]
            win_rate = (wins / debates * 100) if debates > 0 else 0
            print(f"  {model}: {wins}/{debates} ({win_rate:.1f}%) - {tokens:,} tokens")
        
        # Count wins by role
        pro_wins = sum(1 for r in debater_results if r['role'] == 'PRO' and r.get('won') == 1)
        con_wins = sum(1 for r in debater_results if r['role'] == 'CON' and r.get('won') == 1)
        total = len(debater_results) // 2  # Each debate has 2 debaters
        
        print(f"\nWins by Role:")
        print(f"  PRO (NTA): {pro_wins}/{total}")
        print(f"  CON (YTA): {con_wins}/{total}")
        
        # Total token usage
        total_tokens = sum(r.get('token_usage', 0) or 0 for r in results)
        print(f"\nTotal Token Usage: {total_tokens:,}")
        
        print("="*60)


if __name__ == "__main__":
    evaluator = DebateEvaluator()
    results = evaluator.evaluate_all_debates()
    evaluator.print_summary(results)
    if results:
        evaluator.save_results_csv(results)
