from pathlib import Path

from llm import LLM

from .common import StepOutput, VisitOverflow

_ALWAYS = "always"


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
        script_count: int,
        visit_overflow: VisitOverflow | None = None,
    ) -> None:
        self.name = name
        self.scene = scene
        self.character = character
        self.step_dir = step_dir
        self.picture = picture
        self.complete_conditions = complete_conditions
        self.next_step_names = next_step_names
        self.script_count = script_count
        self.visit_overflow = visit_overflow
        self.visit_count = 1

    @property
    def is_terminal(self) -> bool:
        return not self.next_step_names

    @property
    def is_auto_advance(self) -> bool:
        if self.is_terminal:
            return False
        if any(self.complete_conditions):
            return False
        return len(self.next_step_names) == 1

    @property
    def conditions(self) -> list[str]:
        return [c for c in self.complete_conditions if c]

    def invoke(self, user_input: str) -> tuple[str, int | None]:
        next_step_name, llm_index = self._decide_next_step(user_input)
        self.visit_count = min(self.visit_count + 1, self.script_count)

        return next_step_name, llm_index

    def get_output(self) -> StepOutput:
        return StepOutput(
            picture=self.picture,
            script=self.step_dir / "script" / f"{self.visit_count}.txt",
            voice=self.step_dir / "voice" / f"{self.visit_count}.wav",
        )

    def _decide_next_step(self, user_input: str) -> tuple[str, int | None]:
        overflow_target = self._visit_overflow_target()
        if overflow_target is not None:
            return overflow_target, None

        has_conditions = any(self.complete_conditions)
        if not has_conditions:
            return self._next_step_without_conditions(), None

        if all(c == _ALWAYS for c in self.complete_conditions):
            return self.next_step_names[0], None

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

    def _visit_overflow_target(self) -> str | None:
        if self.visit_overflow is None:
            return None
        if self.visit_count < self.visit_overflow.after:
            return None
        return self.visit_overflow.next_step
