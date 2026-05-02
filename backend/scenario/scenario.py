from pathlib import Path

from .common import StepOutput
from .step import Step


class Scenario:
    def __init__(self, name: str, picture: Path, steps: list[Step]) -> None:
        self.name = name
        self.picture = picture
        self._steps_by_name = {step.name: step for step in steps}
        self.current_step = steps[0]

    def invoke(self, user_input: str) -> None:
        next_step_name = self.current_step.invoke(user_input)
        self.current_step = self._steps_by_name[next_step_name]

    def get_output(self) -> StepOutput:
        return self.current_step.get_output()
