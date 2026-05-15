from pathlib import Path

from .step import Step


class Scenario:
    def __init__(self, name: str, picture: Path, steps: list[Step]) -> None:
        self.name = name
        self.picture = picture
        self._steps_by_name = {step.name: step for step in steps}
        self.first_step = steps[0]

    def get_step(self, name: str) -> Step | None:
        return self._steps_by_name.get(name)
