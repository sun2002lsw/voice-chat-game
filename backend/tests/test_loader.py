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
    skip_script: bool = False,
    skip_voice: bool = False,
) -> None:
    step_dir = steps_dir / name
    step_dir.mkdir(parents=True)
    (step_dir / "picture.png").touch()
    if not skip_script:
        (step_dir / "script.txt").write_text("line 1", encoding="utf-8")
    if not skip_voice:
        (step_dir / "voice.wav").touch()


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
                "tone": "인사",
                "character": "Zephyr_smile",
                "loop": False,
                "complete_conditions": [],
                "next_steps": ["2. ask"],
            },
            {
                "step": "2. ask",
                "tone": "묻기",
                "character": "Zephyr_smile",
                "loop": False,
                "complete_conditions": [],
                "next_steps": ["2. ask"],
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
    del graph["steps"][0]["tone"]
    _write_scenario(
        scenarios_root, name="hello", graph=graph, steps_setup=_basic_steps()
    )

    with pytest.raises(ValueError, match="'tone' 키가 없습니다"):
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
                "tone": "...",
                "character": "Zephyr_smile",
                "loop": False,
                "complete_conditions": [],
                "next_steps": ["1. greet"],
            },
            {
                "step": "1. greet",
                "tone": "...",
                "character": "Zephyr_smile",
                "loop": False,
                "complete_conditions": [],
                "next_steps": ["1. greet"],
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


def test_load_scenario_raises_when_voice_file_missing(scenarios_root):
    graph = _basic_graph("hello")
    _write_scenario(
        scenarios_root,
        name="hello",
        graph=graph,
        steps_setup=[
            {"name": "1. greet", "skip_voice": True},
            {"name": "2. ask"},
        ],
    )

    with pytest.raises(FileNotFoundError, match="voice.wav"):
        load_scenario("hello")


def test_load_scenario_raises_when_script_file_missing(scenarios_root):
    graph = _basic_graph("hello")
    _write_scenario(
        scenarios_root,
        name="hello",
        graph=graph,
        steps_setup=[
            {"name": "1. greet", "skip_script": True},
            {"name": "2. ask"},
        ],
    )

    with pytest.raises(FileNotFoundError, match="script.txt"):
        load_scenario("hello")


