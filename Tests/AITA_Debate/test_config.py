# Configuration settings for AITA Debate Test (Lincoln-Douglas Style)

from enum import Enum
from typing import List, Tuple

# =============================================================================
# ROLES
# =============================================================================

class DebateRole(Enum):
    """Roles in the debate."""
    PRO = "PRO"   # Argues NTA (Not The Asshole)
    CON = "CON"   # Argues YTA (You're The Asshole)
    JUDGE = "JUDGE"  # Silent observer, delivers verdict


# =============================================================================
# DEBATE PHASES
# =============================================================================

class DebatePhase(Enum):
    """
    The 9 phases of a Lincoln-Douglas style debate.
    Each phase has a name and indicates which role is the primary speaker.
    """
    PRO_OPENING = ("pro_opening", DebateRole.PRO)
    CON_CROSS_EXAM = ("con_cross_exam", DebateRole.CON)  # CON questions PRO
    CON_OPENING = ("con_opening", DebateRole.CON)
    PRO_CROSS_EXAM = ("pro_cross_exam", DebateRole.PRO)  # PRO questions CON
    PRO_REBUTTAL = ("pro_rebuttal", DebateRole.PRO)
    CON_REBUTTAL = ("con_rebuttal", DebateRole.CON)
    PRO_CLOSING = ("pro_closing", DebateRole.PRO)
    CON_CLOSING = ("con_closing", DebateRole.CON)
    JUDGE_VERDICT = ("judge_verdict", DebateRole.JUDGE)
    
    def __init__(self, phase_name: str, primary_role: DebateRole):
        self.phase_name = phase_name
        self.primary_role = primary_role


# Ordered list of phases for iteration
DEBATE_PHASE_ORDER: List[DebatePhase] = [
    DebatePhase.PRO_OPENING,
    DebatePhase.CON_CROSS_EXAM,
    DebatePhase.CON_OPENING,
    DebatePhase.PRO_CROSS_EXAM,
    DebatePhase.PRO_REBUTTAL,
    DebatePhase.CON_REBUTTAL,
    DebatePhase.PRO_CLOSING,
    DebatePhase.CON_CLOSING,
    DebatePhase.JUDGE_VERDICT,
]

# Phases where the judge should record observations (all except verdict)
JUDGE_OBSERVATION_PHASES: List[DebatePhase] = [
    DebatePhase.PRO_OPENING,
    DebatePhase.CON_CROSS_EXAM,
    DebatePhase.CON_OPENING,
    DebatePhase.PRO_CROSS_EXAM,
    DebatePhase.PRO_REBUTTAL,
    DebatePhase.CON_REBUTTAL,
    DebatePhase.PRO_CLOSING,
    DebatePhase.CON_CLOSING,
]


# =============================================================================
# CROSS-EXAMINATION SETTINGS
# =============================================================================

# Number of Q&A exchanges during cross-examination (randomly selected)
CROSS_EXAM_MIN_QUESTIONS = 2
CROSS_EXAM_MAX_QUESTIONS = 3


# =============================================================================
# MODEL DEFAULTS
# =============================================================================

# Default model assignments (can be overridden via CLI)
DEFAULT_PRO_MODEL = "claude-4-sonnet"
DEFAULT_CON_MODEL = "gpt-4o"
DEFAULT_JUDGE_MODEL = "gemini-2.5-pro"

# All default models as a tuple (PRO, CON, JUDGE)
DEFAULT_MODELS: Tuple[str, str, str] = (
    DEFAULT_PRO_MODEL,
    DEFAULT_CON_MODEL,
    DEFAULT_JUDGE_MODEL,
)


# =============================================================================
# POSITIONS
# =============================================================================

# What each role argues for
PRO_POSITION = "NTA"  # Not The Asshole
CON_POSITION = "YTA"  # You're The Asshole


# =============================================================================
# DATASET CONFIGURATION
# =============================================================================

NUM_SCENARIOS = 10
DATASET_FILE = "dataset.json"
SCENARIOS_FILE = "scenarios.json"


# =============================================================================
# OUTPUT DIRECTORIES
# =============================================================================

DEBATES_DIR = "debates"
RESPONSES_DIR = "responses"


# =============================================================================
# RESULTS
# =============================================================================

RESULTS_CSV_NAME = "AITA_Debate_model_results.csv"
