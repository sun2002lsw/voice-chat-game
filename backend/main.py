from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from api.app import build_app

_PROJECT_ROOT = Path(__file__).parent.parent
_DB_PATH = _PROJECT_ROOT / ".data" / "game.db"

load_dotenv()
app = build_app(db_path=_DB_PATH)
uvicorn.run(app, host="127.0.0.1", port=8000)
