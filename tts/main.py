from dotenv import load_dotenv

from .tts import TTS

load_dotenv()

tts = TTS()
tts.run()
