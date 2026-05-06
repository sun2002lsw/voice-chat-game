from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from api.model import (
    InputRequest,
    ScenarioSummaryDTO,
    SessionStateDTO,
    to_session_state_dto,
)
from game_session.model import SessionState
from game_session.session import GameSession

router = APIRouter()


@router.get("/scenarios")
def list_scenarios(request: Request) -> list[ScenarioSummaryDTO]:
    session = _get_session(request)
    return [
        ScenarioSummaryDTO(
            name=s.name,
            profile_url=f"/api/scenarios/{s.name}/profile",
            has_progress=s.has_progress,
        )
        for s in session.list_scenarios()
    ]


@router.get("/scenarios/{name}/profile")
def get_profile(request: Request, name: str) -> FileResponse:
    session = _get_session(request)
    summaries = session.list_scenarios()

    matched = next((s for s in summaries if s.name == name), None)
    if matched is None:
        raise HTTPException(status_code=404, detail="scenario not found")

    return FileResponse(matched.picture_path)


@router.post("/scenarios/{name}/new")
def start_new(request: Request, name: str) -> SessionStateDTO:
    session = _get_session(request)
    state = session.start_new(name)
    return to_session_state_dto(state)


@router.post("/scenarios/{name}/continue")
def resume(request: Request, name: str) -> SessionStateDTO:
    state = _require_state(_get_session(request), name)
    return to_session_state_dto(state)


@router.get("/scenarios/{name}/state")
def get_state(request: Request, name: str) -> SessionStateDTO:
    state = _require_state(_get_session(request), name)
    return to_session_state_dto(state)


@router.post("/scenarios/{name}/input")
def submit_input(
    request: Request,
    name: str,
    body: InputRequest,
) -> SessionStateDTO:
    session = _get_session(request)
    _require_state(session, name)

    state = session.submit_input(name, body.text)
    return to_session_state_dto(state)


@router.post("/scenarios/{name}/advance")
def advance(request: Request, name: str) -> SessionStateDTO:
    session = _get_session(request)
    _require_state(session, name)

    try:
        state = session.auto_advance(name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return to_session_state_dto(state)


@router.get("/scenarios/{name}/picture")
def get_picture(request: Request, name: str) -> FileResponse:
    state = _require_state(_get_session(request), name)
    return FileResponse(state.picture_path)


@router.get("/scenarios/{name}/voice")
def get_voice(request: Request, name: str) -> FileResponse:
    state = _require_state(_get_session(request), name)
    return FileResponse(state.voice_path)


def _get_session(request: Request) -> GameSession:
    return request.app.state.game_session


def _require_state(session: GameSession, name: str) -> SessionState:
    state = session.get_state(name)
    if state is None:
        raise HTTPException(status_code=404, detail="no progress for scenario")
    return state
