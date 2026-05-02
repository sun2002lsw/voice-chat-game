from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from singleton import Singleton

from .const import MODEL, SYSTEM_PROMPT


class ClassifyResult(BaseModel):
    index: int = Field(
        description="완료 조건 리스트(0-based)에서 매칭되는 항목의 인덱스"
    )


class LLM(metaclass=Singleton):
    def __init__(self) -> None:
        chat = ChatGoogleGenerativeAI(model=MODEL)
        self._chain = chat.with_structured_output(ClassifyResult)

    def get_next_step(
        self,
        scene: str,
        complete_conditions: list[str],
        user_input: str,
    ) -> int:
        numbered_conditions = (f"{i}. {c}" for i, c in enumerate(complete_conditions))
        conditions_text = "\n".join(numbered_conditions)

        user_message = (
            f"상황: {scene}\n\n"
            f"완료 조건:\n{conditions_text}\n\n"
            f"사용자 입력: {user_input}"
        )
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        result: ClassifyResult = self._chain.invoke(messages)
        return result.index
