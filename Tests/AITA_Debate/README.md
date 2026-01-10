# AITA Debate Test

A Lincoln-Douglas style debate benchmark that tests LLMs' argumentation, persuasion, and reasoning abilities through structured debates on "Am I The Asshole?" scenarios.

## Overview

Three language models participate in a formal debate:
- **PRO** (argues NTA - Not The Asshole)
- **CON** (argues YTA - You're The Asshole)  
- **JUDGE** (silently observes, then delivers verdict)

Models are **assigned** their positions regardless of personal opinion - they must channel the strongest possible argument for their side.

## Debate Structure (9 Phases)

| Phase | Speaker | Description |
|-------|---------|-------------|
| 1. PRO Opening | PRO | Constructive case for NTA |
| 2. CON Cross-Exam | CON → PRO | 2-3 Q&A exchanges |
| 3. CON Opening | CON | Constructive case for YTA |
| 4. PRO Cross-Exam | PRO → CON | 2-3 Q&A exchanges |
| 5. PRO Rebuttal | PRO | Attack CON's arguments |
| 6. CON Rebuttal | CON | Attack PRO's arguments |
| 7. PRO Closing | PRO | Final appeal |
| 8. CON Closing | CON | Final appeal |
| 9. JUDGE Verdict | JUDGE | Decision + reasoning |

### Judge Mechanics

The judge:
- Is a **silent observer** (not in the conversation)
- Maintains a **private scratchpad** with observations after each phase
- Delivers a verdict based on **argument quality**, not personal opinion
- Final output: `final_contemplation` + `decision` (PRO or CON)

## Usage

### Run Single Debate (Explicit Role Assignment)

```bash
python main.py --run-debate --scenario-id aita_001 \
    --pro-model claude-4-sonnet \
    --con-model gpt-4o \
    --judge-model gemini-2.5-pro
```

### Run with Random Model Assignment

```bash
python main.py --run-debate --scenario-id aita_001 --random-models
```

Or with a specific pool of models:

```bash
python main.py --run-debate --scenario-id aita_001 --random-models \
    --model-pool claude-4-sonnet gpt-4o gemini-2.5-pro llama-4-scout
```

### Run All Scenarios

```bash
python main.py --run-all \
    --pro-model claude-4-sonnet \
    --con-model gpt-4o \
    --judge-model gemini-2.5-pro
```

### Generate Dataset

```bash
python main.py --generate
```

### Evaluate Results

```bash
python main.py --evaluate
```

## Output Format

### Debate Logs (`debates/`)

Each debate is saved as JSON:

```json
{
  "debate_id": "aita_001_claude-4-sonnet_gpt-4o_gemini-2.5-pro_20260110_143215",
  "scenario_id": "aita_001",
  "scenario_text": "...",
  "models": {
    "pro": "claude-4-sonnet",
    "con": "gpt-4o", 
    "judge": "gemini-2.5-pro"
  },
  "phases": [
    {
      "phase_name": "pro_opening",
      "phase_type": "opening",
      "messages": [
        {
          "id": "1",
          "role": "PRO",
          "model": "claude-4-sonnet",
          "type": "statement",
          "content": "...",
          "timestamp": "..."
        }
      ]
    },
    {
      "phase_name": "con_cross_exam",
      "phase_type": "cross_examination",
      "questioner": "CON",
      "answerer": "PRO",
      "num_exchanges": 3,
      "messages": [
        {"id": "1.1", "role": "CON", "type": "question", "content": "..."},
        {"id": "1.2", "role": "PRO", "type": "answer", "content": "..."},
        {"id": "2.1", "role": "CON", "type": "question", "content": "..."},
        {"id": "2.2", "role": "PRO", "type": "answer", "content": "..."}
      ]
    }
  ],
  "judge_scratchpad": {
    "0_pro_opening": "PRO established a solid foundation...",
    "1_con_cross_exam": "CON exposed a weakness in...",
    "final_contemplation": "After weighing all arguments...",
    "decision": "CON"
  },
  "decision": "CON",
  "started_at": "...",
  "completed_at": "..."
}
```

### Results CSV (`Results/AITA_Debate_model_results.csv`)

```csv
model,role,debate_id,scenario_id,position_argued,won,judge_model
claude-4-sonnet,PRO,aita_001_...,aita_001,NTA,0,gemini-2.5-pro
gpt-4o,CON,aita_001_...,aita_001,YTA,1,gemini-2.5-pro
gemini-2.5-pro,JUDGE,aita_001_...,aita_001,N/A,N/A,gemini-2.5-pro
```

## Metrics

Currently tracked:
- **Decision**: Which side (PRO/CON) won the debate

Future metrics could include:
- Win rate by model
- Win rate by role (PRO vs CON advantage)
- Cross-examination effectiveness
- Judge consistency across similar scenarios

## Comparison to AITA_Conversation (Deprecated)

| Aspect | AITA_Conversation (Old) | AITA_Debate (New) |
|--------|------------------------|-------------------|
| Structure | Free-form, random turns | Lincoln-Douglas formal |
| Roles | Random position assignment | Explicit PRO/CON/JUDGE |
| Win condition | Be the only one with your position | Judge verdict |
| Judge | None (mechanical evaluation) | Active LLM observer |
| Cross-examination | None | Structured Q&A |
| Phases | Unstructured | 9 distinct phases |

## Files

```
AITA_Debate/
├── main.py                      # CLI entry point
├── test_config.py               # Configuration (phases, roles, defaults)
├── dataset.json                 # Scenario dataset
├── scenarios.json               # Real AITA scenarios
├── debates/                     # Output debate logs (JSON)
├── responses/                   # Raw model responses
├── system_messages/             # Prompt templates
│   ├── pro_opening.txt
│   ├── con_opening.txt
│   ├── cross_exam_question.txt
│   ├── cross_exam_answer.txt
│   ├── rebuttal.txt
│   ├── closing.txt
│   ├── judge_observation.txt
│   └── judge_verdict.txt
└── utils/
    ├── debate_manager.py        # Core orchestration
    ├── dataset_creator.py       # Dataset generation
    └── debate_evaluator.py      # Results evaluation
```
