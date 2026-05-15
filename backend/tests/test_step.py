from pathlib import Path

import pytest

from scenario.loader import find_image
from scenario.step import Step

SCRIPT_COUNT = 3


@pytest.fixture
def step_dir(tmp_path: Path) -> Path:
    d = tmp_path / "1. greeting"
    d.mkdir()
    (d / "picture.png").touch()
    (d / "script").mkdir()
    for i in range(1, SCRIPT_COUNT + 1):
        (d / "script" / f"{i}.txt").write_text(f"line {i}")
    (d / "voice").mkdir()
    return d


def _make_step(step_dir: Path, *, conditions: list, nexts: list, count: int = SCRIPT_COUNT) -> Step:
    return Step(
        name="step",
        tone="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=conditions,
        next_step_names=nexts,
        script_count=count,
    )


def test_get_all_outputs_count_matches_script_count(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])
    assert len(step.get_all_outputs()) == SCRIPT_COUNT


def test_get_all_outputs_paths(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])
    outputs = step.get_all_outputs()
    assert outputs[0].script == step_dir / "script" / "1.txt"
    assert outputs[0].voice == step_dir / "voice" / "1.wav"
    assert outputs[-1].script == step_dir / "script" / f"{SCRIPT_COUNT}.txt"


def test_get_all_outputs_same_picture(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])
    assert all(o.picture == step_dir / "picture.png" for o in step.get_all_outputs())


def test_is_terminal_true_when_no_next_steps(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])
    assert step.is_terminal is True


def test_is_terminal_false_when_has_next_steps(step_dir):
    step = _make_step(step_dir, conditions=[""], nexts=["next"])
    assert step.is_terminal is False


def test_conditions_excludes_empty_strings(step_dir):
    step = _make_step(step_dir, conditions=["주문", ""], nexts=["a", "b"])
    assert step.conditions == ["주문"]


def test_conditions_returns_all_when_non_empty(step_dir):
    step = _make_step(step_dir, conditions=["주문", "질문"], nexts=["a", "b"])
    assert step.conditions == ["주문", "질문"]


@pytest.mark.parametrize(
    "filename",
    ["anything.png", "weird-name.jpg", "x.jpeg", "Y.PNG", "a.JPG"],
)
def test_find_image_accepts_image_files(tmp_path, filename):
    (tmp_path / filename).touch()
    assert find_image(tmp_path, label="test").name == filename


def test_find_image_raises_when_no_image(tmp_path):
    (tmp_path / "readme.txt").touch()
    with pytest.raises(FileNotFoundError, match="my_label"):
        find_image(tmp_path, label="my_label")
