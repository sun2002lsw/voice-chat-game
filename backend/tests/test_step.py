from pathlib import Path

import pytest

from scenario.loader import find_image
from scenario.step import Step


@pytest.fixture
def step_dir(tmp_path: Path) -> Path:
    d = tmp_path / "1. greeting"
    d.mkdir()
    (d / "picture.png").touch()
    (d / "script").mkdir()
    (d / "script" / "1.txt").write_text("hello")
    (d / "voice").mkdir()
    return d


class _FakeLLM:
    next_index: int = 0
    last_call_args: dict | None = None

    def __init__(self) -> None:
        pass

    def get_next_step(
        self,
        scene: str,
        complete_conditions: list[str],
        user_input: str,
    ) -> int:
        _FakeLLM.last_call_args = {
            "scene": scene,
            "complete_conditions": complete_conditions,
            "user_input": user_input,
        }
        return _FakeLLM.next_index


class _RaisingLLM:
    def __init__(self) -> None:
        pass

    def get_next_step(self, *args, **kwargs) -> int:
        msg = "LLM should not be called when complete_conditions is empty"
        raise AssertionError(msg)


@pytest.fixture(autouse=True)
def reset_fake_llm_state():
    _FakeLLM.next_index = 0
    _FakeLLM.last_call_args = None


def test_get_output_returns_paths_for_first_visit(step_dir):
    step = Step(
        name="1. greeting",
        scene="인사하는 상황",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
    )

    output = step.get_output()

    assert output.picture == step_dir / "picture.png"
    assert output.script == step_dir / "script" / "1.txt"
    assert output.voice == step_dir / "voice" / "1.wav"


def test_get_output_reflects_visit_count_after_invoke(step_dir, monkeypatch):
    monkeypatch.setattr("scenario.step.LLM", _RaisingLLM)

    step = Step(
        name="self-loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
    )

    step.invoke("입력")
    output_after_first_invoke = step.get_output()

    step.invoke("입력")
    output_after_second_invoke = step.get_output()

    assert output_after_first_invoke.script == step_dir / "script" / "2.txt"
    assert output_after_first_invoke.voice == step_dir / "voice" / "2.wav"
    assert output_after_second_invoke.script == step_dir / "script" / "3.txt"
    assert output_after_second_invoke.voice == step_dir / "voice" / "3.wav"


@pytest.mark.parametrize(
    ("llm_index", "expected_next_step"),
    [
        (0, "2. 결제"),
        (1, "1. 어서오세요-안내"),
    ],
)
def test_invoke_returns_step_name_and_llm_index_tuple(
    step_dir,
    monkeypatch,
    llm_index,
    expected_next_step,
):
    monkeypatch.setattr("scenario.step.LLM", _FakeLLM)
    _FakeLLM.next_index = llm_index

    step = Step(
        name="1. 어서오세요",
        scene="카페 직원으로서 인사한다",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 어서오세요-안내"],
    )

    result = step.invoke("아메리카노 주세요")

    assert result == (expected_next_step, llm_index)


def test_invoke_passes_scene_conditions_and_user_input_to_llm(step_dir, monkeypatch):
    monkeypatch.setattr("scenario.step.LLM", _FakeLLM)

    step = Step(
        name="1. 어서오세요",
        scene="카페 직원으로서 인사한다",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 어서오세요-안내"],
    )

    step.invoke("아메리카노 주세요")

    assert _FakeLLM.last_call_args == {
        "scene": "카페 직원으로서 인사한다",
        "complete_conditions": ["메뉴 주문", "메뉴 질문"],
        "user_input": "아메리카노 주세요",
    }


def test_invoke_skips_llm_when_complete_conditions_empty(step_dir, monkeypatch):
    monkeypatch.setattr("scenario.step.LLM", _RaisingLLM)

    step = Step(
        name="1. 어서오세요-안내",
        scene="안내한다",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[""],
        next_step_names=["1. 어서오세요"],
    )

    result = step.invoke("아무 입력")

    assert result == ("1. 어서오세요", None)


def test_invoke_returns_self_name_when_no_conditions_and_no_next_steps(
    step_dir,
    monkeypatch,
):
    monkeypatch.setattr("scenario.step.LLM", _RaisingLLM)

    step = Step(
        name="2. 결제",
        scene="결제 요청",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
    )

    result = step.invoke("아무 입력")

    assert result == ("2. 결제", None)


def test_invoke_increments_visit_count_on_each_call(step_dir, monkeypatch):
    monkeypatch.setattr("scenario.step.LLM", _FakeLLM)

    step = Step(
        name="1. 어서오세요",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문"],
        next_step_names=["2. 결제"],
    )

    assert step.visit_count == 1
    step.invoke("입력 1")
    assert step.visit_count == 2
    step.invoke("입력 2")
    assert step.visit_count == 3


def test_invoke_raises_when_llm_returns_out_of_range_index(step_dir, monkeypatch):
    monkeypatch.setattr("scenario.step.LLM", _FakeLLM)
    _FakeLLM.next_index = 99

    step = Step(
        name="1. 어서오세요",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 안내"],
    )

    with pytest.raises(IndexError):
        step.invoke("입력")


def test_invoke_increments_visit_count_even_when_no_conditions(step_dir, monkeypatch):
    monkeypatch.setattr("scenario.step.LLM", _RaisingLLM)

    step = Step(
        name="self-loop",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
    )

    step.invoke("입력")

    assert step.visit_count == 2


def test_is_terminal_true_when_no_next_step_names(step_dir):
    step = Step(
        name="end",
        scene="...",
        character="Zephyr_smile",
        step_dir=step_dir,
        picture=step_dir / "picture.png",
        complete_conditions=[],
        next_step_names=[],
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
