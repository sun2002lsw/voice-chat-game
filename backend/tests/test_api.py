from pathlib import Path
from typing import Any
from urllib.parse import quote

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
                "tone": "직원이 인사한다",
                "character": "Zephyr",
                "complete_conditions": ["주문"],
                "next_steps": ["2. 결제"],
            },
            {
                "step": "2. 결제",
                "tone": "결제한다",
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
def reset_singletons():
    Singleton._instances.pop(ScenarioManager, None)
    yield
    Singleton._instances.pop(ScenarioManager, None)


@pytest.fixture
def client(scenarios_root: Path, monkeypatch) -> TestClient:
    monkeypatch.setattr("scenario.loader.SCENARIOS_ROOT", scenarios_root)
    return TestClient(build_app())


def test_list_scenarios_returns_name_and_first_step(client: TestClient):
    body = client.get("/api/scenarios").json()

    assert len(body) == 1
    assert body[0]["name"] == "test_cafe"
    assert body[0]["first_step_name"] == "1. 인사"
    assert body[0]["profile_url"].endswith("/profile")


def test_get_profile_returns_image(client: TestClient):
    resp = client.get("/api/scenarios/test_cafe/profile")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/")


def test_get_profile_404_for_unknown(client: TestClient):
    assert client.get("/api/scenarios/unknown/profile").status_code == 404


def test_get_step_returns_step_data(client: TestClient):
    step_name = quote("1. 인사")
    body = client.get(f"/api/scenarios/test_cafe/steps/{step_name}").json()

    assert body["step_name"] == "1. 인사"
    assert body["is_terminal"] is False
    assert body["scripts"] == ["어서오세요"]
    assert len(body["voice_urls"]) == 1
    assert body["conditions"] == ["주문"]
    assert body["next_step_names"] == ["2. 결제"]


def test_get_step_terminal(client: TestClient):
    step_name = quote("2. 결제")
    body = client.get(f"/api/scenarios/test_cafe/steps/{step_name}").json()

    assert body["is_terminal"] is True
    assert body["next_step_names"] == []


def test_get_step_404_for_unknown(client: TestClient):
    assert client.get("/api/scenarios/test_cafe/steps/ghost").status_code == 404


def test_get_step_picture_returns_image(client: TestClient):
    step_name = quote("1. 인사")
    resp = client.get(f"/api/scenarios/test_cafe/steps/{step_name}/picture")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("image/")


def test_get_step_voice_returns_audio(client: TestClient):
    step_name = quote("1. 인사")
    resp = client.get(f"/api/scenarios/test_cafe/steps/{step_name}/voice/0")
    assert resp.status_code == 200
    assert len(resp.content) > 0


def test_get_step_voice_clamps_index(client: TestClient):
    step_name = quote("1. 인사")
    resp = client.get(f"/api/scenarios/test_cafe/steps/{step_name}/voice/99")
    assert resp.status_code == 200
