from pathlib import Path

import pytest

from scenario.common import VisitOverflow
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


def test_get_output_returns_paths_for_first_visit(step_dir):
    step = Step(
        name="1. greeting",
        scene="인사하는 상황",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
        script_count=SCRIPT_COUNT,
    )

    output = step.get_output()

    assert output.picture == step_dir / "picture.png"
    assert output.script == step_dir / "script" / "1.txt"
    assert output.voice == step_dir / "voice" / "1.wav"


def test_get_output_reflects_visit_count_after_invoke(step_dir):
    step = Step(
        name="self-loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
        script_count=SCRIPT_COUNT,
    )

    step.invoke(0)
    output_after_first_invoke = step.get_output()

    step.invoke(0)
    output_after_second_invoke = step.get_output()

    assert output_after_first_invoke.script == step_dir / "script" / "2.txt"
    assert output_after_first_invoke.voice == step_dir / "voice" / "2.wav"
    assert output_after_second_invoke.script == step_dir / "script" / "3.txt"
    assert output_after_second_invoke.voice == step_dir / "voice" / "3.wav"


@pytest.mark.parametrize(
    ("index", "expected_next_step"),
    [
        (0, "2. 결제"),
        (1, "1. 어서오세요-안내"),
    ],
)
def test_invoke_uses_index_to_select_next_step(step_dir, index, expected_next_step):
    step = Step(
        name="1. 어서오세요",
        scene="카페 직원으로서 인사한다",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 어서오세요-안내"],
        script_count=SCRIPT_COUNT,
    )

    result = step.invoke(index)

    assert result == (expected_next_step, index)


def test_invoke_clamps_out_of_range_index_to_last(step_dir):
    step = Step(
        name="1. 어서오세요",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 안내"],
        script_count=SCRIPT_COUNT,
    )

    result = step.invoke(99)

    assert result == ("1. 안내", 1)


def test_invoke_clamps_negative_index_to_last(step_dir):
    step = Step(
        name="step",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["a", "b"],
        next_step_names=["next_a", "next_b"],
        script_count=SCRIPT_COUNT,
    )

    result = step.invoke(-1)

    assert result == ("next_b", 1)


def test_invoke_returns_self_name_when_terminal(step_dir):
    step = Step(
        name="2. 결제",
        scene="결제 요청",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
        script_count=SCRIPT_COUNT,
    )

    result = step.invoke(0)

    assert result == ("2. 결제", 0)


def test_invoke_increments_visit_count_on_each_call(step_dir):
    step = Step(
        name="1. 어서오세요",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문"],
        next_step_names=["2. 결제"],
        script_count=SCRIPT_COUNT,
    )

    assert step.visit_count == 1
    step.invoke(0)
    assert step.visit_count == 2
    step.invoke(0)
    assert step.visit_count == 3


def test_invoke_increments_visit_count_even_when_terminal(step_dir):
    step = Step(
        name="self-loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
        script_count=SCRIPT_COUNT,
    )

    step.invoke(0)

    assert step.visit_count == 2


def test_invoke_clamps_visit_count_to_script_count_on_self_loop(step_dir):
    step = Step(
        name="self-loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
        script_count=2,
    )

    step.invoke(0)
    assert step.visit_count == 2
    output_at_2 = step.get_output()

    step.invoke(0)
    assert step.visit_count == 2
    output_at_3 = step.get_output()

    step.invoke(0)
    assert step.visit_count == 2

    assert output_at_2.script == step_dir / "script" / "2.txt"
    assert output_at_3.script == step_dir / "script" / "2.txt"


def test_is_terminal_true_when_no_next_step_names(step_dir):
    step = Step(
        name="end",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
        script_count=SCRIPT_COUNT,
    )

    assert step.is_terminal is True


def test_is_terminal_false_when_has_next_step_names(step_dir):
    step = Step(
        name="step",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[""],
        next_step_names=["next"],
        script_count=SCRIPT_COUNT,
    )

    assert step.is_terminal is False


def test_conditions_extracts_non_empty_conditions(step_dir):
    step = Step(
        name="step",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 안내"],
        script_count=SCRIPT_COUNT,
    )

    assert step.conditions == ["메뉴 주문", "메뉴 질문"]


def test_conditions_excludes_empty_string_conditions(step_dir):
    step = Step(
        name="step",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[""],
        next_step_names=["next"],
        script_count=SCRIPT_COUNT,
    )

    assert step.conditions == []


def test_next_step_names_lists_all_targets(step_dir):
    step = Step(
        name="step",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", ""],
        next_step_names=["2. 결제", "1. 안내"],
        script_count=SCRIPT_COUNT,
    )

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


def test_invoke_redirects_to_overflow_at_threshold(step_dir):
    step = Step(
        name="loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["탈출", "계속"],
        next_step_names=["escape", "loop"],
        script_count=SCRIPT_COUNT,
        visit_overflow=VisitOverflow(after=3, next_step="redirect"),
    )
    step.visit_count = 3

    result = step.invoke(0)

    assert result == ("redirect", 0)


def test_invoke_overflow_above_threshold(step_dir):
    step = Step(
        name="loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["탈출", "계속"],
        next_step_names=["escape", "loop"],
        script_count=SCRIPT_COUNT,
        visit_overflow=VisitOverflow(after=3, next_step="redirect"),
    )
    step.visit_count = 100

    result = step.invoke(0)

    assert result == ("redirect", 0)


def test_invoke_does_not_apply_overflow_below_threshold(step_dir):
    step = Step(
        name="loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["탈출", "계속"],
        next_step_names=["escape", "loop"],
        script_count=SCRIPT_COUNT,
        visit_overflow=VisitOverflow(after=3, next_step="redirect"),
    )
    step.visit_count = 2

    result = step.invoke(1)

    assert result == ("loop", 1)
