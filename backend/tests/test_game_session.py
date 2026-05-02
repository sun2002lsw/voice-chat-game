from pathlib import Path
from typing import Any

import pytest
import yaml

from datastore.sqlite import Sqlite
from game_session.model import ScenarioSummary
from game_session.session import GameSession
from scenario.manager import ScenarioManager
from singleton import Singleton


def _write_graph(scenario_dir: Path, graph: dict[str, Any]) -> None:
    graph_yaml_text = yaml.safe_dump(graph, allow_unicode=True)
    (scenario_dir / "graph.yaml").write_text(graph_yaml_text, encoding="utf-8")


def _make_step_dir(
    scenario_dir: Path,
    step_name: str,
    *,
    script_text: str = "기본 대사",
) -> Path:
    step_dir = scenario_dir / "steps" / step_name
    step_dir.mkdir(parents=True)
    (step_dir / "picture.png").touch()
    (step_dir / "script").mkdir()
    (step_dir / "script" / "1.txt").write_text(script_text, encoding="utf-8")
    (step_dir / "voice").mkdir()
    (step_dir / "voice" / "1.wav").touch()
    return step_dir


@pytest.fixture
def scenarios_root(tmp_path: Path) -> Path:
    root = tmp_path / "scenarios"
    root.mkdir()

    cafe_dir = root / "test_cafe"
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
    _make_step_dir(cafe_dir, "1. 인사", script_text="어서오세요")
    _make_step_dir(cafe_dir, "2. 결제", script_text="결제 도와드릴게요")

    # 종착 step "2. 결제" 의 visit 2 스크립트/음성 (self-loop 입력 테스트용)
    payment_step_dir = cafe_dir / "steps" / "2. 결제"
    (payment_step_dir / "script" / "2.txt").write_text(
        "결제 두 번째 안내", encoding="utf-8",
    )
    (payment_step_dir / "voice" / "2.wav").write_bytes(b"RIFF....WAVEfmt ")

    return root


class _FakeLLM:
    next_index: int = 0

    def __init__(self) -> None:
        pass

    def get_next_step(
        self,
        scene: str,
        complete_conditions: list[str],
        user_input: str,
    ) -> int:
        return _FakeLLM.next_index


@pytest.fixture(autouse=True)
def reset_singletons_and_llm(monkeypatch):
    Singleton._instances.pop(ScenarioManager, None)
    _FakeLLM.next_index = 0
    monkeypatch.setattr("scenario.step.LLM", _FakeLLM)
    yield
    Singleton._instances.pop(ScenarioManager, None)


@pytest.fixture
def game_session(
    tmp_path: Path,
    scenarios_root: Path,
    monkeypatch,
) -> GameSession:
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)
    datastore = Sqlite(db_path=tmp_path / "game.db")
    datastore.init_schema()
    manager = ScenarioManager()
    return GameSession(datastore=datastore, scenario_manager=manager)


def test_list_scenarios_marks_no_progress_when_datastore_empty(
    game_session: GameSession,
    scenarios_root: Path,
):
    summaries = game_session.list_scenarios()

    expected_picture = scenarios_root / "test_cafe" / "picture.png"
    assert summaries == [
        ScenarioSummary(
            name="test_cafe",
            picture_path=expected_picture,
            has_progress=False,
        ),
    ]


def test_list_scenarios_marks_has_progress_after_start_new(
    game_session: GameSession,
):
    game_session.start_new("test_cafe")

    summaries = game_session.list_scenarios()

    assert summaries[0].has_progress is True


def test_start_new_records_first_dialog_and_state_log_entry(
    game_session: GameSession,
):
    state = game_session.start_new("test_cafe")

    assert len(state.dialog) == 1
    assert state.dialog[0].role == "character"
    assert state.dialog[0].text == "어서오세요"

    assert len(state.state_log) == 1
    first = state.state_log[0]
    assert first.step_name == "1. 인사"
    assert first.visit_count == 1
    assert first.conditions == ["주문"]
    assert first.next_step_names == ["2. 결제"]
    assert first.character_script == "어서오세요"
    assert first.user_input == ""
    assert first.llm_index is None


