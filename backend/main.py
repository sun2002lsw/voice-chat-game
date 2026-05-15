import uvicorn
from dotenv import load_dotenv

from api.app import build_app

load_dotenv()
app = build_app()
uvicorn.run(app, host="127.0.0.1", port=8000)
