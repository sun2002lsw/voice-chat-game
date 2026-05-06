from pathlib import Path

from datastore.model import ScenarioSnapshot

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
        for step in self._steps_by_name.values():
            step.visit_count = 1
        self.current_step = self._first_step

    @property
    def current_step_name(self) -> str:
        return self.current_step.name

    @property
    def is_terminal(self) -> bool:
        return self.current_step.is_terminal

    @property
    def is_auto_advance(self) -> bool:
        return self.current_step.is_auto_advance

    def invoke(self, user_input: str) -> int | None:
        next_step_name, llm_index = self.current_step.invoke(user_input)
        self.current_step = self._steps_by_name[next_step_name]

        return llm_index

    def get_output(self) -> StepOutput:
        return self.current_step.get_output()

    def snapshot(self) -> ScenarioSnapshot:
        step_visits = {
            name: step.visit_count
            for name, step in self._steps_by_name.items()
        }
        return ScenarioSnapshot(
            current_step_name=self.current_step.name,
            step_visits=step_visits,
        )

    def restore(self, snapshot: ScenarioSnapshot) -> None:
        for name, visit_count in snapshot.step_visits.items():
            self._steps_by_name[name].visit_count = visit_count
        self.current_step = self._steps_by_name[snapshot.current_step_name]
