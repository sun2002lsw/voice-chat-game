import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from scenario.common import ScenarioInfo
from scenario.manager import ScenarioManager
from scenario.scenario import Scenario
from scenario.step import Step
from singleton import Singleton


@pytest.fixture(autouse=True)
def reset_manager_singleton():
    Singleton._instances.pop(ScenarioManager, None)
    yield
    Singleton._instances.pop(ScenarioManager, None)


def _write_graph(scenario_dir: Path, graph: dict[str, Any]) -> None:
    graph_yaml_text = yaml.safe_dump(graph, allow_unicode=True)
    (scenario_dir / "graph.yaml").write_text(graph_yaml_text, encoding="utf-8")


def _make_step_dir(scenario_dir: Path, step_name: str) -> Path:
    step_dir = scenario_dir / "steps" / step_name
    step_dir.mkdir(parents=True)
    (step_dir / "picture.png").touch()
    (step_dir / "script").mkdir()
    (step_dir / "script" / "1.txt").write_text("x")
    (step_dir / "voice").mkdir()
    (step_dir / "voice" / "1.wav").touch()
    return step_dir


def _make_step_dirs(scenario_dir: Path, step_names: list[str]) -> None:
    for step_name in step_names:
        _make_step_dir(scenario_dir, step_name)


def _build_minimal_scenario(root: Path, scenario_name: str = "test") -> Path:
    scenario_dir = root / scenario_name
    scenario_dir.mkdir(parents=True)
    (scenario_dir / "picture.png").touch()

    graph = {
        "scenario": scenario_name,
        "steps": [
            {
                "step": "step1",
                "scene": "...",
                "character": "X",
                "complete_conditions": [],
                "next_steps": [],
            },
        ],
    }
    _write_graph(scenario_dir, graph)
    _make_step_dir(scenario_dir, "step1")

    return scenario_dir


@pytest.fixture
def scenarios_root(tmp_path: Path) -> Path:
    scenarios_root = tmp_path / "scenarios"
    scenarios_root.mkdir()

    cafe_dir = scenarios_root / "test_cafe"
    cafe_dir.mkdir()
    (cafe_dir / "picture.png").touch()

    cafe_graph = {
        "scenario": "test_cafe",
        "steps": [
            {
                "step": "1. 인사",
                "scene": "직원이 인사한다",
                "character": "Zephyr",
                "complete_conditions": ["주문"],
                "next_steps": ["2. 결제"],
            },
            {
                "step": "2. 결제",
                "scene": "결제한다",
                "character": "Zephyr",
                "complete_conditions": [],
                "next_steps": [],
            },
        ],
    }
    _write_graph(cafe_dir, cafe_graph)
    _make_step_dirs(cafe_dir, ["1. 인사", "2. 결제"])

    return scenarios_root


