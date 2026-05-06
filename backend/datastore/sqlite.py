import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from datastore.model import DialogEntry, ScenarioSnapshot, StateLogEntry

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Sqlite:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def init_schema(self) -> None:
        schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        with closing(self._connect()) as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def load_progress(self, scenario_name: str) -> ScenarioSnapshot | None:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT current_step_name, step_visits_json "
                "FROM scenario_progress WHERE scenario_name = ?",
                (scenario_name,),
            ).fetchone()
        if row is None:
            return None

        current_step_name, step_visits_json = row
        return ScenarioSnapshot(
            current_step_name=current_step_name,
            step_visits=json.loads(step_visits_json),
        )

    def append_dialog(self, scenario_name: str, entry: DialogEntry) -> None:
        with closing(self._connect()) as conn:
            self._insert_dialog(conn, scenario_name, entry)
            conn.commit()

    @staticmethod
    def _insert_dialog(
        conn: sqlite3.Connection,
        scenario_name: str,
        entry: DialogEntry,
    ) -> None:
        conn.execute(
            "INSERT INTO dialog_log (scenario_name, role, text, created_at) "
            "VALUES (?, ?, ?, ?)",
            (
                scenario_name,
                entry.role,
                entry.text,
                entry.created_at.isoformat(),
            ),
        )

    def load_dialog(self, scenario_name: str) -> list[DialogEntry]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT role, text, created_at FROM dialog_log "
                "WHERE scenario_name = ? ORDER BY id",
                (scenario_name,),
            ).fetchall()

        entries: list[DialogEntry] = []
        for role, text, created_at_iso in rows:
            created_at = datetime.fromisoformat(created_at_iso)
            entry = DialogEntry(role=role, text=text, created_at=created_at)
            entries.append(entry)

        return entries

    def append_state_log(self, scenario_name: str, entry: StateLogEntry) -> None:
        with closing(self._connect()) as conn:
            self._insert_state_log(conn, scenario_name, entry)
            conn.commit()

    @staticmethod
    def _insert_state_log(
        conn: sqlite3.Connection,
        scenario_name: str,
        entry: StateLogEntry,
    ) -> None:
        conn.execute(
            """
            INSERT INTO state_log (
              scenario_name, step_name, visit_count,
              conditions_json, next_step_names_json,
              character_script, user_input, llm_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scenario_name,
                entry.step_name,
                entry.visit_count,
                json.dumps(entry.conditions, ensure_ascii=False),
                json.dumps(entry.next_step_names, ensure_ascii=False),
                entry.character_script,
                entry.user_input,
                entry.llm_index,
            ),
        )

    def load_state_log(self, scenario_name: str) -> list[StateLogEntry]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT step_name, visit_count, conditions_json, next_step_names_json,
                       character_script, user_input, llm_index
                FROM state_log
                WHERE scenario_name = ?
                ORDER BY id
                """,
                (scenario_name,),
            ).fetchall()

        entries: list[StateLogEntry] = []
        for row in rows:
            (
                step_name,
                visit_count,
                conditions_json,
                next_step_names_json,
                character_script,
                user_input,
                llm_index,
            ) = row

            conditions = json.loads(conditions_json)
            next_step_names = json.loads(next_step_names_json)
            entry = StateLogEntry(
                step_name=step_name,
                visit_count=visit_count,
                conditions=conditions,
                next_step_names=next_step_names,
                character_script=character_script,
                user_input=user_input,
                llm_index=llm_index,
            )
            entries.append(entry)

        return entries

    def save_progress(self, scenario_name: str, snapshot: ScenarioSnapshot) -> None:
        with closing(self._connect()) as conn:
            self._upsert_progress(conn, scenario_name, snapshot)
            conn.commit()

    def clear(self, scenario_name: str) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "DELETE FROM scenario_progress WHERE scenario_name = ?",
                (scenario_name,),
            )
            conn.execute(
                "DELETE FROM dialog_log WHERE scenario_name = ?",
                (scenario_name,),
            )
            conn.execute(
                "DELETE FROM state_log WHERE scenario_name = ?",
                (scenario_name,),
            )
            conn.commit()

    def list_progressed_scenarios(self) -> list[str]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT scenario_name FROM scenario_progress ORDER BY scenario_name",
            ).fetchall()

        return [name for (name,) in rows]

    def complete_last_state_entry(
        self,
        scenario_name: str,
        user_input: str,
        llm_index: int | None,
    ) -> None:
        with closing(self._connect()) as conn:
            self._update_last_state_entry(
                conn,
                scenario_name,
                user_input,
                llm_index,
            )
            conn.commit()

    @staticmethod
    def _update_last_state_entry(
        conn: sqlite3.Connection,
        scenario_name: str,
        user_input: str,
        llm_index: int | None,
    ) -> None:
        conn.execute(
            """
            UPDATE state_log
            SET user_input = ?, llm_index = ?
            WHERE id = (
              SELECT MAX(id) FROM state_log WHERE scenario_name = ?
            )
            """,
            (user_input, llm_index, scenario_name),
        )

    def commit_turn(
        self,
        scenario_name: str,
        snapshot: ScenarioSnapshot,
        completed_user_input: str,
        completed_llm_index: int | None,
        user_dialog: DialogEntry | None,
        new_character_dialog: DialogEntry | None,
        new_state_entry: StateLogEntry,
    ) -> None:
        with closing(self._connect()) as conn:
            self._update_last_state_entry(
                conn,
                scenario_name,
                completed_user_input,
                completed_llm_index,
            )
            self._upsert_progress(conn, scenario_name, snapshot)
            if user_dialog is not None:
                self._insert_dialog(conn, scenario_name, user_dialog)
            if new_character_dialog is not None:
                self._insert_dialog(conn, scenario_name, new_character_dialog)
            self._insert_state_log(conn, scenario_name, new_state_entry)
            conn.commit()

    def _upsert_progress(
        self,
        conn: sqlite3.Connection,
        scenario_name: str,
        snapshot: ScenarioSnapshot,
    ) -> None:
        now_iso = datetime.now(UTC).isoformat()
        conn.execute(
            """
            INSERT INTO scenario_progress
              (scenario_name, current_step_name, step_visits_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(scenario_name) DO UPDATE SET
              current_step_name = excluded.current_step_name,
              step_visits_json = excluded.step_visits_json,
              updated_at = excluded.updated_at
            """,
            (
                scenario_name,
                snapshot.current_step_name,
                json.dumps(snapshot.step_visits, ensure_ascii=False),
                now_iso,
            ),
        )
