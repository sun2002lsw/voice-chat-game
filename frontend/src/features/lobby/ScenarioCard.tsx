import type { ScenarioSummary } from "../../types";

import styles from "./ScenarioCard.module.css";

type Props = {
  scenario: ScenarioSummary;
  onClick: () => void;
};

export function ScenarioCard({ scenario, onClick }: Props) {
  return (
    <button type="button" className={styles.card} onClick={onClick}>
      <img
        className={styles.profile}
        src={scenario.profile_url}
        alt={scenario.name}
      />
      <span className={styles.name}>{scenario.name}</span>
      {scenario.has_progress && (
        <span className={styles.progressBadge}>진행 중</span>
      )}
    </button>
  );
}
