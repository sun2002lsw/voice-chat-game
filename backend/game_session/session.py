import dataclasses
from datetime import UTC, datetime

from game_session.model import (
    DialogEntry,
    ScenarioSummary,
    SessionState,
    StateLogEntry,
)
from scenario.manager import ScenarioManager
from scenario.scenario import Scenario
from scenario.step import Step


class GameSession:
    def __init__(self, scenario_manager: ScenarioManager) -> None:
        self._manager = scenario_manager
        self._dialog: dict[str, list[DialogEntry]] = {}
        self._state_log: dict[str, list[StateLogEntry]] = {}

    def list_scenarios(self) -> list[ScenarioSummary]:
        return [
            ScenarioSummary(
                name=info.name,
                picture_path=info.picture,
            )
            for info in self._manager.list_all()
        ]

    def start_new(self, scenario_name: str) -> SessionState:
        scenario = self._manager.get(scenario_name)
        scenario.reset()

        first_step = scenario.current_step
        first_output = scenario.get_output()
        character_script = first_output.script.read_text(encoding="utf-8")

        now = datetime.now(UTC)
        first_dialog = DialogEntry(role="character", text=character_script, created_at=now)
        first_state_entry = _state_entry_from_step(first_step, character_script)

        self._dialog[scenario_name] = [first_dialog]
        self._state_log[scenario_name] = [first_state_entry]

        return self._build_session_state(scenario_name, scenario)

    def get_state(self, scenario_name: str) -> SessionState | None:
        if scenario_name not in self._dialog:
            return None
        scenario = self._manager.get(scenario_name)
        return self._build_session_state(scenario_name, scenario)

    def submit_input(self, scenario_name: str, text: str) -> SessionState:
        scenario = self._manager.get(scenario_name)
        llm_index = scenario.invoke(text)

        now = datetime.now(UTC)
        user_dialog = DialogEntry(role="user", text=text, created_at=now)

        new_step = scenario.current_step
        new_character_script = scenario.get_output().script.read_text(encoding="utf-8")
        new_character_dialog = DialogEntry(
            role="character", text=new_character_script, created_at=now,
        )
        new_state_entry = _state_entry_from_step(new_step, new_character_script)

        state_log = self._state_log[scenario_name]
        state_log[-1] = dataclasses.replace(
            state_log[-1], user_input=text, llm_index=llm_index,
        )
        self._dialog[scenario_name].extend([user_dialog, new_character_dialog])
        state_log.append(new_state_entry)

        return self._build_session_state(scenario_name, scenario)

    def _build_session_state(
        self,
        scenario_name: str,
        scenario: Scenario,
    ) -> SessionState:
        output = scenario.get_output()
        return SessionState(
            scenario_name=scenario_name,
            current_step_name=scenario.current_step_name,
            current_visit_count=scenario.current_step.visit_count,
            is_terminal=scenario.is_terminal,
            picture_path=output.picture,
            voice_path=output.voice,
            profile_path=scenario.picture,
            dialog=list(self._dialog.get(scenario_name, [])),
            state_log=list(self._state_log.get(scenario_name, [])),
        )


def _state_entry_from_step(step: Step, character_script: str) -> StateLogEntry:
    return StateLogEntry(
        step_name=step.name,
        visit_count=step.visit_count,
        conditions=step.conditions,
        next_step_names=step.next_step_names,
        character_script=character_script,
        user_input="",
        llm_index=None,
    )
