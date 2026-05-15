from pathlib import Path

from .common import StepOutput
from .step import Step


class Scenario:
    def __init__(self, name: str, picture: Path, steps: list[Step]) -> None:
        self.name = name
        self.picture = picture
        self._steps_by_name = {step.name: step for step in steps}
        self._first_step = steps[0]
        self.current_step = steps[0]

    def reset(self) -> None:
        self.current_step = self._first_step

    @property
    def current_step_name(self) -> str:
        return self.current_step.name

    @property
    def is_terminal(self) -> bool:
        return self.current_step.is_terminal

    def invoke(self, index: int) -> int:
        next_step_name, selected = self.current_step.invoke(index)
        self.current_step = self._steps_by_name[next_step_name]
        return selected

    def get_all_step_outputs(self) -> list[StepOutput]:
        return self.current_step.get_all_outputs()