def test_init_eagerly_loads_all_scenarios(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    manager = ScenarioManager()

    assert "test_cafe" in manager._scenarios


def test_init_eagerly_loads_multiple_scenarios(scenarios_root, monkeypatch):
    second_dir = scenarios_root / "test_interview"
    second_dir.mkdir()
    (second_dir / "picture.png").touch()
    second_graph = {
        "scenario": "test_interview",
        "steps": [
            {
                "step": "1. 시작",
                "scene": "면접 시작",
                "character": "Interviewer",
                "complete_conditions": [],
                "next_steps": [],
            },
        ],
    }
    _write_graph(second_dir, second_graph)
    _make_step_dirs(second_dir, ["1. 시작"])

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    manager = ScenarioManager()

    assert set(manager._scenarios.keys()) == {"test_cafe", "test_interview"}


def test_init_raises_when_step_config_invalid(tmp_path, monkeypatch):
    bad_root = tmp_path / "bad_scenarios"
    bad_dir = bad_root / "bad_scenario"
    bad_dir.mkdir(parents=True)
    (bad_dir / "picture.png").touch()
    bad_graph = {
        "scenario": "bad_scenario",
        "steps": [
            {
                "step": "step1",
                "scene": "...",
                "character": "X",
                "complete_conditions": [],
                "next_steps": ["A", "B"],
            },
        ],
    }
    _write_graph(bad_dir, bad_graph)
    _make_step_dirs(bad_dir, ["step1"])

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", bad_root)

    with pytest.raises(ValueError, match="complete_conditions"):
        ScenarioManager()


def test_init_raises_when_conditions_and_next_steps_length_mismatch(
    tmp_path,
    monkeypatch,
):
    bad_root = tmp_path / "bad_scenarios"
    bad_dir = bad_root / "bad_scenario"
    bad_dir.mkdir(parents=True)
    (bad_dir / "picture.png").touch()
    bad_graph = {
        "scenario": "bad_scenario",
        "steps": [
            {
                "step": "step1",
                "scene": "...",
                "character": "X",
                "complete_conditions": ["c1", "c2"],
                "next_steps": ["only_one"],
            },
        ],
    }
    _write_graph(bad_dir, bad_graph)
    _make_step_dirs(bad_dir, ["step1"])

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", bad_root)

    with pytest.raises(ValueError, match="길이가 다릅니다"):
        ScenarioManager()


def test_init_raises_when_step_picture_missing(tmp_path, monkeypatch):
    root = tmp_path / "scenarios"
    scenario_dir = _build_minimal_scenario(root)
    (scenario_dir / "steps" / "step1" / "picture.png").unlink()

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", root)

    with pytest.raises(FileNotFoundError, match="step 'step1'"):
        ScenarioManager()


def test_init_raises_when_scenario_picture_missing(tmp_path, monkeypatch):
    root = tmp_path / "scenarios"
    scenario_dir = _build_minimal_scenario(root)
    (scenario_dir / "picture.png").unlink()

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", root)

    with pytest.raises(FileNotFoundError, match="scenario 'test'"):
        ScenarioManager()


def test_init_raises_when_script_first_file_missing(tmp_path, monkeypatch):
    root = tmp_path / "scenarios"
    scenario_dir = _build_minimal_scenario(root)
    (scenario_dir / "steps" / "step1" / "script" / "1.txt").unlink()

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", root)

    with pytest.raises(FileNotFoundError, match=re.escape("script/1.txt")):
        ScenarioManager()


def test_init_raises_when_script_has_gap(tmp_path, monkeypatch):
    root = tmp_path / "scenarios"
    scenario_dir = _build_minimal_scenario(root)
    script_dir = scenario_dir / "steps" / "step1" / "script"
    (script_dir / "3.txt").write_text("x")

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", root)

    with pytest.raises(ValueError, match="연속"):
        ScenarioManager()


def test_init_raises_when_voice_first_file_missing(tmp_path, monkeypatch):
    root = tmp_path / "scenarios"
    scenario_dir = _build_minimal_scenario(root)
    (scenario_dir / "steps" / "step1" / "voice" / "1.wav").unlink()

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", root)

    with pytest.raises(FileNotFoundError, match=re.escape("voice/1.wav")):
        ScenarioManager()


def test_init_raises_when_voice_has_gap(tmp_path, monkeypatch):
    root = tmp_path / "scenarios"
    scenario_dir = _build_minimal_scenario(root)
    voice_dir = scenario_dir / "steps" / "step1" / "voice"
    (voice_dir / "3.wav").touch()

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", root)

    with pytest.raises(ValueError, match="연속"):
        ScenarioManager()


def test_get_returns_scenario_instance(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    scenario = ScenarioManager().get("test_cafe")

    assert isinstance(scenario, Scenario)


def test_get_returns_scenario_with_name_from_argument(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    scenario = ScenarioManager().get("test_cafe")

    assert scenario.name == "test_cafe"


def test_get_returns_same_instance_on_repeated_calls(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)
    manager = ScenarioManager()

    first_scenario = manager.get("test_cafe")
    second_scenario = manager.get("test_cafe")

    assert first_scenario is second_scenario


def test_get_constructs_first_step_from_yaml(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    scenario = ScenarioManager().get("test_cafe")

    first_step = scenario.first_step
    assert isinstance(first_step, Step)
    assert first_step.name == "1. 인사"
    assert first_step.scene == "직원이 인사한다"
    assert first_step.character == "Zephyr"
    assert first_step.complete_conditions == ["주문"]
    assert first_step.next_step_names == ["2. 결제"]


def test_get_uses_steps_subdir_for_step_dir(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    scenario = ScenarioManager().get("test_cafe")

    expected_step_dir = scenarios_root / "test_cafe" / "steps" / "1. 인사"
    assert scenario.first_step.step_dir == expected_step_dir


def test_get_raises_for_unknown_scenario(scenarios_root, monkeypatch):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    with pytest.raises(KeyError):
        ScenarioManager().get("nonexistent")


def test_list_all_returns_scenario_info_with_name_and_picture(
    scenarios_root, monkeypatch
):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    infos = ScenarioManager().list_all()

    expected_picture = scenarios_root / "test_cafe" / "picture.png"
    assert infos == [ScenarioInfo(name="test_cafe", picture=expected_picture)]


def test_init_skips_non_directory_entries_in_root(scenarios_root, monkeypatch):
    (scenarios_root / "README.md").write_text("not a scenario", encoding="utf-8")
    (scenarios_root / ".DS_Store").touch()

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    manager = ScenarioManager()

    assert set(manager._scenarios.keys()) == {"test_cafe"}


def test_loaded_scenario_first_step_name(
    scenarios_root, monkeypatch
):
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)

    scenario = ScenarioManager().get("test_cafe")
    assert scenario.first_step.name == "1. 인사"
    assert scenario.get_step("2. 결제") is not None
