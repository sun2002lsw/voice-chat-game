from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class StepOutput:
    picture: Path
    script: Path
    voice: Path


@dataclass(frozen=True)
class ScenarioInfo:
    name: str
    picture: Path


@dataclass(frozen=True)
class VisitOverflow:
    after: int
    next_step: str
