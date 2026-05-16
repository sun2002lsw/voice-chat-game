from pathlib import Path


class Step:
    def __init__(
        self,
        name: str,
        tone: str,
        character: str,
        step_dir: Path,
        picture: Path,
        complete_conditions: list[str],
        next_step_names: list[str],
        loop: bool = False,
    ) -> None:
        self.name = name
        self.tone = tone
        self.character = character
        self.step_dir = step_dir
        self.picture = picture
        self.complete_conditions = complete_conditions
        self.next_step_names = next_step_names
        self.loop = loop

    @property
    def is_terminal(self) -> bool:
        return not self.next_step_names

    @property
    def conditions(self) -> list[str]:
        return [c for c in self.complete_conditions if c]

    @property
    def script(self) -> Path:
        return self.step_dir / "script.txt"

    @property
    def voice(self) -> Path:
        return self.step_dir / "voice.wav"
