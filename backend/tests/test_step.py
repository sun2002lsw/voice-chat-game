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


def _make_step(step_dir: Path, *, name: str = "step", conditions: list, nexts: list, count: int = SCRIPT_COUNT) -> Step:
    return Step(
        name=name,
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=conditions,
        next_step_names=nexts,
        script_count=count,
    )


def test_get_all_outputs_returns_one_entry_per_script(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])

    outputs = step.get_all_outputs()

    assert len(outputs) == SCRIPT_COUNT
    assert outputs[0].script == step_dir / "script" / "1.txt"
    assert outputs[0].voice == step_dir / "voice" / "1.wav"
    assert outputs[-1].script == step_dir / "script" / f"{SCRIPT_COUNT}.txt"
    assert outputs[-1].voice == step_dir / "voice" / f"{SCRIPT_COUNT}.wav"


def test_get_all_outputs_same_picture_for_all(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])

    outputs = step.get_all_outputs()

    assert all(o.picture == step_dir / "picture.png" for o in outputs)


def test_invoke_uses_index_to_select_next_step(step_dir):
    step = _make_step(step_dir, conditions=["메뉴 주문", "메뉴 질문"], nexts=["2. 결제", "1. 안내"])

    assert step.invoke(0) == ("2. 결제", 0)
    assert step.invoke(1) == ("1. 안내", 1)


def test_invoke_clamps_out_of_range_index_to_last(step_dir):
    step = _make_step(step_dir, conditions=["a", "b"], nexts=["next_a", "next_b"])

    assert step.invoke(99) == ("next_b", 1)


def test_invoke_clamps_negative_index_to_last(step_dir):
    step = _make_step(step_dir, conditions=["a", "b"], nexts=["next_a", "next_b"])

    assert step.invoke(-1) == ("next_b", 1)


def test_invoke_returns_self_name_when_terminal(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])

    assert step.invoke(0) == (step.name, 0)


def test_is_terminal_true_when_no_next_step_names(step_dir):
    step = _make_step(step_dir, conditions=[], nexts=[])

    assert step.is_terminal is True


def test_is_terminal_false_when_has_next_step_names(step_dir):
    step = _make_step(step_dir, conditions=[""], nexts=["next"])

    assert step.is_terminal is False


def test_conditions_extracts_non_empty_conditions(step_dir):
    step = _make_step(step_dir, conditions=["메뉴 주문", "메뉴 질문"], nexts=["2. 결제", "1. 안내"])

    assert step.conditions == ["메뉴 주문", "메뉴 질문"]


def test_conditions_excludes_empty_string_conditions(step_dir):
    step = _make_step(step_dir, conditions=[""], nexts=["next"])

    assert step.conditions == []


def test_next_step_names_lists_all_targets(step_dir):
    step = _make_step(step_dir, conditions=["메뉴 주문", ""], nexts=["2. 결제", "1. 안내"])

    assert step.next_step_names == ["2. 결제", "1. 안내"]


@pytest.mark.parametrize(
    "filename",
    ["anything.png", "weird-name.jpg", "x.jpeg", "Y.PNG", "a.JPG", "b.Jpeg"],
)
def test_find_image_accepts_image_files_with_any_name(tmp_path, filename):
    (tmp_path / filename).touch()

    result = find_image(tmp_path, label="test")

    assert result.name == filename


def test_find_image_ignores_non_image_files(tmp_path):
    (tmp_path / "readme.txt").touch()
    (tmp_path / "picture.png").touch()

    result = find_image(tmp_path, label="test")

    assert result.name == "picture.png"


def test_find_image_raises_when_no_image_in_folder(tmp_path):
    (tmp_path / "readme.txt").touch()

    with pytest.raises(FileNotFoundError, match="my_label"):
        find_image(tmp_path, label="my_label")
