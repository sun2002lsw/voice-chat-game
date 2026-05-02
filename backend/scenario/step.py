from llm import LLM

from .common import StepOutput, StepPaths, StepTransition


class Step:
    def __init__(
        self,
        name: str,
        scene: str,
        character: str,
        paths: StepPaths,
        transitions: list[StepTransition],
    ) -> None:
        self.name = name
        self.scene = scene
        self.character = character
        self.step_dir = paths.step_dir
        self.picture = paths.picture
        self.transitions = transitions
        self.visit_count = 1

    def invoke(self, user_input: str) -> str:
        next_step_name = self._decide_next_step_name(user_input)
        self.visit_count += 1

        return next_step_name

    def get_output(self) -> StepOutput:
        return StepOutput(
            picture=self.picture,
            script=self.step_dir / "script" / f"{self.visit_count}.txt",
            voice=self.step_dir / "voice" / f"{self.visit_count}.wav",
        )

    def _decide_next_step_name(self, user_input: str) -> str:
        has_conditions = any(t.condition for t in self.transitions)
        if not has_conditions:
            return self._next_step_without_conditions()

        return self._pick_next_step_via_llm(user_input)

    def _next_step_without_conditions(self) -> str:
        if not self.transitions:
            return self.name

        return self.transitions[0].next_step_name

    def _pick_next_step_via_llm(self, user_input: str) -> str:
        conditions = [t.condition for t in self.transitions]
        next_step_index = LLM().get_next_step(
            scene=self.scene,
            complete_conditions=conditions,
            user_input=user_input,
        )

        return self.transitions[next_step_index].next_step_name
