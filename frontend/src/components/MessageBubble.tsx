import type { DialogEntry } from "../types";

import styles from "./MessageBubble.module.css";

type Props = {
  entry: DialogEntry;
};

function formatTime(iso: string): string {
  const date = new Date(iso);
  const hh = String(date.getHours()).padStart(2, "0");
  const mm = String(date.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

export function MessageBubble({ entry }: Props) {
  const isUser = entry.role === "user";
  const rowClass = isUser ? styles.userRow : styles.characterRow;
  const bubbleClass = isUser ? styles.userBubble : styles.characterBubble;

  return (
    <div className={rowClass} data-role={entry.role}>
      {isUser && <span className={styles.time}>{formatTime(entry.created_at)}</span>}
      <div className={bubbleClass}>{entry.text}</div>
    </div>
  );
}
