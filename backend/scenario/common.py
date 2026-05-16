from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioInfo:
    name: str
    picture: Path
