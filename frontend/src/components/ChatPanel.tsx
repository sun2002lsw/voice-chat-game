import { useEffect, useRef } from "react";

import type { DialogEntry } from "../types";

import { ChatInput } from "./ChatInput";
import styles from "./ChatPanel.module.css";
import { MessageBubble } from "./MessageBubble";

type Props = {
  scenarioName: string;
  dialog: DialogEntry[];
  isTerminal: boolean;
  onSubmit: (text: string) => void;
};

export function ChatPanel({ scenarioName, dialog, isTerminal, onSubmit }: Props) {
  const dialogEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    dialogEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [dialog.length]);

  return (
    <div className={styles.panel}>
      <h2 className={styles.header}>{scenarioName}</h2>
      <div className={styles.dialog}>
        {dialog.map((entry, index) => (
          <MessageBubble key={index} entry={entry} />
        ))}
        <div ref={dialogEndRef} />
      </div>
      <ChatInput onSubmit={onSubmit} disabled={isTerminal} />
    </div>
  );
}
