from pathlib import Path
from typing import Any

import pytest
import yaml

from scenario import loader
from scenario.loader import load_scenario


def _write_step(
    steps_dir: Path,
    *,
    name: str,
    script_count: int = 1,
    voice_count: int | None = None,
) -> None:
    if voice_count is None:
        voice_count = script_count
    step_dir = steps_dir / name
    step_dir.mkdir(parents=True)
    (step_dir / "picture.png").touch()
    script_dir = step_dir / "script"
    script_dir.mkdir()
    for i in range(1, script_count + 1):
        (script_dir / f"{i}.txt").write_text(f"line {i}", encoding="utf-8")
    voice_dir = step_dir / "voice"
    voice_dir.mkdir()
    for i in range(1, voice_count + 1):
        (voice_dir / f"{i}.wav").touch()


def _write_scenario(
    scenarios_root: Path,
    *,
    name: str,
    graph: dict[str, Any],
    steps_setup: list[dict[str, Any]],
) -> Path:
    sc_dir = scenarios_root / name
    sc_dir.mkdir(parents=True)
    (sc_dir / "profile.png").touch()
    (sc_dir / "graph.yaml").write_text(
        yaml.safe_dump(graph, allow_unicode=True),
        encoding="utf-8",
    )
    steps_dir = sc_dir / "steps"
    steps_dir.mkdir()
    for setup in steps_setup:
        _write_step(steps_dir, **setup)
    return sc_dir


@pytest.fixture
def scenarios_root(tmp_path, monkeypatch):
    root = tmp_path / ".scenario"
    root.mkdir()
    monkeypatch.setattr(loader, "SCENARIOS_ROOT", root)
    return root


def _basic_graph(name: str) -> dict[str, Any]:
    return {
        "scenario": name,
        "steps": [
            {
                "step": "1. greet",
                "scene": "인사",
                "character": "Zephyr_smile",
                "complete_conditions": [],
                "next_steps": ["2. ask"],
            },
            {
                "step": "2. ask",
                "scene": "묻기",
                "character": "Zephyr_smile",
                "complete_conditions": [],
                "next_steps": [],
            },
        ],
    }


def _basic_steps() -> list[dict[str, Any]]:
    return [{"name": "1. greet"}, {"name": "2. ask"}]


def test_load_scenario_happy_path(scenarios_root):
    _write_scenario(
        scenarios_root,
        name="hello",
        graph=_basic_graph("hello"),
        steps_setup=_basic_steps(),
    )

    sc = load_scenario("hello")

    assert sc.name == "hello"
    assert sc.first_step.name == "1. greet"


def test_load_scenario_raises_when_top_level_not_mapping(scenarios_root):
    sc_dir = scenarios_root / "broken"
    sc_dir.mkdir()
    (sc_dir / "profile.png").touch()
    (sc_dir / "graph.yaml").write_text("- just\n- a list\n", encoding="utf-8")
    (sc_dir / "steps").mkdir()

    with pytest.raises(TypeError, match="매핑"):
        load_scenario("broken")


def test_load_scenario_raises_when_scenario_key_missing(scenarios_root):
    graph = _basic_graph("hello")
    del graph["scenario"]
    _write_scenario(
        scenarios_root, name="hello", graph=graph, steps_setup=_basic_steps()
    )

    with pytest.raises(ValueError, match="'scenario' 키가 없습니다"):
        load_scenario("hello")


def test_load_scenario_raises_when_steps_key_missing(scenarios_root):
    graph = _basic_graph("hello")
    del graph["steps"]
    sc_dir = scenarios_root / "hello"
    sc_dir.mkdir()
    (sc_dir / "profile.png").touch()
    (sc_dir / "graph.yaml").write_text(
        yaml.safe_dump(graph, allow_unicode=True),
        encoding="utf-8",
    )
    (sc_dir / "steps").mkdir()

    with pytest.raises(ValueError, match="'steps' 키가 없습니다"):
        load_scenario("hello")


def test_load_scenario_raises_when_scenario_field_mismatches_dir(scenarios_root):
    graph = _basic_graph("other-name")
    _write_scenario(
        scenarios_root, name="hello", graph=graph, steps_setup=_basic_steps()
    )

    with pytest.raises(ValueError, match="폴더 이름"):
        load_scenario("hello")


def test_load_scenario_raises_when_step_entry_missing_required_key(scenarios_root):
    graph = _basic_graph("hello")
    del graph["steps"][0]["scene"]
    _write_scenario(
        scenarios_root, name="hello", graph=graph, steps_setup=_basic_steps()
    )

    with pytest.raises(ValueError, match="'scene' 키가 없습니다"):
        load_scenario("hello")


def test_load_scenario_raises_when_steps_list_is_empty(scenarios_root):
    graph = {"scenario": "hello", "steps": []}
    sc_dir = scenarios_root / "hello"
    sc_dir.mkdir()
    (sc_dir / "profile.png").touch()
    (sc_dir / "graph.yaml").write_text(
        yaml.safe_dump(graph, allow_unicode=True),
        encoding="utf-8",
    )
    (sc_dir / "steps").mkdir()

    with pytest.raises(ValueError, match="step이 최소 1개"):
        load_scenario("hello")


def test_load_scenario_raises_when_step_names_duplicate(scenarios_root):
    graph = {
        "scenario": "hello",
        "steps": [
            {
                "step": "1. greet",
                "scene": "...",
                "character": "Zephyr_smile",
                "complete_conditions": [],
                "next_steps": ["1. greet"],
            },
            {
                "step": "1. greet",
                "scene": "...",
                "character": "Zephyr_smile",
                "complete_conditions": [],
                "next_steps": [],
            },
        ],
    }
    _write_scenario(
        scenarios_root,
        name="hello",
        graph=graph,
        steps_setup=[{"name": "1. greet"}],
    )

    with pytest.raises(ValueError, match="중복된 step 이름"):
        load_scenario("hello")


def test_load_scenario_raises_when_next_step_references_unknown(scenarios_root):
    graph = _basic_graph("hello")
    graph["steps"][0]["next_steps"] = ["does-not-exist"]
    _write_scenario(
        scenarios_root, name="hello", graph=graph, steps_setup=_basic_steps()
    )

    with pytest.raises(ValueError, match="존재하지 않는 step 'does-not-exist'"):
        load_scenario("hello")


def test_load_scenario_raises_when_voice_count_differs_from_script_count(
    scenarios_root,
):
    graph = _basic_graph("hello")
    _write_scenario(
        scenarios_root,
        name="hello",
        graph=graph,
        steps_setup=[
            {"name": "1. greet", "script_count": 3, "voice_count": 2},
            {"name": "2. ask"},
        ],
    )

    with pytest.raises(ValueError, match="파일 개수가 다릅니다"):
        load_scenario("hello")


