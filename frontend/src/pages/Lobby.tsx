import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchScenarios, resumeSession, startNew } from "../api/client";
import { NewOrContinueModal } from "../components/NewOrContinueModal";
import { ScenarioCard } from "../components/ScenarioCard";
import type { ScenarioSummary } from "../types";

import styles from "./Lobby.module.css";

function playPath(name: string): string {
  return `/play/${encodeURIComponent(name)}`;
}

export function Lobby() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [selected, setSelected] = useState<ScenarioSummary | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchScenarios().then(setScenarios);
  }, []);

  async function handleCardClick(scenario: ScenarioSummary) {
    if (scenario.has_progress) {
      setSelected(scenario);
      return;
    }
    await startNew(scenario.name);
    navigate(playPath(scenario.name));
  }

  async function handleNewGame() {
    if (selected === null) return;
    await startNew(selected.name);
    navigate(playPath(selected.name));
  }

  async function handleContinue() {
    if (selected === null) return;
    await resumeSession(selected.name);
    navigate(playPath(selected.name));
  }

  function handleClose() {
    setSelected(null);
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>시나리오를 골라주세요</h1>
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
