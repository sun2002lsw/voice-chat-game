from pathlib import Path

MODEL = "gemini-2.5-flash"
PROMPT_PATH = Path(__file__).parent / "prompt.txt"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
