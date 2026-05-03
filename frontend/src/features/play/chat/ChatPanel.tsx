import { useEffect, useRef } from "react";

import type { DialogEntry } from "../../../types";

import { ChatInput } from "./ChatInput";
import styles from "./ChatPanel.module.css";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

type Props = {
  scenarioName: string;
  dialog: DialogEntry[];
  isTerminal: boolean;
  isPending: boolean;
  onSubmit: (text: string) => void;
  onHome: () => void;
};

export function ChatPanel({
  scenarioName,
  dialog,
  isTerminal,
  isPending,
  onSubmit,
  onHome,
}: Props) {
  const dialogEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    dialogEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [dialog.length, isPending]);

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
        {dialog.map((entry, index) => (
          <MessageBubble key={index} entry={entry} />
        ))}
        {isPending && <TypingIndicator />}
        <div ref={dialogEndRef} />
      </div>
      <ChatInput
        onSubmit={onSubmit}
        disabled={isTerminal}
        submitDisabled={isTerminal || isPending}
      />
    </div>
  );
}
