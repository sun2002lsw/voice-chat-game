import type { StateLogEntry } from "../types";

import styles from "./DebugPanel.module.css";

type Props = {
  stateLog: StateLogEntry[];
};

export function DebugPanel({ stateLog }: Props) {
  return (
    <div className={styles.panel}>
      {stateLog.map((entry, index) => (
        <Block key={index} entry={entry} />
      ))}
    </div>
  );
}

function Block({ entry }: { entry: StateLogEntry }) {
  const userInputDisplay = entry.user_input === "" ? "(대기 중)" : entry.user_input;
  const llmIndexDisplay =
    entry.llm_index === null ? "(없음)" : String(entry.llm_index);

  return (
    <div className={styles.block} data-testid="debug-block" data-block="">
      <div className={styles.field}>
        <span className={styles.label}>스텝</span>
        <span className={styles.value}>{entry.step_name}</span>
      </div>
      <div className={styles.field}>
        <span className={styles.label}>방문 횟수</span>
        <span className={styles.value}>{entry.visit_count}</span>
      </div>
      <div className={styles.field}>
        <span className={styles.label}>완료 조건</span>
        <ul className={styles.list}>
          {entry.conditions.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      </div>
      <div className={styles.field}>
        <span className={styles.label}>다음 스텝</span>
        <ul className={styles.list}>
          {entry.next_step_names.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      </div>
      <div className={styles.field}>
        <span className={styles.label}>캐릭터 스크립트</span>
        <span className={styles.value}>{entry.character_script}</span>
      </div>
      <hr className={styles.divider} />
      <div className={styles.field}>
        <span className={styles.label}>내 입력</span>
        <span className={styles.value}>{userInputDisplay}</span>
      </div>
      <div className={styles.field}>
        <span className={styles.label}>LLM 인덱스</span>
        <span className={styles.value}>{llmIndexDisplay}</span>
      </div>
    </div>
  );
}
