from pathlib import Path

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
        script_count: int,
    ) -> None:
        self.name = name
        self.scene = scene
        self.character = character
        self.step_dir = step_dir
        self.picture = picture
        self.complete_conditions = complete_conditions
        self.next_step_names = next_step_names
        self.script_count = script_count

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
        return names[selected] if names else self.name, selected

    def get_all_outputs(self) -> list[StepOutput]:
        return [
            StepOutput(
                picture=self.picture,
                script=self.step_dir / "script" / f"{i}.txt",
                voice=self.step_dir / "voice" / f"{i}.wav",
            )
            for i in range(1, self.script_count + 1)
        ]
