import styles from "./ConditionsPanel.module.css";

type Props = {
  conditions: string[];
  nextStepNames: string[];
  isTerminal: boolean;
  isLoading: boolean;
};

export function ConditionsPanel({ conditions, nextStepNames, isTerminal, isLoading }: Props) {
  if (isTerminal) {
    return (
      <div className={styles.panel}>
        <p className={styles.terminal}>종료</p>
      </div>
    );
  }

  return (
    <div className={styles.panel}>
      <p className={styles.hint}>숫자키로 선택</p>
      <ul className={styles.list}>
        {nextStepNames.map((_, i) => (
          <li key={i} className={`${styles.item} ${isLoading ? styles.loading : ""}`}>
            <span className={styles.index}>{i}</span>
            <span className={styles.condition}>{conditions[i] || "(계속)"}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
