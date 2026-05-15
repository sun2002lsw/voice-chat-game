from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from api.app import build_app
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
) -> None:
    step_dir = scenario_dir / "steps" / step_name
    step_dir.mkdir(parents=True)
    (step_dir / "picture.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (step_dir / "script").mkdir()
    (step_dir / "script" / "1.txt").write_text(script_text, encoding="utf-8")
    (step_dir / "voice").mkdir()
    (step_dir / "voice" / "1.wav").write_bytes(b"RIFF....WAVEfmt ")


@pytest.fixture
def scenarios_root(tmp_path: Path) -> Path:
    root = tmp_path / "scenarios"
    root.mkdir()

    cafe_dir = root / "test_cafe"
    cafe_dir.mkdir()
    (cafe_dir / "picture.png").write_bytes(b"\x89PNG\r\n\x1a\n")
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

    return root


@pytest.fixture(autouse=True)
def reset_singletons(monkeypatch):
    Singleton._instances.pop(ScenarioManager, None)
    yield
    Singleton._instances.pop(ScenarioManager, None)


@pytest.fixture
def client(
    scenarios_root: Path,
    monkeypatch,
) -> TestClient:
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)
    app = build_app()
    return TestClient(app)


def test_list_scenarios_returns_summary(client: TestClient):
    response = client.get("/api/scenarios")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    summary = body[0]
    assert summary["name"] == "test_cafe"
    assert summary["profile_url"].endswith("/api/scenarios/test_cafe/profile")


def test_get_scenario_profile_returns_image(client: TestClient):
    response = client.get("/api/scenarios/test_cafe/profile")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
    assert len(response.content) > 0


def test_get_scenario_profile_returns_404_for_unknown_scenario(client: TestClient):
    response = client.get("/api/scenarios/unknown_scenario/profile")
    assert response.status_code == 404


def test_post_new_returns_initial_state(client: TestClient):
    response = client.post("/api/scenarios/test_cafe/new")

    assert response.status_code == 200
    body = response.json()
    assert body["scenario_name"] == "test_cafe"
    assert body["current_step_name"] == "1. 인사"
    assert body["is_terminal"] is False
    assert body["picture_url"] == "/api/scenarios/test_cafe/picture"
    assert body["voice_urls"] == ["/api/scenarios/test_cafe/voice/0"]
    assert body["scripts"] == ["어서오세요"]

    assert body["dialog"] == ["어서오세요"]

    assert len(body["state_log"]) == 1
    first_entry = body["state_log"][0]
    assert first_entry["step_name"] == "1. 인사"
    assert first_entry["conditions"] == ["주문"]
    assert first_entry["next_step_names"] == ["2. 결제"]
    assert first_entry["character_script"] == "어서오세요"
    assert first_entry["selected_index"] is None


def test_get_state_returns_404_when_no_progress(client: TestClient):
    response = client.get("/api/scenarios/test_cafe/state")
    assert response.status_code == 404


def test_get_state_returns_current_session_state(client: TestClient):
    client.post("/api/scenarios/test_cafe/new")

    response = client.get("/api/scenarios/test_cafe/state")

    assert response.status_code == 200
    assert response.json()["current_step_name"] == "1. 인사"


def test_post_input_advances_to_next_step_and_appends_logs(client: TestClient):
    client.post("/api/scenarios/test_cafe/new")

    response = client.post(
        "/api/scenarios/test_cafe/input",
        json={"index": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_step_name"] == "2. 결제"
    assert body["dialog"] == ["어서오세요", "결제 도와드릴게요"]
    assert len(body["state_log"]) == 2

    completed = body["state_log"][0]
    assert completed["step_name"] == "1. 인사"
    assert completed["selected_index"] == 0

    started = body["state_log"][1]
    assert started["step_name"] == "2. 결제"
    assert started["selected_index"] is None
    assert started["character_script"] == "결제 도와드릴게요"


def test_post_input_returns_404_when_no_progress(client: TestClient):
    response = client.post(
        "/api/scenarios/test_cafe/input",
        json={"index": 0},
    )
    assert response.status_code == 404


def test_get_picture_returns_image(client: TestClient):
    client.post("/api/scenarios/test_cafe/new")

    response = client.get("/api/scenarios/test_cafe/picture")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
    assert len(response.content) > 0


def test_get_voice_returns_audio_bytes(client: TestClient):
    client.post("/api/scenarios/test_cafe/new")

    response = client.get("/api/scenarios/test_cafe/voice/0")

    assert response.status_code == 200
    assert len(response.content) > 0


def test_get_picture_returns_404_when_no_progress(client: TestClient):
    response = client.get("/api/scenarios/test_cafe/picture")
    assert response.status_code == 404


def test_get_voice_returns_404_when_no_progress(client: TestClient):
    response = client.get("/api/scenarios/test_cafe/voice/0")
    assert response.status_code == 404


def test_post_input_returns_422_when_index_field_missing(client: TestClient):
    client.post("/api/scenarios/test_cafe/new")

    response = client.post("/api/scenarios/test_cafe/input", json={})

    assert response.status_code == 422


def test_get_picture_reflects_current_step_after_transition(
    scenarios_root: Path,
    monkeypatch,
):
    distinct_payment_picture = b"\x89PNG\r\n\x1a\nPAYMENT"
    payment_step_dir = scenarios_root / "test_cafe" / "steps" / "2. 결제"
    (payment_step_dir / "picture.png").write_bytes(distinct_payment_picture)

    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)
    app = build_app()
    client = TestClient(app)

    client.post("/api/scenarios/test_cafe/new")
    client.post(
        "/api/scenarios/test_cafe/input",
        json={"index": 0},
    )

    response = client.get("/api/scenarios/test_cafe/picture")

    assert response.status_code == 200
    assert response.content == distinct_payment_picture


def test_post_input_marks_is_terminal_true_at_terminal_step(client: TestClient):
    client.post("/api/scenarios/test_cafe/new")

    response = client.post(
        "/api/scenarios/test_cafe/input",
        json={"index": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_step_name"] == "2. 결제"
    assert body["is_terminal"] is True


