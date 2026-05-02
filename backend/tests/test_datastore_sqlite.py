from datetime import UTC, datetime
from pathlib import Path

import pytest

from datastore.model import DialogEntry, ScenarioSnapshot, StateLogEntry
from datastore.sqlite import Sqlite


@pytest.fixture
def datastore(tmp_path: Path) -> Sqlite:
    ds = Sqlite(db_path=tmp_path / "test.db")
    ds.init_schema()
    return ds


def test_load_progress_returns_none_when_empty(datastore):
    assert datastore.load_progress("회사 면접") is None


def test_save_then_load_progress_round_trip(datastore):
    snapshot = ScenarioSnapshot(
        current_step_name="2. 결제",
        step_visits={"1. 어서오세요": 2, "2. 결제": 1},
    )

    datastore.save_progress("커피숍", snapshot)
    loaded = datastore.load_progress("커피숍")

    assert loaded == snapshot


def test_save_progress_overwrites_existing_for_same_scenario(datastore):
    first = ScenarioSnapshot(
        current_step_name="1. 어서오세요",
        step_visits={"1. 어서오세요": 1},
    )
    second = ScenarioSnapshot(
        current_step_name="2. 결제",
        step_visits={"1. 어서오세요": 3, "2. 결제": 1},
    )

    datastore.save_progress("커피숍", first)
    datastore.save_progress("커피숍", second)

    assert datastore.load_progress("커피숍") == second


def test_load_dialog_returns_empty_when_no_entries(datastore):
    assert datastore.load_dialog("커피숍") == []


def test_append_dialog_then_load_in_insert_order(datastore):
    t1 = datetime(2026, 5, 3, 12, 0, 0, tzinfo=UTC)
    t2 = datetime(2026, 5, 3, 12, 0, 5, tzinfo=UTC)
    t3 = datetime(2026, 5, 3, 12, 0, 10, tzinfo=UTC)

    datastore.append_dialog(
        "커피숍",
        DialogEntry(role="character", text="안녕하세요", created_at=t1),
    )
    datastore.append_dialog(
        "커피숍",
        DialogEntry(role="user", text="안녕", created_at=t2),
    )
    datastore.append_dialog(
        "커피숍",
        DialogEntry(role="character", text="주문하시겠어요?", created_at=t3),
    )

    loaded = datastore.load_dialog("커피숍")

    assert loaded == [
        DialogEntry(role="character", text="안녕하세요", created_at=t1),
        DialogEntry(role="user", text="안녕", created_at=t2),
        DialogEntry(role="character", text="주문하시겠어요?", created_at=t3),
    ]


def test_load_dialog_isolated_per_scenario(datastore):
    t = datetime(2026, 5, 3, tzinfo=UTC)
    a_entry = DialogEntry(role="user", text="A 메시지", created_at=t)
    b_entry = DialogEntry(role="user", text="B 메시지", created_at=t)
    datastore.append_dialog("A", a_entry)
    datastore.append_dialog("B", b_entry)

    a_dialog = datastore.load_dialog("A")
    b_dialog = datastore.load_dialog("B")

    assert len(a_dialog) == 1
    assert a_dialog[0].text == "A 메시지"
    assert len(b_dialog) == 1
    assert b_dialog[0].text == "B 메시지"


def test_load_state_log_returns_empty_when_no_entries(datastore):
    assert datastore.load_state_log("커피숍") == []


def test_append_state_log_preserves_all_fields(datastore):
    entry = StateLogEntry(
        step_name="1. 어서오세요",
        visit_count=2,
        conditions=["메뉴 주문", "메뉴 질문"],
        next_step_names=["2. 결제", "1. 어서오세요-안내"],
        character_script="어서오세요, 무엇을 도와드릴까요?",
        user_input="아메리카노 주세요",
        llm_index=0,
    )

    datastore.append_state_log("커피숍", entry)
    loaded = datastore.load_state_log("커피숍")

    assert loaded == [entry]


def test_state_log_preserves_none_llm_index_for_first_entry(datastore):
    entry = StateLogEntry(
        step_name="1. 어서오세요",
        visit_count=1,
        conditions=[],
        next_step_names=[],
        character_script="어서오세요",
        user_input="",
        llm_index=None,
    )

    datastore.append_state_log("커피숍", entry)
    loaded = datastore.load_state_log("커피숍")

    assert loaded == [entry]
    assert loaded[0].llm_index is None


def test_state_log_loads_in_insert_order(datastore):
    first = StateLogEntry(
        step_name="step1", visit_count=1, conditions=[], next_step_names=["step2"],
        character_script="첫 대사", user_input="입력1", llm_index=None,
    )
    second = StateLogEntry(
        step_name="step2",
        visit_count=1,
        conditions=["조건"],
        next_step_names=["step3"],
        character_script="두번째 대사",
        user_input="입력2",
        llm_index=0,
    )

    datastore.append_state_log("커피숍", first)
    datastore.append_state_log("커피숍", second)

    assert datastore.load_state_log("커피숍") == [first, second]


def test_state_log_isolated_per_scenario(datastore):
    a_entry = StateLogEntry(
        step_name="a-step", visit_count=1, conditions=[], next_step_names=[],
        character_script="A 대사", user_input="", llm_index=None,
    )
    b_entry = StateLogEntry(
        step_name="b-step", visit_count=1, conditions=[], next_step_names=[],
        character_script="B 대사", user_input="", llm_index=None,
    )

    datastore.append_state_log("A", a_entry)
    datastore.append_state_log("B", b_entry)

    assert datastore.load_state_log("A") == [a_entry]
    assert datastore.load_state_log("B") == [b_entry]


