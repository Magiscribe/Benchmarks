"""Per-task .harness_state.json read/write and .done parsing."""
import json
from pathlib import Path


def save_state(state_file: Path, state: dict):
    state_file.write_text(json.dumps(state, indent=2))


def load_state(state_file: Path):
    if not state_file.exists():
        return None
    return json.loads(state_file.read_text())


def parse_done(workspace: Path):
    """Return (present, self_report_dict_or_None)."""
    done = workspace / ".done"
    if not done.exists():
        return False, None
    try:
        text = done.read_text().strip()
    except Exception:
        return True, None
    if not text:
        return True, None
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return True, data
        return True, {"raw": text}
    except json.JSONDecodeError:
        return True, {"raw": text}
