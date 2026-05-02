from pathlib import Path

from scenario.common import StepOutput
from scenario.scenario import Scenario


class _FakeStep:
    def __init__(self, name: str, next_step_name: str | None = None) -> None:
        self.name = name
        self._next_step_name = next_step_name if next_step_name is not None else name
        self.last_user_input: str | None = None

    def invoke(self, user_input: str) -> str:
        self.last_user_input = user_input
        return self._next_step_name

    def get_output(self) -> StepOutput:
        return StepOutput(
            picture=Path(f"{self.name}/picture.png"),
            script=Path(f"{self.name}/script.txt"),
            voice=Path(f"{self.name}/voice.wav"),
        )


def test_scenario_stores_name_from_argument():
    only_step = _FakeStep("step1", next_step_name="step1")

    scenario = Scenario(
        name="test_scenario", picture=Path("test.png"), steps=[only_step]
    )

    assert scenario.name == "test_scenario"


def test_current_step_starts_as_first_step():
    first_step = _FakeStep("step1")
    second_step = _FakeStep("step2")

    scenario = Scenario(
        name="test", picture=Path("test.png"), steps=[first_step, second_step]
    )

    assert scenario.current_step is first_step


def test_invoke_passes_user_input_to_current_step():
    only_step = _FakeStep("step1", next_step_name="step1")

    scenario = Scenario(name="test", picture=Path("test.png"), steps=[only_step])
    scenario.invoke("hello")

    assert only_step.last_user_input == "hello"


def test_invoke_transitions_current_step_to_returned_name():
    first_step = _FakeStep("step1", next_step_name="step2")
    second_step = _FakeStep("step2", next_step_name="step2")

    scenario = Scenario(
        name="test", picture=Path("test.png"), steps=[first_step, second_step]
    )
    scenario.invoke("input")

    assert scenario.current_step is second_step


def test_invoke_keeps_current_step_on_self_loop():
    only_step = _FakeStep("step1", next_step_name="step1")

    scenario = Scenario(name="test", picture=Path("test.png"), steps=[only_step])
    scenario.invoke("input")

    assert scenario.current_step is only_step


def test_get_output_delegates_to_current_step():
    first_step = _FakeStep("step1", next_step_name="step2")
    second_step = _FakeStep("step2", next_step_name="step2")

    scenario = Scenario(
        name="test", picture=Path("test.png"), steps=[first_step, second_step]
    )

    initial_output = scenario.get_output()
    assert initial_output.picture == Path("step1/picture.png")

    scenario.invoke("input")
    output_after_transition = scenario.get_output()

    assert output_after_transition.picture == Path("step2/picture.png")
