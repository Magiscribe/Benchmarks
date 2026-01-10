import json
import os
import random
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class ConversationManager:
    """Manages multi-agent conversations for AITA debates."""
    
    def __init__(
        self, 
        models: List[str], 
        max_turns: int = 15,
        conversations_dir: str = "conversations"
    ):
        """
        Initialize conversation manager.
        
        Args:
            models: List of 3 model names participating in the conversation
            max_turns: Maximum number of conversation turns
            conversations_dir: Directory to save conversation logs
        """
        if len(models) != 3:
            raise ValueError("Exactly 3 models required for conversation")
        
        self.models = models
        self.max_turns = max_turns
        self.conversations_dir = conversations_dir
        os.makedirs(conversations_dir, exist_ok=True)
        
    def generate_conversation_id(self, scenario_id: str) -> str:
        """Generate a unique conversation ID."""
        model_str = "_".join(sorted(self.models))
        return f"{scenario_id}_{model_str}"
    
    def select_next_speaker(
        self, 
        last_speaker: Optional[str],
        models: List[str]
    ) -> str:
        """
        Select the next speaker using conversational random mechanics.
        
        Rules:
        - First turn: random selection from all 3 models
        - Subsequent turns: random from 2 models who didn't just speak
        
        Args:
            last_speaker: The model who spoke last (None for first turn)
            models: List of all model names
            
        Returns:
            Selected model name
        """
        if last_speaker is None:
            # First turn: random selection
            return random.choice(models)
        else:
            # Subsequent turns: select from models who didn't just speak
            available = [m for m in models if m != last_speaker]
            return random.choice(available)
    
    def format_conversation_history(self, turns: List[Dict]) -> str:
        """
        Format conversation history for prompt context.
        
        Args:
            turns: List of turn dictionaries with 'speaker' and 'message'
            
        Returns:
            Formatted conversation history string
        """
        if not turns:
            return "No messages yet. You are starting the conversation."
        
        formatted = []
        for turn in turns:
            formatted.append(f"{turn['speaker']}: {turn['message']}")
        
        return "\n\n".join(formatted)
    
    def extract_json_from_response(self, response_text: str) -> Dict:
        """
        Extract JSON object from model response.
        
        Args:
            response_text: Raw response text from model
            
        Returns:
            Parsed JSON dictionary
        """
        # Try to find JSON in code blocks first
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            # Try to find JSON object directly
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
            else:
                json_str = response_text
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response text: {response_text[:200]}...")
            # Return a default structure
            return {"message": response_text, "position": "UNKNOWN"}
    
    def initialize_conversation(
        self,
        scenario: Dict,
        model_runner
    ) -> Dict[str, str]:
        """
        Get initial positions from all models.
        
        Args:
            scenario: Scenario dictionary with 'scenario_id', 'text', etc.
            model_runner: ModelRunner instance
            
        Returns:
            Dictionary mapping model names to initial positions (YTA/NTA)
        """
        initial_positions = {}
        
        # Load initial system message template
        system_msg_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "system_messages", 
            "initial.txt"
        )
        with open(system_msg_path, 'r', encoding='utf-8') as f:
            initial_template = f.read()
        
        for model in self.models:
            print(f"Getting initial position from {model}...")
            
            # Format the prompt with scenario
            prompt = initial_template.format(scenario_text=scenario['text'])
            
            # Get response from model
            response = model_runner.run_conversation_turn(
                model=model,
                system_prompt=prompt
            )
            
            # Parse response
            parsed = self.extract_json_from_response(response)
            position = parsed.get("position", "NTA")
            
            initial_positions[model] = position
            print(f"  → {model}: {position}")
        
        return initial_positions
    
    def run_conversation(
        self,
        scenario: Dict,
        initial_positions: Dict[str, str],
        model_runner
    ) -> List[Dict]:
        """
        Execute the conversation between models.
        
        Args:
            scenario: Scenario dictionary
            initial_positions: Initial position assignments for each model
            model_runner: ModelRunner instance
            
        Returns:
            List of conversation turns
        """
        turns = []
        last_speaker = None
        
        # Load response system message template
        system_msg_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "system_messages", 
            "response.txt"
        )
        with open(system_msg_path, 'r', encoding='utf-8') as f:
            response_template = f.read()
        
        for turn_num in range(self.max_turns):
            # Select next speaker
            speaker = self.select_next_speaker(last_speaker, self.models)
            
            # Format conversation history
            history_str = self.format_conversation_history(turns)
            
            # Format prompt
            prompt = response_template.format(
                scenario_text=scenario['text'],
                conversation_history=history_str
            )
            
            print(f"Turn {turn_num + 1}/{self.max_turns}: {speaker} speaking...")
            
            # Get response
            response = model_runner.run_conversation_turn(
                model=speaker,
                system_prompt=prompt
            )
            
            # Parse response
            parsed = self.extract_json_from_response(response)
            message = parsed.get("message", response)
            current_position = parsed.get("current_position", "UNKNOWN")
            
            # Record turn with timestamp
            turn = {
                "speaker": speaker,
                "message": message,
                "current_position": current_position,
                "timestamp": datetime.now().isoformat()
            }
            turns.append(turn)
            
            last_speaker = speaker
        
        return turns
    
    def get_final_positions(
        self,
        scenario: Dict,
        turns: List[Dict],
        model_runner
    ) -> Dict[str, str]:
        """
        Get final positions from all models after conversation.
        
        Args:
            scenario: Scenario dictionary
            turns: List of conversation turns
            model_runner: ModelRunner instance
            
        Returns:
            Dictionary mapping model names to final positions
        """
        final_positions = {}
        
        # Load final system message template
        system_msg_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "system_messages", 
            "final.txt"
        )
        with open(system_msg_path, 'r', encoding='utf-8') as f:
            final_template = f.read()
        
        # Format conversation history
        history_str = self.format_conversation_history(turns)
        
        for model in self.models:
            print(f"Getting final position from {model}...")
            
            # Format prompt
            prompt = final_template.format(
                scenario_text=scenario['text'],
                conversation_history=history_str
            )
            
            # Get response
            response = model_runner.run_conversation_turn(
                model=model,
                system_prompt=prompt
            )
            
            # Parse response
            parsed = self.extract_json_from_response(response)
            position = parsed.get("final_position", parsed.get("position", "NTA"))
            
            final_positions[model] = position
            print(f"  → {model}: {position}")
        
        return final_positions
    
    def save_conversation_log(
        self,
        scenario: Dict,
        initial_positions: Dict[str, str],
        turns: List[Dict],
        final_positions: Dict[str, str]
    ) -> str:
        """
        Save complete conversation log to JSON file.
        
        Args:
            scenario: Scenario dictionary
            initial_positions: Initial positions for each model
            turns: List of conversation turns
            final_positions: Final positions for each model
            
        Returns:
            Path to saved conversation log
        """
        conversation_id = self.generate_conversation_id(scenario['scenario_id'])
        
        log = {
            "conversation_id": conversation_id,
            "scenario_id": scenario['scenario_id'],
            "scenario_text": scenario['text'],
            "models": self.models,
            "initial_positions": initial_positions,
            "turns": turns,
            "final_positions": final_positions,
            "started_at": turns[0]["timestamp"] if turns else None,
            "completed_at": datetime.now().isoformat()
        }
        
        output_path = os.path.join(
            self.conversations_dir, 
            f"{conversation_id}.json"
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        
        print(f"Conversation log saved to {output_path}")
        return output_path
    
    def run_full_conversation(
        self,
        scenario: Dict,
        model_runner
    ) -> Dict:
        """
        Run a complete conversation: initial → turns → final.
        
        Args:
            scenario: Scenario dictionary
            model_runner: ModelRunner instance
            
        Returns:
            Complete conversation log dictionary
        """
        print(f"\n{'='*60}")
        print(f"Starting conversation for scenario: {scenario['scenario_id']}")
        print(f"Models: {', '.join(self.models)}")
        print(f"{'='*60}\n")
        
        # Step 1: Get initial positions
        print("PHASE 1: Getting initial positions...")
        initial_positions = self.initialize_conversation(scenario, model_runner)
        
        # Step 2: Run conversation
        print("\nPHASE 2: Running conversation...")
        turns = self.run_conversation(scenario, initial_positions, model_runner)
        
        # Step 3: Get final positions
        print("\nPHASE 3: Getting final positions...")
        final_positions = self.get_final_positions(scenario, turns, model_runner)
        
        # Step 4: Save log
        print("\nPHASE 4: Saving conversation log...")
        self.save_conversation_log(scenario, initial_positions, turns, final_positions)
        
        print(f"\n{'='*60}")
        print("Conversation complete!")
        print(f"Initial: {initial_positions}")
        print(f"Final:   {final_positions}")
        print(f"{'='*60}\n")
        
        return {
            "conversation_id": self.generate_conversation_id(scenario['scenario_id']),
            "scenario_id": scenario['scenario_id'],
            "initial_positions": initial_positions,
            "final_positions": final_positions,
            "total_turns": len(turns)
        }


if __name__ == "__main__":
    print("ConversationManager initialized and ready to use.")
    print("\nUsage:")
    print("  manager = ConversationManager(['model1', 'model2', 'model3'])")
    print("  result = manager.run_full_conversation(scenario, model_runner)")
