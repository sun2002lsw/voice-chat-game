from pathlib import Path

from .common import StepOutput, VisitOverflow


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
    def conditions(self) -> list[str]:
        return [c for c in self.complete_conditions if c]

    def invoke(self, index: int) -> tuple[str, int]:
        names = self.next_step_names
        if names:
            last = len(names) - 1
            selected = index if 0 <= index <= last else last
        else:
            selected = 0

        overflow_target = self._visit_overflow_target()
        if overflow_target is not None:
            next_step_name = overflow_target
        elif names:
            next_step_name = names[selected]
        else:
            next_step_name = self.name

        self.visit_count = min(self.visit_count + 1, self.script_count)
        return next_step_name, selected

    def get_output(self) -> StepOutput:
        return StepOutput(
            picture=self.picture,
            script=self.step_dir / "script" / f"{self.visit_count}.txt",
            voice=self.step_dir / "voice" / f"{self.visit_count}.wav",
        )

    def _visit_overflow_target(self) -> str | None:
        if self.visit_overflow is None:
            return None
        if self.visit_count < self.visit_overflow.after:
            return None
        return self.visit_overflow.next_step
