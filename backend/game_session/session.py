from datetime import UTC, datetime

from datastore.model import DialogEntry, StateLogEntry
from datastore.sqlite import Sqlite
from game_session.model import ScenarioSummary, SessionState
from scenario.manager import ScenarioManager
from scenario.scenario import Scenario
from scenario.step import Step


class GameSession:
    def __init__(
        self,
        datastore: Sqlite,
        scenario_manager: ScenarioManager,
    ) -> None:
        self._datastore = datastore
        self._manager = scenario_manager

    def list_scenarios(self) -> list[ScenarioSummary]:
        progressed = set(self._datastore.list_progressed_scenarios())
        return [
            ScenarioSummary(
                name=info.name,
                picture_path=info.picture,
                has_progress=info.name in progressed,
            )
            for info in self._manager.list_all()
        ]

    def start_new(self, scenario_name: str) -> SessionState:
        self._datastore.clear(scenario_name)
        scenario = self._manager.get(scenario_name)
        scenario.reset()

        first_step = scenario.current_step
        first_output = scenario.get_output()
        character_script = first_output.script.read_text(encoding="utf-8")

        now = datetime.now(UTC)
        first_dialog = DialogEntry(
            role="character",
            text=character_script,
            created_at=now,
        )
        first_state_entry = _state_entry_from_step(first_step, character_script)

        self._datastore.append_dialog(scenario_name, first_dialog)
        self._datastore.append_state_log(scenario_name, first_state_entry)
        self._datastore.save_progress(scenario_name, scenario.snapshot())

        return self._build_session_state(scenario_name, scenario)

    def resume(self, scenario_name: str) -> SessionState | None:
        snapshot = self._datastore.load_progress(scenario_name)
        if snapshot is None:
            return None

        scenario = self._manager.get(scenario_name)
        scenario.restore(snapshot)

        return self._build_session_state(scenario_name, scenario)

    def get_state(self, scenario_name: str) -> SessionState | None:
        return self.resume(scenario_name)

    def submit_input(self, scenario_name: str, text: str) -> SessionState:
        scenario = self._manager.get(scenario_name)

        llm_index = scenario.invoke(text)

        now = datetime.now(UTC)
        user_dialog = DialogEntry(role="user", text=text, created_at=now)

        new_step = scenario.current_step
        new_script_path = scenario.get_output().script
        new_character_script = new_script_path.read_text(encoding="utf-8")

        new_character_dialog = DialogEntry(
            role="character",
            text=new_character_script,
            created_at=now,
        )
        new_state_entry = _state_entry_from_step(new_step, new_character_script)

        self._datastore.commit_turn(
            scenario_name=scenario_name,
            snapshot=scenario.snapshot(),
            completed_user_input=text,
            completed_llm_index=llm_index,
            user_dialog=user_dialog,
            new_character_dialog=new_character_dialog,
            new_state_entry=new_state_entry,
        )

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
            dialog=self._datastore.load_dialog(scenario_name),
            state_log=self._datastore.load_state_log(scenario_name),
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
