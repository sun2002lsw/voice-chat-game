from pathlib import Path
from typing import Any

import yaml

from .common import StepPaths, StepTransition
from .scenario import Scenario
from .step import Step

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCENARIOS_ROOT = PROJECT_ROOT / ".scenario"

_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})


def find_image(folder: Path, *, label: str) -> Path:
    images = [
        f
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTENSIONS
    ]
    if not images:
        msg = f"{label}에 사진 파일이 없습니다: {folder}"
        raise FileNotFoundError(msg)
    return images[0]


def load_all_scenarios() -> dict[str, Scenario]:
    scenarios: dict[str, Scenario] = {}
    for scenario_dir in SCENARIOS_ROOT.iterdir():
        if scenario_dir.is_dir():
            scenarios[scenario_dir.name] = load_scenario(scenario_dir.name)

    return scenarios


def load_scenario(name: str) -> Scenario:
    scenario_dir = SCENARIOS_ROOT / name
    picture_path = find_image(scenario_dir, label=f"scenario '{name}'")

    graph_path = scenario_dir / "graph.yaml"
    graph_text = graph_path.read_text(encoding="utf-8")
    graph = yaml.safe_load(graph_text)

    steps_dir = scenario_dir / "steps"
    step_entries = graph["steps"]
    steps = [_build_step(entry, steps_dir) for entry in step_entries]

    return Scenario(name=name, picture=picture_path, steps=steps)


def _build_step(entry: dict[str, Any], steps_dir: Path) -> Step:
    _validate_step_entry(entry)

    step_name = entry["step"]
    step_dir = steps_dir / step_name
    _validate_step_files(step_name, step_dir)

    picture_path = find_image(step_dir, label=f"step '{step_name}'")
    paths = StepPaths(step_dir=step_dir, picture=picture_path)
    transitions = _build_transitions(entry)

    return Step(
        name=step_name,
        scene=entry["scene"],
        character=entry["character"],
        paths=paths,
        transitions=transitions,
    )


def _build_transitions(entry: dict[str, Any]) -> list[StepTransition]:
    conditions = entry["complete_conditions"]
    next_steps = entry["next_steps"]

    if not conditions:
        return [
            StepTransition(condition="", next_step_name=name) for name in next_steps
        ]

    pairs = zip(conditions, next_steps, strict=True)
    return [StepTransition(condition=c, next_step_name=n) for c, n in pairs]


def _validate_step_entry(entry: dict[str, Any]) -> None:
    if entry["complete_conditions"]:
        return

    next_step_count = len(entry["next_steps"])
    if next_step_count > 1:
        msg = (
            f"complete_conditions가 비어있는 step '{entry['step']}'은 "
            f"next_steps가 0개 또는 1개여야 합니다. "
            f"현재: {next_step_count}개"
        )
        raise ValueError(msg)


def _validate_step_files(step_name: str, step_dir: Path) -> None:
    _validate_numbered_files(
        step_name,
        folder=step_dir / "script",
        extension="txt",
        label="script",
    )
    _validate_numbered_files(
        step_name,
        folder=step_dir / "voice",
        extension="wav",
        label="voice",
    )


def _validate_numbered_files(
    step_name: str,
    *,
    folder: Path,
    extension: str,
    label: str,
) -> None:
    if not folder.is_dir():
        msg = f"step '{step_name}'의 {label} 폴더가 없습니다: {folder}"
        raise FileNotFoundError(msg)

    found_files = list(folder.glob(f"*.{extension}"))
    raw_numbers = (int(file.stem) for file in found_files)
    found_numbers = sorted(raw_numbers)

    if not found_numbers:
        msg = f"step '{step_name}'의 {label}/1.{extension}이 없습니다"
        raise FileNotFoundError(msg)

    expected_numbers = list(range(1, len(found_numbers) + 1))
    if found_numbers != expected_numbers:
        msg = (
            f"step '{step_name}'의 {label} 파일 번호가 1부터 연속되지 않습니다. "
            f"발견: {found_numbers}"
        )
        raise ValueError(msg)
