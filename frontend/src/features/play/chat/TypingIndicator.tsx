import styles from "./TypingIndicator.module.css";

export function TypingIndicator() {
  return (
    <div className={styles.row} role="status" aria-label="응답 작성 중">
      <div className={styles.bubble}>
        <span className={styles.dot} />
        <span className={styles.dot} />
        <span className={styles.dot} />
      </div>
    </div>
  );
}