def test_clear_removes_progress_dialog_and_state_log(datastore):
    snapshot = ScenarioSnapshot(current_step_name="step1", step_visits={"step1": 1})
    datastore.save_progress("커피숍", snapshot)
    hi_entry = DialogEntry(
        role="user",
        text="hi",
        created_at=datetime(2026, 5, 3, tzinfo=UTC),
    )
    datastore.append_dialog("커피숍", hi_entry)
    datastore.append_state_log(
        "커피숍",
        StateLogEntry(
            step_name="step1", visit_count=1, conditions=[], next_step_names=[],
            character_script="대사", user_input="", llm_index=None,
        ),
    )

    datastore.clear("커피숍")

    assert datastore.load_progress("커피숍") is None
    assert datastore.load_dialog("커피숍") == []
    assert datastore.load_state_log("커피숍") == []


def test_clear_does_not_affect_other_scenarios(datastore):
    snapshot = ScenarioSnapshot(current_step_name="s", step_visits={"s": 1})
    datastore.save_progress("A", snapshot)
    datastore.save_progress("B", snapshot)

    datastore.clear("A")

    assert datastore.load_progress("A") is None
    assert datastore.load_progress("B") == snapshot


def test_list_progressed_scenarios_empty_when_none(datastore):
    assert datastore.list_progressed_scenarios() == []


def test_list_progressed_scenarios_returns_those_with_progress(datastore):
    snapshot = ScenarioSnapshot(current_step_name="s", step_visits={"s": 1})
    datastore.save_progress("A", snapshot)
    datastore.save_progress("B", snapshot)

    result = datastore.list_progressed_scenarios()

    assert set(result) == {"A", "B"}


def _seed_initial_turn(datastore):
    initial_entry = StateLogEntry(
        step_name="step1",
        visit_count=1,
        conditions=["c1"],
        next_step_names=["step2"],
        character_script="첫 대사",
        user_input="",
        llm_index=None,
    )
    datastore.append_state_log("커피숍", initial_entry)
    initial_snapshot = ScenarioSnapshot(
        current_step_name="step1", step_visits={"step1": 1},
    )
    datastore.save_progress("커피숍", initial_snapshot)
    return initial_entry


def test_complete_last_state_entry_fills_user_input_and_llm_index(datastore):
    _seed_initial_turn(datastore)

    datastore.complete_last_state_entry(
        "커피숍", user_input="주문할게요", llm_index=0,
    )

    state_log = datastore.load_state_log("커피숍")
    assert len(state_log) == 1
    completed = state_log[0]
    assert completed.user_input == "주문할게요"
    assert completed.llm_index == 0
    assert completed.step_name == "step1"
    assert completed.character_script == "첫 대사"


def test_commit_turn_completes_last_entry_and_appends_new_state_entry(datastore):
    _seed_initial_turn(datastore)

    new_snapshot = ScenarioSnapshot(
        current_step_name="step2", step_visits={"step1": 2, "step2": 1},
    )
    user_dialog = DialogEntry(
        role="user", text="주문할게요", created_at=datetime(2026, 5, 3, tzinfo=UTC),
    )
    new_character_dialog = DialogEntry(
        role="character",
        text="결제 도와드릴게요",
        created_at=datetime(2026, 5, 3, 1, 0, 0, tzinfo=UTC),
    )
    new_state_entry = StateLogEntry(
        step_name="step2",
        visit_count=1,
        conditions=[],
        next_step_names=[],
        character_script="결제 도와드릴게요",
        user_input="",
        llm_index=None,
    )

    datastore.commit_turn(
        scenario_name="커피숍",
        snapshot=new_snapshot,
        completed_user_input="주문할게요",
        completed_llm_index=0,
        user_dialog=user_dialog,
        new_character_dialog=new_character_dialog,
        new_state_entry=new_state_entry,
    )

    state_log = datastore.load_state_log("커피숍")
    assert len(state_log) == 2
    assert state_log[0].user_input == "주문할게요"
    assert state_log[0].llm_index == 0
    assert state_log[0].step_name == "step1"
    assert state_log[1] == new_state_entry

    assert datastore.load_dialog("커피숍") == [user_dialog, new_character_dialog]
    assert datastore.load_progress("커피숍") == new_snapshot


def test_commit_turn_skips_character_dialog_when_none(datastore):
    _seed_initial_turn(datastore)

    new_snapshot = ScenarioSnapshot(
        current_step_name="step1", step_visits={"step1": 2},
    )
    user_dialog = DialogEntry(
        role="user", text="입력", created_at=datetime(2026, 5, 3, tzinfo=UTC),
    )
    new_state_entry = StateLogEntry(
        step_name="step1",
        visit_count=2,
        conditions=["c1"],
        next_step_names=["step2"],
        character_script="두 번째 방문 대사",
        user_input="",
        llm_index=None,
    )

    datastore.commit_turn(
        scenario_name="커피숍",
        snapshot=new_snapshot,
        completed_user_input="입력",
        completed_llm_index=None,
        user_dialog=user_dialog,
        new_character_dialog=None,
        new_state_entry=new_state_entry,
    )

    assert datastore.load_dialog("커피숍") == [user_dialog]
    state_log = datastore.load_state_log("커피숍")
    assert len(state_log) == 2
    assert state_log[0].user_input == "입력"
    assert state_log[0].llm_index is None
    assert state_log[1] == new_state_entry
