from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StepOutput:
    picture: Path
    script: Path
    voice: Path


@dataclass(frozen=True)
class StepTransition:
    condition: str
    next_step_name: str


@dataclass(frozen=True)
class StepPaths:
    step_dir: Path
    picture: Path


@dataclass(frozen=True)
class ScenarioInfo:
    name: str
    picture: Path
