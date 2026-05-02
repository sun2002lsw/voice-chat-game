from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import route
from datastore.sqlite import Sqlite
from game_session.session import GameSession
from scenario.manager import ScenarioManager


def build_app(db_path: Path) -> FastAPI:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    datastore = Sqlite(db_path=db_path)
    datastore.init_schema()
    manager = ScenarioManager()
    game_session = GameSession(datastore=datastore, scenario_manager=manager)

    app = FastAPI(title="voice-chat-game")
    app.state.game_session = game_session

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    app.include_router(route.router, prefix="/api")

    return app
