from fastapi import FastAPI

from api import route
from game_session.session import GameSession
from scenario.manager import ScenarioManager


def build_app() -> FastAPI:
    manager = ScenarioManager()
    game_session = GameSession(scenario_manager=manager)

    app = FastAPI(title="voice-chat-game")
    app.state.game_session = game_session
    app.include_router(route.router, prefix="/api")

    # CORS 미설정: 개발 환경에서는 Vite proxy가 처리하므로 고려하지 않음

    return app
