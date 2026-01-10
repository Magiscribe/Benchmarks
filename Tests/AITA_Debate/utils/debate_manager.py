"""
DebateManager - Orchestrates Lincoln-Douglas style debates between LLMs.
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add Inference to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'Inference'))

from available_models import MODELS

# Import test config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from test_config import (
    DebateRole, DebatePhase, DEBATE_PHASE_ORDER,
    JUDGE_OBSERVATION_PHASES, CROSS_EXAM_MIN_QUESTIONS, CROSS_EXAM_MAX_QUESTIONS,
    PRO_POSITION, CON_POSITION
)


class DebateManager:
    """Manages the execution of a structured Lincoln-Douglas debate."""
    
    def __init__(
        self,
        pro_model: str,
        con_model: str,
        judge_model: str,
        debates_dir: str = "debates",
        system_messages_dir: str = None
    ):
        """
        Initialize the debate manager.
        
        Args:
            pro_model: Model name for PRO role (argues NTA)
            con_model: Model name for CON role (argues YTA)
            judge_model: Model name for JUDGE role
            debates_dir: Directory to save debate logs
            system_messages_dir: Directory containing system message templates
        """
        self.models = {
            DebateRole.PRO: pro_model,
            DebateRole.CON: con_model,
            DebateRole.JUDGE: judge_model,
        }
        self.debates_dir = debates_dir
        
        # Set system messages directory
        if system_messages_dir is None:
            self.system_messages_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "system_messages"
            )
        else:
            self.system_messages_dir = system_messages_dir
        
        # Ensure debates directory exists
        os.makedirs(self.debates_dir, exist_ok=True)
        
        # Token usage tracking per model
        self.token_usage = {
            pro_model: 0,
            con_model: 0,
            judge_model: 0,
        }
    
    def _load_system_message(self, filename: str) -> str:
        """Load a system message template from file."""
        filepath = os.path.join(self.system_messages_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def _format_debate_history(self, phases: List[Dict]) -> str:
        """Format the debate history for inclusion in prompts."""
        if not phases:
            return "(No debate history yet)"
        
        history_parts = []
        for phase in phases:
            phase_name = phase['phase_name'].upper().replace('_', ' ')
            history_parts.append(f"\n=== {phase_name} ===")
            
            for msg in phase.get('messages', []):
                role = msg['role']
                msg_type = msg.get('type', 'statement')
                content = msg['content']
                
                if msg_type == 'question':
                    history_parts.append(f"\n[{role} QUESTION]: {content}")
                elif msg_type == 'answer':
                    history_parts.append(f"\n[{role} ANSWER]: {content}")
                else:
                    history_parts.append(f"\n[{role}]: {content}")
        
        return "\n".join(history_parts)
    
    def _format_judge_observations(self, scratchpad: Dict) -> str:
        """Format judge observations for the final verdict."""
        if not scratchpad:
            return "(No observations recorded)"
        
        parts = []
        for key, value in scratchpad.items():
            if key not in ('final_contemplation', 'decision'):
                phase_name = key.split('_', 1)[1] if '_' in key else key
                parts.append(f"After {phase_name}: {value}")
        
        return "\n".join(parts)
    
    def _parse_json_response(self, response: str) -> Dict:
        """Extract and parse JSON from model response."""
        # Try to find JSON in the response
        try:
            # Look for JSON block
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback: return the raw response as content
        return {"content": response}
    
    def _run_model(
        self, 
        model_runner, 
        model_name: str, 
        prompt: str
    ) -> Tuple[str, int]:
        """
        Run a model and return response with token count estimate.
        
        Returns:
            Tuple of (response_text, estimated_tokens)
        """
        response = model_runner.run_conversation_turn(model_name, prompt)
        
        # Estimate tokens (rough approximation: ~4 chars per token)
        prompt_tokens = len(prompt) // 4
        response_tokens = len(response) // 4
        total_tokens = prompt_tokens + response_tokens
        
        # Track usage
        if model_name in self.token_usage:
            self.token_usage[model_name] += total_tokens
        else:
            # Map to original model name if needed
            for orig_name, usage_model in self.models.items():
                if MODELS.get(usage_model, usage_model) == model_name:
                    self.token_usage[usage_model] += total_tokens
                    break
        
        return response, total_tokens
    
    def _run_opening(
        self,
        model_runner,
        role: DebateRole,
        scenario_text: str,
        debate_history: str
    ) -> Dict:
        """Run an opening constructive statement."""
        model_name = self.models[role]
        
        if role == DebateRole.PRO:
            template = self._load_system_message("pro_opening.txt")
        else:
            template = self._load_system_message("con_opening.txt")
        
        prompt = template.format(
            scenario_text=scenario_text,
            debate_history=debate_history
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        return {
            "role": role.value,
            "model": model_name,
            "type": "statement",
            "content": parsed.get("statement", parsed.get("content", response)),
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens
        }
    
    def _run_cross_exam_question(
        self,
        model_runner,
        questioner_role: DebateRole,
        answerer_role: DebateRole,
        scenario_text: str,
        debate_history: str
    ) -> Dict:
        """Run a cross-examination question."""
        model_name = self.models[questioner_role]
        
        template = self._load_system_message("cross_exam_question.txt")
        
        questioner_position = PRO_POSITION if questioner_role == DebateRole.PRO else CON_POSITION
        answerer_position = CON_POSITION if questioner_role == DebateRole.PRO else PRO_POSITION
        
        prompt = template.format(
            questioner_role=questioner_role.value,
            questioner_position=questioner_position,
            answerer_role=answerer_role.value,
            answerer_position=answerer_position,
            scenario_text=scenario_text,
            debate_history=debate_history
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        return {
            "role": questioner_role.value,
            "model": model_name,
            "type": "question",
            "content": parsed.get("question", parsed.get("content", response)),
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens
        }
    
    def _run_cross_exam_answer(
        self,
        model_runner,
        answerer_role: DebateRole,
        questioner_role: DebateRole,
        question: str,
        scenario_text: str,
        debate_history: str
    ) -> Dict:
        """Run a cross-examination answer."""
        model_name = self.models[answerer_role]
        
        template = self._load_system_message("cross_exam_answer.txt")
        
        answerer_position = PRO_POSITION if answerer_role == DebateRole.PRO else CON_POSITION
        questioner_position = CON_POSITION if answerer_role == DebateRole.PRO else PRO_POSITION
        
        prompt = template.format(
            answerer_role=answerer_role.value,
            answerer_position=answerer_position,
            questioner_role=questioner_role.value,
            questioner_position=questioner_position,
            question=question,
            scenario_text=scenario_text,
            debate_history=debate_history
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        return {
            "role": answerer_role.value,
            "model": model_name,
            "type": "answer",
            "content": parsed.get("answer", parsed.get("content", response)),
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens
        }
    
    def _run_rebuttal(
        self,
        model_runner,
        role: DebateRole,
        scenario_text: str,
        debate_history: str
    ) -> Dict:
        """Run a rebuttal statement."""
        model_name = self.models[role]
        
        template = self._load_system_message("rebuttal.txt")
        position = PRO_POSITION if role == DebateRole.PRO else CON_POSITION
        
        prompt = template.format(
            role=role.value,
            position=position,
            scenario_text=scenario_text,
            debate_history=debate_history
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        return {
            "role": role.value,
            "model": model_name,
            "type": "statement",
            "content": parsed.get("statement", parsed.get("content", response)),
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens
        }
    
    def _run_closing(
        self,
        model_runner,
        role: DebateRole,
        scenario_text: str,
        debate_history: str
    ) -> Dict:
        """Run a closing statement."""
        model_name = self.models[role]
        
        template = self._load_system_message("closing.txt")
        position = PRO_POSITION if role == DebateRole.PRO else CON_POSITION
        
        prompt = template.format(
            role=role.value,
            position=position,
            scenario_text=scenario_text,
            debate_history=debate_history
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        return {
            "role": role.value,
            "model": model_name,
            "type": "statement",
            "content": parsed.get("statement", parsed.get("content", response)),
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens
        }
    
    def _run_judge_observation(
        self,
        model_runner,
        phase_name: str,
        scenario_text: str,
        debate_history: str
    ) -> str:
        """Run a judge observation after a debate phase."""
        model_name = self.models[DebateRole.JUDGE]
        
        template = self._load_system_message("judge_observation.txt")
        
        prompt = template.format(
            phase_name=phase_name.replace('_', ' ').upper(),
            scenario_text=scenario_text,
            debate_history=debate_history
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        return parsed.get("observation", parsed.get("content", response))
    
    def _run_judge_verdict(
        self,
        model_runner,
        scenario_text: str,
        debate_history: str,
        judge_observations: str
    ) -> Tuple[str, str]:
        """
        Run the judge's final verdict.
        
        Returns:
            Tuple of (final_contemplation, decision)
        """
        model_name = self.models[DebateRole.JUDGE]
        
        template = self._load_system_message("judge_verdict.txt")
        
        prompt = template.format(
            scenario_text=scenario_text,
            debate_history=debate_history,
            judge_observations=judge_observations
        )
        
        response, tokens = self._run_model(model_runner, model_name, prompt)
        parsed = self._parse_json_response(response)
        
        decision = parsed.get("decision", "PRO")
        # Normalize decision
        if decision.upper() in ["PRO", "NTA", "NOT THE ASSHOLE"]:
            decision = "PRO"
        elif decision.upper() in ["CON", "YTA", "YOU'RE THE ASSHOLE", "YOURE THE ASSHOLE"]:
            decision = "CON"
        
        return (
            parsed.get("final_contemplation", parsed.get("content", response)),
            decision
        )
    
    def run_full_debate(self, scenario: Dict, model_runner) -> Dict:
        """
        Run a complete Lincoln-Douglas debate on a scenario.
        
        Args:
            scenario: Scenario dict with 'scenario_id' and 'text' keys
            model_runner: ModelRunner instance for API calls
            
        Returns:
            Complete debate log dictionary
        """
        scenario_id = scenario['scenario_id']
        scenario_text = scenario.get('text', scenario.get('scenario_text', ''))
        
        # Generate debate ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pro_model = self.models[DebateRole.PRO]
        con_model = self.models[DebateRole.CON]
        judge_model = self.models[DebateRole.JUDGE]
        debate_id = f"{scenario_id}_{pro_model}_{con_model}_{judge_model}_{timestamp}"
        
        print(f"\n{'='*60}")
        print(f"STARTING DEBATE: {debate_id}")
        print(f"PRO (NTA): {pro_model}")
        print(f"CON (YTA): {con_model}")
        print(f"JUDGE: {judge_model}")
        print(f"{'='*60}")
        
        # Initialize debate log
        debate_log = {
            "debate_id": debate_id,
            "scenario_id": scenario_id,
            "scenario_text": scenario_text,
            "models": {
                "pro": pro_model,
                "con": con_model,
                "judge": judge_model
            },
            "phases": [],
            "judge_scratchpad": {},
            "token_usage": {},
            "started_at": datetime.now().isoformat()
        }
        
        # Reset token tracking
        self.token_usage = {
            pro_model: 0,
            con_model: 0,
            judge_model: 0,
        }
        
        # Run each phase
        for phase_idx, phase in enumerate(DEBATE_PHASE_ORDER):
            phase_name = phase.phase_name
            print(f"\n[Phase {phase_idx + 1}/{len(DEBATE_PHASE_ORDER)}] {phase_name.upper()}")
            
            phase_data = {
                "phase_name": phase_name,
                "messages": []
            }
            
            debate_history = self._format_debate_history(debate_log["phases"])
            
            if phase == DebatePhase.PRO_OPENING:
                phase_data["phase_type"] = "opening"
                msg = self._run_opening(model_runner, DebateRole.PRO, scenario_text, debate_history)
                phase_data["messages"].append({"id": "1", **msg})
                
            elif phase == DebatePhase.CON_OPENING:
                phase_data["phase_type"] = "opening"
                msg = self._run_opening(model_runner, DebateRole.CON, scenario_text, debate_history)
                phase_data["messages"].append({"id": "1", **msg})
                
            elif phase == DebatePhase.CON_CROSS_EXAM:
                phase_data["phase_type"] = "cross_examination"
                phase_data["questioner"] = "CON"
                phase_data["answerer"] = "PRO"
                num_exchanges = random.randint(CROSS_EXAM_MIN_QUESTIONS, CROSS_EXAM_MAX_QUESTIONS)
                phase_data["num_exchanges"] = num_exchanges
                
                for i in range(num_exchanges):
                    # CON asks, PRO answers
                    q_msg = self._run_cross_exam_question(
                        model_runner, DebateRole.CON, DebateRole.PRO,
                        scenario_text, self._format_debate_history(debate_log["phases"] + [phase_data])
                    )
                    phase_data["messages"].append({"id": f"{i+1}.1", **q_msg})
                    
                    a_msg = self._run_cross_exam_answer(
                        model_runner, DebateRole.PRO, DebateRole.CON,
                        q_msg["content"], scenario_text,
                        self._format_debate_history(debate_log["phases"] + [phase_data])
                    )
                    phase_data["messages"].append({"id": f"{i+1}.2", **a_msg})
                    
            elif phase == DebatePhase.PRO_CROSS_EXAM:
                phase_data["phase_type"] = "cross_examination"
                phase_data["questioner"] = "PRO"
                phase_data["answerer"] = "CON"
                num_exchanges = random.randint(CROSS_EXAM_MIN_QUESTIONS, CROSS_EXAM_MAX_QUESTIONS)
                phase_data["num_exchanges"] = num_exchanges
                
                for i in range(num_exchanges):
                    # PRO asks, CON answers
                    q_msg = self._run_cross_exam_question(
                        model_runner, DebateRole.PRO, DebateRole.CON,
                        scenario_text, self._format_debate_history(debate_log["phases"] + [phase_data])
                    )
                    phase_data["messages"].append({"id": f"{i+1}.1", **q_msg})
                    
                    a_msg = self._run_cross_exam_answer(
                        model_runner, DebateRole.CON, DebateRole.PRO,
                        q_msg["content"], scenario_text,
                        self._format_debate_history(debate_log["phases"] + [phase_data])
                    )
                    phase_data["messages"].append({"id": f"{i+1}.2", **a_msg})
                    
            elif phase == DebatePhase.PRO_REBUTTAL:
                phase_data["phase_type"] = "rebuttal"
                msg = self._run_rebuttal(model_runner, DebateRole.PRO, scenario_text, debate_history)
                phase_data["messages"].append({"id": "1", **msg})
                
            elif phase == DebatePhase.CON_REBUTTAL:
                phase_data["phase_type"] = "rebuttal"
                msg = self._run_rebuttal(model_runner, DebateRole.CON, scenario_text, debate_history)
                phase_data["messages"].append({"id": "1", **msg})
                
            elif phase == DebatePhase.PRO_CLOSING:
                phase_data["phase_type"] = "closing"
                msg = self._run_closing(model_runner, DebateRole.PRO, scenario_text, debate_history)
                phase_data["messages"].append({"id": "1", **msg})
                
            elif phase == DebatePhase.CON_CLOSING:
                phase_data["phase_type"] = "closing"
                msg = self._run_closing(model_runner, DebateRole.CON, scenario_text, debate_history)
                phase_data["messages"].append({"id": "1", **msg})
                
            elif phase == DebatePhase.JUDGE_VERDICT:
                phase_data["phase_type"] = "verdict"
                # Get final verdict
                judge_obs_text = self._format_judge_observations(debate_log["judge_scratchpad"])
                final_debate_history = self._format_debate_history(debate_log["phases"])
                
                contemplation, decision = self._run_judge_verdict(
                    model_runner, scenario_text, final_debate_history, judge_obs_text
                )
                
                debate_log["judge_scratchpad"]["final_contemplation"] = contemplation
                debate_log["judge_scratchpad"]["decision"] = decision
                debate_log["decision"] = decision
                
                print(f"\n*** VERDICT: {decision} ***")
            
            # Add phase to log
            debate_log["phases"].append(phase_data)
            
            # Judge observes (except during verdict phase)
            if phase in JUDGE_OBSERVATION_PHASES:
                updated_history = self._format_debate_history(debate_log["phases"])
                observation = self._run_judge_observation(
                    model_runner, phase_name, scenario_text, updated_history
                )
                debate_log["judge_scratchpad"][f"{phase_idx}_{phase_name}"] = observation
        
        # Record final token usage
        debate_log["token_usage"] = dict(self.token_usage)
        debate_log["completed_at"] = datetime.now().isoformat()
        
        # Save debate log
        output_path = os.path.join(self.debates_dir, f"{debate_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(debate_log, f, indent=2, ensure_ascii=False)
        
        print(f"\nDebate saved to: {output_path}")
        print(f"Token usage: {self.token_usage}")
        
        return debate_log
