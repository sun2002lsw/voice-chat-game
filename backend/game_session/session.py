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
        first_script = first_step.get_all_outputs()[0].script.read_text(encoding="utf-8")

        now = datetime.now(UTC)
        self._dialog[scenario_name] = [
            DialogEntry(role="character", text=first_script, created_at=now)
        ]
        self._state_log[scenario_name] = [
            _state_entry_from_step(first_step, first_script)
        ]

        return self._build_session_state(scenario_name, scenario)

    def get_state(self, scenario_name: str) -> SessionState | None:
        if scenario_name not in self._dialog:
            return None
        scenario = self._manager.get(scenario_name)
        return self._build_session_state(scenario_name, scenario)

    def submit_input(self, scenario_name: str, index: int) -> SessionState:
        scenario = self._manager.get(scenario_name)
        selected_index = scenario.invoke(index)

        now = datetime.now(UTC)
        user_dialog = DialogEntry(role="user", text=str(index), created_at=now)

        new_step = scenario.current_step
        new_script = new_step.get_all_outputs()[0].script.read_text(encoding="utf-8")
        new_character_dialog = DialogEntry(role="character", text=new_script, created_at=now)

        state_log = self._state_log[scenario_name]
        state_log[-1] = dataclasses.replace(state_log[-1], selected_index=selected_index)
        self._dialog[scenario_name].extend([user_dialog, new_character_dialog])
        state_log.append(_state_entry_from_step(new_step, new_script))

        return self._build_session_state(scenario_name, scenario)

    def _build_session_state(
        self,
        scenario_name: str,
        scenario: Scenario,
    ) -> SessionState:
        outputs = scenario.get_all_step_outputs()
        scripts = [o.script.read_text(encoding="utf-8") for o in outputs]
        voice_paths = [o.voice for o in outputs]
        return SessionState(
            scenario_name=scenario_name,
            current_step_name=scenario.current_step_name,
            is_terminal=scenario.is_terminal,
            picture_path=outputs[0].picture,
            scripts=scripts,
            voice_paths=voice_paths,
            profile_path=scenario.picture,
            dialog=list(self._dialog.get(scenario_name, [])),
            state_log=list(self._state_log.get(scenario_name, [])),
        )


def _state_entry_from_step(step: Step, character_script: str) -> StateLogEntry:
    return StateLogEntry(
        step_name=step.name,
        conditions=step.conditions,
        next_step_names=step.next_step_names,
        character_script=character_script,
        selected_index=None,
    )
