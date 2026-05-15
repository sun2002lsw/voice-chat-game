from pydantic import BaseModel

from game_session.model import SessionState


class ScenarioSummaryDTO(BaseModel):
    name: str
    profile_url: str


class StateLogEntryDTO(BaseModel):
    step_name: str
    conditions: list[str]
    next_step_names: list[str]
    character_script: str
    selected_index: int | None


class SessionStateDTO(BaseModel):
    scenario_name: str
    current_step_name: str
    is_terminal: bool
    profile_url: str
    picture_url: str
    scripts: list[str]
    voice_urls: list[str]
    dialog: list[str]
    state_log: list[StateLogEntryDTO]


class InputRequest(BaseModel):
    index: int


def to_session_state_dto(state: SessionState) -> SessionStateDTO:
    name = state.scenario_name

    voice_urls = [
        f"/api/scenarios/{name}/voice/{i}"
        for i in range(len(state.voice_paths))
    ]

    state_log_dtos = [
        StateLogEntryDTO(
            step_name=e.step_name,
            conditions=e.conditions,
            next_step_names=e.next_step_names,
            character_script=e.character_script,
            selected_index=e.selected_index,
        )
        for e in state.state_log
    ]

    return SessionStateDTO(
        scenario_name=state.scenario_name,
        current_step_name=state.current_step_name,
        is_terminal=state.is_terminal,
        profile_url=f"/api/scenarios/{name}/profile",
        picture_url=f"/api/scenarios/{name}/picture",
        scripts=state.scripts,
        voice_urls=voice_urls,
        dialog=state.dialog,
        state_log=state_log_dtos,
    )
