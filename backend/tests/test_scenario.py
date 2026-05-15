from pathlib import Path

from scenario.common import StepOutput
from scenario.scenario import Scenario
from scenario.step import Step


def _make_step(name: str, nexts: list[str] | None = None) -> Step:
    return Step(
        name=name,
        tone="...",
        character="Zephyr_smile",
        step_dir=Path(name),
        picture=Path(f"{name}/picture.png"),
        complete_conditions=["조건"] if nexts else [],
        next_step_names=nexts or [],
        script_count=1,
    )


def test_first_step_is_steps_zero():
    first = _make_step("step1", ["step2"])
    second = _make_step("step2")
    scenario = Scenario(name="s", picture=Path("p.png"), steps=[first, second])

    assert scenario.first_step is first


def test_get_step_returns_correct_step():
    first = _make_step("step1", ["step2"])
    second = _make_step("step2")
    scenario = Scenario(name="s", picture=Path("p.png"), steps=[first, second])

    assert scenario.get_step("step1") is first
    assert scenario.get_step("step2") is second


def test_get_step_returns_none_for_unknown():
    step = _make_step("step1")
    scenario = Scenario(name="s", picture=Path("p.png"), steps=[step])

    assert scenario.get_step("ghost") is None


def test_scenario_stores_name_and_picture():
    step = _make_step("step1")
    scenario = Scenario(name="my_scenario", picture=Path("cover.png"), steps=[step])

    assert scenario.name == "my_scenario"
    assert scenario.picture == Path("cover.png")
