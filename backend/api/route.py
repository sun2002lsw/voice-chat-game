from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.model import ScenarioSummaryDTO, StepDTO
from scenario.manager import ScenarioManager
from scenario.scenario import Scenario
from scenario.step import Step

router = APIRouter()

_NO_CACHE = {"Cache-Control": "no-store"}


@router.get("/scenarios")
def list_scenarios() -> list[ScenarioSummaryDTO]:
    manager = ScenarioManager()
    return [
        ScenarioSummaryDTO(
            name=info.name,
            profile_url=f"/api/scenarios/{quote(info.name)}/profile",
            first_step_name=manager.get(info.name).first_step.name,
        )
        for info in manager.list_all()
    ]


@router.get("/scenarios/{name}/profile")
def get_profile(name: str) -> FileResponse:
    scenario = _require_scenario(name)
    return FileResponse(scenario.picture, headers=_NO_CACHE)


@router.get("/scenarios/{name}/steps/{step_name}")
def get_step(name: str, step_name: str) -> StepDTO:
    scenario = _require_scenario(name)
    step = _require_step(scenario, step_name)
    outputs = step.get_all_outputs()
    base = f"/api/scenarios/{quote(name)}/steps/{quote(step_name)}"
    return StepDTO(
        step_name=step.name,
        is_terminal=step.is_terminal,
        picture_url=f"{base}/picture",
        scripts=[o.script.read_text(encoding="utf-8") for o in outputs],
        voice_urls=[f"{base}/voice/{i}" for i in range(len(outputs))],
        conditions=step.complete_conditions,
        next_step_names=step.next_step_names,
    )


@router.get("/scenarios/{name}/steps/{step_name}/picture")
def get_step_picture(name: str, step_name: str) -> FileResponse:
    scenario = _require_scenario(name)
    step = _require_step(scenario, step_name)
    return FileResponse(step.picture, headers=_NO_CACHE)


@router.get("/scenarios/{name}/steps/{step_name}/voice/{index}")
def get_step_voice(name: str, step_name: str, index: int) -> FileResponse:
    scenario = _require_scenario(name)
    step = _require_step(scenario, step_name)
    outputs = step.get_all_outputs()
    clamped = min(max(0, index), len(outputs) - 1)
    return FileResponse(outputs[clamped].voice, headers=_NO_CACHE)


def _require_scenario(name: str) -> Scenario:
    try:
        return ScenarioManager().get(name)
    except KeyError:
        raise HTTPException(status_code=404, detail="scenario not found")


def _require_step(scenario: Scenario, step_name: str) -> Step:
    step = scenario.get_step(step_name)
    if step is None:
        raise HTTPException(status_code=404, detail="step not found")
    return step
