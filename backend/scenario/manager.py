from singleton import Singleton

from .common import ScenarioInfo
from .loader import load_all_scenarios
from .scenario import Scenario


class ScenarioManager(metaclass=Singleton):
    def __init__(self) -> None:
        self._scenarios: dict[str, Scenario] = load_all_scenarios()

    def get(self, name: str) -> Scenario:
        return self._scenarios[name]

    def list_all(self) -> list[ScenarioInfo]:
        return [
            ScenarioInfo(name=scenario.name, picture=scenario.picture)
            for scenario in self._scenarios.values()
        ]
