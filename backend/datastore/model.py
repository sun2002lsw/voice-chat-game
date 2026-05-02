from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DialogEntry:
    role: str
    text: str
    created_at: datetime


@dataclass(frozen=True)
class StateLogEntry:
    step_name: str
    visit_count: int
    conditions: list[str]
    next_step_names: list[str]
    character_script: str
    user_input: str
    llm_index: int | None


@dataclass(frozen=True)
class ScenarioSnapshot:
    current_step_name: str
    step_visits: dict[str, int]
