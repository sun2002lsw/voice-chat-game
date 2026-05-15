from fastapi import FastAPI

from api import route
from scenario.manager import ScenarioManager


def build_app() -> FastAPI:
    ScenarioManager()  # 시나리오 파일 이상 여부를 기동 시점에 확인

    app = FastAPI(title="voice-chat-game")
    app.include_router(route.router, prefix="/api")

    return app
