import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchScenarios, resumeSession, startNew } from "../../api/client";
import { NewOrContinueModal } from "./NewOrContinueModal";
import { ScenarioCard } from "./ScenarioCard";
import type { ScenarioSummary } from "../../types";

import styles from "./Lobby.module.css";

function playPath(name: string): string {
  return `/play/${encodeURIComponent(name)}`;
}

export function Lobby() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [selected, setSelected] = useState<ScenarioSummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchScenarios()
      .then(setScenarios)
      .catch(() => setErrorMessage("시나리오 목록을 불러오지 못했습니다."));
  }, []);

  async function enterScenario(
    name: string,
    enter: (name: string) => Promise<unknown>,
    failureMessage: string,
  ) {
    try {
      await enter(name);
      navigate(playPath(name));
    } catch {
      setErrorMessage(failureMessage);
    }
  }

  async function handleCardClick(scenario: ScenarioSummary) {
    if (scenario.has_progress) {
      setSelected(scenario);
      return;
    }
    await enterScenario(scenario.name, startNew, "새 게임을 시작하지 못했습니다.");
  }

  async function handleNewGame() {
    if (selected === null) return;
    await enterScenario(selected.name, startNew, "새 게임을 시작하지 못했습니다.");
  }

  async function handleContinue() {
    if (selected === null) return;
    await enterScenario(selected.name, resumeSession, "이어하기에 실패했습니다.");
  }

  function handleClose() {
    setSelected(null);
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>시나리오를 골라주세요</h1>
      {errorMessage !== null && (
        <div role="alert" className={styles.alert}>
          <span>{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            aria-label="알림 닫기"
          >
            닫기
          </button>
        </div>
      )}
      <div className={styles.grid}>
        {scenarios.map((scenario) => (
          <ScenarioCard
            key={scenario.name}
            scenario={scenario}
            onClick={() => handleCardClick(scenario)}
          />
        ))}
      </div>
      {selected !== null && (
        <NewOrContinueModal
          scenarioName={selected.name}
          onNewGame={handleNewGame}
          onContinue={handleContinue}
          onClose={handleClose}
        />
      )}
    </div>
  );
}
