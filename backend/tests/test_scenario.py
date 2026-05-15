from pathlib import Path

from scenario.common import StepOutput
from scenario.scenario import Scenario


class _FakeStep:
    def __init__(
        self,
        name: str,
        next_step_name: str | None = None,
        selected_index: int = 0,
        *,
        is_terminal: bool = False,
    ) -> None:
        self.name = name
        self._next_step_name = next_step_name if next_step_name is not None else name
        self._selected_index = selected_index
        self.is_terminal = is_terminal
        self.visit_count = 1
        self.last_index: int | None = None

    def invoke(self, index: int) -> tuple[str, int]:
        self.last_index = index
        self.visit_count += 1
        return self._next_step_name, self._selected_index

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


def test_invoke_passes_index_to_current_step():
    only_step = _FakeStep("step1", next_step_name="step1")

    scenario = Scenario(name="test", picture=Path("test.png"), steps=[only_step])
    scenario.invoke(2)

    assert only_step.last_index == 2


def test_invoke_transitions_current_step_to_returned_name():
    first_step = _FakeStep("step1", next_step_name="step2")
    second_step = _FakeStep("step2", next_step_name="step2")

    scenario = Scenario(
        name="test", picture=Path("test.png"), steps=[first_step, second_step]
    )
    scenario.invoke(0)

    assert scenario.current_step is second_step


def test_invoke_keeps_current_step_on_self_loop():
    only_step = _FakeStep("step1", next_step_name="step1")

    scenario = Scenario(name="test", picture=Path("test.png"), steps=[only_step])
    scenario.invoke(0)

    assert scenario.current_step is only_step


def test_get_output_delegates_to_current_step():
    first_step = _FakeStep("step1", next_step_name="step2")
    second_step = _FakeStep("step2", next_step_name="step2")

    scenario = Scenario(
        name="test", picture=Path("test.png"), steps=[first_step, second_step]
    )

    initial_output = scenario.get_output()
    assert initial_output.picture == Path("step1/picture.png")

    scenario.invoke(0)
    output_after_transition = scenario.get_output()

    assert output_after_transition.picture == Path("step2/picture.png")


def test_invoke_returns_selected_index_from_step():
    only_step = _FakeStep("step1", next_step_name="step1", selected_index=1)

    scenario = Scenario(name="test", picture=Path("p.png"), steps=[only_step])
    result = scenario.invoke(1)

    assert result == 1


def test_is_terminal_delegates_to_current_step():
    terminal_step = _FakeStep("end", next_step_name="end", is_terminal=True)

    scenario = Scenario(name="t", picture=Path("p.png"), steps=[terminal_step])

    assert scenario.is_terminal is True


def test_is_terminal_false_when_current_step_not_terminal():
    step = _FakeStep("step1", next_step_name="step1", is_terminal=False)

    scenario = Scenario(name="t", picture=Path("p.png"), steps=[step])

    assert scenario.is_terminal is False


def test_current_step_name_reflects_transitions():
    first_step = _FakeStep("step1", next_step_name="step2")
    second_step = _FakeStep("step2", next_step_name="step2")

    scenario = Scenario(
        name="test", picture=Path("p.png"), steps=[first_step, second_step]
    )

    assert scenario.current_step_name == "step1"

    scenario.invoke(0)

    assert scenario.current_step_name == "step2"


def test_reset_returns_to_first_step():
    first_step = _FakeStep("step1", next_step_name="step2")
    second_step = _FakeStep("step2", next_step_name="step2")

    scenario = Scenario(
        name="t", picture=Path("p.png"), steps=[first_step, second_step]
    )
    scenario.invoke(0)
    assert scenario.current_step is second_step

    scenario.reset()

    assert scenario.current_step is first_step


def test_reset_clears_visit_counts():
    first_step = _FakeStep("step1", next_step_name="step1")

    scenario = Scenario(name="t", picture=Path("p.png"), steps=[first_step])
    scenario.invoke(0)
    assert first_step.visit_count == 2

    scenario.reset()

    assert first_step.visit_count == 1
