import time
from pathlib import Path

import yaml

from .gemini import generate_voice

_PROJECT_ROOT = Path(__file__).parent.parent
_SCENARIOS_ROOT = _PROJECT_ROOT / ".scenario"
_CHARACTERS_ROOT = _PROJECT_ROOT / ".character"


class TTS:
    def run(self) -> None:
        self._count = 0
        self._elapsed = 0.0
        self._cost_usd = 0.0

        for scenario_dir in _SCENARIOS_ROOT.iterdir():
            if scenario_dir.is_dir():
                self._process_scenario(scenario_dir)

        print(
            f"\n총: {self._count}개 파일, {self._elapsed:.1f}s, ${self._cost_usd:.4f}",
        )

    def _process_scenario(self, scenario_dir: Path) -> None:
        graph_path = scenario_dir / "graph.yaml"
        graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
        steps_dir = scenario_dir / "steps"
        for entry in graph["steps"]:
            step_dir = steps_dir / entry["step"]
            self._process_step(
                step_dir,
                character=entry["character"],
                scene=entry["scene"],
            )

    def _process_step(self, step_dir: Path, *, character: str, scene: str) -> None:
        voice_dir = step_dir / "voice"
        voice_dir.mkdir(exist_ok=True)

        chatacter_txt = _CHARACTERS_ROOT / f"{character}.txt"
        director_note = chatacter_txt.read_text(encoding="utf-8")
        voice_name = character.split("_", maxsplit=1)[0]
        script_files = sorted((step_dir / "script").glob("*.txt"))

        for script_file in script_files:
            voice_file = voice_dir / f"{script_file.stem}.wav"
            if voice_file.exists():
                continue

            text = script_file.read_text(encoding="utf-8")
            start = time.perf_counter()
            usage = generate_voice(
                text=text,
                output_path=voice_file,
                voice_name=voice_name,
                director_note=director_note,
                scene=scene,
            )
            elapsed = time.perf_counter() - start

            self._count += 1
            self._elapsed += elapsed
            self._cost_usd += usage.cost_usd

            print(
                f"{step_dir.name} - {script_file.stem}: "
                f"{elapsed:.1f}s, ${usage.cost_usd:.4f}",
            )
