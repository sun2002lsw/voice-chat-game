import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchScenarios } from "../../api/client";
import { ScenarioCard } from "./ScenarioCard";
import type { ScenarioSummary } from "../../types";

import styles from "./Lobby.module.css";

export function Lobby() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const t = Date.now();
    fetchScenarios()
      .then((data) =>
        setScenarios(
          data.map((s) => ({ ...s, profile_url: `${s.profile_url}?t=${t}` })),
        ),
      )
      .catch(() => setErrorMessage("시나리오 목록을 불러오지 못했습니다."));
  }, []);

  function handleCardClick(scenario: ScenarioSummary) {
    navigate(`/play/${encodeURIComponent(scenario.name)}`, {
      state: { firstStepName: scenario.first_step_name },
    });
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
    </div>
  );
}