def test_start_new_clears_existing_progress(game_session: GameSession):
    _FakeLLM.next_index = 0
    game_session.start_new("test_cafe")
    game_session.submit_input("test_cafe", "주문할게요")

    state = game_session.start_new("test_cafe")

    assert state.current_step_name == "1. 인사"
    assert len(state.dialog) == 1
    assert len(state.state_log) == 1


def test_submit_input_appends_user_and_character_dialogs(
    game_session: GameSession,
):
    _FakeLLM.next_index = 0
    game_session.start_new("test_cafe")

    state = game_session.submit_input("test_cafe", "주문할게요")

    roles = [d.role for d in state.dialog]
    assert roles == ["character", "user", "character"]
    assert state.dialog[1].text == "주문할게요"
    assert state.dialog[2].text == "결제 도와드릴게요"


def test_submit_input_transitions_to_next_step(game_session: GameSession):
    _FakeLLM.next_index = 0
    game_session.start_new("test_cafe")

    state = game_session.submit_input("test_cafe", "주문할게요")

    assert state.current_step_name == "2. 결제"


def test_submit_input_completes_first_entry_and_starts_next(
    game_session: GameSession,
):
    _FakeLLM.next_index = 0
    game_session.start_new("test_cafe")

    state = game_session.submit_input("test_cafe", "아메리카노")

    assert len(state.state_log) == 2

    completed = state.state_log[0]
    assert completed.step_name == "1. 인사"
    assert completed.visit_count == 1
    assert completed.conditions == ["주문"]
    assert completed.next_step_names == ["2. 결제"]
    assert completed.character_script == "어서오세요"
    assert completed.user_input == "아메리카노"
    assert completed.llm_index == 0

    started = state.state_log[1]
    assert started.step_name == "2. 결제"
    assert started.visit_count == 1
    assert started.conditions == []
    assert started.next_step_names == []
    assert started.character_script == "결제 도와드릴게요"
    assert started.user_input == ""
    assert started.llm_index is None


def test_submit_input_skips_character_dialog_on_self_loop(
    game_session: GameSession,
):
    _FakeLLM.next_index = 0
    game_session.start_new("test_cafe")
    game_session.submit_input("test_cafe", "주문")

    dialog_count_before = 3

    state = game_session.submit_input("test_cafe", "결제 후 추가 발화")

    user_dialogs = [d for d in state.dialog if d.role == "user"]
    assert len(state.dialog) == dialog_count_before + 1
    assert len(user_dialogs) == 2
    assert state.dialog[-1].role == "user"
    assert state.dialog[-1].text == "결제 후 추가 발화"


def test_resume_returns_none_when_no_progress(game_session: GameSession):
    assert game_session.resume("test_cafe") is None


def test_resume_restores_state_through_fresh_manager_and_datastore(
    tmp_path: Path,
    game_session: GameSession,
):
    _FakeLLM.next_index = 0
    game_session.start_new("test_cafe")
    game_session.submit_input("test_cafe", "주문할게요")

    Singleton._instances.pop(ScenarioManager, None)
    fresh_manager = ScenarioManager()
    fresh_datastore = Sqlite(db_path=tmp_path / "game.db")
    fresh_session = GameSession(
        datastore=fresh_datastore, scenario_manager=fresh_manager,
    )

    state = fresh_session.resume("test_cafe")

    assert state is not None
    assert state.current_step_name == "2. 결제"
    assert len(state.dialog) == 3
    assert len(state.state_log) == 2


def test_get_state_returns_none_when_no_progress(game_session: GameSession):
    assert game_session.get_state("test_cafe") is None


def test_get_state_returns_current_state_after_start_new(
    game_session: GameSession,
):
    game_session.start_new("test_cafe")

    state = game_session.get_state("test_cafe")

    assert state is not None
    assert state.current_step_name == "1. 인사"
