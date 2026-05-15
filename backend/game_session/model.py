from dataclasses import dataclass
from pathlib import Path

from datastore.model import DialogEntry, StateLogEntry


@dataclass(frozen=True)
class ScenarioSummary:
    name: str
    picture_path: Path


@dataclass(frozen=True)
class SessionState:
    scenario_name: str
    current_step_name: str
    current_visit_count: int
    is_terminal: bool
    is_auto_advance: bool
    picture_path: Path
    voice_path: Path
    profile_path: Path
    dialog: list[DialogEntry]
    state_log: list[StateLogEntry]
