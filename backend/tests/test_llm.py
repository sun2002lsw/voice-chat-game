import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from llm import LLM
from llm.const import SYSTEM_PROMPT
from singleton import Singleton


@pytest.fixture(autouse=True)
def reset_llm_singleton():
    Singleton._instances.pop(LLM, None)
    yield
    Singleton._instances.pop(LLM, None)


@pytest.fixture(autouse=True)
def reset_fake_chat_state():
    _FakeChat.next_index = 0
    _FakeChat.last_chain = None


class _FakeStructuredChain:
    def __init__(self, schema, index_to_return: int = 0) -> None:
        self.schema = schema
        self.index_to_return = index_to_return
        self.last_messages = None

    def invoke(self, messages, *args, **kwargs):
        self.last_messages = messages
        return self.schema(index=self.index_to_return)


class _FakeChat:
    next_index: int = 0
    last_chain: _FakeStructuredChain | None = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    def with_structured_output(self, schema):
        chain = _FakeStructuredChain(schema, index_to_return=_FakeChat.next_index)
        _FakeChat.last_chain = chain
        return chain


def _patch_chat(monkeypatch) -> None:
    monkeypatch.setattr("llm.llm.ChatGoogleGenerativeAI", _FakeChat)


def _captured_human_message_content() -> str:
    last_messages = _FakeChat.last_chain.last_messages
    human_message = last_messages[1]
    return human_message.content


def test_llm_is_singleton(monkeypatch):
    _patch_chat(monkeypatch)

    first_instance = LLM()
    second_instance = LLM()

    assert first_instance is second_instance


@pytest.mark.parametrize("picked_index", [0, 1])
def test_get_next_step_returns_index_from_structured_output(monkeypatch, picked_index):
    _patch_chat(monkeypatch)
    _FakeChat.next_index = picked_index

    result = LLM().get_next_step(
        scene="카페 직원으로서 인사한다",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        user_input="아메리카노 주세요",
    )

    assert result == picked_index


def test_get_next_step_sends_system_and_human_messages(monkeypatch):
    _patch_chat(monkeypatch)

    LLM().get_next_step(
        scene="카페 직원으로서 인사한다",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        user_input="아메리카노 주세요",
    )

    sent_messages = _FakeChat.last_chain.last_messages
    system_message, human_message = sent_messages

    assert isinstance(system_message, SystemMessage)
    assert isinstance(human_message, HumanMessage)


def test_get_next_step_uses_system_prompt_from_const(monkeypatch):
    _patch_chat(monkeypatch)

    LLM().get_next_step(
        scene="카페 직원으로서 인사한다",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        user_input="아메리카노 주세요",
    )

    system_message = _FakeChat.last_chain.last_messages[0]

    assert system_message.content == SYSTEM_PROMPT


def test_get_next_step_includes_scene_in_human_message(monkeypatch):
    _patch_chat(monkeypatch)

    LLM().get_next_step(
        scene="카페 직원으로서 인사한다",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        user_input="아메리카노 주세요",
    )

    human_content = _captured_human_message_content()

    assert "카페 직원으로서 인사한다" in human_content


def test_get_next_step_includes_user_input_in_human_message(monkeypatch):
    _patch_chat(monkeypatch)

    LLM().get_next_step(
        scene="카페 직원으로서 인사한다",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        user_input="아메리카노 주세요",
    )

    human_content = _captured_human_message_content()

    assert "아메리카노 주세요" in human_content


def test_get_next_step_numbers_complete_conditions_zero_based(monkeypatch):
    _patch_chat(monkeypatch)

    LLM().get_next_step(
        scene="카페 직원으로서 인사한다",
        complete_conditions=["메뉴 주문", "메뉴 질문"],
        user_input="아메리카노 주세요",
    )

    human_content = _captured_human_message_content()

    assert "0. 메뉴 주문" in human_content
    assert "1. 메뉴 질문" in human_content
