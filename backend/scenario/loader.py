from pathlib import Path
from typing import Any

import yaml

from .scenario import Scenario
from .step import Step

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCENARIOS_ROOT = PROJECT_ROOT / ".scenario"

_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})

_REQUIRED_GRAPH_KEYS = ("scenario", "steps")
_REQUIRED_STEP_KEYS = (
    "step",
    "tone",
    "character",
    "loop",
    "complete_conditions",
    "next_steps",
)


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
    _validate_graph_top_level(graph, scenario_name=name)

    step_entries = graph["steps"]
    if not step_entries:
        msg = f"시나리오 '{name}'의 graph.yaml에 step이 최소 1개 필요합니다"
        raise ValueError(msg)

    steps_dir = scenario_dir / "steps"
    steps = [_build_step(entry, steps_dir) for entry in step_entries]
    _validate_scenario_consistency(steps)

    return Scenario(name=name, picture=picture_path, steps=steps)


def _validate_graph_top_level(graph: Any, *, scenario_name: str) -> None:  # noqa: ANN401
    if not isinstance(graph, dict):
        msg = f"시나리오 '{scenario_name}'의 graph.yaml 최상위는 매핑이어야 합니다"
        raise TypeError(msg)

    for key in _REQUIRED_GRAPH_KEYS:
        if key not in graph:
            msg = (
                f"시나리오 '{scenario_name}'의 graph.yaml에 '{key}' 키가 없습니다"
            )
            raise ValueError(msg)

    declared_name = graph["scenario"]
    if declared_name != scenario_name:
        msg = (
            f"graph.yaml의 'scenario' 필드 ('{declared_name}')가 "
            f"폴더 이름 ('{scenario_name}')과 다릅니다"
        )
        raise ValueError(msg)


def _build_step(entry: dict[str, Any], steps_dir: Path) -> Step:
    _validate_step_entry(entry)

    step_name = entry["step"]
    step_dir = steps_dir / step_name
    script_count = _validate_step_files(step_name, step_dir)

    picture_path = find_image(step_dir, label=f"step '{step_name}'")
    complete_conditions, next_step_names = _build_transition_lists(entry)

    return Step(
        name=step_name,
        tone=entry["tone"],
        character=entry["character"],
        step_dir=step_dir,
        picture=picture_path,
        complete_conditions=complete_conditions,
        next_step_names=next_step_names,
        script_count=script_count,
        loop=entry["loop"],
    )


def _build_transition_lists(
    entry: dict[str, Any],
) -> tuple[list[str], list[str]]:
    conditions = entry["complete_conditions"]
    next_steps = entry["next_steps"]

    if not conditions:
        empty_conditions = ["" for _ in next_steps]
        return empty_conditions, list(next_steps)

    if len(conditions) != len(next_steps):
        msg = (
            f"step '{entry['step']}'의 complete_conditions 와 next_steps "
            f"길이가 다릅니다. "
            f"conditions={len(conditions)}, next_steps={len(next_steps)}"
        )
        raise ValueError(msg)

    return list(conditions), list(next_steps)


def _validate_step_entry(entry: dict[str, Any]) -> None:
    if not isinstance(entry, dict):
        msg = f"step entry는 매핑이어야 합니다 (현재: {entry!r})"
        raise TypeError(msg)

    for key in _REQUIRED_STEP_KEYS:
        if key not in entry:
            msg = f"step entry에 '{key}' 키가 없습니다: {entry!r}"
            raise ValueError(msg)

    if entry["complete_conditions"]:
        return

    next_step_count = len(entry["next_steps"])
    if next_step_count != 1:
        msg = (
            f"complete_conditions가 비어있는 step '{entry['step']}'은 "
            f"자동 진행을 위해 next_steps가 정확히 1개여야 합니다. "
            f"현재: {next_step_count}개"
        )
        raise ValueError(msg)


def _validate_step_files(step_name: str, step_dir: Path) -> int:
    script_count = _validate_numbered_files(
        step_name,
        folder=step_dir / "script",
        extension="txt",
        label="script",
    )
    voice_count = _validate_numbered_files(
        step_name,
        folder=step_dir / "voice",
        extension="wav",
        label="voice",
    )
    if script_count != voice_count:
        msg = (
            f"step '{step_name}'의 script({script_count}개)와 "
            f"voice({voice_count}개) 파일 개수가 다릅니다"
        )
        raise ValueError(msg)
    return script_count


def _validate_numbered_files(
    step_name: str,
    *,
    folder: Path,
    extension: str,
    label: str,
) -> int:
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

    return len(found_numbers)


def _validate_scenario_consistency(steps: list[Step]) -> None:
    names = [s.name for s in steps]

    seen: set[str] = set()
    duplicates: set[str] = set()
    for name in names:
        if name in seen:
            duplicates.add(name)
        seen.add(name)
    if duplicates:
        msg = f"중복된 step 이름이 있습니다: {sorted(duplicates)}"
        raise ValueError(msg)

    valid = set(names)
    for s in steps:
        for next_name in s.next_step_names:
            if next_name not in valid:
                msg = (
                    f"step '{s.name}'의 next_steps가 "
                    f"존재하지 않는 step '{next_name}'을 참조합니다"
                )
                raise ValueError(msg)
