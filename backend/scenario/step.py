from pathlib import Path

from llm import LLM

from .common import StepOutput


class Step:
    def __init__(
        self,
        name: str,
        scene: str,
        character: str,
        step_dir: Path,
        picture: Path,
        complete_conditions: list[str],
        next_step_names: list[str],
    ) -> None:
        self.name = name
        self.scene = scene
        self.character = character
        self.step_dir = step_dir
        self.picture = picture
        self.complete_conditions = complete_conditions
        self.next_step_names = next_step_names
        self.visit_count = 1

    @property
    def is_terminal(self) -> bool:
        return not self.next_step_names

    @property
    def conditions(self) -> list[str]:
        non_empty: list[str] = []
        for c in self.complete_conditions:
            if c:
                non_empty.append(c)
        return non_empty

    def invoke(self, user_input: str) -> tuple[str, int | None]:
        next_step_name, llm_index = self._decide_next_step(user_input)
        self.visit_count += 1

        return next_step_name, llm_index

    def get_output(self) -> StepOutput:
        return StepOutput(
            picture=self.picture,
            script=self.step_dir / "script" / f"{self.visit_count}.txt",
            voice=self.step_dir / "voice" / f"{self.visit_count}.wav",
        )

    def _decide_next_step(self, user_input: str) -> tuple[str, int | None]:
        has_conditions = any(c for c in self.complete_conditions)
        if not has_conditions:
            return self._next_step_without_conditions(), None

        return self._pick_next_step_via_llm(user_input)

    def _next_step_without_conditions(self) -> str:
        if not self.next_step_names:
            return self.name

        return self.next_step_names[0]

    def _pick_next_step_via_llm(self, user_input: str) -> tuple[str, int]:
        next_step_index = LLM().get_next_step(
            scene=self.scene,
            complete_conditions=self.complete_conditions,
            user_input=user_input,
        )
        next_step_name = self.next_step_names[next_step_index]

        return next_step_name, next_step_index
