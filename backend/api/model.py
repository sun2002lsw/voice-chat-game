from pydantic import BaseModel


class ScenarioSummaryDTO(BaseModel):
    name: str
    profile_url: str
    first_step_name: str


class StepDTO(BaseModel):
    step_name: str
    is_terminal: bool
    loop: bool
    picture_url: str
    script: str
    voice_url: str
    conditions: list[str]
    next_step_names: list[str]
