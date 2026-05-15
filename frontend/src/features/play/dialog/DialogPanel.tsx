import { useEffect, useRef } from "react";

import styles from "./DialogPanel.module.css";

type Props = {
  scenarioName: string;
  dialog: string[];
  isTerminal: boolean;
  onHome: () => void;
};

export function DialogPanel({ scenarioName, dialog, isTerminal, onHome }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [dialog.length]);

  return (
    <div className={styles.panel}>
      <header className={styles.header}>
        <button
          type="button"
          className={styles.homeButton}
          onClick={onHome}
          aria-label="로비로 가기"
        >
          🏠
        </button>
        <h2 className={styles.title}>{scenarioName}</h2>
      </header>
      <div className={styles.dialog}>
        {dialog.map((text, i) => (
          <div key={i} className={styles.bubble}>{text}</div>
        ))}
        {isTerminal && <p className={styles.terminal}>— 종료 —</p>}
        <div ref={endRef} />
      </div>
    </div>
  );
}
