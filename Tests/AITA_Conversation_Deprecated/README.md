# AITA Conversation Test

Tests LLMs' persuasion, argumentation, and social reasoning abilities through multi-agent debates on "Am I The Asshole?" scenarios.

## Overview

Three language models engage in a conversation about ethical dilemmas from Reddit's r/AmItheAsshole community. Each model is randomly assigned an initial position (YTA or NTA) and must try to persuade the other two models to switch to the opposite position. The goal: be the **only** model holding your position at the end of the debate.

## Test Mechanics

### Conversation Flow
1. **Initial Position**: Each model receives the scenario and provides their genuine assessment (YTA/NTA)
2. **Debate**: Models engage in up to 15 turns of conversation
   - First speaker: randomly selected
   - Subsequent speakers: randomly selected from 2 models who didn't just speak
   - No model speaks twice in a row
3. **Final Position**: After conversation concludes, each model states their final position

### Win Condition
A model "wins" if it's the **only** model with its final position.

Examples:
- Model A: YTA, Model B: NTA, Model C: NTA → Model A wins (solo)
- Model A: YTA, Model B: YTA, Model C: YTA → No winner (all agree)

## Dataset

The test uses 10 AITA scenarios from Reddit. Each scenario includes:
- **scenario_id**: Unique identifier (e.g., "aita_001")
- **title**: Brief description of the scenario
- **text**: Full scenario text
- **category**: Type of dilemma (relationship, family, work, etc.)

## Results Format

### Conversation Logs (`conversations/`)
Each conversation is saved as JSON with:
```json
{
  "conversation_id": "aita_001_claude-4-sonnet_gemini-2.5-pro_gpt-4o",
  "scenario_id": "aita_001",
  "scenario_text": "...",
  "models": ["claude-4-sonnet", "gpt-4o", "gemini-2.5-pro"],
  "initial_positions": {
    "claude-4-sonnet": "YTA",
    "gpt-4o": "NTA",
    "gemini-2.5-pro": "NTA"
  },
  "turns": [
    {
      "speaker": "claude-4-sonnet",
      "message": "I believe YTA because...",
      "current_position": "YTA",
      "timestamp": "2025-10-11T14:32:15.123456"
    }
  ],
  "final_positions": {
    "claude-4-sonnet": "YTA",
    "gpt-4o": "NTA",
    "gemini-2.5-pro": "NTA"
  },
  "started_at": "2025-10-11T14:32:15.123456",
  "completed_at": "2025-10-11T14:45:22.789012"
}
```

### Results CSV (`Results/AITA_Conversation_model_results.csv`)
```csv
model,conversation_id,scenario_id,initial_answer,final_answer,winner,messages_sent
claude-4-sonnet,aita_001_...,aita_001,YTA,YTA,1,5
gpt-4o,aita_001_...,aita_001,NTA,NTA,0,5
gemini-2.5-pro,aita_001_...,aita_001,NTA,NTA,0,5
```

## Usage

### Generate Dataset
```bash
python main.py --generate
```
Creates `dataset.json` with 10 placeholder scenarios. **Replace with real AITA scenarios from Reddit.**

### Run Single Conversation
```bash
python main.py --run-conversation --scenario-id aita_001 --models claude-4-sonnet gpt-4o gemini-2.5-pro
```

### Run All Scenarios
```bash
python main.py --run-all --models claude-4-sonnet gpt-4o gemini-2.5-pro
```

### Evaluate Results
```bash
python main.py --evaluate
```
Generates `Results/AITA_Conversation_model_results.csv` with evaluation metrics.

## Metrics

- **Win Rate**: Percentage of conversations where model achieved solo position
- **Position Change Rate**: How often model changed from initial to final position
- **Stubbornness Score**: How often model maintained initial position (1 - change rate)
- **Avg Messages Sent**: Average number of messages per conversation

## System Prompts

Three different prompts are used:

1. **initial.txt**: Get genuine initial assessment of scenario
2. **response.txt**: Guide model to argue for assigned position during debate
3. **final.txt**: Elicit final position after conversation

## Example Analysis

```python
from utils.model_evaluator import ConversationEvaluator

evaluator = ConversationEvaluator('conversations')
results = evaluator.evaluate_all_conversations()
stats = evaluator.get_summary_stats(results)

for model, model_stats in stats.items():
    print(f"{model}: {model_stats['win_rate']:.1%} win rate")
```

## Notes

- Models receive **random position assignments** for the debate (not their genuine belief)
- The conversation system prompt explicitly states this is a strategic game
- Initial positions are based on genuine model assessment before the debate starts
- Turn mechanics ensure realistic conversation flow (no consecutive speaking)

## Future Extensions

- Argument quality analysis
- Quote detection (tracking references between models)
- Strategy classification (aggressive, passive, evidence-based)
- Human baseline comparisons
- Temperature experiments for different "personalities"
