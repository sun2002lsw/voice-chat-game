from datetime import datetime

from pydantic import BaseModel

from game_session.model import SessionState


class ScenarioSummaryDTO(BaseModel):
    name: str
    profile_url: str
    has_progress: bool


class DialogEntryDTO(BaseModel):
    role: str
    text: str
    created_at: datetime


class StateLogEntryDTO(BaseModel):
    step_name: str
    visit_count: int
    conditions: list[str]
    next_step_names: list[str]
    character_script: str
    user_input: str
    llm_index: int | None


class SessionStateDTO(BaseModel):
    scenario_name: str
    current_step_name: str
    is_terminal: bool
    profile_url: str
    picture_url: str
    voice_url: str
    dialog: list[DialogEntryDTO]
    state_log: list[StateLogEntryDTO]


class InputRequest(BaseModel):
    text: str


def to_session_state_dto(state: SessionState) -> SessionStateDTO:
    name = state.scenario_name

    dialog_dtos: list[DialogEntryDTO] = []
    for entry in state.dialog:
        dialog_dto = DialogEntryDTO(
            role=entry.role,
            text=entry.text,
            created_at=entry.created_at,
        )
        dialog_dtos.append(dialog_dto)

    state_log_dtos: list[StateLogEntryDTO] = []
    for entry in state.state_log:
        state_dto = StateLogEntryDTO(
            step_name=entry.step_name,
            visit_count=entry.visit_count,
            conditions=entry.conditions,
            next_step_names=entry.next_step_names,
            character_script=entry.character_script,
            user_input=entry.user_input,
            llm_index=entry.llm_index,
        )
        state_log_dtos.append(state_dto)

    return SessionStateDTO(
        scenario_name=state.scenario_name,
        current_step_name=state.current_step_name,
        is_terminal=state.is_terminal,
        profile_url=f"/api/scenarios/{name}/profile",
        picture_url=f"/api/scenarios/{name}/picture",
        voice_url=f"/api/scenarios/{name}/voice",
        dialog=dialog_dtos,
        state_log=state_log_dtos,
    )
