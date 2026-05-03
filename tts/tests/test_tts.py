from pathlib import Path

import pytest
import yaml
from tts import TTS
from tts.gemini import Usage

_FAKE_USAGE = Usage(prompt_tokens=10, output_tokens=20, total_tokens=30)


@pytest.fixture
def fake_scenarios_root(tmp_path: Path, monkeypatch) -> Path:
    scenarios_root = tmp_path / "scenarios"
    scenarios_root.mkdir()

    characters_root = tmp_path / "characters"
    characters_root.mkdir()
    (characters_root / "Zephyr_smile.txt").write_text(
        "Style: smile.",
        encoding="utf-8",
    )

    scenario_dir = scenarios_root / "test_cafe"
    scenario_dir.mkdir()

    graph = {
        "scenario": "test_cafe",
        "steps": [
            {
                "step": "1. greeting",
                "scene": "직원이 인사한다",
                "character": "Zephyr_smile",
                "complete_conditions": [],
                "next_steps": [],
            },
        ],
    }
    graph_yaml = yaml.safe_dump(graph, allow_unicode=True)
    (scenario_dir / "graph.yaml").write_text(graph_yaml, encoding="utf-8")

    step_dir = scenario_dir / "steps" / "1. greeting"
    step_dir.mkdir(parents=True)
    script_dir = step_dir / "script"
    script_dir.mkdir()
    (script_dir / "1.txt").write_text("어서오세요!", encoding="utf-8")
    (script_dir / "2.txt").write_text("결제 도와드릴까요?", encoding="utf-8")

    monkeypatch.setattr("tts.tts._SCENARIOS_ROOT", scenarios_root)
    monkeypatch.setattr("tts.tts._CHARACTERS_ROOT", characters_root)
    monkeypatch.setattr("tts.tts._PROJECT_ROOT", tmp_path)
    return scenarios_root


def test_run_calls_generate_voice_for_each_script(fake_scenarios_root, monkeypatch):
    calls = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        calls.append(output_path.name)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert sorted(calls) == ["1.wav", "2.wav"]


def test_run_skips_existing_voice_files(fake_scenarios_root, monkeypatch):
    voice_dir = fake_scenarios_root / "test_cafe" / "steps" / "1. greeting" / "voice"
    voice_dir.mkdir()
    (voice_dir / "1.wav").touch()

    calls = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        calls.append(output_path.name)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert calls == ["2.wav"]


def test_run_skips_all_when_all_voice_files_exist(fake_scenarios_root, monkeypatch):
    voice_dir = fake_scenarios_root / "test_cafe" / "steps" / "1. greeting" / "voice"
    voice_dir.mkdir()
    (voice_dir / "1.wav").touch()
    (voice_dir / "2.wav").touch()

    calls = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        calls.append(output_path.name)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert calls == []


def test_run_uses_first_part_of_character_as_voice_name(
    fake_scenarios_root,
    monkeypatch,
):
    captured_voice_names = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        captured_voice_names.append(voice_name)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert captured_voice_names == ["Zephyr", "Zephyr"]


def test_run_passes_character_file_content_as_director_note(
    fake_scenarios_root,
    monkeypatch,
):
    captured_notes = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        captured_notes.append(director_note)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert captured_notes == ["Style: smile.", "Style: smile."]


def test_run_passes_script_text_to_generate_voice(fake_scenarios_root, monkeypatch):
    captured_texts = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        captured_texts.append(text)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert sorted(captured_texts) == sorted(["어서오세요!", "결제 도와드릴까요?"])


def test_run_passes_scene_from_graph_entry(fake_scenarios_root, monkeypatch):
    captured_scenes = []

    def fake_generate(*, text, output_path, voice_name, director_note, scene):
        captured_scenes.append(scene)
        output_path.touch()
        return _FAKE_USAGE

    monkeypatch.setattr("tts.tts.generate_voice", fake_generate)

    TTS().run()

    assert captured_scenes == ["직원이 인사한다", "직원이 인사한다"]
