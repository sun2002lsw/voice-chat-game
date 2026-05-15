from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class DialogEntry:
    role: str
    text: str
    created_at: datetime


@dataclass(frozen=True)
class StateLogEntry:
    step_name: str
    conditions: list[str]
    next_step_names: list[str]
    character_script: str
    selected_index: int | None


@dataclass(frozen=True)
class ScenarioSummary:
    name: str
    picture_path: Path


@dataclass(frozen=True)
class SessionState:
    scenario_name: str
    current_step_name: str
    is_terminal: bool
    picture_path: Path
    scripts: list[str]
    voice_paths: list[Path]
    profile_path: Path
    dialog: list[DialogEntry]
    state_log: list[StateLogEntry]
