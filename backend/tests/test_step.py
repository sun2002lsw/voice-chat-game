from pathlib import Path

import pytest

from scenario.loader import find_image
from scenario.step import Step


@pytest.fixture
def step_dir(tmp_path: Path) -> Path:
    d = tmp_path / "1. greeting"
    d.mkdir()
    (d / "picture.png").touch()
    (d / "script.txt").write_text("line 1")
    (d / "voice.wav").touch()
    return d


def _make_step(step_dir: Path, *, conditions: list, nexts: list) -> Step:
    return Step(
        name="step",
        tone="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=conditions,
        next_step_names=nexts,
    )


def test_script_path(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=["step"])
    assert step.script == step_dir / "script.txt"


def test_voice_path(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=["step"])
    assert step.voice == step_dir / "voice.wav"


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
